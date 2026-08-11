import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";
import {
  buildOpenAIRequest,
  expectedAccessToken,
  shouldUseWebSearch,
} from "../src/chat_core.js";

const SITE_ORIGIN = "https://ddanyro.github.io";

function workerEnv(overrides = {}) {
  return {
    OPENAI_API_KEY: "openai-test",
    PORTFOLIO_PASSWORD: "portfolio-test",
    PORTFOLIO_CHAT_RATE_LIMITER: {limit: async () => ({success: true})},
    AI: {run: async () => ({choices: [{message: {content: "Fallback test."}}]})},
    OPENAI_RETRY_BASE_MS: 0,
    OPENAI_ATTEMPT_TIMEOUT_MS: 100,
    OPENAI_TOTAL_BUDGET_MS: 500,
    ...overrides,
  };
}

test("enables web search only for questions that need fresh external data", () => {
  assert.equal(shouldUseWebSearch("Cum arată riscul portofoliului?"), false);
  assert.equal(shouldUseWebSearch("Care sunt știrile recente despre NVDA?"), true);
  assert.equal(shouldUseWebSearch("Verifică pe internet rezultatele de azi"), true);
  assert.equal(shouldUseWebSearch("Analizează fără căutare web știrile din dashboard"), false);

  const base = {message: "Test", contextJson: "{}", history: []};
  assert.equal("tools" in buildOpenAIRequest({...base, useWebSearch: false}), false);
  assert.deepEqual(
    buildOpenAIRequest({...base, useWebSearch: true}).tools,
    [{type: "web_search"}],
  );
});

test("rejects localhost and unknown origins", async () => {
  const response = await worker.fetch(new Request("https://worker.example", {
    method: "POST",
    headers: {Origin: "http://localhost:8000", "Content-Type": "application/json"},
    body: JSON.stringify({message: "Test"}),
  }), workerEnv());
  assert.equal(response.status, 403);
  assert.equal(response.headers.get("Access-Control-Allow-Origin"), null);
});

test("answers the public site's CORS preflight", async () => {
  const response = await worker.fetch(new Request("https://worker.example", {
    method: "OPTIONS",
    headers: {Origin: SITE_ORIGIN},
  }), workerEnv());
  assert.equal(response.status, 204);
  assert.equal(response.headers.get("Access-Control-Allow-Origin"), SITE_ORIGIN);
});

test("forwards an authenticated request to OpenAI", async (context) => {
  const originalFetch = globalThis.fetch;
  context.after(() => { globalThis.fetch = originalFetch; });
  globalThis.fetch = async (url, options) => {
    assert.equal(url, "https://api.openai.com/v1/responses");
    assert.equal(options.headers.Authorization, "Bearer openai-test");
    return new Response(JSON.stringify({
      model: "gpt-5.6-terra",
      output: [{type: "message", content: [{type: "output_text", text: "Răspuns test.", annotations: []}]}],
    }), {status: 200, headers: {"Content-Type": "application/json"}});
  };
  const password = "portfolio-test";
  const response = await worker.fetch(new Request("https://worker.example", {
    method: "POST",
    headers: {Origin: SITE_ORIGIN, "Content-Type": "application/json", "CF-Connecting-IP": "192.0.2.10"},
    body: JSON.stringify({
      message: "Cum arată riscul?",
      context: {portfolio: {position_count: 1}},
      history: [],
      accessToken: await expectedAccessToken(password),
    }),
  }), workerEnv({PORTFOLIO_PASSWORD: password}));
  assert.equal(response.status, 200);
  assert.equal(response.headers.get("Access-Control-Allow-Origin"), SITE_ORIGIN);
  assert.equal((await response.json()).text, "Răspuns test.");
});

test("falls back to Workers AI when OpenAI credit is exhausted", async (context) => {
  const originalFetch = globalThis.fetch;
  context.after(() => { globalThis.fetch = originalFetch; });
  let openAICalls = 0;
  globalThis.fetch = async () => {
    openAICalls += 1;
    return new Response(JSON.stringify({
      error: {code: "credit_balance_exhausted", type: "insufficient_quota"},
    }), {status: 429, headers: {"Content-Type": "application/json"}});
  };
  const password = "portfolio-test";
  let fallbackCalls = 0;
  const response = await worker.fetch(new Request("https://worker.example", {
    method: "POST",
    headers: {Origin: SITE_ORIGIN, "Content-Type": "application/json"},
    body: JSON.stringify({
      message: "Ce risc am?", context: {}, history: [],
      accessToken: await expectedAccessToken(password),
    }),
  }), workerEnv({
    PORTFOLIO_PASSWORD: password,
    AI: {run: async (model, input) => {
      fallbackCalls += 1;
      assert.equal(model, "@cf/openai/gpt-oss-120b");
      assert.equal(input.messages.at(-1).content, "Ce risc am?");
      return {choices: [{message: {content: "Folosește stopul existent."}}]};
    }},
  }));
  const payload = await response.json();
  assert.equal(response.status, 200);
  assert.equal(openAICalls, 1);
  assert.equal(fallbackCalls, 1);
  assert.equal(payload.provider, "cloudflare-workers-ai");
  assert.equal(payload.degraded, true);
  assert.match(payload.notice, /fără verificare web live/);
  assert.match(payload.notice, /creditul OpenAI este epuizat/);
});

test("retries a temporary OpenAI server error before using the answer", async (context) => {
  const originalFetch = globalThis.fetch;
  context.after(() => { globalThis.fetch = originalFetch; });
  let calls = 0;
  globalThis.fetch = async () => {
    calls += 1;
    if (calls === 1) {
      return new Response(JSON.stringify({error: {code: "server_error"}}), {
        status: 503,
        headers: {"Content-Type": "application/json", "x-request-id": "req_retry_test"},
      });
    }
    return new Response(JSON.stringify({
      model: "gpt-5.6-terra",
      output: [{type: "message", content: [{type: "output_text", text: "Recuperat.", annotations: []}]}],
    }), {status: 200, headers: {"Content-Type": "application/json"}});
  };
  const password = "portfolio-test";
  const response = await worker.fetch(new Request("https://worker.example", {
    method: "POST",
    headers: {Origin: SITE_ORIGIN, "Content-Type": "application/json"},
    body: JSON.stringify({
      message: "Analizează riscul.", context: {}, history: [],
      accessToken: await expectedAccessToken(password),
    }),
  }), workerEnv({PORTFOLIO_PASSWORD: password}));
  const payload = await response.json();
  assert.equal(response.status, 200);
  assert.equal(calls, 2);
  assert.equal(payload.provider, "openai");
  assert.equal(payload.text, "Recuperat.");
});

test("falls back to Workers AI for a non-429 OpenAI error", async (context) => {
  const originalFetch = globalThis.fetch;
  context.after(() => { globalThis.fetch = originalFetch; });
  globalThis.fetch = async () => new Response(JSON.stringify({
    error: {code: "model_not_found", type: "invalid_request_error"},
  }), {status: 400, headers: {"Content-Type": "application/json"}});
  const password = "portfolio-test";
  const response = await worker.fetch(new Request("https://worker.example", {
    method: "POST",
    headers: {Origin: SITE_ORIGIN, "Content-Type": "application/json"},
    body: JSON.stringify({
      message: "Ce oportunități sunt?", context: {}, history: [],
      accessToken: await expectedAccessToken(password),
    }),
  }), workerEnv({PORTFOLIO_PASSWORD: password}));
  const payload = await response.json();
  assert.equal(response.status, 200);
  assert.equal(payload.provider, "cloudflare-workers-ai");
  assert.equal(payload.reason, "model_not_found");
});

test("falls back when OpenAI returns a successful but unusable payload", async (context) => {
  const originalFetch = globalThis.fetch;
  context.after(() => { globalThis.fetch = originalFetch; });
  globalThis.fetch = async () => new Response(JSON.stringify({
    model: "gpt-5.6-terra", output: [],
  }), {status: 200, headers: {"Content-Type": "application/json"}});
  const password = "portfolio-test";
  const response = await worker.fetch(new Request("https://worker.example", {
    method: "POST",
    headers: {Origin: SITE_ORIGIN, "Content-Type": "application/json"},
    body: JSON.stringify({
      message: "Analizează riscul.", context: {}, history: [],
      accessToken: await expectedAccessToken(password),
    }),
  }), workerEnv({PORTFOLIO_PASSWORD: password}));
  const payload = await response.json();
  assert.equal(response.status, 200);
  assert.equal(payload.provider, "cloudflare-workers-ai");
  assert.equal(payload.reason, "openai_invalid_response");
});

test("falls back when the OpenAI request has a transport failure", async (context) => {
  const originalFetch = globalThis.fetch;
  context.after(() => { globalThis.fetch = originalFetch; });
  globalThis.fetch = async () => { throw new Error("connection reset"); };
  const password = "portfolio-test";
  const response = await worker.fetch(new Request("https://worker.example", {
    method: "POST",
    headers: {Origin: SITE_ORIGIN, "Content-Type": "application/json"},
    body: JSON.stringify({
      message: "Analizează piața.", context: {}, history: [],
      accessToken: await expectedAccessToken(password),
    }),
  }), workerEnv({PORTFOLIO_PASSWORD: password}));
  const payload = await response.json();
  assert.equal(response.status, 200);
  assert.equal(payload.provider, "cloudflare-workers-ai");
  assert.equal(payload.reason, "openai_transport_error");
});

test("labels an OpenAI timeout before falling back", async (context) => {
  const originalFetch = globalThis.fetch;
  context.after(() => { globalThis.fetch = originalFetch; });
  globalThis.fetch = async (_url, options) => new Promise((_resolve, reject) => {
    options.signal.addEventListener("abort", () => {
      const error = new Error("timed out");
      error.name = "AbortError";
      reject(error);
    }, {once: true});
  });
  const password = "portfolio-test";
  const response = await worker.fetch(new Request("https://worker.example", {
    method: "POST",
    headers: {Origin: SITE_ORIGIN, "Content-Type": "application/json"},
    body: JSON.stringify({
      message: "Analizează piața.", context: {}, history: [],
      accessToken: await expectedAccessToken(password),
    }),
  }), workerEnv({
    PORTFOLIO_PASSWORD: password,
    OPENAI_MAX_ATTEMPTS: 1,
    OPENAI_ATTEMPT_TIMEOUT_MS: 5,
    OPENAI_TOTAL_BUDGET_MS: 10,
  }));
  const payload = await response.json();
  assert.equal(response.status, 200);
  assert.equal(payload.reason, "openai_timeout");
  assert.match(payload.notice, /timpul alocat/);
});

test("returns 429 when the Cloudflare limiter rejects the request", async () => {
  const password = "portfolio-test";
  const response = await worker.fetch(new Request("https://worker.example", {
    method: "POST",
    headers: {Origin: SITE_ORIGIN, "Content-Type": "application/json", "CF-Connecting-IP": "192.0.2.11"},
    body: JSON.stringify({
      message: "Test",
      context: {},
      history: [],
      accessToken: await expectedAccessToken(password),
    }),
  }), workerEnv({
    PORTFOLIO_PASSWORD: password,
    PORTFOLIO_CHAT_RATE_LIMITER: {limit: async () => ({success: false})},
  }));
  assert.equal(response.status, 429);
});

test("keeps the personal chat available if the rate limiter binding fails", async (context) => {
  const originalFetch = globalThis.fetch;
  context.after(() => { globalThis.fetch = originalFetch; });
  globalThis.fetch = async () => new Response(JSON.stringify({
    model: "gpt-5.6-terra",
    output: [{type: "message", content: [{type: "output_text", text: "Disponibil.", annotations: []}]}],
  }), {status: 200, headers: {"Content-Type": "application/json"}});
  const password = "portfolio-test";
  const response = await worker.fetch(new Request("https://worker.example", {
    method: "POST",
    headers: {Origin: SITE_ORIGIN, "Content-Type": "application/json"},
    body: JSON.stringify({
      message: "Test", context: {}, history: [],
      accessToken: await expectedAccessToken(password),
    }),
  }), workerEnv({
    PORTFOLIO_PASSWORD: password,
    PORTFOLIO_CHAT_RATE_LIMITER: {limit: async () => { throw new Error("binding unavailable"); }},
  }));
  assert.equal(response.status, 200);
  assert.equal((await response.json()).text, "Disponibil.");
});
