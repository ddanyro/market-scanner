import {
  buildCloudflareAIRequest,
  buildOpenAIRequest,
  CLOUDFLARE_FALLBACK_MODEL,
  extractCloudflareAIAnswer,
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

function openAIHttpReason(response, payload) {
  const code = String(payload?.error?.code || "").trim();
  if (response.status === 429) return safeOpenAIErrorReason(payload);
  return code || `openai_http_${response.status}`;
}

async function runCloudflareFallback(env, validated, reason) {
  if (!env.AI || typeof env.AI.run !== "function") {
    throw new Error("Bindingul Cloudflare Workers AI nu este configurat.");
  }
  const payload = await env.AI.run(
    CLOUDFLARE_FALLBACK_MODEL,
    buildCloudflareAIRequest(validated),
  );
  return extractCloudflareAIAnswer(payload, reason);
}

async function cloudflareFallbackResponse(env, validated, reason, origin) {
  try {
    const fallbackAnswer = await runCloudflareFallback(env, validated, reason);
    console.log(JSON.stringify({
      event: "portfolio_chat_cloudflare_fallback_used",
      reason,
      model: CLOUDFLARE_FALLBACK_MODEL,
    }));
    return jsonResponse(fallbackAnswer, 200, origin);
  } catch (fallbackError) {
    console.error(JSON.stringify({
      event: "portfolio_chat_cloudflare_fallback_failed",
      reason,
      message: String(fallbackError && fallbackError.message || fallbackError),
    }));
    return null;
  }
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
      let rateLimit = {success: true};
      try {
        rateLimit = await env.PORTFOLIO_CHAT_RATE_LIMITER.limit({key: rateKey});
      } catch (rateLimitError) {
        console.error(JSON.stringify({
          event: "portfolio_chat_rate_limiter_failed_open",
          message: String(rateLimitError && rateLimitError.message || rateLimitError),
        }));
      }
      if (!rateLimit.success) {
        return jsonResponse({error: "Prea multe întrebări. Reîncearcă peste câteva minute."}, 429, origin);
      }
      let openAIResponse;
      try {
        openAIResponse = await fetch("https://api.openai.com/v1/responses", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${env.OPENAI_API_KEY}`,
          },
          body: JSON.stringify(buildOpenAIRequest(validated)),
        });
      } catch (openAIError) {
        console.error(JSON.stringify({
          event: "openai_portfolio_chat_transport_failed",
          message: String(openAIError && openAIError.message || openAIError),
        }));
        const fallbackResponse = await cloudflareFallbackResponse(
          env, validated, "openai_transport_error", origin,
        );
        if (fallbackResponse) return fallbackResponse;
        return jsonResponse({
          error: "Nici OpenAI, nici serviciul AI de rezervă nu au putut răspunde.",
          reason: "both_providers_unavailable",
        }, 503, origin);
      }
      const payload = await openAIResponse.json().catch(() => ({}));
      if (!openAIResponse.ok) {
        const reason = openAIHttpReason(openAIResponse, payload);
        console.error(JSON.stringify({
          event: "openai_portfolio_chat_failed",
          status: openAIResponse.status,
          code: payload?.error?.code,
          type: payload?.error?.type,
        }));
        const fallbackResponse = await cloudflareFallbackResponse(
          env, validated, reason, origin,
        );
        if (fallbackResponse) return fallbackResponse;
        return jsonResponse({
          error: "Nici OpenAI, nici serviciul AI de rezervă nu au putut răspunde.",
          reason: "both_providers_unavailable",
        }, 503, origin);
      }
      try {
        return jsonResponse(extractOpenAIAnswer(payload), 200, origin);
      } catch (parseError) {
        console.error(JSON.stringify({
          event: "openai_portfolio_chat_invalid_response",
          message: String(parseError && parseError.message || parseError),
        }));
        const fallbackResponse = await cloudflareFallbackResponse(
          env, validated, "openai_invalid_response", origin,
        );
        if (fallbackResponse) return fallbackResponse;
        return jsonResponse({
          error: "Nici OpenAI, nici serviciul AI de rezervă nu au putut răspunde.",
          reason: "both_providers_unavailable",
        }, 503, origin);
      }
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
