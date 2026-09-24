# Swing regime diagnostic replay

## Comportamentul dashboardului

`swing_model.py` este sursa comună pentru regim și timing. Regimul
FAVORABLE/SELECTIVE permite cercetarea candidaților; DEFENSIVE/UNKNOWN o oprește.
Această permisiune nu execută ordine și nu validează automat un instrument.
Verdictul vechi de pullback rămâne separat. Continuarea trendului este afișată
ca scenariu de cercetare **NEVALIDAT**, nu ca BUY nou.

Continuarea verifică poziția prețului față de SMA200/50/10 și RSI ≥50. Acesta
este un criteriu inițial explicit pentru comparație, nu un prag optimizat sau
demonstrat statistic. SMA50 este obligatorie pentru continuare, nu a fost
adăugată retroactiv la regula veche de pullback.

Datele-cheie lipsă/invalide sau mai vechi de 96 ore produc UNKNOWN; toleranța
include weekendurile, dar nu certifică închiderea ședinței. Timestampurile
Finviz de preluare sunt etichetate separat de observația bursieră și reduc
calitatea la PARTIAL. Un cache Market Tide expirat nu poate impune un veto
pretins actual. Snapshoturile vechi fără timestampurile noi necesită o
actualizare pentru confirmarea regimului. Scorul și încrederea descriu datele,
nu probabilitatea de câștig.

Filtrele defensive SUA existente (VIX >30, breadth <30%, ambii indici sub
SMA200) sunt păstrate. Slăbiciunea Market Tide menține WAIT pentru pullback,
dar poate permite cercetare SELECTIVE. BVB sub SMA200 rămâne DEFENSIVE.

## Diagnostic local

Run from the repository root:

```sh
.venv/bin/python scripts/validate_swing_regimes.py --input dashboard_state.json --roundtrip-cost-bps 20
```

The command reads local JSON and writes JSON to stdout only. It performs no
network requests and does not update dashboard data. Cost is a required,
user-specified hypothetical **roundtrip** cost in basis points; `0` disables the
adjustment. `20` is an example, not an estimate of actual brokerage, spread or
slippage costs.

Input can be `dashboard_state.json` with `bvb_proxy`, a standalone proxy row with
`Chart_Dates` / `Chart_History`, or an object with `dates` / `closes`. Dates must be
unique, chronological `YYYY-MM-DD` values aligned with positive finite closes.
At least 200 observations are required; invalid input is rejected rather than
silently removing sessions.

## What is compared

- Original BVB BUY rule: above SMA200 and SMA10, RSI in `[45, 70)`; its historical
  missing-RSI acceptance is deliberately preserved for this baseline.
- New market regime allowing candidate research, **not** an entry signal.
- New continuation setup marked `READY`, still **research-only**.

The first evaluated session has 200 closes available. SMA10/50/200 and Wilder
RSI (`alpha=1/14`, `adjust=False`, initial gain/loss zero) use only the current
and preceding closes. Every historical evaluation uses that session's date as
both observation time and evaluation clock, rather than today's clock. This
assumes contemporaneous availability; a cached/revised series does not prove
what data was available historically. The output is a reconstruction, not a
record of the dashboard's previous verdicts.

For each cohort, the report gives frequency and mean/median proxy close returns
after 5, 10 and 20 subsequent observations. It separately counts unavailable
future outcomes. The cost-adjusted mean subtracts one hypothetical roundtrip
cost. These are **overlapping, non-independent forward labels**, with overlapping
cohorts, not actual trades, fill simulations, portfolio returns or win rates.
Horizons count supplied observations; completeness against the exchange trading
calendar is not verified and missing sessions are not reconstructed.
The proxy is TVBETETF, not every BVB stock or an official full-market index.

## Limits and promotion requirements

This diagnostic does not establish profitability, an optimal BUY frequency,
drawdown, or financial validity. It does not simulate positions, sizing, exits,
liquidity, spreads, execution delays or exposure. Same-close forward labels are
not proof that the close was an executable entry after signal calculation.
An input may include an incomplete final session; it is not automatically
certified as a finalized daily close.

A full US historical replay is not available without point-in-time daily
sentiment and breadth history. Current US values must not be copied backward or
replaced with price-only approximations while claiming a full-model backtest.

Before promoting continuation from research-only:

1. Freeze parameters and selection rules before evaluating an unseen period;
   keep tuning/training data separate from out-of-sample evaluation.
2. Use point-in-time instrument universes and inputs across several market
   regimes; check revisions, survivorship, missing data and final-close timing.
3. Specify executable entries, exits, stops, sizing and overlapping-position
   rules. Compare the original and proposed strategies under identical rules.
4. Include commissions, spread/slippage, liquidity constraints and realistic
   execution timing; test cost sensitivity, separately for US and BVB.
5. Evaluate trade expectancy, exposure, turnover and portfolio drawdown with
   uncertainty and enough independent observations; do not choose rules merely
   because they produce more green sessions.

Keep continuation research-only unless that separate evaluation supports an
explicit promotion decision.
