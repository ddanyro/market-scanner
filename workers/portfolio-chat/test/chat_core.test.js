import test from "node:test";
import assert from "node:assert/strict";
import {
  buildCloudflareAIRequest,
  buildOpenAIRequest,
  CLOUDFLARE_FALLBACK_MODEL,
  expectedAccessToken,
  extractCloudflareAIAnswer,
  extractOpenAIAnswer,
  selectContextForMessage,
  validateChatRequest,
} from "../src/chat_core.js";

test("validates the derived portfolio token and trims history", async () => {
  const password = "secret";
  const history = Array.from({length: 12}, (_, index) => ({
    role: index % 2 ? "assistant" : "user", content: `m${index}`,
  }));
  const result = await validateChatRequest({
    message: "Ce risc am?",
    accessToken: await expectedAccessToken(password),
    context: {portfolio: {position_count: 2}},
    history,
  }, password);
  assert.equal(result.history.length, 8);
  assert.equal(result.message, "Ce risc am?");
});

test("builds a bounded Workers AI continuity request without claiming web access", () => {
  const request = buildCloudflareAIRequest({
    message: "Ce cumpăr?", contextJson: "{}", history: [{role: "user", content: "Salut"}],
  });
  assert.equal(request.max_tokens, 1800);
  assert.equal(request.messages.at(-1).content, "Ce cumpăr?");
  assert.match(request.messages[0].content, /Nu ai căutare web live/);
});

test("extracts and labels a degraded Workers AI answer", () => {
  const answer = extractCloudflareAIAnswer({
    choices: [{message: {content: "Analiză locală."}}],
  }, "credit_balance_exhausted");
  assert.equal(answer.text, "Analiză locală.");
  assert.equal(answer.model, CLOUDFLARE_FALLBACK_MODEL);
  assert.equal(answer.provider, "cloudflare-workers-ai");
  assert.equal(answer.degraded, true);
  assert.match(answer.notice, /fără verificare web live/);
});

test("rejects an invalid portfolio token", async () => {
  await assert.rejects(() => validateChatRequest({
    message: "Test", accessToken: "bad", context: {},
  }, "secret"), /neautorizat/i);
});

test("selects only relevant context for focused questions", () => {
  const context = {
    schema: "v1",
    portfolio: {value: 1},
    positions: [{symbol: "NVDA"}],
    broker_liquidity: {cash: 10},
    market_context: {vix: 15},
    buy_candidates: [{symbol: "MSFT"}],
    us_sector_rotation: {technology: "strong"},
    evidence: {items: [{title: "News"}]},
    rates: {fed: 4},
  };
  const news = selectContextForMessage(context, "Care sunt știrile recente?", true);
  assert.ok(news.evidence);
  assert.equal(news.buy_candidates, undefined);
  assert.equal(news.rates, undefined);

  const buy = selectContextForMessage(context, "Ce instrument cumpăr?", false);
  assert.ok(buy.buy_candidates);
  assert.ok(buy.us_sector_rotation);
  assert.equal(buy.evidence, undefined);

  const risk = selectContextForMessage(context, "Ce risc am în portofoliu?", false);
  assert.ok(risk.positions);
  assert.ok(risk.broker_liquidity);
  assert.equal(risk.buy_candidates, undefined);
  assert.equal(risk.evidence, undefined);

  assert.equal(selectContextForMessage(context, "Ce părere ai?"), context);
});

test("uses Responses API fields, Terra, explicit caching, conditional web search, and no storage", () => {
  const request = buildOpenAIRequest({
    message: "Care sunt știrile de azi?", contextJson: "{}", history: [],
    useWebSearch: true,
  });
  assert.equal(request.model, "gpt-5.6-terra");
  assert.equal(request.store, false);
  assert.deepEqual(request.reasoning, {effort: "low"});
  assert.equal(request.prompt_cache_key, "market-scanner:portfolio-chat:v2");
  assert.deepEqual(request.prompt_cache_options, {mode: "explicit", ttl: "30m"});
  assert.deepEqual(request.tools, [{type: "web_search"}]);
  assert.match(request.input[0].content[0].text, /Nu inventa/);
  assert.deepEqual(
    request.input[0].content[0].prompt_cache_breakpoint,
    {mode: "explicit"},
  );
  assert.deepEqual(
    request.input[0].content[1].prompt_cache_breakpoint,
    {mode: "explicit"},
  );
});

test("extracts text and clickable citation coordinates", () => {
  const answer = extractOpenAIAnswer({
    model: "gpt-5.6-terra",
    usage: {
      input_tokens: 1200,
      output_tokens: 80,
      total_tokens: 1280,
      input_tokens_details: {cached_tokens: 900},
    },
    output: [{type: "message", content: [{
      type: "output_text", text: "Vezi sursa.", annotations: [{
        type: "url_citation", start_index: 5, end_index: 10,
        url: "https://example.com/report", title: "Raport",
      }],
    }]}],
  });
  assert.equal(answer.text, "Vezi sursa.");
  assert.equal(answer.citations[0].title, "Raport");
  assert.equal(answer.usage.cached_tokens, 900);
  assert.equal(answer.usage.uncached_input_tokens, 300);
  assert.ok(answer.usage.estimated_cost_usd > 0);
});
