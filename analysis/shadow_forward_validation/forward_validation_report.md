# Enhanced Scoring forward validation

Generated: 2026-09-16T14:41:11+00:00

## Data coverage

```csv
partition,predictions,execution_eligible_pct,options_pct,options_partial_pct,portfolio_fit_pct,matured_1d,matured_5d,matured_10d,matured_20d,matured_60d
calibration,1266,92.73301737756714,0.0,8.214849921011059,61.05845181674565,1014,48,0,0,0
holdout_locked,0,,,,,0,0,0,0,0
```

## Gross, net and benchmark alpha

```csv
partition,horizon,metric,n,mean,median,win_rate,average_gain,average_loss,expectancy
calibration,1,gross_return_pct,938,-0.6837864318239504,-0.6315833643863122,39.97867803837953,1.1726566695950107,-1.9203160286838268,-0.6837864318239504
calibration,1,net_return_pct,184,-2.7806311483097317,-1.4526936721807164,21.73913043478261,1.8646376665908952,-4.070983596893239,-2.7806311483097317
calibration,1,spy_return_pct,938,-0.197316701024989,-0.4461622179203206,29.637526652452024,0.49928122764637184,-0.4907321921926227,-0.197316701024989
calibration,1,qqq_return_pct,938,-0.4637726978676874,-0.7973383343151008,29.31769722814499,0.44051001273756313,-0.8388522535485984,-0.4637726978676874
calibration,1,sector_return_pct,538,-0.15147198914333468,-0.38428160821506463,35.87360594795539,1.2612275835884301,-0.9417647935990757,-0.15147198914333468
calibration,1,cash_return_pct,938,0.015142511988581686,0.015232836506595682,100.0,0.015142511988581686,,0.015142511988581686
calibration,1,gross_alpha_spy_pct,938,-0.4864697307989615,-0.5655011873907823,41.89765458422175,1.3854784062573136,-1.8363332498138534,-0.4864697307989615
calibration,1,net_alpha_spy_pct,184,-2.742830110624714,-1.5398967337385336,23.91304347826087,1.8774973730235038,-4.194933034057011,-2.742830110624714
calibration,1,net_alpha_qqq_pct,184,-2.4758022594172573,-1.2699445215728549,30.978260869565215,1.7142219808382833,-4.356364320004389,-2.4758022594172573
calibration,1,net_alpha_sector_pct,178,-2.6793565700804822,-1.0090052280673598,26.96629213483146,1.2630665664557716,-4.135020497416946,-2.6793565700804822
calibration,1,net_alpha_cash_pct,184,-2.795765742468319,-1.4677966065735797,20.652173913043477,1.9469529498839184,-4.030171977464107,-2.795765742468319
calibration,5,gross_return_pct,48,-1.2680230284932974,-1.140389080168125,45.83333333333333,2.0687358637131448,-4.091434398821826,-1.2680230284932974
calibration,5,net_return_pct,3,-12.391043417993764,-12.391043417993764,0.0,,-12.391043417993764,-12.391043417993764
calibration,5,spy_return_pct,48,-0.4792564946895117,-0.4830649984233548,0.0,,-0.4792564946895117,-0.4792564946895117
calibration,5,qqq_return_pct,48,-1.0896370948822416,-1.1161388014531315,0.0,,-1.0896370948822416,-1.0896370948822416
calibration,5,sector_return_pct,48,-0.13290513155833877,-1.0264185282690685,37.5,1.7879789811717117,-1.2854355991963688,-0.13290513155833877
calibration,5,cash_return_pct,48,0.07403333442979425,0.07402695934297654,100.0,0.07403333442979425,,0.07403333442979425
calibration,5,gross_alpha_spy_pct,48,-0.7887665338037855,-0.6312495488260961,45.83333333333333,2.542758129435636,-3.6077489411602195,-0.7887665338037855
calibration,5,net_alpha_spy_pct,3,-11.87745355006975,-11.880925731248338,0.0,,-11.87745355006975,-11.87745355006975
calibration,5,net_alpha_qqq_pct,3,-11.224418039996621,-11.228077991196862,0.0,,-11.224418039996621,-11.224418039996621
calibration,5,net_alpha_sector_pct,3,-11.203126616523052,-11.187972671465985,0.0,,-11.203126616523052,-11.203126616523052
calibration,5,net_alpha_cash_pct,3,-12.465019365503295,-12.465012989362812,0.0,,-12.465019365503295,-12.465019365503295
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
calibration,1,baseline_buy,322,-0.7136569521422039,31.366459627329192,41,-1.6512200019896786,29.268292682926827,41,-1.724297953388534,48.78048780487805,41,-1.470594216965554,48.78048780487805,41,-1.7102468856448207,48.78048780487805,41,-1.666330482083298,29.268292682926827,322,-1.8312311703649429,10.248447204968944,322,0.16090496573907015,52.17391304347826,322,0.0,0.0
calibration,1,enhanced_shadow_buy,314,-0.6232991396698238,32.1656050955414,33,-0.23547690111075387,36.36363636363637,33,-0.21834311679324186,60.60606060606061,33,0.04991170417915346,60.60606060606061,33,-0.4018039912114806,60.60606060606061,33,-0.2506073904974392,36.36363636363637,314,-1.754859284162706,10.509554140127388,314,0.22069213348369432,53.18471337579618,314,0.0,0.0
calibration,1,enhanced_raw_75,91,-0.6368898683346038,35.16483516483517,56,-0.4485695400460165,32.142857142857146,56,-0.5159405028427005,42.857142857142854,56,-0.26896307589285345,42.857142857142854,56,-0.4786001849425455,39.285714285714285,56,-0.4636817531612893,32.142857142857146,91,-1.6834293224799377,17.582417582417584,91,1.1949152087785622,71.42857142857143,91,0.0,0.0
calibration,1,enhanced_adjusted_75,274,0.18039392629582535,56.56934306569343,89,-0.5754058349435448,25.842696629213485,89,-0.6455444900828778,30.337078651685395,89,-0.4092510770358245,40.44943820224719,89,-0.4072795421572816,37.07865168539326,89,-0.5905250359616661,25.842696629213485,274,-1.1458453403236384,21.16788321167883,274,1.6141171139983659,86.86131386861314,274,0.0,0.0
calibration,5,baseline_buy,2,2.0308101878446783,100.0,0,,,0,,,0,,,0,,,0,,,2,-0.4001625064088077,0.0,2,3.3813488774416145,100.0,2,-0.8843572872839212,0.0
calibration,5,enhanced_shadow_buy,2,2.0308101878446783,100.0,0,,,0,,,0,,,0,,,0,,,2,-0.4001625064088077,0.0,2,3.3813488774416145,100.0,2,-0.8843572872839212,0.0
calibration,5,enhanced_raw_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
calibration,5,enhanced_adjusted_75,22,2.0687358637131448,100.0,0,,,0,,,0,,,0,,,0,,,22,-2.192766019335504,0.0,22,5.032814670754896,100.0,22,-3.7336990030863375,0.0
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
calibration,1,baseline,50-59,6,-1.593353596576604,-1.5933535965766041,0.0,,-1.593353596576604,-1.593353596576604
calibration,1,baseline,60-69,0,,,,,,
calibration,1,baseline,70-74,0,,,,,,
calibration,1,baseline,75-79,137,-3.097988340777795,-1.603267506542963,17.51824817518248,2.205804687719307,-4.22445765656479,-3.097988340777795
calibration,1,baseline,80-84,0,,,,,,
calibration,1,baseline,85-89,0,,,,,,
calibration,1,baseline,90+,41,-1.724297953388534,-0.7848963037899852,48.78048780487805,1.4835285953885387,-4.7793708569857465,-1.724297953388534
calibration,1,raw,0-49,6,-1.593353596576604,-1.5933535965766041,0.0,,-1.593353596576604,-1.593353596576604
calibration,1,raw,50-59,1,-13.59503346612777,-13.59503346612777,0.0,,-13.59503346612777,-13.59503346612777
calibration,1,raw,60-69,77,-5.483942120915159,-4.84037175725172,16.883116883116884,2.108927245211834,-7.026243710909705,-5.483942120915159
calibration,1,raw,70-74,44,-0.6902130418113992,-0.9040476812665201,15.909090909090908,2.2977110673472203,-1.2554959813819486,-0.6902130418113992
calibration,1,raw,75-79,56,-0.5159405028427005,-1.0040555130259843,42.857142857142854,1.6295771980770735,-2.125078778532531,-0.5159405028427005
calibration,1,raw,80-84,0,,,,,,
calibration,1,raw,85-89,0,,,,,,
calibration,1,raw,90+,0,,,,,,
calibration,1,adjusted,0-49,6,-1.593353596576604,-1.5933535965766041,0.0,,-1.593353596576604,-1.593353596576604
calibration,1,adjusted,50-59,0,,,,,,
calibration,1,adjusted,60-69,13,-12.615162822141773,-4.84037175725172,0.0,,-12.615162822141773,-12.615162822141773
calibration,1,adjusted,70-74,76,-3.6009216114509033,-2.042937570607277,22.36842105263158,2.269349002278532,-5.292355517101758,-3.6009216114509033
calibration,1,adjusted,75-79,63,-1.150812762276158,-1.2152307880484987,11.11111111111111,2.0514827809326186,-1.5510997051772546,-1.150812762276158
calibration,1,adjusted,80-84,26,0.5787594002316084,0.22251760767485734,76.92307692307693,1.4835285953885387,-2.4371379169581595,0.5787594002316084
calibration,1,adjusted,85-89,0,,,,,,
calibration,1,adjusted,90+,0,,,,,,
calibration,5,baseline,0-49,0,,,,,,
calibration,5,baseline,50-59,0,,,,,,
calibration,5,baseline,60-69,0,,,,,,
calibration,5,baseline,70-74,0,,,,,,
calibration,5,baseline,75-79,3,-11.87745355006975,-11.880925731248338,0.0,,-11.87745355006975,-11.87745355006975
calibration,5,baseline,80-84,0,,,,,,
calibration,5,baseline,85-89,0,,,,,,
calibration,5,baseline,90+,0,,,,,,
calibration,5,raw,0-49,0,,,,,,
calibration,5,raw,50-59,0,,,,,,
calibration,5,raw,60-69,3,-11.87745355006975,-11.880925731248338,0.0,,-11.87745355006975,-11.87745355006975
calibration,5,raw,70-74,0,,,,,,
calibration,5,raw,75-79,0,,,,,,
calibration,5,raw,80-84,0,,,,,,
calibration,5,raw,85-89,0,,,,,,
calibration,5,raw,90+,0,,,,,,
calibration,5,adjusted,0-49,0,,,,,,
calibration,5,adjusted,50-59,0,,,,,,
calibration,5,adjusted,60-69,0,,,,,,
calibration,5,adjusted,70-74,3,-11.87745355006975,-11.880925731248338,0.0,,-11.87745355006975,-11.87745355006975
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
calibration,OPTIONS_DATA_PARTIAL,contracts_only,7,89.28571428571429,73.46857142857142,76.0757142857143,100.0,4,2.7445395831022203,0,,0,,0,,0,
calibration,OPTIONS_DATA_PARTIAL,partial,33,81.81818181818181,72.89545454545454,75.44060606060606,100.0,15,-1.130740588462477,0,,0,,0,,0,
calibration,OPTIONS_DATA_PARTIAL,quote_only,64,86.71875,72.92390625,75.47015625,100.0,37,-2.4909179412418685,0,,0,,0,,0,
calibration,OPTIONS_NOT_ELIGIBLE,unavailable,764,78.33769633507853,63.295772251308904,64.7730497382199,35.47120418848168,11,-1.5741251456222847,0,,0,,0,,0,
calibration,OPTIONS_UNAVAILABLE,unavailable,398,81.03015075376885,69.78532663316582,71.98311557788945,100.0,122,-3.253882823401724,3,-11.87745355006975,0,,0,,0,
```

Availability is reported separately from the formula value. Missing options
data is never classified as an observed score of 50.

## Portfolio Fit cohorts

```csv
partition,cohort,predictions,raw_score_mean,adjusted_score_mean,net_alpha_spy_1d_n,net_alpha_spy_1d_mean,net_alpha_spy_1d_median,net_alpha_spy_1d_win_rate,net_alpha_spy_1d_average_gain,net_alpha_spy_1d_average_loss,net_alpha_spy_1d_expectancy,net_alpha_spy_5d_n,net_alpha_spy_5d_mean,net_alpha_spy_5d_median,net_alpha_spy_5d_win_rate,net_alpha_spy_5d_average_gain,net_alpha_spy_5d_average_loss,net_alpha_spy_5d_expectancy,net_alpha_spy_10d_n,net_alpha_spy_10d_mean,net_alpha_spy_10d_median,net_alpha_spy_10d_win_rate,net_alpha_spy_10d_average_gain,net_alpha_spy_10d_average_loss,net_alpha_spy_10d_expectancy,net_alpha_spy_20d_n,net_alpha_spy_20d_mean,net_alpha_spy_20d_median,net_alpha_spy_20d_win_rate,net_alpha_spy_20d_average_gain,net_alpha_spy_20d_average_loss,net_alpha_spy_20d_expectancy,net_alpha_spy_60d_n,net_alpha_spy_60d_mean,net_alpha_spy_60d_median,net_alpha_spy_60d_win_rate,net_alpha_spy_60d_average_gain,net_alpha_spy_60d_average_loss,net_alpha_spy_60d_expectancy
calibration,missing,493,66.00997971602435,66.00997971602435,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,other_observed,248,59.48673387096774,59.492661290322566,67,-0.6896723098662144,-1.2152307880484987,35.82089552238806,1.6295771980770735,-1.98413715150898,-0.6896723098662144,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,raw_medium_fit_good,525,69.37878095238095,73.92674285714286,122,-3.8215405788221037,-1.8786637022011905,16.39344262295082,2.175001582959219,-4.997333159563539,-3.8215405788221037,3,-11.87745355006975,-11.880925731248338,0.0,,-11.87745355006975,-11.87745355006975,0,,,,,,,0,,,,,,,0,,,,,,
```

## Component contribution and redundancy

```csv
partition,horizon,component,n,pearson_forward_alpha,spearman_forward_alpha,max_abs_component_correlation,incremental_r2
calibration,1,technical_score,189,0.049169941930678564,0.10282147597389771,0.42253313118898306,
calibration,1,momentum_score,189,-0.035871068639969035,-0.03199387304573175,0.4813697501774116,
calibration,1,research_score,189,-0.07133489079770364,0.0792692499417956,0.387946475004763,
calibration,1,volatility_score,189,-0.11497188587323005,-0.09818392689162035,0.2736526827618531,
calibration,1,liquidity_score,189,0.6073582673025939,0.6529422818970384,0.105668558677765,
calibration,1,options_score,0,,,,
calibration,1,relative_opportunity_score,189,,,,
calibration,1,risk_reward_score,189,-0.09321990429499856,-0.20743664546686214,0.4813697501774116,
calibration,5,technical_score,3,,,0.42253313118898306,
calibration,5,momentum_score,3,,,0.4813697501774116,
calibration,5,research_score,3,,,0.387946475004763,
calibration,5,volatility_score,3,,,0.2736526827618531,
calibration,5,liquidity_score,3,,,0.105668558677765,
calibration,5,options_score,0,,,,
calibration,5,relative_opportunity_score,3,,,,
calibration,5,risk_reward_score,3,,,0.4813697501774116,
calibration,10,technical_score,0,,,0.42253313118898306,
calibration,10,momentum_score,0,,,0.4813697501774116,
calibration,10,research_score,0,,,0.387946475004763,
calibration,10,volatility_score,0,,,0.2736526827618531,
calibration,10,liquidity_score,0,,,0.105668558677765,
calibration,10,options_score,0,,,,
calibration,10,relative_opportunity_score,0,,,,
calibration,10,risk_reward_score,0,,,0.4813697501774116,
calibration,20,technical_score,0,,,0.42253313118898306,
calibration,20,momentum_score,0,,,0.4813697501774116,
calibration,20,research_score,0,,,0.387946475004763,
calibration,20,volatility_score,0,,,0.2736526827618531,
calibration,20,liquidity_score,0,,,0.105668558677765,
calibration,20,options_score,0,,,,
calibration,20,relative_opportunity_score,0,,,,
calibration,20,risk_reward_score,0,,,0.4813697501774116,
calibration,60,technical_score,0,,,0.42253313118898306,
calibration,60,momentum_score,0,,,0.4813697501774116,
calibration,60,research_score,0,,,0.387946475004763,
calibration,60,volatility_score,0,,,0.2736526827618531,
calibration,60,liquidity_score,0,,,0.105668558677765,
calibration,60,options_score,0,,,,
calibration,60,relative_opportunity_score,0,,,,
calibration,60,risk_reward_score,0,,,0.4813697501774116,
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
5522e100effd8a5697d20573,2026-09-10T21:10:03+00:00,calibration,TRGP,BUY,WAIT,73.1,100.0,77.13,-3.6307914717671,,,,
53c26794356af012cc307291,2026-09-11T06:44:58+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-19.383814384315958,,,,
8ca424c3afa2faff80cd5fa8,2026-09-11T08:54:52+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186612984672122,,,,
3457725c926d4c9bca6c86ef,2026-09-11T09:29:41+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186612984672122,,,,
62964736889913e1a2f9310e,2026-09-11T11:00:53+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186612984672122,,,,
f210d637d4e1bb82d574ae0b,2026-09-11T11:21:56+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186612984672122,,,,
67f32e63bb66249fa1c7fee3,2026-09-11T11:38:56+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186612984672122,,,,
fb9cc1abbfcca2453eec217b,2026-09-15T20:21:08+00:00,calibration,ELV,BUY,WAIT,67.59,100.0,72.45,-4.543222455309255,,,,
fabca3d3e4bba17e1172975c,2026-09-16T05:40:32+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
fabca3d3e4bba17e1172975c,2026-09-16T05:40:32+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,,,,,
e1338d825a461549ab9e718a,2026-09-16T05:50:47+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
e1338d825a461549ab9e718a,2026-09-16T05:50:47+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,,,,,
e991d1db51ca3517cd30ca69,2026-09-16T05:54:18+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
e991d1db51ca3517cd30ca69,2026-09-16T05:54:18+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,,,,,
92e9fb98a9868fa5713aaf9d,2026-09-16T06:00:15+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
92e9fb98a9868fa5713aaf9d,2026-09-16T06:00:15+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,,,,,
3f6b3bd68f68e3e0a4cb2309,2026-09-16T06:03:42+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
3f6b3bd68f68e3e0a4cb2309,2026-09-16T06:03:42+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,,,,,
```

## BUY / WAIT / AVOID transition matrix

```csv
partition,baseline_decision,enhanced_decision,predictions
calibration,BUY,BUY,360
calibration,BUY,WAIT,18
calibration,BUY,AVOID,0
calibration,WAIT,BUY,0
calibration,WAIT,WAIT,767
calibration,WAIT,AVOID,0
calibration,AVOID,BUY,0
calibration,AVOID,WAIT,0
calibration,AVOID,AVOID,121
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
calibration,piață mixtă,baseline_buy,0,,,,,,
calibration,piață mixtă,enhanced_raw_75,0,,,,,,
calibration,piață mixtă,enhanced_adjusted_75,0,,,,,,
calibration,trend descendent,baseline_buy,0,,,,,,
calibration,trend descendent,enhanced_raw_75,0,,,,,,
calibration,trend descendent,enhanced_adjusted_75,0,,,,,,
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
