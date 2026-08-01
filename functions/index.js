"use strict";

const {onRequest} = require("firebase-functions/v2/https");
const {logger} = require("firebase-functions");
const {
  buildOpenAIRequest,
  extractOpenAIAnswer,
  validateChatRequest,
} = require("./chat_core");

const recentRequests = new Map();
const WINDOW_MS = 5 * 60 * 1000;
const MAX_REQUESTS_PER_WINDOW = 12;

function enforceRateLimit(key) {
  const now = Date.now();
  const recent = (recentRequests.get(key) || []).filter((time) => now - time < WINDOW_MS);
  if (recent.length >= MAX_REQUESTS_PER_WINDOW) return false;
  recent.push(now);
  recentRequests.set(key, recent);
  return true;
}

exports.portfolioChat = onRequest({
  region: "europe-west1",
  cors: [
    "https://ddanyro.github.io",
    /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/,
  ],
  secrets: ["OPENAI_API_KEY", "PORTFOLIO_PASSWORD"],
  timeoutSeconds: 60,
  memory: "512MiB",
  maxInstances: 3,
}, async (request, response) => {
  response.set("Cache-Control", "no-store");
  if (request.method !== "POST") {
    response.status(405).json({error: "Metodă neacceptată."});
    return;
  }
  try {
    const validated = validateChatRequest(request.body, process.env.PORTFOLIO_PASSWORD);
    const rateKey = String(request.ip || request.get("x-forwarded-for") || "unknown");
    if (!enforceRateLimit(rateKey)) {
      response.status(429).json({error: "Prea multe întrebări. Reîncearcă peste câteva minute."});
      return;
    }
    const openAIResponse = await fetch("https://api.openai.com/v1/responses", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`,
      },
      body: JSON.stringify(buildOpenAIRequest(validated)),
      signal: AbortSignal.timeout(55000),
    });
    const payload = await openAIResponse.json().catch(() => ({}));
    if (!openAIResponse.ok) {
      logger.error("OpenAI portfolio chat failed", {
        status: openAIResponse.status,
        code: payload && payload.error && payload.error.code,
        type: payload && payload.error && payload.error.type,
      });
      response.status(openAIResponse.status === 429 ? 429 : 502).json({
        error: openAIResponse.status === 429
          ? "Serviciul AI a atins limita temporară. Reîncearcă în scurt timp."
          : "Serviciul AI nu a putut genera răspunsul.",
      });
      return;
    }
    response.status(200).json(extractOpenAIAnswer(payload));
  } catch (error) {
    const status = Number(error.statusCode) || (error.name === "TimeoutError" ? 504 : 500);
    if (status >= 500) logger.error("Portfolio chat request failed", error);
    response.status(status).json({
      error: status >= 500 ? "Chatul AI este temporar indisponibil." : error.message,
    });
  }
});
