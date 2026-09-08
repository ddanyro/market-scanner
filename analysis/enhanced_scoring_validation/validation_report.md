# Enhanced Scoring shadow validation

Generated: 2026-09-08T10:15:39.938256+03:00

## Data integrity verdict

- Daily committed snapshots: **251**; recommendations: **291505** across **1757** tickers (2026-01-01 to 2026-09-08).
- Baseline has no persisted continuous 0–100 score. `baseline_score` is the faithful gate proxy `Checks_Passed / 4 × 100`; it has only five possible values.
- Enhanced values are retrospective reconstructions with the unchanged v1 formula. They are not contemporaneously logged Enhanced predictions.
- Historical Options observations: **0**. Historical Portfolio Fit observations: **0**. Both are therefore untestable, not evidence of zero value.
- IBKR trades read: **159**; matched to a recommendation timestamped before execution: **59**.
- Rejected price-discontinuity paths by horizon: **{'1': 97, '5': 331, '10': 524, '20': 781, '60': 1081}**; these remain explicit missing outcomes.
- Raw versus adjusted Spearman correlation: **1.000000**. With Portfolio Fit fixed at 50, adjusted is only `0.85 × raw + 7.5` and cannot change ranking.
- Repeated ticker/day observations are not independent trades. Results are diagnostic and must not be promoted to production evidence.

## Outcome coverage

| horizon | available | missing |
|---|---|---|
| 1 | 208251 | 83254 |
| 5 | 202047 | 89458 |
| 10 | 192018 | 99487 |
| 20 | 172536 | 118969 |
| 60 | 110137 | 181368 |

## Baseline versus Enhanced — 20D, score >= 75

Hit rate is directional classification accuracy using score >=75 versus positive return; win rate is the positive-return rate inside the selected bucket.

| score | n | average | median | win_rate | hit_rate | average_gain | average_loss | expectancy | average_mae | average_mfe | spearman |
|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 59969 | 1.495 | 0.648 | 53.049 | 48.585 | 9.693 | -7.769 | 1.495 | -7.710 | 10.699 | -0.039 |
| raw_enhanced | 615 | 4.798 | 4.024 | 68.293 | 46.596 | 11.688 | -10.041 | 4.798 | -7.438 | 14.447 | -0.000 |
| portfolio_adjusted | 5 | 0.448 | 2.971 | 60.000 | 46.466 | 9.459 | -13.068 | 0.448 | -10.750 | 11.110 | -0.000 |

### Date-block bootstrap: >=75 Raw minus >=75 Baseline

Dates, not rows, are resampled. This controls repeated same-day recommendations, but the two thresholds still select very different cohort sizes.

| horizon | paired_dates | enhanced_minus_baseline_mean_pct | bootstrap_ci_low_95 | bootstrap_ci_high_95 |
|---|---|---|---|---|
| 1 | 157 | -0.025 | -0.281 | 0.236 |
| 5 | 153 | 1.146 | 0.464 | 1.871 |
| 10 | 146 | 1.028 | 0.062 | 2.037 |
| 20 | 132 | 3.363 | 1.884 | 4.945 |
| 60 | 84 | 9.560 | 4.959 | 14.499 |

## Score buckets — 20D

| score | bucket | n | average | median | win_rate |
|---|---|---|---|---|---|
| baseline | 0-49 | 53789 | 3.637 | 1.961 | 55.208 |
| baseline | 50-59 | 58778 | 1.987 | 0.689 | 52.498 |
| baseline | 60-69 | 0 | NA | NA | NA |
| baseline | 70-74 | 0 | NA | NA | NA |
| baseline | 75-79 | 53856 | 1.476 | 0.589 | 52.830 |
| baseline | 80-84 | 0 | NA | NA | NA |
| baseline | 85-89 | 0 | NA | NA | NA |
| baseline | 90+ | 6113 | 1.661 | 0.997 | 54.981 |
| raw_enhanced | 0-49 | 43079 | 2.717 | 1.015 | 52.524 |
| raw_enhanced | 50-59 | 67598 | 2.481 | 1.043 | 53.857 |
| raw_enhanced | 60-69 | 56777 | 1.874 | 0.836 | 53.687 |
| raw_enhanced | 70-74 | 4467 | 1.771 | 1.029 | 54.421 |
| raw_enhanced | 75-79 | 614 | 4.798 | 4.024 | 68.241 |
| raw_enhanced | 80-84 | 1 | 4.822 | 4.822 | 100.000 |
| raw_enhanced | 85-89 | 0 | NA | NA | NA |
| raw_enhanced | 90+ | 0 | NA | NA | NA |
| portfolio_adjusted | 0-49 | 43068 | 2.715 | 1.014 | 52.522 |
| portfolio_adjusted | 50-59 | 81399 | 2.474 | 1.052 | 54.029 |
| portfolio_adjusted | 60-69 | 46907 | 1.687 | 0.758 | 53.314 |
| portfolio_adjusted | 70-74 | 1157 | 3.942 | 3.631 | 65.341 |
| portfolio_adjusted | 75-79 | 5 | 0.448 | 2.971 | 60.000 |
| portfolio_adjusted | 80-84 | 0 | NA | NA | NA |
| portfolio_adjusted | 85-89 | 0 | NA | NA | NA |
| portfolio_adjusted | 90+ | 0 | NA | NA | NA |

## BUY / WAIT / AVOID — 20D

| model | decision | n | average | median | win_rate | average_gain | average_loss | average_mae | average_mfe |
|---|---|---|---|---|---|---|---|---|---|
| baseline | BUY | 6113 | 1.661 | 0.997 | 54.981 | 9.241 | -7.598 | -7.510 | 10.240 |
| baseline | WAIT | 53856 | 1.476 | 0.589 | 52.830 | 9.747 | -7.788 | -7.733 | 10.751 |
| baseline | AVOID | 112567 | 2.775 | 1.231 | 53.793 | 15.311 | -11.819 | -11.269 | 18.571 |
| enhanced | BUY | 6113 | 1.661 | 0.997 | 54.981 | 9.241 | -7.598 | -7.510 | 10.240 |
| enhanced | WAIT | 53856 | 1.476 | 0.589 | 52.830 | 9.747 | -7.788 | -7.733 | 10.751 |
| enhanced | AVOID | 112567 | 2.775 | 1.231 | 53.793 | 15.311 | -11.819 | -11.269 | 18.571 |

Outcome classes for the confusion matrix are defined before inspection as BUY > +2%, AVOID < -2%, otherwise WAIT.

| model | horizon | predicted | actual | count |
|---|---|---|---|---|
| baseline | 20 | BUY | BUY | 2768 |
| baseline | 20 | BUY | WAIT | 1111 |
| baseline | 20 | BUY | AVOID | 2234 |
| baseline | 20 | WAIT | BUY | 23230 |
| baseline | 20 | WAIT | WAIT | 10034 |
| baseline | 20 | WAIT | AVOID | 20592 |
| baseline | 20 | AVOID | BUY | 53659 |
| baseline | 20 | AVOID | WAIT | 14215 |
| baseline | 20 | AVOID | AVOID | 44693 |
| enhanced | 20 | BUY | BUY | 2768 |
| enhanced | 20 | BUY | WAIT | 1111 |
| enhanced | 20 | BUY | AVOID | 2234 |
| enhanced | 20 | WAIT | BUY | 23230 |
| enhanced | 20 | WAIT | WAIT | 10034 |
| enhanced | 20 | WAIT | AVOID | 20592 |
| enhanced | 20 | AVOID | BUY | 53659 |
| enhanced | 20 | AVOID | WAIT | 14215 |
| enhanced | 20 | AVOID | AVOID | 44693 |

## Component contribution — chronological 70/30 validation, 20D

`incremental_delta_r2` and `incremental_delta_mae` compare a ridge model containing all variable components against the same model without that component. Positive is better. No weights were fitted or changed.

| component | n | unique_values | incremental_delta_r2 | incremental_delta_mae | spearman_1d | spearman_5d | spearman_10d | spearman_20d | spearman_60d |
|---|---|---|---|---|---|---|---|---|---|
| technical_score | 172536 | 5 | -0.009 | -0.105 | -0.014 | -0.007 | -0.016 | -0.039 | 0.003 |
| momentum_score | 172536 | 7522 | -0.008 | -0.063 | -0.003 | -0.007 | -0.014 | -0.053 | -0.123 |
| research_score | 172536 | 18 | 0.000 | -0.006 | 0.018 | 0.036 | 0.042 | 0.058 | 0.106 |
| volatility_score | 172536 | 6112 | 0.004 | 0.014 | -0.007 | 0.032 | 0.041 | 0.025 | 0.141 |
| liquidity_score | 172536 | 250 | 0.000 | 0.000 | 0.002 | 0.005 | 0.003 | 0.005 | NA |
| options_score | 172536 | 1 | NA | NA | NA | NA | NA | NA | NA |
| relative_opportunity_score | 172536 | 1 | NA | NA | NA | NA | NA | NA | NA |
| risk_reward_score | 172536 | 401 | 0.000 | 0.000 | 0.005 | 0.023 | 0.040 | 0.073 | 0.123 |
| portfolio_fit_score | 172536 | 1 | NA | NA | NA | NA | NA | NA | NA |

## Redundancy pairs (|Spearman| >= 0.75)

_No observations._

## Market regimes — 20D

| regime | score | n | spearman_20d | selected_n | selected_average | selected_win_rate |
|---|---|---|---|---|---|---|
| bullish | baseline | 4788 | 0.084 | 2128 | -0.512 | 45.160 |
| bullish | raw_enhanced | 4788 | 0.092 | 15 | -0.949 | 60.000 |
| bullish | portfolio_adjusted | 4788 | 0.092 | 0 | NA | NA |
| bearish | baseline | 5855 | -0.154 | 2497 | 1.508 | 52.503 |
| bearish | raw_enhanced | 5855 | -0.074 | 47 | 3.763 | 68.085 |
| bearish | portfolio_adjusted | 5855 | -0.074 | 2 | 11.777 | 100.000 |
| sideways | baseline | 161893 | -0.038 | 55344 | 1.571 | 53.377 |
| sideways | raw_enhanced | 161893 | 0.000 | 553 | 5.042 | 68.535 |
| sideways | portfolio_adjusted | 161893 | 0.000 | 3 | -7.105 | 33.333 |
| high_volatility | baseline | 17031 | -0.207 | 3040 | 5.532 | 61.053 |
| high_volatility | raw_enhanced | 17031 | -0.158 | 63 | 14.193 | 76.190 |
| high_volatility | portfolio_adjusted | 17031 | -0.158 | 1 | 4.822 | 100.000 |
| low_volatility | baseline | 87092 | 0.062 | 33005 | 1.105 | 53.007 |
| low_volatility | raw_enhanced | 87092 | 0.078 | 289 | 2.921 | 65.744 |
| low_volatility | portfolio_adjusted | 87092 | 0.078 | 3 | -1.851 | 33.333 |

## Baseline != Enhanced

Disagreements: **0**.

_No observations._

## Explicit conclusions

- **A — Predictiveness:** Raw Enhanced improves rank correlation from -0.039 to -0.000 at 20D and from 0.003 to 0.049 at 60D. The 20D result is effectively zero; the 60D +0.049 signal is weak. The >=75 Raw bucket is promising (615 observations, 4.80% mean, 68.3% wins) versus Baseline (59969, 1.49%, 53.0%), but it is a much smaller and repeatedly sampled cohort, so this is not an apples-to-apples replacement test.
- **B — Portfolio Fit:** cannot be validated. Every historical fit is neutral 50; adjusted score is a monotone shrinkage of Raw and has identical ranking. There are zero observable cases of high Raw + weak Fit or medium Raw + strong Fit.
- **C — Volatility/Liquidity/Options:** Volatility is the only new risk component with positive 20D holdout contribution (delta R² +0.0037; delta MAE +0.0139 pp) and stronger 60D correlation (+0.141). Liquidity is effectively neutral in the training period and adds no measurable information. Options has zero historical observations and is untestable.
- **D — Redundancy:** Technical is exactly the Baseline Gate Score in this reconstruction. Portfolio Adjusted is redundant with Raw until real Portfolio Fit varies. Options, Relative Opportunity and Portfolio Fit are constants, so they dilute rather than differentiate historical Raw scores; this does not prove they are intrinsically useless.
- **Keep provisionally:** Research, Volatility and Risk/Reward. Their 20D/60D correlations are positive, although only Volatility has a material positive holdout delta R².
- **Recalibrate only after a clean holdout:** Technical and Momentum. At 20D their correlations are -0.039 and -0.053 and their incremental holdout contributions are negative; Momentum falls to -0.123 at 60D.
- **Missing evidence/features:** contemporaneous portfolio allocation, broad options comparison cohort, benchmark-relative alpha, slippage/transaction costs, earnings-event controls, and explicit market-regime interactions.
- **15% Portfolio adjustment:** not justified or rejected by this sample—it is unidentifiable. The current 15% must remain shadow until non-neutral fits have forward outcomes.
- **Current weights:** the data does not support declaring 25% Technical / 15% Momentum optimal. No alternative weights were fitted. Research/Volatility/Risk-Reward show more favorable directional evidence than their current combined interpretation, but changing weights now would be sample reuse.
- **Decision comparison:** historical Enhanced decisions equal Baseline in all rows because the IBKR risk gates were absent historically. Both have the same 20D three-class accuracy of 33.3% under the predeclared ±2% outcome definition.
- **Regimes:** behavior is not stable. Raw correlation is positive in bullish/low-volatility samples, approximately zero sideways, and negative in bearish/high-volatility samples. One global weight vector is therefore not empirically supported yet.

## OPTIONS selection-bias audit

Historical option coverage is zero because the top-3 lazy collection was added only with Enhanced v1. Missing options are encoded as neutral 50, and selection into the future top-3 is conditional on the baseline rank. Comparing covered versus uncovered names later would therefore be selection-biased unless candidates are randomized or all eligible names receive delayed option snapshots for measurement.

## VERDICT — SHOULD ENHANCED SCORING REPLACE BASELINE?

**NOT YET.** This reconstruction can test the legacy-derived Technical, Momentum, Research, ATR-volatility and Risk/Reward mixture, but it cannot test the two central IBKR additions—actual Portfolio Fit and Options—and it contains no contemporaneous Enhanced predictions. Shadow logging must accumulate before a defensible replacement decision.

## TOP 5 NEXT IMPROVEMENTS

1. Persist every shadow prediction and immutable input snapshot before market close, including score version and data availability flags.
2. Record Portfolio Fit contemporaneously and retain the unadjusted allocation dimensions used to calculate it.
3. Create an options measurement cohort: fetch options for top-3 operationally, but collect delayed/end-of-day features for a broader comparison cohort to quantify selection bias.
4. Use non-overlapping evaluation anchors or date/ticker-cluster bootstrap confidence intervals; keep a final chronological holdout untouched.
5. Add benchmark-relative forward returns and transaction-cost/slippage outcomes before any weight optimization.
