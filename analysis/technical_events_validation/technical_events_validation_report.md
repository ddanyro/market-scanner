# TECHNICAL EVENTS VALIDATION REPORT

Generated: 2026-09-10T08:45:07+00:00

## Sample size and coverage

```csv
snapshots,observations,tickers,matured_1d,matured_5d,matured_10d,matured_20d,matured_60d
10,7128,1320,24,0,0,0,0
```

## Score buckets

```csv
feature,bucket,horizon,n,average_return,median_return,win_rate,directional_hit_rate,expectancy,average_mae,average_mfe
short_event_score,<40,1,15,2.794062991721887,1.4340967080528344e-06,66.66666666666666,,2.794062991721887,2.794062991721887,2.9114337718070633
short_event_score,<40,5,0,,,,,,,
short_event_score,<40,10,0,,,,,,,
short_event_score,<40,20,0,,,,,,,
short_event_score,<40,60,0,,,,,,,
short_event_score,40-49,1,0,,,,,,,
short_event_score,40-49,5,0,,,,,,,
short_event_score,40-49,10,0,,,,,,,
short_event_score,40-49,20,0,,,,,,,
short_event_score,40-49,60,0,,,,,,,
short_event_score,50-59,1,9,-3.3388988004503073,-3.3388988004503073,0.0,,-3.3388988004503073,-3.672788298388774,2.5542591967447237
short_event_score,50-59,5,0,,,,,,,
short_event_score,50-59,10,0,,,,,,,
short_event_score,50-59,20,0,,,,,,,
short_event_score,50-59,60,0,,,,,,,
short_event_score,60-69,1,0,,,,,,,
short_event_score,60-69,5,0,,,,,,,
short_event_score,60-69,10,0,,,,,,,
short_event_score,60-69,20,0,,,,,,,
short_event_score,60-69,60,0,,,,,,,
short_event_score,70-79,1,0,,,,,,,
short_event_score,70-79,5,0,,,,,,,
short_event_score,70-79,10,0,,,,,,,
short_event_score,70-79,20,0,,,,,,,
short_event_score,70-79,60,0,,,,,,,
short_event_score,80+,1,0,,,,,,,
short_event_score,80+,5,0,,,,,,,
short_event_score,80+,10,0,,,,,,,
short_event_score,80+,20,0,,,,,,,
short_event_score,80+,60,0,,,,,,,
intermediate_event_score,<40,1,5,-1.4084523832294304,-1.4084523832294304,0.0,,-1.4084523832294304,-1.4084523832294304,-1.0563400429739023
intermediate_event_score,<40,5,0,,,,,,,
intermediate_event_score,<40,10,0,,,,,,,
intermediate_event_score,<40,20,0,,,,,,,
intermediate_event_score,<40,60,0,,,,,,,
intermediate_event_score,40-49,1,19,0.9949009256801414,1.4340967080528344e-06,52.63157894736842,,0.9949009256801414,0.8367427424461309,3.7863968190883135
intermediate_event_score,40-49,5,0,,,,,,,
intermediate_event_score,40-49,10,0,,,,,,,
intermediate_event_score,40-49,20,0,,,,,,,
intermediate_event_score,40-49,60,0,,,,,,,
intermediate_event_score,50-59,1,0,,,,,,,
intermediate_event_score,50-59,5,0,,,,,,,
intermediate_event_score,50-59,10,0,,,,,,,
intermediate_event_score,50-59,20,0,,,,,,,
intermediate_event_score,50-59,60,0,,,,,,,
intermediate_event_score,60-69,1,0,,,,,,,
intermediate_event_score,60-69,5,0,,,,,,,
intermediate_event_score,60-69,10,0,,,,,,,
intermediate_event_score,60-69,20,0,,,,,,,
intermediate_event_score,60-69,60,0,,,,,,,
intermediate_event_score,70-79,1,0,,,,,,,
intermediate_event_score,70-79,5,0,,,,,,,
intermediate_event_score,70-79,10,0,,,,,,,
intermediate_event_score,70-79,20,0,,,,,,,
intermediate_event_score,70-79,60,0,,,,,,,
intermediate_event_score,80+,1,0,,,,,,,
intermediate_event_score,80+,5,0,,,,,,,
intermediate_event_score,80+,10,0,,,,,,,
intermediate_event_score,80+,20,0,,,,,,,
intermediate_event_score,80+,60,0,,,,,,,
```

## Direction and timeframe results

```csv
timeframe,direction,horizon,n,average_return,median_return,win_rate,directional_hit_rate,expectancy,average_mae,average_mfe
SHORT_TERM,BULLISH,1,9,-3.3388988004503073,-3.3388988004503073,0.0,0.0,-3.3388988004503073,-3.672788298388774,2.5542591967447237
SHORT_TERM,BULLISH,5,0,,,,,,,
SHORT_TERM,BULLISH,10,0,,,,,,,
SHORT_TERM,BULLISH,20,0,,,,,,,
SHORT_TERM,BULLISH,60,0,,,,,,,
SHORT_TERM,NEUTRAL,1,0,,,,,,,
SHORT_TERM,NEUTRAL,5,0,,,,,,,
SHORT_TERM,NEUTRAL,10,0,,,,,,,
SHORT_TERM,NEUTRAL,20,0,,,,,,,
SHORT_TERM,NEUTRAL,60,0,,,,,,,
SHORT_TERM,BEARISH,1,15,2.794062991721887,1.4340967080528344e-06,66.66666666666666,33.33333333333333,2.794062991721887,2.794062991721887,2.9114337718070633
SHORT_TERM,BEARISH,5,0,,,,,,,
SHORT_TERM,BEARISH,10,0,,,,,,,
SHORT_TERM,BEARISH,20,0,,,,,,,
SHORT_TERM,BEARISH,60,0,,,,,,,
INTERMEDIATE_TERM,BULLISH,1,0,,,,,,,
INTERMEDIATE_TERM,BULLISH,5,0,,,,,,,
INTERMEDIATE_TERM,BULLISH,10,0,,,,,,,
INTERMEDIATE_TERM,BULLISH,20,0,,,,,,,
INTERMEDIATE_TERM,BULLISH,60,0,,,,,,,
INTERMEDIATE_TERM,NEUTRAL,1,14,1.3502221726742245,-3.3388988004503073,35.714285714285715,,1.3502221726742245,1.1355789239994962,5.138680885156745
INTERMEDIATE_TERM,NEUTRAL,5,0,,,,,,,
INTERMEDIATE_TERM,NEUTRAL,10,0,,,,,,,
INTERMEDIATE_TERM,NEUTRAL,20,0,,,,,,,
INTERMEDIATE_TERM,NEUTRAL,60,0,,,,,,,
INTERMEDIATE_TERM,BEARISH,1,10,-0.7042254745663612,-0.7042254745663612,50.0,50.0,-0.7042254745663612,-0.7042254745663612,-0.5281693044385971
INTERMEDIATE_TERM,BEARISH,5,0,,,,,,,
INTERMEDIATE_TERM,BEARISH,10,0,,,,,,,
INTERMEDIATE_TERM,BEARISH,20,0,,,,,,,
INTERMEDIATE_TERM,BEARISH,60,0,,,,,,,
LONG_TERM,BULLISH,1,0,,,,,,,
LONG_TERM,BULLISH,5,0,,,,,,,
LONG_TERM,BULLISH,10,0,,,,,,,
LONG_TERM,BULLISH,20,0,,,,,,,
LONG_TERM,BULLISH,60,0,,,,,,,
LONG_TERM,NEUTRAL,1,19,0.9949009256801414,1.4340967080528344e-06,52.63157894736842,,0.9949009256801414,0.8367427424461309,3.7863968190883135
LONG_TERM,NEUTRAL,5,0,,,,,,,
LONG_TERM,NEUTRAL,10,0,,,,,,,
LONG_TERM,NEUTRAL,20,0,,,,,,,
LONG_TERM,NEUTRAL,60,0,,,,,,,
LONG_TERM,BEARISH,1,5,-1.4084523832294304,-1.4084523832294304,0.0,100.0,-1.4084523832294304,-1.4084523832294304,-1.0563400429739023
LONG_TERM,BEARISH,5,0,,,,,,,
LONG_TERM,BEARISH,10,0,,,,,,,
LONG_TERM,BEARISH,20,0,,,,,,,
LONG_TERM,BEARISH,60,0,,,,,,,
OVERALL,BULLISH,1,0,,,,,,,
OVERALL,BULLISH,5,0,,,,,,,
OVERALL,BULLISH,10,0,,,,,,,
OVERALL,BULLISH,20,0,,,,,,,
OVERALL,BULLISH,60,0,,,,,,,
OVERALL,NEUTRAL,1,9,-3.3388988004503073,-3.3388988004503073,0.0,,-3.3388988004503073,-3.672788298388774,2.5542591967447237
OVERALL,NEUTRAL,5,0,,,,,,,
OVERALL,NEUTRAL,10,0,,,,,,,
OVERALL,NEUTRAL,20,0,,,,,,,
OVERALL,NEUTRAL,60,0,,,,,,,
OVERALL,BEARISH,1,15,2.794062991721887,1.4340967080528344e-06,66.66666666666666,33.33333333333333,2.794062991721887,2.794062991721887,2.9114337718070633
OVERALL,BEARISH,5,0,,,,,,,
OVERALL,BEARISH,10,0,,,,,,,
OVERALL,BEARISH,20,0,,,,,,,
OVERALL,BEARISH,60,0,,,,,,,
```

## Event types

```csv
event_type,horizon,n,average_return,median_return,win_rate,directional_hit_rate,expectancy,average_mae,average_mfe
BREAKOUT,1,29,2.0970363894230153,1.4340967080528344e-06,51.724137931034484,51.724137931034484,2.0970363894230153,1.993415510752457,3.9866565161827707
BREAKOUT,5,0,,,,,,,
BREAKOUT,10,0,,,,,,,
BREAKOUT,20,0,,,,,,,
BREAKOUT,60,0,,,,,,,
BREAKDOWN,1,51,-2.633036734863173,-3.3388988004503073,9.803921568627452,90.19607843137256,-2.633036734863173,-2.8687234392903256,1.5958811337951877
BREAKDOWN,5,0,,,,,,,
BREAKDOWN,10,0,,,,,,,
BREAKDOWN,20,0,,,,,,,
BREAKDOWN,60,0,,,,,,,
CROSSOVER,1,109,0.077706829067937,-1.4084523832294304,45.87155963302752,45.87155963302752,0.077706829067937,-0.08770631669974353,3.0134049350294903
CROSSOVER,5,0,,,,,,,
CROSSOVER,10,0,,,,,,,
CROSSOVER,20,0,,,,,,,
CROSSOVER,60,0,,,,,,,
CROSSUNDER,1,112,1.0661113491781276,1.4340967080528344e-06,53.57142857142857,46.42857142857143,1.0661113491781276,0.9856201309251044,2.565379870880396
CROSSUNDER,5,0,,,,,,,
CROSSUNDER,10,0,,,,,,,
CROSSUNDER,20,0,,,,,,,
CROSSUNDER,60,0,,,,,,,
BOUNCE,1,0,,,,,,,
BOUNCE,5,0,,,,,,,
BOUNCE,10,0,,,,,,,
BOUNCE,20,0,,,,,,,
BOUNCE,60,0,,,,,,,
REVERSAL,1,318,2.0534246630634696,1.4340967080528344e-06,51.886792452830186,54.40251572327044,2.0534246630634696,1.9400282298013491,4.104701766863981
REVERSAL,5,0,,,,,,,
REVERSAL,10,0,,,,,,,
REVERSAL,20,0,,,,,,,
REVERSAL,60,0,,,,,,,
MOMENTUM,1,97,0.7989023322899174,1.4340967080528344e-06,51.546391752577314,41.23711340206185,0.7989023322899174,0.7059640184307565,2.5118663810463753
MOMENTUM,5,0,,,,,,,
MOMENTUM,10,0,,,,,,,
MOMENTUM,20,0,,,,,,,
MOMENTUM,60,0,,,,,,,
VOLUME_CONFIRMATION,1,0,,,,,,,
VOLUME_CONFIRMATION,5,0,,,,,,,
VOLUME_CONFIRMATION,10,0,,,,,,,
VOLUME_CONFIRMATION,20,0,,,,,,,
VOLUME_CONFIRMATION,60,0,,,,,,,
RELATIVE_STRENGTH,1,0,,,,,,,
RELATIVE_STRENGTH,5,0,,,,,,,
RELATIVE_STRENGTH,10,0,,,,,,,
RELATIVE_STRENGTH,20,0,,,,,,,
RELATIVE_STRENGTH,60,0,,,,,,,
VOLATILITY,1,0,,,,,,,
VOLATILITY,5,0,,,,,,,
VOLATILITY,10,0,,,,,,,
VOLATILITY,20,0,,,,,,,
VOLATILITY,60,0,,,,,,,
```

## Recency decay

```csv
recency_bucket,horizon,mean_recency_factor,n,average_return,median_return,win_rate,directional_hit_rate,expectancy,average_mae,average_mfe
0-2 sessions,1,0.9594329624368386,127,2.9783857720291667,1.4340967080528344e-06,66.92913385826772,33.07086614173229,2.9783857720291667,2.9074013905776814,4.272849953352779
0-2 sessions,5,0.9594329624368386,0,,,,,,,
0-2 sessions,10,0.9594329624368386,0,,,,,,,
0-2 sessions,20,0.9594329624368386,0,,,,,,,
0-2 sessions,60,0.9594329624368386,0,,,,,,,
3-5 sessions,1,0.7689893510481253,140,-1.3992489821603666,-3.3388988004503073,14.285714285714285,37.857142857142854,-1.3992489821603666,-1.613892230835095,2.4646623746626237
3-5 sessions,5,0.7689893510481253,0,,,,,,,
3-5 sessions,10,0.7689893510481253,0,,,,,,,
3-5 sessions,20,0.7689893510481253,0,,,,,,,
3-5 sessions,60,0.7689893510481253,0,,,,,,,
6-10 sessions,1,0.6399952247136053,118,2.9259945053176875,1.4340967080528344e-06,63.559322033898304,79.66101694915254,2.9259945053176875,2.8750622090219893,3.8995508820625924
6-10 sessions,5,0.6399952247136053,0,,,,,,,
6-10 sessions,10,0.6399952247136053,0,,,,,,,
6-10 sessions,20,0.6399952247136053,0,,,,,,,
6-10 sessions,60,0.6399952247136053,0,,,,,,,
11+ sessions,1,0.627582227677235,331,0.7772168556047324,-1.4084523832294304,49.848942598187314,56.49546827794561,0.7772168556047324,0.6501169258758901,3.0630851373473162
11+ sessions,5,0.627582227677235,0,,,,,,,
11+ sessions,10,0.627582227677235,0,,,,,,,
11+ sessions,20,0.627582227677235,0,,,,,,,
11+ sessions,60,0.627582227677235,0,,,,,,,
```

## Timeframe agreement

```csv
timeframe_agreement,horizon,n,average_return,median_return,win_rate,directional_hit_rate,expectancy,average_mae,average_mfe
all_three_bullish,1,0,,,,,,,
all_three_bullish,5,0,,,,,,,
all_three_bullish,10,0,,,,,,,
all_three_bullish,20,0,,,,,,,
all_three_bullish,60,0,,,,,,,
all_three_bearish,1,5,-1.4084523832294304,-1.4084523832294304,0.0,100.0,-1.4084523832294304,-1.4084523832294304,-1.0563400429739023
all_three_bearish,5,0,,,,,,,
all_three_bearish,10,0,,,,,,,
all_three_bearish,20,0,,,,,,,
all_three_bearish,60,0,,,,,,,
short_bullish_long_bearish,1,0,,,,,,,
short_bullish_long_bearish,5,0,,,,,,,
short_bullish_long_bearish,10,0,,,,,,,
short_bullish_long_bearish,20,0,,,,,,,
short_bullish_long_bearish,60,0,,,,,,,
short_bearish_long_bullish,1,0,,,,,,,
short_bearish_long_bullish,5,0,,,,,,,
short_bearish_long_bullish,10,0,,,,,,,
short_bearish_long_bullish,20,0,,,,,,,
short_bearish_long_bullish,60,0,,,,,,,
other_combinations,1,19,0.9949009256801414,1.4340967080528344e-06,52.63157894736842,,0.9949009256801414,0.8367427424461309,3.7863968190883135
other_combinations,5,0,,,,,,,
other_combinations,10,0,,,,,,,
other_combinations,20,0,,,,,,,
other_combinations,60,0,,,,,,,
```

## Support / resistance events

```csv
support_resistance_event,horizon,n,average_return,median_return,win_rate,directional_hit_rate,expectancy,average_mae,average_mfe
breakout_above_resistance,1,0,,,,,,,
breakout_above_resistance,5,0,,,,,,,
breakout_above_resistance,10,0,,,,,,,
breakout_above_resistance,20,0,,,,,,,
breakout_above_resistance,60,0,,,,,,,
breakdown_below_support,1,23,-2.9192365358370735,-3.3388988004503073,0.0,100.0,-2.9192365358370735,-3.1805413603106563,1.7693463185450227
breakdown_below_support,5,0,,,,,,,
breakdown_below_support,10,0,,,,,,,
breakdown_below_support,20,0,,,,,,,
breakdown_below_support,60,0,,,,,,,
bounce_from_support,1,0,,,,,,,
bounce_from_support,5,0,,,,,,,
bounce_from_support,10,0,,,,,,,
bounce_from_support,20,0,,,,,,,
bounce_from_support,60,0,,,,,,,
rejection_from_resistance,1,0,,,,,,,
rejection_from_resistance,5,0,,,,,,,
rejection_from_resistance,10,0,,,,,,,
rejection_from_resistance,20,0,,,,,,,
rejection_from_resistance,60,0,,,,,,,
```

## Confidence and feature predictive power

```csv
feature,horizon,n,pearson,spearman
short_event_score,1,24,-0.563970095499331,-0.6462264150943394
short_event_score,5,0,,
short_event_score,10,0,,
short_event_score,20,0,,
short_event_score,60,0,,
intermediate_event_score,1,24,0.37516016884268827,0.1933962264150943
intermediate_event_score,5,0,,
intermediate_event_score,10,0,,
intermediate_event_score,20,0,,
intermediate_event_score,60,0,,
long_event_score,1,24,-0.025674542869359412,-0.13679245283018865
long_event_score,5,0,,
long_event_score,10,0,,
long_event_score,20,0,,
long_event_score,60,0,,
overall_event_score,1,24,-0.2601674106968836,-0.6462264150943394
overall_event_score,5,0,,
overall_event_score,10,0,,
overall_event_score,20,0,,
overall_event_score,60,0,,
confidence,1,24,0.655785233682632,0.8820754716981131
confidence,5,0,,
confidence,10,0,,
confidence,20,0,,
confidence,60,0,,
bullish_event_count,1,24,0.4448591977395974,0.7028301886792452
bullish_event_count,5,0,,
bullish_event_count,10,0,,
bullish_event_count,20,0,,
bullish_event_count,60,0,,
bearish_event_count,1,24,0.9608726919308908,0.9700709952622315
bearish_event_count,5,0,,
bearish_event_count,10,0,,
bearish_event_count,20,0,,
bearish_event_count,60,0,,
```

## Existing Technical Score versus Technical Events

```csv
score,horizon,n,pearson,spearman,high_score_n,high_score_average_return,high_score_median_return,high_score_win_rate,high_score_directional_hit_rate,high_score_expectancy,high_score_average_mae,high_score_average_mfe,incremental_r2_of_events
existing_technical_score,1,24,0.4498204612462411,0.6462264150943394,5,-1.4084523832294304,-1.4084523832294304,0.0,,-1.4084523832294304,-1.4084523832294304,-1.0563400429739023,
overall_event_score,1,24,-0.2601674106968836,-0.6462264150943394,0,,,,,,,,
simulated_equal_weight_score,1,24,0.5188241941048257,0.6462264150943394,0,,,,,,,,
existing_technical_score,5,0,,,0,,,,,,,,
overall_event_score,5,0,,,0,,,,,,,,
simulated_equal_weight_score,5,0,,,0,,,,,,,,
existing_technical_score,10,0,,,0,,,,,,,,
overall_event_score,10,0,,,0,,,,,,,,
simulated_equal_weight_score,10,0,,,0,,,,,,,,
existing_technical_score,20,0,,,0,,,,,,,,
overall_event_score,20,0,,,0,,,,,,,,
simulated_equal_weight_score,20,0,,,0,,,,,,,,
existing_technical_score,60,0,,,0,,,,,,,,
overall_event_score,60,0,,,0,,,,,,,,
simulated_equal_weight_score,60,0,,,0,,,,,,,,
```

`simulated_equal_weight_score` is a 50/50 analytical simulation only. It is
not consumed by Baseline, Enhanced, Risk Score, or BUY/WAIT/AVOID.

## Market regimes

```csv
regime_dimension,regime,horizon,n,average_return,median_return,win_rate,directional_hit_rate,expectancy,average_mae,average_mfe
trend_regime,bullish,1,24,0.4942023196573139,-1.4084523832294304,41.66666666666667,,0.4942023196573139,0.36899375793038897,2.7774933061586857
trend_regime,bullish,5,0,,,,,,,
trend_regime,bullish,10,0,,,,,,,
trend_regime,bullish,20,0,,,,,,,
trend_regime,bullish,60,0,,,,,,,
trend_regime,bearish,1,0,,,,,,,
trend_regime,bearish,5,0,,,,,,,
trend_regime,bearish,10,0,,,,,,,
trend_regime,bearish,20,0,,,,,,,
trend_regime,bearish,60,0,,,,,,,
trend_regime,sideways,1,0,,,,,,,
trend_regime,sideways,5,0,,,,,,,
trend_regime,sideways,10,0,,,,,,,
trend_regime,sideways,20,0,,,,,,,
trend_regime,sideways,60,0,,,,,,,
volatility_regime,low_volatility,1,24,0.4942023196573139,-1.4084523832294304,41.66666666666667,,0.4942023196573139,0.36899375793038897,2.7774933061586857
volatility_regime,low_volatility,5,0,,,,,,,
volatility_regime,low_volatility,10,0,,,,,,,
volatility_regime,low_volatility,20,0,,,,,,,
volatility_regime,low_volatility,60,0,,,,,,,
volatility_regime,high_volatility,1,0,,,,,,,
volatility_regime,high_volatility,5,0,,,,,,,
volatility_regime,high_volatility,10,0,,,,,,,
volatility_regime,high_volatility,20,0,,,,,,,
volatility_regime,high_volatility,60,0,,,,,,,
volatility_regime,unknown,1,0,,,,,,,
volatility_regime,unknown,5,0,,,,,,,
volatility_regime,unknown,10,0,,,,,,,
volatility_regime,unknown,20,0,,,,,,,
volatility_regime,unknown,60,0,,,,,,,
```

Trend regimes are a deterministic grouping of the point-in-time market stage.
High volatility means point-in-time VIX >= 25; these are reporting categories,
not changes to Technical Events thresholds.

## Anti-look-ahead and integrity

- The stored entry is never replaced with a later entry price.
- Split/dividend adjustment uses only a mechanical adjustment factor.
- Outcomes use daily sessions strictly after `signal_day`.
- MAE/MFE use only the path through each matured horizon.
- The immutable signal ledger is never rewritten by this evaluator.
- Integrity errors: **0**
- Details: `[]`

## Verdict

**INSUFFICIENT DATA**

Reason: `0/100 matured 20D observations`

No engine formula, weight, decay parameter, threshold, Enhanced score, or
authoritative decision is recalibrated by this report.
