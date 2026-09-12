import {
  buildCloudflareAIRequest,
  buildOpenAIRequest,
  CLOUDFLARE_FALLBACK_MODEL,
  extractCloudflareAIAnswer,
  extractOpenAIAnswer,
  validateChatRequest,
} from "./chat_core.js";

const ALLOWED_ORIGIN = "https://ddanyro.github.io";
const RUNTIME_MANIFEST_KEY = "market-scanner-runtime/v1/manifest.json";
const PUBLIC_RUNTIME_ARTIFACTS = new Map([
  ["/runtime/index.html", "dashboard-html"],
  ["/runtime/watchlist_compact.json", "watchlist-compact"],
  ["/runtime/watchlist_details.json", "watchlist-details"],
]);
const OPENAI_QUOTA_CODES = new Set([
  "credit_balance_exhausted",
  "organization_spend_limit_exceeded",
  "project_spend_limit_exceeded",
  "organization_usage_limit_exceeded",
]);
const OPENAI_RETRYABLE_STATUSES = new Set([408, 409, 429, 500, 502, 503, 504]);
const OPENAI_MAX_ATTEMPTS = 3;
const OPENAI_ATTEMPT_TIMEOUT_MS = 35000;
const OPENAI_TOTAL_BUDGET_MS = 65000;
const OPENAI_RETRY_BASE_MS = 500;
const OPENAI_MAX_RETRY_DELAY_MS = 5000;

const textEncoder = new TextEncoder();

function hex(bytes) {
  return Array.from(new Uint8Array(bytes), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

async function sha256(value) {
  const bytes = typeof value === "string" ? textEncoder.encode(value) : value;
  return hex(await crypto.subtle.digest("SHA-256", bytes));
}

async function hmacSha256(key, value) {
  const cryptoKey = await crypto.subtle.importKey(
    "raw", key, {name: "HMAC", hash: "SHA-256"}, false, ["sign"],
  );
  return new Uint8Array(await crypto.subtle.sign("HMAC", cryptoKey, textEncoder.encode(value)));
}

function uriPart(value) {
  return encodeURIComponent(value).replace(/[!'()*]/g, (character) => (
    `%${character.charCodeAt(0).toString(16).toUpperCase()}`
  ));
}

async function signedR2Get(env, key) {
  const accountId = String(env.SHADOW_R2_ACCOUNT_ID || "").trim();
  const accessKey = String(env.SHADOW_R2_ACCESS_KEY_ID || "").trim();
  const secretKey = String(env.SHADOW_R2_SECRET_ACCESS_KEY || "").trim();
  const bucket = String(env.SHADOW_R2_BUCKET || "market-scanner-shadow").trim();
  if (!accountId || !accessKey || !secretKey || !bucket) return null;

  const now = new Date();
  const amzDate = now.toISOString().replace(/[:-]|\.\d{3}/g, "");
  const dateStamp = amzDate.slice(0, 8);
  const host = `${accountId}.r2.cloudflarestorage.com`;
  const canonicalUri = `/${[bucket, ...key.split("/")].map(uriPart).join("/")}`;
  const payloadHash = await sha256(new Uint8Array());
  const canonicalHeaders = `host:${host}\nx-amz-content-sha256:${payloadHash}\nx-amz-date:${amzDate}\n`;
  const signedHeaders = "host;x-amz-content-sha256;x-amz-date";
  const canonicalRequest = [
    "GET", canonicalUri, "", canonicalHeaders, signedHeaders, payloadHash,
  ].join("\n");
  const scope = `${dateStamp}/auto/s3/aws4_request`;
  const stringToSign = [
    "AWS4-HMAC-SHA256", amzDate, scope, await sha256(textEncoder.encode(canonicalRequest)),
  ].join("\n");
  const dateKey = await hmacSha256(textEncoder.encode(`AWS4${secretKey}`), dateStamp);
  const regionKey = await hmacSha256(dateKey, "auto");
  const serviceKey = await hmacSha256(regionKey, "s3");
  const signingKey = await hmacSha256(serviceKey, "aws4_request");
  const signature = hex(await hmacSha256(signingKey, stringToSign));
  const response = await fetch(`https://${host}${canonicalUri}`, {headers: {
    "x-amz-content-sha256": payloadHash,
    "x-amz-date": amzDate,
    "Authorization": `AWS4-HMAC-SHA256 Credential=${accessKey}/${scope},SignedHeaders=${signedHeaders},Signature=${signature}`,
  }});
  if (response.status === 404) return null;
  if (!response.ok) throw new Error(`R2 GET failed with HTTP ${response.status}`);
  return response;
}

async function runtimeObject(env, key) {
  if (env.MARKET_SCANNER_DATA && typeof env.MARKET_SCANNER_DATA.get === "function") {
    return env.MARKET_SCANNER_DATA.get(key);
  }
  return signedR2Get(env, key);
}

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

function isQuotaError(payload) {
  return OPENAI_QUOTA_CODES.has(String(payload?.error?.code || "").trim());
}

function retryAfterMs(response) {
  const value = String(response.headers.get("Retry-After") || "").trim();
  if (!value) return null;
  const seconds = Number(value);
  if (Number.isFinite(seconds) && seconds >= 0) return seconds * 1000;
  const date = Date.parse(value);
  return Number.isFinite(date) ? Math.max(date - Date.now(), 0) : null;
}

function retryDelayMs(response, attempt, baseMs) {
  const requestedDelay = response ? retryAfterMs(response) : null;
  if (requestedDelay !== null) return requestedDelay + Math.floor(Math.random() * 250);
  return Math.min(baseMs * (2 ** (attempt - 1)), OPENAI_MAX_RETRY_DELAY_MS)
    + Math.floor(Math.random() * 250);
}

function wait(delayMs) {
  return new Promise((resolve) => setTimeout(resolve, delayMs));
}

function openAITelemetry(response) {
  return {
    request_id: response?.headers.get("x-request-id") || null,
    processing_ms: response?.headers.get("openai-processing-ms") || null,
    ratelimit_remaining_requests: response?.headers.get("x-ratelimit-remaining-requests") || null,
    ratelimit_remaining_tokens: response?.headers.get("x-ratelimit-remaining-tokens") || null,
    retry_after: response?.headers.get("Retry-After") || null,
  };
}

async function requestOpenAI(env, validated) {
  const startedAt = Date.now();
  const maxAttempts = Math.max(1, Number(env.OPENAI_MAX_ATTEMPTS) || OPENAI_MAX_ATTEMPTS);
  const timeoutMs = Math.max(1, Number(env.OPENAI_ATTEMPT_TIMEOUT_MS) || OPENAI_ATTEMPT_TIMEOUT_MS);
  const totalBudgetMs = Math.max(timeoutMs, Number(env.OPENAI_TOTAL_BUDGET_MS) || OPENAI_TOTAL_BUDGET_MS);
  const configuredRetryBaseMs = Number(env.OPENAI_RETRY_BASE_MS);
  const retryBaseMs = Number.isFinite(configuredRetryBaseMs)
    ? Math.max(0, configuredRetryBaseMs)
    : OPENAI_RETRY_BASE_MS;
  const requestBody = JSON.stringify(buildOpenAIRequest(validated));
  let lastFailure = null;

  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    const remainingBudgetMs = totalBudgetMs - (Date.now() - startedAt);
    if (remainingBudgetMs <= 0) break;
    const controller = new AbortController();
    const timer = setTimeout(
      () => controller.abort(), Math.min(timeoutMs, remainingBudgetMs),
    );
    let response = null;
    let payload = {};
    try {
      response = await fetch("https://api.openai.com/v1/responses", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${env.OPENAI_API_KEY}`,
        },
        body: requestBody,
        signal: controller.signal,
      });
      payload = await response.json().catch(() => ({}));
      const elapsedMs = Date.now() - startedAt;
      if (response.ok) {
        console.log(JSON.stringify({
          event: "openai_portfolio_chat_request_succeeded",
          attempt,
          elapsed_ms: elapsedMs,
          raw_context_chars: validated.rawContextChars,
          context_chars: validated.contextJson.length,
          web_search_enabled: validated.useWebSearch,
          ...openAITelemetry(response),
        }));
        return {response, payload, attempt, elapsedMs};
      }

      const reason = openAIHttpReason(response, payload);
      const retryable = OPENAI_RETRYABLE_STATUSES.has(response.status) && !isQuotaError(payload);
      lastFailure = {response, payload, reason, attempt, elapsedMs};
      console.error(JSON.stringify({
        event: "openai_portfolio_chat_attempt_failed",
        status: response.status,
        code: payload?.error?.code,
        type: payload?.error?.type,
        reason,
        retryable,
        attempt,
        elapsed_ms: elapsedMs,
        raw_context_chars: validated.rawContextChars,
        context_chars: validated.contextJson.length,
        web_search_enabled: validated.useWebSearch,
        ...openAITelemetry(response),
      }));
      if (!retryable || attempt >= maxAttempts) break;
      const delayMs = retryDelayMs(response, attempt, retryBaseMs);
      if (elapsedMs + delayMs >= totalBudgetMs) break;
      await wait(delayMs);
    } catch (error) {
      const elapsedMs = Date.now() - startedAt;
      const timedOut = error?.name === "AbortError";
      const reason = timedOut ? "openai_timeout" : "openai_transport_error";
      lastFailure = {response: null, payload: {}, reason, attempt, elapsedMs, error};
      console.error(JSON.stringify({
        event: "openai_portfolio_chat_attempt_failed",
        reason,
        retryable: true,
        attempt,
        elapsed_ms: elapsedMs,
        raw_context_chars: validated.rawContextChars,
        context_chars: validated.contextJson.length,
        web_search_enabled: validated.useWebSearch,
        message: String(error?.message || error),
      }));
      if (attempt >= maxAttempts) break;
      const delayMs = retryDelayMs(null, attempt, retryBaseMs);
      if (elapsedMs + delayMs >= totalBudgetMs) break;
      await wait(delayMs);
    } finally {
      clearTimeout(timer);
    }
  }
  throw Object.assign(new Error(lastFailure?.reason || "openai_unavailable"), {
    openAIFailure: lastFailure,
  });
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
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Vary": "Origin",
  } : {};
}

async function runtimeResponse(request, env, origin, artifactName) {
  if (origin && origin !== ALLOWED_ORIGIN) {
    return jsonResponse({error: "Origine neautorizată."}, 403, origin);
  }
  if (request.method === "OPTIONS") {
    return new Response(null, {status: 204, headers: corsHeaders(origin)});
  }
  if (request.method !== "GET") {
    return jsonResponse({error: "Metodă neacceptată."}, 405, origin);
  }
  if ((!env.MARKET_SCANNER_DATA || typeof env.MARKET_SCANNER_DATA.get !== "function")
      && (!env.SHADOW_R2_ACCOUNT_ID || !env.SHADOW_R2_ACCESS_KEY_ID
          || !env.SHADOW_R2_SECRET_ACCESS_KEY)) {
    return jsonResponse({error: "Stocarea dashboardului nu este configurată."}, 503, origin);
  }
  const manifestObject = await runtimeObject(env, RUNTIME_MANIFEST_KEY);
  if (!manifestObject) {
    return jsonResponse({error: "Manifestul dashboardului lipsește."}, 503, origin);
  }
  const manifest = await manifestObject.json();
  const descriptor = manifest?.artifacts?.[artifactName];
  if (!descriptor || descriptor.private) {
    return jsonResponse({error: "Artefact indisponibil."}, 404, origin);
  }
  const artifact = await runtimeObject(env, descriptor.key);
  if (!artifact) {
    return jsonResponse({error: "Versiunea dashboardului lipsește."}, 503, origin);
  }
  const headers = new Headers({
    "Content-Type": descriptor.content_type || "application/octet-stream",
    "Cache-Control": "public, max-age=60, must-revalidate",
    "ETag": `\"${descriptor.sha256}\"`,
    "X-Content-Type-Options": "nosniff",
  });
  if (origin === ALLOWED_ORIGIN) {
    headers.set("Access-Control-Allow-Origin", ALLOWED_ORIGIN);
    headers.set("Vary", "Origin");
  }
  const artifactBody = artifact.body instanceof ReadableStream
    ? artifact.body
    : new Response(artifact.body).body;
  if (descriptor.content_encoding === "gzip") {
    headers.set("Content-Encoding", "gzip");
  }
  return new Response(artifactBody, {status: 200, headers});
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
    const artifactName = PUBLIC_RUNTIME_ARTIFACTS.get(new URL(request.url).pathname);
    if (artifactName) {
      return runtimeResponse(request, env, origin, artifactName);
    }
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
      let openAIResult;
      try {
        openAIResult = await requestOpenAI(env, validated);
      } catch (openAIError) {
        const failure = openAIError.openAIFailure || {};
        const reason = failure.reason || "openai_transport_error";
        console.error(JSON.stringify({
          event: "openai_portfolio_chat_failed",
          reason,
          status: failure.response?.status,
          code: failure.payload?.error?.code,
          attempt: failure.attempt,
          elapsed_ms: failure.elapsedMs,
          ...openAITelemetry(failure.response),
          message: String(openAIError && openAIError.message || openAIError),
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
      const payload = openAIResult.payload;
      try {
        const answer = extractOpenAIAnswer(payload);
        console.log(JSON.stringify({
          event: "openai_portfolio_chat_usage",
          model: answer.model,
          usage: answer.usage,
          attempt: openAIResult.attempt,
          elapsed_ms: openAIResult.elapsedMs,
        }));
        return jsonResponse(answer, 200, origin);
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
