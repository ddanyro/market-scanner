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

test("filters a large unrelated dashboard context before enforcing the model limit", async () => {
  const password = "secret";
  const result = await validateChatRequest({
    message: "Ce ordine de cumpărare am?",
    accessToken: await expectedAccessToken(password),
    context: {
      schema: "v3",
      positions: [{symbol: "NVDA"}],
      active_buy_orders: [{symbol: "MSFT", action: "BUY"}],
      active_sell_orders: [],
      order_summary: {total: 1, buy_count: 1, sell_count: 0},
      evidence: {items: [{body: "x".repeat(220000)}]},
      buy_candidates: [{body: "y".repeat(220000)}],
      market_overviews: {SUA: {body: "z".repeat(220000)}},
    },
  }, password);
  assert.equal(result.context.active_buy_orders[0].symbol, "MSFT");
  assert.equal(result.context.evidence, undefined);
  assert.equal(result.context.buy_candidates, undefined);
  assert.equal(result.context.market_overviews, undefined);
  assert.ok(result.contextJson.length < 180000);
  assert.ok(result.rawContextChars > 180000);
});

test("keeps the tail of a long assistant answer for a GPT continuation", async () => {
  const password = "secret";
  const longAnswer = "început-omis " + "x".repeat(17000) + " FINAL-IMPORTANT";
  const result = await validateChatRequest({
    message: "Continuă răspunsul.",
    continuation: true,
    accessToken: await expectedAccessToken(password),
    context: {},
    history: [{role: "assistant", content: longAnswer}],
  }, password);
  assert.equal(result.continuation, true);
  assert.match(result.history[0].content, /^\[Începutul răspunsului anterior/);
  assert.match(result.history[0].content, /FINAL-IMPORTANT$/);
  assert.ok(result.history[0].content.length > 2000);
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
  assert.equal(answer.complete, true);
});

test("marks a length-limited Workers AI response as incomplete", () => {
  const answer = extractCloudflareAIAnswer({
    choices: [{finish_reason: "length", message: {content: "Răspuns parțial."}}],
  }, "openai_unavailable");
  assert.equal(answer.complete, false);
  assert.equal(answer.incomplete_reason, "length");
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
    active_buy_orders: [{symbol: "AAPL", action: "BUY"}],
    active_sell_orders: [{symbol: "NVDA", action: "SELL"}],
    order_summary: {total: 2, buy_count: 1, sell_count: 1},
  };
  const news = selectContextForMessage(context, "Care sunt știrile recente?", true);
  assert.ok(news.evidence);
  assert.equal(news.buy_candidates, undefined);
  assert.equal(news.rates, undefined);

  const buy = selectContextForMessage(context, "Ce instrument cumpăr?", false);
  assert.ok(buy.buy_candidates);
  assert.equal(buy.active_buy_orders[0].symbol, "AAPL");
  assert.equal(buy.order_summary.buy_count, 1);
  assert.ok(buy.us_sector_rotation);
  assert.equal(buy.evidence, undefined);

  const risk = selectContextForMessage(context, "Ce risc am în portofoliu?", false);
  assert.ok(risk.positions);
  assert.ok(risk.broker_liquidity);
  assert.equal(risk.active_sell_orders[0].symbol, "NVDA");
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
  assert.equal(request.max_output_tokens, 4096);
  assert.deepEqual(request.reasoning, {effort: "low"});
  assert.equal(request.prompt_cache_key, "market-scanner:portfolio-chat:v3");
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
  assert.equal(answer.complete, true);
});

test("preserves partial OpenAI text and exposes incomplete status", () => {
  const answer = extractOpenAIAnswer({
    status: "incomplete",
    incomplete_details: {reason: "max_output_tokens"},
    output: [{type: "message", content: [{
      type: "output_text", text: "**Infer", annotations: [],
    }]}],
  });
  assert.equal(answer.text, "**Infer");
  assert.equal(answer.complete, false);
  assert.equal(answer.incomplete_reason, "max_output_tokens");
});
