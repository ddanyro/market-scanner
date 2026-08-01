import test from "node:test";
import assert from "node:assert/strict";
import {
  buildCloudflareAIRequest,
  buildOpenAIRequest,
  CLOUDFLARE_FALLBACK_MODEL,
  expectedAccessToken,
  extractCloudflareAIAnswer,
  extractOpenAIAnswer,
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
  const answer = extractCloudflareAIAnswer({response: "Analiză locală."}, "credit_balance_exhausted");
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

test("uses Responses API fields, Sol, web search, and no storage", () => {
  const request = buildOpenAIRequest({
    message: "Ce cumpăr?", contextJson: "{}", history: [],
  });
  assert.equal(request.model, "gpt-5.6-sol");
  assert.equal(request.store, false);
  assert.deepEqual(request.reasoning, {effort: "high"});
  assert.deepEqual(request.tools, [{type: "web_search"}]);
  assert.match(request.instructions, /Nu inventa/);
});

test("extracts text and clickable citation coordinates", () => {
  const answer = extractOpenAIAnswer({
    model: "gpt-5.6-sol-2026-07-01",
    output: [{type: "message", content: [{
      type: "output_text", text: "Vezi sursa.", annotations: [{
        type: "url_citation", start_index: 5, end_index: 10,
        url: "https://example.com/report", title: "Raport",
      }],
    }]}],
  });
  assert.equal(answer.text, "Vezi sursa.");
  assert.equal(answer.citations[0].title, "Raport");
});
