"use strict";

if (window.__marketScannerTradevilleContentBridgeInstalled) {
  // The service worker may inject the bridge into a tab that already received
  // the manifest content script. Never create a second polling loop.
} else {
window.__marketScannerTradevilleContentBridgeInstalled = true;

const REQUEST_SOURCE = "market-scanner-tradeville-extension";
const RESULT_SOURCE = "market-scanner-tradeville-page";
let activeJob = null;

async function pollBridge() {
  if (activeJob) return;
  let response;
  try {
    response = await chrome.runtime.sendMessage({ type: "TRADEVILLE_BRIDGE_POLL" });
  } catch (_) {
    return;
  }
  if (!response?.ok || !response.job) return;
  activeJob = response.job.id;
  window.postMessage({
    source: REQUEST_SOURCE,
    type: "SYNC",
    jobId: response.job.id,
    token: response.job.token
  }, window.location.origin);
}

window.addEventListener("message", async event => {
  if (event.source !== window || event.origin !== window.location.origin) return;
  const data = event.data;
  if (!data || data.source !== RESULT_SOURCE || data.type !== "SYNC_RESULT") return;
  if (!activeJob || data.jobId !== activeJob) return;
  try {
    await chrome.runtime.sendMessage({
      type: "TRADEVILLE_BRIDGE_RESULT",
      jobId: data.jobId,
      token: data.token,
      ok: data.ok === true,
      snapshot: data.snapshot || null,
      error: data.error || null
    });
  } finally {
    activeJob = null;
  }
});

setInterval(pollBridge, 1000);
pollBridge();
chrome.runtime.sendMessage({ type: "TRADEVILLE_BRIDGE_READY" }).catch(() => {});
}
