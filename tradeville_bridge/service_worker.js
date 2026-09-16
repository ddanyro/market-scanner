"use strict";

const BRIDGE_URL = "http://127.0.0.1:43129";
const BRIDGE_HEADER = "market-scanner-tradeville-v1";

async function injectIntoOpenTradevilleTabs() {
  let tabs = [];
  try {
    tabs = await chrome.tabs.query({ url: "https://portal.tradeville.ro/*" });
  } catch (_) {
    return;
  }
  for (const tab of tabs) {
    if (!tab.id) continue;
    try {
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ["page_ws_client.js"],
        world: "MAIN"
      });
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ["content_bridge.js"]
      });
    } catch (_) {
      // A tab can navigate or close between query and injection. The manifest
      // content script will handle its next Tradeville navigation.
    }
  }
}

chrome.runtime.onInstalled.addListener(injectIntoOpenTradevilleTabs);
chrome.runtime.onStartup.addListener(injectIntoOpenTradevilleTabs);
chrome.action.onClicked.addListener(injectIntoOpenTradevilleTabs);

async function bridgeFetch(path, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("X-Market-Scanner-Bridge", BRIDGE_HEADER);
  return fetch(`${BRIDGE_URL}${path}`, {
    ...options,
    headers,
    cache: "no-store"
  });
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  const senderUrl = sender.url || sender.tab?.url || "";
  if (!sender.tab || !senderUrl.startsWith("https://portal.tradeville.ro/")) {
    sendResponse({ ok: false, error: "invalid_sender" });
    return false;
  }

  if (message?.type === "TRADEVILLE_BRIDGE_READY") {
    chrome.action.setBadgeBackgroundColor({ color: "#188038" });
    chrome.action.setBadgeText({ text: "ON" });
    // A reloaded unpacked extension invalidates the old content-script
    // context while the page itself can remain open. Reinject the versioned
    // page client from the current extension package.
    chrome.scripting.executeScript({
      target: { tabId: sender.tab.id },
      files: ["page_ws_client.js"],
      world: "MAIN"
    }).then(
      () => sendResponse({ ok: true, version: 2 }),
      () => sendResponse({ ok: false, error: "page_injection_failed" })
    );
    return true;
  }

  if (message?.type === "TRADEVILLE_BRIDGE_POLL") {
    bridgeFetch("/v1/job")
      .then(async response => {
        if (response.status === 204) return { ok: true, job: null };
        if (!response.ok) throw new Error(`bridge_http_${response.status}`);
        return { ok: true, job: await response.json() };
      })
      .then(sendResponse)
      .catch(() => sendResponse({ ok: false, offline: true }));
    return true;
  }

  if (message?.type === "TRADEVILLE_BRIDGE_RESULT") {
    const jobId = encodeURIComponent(String(message.jobId || ""));
    bridgeFetch(`/v1/jobs/${jobId}/result`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        token: message.token,
        ok: message.ok === true,
        snapshot: message.snapshot || null,
        error: message.error || null
      })
    })
      .then(response => {
        if (!response.ok) throw new Error(`bridge_http_${response.status}`);
        return { ok: true };
      })
      .then(sendResponse)
      .catch(error => sendResponse({ ok: false, error: String(error.message || error) }));
    return true;
  }

  return false;
});
