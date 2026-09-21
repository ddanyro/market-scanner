"use strict";

(() => {
  const CONTENT_BRIDGE_VERSION = 3;
  if (window.__marketScannerTradevilleContentBridgeVersion === CONTENT_BRIDGE_VERSION) {
    // The service worker may inject the bridge into a tab that already received
    // the manifest content script. Never create a second polling loop.
    return;
  }
  window.__marketScannerTradevilleContentBridgeInstalled = true;
  window.__marketScannerTradevilleContentBridgeVersion = CONTENT_BRIDGE_VERSION;

  const REQUEST_SOURCE = "market-scanner-tradeville-extension-v2";
  const RESULT_SOURCE = "market-scanner-tradeville-page-v2";
  let activeJob = null;
  let activeDeadline = 0;
  let polling = false;

  async function sendBounded(message) {
    let timer;
    try {
      return await Promise.race([
        chrome.runtime.sendMessage(message),
        new Promise((_, reject) => {
          timer = setTimeout(() => reject(new Error("extension_message_timeout")), 5000);
        })
      ]);
    } finally {
      clearTimeout(timer);
    }
  }

async function pollBridge() {
  if (window.__marketScannerTradevilleContentBridgeVersion !== CONTENT_BRIDGE_VERSION) return;
  if (activeJob && Date.now() >= activeDeadline) activeJob = null;
  if (activeJob || polling) return;
  polling = true;
  let response;
  try {
    response = await sendBounded({ type: "TRADEVILLE_BRIDGE_POLL" });
  } catch (_) {
    return;
  } finally {
    polling = false;
  }
  if (!response?.ok || !response.job) return;
  if (window.__marketScannerTradevilleContentBridgeVersion !== CONTENT_BRIDGE_VERSION) return;
  activeDeadline = Number(response.job.expiresAt) || (Date.now() + 50000);
  if (Date.now() >= activeDeadline) return;
  activeJob = response.job.id;
  window.postMessage({
    source: REQUEST_SOURCE,
    type: "SYNC",
    jobId: response.job.id,
    token: response.job.token,
    historyStart: response.job.historyStart
  }, window.location.origin);
}

window.addEventListener("message", async event => {
  if (window.__marketScannerTradevilleContentBridgeVersion !== CONTENT_BRIDGE_VERSION) return;
  if (event.source !== window || event.origin !== window.location.origin) return;
  const data = event.data;
  if (!data || data.source !== RESULT_SOURCE || data.type !== "SYNC_RESULT") return;
  if (!activeJob || data.jobId !== activeJob) return;
  try {
    await sendBounded({
      type: "TRADEVILLE_BRIDGE_RESULT",
      jobId: data.jobId,
      token: data.token,
      ok: data.ok === true,
      snapshot: data.snapshot || null,
      error: data.error || null
    });
  } catch (_) {
    // A stopped bridge or reloaded extension must not wedge future syncs.
  } finally {
    if (activeJob === data.jobId) activeJob = null;
  }
});

  setInterval(pollBridge, 1000);
  pollBridge();
  chrome.runtime.sendMessage({ type: "TRADEVILLE_BRIDGE_READY" }).catch(() => {});
})();
