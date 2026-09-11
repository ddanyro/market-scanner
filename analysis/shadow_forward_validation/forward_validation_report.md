# Enhanced Scoring forward validation

Generated: 2026-09-11T11:39:29+00:00

## Data coverage

```csv
partition,predictions,execution_eligible_pct,options_pct,options_partial_pct,portfolio_fit_pct,matured_1d,matured_5d,matured_10d,matured_20d,matured_60d
calibration,332,92.7710843373494,0.0,12.048192771084338,60.24096385542169,94,0,0,0,0
holdout_locked,0,,,,,0,0,0,0,0
```

## Gross, net and benchmark alpha

```csv
partition,horizon,metric,n,mean,median,win_rate,average_gain,average_loss,expectancy
calibration,1,gross_return_pct,90,-1.8228771591851323,-1.7568192325473908,21.11111111111111,1.3295607228656816,-2.66648729663535,-1.8228771591851323
calibration,1,net_return_pct,3,-8.267651932313859,-8.267651932313859,0.0,,-8.267651932313859,-8.267651932313859
calibration,1,spy_return_pct,90,-0.7202936700798246,-0.7240929496966642,0.0,,-0.7202936700798246,-0.7202936700798246
calibration,1,qqq_return_pct,90,-1.2220507838260748,-1.2485170119230449,0.0,,-1.2220507838260748,-1.2220507838260748
calibration,1,sector_return_pct,48,-0.667435200683458,-0.5701922646832225,16.666666666666664,0.33146936040021335,-0.8672161129001921,-0.667435200683458
calibration,1,cash_return_pct,90,0.014802284080916994,0.014801009822229538,100.0,0.014802284080916994,,0.014802284080916994
calibration,1,gross_alpha_spy_pct,90,-1.102583489105308,-1.0447649183778551,32.22222222222222,1.494235912960565,-2.3371369753333453,-1.102583489105308
calibration,1,net_alpha_spy_pct,3,-7.513108043716978,-7.516571815344809,0.0,,-7.513108043716978,-7.513108043716978
calibration,1,net_alpha_qqq_pct,3,-6.968715931444763,-6.9723709829800375,0.0,,-6.968715931444763,-6.968715931444763
calibration,1,net_alpha_sector_pct,3,-7.792494198759516,-7.777230944077508,0.0,,-7.792494198759516,-7.792494198759516
calibration,1,net_alpha_cash_pct,3,-8.282442745804065,-8.28244147133136,0.0,,-8.282442745804065,-8.282442745804065
calibration,5,gross_return_pct,0,,,,,,
calibration,5,net_return_pct,0,,,,,,
calibration,5,spy_return_pct,0,,,,,,
calibration,5,qqq_return_pct,0,,,,,,
calibration,5,sector_return_pct,0,,,,,,
calibration,5,cash_return_pct,0,,,,,,
calibration,5,gross_alpha_spy_pct,0,,,,,,
calibration,5,net_alpha_spy_pct,0,,,,,,
calibration,5,net_alpha_qqq_pct,0,,,,,,
calibration,5,net_alpha_sector_pct,0,,,,,,
calibration,5,net_alpha_cash_pct,0,,,,,,
calibration,10,gross_return_pct,0,,,,,,
calibration,10,net_return_pct,0,,,,,,
calibration,10,spy_return_pct,0,,,,,,
calibration,10,qqq_return_pct,0,,,,,,
calibration,10,sector_return_pct,0,,,,,,
calibration,10,cash_return_pct,0,,,,,,
calibration,10,gross_alpha_spy_pct,0,,,,,,
calibration,10,net_alpha_spy_pct,0,,,,,,
calibration,10,net_alpha_qqq_pct,0,,,,,,
calibration,10,net_alpha_sector_pct,0,,,,,,
calibration,10,net_alpha_cash_pct,0,,,,,,
calibration,20,gross_return_pct,0,,,,,,
calibration,20,net_return_pct,0,,,,,,
calibration,20,spy_return_pct,0,,,,,,
calibration,20,qqq_return_pct,0,,,,,,
calibration,20,sector_return_pct,0,,,,,,
calibration,20,cash_return_pct,0,,,,,,
calibration,20,gross_alpha_spy_pct,0,,,,,,
calibration,20,net_alpha_spy_pct,0,,,,,,
calibration,20,net_alpha_qqq_pct,0,,,,,,
calibration,20,net_alpha_sector_pct,0,,,,,,
calibration,20,net_alpha_cash_pct,0,,,,,,
calibration,60,gross_return_pct,0,,,,,,
calibration,60,net_return_pct,0,,,,,,
calibration,60,spy_return_pct,0,,,,,,
calibration,60,qqq_return_pct,0,,,,,,
calibration,60,sector_return_pct,0,,,,,,
calibration,60,cash_return_pct,0,,,,,,
calibration,60,gross_alpha_spy_pct,0,,,,,,
calibration,60,net_alpha_spy_pct,0,,,,,,
calibration,60,net_alpha_qqq_pct,0,,,,,,
calibration,60,net_alpha_sector_pct,0,,,,,,
calibration,60,net_alpha_cash_pct,0,,,,,,
holdout_locked,1,gross_return_pct,0,,,,,,
holdout_locked,1,net_return_pct,0,,,,,,
holdout_locked,1,spy_return_pct,0,,,,,,
holdout_locked,1,qqq_return_pct,0,,,,,,
holdout_locked,1,sector_return_pct,0,,,,,,
holdout_locked,1,cash_return_pct,0,,,,,,
holdout_locked,1,gross_alpha_spy_pct,0,,,,,,
holdout_locked,1,net_alpha_spy_pct,0,,,,,,
holdout_locked,1,net_alpha_qqq_pct,0,,,,,,
holdout_locked,1,net_alpha_sector_pct,0,,,,,,
holdout_locked,1,net_alpha_cash_pct,0,,,,,,
holdout_locked,5,gross_return_pct,0,,,,,,
holdout_locked,5,net_return_pct,0,,,,,,
holdout_locked,5,spy_return_pct,0,,,,,,
holdout_locked,5,qqq_return_pct,0,,,,,,
holdout_locked,5,sector_return_pct,0,,,,,,
holdout_locked,5,cash_return_pct,0,,,,,,
holdout_locked,5,gross_alpha_spy_pct,0,,,,,,
holdout_locked,5,net_alpha_spy_pct,0,,,,,,
holdout_locked,5,net_alpha_qqq_pct,0,,,,,,
holdout_locked,5,net_alpha_sector_pct,0,,,,,,
holdout_locked,5,net_alpha_cash_pct,0,,,,,,
holdout_locked,10,gross_return_pct,0,,,,,,
holdout_locked,10,net_return_pct,0,,,,,,
holdout_locked,10,spy_return_pct,0,,,,,,
holdout_locked,10,qqq_return_pct,0,,,,,,
holdout_locked,10,sector_return_pct,0,,,,,,
holdout_locked,10,cash_return_pct,0,,,,,,
holdout_locked,10,gross_alpha_spy_pct,0,,,,,,
holdout_locked,10,net_alpha_spy_pct,0,,,,,,
holdout_locked,10,net_alpha_qqq_pct,0,,,,,,
holdout_locked,10,net_alpha_sector_pct,0,,,,,,
holdout_locked,10,net_alpha_cash_pct,0,,,,,,
holdout_locked,20,gross_return_pct,0,,,,,,
holdout_locked,20,net_return_pct,0,,,,,,
holdout_locked,20,spy_return_pct,0,,,,,,
holdout_locked,20,qqq_return_pct,0,,,,,,
holdout_locked,20,sector_return_pct,0,,,,,,
holdout_locked,20,cash_return_pct,0,,,,,,
holdout_locked,20,gross_alpha_spy_pct,0,,,,,,
holdout_locked,20,net_alpha_spy_pct,0,,,,,,
holdout_locked,20,net_alpha_qqq_pct,0,,,,,,
holdout_locked,20,net_alpha_sector_pct,0,,,,,,
holdout_locked,20,net_alpha_cash_pct,0,,,,,,
holdout_locked,60,gross_return_pct,0,,,,,,
holdout_locked,60,net_return_pct,0,,,,,,
holdout_locked,60,spy_return_pct,0,,,,,,
holdout_locked,60,qqq_return_pct,0,,,,,,
holdout_locked,60,sector_return_pct,0,,,,,,
holdout_locked,60,cash_return_pct,0,,,,,,
holdout_locked,60,gross_alpha_spy_pct,0,,,,,,
holdout_locked,60,net_alpha_spy_pct,0,,,,,,
holdout_locked,60,net_alpha_qqq_pct,0,,,,,,
holdout_locked,60,net_alpha_sector_pct,0,,,,,,
holdout_locked,60,net_alpha_cash_pct,0,,,,,,
```

## Baseline versus Enhanced

```csv
partition,horizon,model,gross_return_pct_n,gross_return_pct_mean,gross_return_pct_win_rate,net_return_pct_n,net_return_pct_mean,net_return_pct_win_rate,net_alpha_spy_pct_n,net_alpha_spy_pct_mean,net_alpha_spy_pct_win_rate,net_alpha_qqq_pct_n,net_alpha_qqq_pct_mean,net_alpha_qqq_pct_win_rate,net_alpha_sector_pct_n,net_alpha_sector_pct_mean,net_alpha_sector_pct_win_rate,net_alpha_cash_pct_n,net_alpha_cash_pct_mean,net_alpha_cash_pct_win_rate,mae_pct_n,mae_pct_mean,mae_pct_win_rate,mfe_pct_n,mfe_pct_mean,mfe_pct_win_rate,path_max_drawdown_pct_n,path_max_drawdown_pct_mean,path_max_drawdown_pct_win_rate
calibration,1,baseline_buy,18,-2.756265096705971,5.555555555555555,0,,,0,,,0,,,0,,,0,,,18,-4.476797485632109,0.0,18,-1.7496424267768058,27.77777777777778,18,0.0,0.0
calibration,1,enhanced_shadow_buy,18,-2.756265096705971,5.555555555555555,0,,,0,,,0,,,0,,,0,,,18,-4.476797485632109,0.0,18,-1.7496424267768058,27.77777777777778,18,0.0,0.0
calibration,1,enhanced_raw_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
calibration,1,enhanced_adjusted_75,22,0.2495146829982722,54.54545454545454,0,,,0,,,0,,,0,,,0,,,22,-1.942414835760578,0.0,22,1.1584704298064714,81.81818181818183,22,0.0,0.0
calibration,5,baseline_buy,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
calibration,5,enhanced_shadow_buy,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
calibration,5,enhanced_raw_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
calibration,5,enhanced_adjusted_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
calibration,10,baseline_buy,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
calibration,10,enhanced_shadow_buy,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
calibration,10,enhanced_raw_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
calibration,10,enhanced_adjusted_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
calibration,20,baseline_buy,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
calibration,20,enhanced_shadow_buy,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
calibration,20,enhanced_raw_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
calibration,20,enhanced_adjusted_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
calibration,60,baseline_buy,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
calibration,60,enhanced_shadow_buy,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
calibration,60,enhanced_raw_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
calibration,60,enhanced_adjusted_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,1,baseline_buy,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,1,enhanced_shadow_buy,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,1,enhanced_raw_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,1,enhanced_adjusted_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,5,baseline_buy,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,5,enhanced_shadow_buy,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,5,enhanced_raw_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,5,enhanced_adjusted_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,10,baseline_buy,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,10,enhanced_shadow_buy,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,10,enhanced_raw_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,10,enhanced_adjusted_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,20,baseline_buy,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,20,enhanced_shadow_buy,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,20,enhanced_raw_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,20,enhanced_adjusted_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,60,baseline_buy,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,60,enhanced_shadow_buy,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,60,enhanced_raw_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
holdout_locked,60,enhanced_adjusted_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
```

## Risk-adjusted event-study metrics

```csv
partition,model,days,max_drawdown_pct,annualized_volatility_pct,approx_sharpe,approx_sortino
calibration,baseline,0,,,,
calibration,enhanced_shadow,0,,,,
calibration,enhanced_raw,0,,,,
calibration,enhanced_adjusted,0,,,,
holdout_locked,baseline,0,,,,
holdout_locked,enhanced_shadow,0,,,,
holdout_locked,enhanced_raw,0,,,,
holdout_locked,enhanced_adjusted,0,,,,
```

## Score buckets — net alpha versus SPY

```csv
partition,horizon,score,bucket,n,mean,median,win_rate,average_gain,average_loss,expectancy
calibration,1,baseline,0-49,0,,,,,,
calibration,1,baseline,50-59,0,,,,,,
calibration,1,baseline,60-69,0,,,,,,
calibration,1,baseline,70-74,0,,,,,,
calibration,1,baseline,75-79,3,-7.513108043716978,-7.516571815344809,0.0,,-7.513108043716978,-7.513108043716978
calibration,1,baseline,80-84,0,,,,,,
calibration,1,baseline,85-89,0,,,,,,
calibration,1,baseline,90+,0,,,,,,
calibration,1,raw,0-49,0,,,,,,
calibration,1,raw,50-59,0,,,,,,
calibration,1,raw,60-69,3,-7.513108043716978,-7.516571815344809,0.0,,-7.513108043716978,-7.513108043716978
calibration,1,raw,70-74,0,,,,,,
calibration,1,raw,75-79,0,,,,,,
calibration,1,raw,80-84,0,,,,,,
calibration,1,raw,85-89,0,,,,,,
calibration,1,raw,90+,0,,,,,,
calibration,1,adjusted,0-49,0,,,,,,
calibration,1,adjusted,50-59,0,,,,,,
calibration,1,adjusted,60-69,0,,,,,,
calibration,1,adjusted,70-74,3,-7.513108043716978,-7.516571815344809,0.0,,-7.513108043716978,-7.513108043716978
calibration,1,adjusted,75-79,0,,,,,,
calibration,1,adjusted,80-84,0,,,,,,
calibration,1,adjusted,85-89,0,,,,,,
calibration,1,adjusted,90+,0,,,,,,
calibration,5,baseline,0-49,0,,,,,,
calibration,5,baseline,50-59,0,,,,,,
calibration,5,baseline,60-69,0,,,,,,
calibration,5,baseline,70-74,0,,,,,,
calibration,5,baseline,75-79,0,,,,,,
calibration,5,baseline,80-84,0,,,,,,
calibration,5,baseline,85-89,0,,,,,,
calibration,5,baseline,90+,0,,,,,,
calibration,5,raw,0-49,0,,,,,,
calibration,5,raw,50-59,0,,,,,,
calibration,5,raw,60-69,0,,,,,,
calibration,5,raw,70-74,0,,,,,,
calibration,5,raw,75-79,0,,,,,,
calibration,5,raw,80-84,0,,,,,,
calibration,5,raw,85-89,0,,,,,,
calibration,5,raw,90+,0,,,,,,
calibration,5,adjusted,0-49,0,,,,,,
calibration,5,adjusted,50-59,0,,,,,,
calibration,5,adjusted,60-69,0,,,,,,
calibration,5,adjusted,70-74,0,,,,,,
calibration,5,adjusted,75-79,0,,,,,,
calibration,5,adjusted,80-84,0,,,,,,
calibration,5,adjusted,85-89,0,,,,,,
calibration,5,adjusted,90+,0,,,,,,
calibration,10,baseline,0-49,0,,,,,,
calibration,10,baseline,50-59,0,,,,,,
calibration,10,baseline,60-69,0,,,,,,
calibration,10,baseline,70-74,0,,,,,,
calibration,10,baseline,75-79,0,,,,,,
calibration,10,baseline,80-84,0,,,,,,
calibration,10,baseline,85-89,0,,,,,,
calibration,10,baseline,90+,0,,,,,,
calibration,10,raw,0-49,0,,,,,,
calibration,10,raw,50-59,0,,,,,,
calibration,10,raw,60-69,0,,,,,,
calibration,10,raw,70-74,0,,,,,,
calibration,10,raw,75-79,0,,,,,,
calibration,10,raw,80-84,0,,,,,,
calibration,10,raw,85-89,0,,,,,,
calibration,10,raw,90+,0,,,,,,
calibration,10,adjusted,0-49,0,,,,,,
calibration,10,adjusted,50-59,0,,,,,,
calibration,10,adjusted,60-69,0,,,,,,
calibration,10,adjusted,70-74,0,,,,,,
calibration,10,adjusted,75-79,0,,,,,,
calibration,10,adjusted,80-84,0,,,,,,
calibration,10,adjusted,85-89,0,,,,,,
calibration,10,adjusted,90+,0,,,,,,
calibration,20,baseline,0-49,0,,,,,,
calibration,20,baseline,50-59,0,,,,,,
calibration,20,baseline,60-69,0,,,,,,
calibration,20,baseline,70-74,0,,,,,,
calibration,20,baseline,75-79,0,,,,,,
calibration,20,baseline,80-84,0,,,,,,
calibration,20,baseline,85-89,0,,,,,,
calibration,20,baseline,90+,0,,,,,,
calibration,20,raw,0-49,0,,,,,,
calibration,20,raw,50-59,0,,,,,,
calibration,20,raw,60-69,0,,,,,,
calibration,20,raw,70-74,0,,,,,,
calibration,20,raw,75-79,0,,,,,,
calibration,20,raw,80-84,0,,,,,,
calibration,20,raw,85-89,0,,,,,,
calibration,20,raw,90+,0,,,,,,
calibration,20,adjusted,0-49,0,,,,,,
calibration,20,adjusted,50-59,0,,,,,,
calibration,20,adjusted,60-69,0,,,,,,
calibration,20,adjusted,70-74,0,,,,,,
calibration,20,adjusted,75-79,0,,,,,,
calibration,20,adjusted,80-84,0,,,,,,
calibration,20,adjusted,85-89,0,,,,,,
calibration,20,adjusted,90+,0,,,,,,
calibration,60,baseline,0-49,0,,,,,,
calibration,60,baseline,50-59,0,,,,,,
calibration,60,baseline,60-69,0,,,,,,
calibration,60,baseline,70-74,0,,,,,,
calibration,60,baseline,75-79,0,,,,,,
calibration,60,baseline,80-84,0,,,,,,
calibration,60,baseline,85-89,0,,,,,,
calibration,60,baseline,90+,0,,,,,,
calibration,60,raw,0-49,0,,,,,,
calibration,60,raw,50-59,0,,,,,,
calibration,60,raw,60-69,0,,,,,,
calibration,60,raw,70-74,0,,,,,,
calibration,60,raw,75-79,0,,,,,,
calibration,60,raw,80-84,0,,,,,,
calibration,60,raw,85-89,0,,,,,,
calibration,60,raw,90+,0,,,,,,
calibration,60,adjusted,0-49,0,,,,,,
calibration,60,adjusted,50-59,0,,,,,,
calibration,60,adjusted,60-69,0,,,,,,
calibration,60,adjusted,70-74,0,,,,,,
calibration,60,adjusted,75-79,0,,,,,,
calibration,60,adjusted,80-84,0,,,,,,
calibration,60,adjusted,85-89,0,,,,,,
calibration,60,adjusted,90+,0,,,,,,
holdout_locked,1,baseline,0-49,0,,,,,,
holdout_locked,1,baseline,50-59,0,,,,,,
holdout_locked,1,baseline,60-69,0,,,,,,
holdout_locked,1,baseline,70-74,0,,,,,,
holdout_locked,1,baseline,75-79,0,,,,,,
holdout_locked,1,baseline,80-84,0,,,,,,
holdout_locked,1,baseline,85-89,0,,,,,,
holdout_locked,1,baseline,90+,0,,,,,,
holdout_locked,1,raw,0-49,0,,,,,,
holdout_locked,1,raw,50-59,0,,,,,,
holdout_locked,1,raw,60-69,0,,,,,,
holdout_locked,1,raw,70-74,0,,,,,,
holdout_locked,1,raw,75-79,0,,,,,,
holdout_locked,1,raw,80-84,0,,,,,,
holdout_locked,1,raw,85-89,0,,,,,,
holdout_locked,1,raw,90+,0,,,,,,
holdout_locked,1,adjusted,0-49,0,,,,,,
holdout_locked,1,adjusted,50-59,0,,,,,,
holdout_locked,1,adjusted,60-69,0,,,,,,
holdout_locked,1,adjusted,70-74,0,,,,,,
holdout_locked,1,adjusted,75-79,0,,,,,,
holdout_locked,1,adjusted,80-84,0,,,,,,
holdout_locked,1,adjusted,85-89,0,,,,,,
holdout_locked,1,adjusted,90+,0,,,,,,
holdout_locked,5,baseline,0-49,0,,,,,,
holdout_locked,5,baseline,50-59,0,,,,,,
holdout_locked,5,baseline,60-69,0,,,,,,
holdout_locked,5,baseline,70-74,0,,,,,,
holdout_locked,5,baseline,75-79,0,,,,,,
holdout_locked,5,baseline,80-84,0,,,,,,
holdout_locked,5,baseline,85-89,0,,,,,,
holdout_locked,5,baseline,90+,0,,,,,,
holdout_locked,5,raw,0-49,0,,,,,,
holdout_locked,5,raw,50-59,0,,,,,,
holdout_locked,5,raw,60-69,0,,,,,,
holdout_locked,5,raw,70-74,0,,,,,,
holdout_locked,5,raw,75-79,0,,,,,,
holdout_locked,5,raw,80-84,0,,,,,,
holdout_locked,5,raw,85-89,0,,,,,,
holdout_locked,5,raw,90+,0,,,,,,
holdout_locked,5,adjusted,0-49,0,,,,,,
holdout_locked,5,adjusted,50-59,0,,,,,,
holdout_locked,5,adjusted,60-69,0,,,,,,
holdout_locked,5,adjusted,70-74,0,,,,,,
holdout_locked,5,adjusted,75-79,0,,,,,,
holdout_locked,5,adjusted,80-84,0,,,,,,
holdout_locked,5,adjusted,85-89,0,,,,,,
holdout_locked,5,adjusted,90+,0,,,,,,
holdout_locked,10,baseline,0-49,0,,,,,,
holdout_locked,10,baseline,50-59,0,,,,,,
holdout_locked,10,baseline,60-69,0,,,,,,
holdout_locked,10,baseline,70-74,0,,,,,,
holdout_locked,10,baseline,75-79,0,,,,,,
holdout_locked,10,baseline,80-84,0,,,,,,
holdout_locked,10,baseline,85-89,0,,,,,,
holdout_locked,10,baseline,90+,0,,,,,,
holdout_locked,10,raw,0-49,0,,,,,,
holdout_locked,10,raw,50-59,0,,,,,,
holdout_locked,10,raw,60-69,0,,,,,,
holdout_locked,10,raw,70-74,0,,,,,,
holdout_locked,10,raw,75-79,0,,,,,,
holdout_locked,10,raw,80-84,0,,,,,,
holdout_locked,10,raw,85-89,0,,,,,,
holdout_locked,10,raw,90+,0,,,,,,
holdout_locked,10,adjusted,0-49,0,,,,,,
holdout_locked,10,adjusted,50-59,0,,,,,,
holdout_locked,10,adjusted,60-69,0,,,,,,
holdout_locked,10,adjusted,70-74,0,,,,,,
holdout_locked,10,adjusted,75-79,0,,,,,,
holdout_locked,10,adjusted,80-84,0,,,,,,
holdout_locked,10,adjusted,85-89,0,,,,,,
holdout_locked,10,adjusted,90+,0,,,,,,
holdout_locked,20,baseline,0-49,0,,,,,,
holdout_locked,20,baseline,50-59,0,,,,,,
holdout_locked,20,baseline,60-69,0,,,,,,
holdout_locked,20,baseline,70-74,0,,,,,,
holdout_locked,20,baseline,75-79,0,,,,,,
holdout_locked,20,baseline,80-84,0,,,,,,
holdout_locked,20,baseline,85-89,0,,,,,,
holdout_locked,20,baseline,90+,0,,,,,,
holdout_locked,20,raw,0-49,0,,,,,,
holdout_locked,20,raw,50-59,0,,,,,,
holdout_locked,20,raw,60-69,0,,,,,,
holdout_locked,20,raw,70-74,0,,,,,,
holdout_locked,20,raw,75-79,0,,,,,,
holdout_locked,20,raw,80-84,0,,,,,,
holdout_locked,20,raw,85-89,0,,,,,,
holdout_locked,20,raw,90+,0,,,,,,
holdout_locked,20,adjusted,0-49,0,,,,,,
holdout_locked,20,adjusted,50-59,0,,,,,,
holdout_locked,20,adjusted,60-69,0,,,,,,
holdout_locked,20,adjusted,70-74,0,,,,,,
holdout_locked,20,adjusted,75-79,0,,,,,,
holdout_locked,20,adjusted,80-84,0,,,,,,
holdout_locked,20,adjusted,85-89,0,,,,,,
holdout_locked,20,adjusted,90+,0,,,,,,
holdout_locked,60,baseline,0-49,0,,,,,,
holdout_locked,60,baseline,50-59,0,,,,,,
holdout_locked,60,baseline,60-69,0,,,,,,
holdout_locked,60,baseline,70-74,0,,,,,,
holdout_locked,60,baseline,75-79,0,,,,,,
holdout_locked,60,baseline,80-84,0,,,,,,
holdout_locked,60,baseline,85-89,0,,,,,,
holdout_locked,60,baseline,90+,0,,,,,,
holdout_locked,60,raw,0-49,0,,,,,,
holdout_locked,60,raw,50-59,0,,,,,,
holdout_locked,60,raw,60-69,0,,,,,,
holdout_locked,60,raw,70-74,0,,,,,,
holdout_locked,60,raw,75-79,0,,,,,,
holdout_locked,60,raw,80-84,0,,,,,,
holdout_locked,60,raw,85-89,0,,,,,,
holdout_locked,60,raw,90+,0,,,,,,
holdout_locked,60,adjusted,0-49,0,,,,,,
holdout_locked,60,adjusted,50-59,0,,,,,,
holdout_locked,60,adjusted,60-69,0,,,,,,
holdout_locked,60,adjusted,70-74,0,,,,,,
holdout_locked,60,adjusted,75-79,0,,,,,,
holdout_locked,60,adjusted,80-84,0,,,,,,
holdout_locked,60,adjusted,85-89,0,,,,,,
holdout_locked,60,adjusted,90+,0,,,,,,
```

## Options availability/control cohort

```csv
partition,options_cohort,options_data_quality,predictions,baseline_score_mean,raw_score_mean,availability_adjusted_raw_mean,portfolio_fit_coverage_pct,net_alpha_spy_1d_n,net_alpha_spy_1d_mean,net_alpha_spy_5d_n,net_alpha_spy_5d_mean,net_alpha_spy_10d_n,net_alpha_spy_10d_mean,net_alpha_spy_20d_n,net_alpha_spy_20d_mean,net_alpha_spy_60d_n,net_alpha_spy_60d_mean
calibration,OPTIONS_DATA_PARTIAL,partial,27,82.4074074074074,73.46666666666665,76.07592592592592,100.0,0,,0,,0,,0,,0,
calibration,OPTIONS_DATA_PARTIAL,quote_only,13,86.53846153846153,71.93615384615383,74.37538461538462,100.0,0,,0,,0,,0,,0,
calibration,OPTIONS_NOT_ELIGIBLE,unavailable,223,79.93273542600897,64.3916143497758,65.99076233183855,40.80717488789238,0,,0,,0,,0,,0,
calibration,OPTIONS_UNAVAILABLE,unavailable,69,78.26086956521739,69.87014492753623,72.07724637681159,100.0,3,-7.513108043716978,0,,0,,0,,0,
```

Availability is reported separately from the formula value. Missing options
data is never classified as an observed score of 50.

## Portfolio Fit cohorts

```csv
partition,cohort,predictions,raw_score_mean,adjusted_score_mean,net_alpha_spy_1d_n,net_alpha_spy_1d_mean,net_alpha_spy_1d_median,net_alpha_spy_1d_win_rate,net_alpha_spy_1d_average_gain,net_alpha_spy_1d_average_loss,net_alpha_spy_1d_expectancy,net_alpha_spy_5d_n,net_alpha_spy_5d_mean,net_alpha_spy_5d_median,net_alpha_spy_5d_win_rate,net_alpha_spy_5d_average_gain,net_alpha_spy_5d_average_loss,net_alpha_spy_5d_expectancy,net_alpha_spy_10d_n,net_alpha_spy_10d_mean,net_alpha_spy_10d_median,net_alpha_spy_10d_win_rate,net_alpha_spy_10d_average_gain,net_alpha_spy_10d_average_loss,net_alpha_spy_10d_expectancy,net_alpha_spy_20d_n,net_alpha_spy_20d_mean,net_alpha_spy_20d_median,net_alpha_spy_20d_win_rate,net_alpha_spy_20d_average_gain,net_alpha_spy_20d_average_loss,net_alpha_spy_20d_expectancy,net_alpha_spy_60d_n,net_alpha_spy_60d_mean,net_alpha_spy_60d_median,net_alpha_spy_60d_win_rate,net_alpha_spy_60d_average_gain,net_alpha_spy_60d_average_loss,net_alpha_spy_60d_expectancy
calibration,missing,132,66.67469696969698,66.67469696969698,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,other_observed,68,59.916470588235285,60.27779411764706,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,raw_medium_fit_good,132,69.87696969696968,74.21378787878788,3,-7.513108043716978,-7.516571815344809,0.0,,-7.513108043716978,-7.513108043716978,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
```

## Component contribution and redundancy

```csv
partition,horizon,component,n,pearson_forward_alpha,spearman_forward_alpha,max_abs_component_correlation,incremental_r2
calibration,1,technical_score,3,,,0.43907225233019315,
calibration,1,momentum_score,3,,,0.49990482685619947,
calibration,1,research_score,3,,,0.43917980476145324,
calibration,1,volatility_score,3,,,0.3713516784639485,
calibration,1,liquidity_score,3,,,0.2505879056062277,
calibration,1,options_score,0,,,,
calibration,1,relative_opportunity_score,3,,,,
calibration,1,risk_reward_score,3,,,0.4999048268561994,
calibration,5,technical_score,0,,,0.43907225233019315,
calibration,5,momentum_score,0,,,0.49990482685619947,
calibration,5,research_score,0,,,0.43917980476145324,
calibration,5,volatility_score,0,,,0.3713516784639485,
calibration,5,liquidity_score,0,,,0.2505879056062277,
calibration,5,options_score,0,,,,
calibration,5,relative_opportunity_score,0,,,,
calibration,5,risk_reward_score,0,,,0.4999048268561994,
calibration,10,technical_score,0,,,0.43907225233019315,
calibration,10,momentum_score,0,,,0.49990482685619947,
calibration,10,research_score,0,,,0.43917980476145324,
calibration,10,volatility_score,0,,,0.3713516784639485,
calibration,10,liquidity_score,0,,,0.2505879056062277,
calibration,10,options_score,0,,,,
calibration,10,relative_opportunity_score,0,,,,
calibration,10,risk_reward_score,0,,,0.4999048268561994,
calibration,20,technical_score,0,,,0.43907225233019315,
calibration,20,momentum_score,0,,,0.49990482685619947,
calibration,20,research_score,0,,,0.43917980476145324,
calibration,20,volatility_score,0,,,0.3713516784639485,
calibration,20,liquidity_score,0,,,0.2505879056062277,
calibration,20,options_score,0,,,,
calibration,20,relative_opportunity_score,0,,,,
calibration,20,risk_reward_score,0,,,0.4999048268561994,
calibration,60,technical_score,0,,,0.43907225233019315,
calibration,60,momentum_score,0,,,0.49990482685619947,
calibration,60,research_score,0,,,0.43917980476145324,
calibration,60,volatility_score,0,,,0.3713516784639485,
calibration,60,liquidity_score,0,,,0.2505879056062277,
calibration,60,options_score,0,,,,
calibration,60,relative_opportunity_score,0,,,,
calibration,60,risk_reward_score,0,,,0.4999048268561994,
holdout_locked,1,technical_score,0,,,,
holdout_locked,1,momentum_score,0,,,,
holdout_locked,1,research_score,0,,,,
holdout_locked,1,volatility_score,0,,,,
holdout_locked,1,liquidity_score,0,,,,
holdout_locked,1,options_score,0,,,,
holdout_locked,1,relative_opportunity_score,0,,,,
holdout_locked,1,risk_reward_score,0,,,,
holdout_locked,5,technical_score,0,,,,
holdout_locked,5,momentum_score,0,,,,
holdout_locked,5,research_score,0,,,,
holdout_locked,5,volatility_score,0,,,,
holdout_locked,5,liquidity_score,0,,,,
holdout_locked,5,options_score,0,,,,
holdout_locked,5,relative_opportunity_score,0,,,,
holdout_locked,5,risk_reward_score,0,,,,
holdout_locked,10,technical_score,0,,,,
holdout_locked,10,momentum_score,0,,,,
holdout_locked,10,research_score,0,,,,
holdout_locked,10,volatility_score,0,,,,
holdout_locked,10,liquidity_score,0,,,,
holdout_locked,10,options_score,0,,,,
holdout_locked,10,relative_opportunity_score,0,,,,
holdout_locked,10,risk_reward_score,0,,,,
holdout_locked,20,technical_score,0,,,,
holdout_locked,20,momentum_score,0,,,,
holdout_locked,20,research_score,0,,,,
holdout_locked,20,volatility_score,0,,,,
holdout_locked,20,liquidity_score,0,,,,
holdout_locked,20,options_score,0,,,,
holdout_locked,20,relative_opportunity_score,0,,,,
holdout_locked,20,risk_reward_score,0,,,,
holdout_locked,60,technical_score,0,,,,
holdout_locked,60,momentum_score,0,,,,
holdout_locked,60,research_score,0,,,,
holdout_locked,60,volatility_score,0,,,,
holdout_locked,60,liquidity_score,0,,,,
holdout_locked,60,options_score,0,,,,
holdout_locked,60,relative_opportunity_score,0,,,,
holdout_locked,60,risk_reward_score,0,,,,
```

Incremental R² is intentionally withheld until at least 30 complete matured
observations are available; this avoids unstable attribution on tiny samples.

## Baseline / Enhanced decision disagreements

```csv
snapshot_id,recorded_at,sample_partition,symbol,baseline_decision,enhanced_decision,raw_score,portfolio_fit,adjusted_score,net_alpha_spy_pct_1d,net_alpha_spy_pct_5d,net_alpha_spy_pct_10d,net_alpha_spy_pct_20d,net_alpha_spy_pct_60d
5522e100effd8a5697d20573,2026-09-10T21:10:03+00:00,calibration,TRGP,BUY,WAIT,73.1,100.0,77.13,,,,,
53c26794356af012cc307291,2026-09-11T06:44:58+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,,,,,
8ca424c3afa2faff80cd5fa8,2026-09-11T08:54:52+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,,,,,
3457725c926d4c9bca6c86ef,2026-09-11T09:29:41+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,,,,,
62964736889913e1a2f9310e,2026-09-11T11:00:53+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,,,,,
f210d637d4e1bb82d574ae0b,2026-09-11T11:21:56+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,,,,,
67f32e63bb66249fa1c7fee3,2026-09-11T11:38:56+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,,,,,
```

## BUY / WAIT / AVOID transition matrix

```csv
partition,baseline_decision,enhanced_decision,predictions
calibration,BUY,BUY,92
calibration,BUY,WAIT,7
calibration,BUY,AVOID,0
calibration,WAIT,BUY,0
calibration,WAIT,WAIT,201
calibration,WAIT,AVOID,0
calibration,AVOID,BUY,0
calibration,AVOID,WAIT,0
calibration,AVOID,AVOID,32
holdout_locked,BUY,BUY,0
holdout_locked,BUY,WAIT,0
holdout_locked,BUY,AVOID,0
holdout_locked,WAIT,BUY,0
holdout_locked,WAIT,WAIT,0
holdout_locked,WAIT,AVOID,0
holdout_locked,AVOID,BUY,0
holdout_locked,AVOID,WAIT,0
holdout_locked,AVOID,AVOID,0
```

## Market regimes

```csv
partition,market_regime,model,n,mean,median,win_rate,average_gain,average_loss,expectancy
calibration,corecție într-un trend ascendent,baseline_buy,0,,,,,,
calibration,corecție într-un trend ascendent,enhanced_raw_75,0,,,,,,
calibration,corecție într-un trend ascendent,enhanced_adjusted_75,0,,,,,,
calibration,creștere confirmată,baseline_buy,0,,,,,,
calibration,creștere confirmată,enhanced_raw_75,0,,,,,,
calibration,creștere confirmată,enhanced_adjusted_75,0,,,,,,
```

## Method constraints

- Signal entry is the ask captured at signal time, otherwise the captured last price.
- No later price is permitted to replace signal entry.
- Later adjusted-price factors may mechanically normalize splits/dividends.
- Costs include estimated IBKR commission, captured spread, estimated slippage and FX.
- Calibration and locked holdout are never pooled for threshold or weight selection.
- This evaluator does not optimize weights and cannot change BUY/WAIT/AVOID.
- Options N/A and Portfolio Fit N/A remain missing observations, never observed 50 scores.

## Integrity

- Errors: **0**
- Details: `[]`

## Preliminary verdict

**CONTINUE SHADOW**

Reason: `locked holdout has 0/100 matured observations`

Promotion requires positive and robust **net excess return**, acceptable
expectancy/drawdown and consistency across regimes in the locked holdout.
