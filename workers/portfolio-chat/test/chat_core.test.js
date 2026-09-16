import test from "node:test";
import assert from "node:assert/strict";
import {
  buildCloudflareAIRequest,
  buildOpenAIRequest,
  CLOUDFLARE_FALLBACK_MODEL,
  compactContextForModel,
  expectedAccessToken,
  extractCloudflareAIAnswer,
  extractOpenAIAnswer,
  selectContextForMessage,
  validateChatRequest,
} from "../src/chat_core.js";

test("compacts broad context while preserving positions and active orders", async () => {
  const password = "secret";
  const result = await validateChatRequest({
    message: "Analizează în ansamblu tot portofoliul și contextul pieței.",
    accessToken: await expectedAccessToken(password),
    context: {
      positions: [
        {symbol: "NVDA", shares: 10, chart_ohlc: "x".repeat(220000)},
        {symbol: "MSFT", shares: 5},
      ],
      active_buy_orders: [{symbol: "AAPL", action: "BUY", limit_price: 210}],
      active_sell_orders: [{symbol: "NVDA", action: "SELL", stop_price: 170}],
      market_overviews: {SUA: {analysis: "m".repeat(120000)}},
      current_ai_analysis: {portfolio_overview: "a".repeat(120000)},
    },
  }, password);
  assert.equal(result.contextCompacted, true);
  assert.equal(result.context.positions.length, 2);
  assert.equal(result.context.positions[0].symbol, "NVDA");
  assert.equal(result.context.positions[0].chart_ohlc, undefined);
  assert.equal(result.context.active_buy_orders[0].symbol, "AAPL");
  assert.equal(result.context.active_sell_orders[0].symbol, "NVDA");
  assert.equal(result.context.context_compaction.applied, true);
  assert.ok(result.contextJson.length < 180000);
});

test("leaves an already small context unchanged", () => {
  const context = {positions: [{symbol: "NVDA"}]};
  const result = compactContextForModel(context);
  assert.equal(result.compacted, false);
  assert.equal(result.context, context);
});

test("always fits exceptionally large relevant sections instead of returning 413", async () => {
  const password = "secret";
  const hugeRows = Array.from({length: 50}, (_, index) => ({
    symbol: `SYM${index}`,
    ...Object.fromEntries(Array.from({length: 10}, (_, field) => [
      `field_${field}`, `${field}-` + "d".repeat(180),
    ])),
  }));
  const result = await validateChatRequest({
    message: "Analizează toate datele disponibile.",
    accessToken: await expectedAccessToken(password),
    context: {
      positions: hugeRows,
      active_buy_orders: hugeRows,
      active_sell_orders: hugeRows,
      buy_candidates: hugeRows,
      market_overviews: {SUA: hugeRows, BVB: hugeRows},
    },
  }, password);
  assert.equal(result.contextCompacted, true);
  assert.ok(result.contextJson.length <= 180000);
  assert.equal(result.context.context_compaction.forced_budget, true);
  assert.ok(result.context.context_compaction.summarized_sections.length > 0);
});

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

test("prioritises any explicitly mentioned held position and active orders", () => {
  const context = {
    positions: [
      {symbol: "3USL", current_price_eur: 157.37, current_value_eur: 2045.81},
      {symbol: "PANW", current_price_eur: 372.2},
    ],
    active_buy_orders: [
      {symbol: "PANW", action: "BUY", effective_order_price: 350},
      {symbol: "MSFT", action: "BUY", effective_order_price: 410},
    ],
    active_sell_orders: [
      {symbol: "3USL", action: "SELL", effective_order_price: 150.651},
    ],
  };

  const selected = selectContextForMessage(
    context,
    "Care este pierderea pentru PANW și 3USL până la stop?",
  );
  assert.deepEqual(selected.requested_instruments.symbols, ["3USL", "PANW"]);
  assert.deepEqual(
    selected.requested_instruments.held_positions.map((item) => item.symbol),
    ["3USL", "PANW"],
  );
  assert.deepEqual(
    selected.requested_instruments.active_buy_orders.map((item) => item.symbol),
    ["PANW"],
  );
  assert.deepEqual(
    selected.requested_instruments.active_sell_orders.map((item) => item.symbol),
    ["3USL"],
  );
  assert.equal(selected.positions.length, 2);
  assert.equal(selected.active_buy_orders.length, 2);
});

test("matches symbols containing an exchange suffix without partial matches", () => {
  const selected = selectContextForMessage({
    positions: [{symbol: "LQQ.PA", current_price_eur: 100}],
    active_buy_orders: [],
    active_sell_orders: [],
  }, "Ce risc are LQQ.PA?");
  assert.deepEqual(selected.requested_instruments.symbols, ["LQQ.PA"]);
  assert.equal(selected.requested_instruments.held_positions[0].symbol, "LQQ.PA");
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

test("enables portfolio web search for legacy continuation payloads", async () => {
  const password = "secret";
  const result = await validateChatRequest({
    message: "Mă refer strict la ordinele de cumpărare.",
    continuation: true,
    webSearch: false,
    accessToken: await expectedAccessToken(password),
    context: {active_buy_orders: [{symbol: "MSFT"}]},
    history: [{role: "assistant", content: "Am analizat portofoliul."}],
  }, password);
  assert.equal(result.useWebSearch, true);
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
  assert.match(answer.notice, /^Răspuns AI de rezervă:/);
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
    tvbetetf_market: {current_price: 55.05, technical_verdict: "PRUDENȚĂ"},
    lqq_market: {current_price: 9.31, sma200: 8.39},
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
  assert.equal(news.tvbetetf_market.current_price, 55.05);
  assert.equal(news.lqq_market.sma200, 8.39);
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
  assert.match(request.input[0].content[0].text, /profit lunar de 3\.000 EUR/);
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

test("builds a minimal OpenAI compatibility request without optional fields", () => {
  const request = buildOpenAIRequest({
    message: "Cum arată riscul?", contextJson: "{}", history: [],
    useWebSearch: true, compatibilityMode: true,
  });
  assert.equal(request.model, "gpt-5.6-terra");
  assert.equal(request.store, false);
  assert.equal("reasoning" in request, false);
  assert.equal("max_output_tokens" in request, false);
  assert.equal("prompt_cache_key" in request, false);
  assert.equal("prompt_cache_options" in request, false);
  assert.equal("tools" in request, false);
  assert.equal("prompt_cache_breakpoint" in request.input[0].content[0], false);
  assert.equal("prompt_cache_breakpoint" in request.input[0].content[1], false);
});

test("serializes assistant history as Responses API output text", () => {
  const request = buildOpenAIRequest({
    message: "Mă refer strict la ordinele de cumpărare.",
    contextJson: "{}",
    history: [
      {role: "user", content: "Analizează ordinele."},
      {role: "assistant", content: "Am analizat ordinele de vânzare."},
    ],
    useWebSearch: false,
  });
  assert.equal(request.input[1].role, "user");
  assert.equal(request.input[1].content[0].type, "input_text");
  assert.equal(request.input[2].role, "assistant");
  assert.equal(request.input[2].content[0].type, "output_text");
  assert.equal(request.input.at(-1).role, "user");
  assert.equal(request.input.at(-1).content[0].type, "input_text");
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
