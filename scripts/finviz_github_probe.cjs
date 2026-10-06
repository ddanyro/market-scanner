// Bounded public-page diagnostic; no credentials, challenge handling or retries.
const { chromium } = require('playwright');
const fs = require('node:fs/promises');
const path = require('node:path');

const symbols = ['AAPL', 'CLS', 'CRWD'];
const output = path.resolve(process.env.PROBE_OUTPUT || 'finviz-probe-output');

async function snapshot(page) {
  return page.evaluate(() => {
    const body = document.body?.innerText || '';
    const blocked = /just a moment|attention required/i.test(document.title)
      || /verify you are human|performing security verification|checking your browser/i.test(body)
      || !!document.querySelector('iframe[src*="challenges.cloudflare.com"]');
    const metrics = {};
    for (const cell of document.querySelectorAll('td')) {
      const label = cell.textContent.trim();
      if (['ATR (14)', 'Volatility'].includes(label)) {
        metrics[label] = cell.nextElementSibling?.textContent.trim() || '';
      }
    }
    return { title: document.title, url: location.href, blocked, metrics };
  });
}

async function main() {
  await fs.mkdir(output, { recursive: true });
  const report = { timestamp: new Date().toISOString(), environment: 'github-actions-standard-chromium', results: [] };
  let browser;
  let stopReason = null;
  try {
    browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    for (const symbol of symbols) {
      if (stopReason) {
        report.results.push({ symbol, status: 'not_run', reason: stopReason });
        continue;
      }
      const result = { symbol };
      try {
        const response = await page.goto(`https://finviz.com/stock?t=${symbol}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
        result.httpStatus = response?.status() ?? null;
        let state = await snapshot(page);
        if (![403, 429].includes(result.httpStatus) && !state.blocked && result.httpStatus === 200) {
          // Only allow ordinary page rendering; never retry or interact with a challenge.
          await page.waitForFunction(() => {
            const text = document.body?.innerText || '';
            return /verify you are human|performing security verification/i.test(text)
              || /just a moment/i.test(document.title)
              || Array.from(document.querySelectorAll('td')).some(td => td.textContent.trim() === 'Volatility');
          }, { }, { timeout: 10000 }).catch(() => {});
          state = await snapshot(page);
        }
        Object.assign(result, state);
        if ([403, 429].includes(result.httpStatus) || state.blocked) {
          result.status = 'blocked';
          stopReason = 'Stopped after access restriction; no challenge bypass attempted.';
        } else {
          const atr = Number(state.metrics['ATR (14)']);
          const volatility = (state.metrics.Volatility || '').match(/^(\d+(?:\.\d+)?)%\s+(\d+(?:\.\d+)?)%$/);
          const tickerMatches = new RegExp(`\\b${symbol}\\b`).test(state.title);
          result.status = result.httpStatus === 200 && tickerMatches && Number.isFinite(atr) && atr > 0 && volatility ? 'ok' : 'missing_metrics';
          if (result.status === 'ok') {
            result.atr14 = atr;
            result.volatilityWeekPct = Number(volatility[1]);
            result.volatilityMonthPct = Number(volatility[2]);
          }
        }
        await page.screenshot({ path: path.join(output, `${symbol}.png`), fullPage: false }).catch(() => {});
      } catch (error) {
        result.status = 'navigation_error';
        result.error = error.message;
        stopReason = 'Stopped after navigation error.';
      }
      report.results.push(result);
      console.log(JSON.stringify(result));
    }
  } catch (error) {
    report.error = error.message;
  } finally {
    if (browser) await browser.close().catch(() => {});
    report.success = report.results.length === symbols.length && report.results.every(row => row.status === 'ok');
    await fs.writeFile(path.join(output, 'report.json'), JSON.stringify(report, null, 2));
    const summary = ['## Finviz public access probe', '', '| Symbol | Status | HTTP | ATR14 | Week % | Month % |', '|---|---|---|---|---|---|',
      ...report.results.map(row => `| ${row.symbol} | ${row.status} | ${row.httpStatus ?? '-'} | ${row.atr14 ?? '-'} | ${row.volatilityWeekPct ?? '-'} | ${row.volatilityMonthPct ?? '-'} |`),
      '', 'Standard headless Chromium, no login, no imported cookies, no challenge bypass. Stops on an access restriction.',
      report.error ? `Error: ${report.error}` : '', ''].join('\n');
    if (process.env.GITHUB_STEP_SUMMARY) await fs.appendFile(process.env.GITHUB_STEP_SUMMARY, summary);
    process.exitCode = report.success ? 0 : 1;
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
