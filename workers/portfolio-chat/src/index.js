import {
  buildCloudflareAIRequest,
  buildOpenAIRequest,
  CLOUDFLARE_FALLBACK_MODEL,
  extractCloudflareAIAnswer,
  extractOpenAIAnswer,
  expectedAccessToken,
  safeTokenEqual,
  validateChatRequest,
} from "./chat_core.js";

const ALLOWED_ORIGIN = "https://ddanyro.github.io";
const WORKER_ORIGIN = "https://market-scanner-portfolio-chat.daniel-dragomir.workers.dev";
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
// Responses that combine a broad portfolio context with web search regularly
// need more than 35 seconds.  The old deadline aborted healthy OpenAI requests
// before the model could finish its search and synthesis.
const OPENAI_ATTEMPT_TIMEOUT_MS = 90000;
const OPENAI_TOTAL_BUDGET_MS = 120000;
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

function reportProgress(callback, stage, message, details = {}) {
  if (typeof callback !== "function") return;
  try {
    callback({stage, message, ...details, at: new Date().toISOString()});
  } catch {
    // Progress reporting must never interrupt the actual model request.
  }
}

async function requestOpenAI(env, validated, onProgress = null) {
  const startedAt = Date.now();
  const maxAttempts = Math.max(1, Number(env.OPENAI_MAX_ATTEMPTS) || OPENAI_MAX_ATTEMPTS);
  const timeoutMs = Math.max(1, Number(env.OPENAI_ATTEMPT_TIMEOUT_MS) || OPENAI_ATTEMPT_TIMEOUT_MS);
  const totalBudgetMs = Math.max(timeoutMs, Number(env.OPENAI_TOTAL_BUDGET_MS) || OPENAI_TOTAL_BUDGET_MS);
  const configuredRetryBaseMs = Number(env.OPENAI_RETRY_BASE_MS);
  const retryBaseMs = Number.isFinite(configuredRetryBaseMs)
    ? Math.max(0, configuredRetryBaseMs)
    : OPENAI_RETRY_BASE_MS;
  let webSearchEnabled = validated.useWebSearch;
  let webSearchDowngraded = false;
  let compatibilityMode = false;
  let lastFailure = null;

  reportProgress(
    onProgress,
    validated.useWebSearch ? "openai_web_search" : "openai_analysis",
    validated.useWebSearch
      ? "OpenAI analizează datele și caută informații recente pe web…"
      : "OpenAI analizează datele portofoliului…",
    {web_search: validated.useWebSearch},
  );

  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    const remainingBudgetMs = totalBudgetMs - (Date.now() - startedAt);
    if (remainingBudgetMs <= 0) break;
    const controller = new AbortController();
    const timer = setTimeout(
      () => controller.abort(), Math.min(timeoutMs, remainingBudgetMs),
    );
    let response = null;
    let payload = {};
    if (attempt > 1) {
      reportProgress(onProgress, "openai_retry", `Reîncerc OpenAI (${attempt}/${maxAttempts})…`, {
        attempt, max_attempts: maxAttempts,
      });
    }
    try {
      response = await fetch("https://api.openai.com/v1/responses", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${env.OPENAI_API_KEY}`,
        },
        body: JSON.stringify(buildOpenAIRequest({
          ...validated,
          useWebSearch: webSearchEnabled,
          compatibilityMode,
        })),
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
        return {
          response, payload, attempt, elapsedMs, webSearchDowngraded,
          compatibilityMode,
        };
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
        error_param: payload?.error?.param || null,
        error_message: String(payload?.error?.message || "").slice(0, 500) || null,
        ...openAITelemetry(response),
      }));
      // Some API/account combinations can reject an otherwise documented
      // optional Responses field with `invalid_value`. Retry the same model,
      // question and dashboard context using only the stable core payload.
      if (response.status === 400 && reason === "invalid_value"
          && !compatibilityMode && attempt < maxAttempts) {
        reportProgress(
          onProgress,
          "openai_compatibility_retry",
          "OpenAI a respins un parametru opțional; reîncerc aceeași analiză în mod compatibil…",
          {attempt},
        );
        webSearchDowngraded = webSearchEnabled;
        webSearchEnabled = false;
        compatibilityMode = true;
        continue;
      }
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
  return [ALLOWED_ORIGIN, WORKER_ORIGIN].includes(origin) ? {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Vary": "Origin, Authorization",
  } : {};
}

function isPublicRuntimeOrigin(origin) {
  if (!origin || [ALLOWED_ORIGIN, WORKER_ORIGIN].includes(origin)) return true;
  try {
    const parsed = new URL(origin);
    return parsed.protocol === "http:"
      && ["localhost", "127.0.0.1", "[::1]"].includes(parsed.hostname);
  } catch {
    return false;
  }
}

function publicRuntimeCorsHeaders(origin) {
  return origin && isPublicRuntimeOrigin(origin) ? {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Headers": "Authorization, Content-Type",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Vary": "Origin",
  } : {};
}

function runtimeJsonResponse(payload, status, origin) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      ...publicRuntimeCorsHeaders(origin),
    },
  });
}

async function runtimeResponse(request, env, origin, artifactName) {
  if (!isPublicRuntimeOrigin(origin)) {
    return runtimeJsonResponse({error: "Origine neautorizată."}, 403, origin);
  }
  if (request.method === "OPTIONS") {
    return new Response(null, {status: 204, headers: publicRuntimeCorsHeaders(origin)});
  }
  if (request.method !== "GET") {
    return runtimeJsonResponse({error: "Metodă neacceptată."}, 405, origin);
  }
  const authorization = String(request.headers.get("Authorization") || "");
  const receivedToken = authorization.replace(/^Bearer\s+/i, "").trim();
  const expectedToken = await expectedAccessToken(env.PORTFOLIO_PASSWORD);
  if (!env.PORTFOLIO_PASSWORD
      || !(await safeTokenEqual(receivedToken, expectedToken))) {
    return runtimeJsonResponse({error: "Autentificare necesară."}, 401, origin);
  }
  if ((!env.MARKET_SCANNER_DATA || typeof env.MARKET_SCANNER_DATA.get !== "function")
      && (!env.SHADOW_R2_ACCOUNT_ID || !env.SHADOW_R2_ACCESS_KEY_ID
          || !env.SHADOW_R2_SECRET_ACCESS_KEY)) {
    return runtimeJsonResponse({error: "Stocarea dashboardului nu este configurată."}, 503, origin);
  }
  const manifestObject = await runtimeObject(env, RUNTIME_MANIFEST_KEY);
  if (!manifestObject) {
    return runtimeJsonResponse({error: "Manifestul dashboardului lipsește."}, 503, origin);
  }
  const manifest = await manifestObject.json();
  const descriptor = manifest?.artifacts?.[artifactName];
  if (!descriptor || descriptor.private) {
    return runtimeJsonResponse({error: "Artefact indisponibil."}, 404, origin);
  }
  const artifact = await runtimeObject(env, descriptor.key);
  if (!artifact) {
    return runtimeJsonResponse({error: "Versiunea dashboardului lipsește."}, 503, origin);
  }
  const headers = new Headers({
    "Content-Type": descriptor.content_type || "application/octet-stream",
    "Cache-Control": "private, max-age=60, must-revalidate",
    "ETag": `\"${descriptor.sha256}\"`,
    "X-Content-Type-Options": "nosniff",
  });
  for (const [name, value] of Object.entries(publicRuntimeCorsHeaders(origin))) {
    headers.set(name, value);
  }
  const artifactBody = artifact.body instanceof ReadableStream
    ? artifact.body
    : new Response(artifact.body).body;
  if (descriptor.content_encoding === "gzip") {
    headers.set("Content-Encoding", "gzip");
  }
  const responseInit = {status: 200, headers};
  if (descriptor.content_encoding === "gzip") {
    // R2 already stores the exact gzip bytes. Without manual encoding mode,
    // Cloudflare may apply gzip again and browsers receive a double-gzip body.
    responseInit.encodeBody = "manual";
  }
  return new Response(artifactBody, responseInit);
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

function streamChatResponse(env, validated, origin) {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      let closed = false;
      const send = (event, payload) => {
        if (closed) return;
        controller.enqueue(encoder.encode(
          `event: ${event}\ndata: ${JSON.stringify(payload)}\n\n`,
        ));
      };
      const close = () => {
        if (!closed) {
          closed = true;
          controller.close();
        }
      };
      const fail = (message, reason = "stream_error") => {
        send("error", {error: message, reason});
        close();
      };

      send("progress", {
        stage: "context_ready",
        message: "Am pregătit datele relevante din portofoliu și ordine…",
        positions: Array.isArray(validated.context?.positions)
          ? validated.context.positions.length : 0,
        active_buy_orders: Array.isArray(validated.context?.active_buy_orders)
          ? validated.context.active_buy_orders.length : 0,
        context_chars: validated.contextJson.length,
        at: new Date().toISOString(),
      });

      (async () => {
        let openAIResult;
        try {
          openAIResult = await requestOpenAI(
            env, validated, (payload) => send("progress", payload),
          );
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
          if (validated.continuation) {
            fail("GPT nu a putut continua acum. Reîncearcă folosind același buton.", reason);
            return;
          }
          send("progress", {
            stage: "cloudflare_fallback",
            message: "OpenAI nu a finalizat cererea; pornesc serviciul AI de rezervă…",
            reason,
            at: new Date().toISOString(),
          });
          const fallbackResponse = await cloudflareFallbackResponse(
            env, validated, reason, origin,
          );
          if (!fallbackResponse) {
            fail("Nici OpenAI, nici serviciul AI de rezervă nu au putut răspunde.", "both_providers_unavailable");
            return;
          }
          send("result", await fallbackResponse.json());
          close();
          return;
        }

        try {
          send("progress", {
            stage: "finalizing",
            message: "Formatez concluziile și sursele…",
            at: new Date().toISOString(),
          });
          const answer = extractOpenAIAnswer(openAIResult.payload);
          if (openAIResult.compatibilityMode) {
            answer.degraded = true;
            answer.reason = "openai_invalid_value_recovered";
            answer.notice = openAIResult.webSearchDowngraded
              ? "GPT a răspuns folosind datele dashboardului; căutarea web și parametrii opționali respinși de endpoint au fost omiși pentru această cerere."
              : "GPT a răspuns după omiterea parametrilor opționali respinși de endpoint; modelul și datele dashboardului au rămas neschimbate.";
          }
          console.log(JSON.stringify({
            event: "openai_portfolio_chat_usage",
            model: answer.model,
            usage: answer.usage,
            attempt: openAIResult.attempt,
            elapsed_ms: openAIResult.elapsedMs,
          }));
          send("result", answer);
          close();
        } catch (parseError) {
          console.error(JSON.stringify({
            event: "openai_portfolio_chat_invalid_response",
            message: String(parseError && parseError.message || parseError),
          }));
          if (validated.continuation) {
            fail("GPT nu a returnat o continuare utilizabilă. Reîncearcă folosind același buton.", "openai_invalid_response");
            return;
          }
          send("progress", {
            stage: "cloudflare_fallback",
            message: "Răspunsul OpenAI nu este utilizabil; pornesc serviciul AI de rezervă…",
            reason: "openai_invalid_response",
            at: new Date().toISOString(),
          });
          const fallbackResponse = await cloudflareFallbackResponse(
            env, validated, "openai_invalid_response", origin,
          );
          if (!fallbackResponse) {
            fail("Nici OpenAI, nici serviciul AI de rezervă nu au putut răspunde.", "both_providers_unavailable");
            return;
          }
          send("result", await fallbackResponse.json());
          close();
        }
      })().catch((error) => {
        console.error(JSON.stringify({
          event: "portfolio_chat_stream_failed",
          message: String(error && error.message || error),
        }));
        fail("Chatul AI este temporar indisponibil.");
      });
    },
  });
  return new Response(stream, {
    status: 200,
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Accel-Buffering": "no",
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
    if (![ALLOWED_ORIGIN, WORKER_ORIGIN].includes(origin)) {
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
      if (body.streamProgress === true) {
        return streamChatResponse(env, validated, origin);
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
        // A continuation must stay with the provider that authored the
        // partial answer. Switching to Workers AI here loses the exact
        // reasoning/thread and produces a visibly unrelated continuation.
        if (validated.continuation) {
          return jsonResponse({
            error: "GPT nu a putut continua acum. Reîncearcă folosind același buton.",
            reason,
            retryable: true,
          }, 503, origin);
        }
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
        if (openAIResult.compatibilityMode) {
          answer.degraded = true;
          answer.reason = "openai_invalid_value_recovered";
          answer.notice = openAIResult.webSearchDowngraded
            ? "GPT a răspuns folosind datele dashboardului; căutarea web și parametrii opționali respinși de endpoint au fost omiși pentru această cerere."
            : "GPT a răspuns după omiterea parametrilor opționali respinși de endpoint; modelul și datele dashboardului au rămas neschimbate.";
        }
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
        if (validated.continuation) {
          return jsonResponse({
            error: "GPT nu a returnat o continuare utilizabilă. Reîncearcă folosind același buton.",
            reason: "openai_invalid_response",
            retryable: true,
          }, 503, origin);
        }
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
