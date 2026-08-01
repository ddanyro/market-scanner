"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const {
  buildOpenAIRequest,
  expectedAccessToken,
  extractOpenAIAnswer,
  validateChatRequest,
} = require("./chat_core");

test("validates the derived portfolio token and trims history", () => {
  const password = "secret";
  const history = Array.from({length: 12}, (_, index) => ({
    role: index % 2 ? "assistant" : "user", content: `m${index}`,
  }));
  const result = validateChatRequest({
    message: "Ce risc am?",
    accessToken: expectedAccessToken(password),
    context: {portfolio: {position_count: 2}},
    history,
  }, password);
  assert.equal(result.history.length, 8);
  assert.equal(result.message, "Ce risc am?");
});

test("rejects an invalid portfolio token", () => {
  assert.throws(() => validateChatRequest({
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
