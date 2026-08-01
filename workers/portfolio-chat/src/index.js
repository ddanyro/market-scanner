import {
  buildOpenAIRequest,
  extractOpenAIAnswer,
  validateChatRequest,
} from "./chat_core.js";

const ALLOWED_ORIGIN = "https://ddanyro.github.io";
const OPENAI_QUOTA_CODES = new Set([
  "credit_balance_exhausted",
  "organization_spend_limit_exceeded",
  "project_spend_limit_exceeded",
  "organization_usage_limit_exceeded",
]);

function safeOpenAIErrorReason(payload) {
  const code = String(payload?.error?.code || "").trim();
  if (OPENAI_QUOTA_CODES.has(code)) return code;
  return code === "rate_limit_exceeded" ? code : "rate_limit";
}

function corsHeaders(origin) {
  return origin === ALLOWED_ORIGIN ? {
    "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Vary": "Origin",
  } : {};
}

function jsonResponse(payload, status, origin) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      ...corsHeaders(origin),
    },
  });
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    if (origin !== ALLOWED_ORIGIN) {
      return jsonResponse({error: "Origine neautorizată."}, 403, origin);
    }
    if (request.method === "OPTIONS") {
      return new Response(null, {status: 204, headers: corsHeaders(origin)});
    }
    if (request.method !== "POST") {
      return jsonResponse({error: "Metodă neacceptată."}, 405, origin);
    }
    try {
      const body = await request.json();
      const validated = await validateChatRequest(body, env.PORTFOLIO_PASSWORD);
      const rateKey = request.headers.get("CF-Connecting-IP") || "unknown";
      const rateLimit = await env.PORTFOLIO_CHAT_RATE_LIMITER.limit({key: rateKey});
      if (!rateLimit.success) {
        return jsonResponse({error: "Prea multe întrebări. Reîncearcă peste câteva minute."}, 429, origin);
      }
      const openAIResponse = await fetch("https://api.openai.com/v1/responses", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${env.OPENAI_API_KEY}`,
        },
        body: JSON.stringify(buildOpenAIRequest(validated)),
      });
      const payload = await openAIResponse.json().catch(() => ({}));
      if (!openAIResponse.ok) {
        const reason = safeOpenAIErrorReason(payload);
        console.error(JSON.stringify({
          event: "openai_portfolio_chat_failed",
          status: openAIResponse.status,
          code: payload?.error?.code,
          type: payload?.error?.type,
        }));
        return jsonResponse({
          error: openAIResponse.status === 429
            ? (OPENAI_QUOTA_CODES.has(reason)
              ? "Cheia OpenAI nu are credit disponibil sau a atins limita de utilizare. Verifică Billing și Limits în OpenAI Platform."
              : "Serviciul AI a atins limita temporară. Reîncearcă în scurt timp.")
            : "Serviciul AI nu a putut genera răspunsul.",
          ...(openAIResponse.status === 429 ? {reason} : {}),
        }, openAIResponse.status === 429 ? 429 : 502, origin);
      }
      return jsonResponse(extractOpenAIAnswer(payload), 200, origin);
    } catch (error) {
      const status = Number(error.statusCode) || 500;
      if (status >= 500) {
        console.error(JSON.stringify({
          event: "portfolio_chat_request_failed",
          message: String(error && error.message || error),
        }));
      }
      return jsonResponse({
        error: status >= 500 ? "Chatul AI este temporar indisponibil." : error.message,
      }, status, origin);
    }
  },
};
