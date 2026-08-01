import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";
import {expectedAccessToken} from "../src/chat_core.js";

const SITE_ORIGIN = "https://ddanyro.github.io";

function workerEnv(overrides = {}) {
  return {
    OPENAI_API_KEY: "openai-test",
    PORTFOLIO_PASSWORD: "portfolio-test",
    PORTFOLIO_CHAT_RATE_LIMITER: {limit: async () => ({success: true})},
    ...overrides,
  };
}

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
      model: "gpt-5.6-sol",
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
