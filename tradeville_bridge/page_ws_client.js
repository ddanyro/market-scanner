"use strict";

(() => {
  const BRIDGE_VERSION = 2;
  if (window.__marketScannerTradevilleBridgeVersion === BRIDGE_VERSION) return;
  window.__marketScannerTradevilleBridgeInstalled = true;
  window.__marketScannerTradevilleBridgeVersion = BRIDGE_VERSION;

  const REQUEST_SOURCE = "market-scanner-tradeville-extension-v2";
  const RESULT_SOURCE = "market-scanner-tradeville-page-v2";
  const WS_URL = "wss://portal.tradeville.ro";
  const WS_PROTOCOL = "pf4";
  const COMMANDS = new Set([
    "login", "persoana", "portof", "ordineActive", "infocont",
    "get_Sume_inDecontare", "activecurente", "cursbnr", "graf_pers_brut"
  ]);

  function parseJsonStorage(key) {
    const raw = window.localStorage.getItem(key);
    if (!raw) return null;
    try { return JSON.parse(raw); } catch (_) { return null; }
  }

  function cookieValue(name) {
    const prefix = `${encodeURIComponent(name)}=`;
    for (const part of document.cookie.split(";")) {
      const value = part.trim();
      if (value.startsWith(prefix)) return decodeURIComponent(value.slice(prefix.length));
    }
    return null;
  }

  // Tradeville encodes many tables as an object of parallel arrays. This is
  // the same lossless transformation used by the production portal.
  function decodeRows(value) {
    if (!value) return [];
    if (typeof value === "string") return [value];
    if (Array.isArray(value)) {
      if (!value[0]) return [];
      const first = value[0];
      const firstKey = first && typeof first === "object" ? Object.keys(first)[0] : null;
      if (!firstKey || !Array.isArray(first[firstKey])) return value;
    }
    if (typeof value !== "object") return [];
    const lengths = Object.values(value).map(item => Array.isArray(item) ? item.length : 1);
    const length = Math.max(0, ...lengths);
    const rows = [];
    for (let index = 0; index < length; index += 1) {
      const row = {};
      for (const [key, item] of Object.entries(value)) {
        row[key] = Array.isArray(item) ? item[index] : item;
      }
      rows.push(row);
    }
    return rows;
  }

  function safeError(error) {
    const message = String(error?.message || error || "unknown_error");
    return message.replace(/[A-Za-z0-9_\-]{24,}/g, "[redacted]").slice(0, 300);
  }

  function tradevilleWallClockIso() {
    const parts = Object.fromEntries(
      new Intl.DateTimeFormat("en-CA", {
        timeZone: "Europe/Bucharest",
        year: "numeric", month: "2-digit", day: "2-digit",
        hour: "2-digit", minute: "2-digit", second: "2-digit",
        hourCycle: "h23"
      }).formatToParts(new Date()).map(item => [item.type, item.value])
    );
    return `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}:${parts.second}.000Z`;
  }

  function openSocket() {
    return new Promise((resolve, reject) => {
      const socket = new WebSocket(WS_URL, [WS_PROTOCOL]);
      const waiters = [];
      let openTimer = setTimeout(() => {
        socket.close();
        reject(new Error("websocket_open_timeout"));
      }, 12000);

      socket.addEventListener("open", () => {
        clearTimeout(openTimer);
        resolve({ socket, waiters });
      }, { once: true });
      socket.addEventListener("error", () => reject(new Error("websocket_error")), { once: true });
      socket.addEventListener("message", event => {
        let payload;
        try { payload = JSON.parse(event.data); } catch (_) { return; }
        for (let index = 0; index < waiters.length; index += 1) {
          const waiter = waiters[index];
          if (waiter.command === payload.cmd && waiter.predicate(payload)) {
            waiters.splice(index, 1);
            clearTimeout(waiter.timer);
            waiter.resolve(payload);
            break;
          }
        }
      });
      socket.addEventListener("close", () => {
        for (const waiter of waiters.splice(0)) {
          clearTimeout(waiter.timer);
          waiter.reject(new Error("websocket_closed"));
        }
      });
    });
  }

  function sendAndWait(connection, message, predicate = () => true, timeout = 15000) {
    if (!COMMANDS.has(message.cmd)) return Promise.reject(new Error("command_not_allowed"));
    return new Promise((resolve, reject) => {
      const waiter = { command: message.cmd, predicate, resolve, reject, timer: null };
      waiter.timer = setTimeout(() => {
        const position = connection.waiters.indexOf(waiter);
        if (position >= 0) connection.waiters.splice(position, 1);
        reject(new Error(`${message.cmd}_timeout`));
      }, timeout);
      connection.waiters.push(waiter);
      connection.socket.send(JSON.stringify(message));
    });
  }

  function usableResponse(response, command) {
    if (!response) throw new Error(`${command}_empty_response`);
    if (response.err && response.OK !== 1) throw new Error(`${command}_failed`);
    return response;
  }

  async function collectAccount(connection, person, historyStart) {
    const personId = String(person.persoana || "");
    usableResponse(await sendAndWait(
      connection,
      { cmd: "persoana", persoana: personId },
      response => !response.persoana || response.persoana === personId
    ), "persoana");

    const portfolio = usableResponse(await sendAndWait(
      connection, { cmd: "portof", prm: { bid: "pret" } },
      response => response.prm?.bid === "pret" || !response.prm
    ), "portof");
    const orders = usableResponse(await sendAndWait(
      connection, { cmd: "ordineActive" }
    ), "ordineActive");
    const accountInfo = usableResponse(await sendAndWait(
      connection, { cmd: "infocont", prm: {} },
      response => !response.prm || Object.keys(response.prm).length === 0
    ), "infocont");
    const settlement = usableResponse(await sendAndWait(
      connection, { cmd: "get_Sume_inDecontare" }
    ), "get_Sume_inDecontare");
    const portfolioGraphRequest = {
      cmd: "graf_pers_brut",
      iday: false,
      nu2a: 1,
      nuob: 0,
      admine: "",
      cont: null,
      prm: {
        // The portal sends wall-clock Bucharest time encoded as UTC (J7).
        dsgraf: tradevilleWallClockIso(),
        dupas: `${historyStart || "2025-09-16"}T00:00:00.000Z`,
        opt: "",
        sims: ""
      }
    };
    let portfolioGraphData = [];
    let portfolioGraphError = null;
    try {
      const portfolioGraph = usableResponse(await sendAndWait(
        connection,
        portfolioGraphRequest,
        // The socket first emits an empty acknowledgement; the historical
        // payload follows in a second message with the same command. Accept
        // both the former array and a non-empty object payload so a harmless
        // server-side representation change does not look like a timeout.
        response => (
          (Array.isArray(response.data) && response.data.length > 0)
          || (response.data && typeof response.data === "object"
            && Object.keys(response.data).length > 0)
        ),
        12000
      ), "graf_pers_brut");
      portfolioGraphData = Array.isArray(portfolioGraph.data)
        ? portfolioGraph.data
        : [portfolioGraph.data];
    } catch (error) {
      // Current positions, orders and balances remain useful even when the
      // optional historical graph endpoint is slow or unavailable. Python
      // will graft only the last known-good encrypted graph for this account.
      portfolioGraphError = safeError(error);
    }

    return {
      person: {
        name: String(person.nume || personId),
        id: personId,
        is_subaccount: Number(person.subc || 0) === 1,
        readonly: Number(person.readonly || 0) === 1
      },
      portfolio: decodeRows(portfolio.data),
      orders: decodeRows(orders.data),
      account_info: decodeRows(accountInfo.data),
      settlement: decodeRows(settlement.data),
      // Keep this payload lossless: it can be an already computed point
      // series or the four raw parallel-array tables used by the portal.
      portfolio_graph: portfolioGraphData,
      portfolio_graph_request: {
        iday: false,
        adjusted_available: true,
        starts_at: historyStart || "2025-09-16",
        error: portfolioGraphError
      }
    };
  }

  async function syncTradeville(historyStart) {
    historyStart = /^\d{4}-\d{2}-\d{2}$/.test(String(historyStart || ""))
      ? String(historyStart)
      : "2025-09-16";
    const user = parseJsonStorage("usersitoken");
    const active = parseJsonStorage("persoanaactiva") || {};
    const sessionToken = cookieValue("legatura");
    if (!user || !sessionToken) throw new Error("tradeville_session_missing");

    const connection = await openSocket();
    try {
      const login = usableResponse(await sendAndWait(connection, {
        cmd: "login",
        prm: {
          coduser: user.coduser,
          token: sessionToken,
          demo: Boolean(user.demo),
          idp: user.idp,
          platf: "p4ptr"
        }
      }), "login");
      if (Number(login.OK) !== 1) throw new Error("tradeville_login_rejected");

      const initialPerson = String(active.persoana || "");
      const peopleResponse = usableResponse(await sendAndWait(
        connection, { cmd: "persoana", persoana: initialPerson }
      ), "persoana");
      const people = decodeRows(peopleResponse.data).filter(
        item => item && item.persoana && item.nume
      );
      if (!people.length) throw new Error("tradeville_accounts_missing");

      const ratesResponse = usableResponse(await sendAndWait(
        connection, { cmd: "cursbnr" }
      ), "cursbnr");
      const accounts = [];
      // Person selection is connection-scoped, so accounts must be collected
      // sequentially. Parallel requests could mix two legal portfolios.
      for (const person of people) {
        if (Number(person.subc || 0) === 1) continue;
        accounts.push(await collectAccount(connection, person, historyStart));
      }
      if (!accounts.length) throw new Error("tradeville_total_accounts_missing");

      return {
        schema: "market-scanner.tradeville.websocket.v2",
        bridge_version: BRIDGE_VERSION,
        fetched_at: new Date().toISOString(),
        source: "Tradeville WebSocket pf4",
        accounts,
        exchange_rates: decodeRows(ratesResponse.data)
      };
    } finally {
      connection.socket.close(1000, "read_only_sync_complete");
    }
  }

  window.addEventListener("message", async event => {
    if (event.source !== window || event.origin !== window.location.origin) return;
    const request = event.data;
    if (!request || request.source !== REQUEST_SOURCE || request.type !== "SYNC") return;
    try {
      const snapshot = await syncTradeville(request.historyStart);
      window.postMessage({
        source: RESULT_SOURCE,
        type: "SYNC_RESULT",
        jobId: request.jobId,
        token: request.token,
        ok: true,
        snapshot
      }, window.location.origin);
    } catch (error) {
      window.postMessage({
        source: RESULT_SOURCE,
        type: "SYNC_RESULT",
        jobId: request.jobId,
        token: request.token,
        ok: false,
        error: safeError(error)
      }, window.location.origin);
    }
  });
})();
