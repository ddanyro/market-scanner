# Enhanced Scoring forward validation

Generated: 2026-09-18T16:15:23+00:00

## Data coverage

```csv
partition,predictions,execution_eligible_pct,options_pct,options_partial_pct,portfolio_fit_pct,matured_1d,matured_5d,matured_10d,matured_20d,matured_60d
calibration,1620,92.77777777777779,0.0,7.34567901234568,68.27160493827161,1493,498,0,0,0
holdout_locked,0,,,,,0,0,0,0,0
```

## Gross, net and benchmark alpha

```csv
partition,horizon,metric,n,mean,median,win_rate,average_gain,average_loss,expectancy
calibration,1,gross_return_pct,1389,-0.5240443868466655,-0.5223981212049256,42.98056155507559,1.6793474880010577,-2.184934474326578,-0.5240443868466655
calibration,1,net_return_pct,235,-4.002533592434476,-2.324825721138958,18.72340425531915,1.8079730430982257,-5.34107962365667,-4.002533592434476
calibration,1,spy_return_pct,1389,-0.11457520656125739,-0.4461622179203206,38.58891288696904,0.575502917225284,-0.5481999127155203,-0.11457520656125739
calibration,1,qqq_return_pct,1389,-0.06865592356946026,-0.6288984941619669,42.1886249100072,0.916500769980016,-0.7875872092730629,-0.06865592356946026
calibration,1,sector_return_pct,754,-0.11197035442927734,-0.38428160821506463,41.37931034482759,1.1452988120494065,-0.9994544719436425,-0.11197035442927734
calibration,1,cash_return_pct,1389,0.015222372313946348,0.015232836506595682,100.0,0.015222372313946348,,0.015222372313946348
calibration,1,gross_alpha_spy_pct,1389,-0.4094691802854082,-0.5246671081262089,44.56443484521238,1.748936041877427,-2.144602729011116,-0.4094691802854082
calibration,1,net_alpha_spy_pct,235,-4.094913861525434,-2.0122438796120456,20.851063829787233,1.728064628838623,-5.628924324040697,-4.094913861525434
calibration,1,net_alpha_qqq_pct,235,-4.113525936909327,-1.691761454212497,24.25531914893617,1.7142219808382833,-5.979714876862215,-4.113525936909327
calibration,1,net_alpha_sector_pct,229,-4.029753675630308,-1.9551209754170484,20.52401746724891,1.2868216489963826,-5.40271543528665,-4.029753675630308
calibration,1,net_alpha_cash_pct,235,-4.017731055582881,-2.3400585576455537,17.872340425531917,1.8782826213280834,-5.300801389418428,-4.017731055582881
calibration,5,gross_return_pct,494,-1.579443719389398,-1.7620348579788836,26.31578947368421,2.4387475335156545,-3.014512023998345,-1.579443719389398
calibration,5,net_return_pct,170,-4.144792119859629,-3.022524077059294,21.764705882352942,2.462501705687599,-5.982911454786302,-4.144792119859629
calibration,5,spy_return_pct,494,-0.5180650330723293,-0.6908331113004595,26.923076923076923,0.3253582514107572,-0.8287999273555717,-0.5180650330723293
calibration,5,qqq_return_pct,494,0.024088209144877186,0.1965320242145019,79.95951417004049,0.4348032260830095,-1.6146232220729229,0.024088209144877186
calibration,5,sector_return_pct,416,-0.8195386954655078,-0.8213012761428051,30.048076923076923,0.6772280156958228,-1.462479722596664,-0.8195386954655078
calibration,5,cash_return_pct,494,0.07540396702268409,0.07618738999861652,100.0,0.07540396702268409,,0.07540396702268409
calibration,5,gross_alpha_spy_pct,494,-1.0613786863170684,-1.3237492086837666,31.17408906882591,2.5602994706256244,-2.701785851520524,-1.0613786863170684
calibration,5,net_alpha_spy_pct,170,-3.859176818917506,-2.7505305239742914,22.35294117647059,2.718931089162586,-5.752874550031473,-3.859176818917506
calibration,5,net_alpha_qqq_pct,170,-4.678185884069667,-3.611995184171974,20.588235294117645,2.0873066725076383,-6.432202472811931,-4.678185884069667
calibration,5,net_alpha_sector_pct,170,-3.3793610841020447,-1.9958930156292514,21.764705882352942,2.612851802761163,-5.0463676766880505,-3.3793610841020447
calibration,5,net_alpha_cash_pct,170,-4.22040527013585,-3.097411660981628,21.764705882352942,2.3867710043103787,-6.058491902876531,-4.22040527013585
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
calibration,1,baseline_buy,408,-0.6877478196687719,35.049019607843135,46,-2.8045238076260133,26.08695652173913,46,-2.928298786196021,43.47826086956522,46,-2.8193474336692788,43.47826086956522,46,-2.8207916143407714,43.47826086956522,46,-2.819667095114226,26.08695652173913,408,-1.9587897558184857,15.196078431372548,408,0.5196826172941071,59.068627450980394,408,0.0,0.0
calibration,1,enhanced_shadow_buy,390,-0.5029116309758347,36.666666666666664,33,-0.23547690111075387,36.36363636363637,33,-0.21834311679324186,60.60606060606061,33,0.04991170417915346,60.60606060606061,33,-0.4018039912114806,60.60606060606061,33,-0.2506073904974392,36.36363636363637,390,-1.7928666556521229,15.897435897435896,390,0.6535239009198975,61.53846153846154,390,0.0,0.0
calibration,1,enhanced_raw_75,91,-0.854460216158775,36.26373626373626,56,-0.4485695400460165,32.142857142857146,56,-0.5159405028427005,42.857142857142854,56,-0.26896307589285345,42.857142857142854,56,-0.4786001849425455,39.285714285714285,56,-0.4636817531612893,32.142857142857146,91,-2.1534603093876794,17.582417582417584,91,1.285134183909824,71.42857142857143,91,0.0,0.0
calibration,1,enhanced_adjusted_75,307,0.10204951503973521,57.32899022801303,99,-0.6542877578167923,27.27272727272727,99,-0.7643411120013478,32.323232323232325,99,-0.6612471544618674,36.36363636363637,99,-0.623043265121955,32.323232323232325,99,-0.6694365656132722,27.27272727272727,307,-1.3121945902202947,19.54397394136808,307,1.6189504334593703,85.99348534201955,307,0.0,0.0
calibration,5,baseline_buy,112,-0.1675356090000122,60.71428571428571,40,-1.0480126671502226,55.00000000000001,40,-0.8745953333574166,55.00000000000001,40,-1.7000451376970243,55.00000000000001,40,-0.40605806782601855,55.00000000000001,40,-1.123550154110698,55.00000000000001,112,-2.8377392364307665,26.785714285714285,112,2.3985234272364764,78.57142857142857,112,-1.9190098792601513,0.0
calibration,5,enhanced_shadow_buy,105,-0.00863004689237701,64.76190476190476,33,-0.019865831759530047,66.66666666666666,33,0.23772075474662083,66.66666666666666,33,-0.5801644492907703,66.66666666666666,33,0.6462533153024962,66.66666666666666,33,-0.09554117694021705,66.66666666666666,105,-2.5736601730524615,28.57142857142857,105,2.674537549524123,82.85714285714286,105,-1.9796275764157858,0.0
calibration,5,enhanced_raw_75,62,0.1299569434175559,56.451612903225815,56,-0.2932715896956912,55.35714285714286,56,-0.12136742222963896,51.78571428571429,56,-0.9201285867359973,51.78571428571429,56,0.06284502960797754,51.78571428571429,56,-0.36885549830174796,55.35714285714286,62,-2.9149710843639918,19.35483870967742,62,3.629931667171276,91.93548387096774,62,-2.858942854838365,0.0
calibration,5,enhanced_adjusted_75,222,-0.0991872324456919,48.1981981981982,86,-1.1844615144978463,38.372093023255815,86,-1.006636955891304,36.04651162790697,86,-1.819058754396926,36.04651162790697,86,-0.8149050757879113,38.372093023255815,86,-1.2600292295066073,38.372093023255815,222,-2.6295580299908705,15.765765765765765,222,3.599344401466049,97.74774774774775,222,-3.4450020592128636,0.0
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
calibration,1,baseline,50-59,6,-2.2173622190915583,-2.2173622190915583,0.0,,-2.2173622190915583,-2.2173622190915583
calibration,1,baseline,60-69,0,,,,,,
calibration,1,baseline,70-74,0,,,,,,
calibration,1,baseline,75-79,183,-4.449720437043229,-2.0122438796120456,15.846994535519126,1.8967101691490262,-5.644827499248263,-4.449720437043229
calibration,1,baseline,80-84,0,,,,,,
calibration,1,baseline,85-89,0,,,,,,
calibration,1,baseline,90+,46,-2.928298786196021,-1.471143355246887,43.47826086956522,1.4835285953885387,-6.322012156645682,-2.928298786196021
calibration,1,raw,0-49,6,-2.2173622190915583,-2.2173622190915583,0.0,,-2.2173622190915583,-2.2173622190915583
calibration,1,raw,50-59,5,-14.88248887450148,-13.59503346612777,0.0,,-14.88248887450148,-14.88248887450148
calibration,1,raw,60-69,109,-6.7337915116177545,-5.066483536561607,11.926605504587156,2.108927245211834,-7.931243009938428,-6.7337915116177545
calibration,1,raw,70-74,59,-1.8934270651846428,-1.2771626823191136,20.33898305084746,1.5124383226240774,-2.7630097173911246,-1.8934270651846428
calibration,1,raw,75-79,56,-0.5159405028427005,-1.0040555130259843,42.857142857142854,1.6295771980770735,-2.125078778532531,-0.5159405028427005
calibration,1,raw,80-84,0,,,,,,
calibration,1,raw,85-89,0,,,,,,
calibration,1,raw,90+,0,,,,,,
calibration,1,adjusted,0-49,6,-2.2173622190915583,-2.2173622190915583,0.0,,-2.2173622190915583,-2.2173622190915583
calibration,1,adjusted,50-59,0,,,,,,
calibration,1,adjusted,60-69,31,-12.352491549208583,-5.27941774923061,0.0,,-12.352491549208583,-12.352491549208583
calibration,1,adjusted,70-74,99,-4.9535714750538204,-3.902111832449859,17.17171717171717,2.269349002278532,-6.451006208159309,-4.9535714750538204
calibration,1,adjusted,75-79,73,-1.2427056780021266,-1.2152307880484987,16.43835616438356,1.368805155548893,-1.7564455141105242,-1.2427056780021266
calibration,1,adjusted,80-84,26,0.5787594002316084,0.22251760767485734,76.92307692307693,1.4835285953885387,-2.4371379169581595,0.5787594002316084
calibration,1,adjusted,85-89,0,,,,,,
calibration,1,adjusted,90+,0,,,,,,
calibration,5,baseline,0-49,0,,,,,,
calibration,5,baseline,50-59,0,,,,,,
calibration,5,baseline,60-69,0,,,,,,
calibration,5,baseline,70-74,0,,,,,,
calibration,5,baseline,75-79,130,-4.777509583705226,-2.7619758743402767,12.307692307692308,2.943615203119151,-5.861176220452507,-4.777509583705226
calibration,5,baseline,80-84,0,,,,,,
calibration,5,baseline,85-89,0,,,,,,
calibration,5,baseline,90+,40,-0.8745953333574166,0.9233831693643251,55.00000000000001,2.5555244608305383,-5.066963970698249,-0.8745953333574166
calibration,5,raw,0-49,0,,,,,,
calibration,5,raw,50-59,1,-16.16214695437106,-16.16214695437106,0.0,,-16.16214695437106,-16.16214695437106
calibration,5,raw,60-69,72,-7.244871192844962,-4.216518636990093,8.333333333333332,3.267160187304352,-8.200510409222172,-7.244871192844962
calibration,5,raw,70-74,41,-2.7187953837050745,-2.2072292625368934,7.317073170731707,1.9580785483707672,-3.088022273079483,-2.7187953837050745
calibration,5,raw,75-79,56,-0.12136742222963896,0.9233831693643251,51.78571428571429,2.684213262732409,-3.1347688986703557,-0.12136742222963896
calibration,5,raw,80-84,0,,,,,,
calibration,5,raw,85-89,0,,,,,,
calibration,5,raw,90+,0,,,,,,
calibration,5,adjusted,0-49,0,,,,,,
calibration,5,adjusted,50-59,0,,,,,,
calibration,5,adjusted,60-69,13,-12.837961076509155,-9.508033852512504,7.6923076923076925,2.224361577029266,-14.09315463097069,-12.837961076509155
calibration,5,adjusted,70-74,71,-5.670363197390213,-3.301175278337966,8.450704225352112,2.915362786528361,-6.462891749751925,-5.670363197390213
calibration,5,adjusted,75-79,60,-1.7200637364836282,-2.126361180471597,18.333333333333332,3.3533682234037254,-2.8589974417644632,-1.7200637364836282
calibration,5,adjusted,80-84,26,0.639732537783291,0.9233831693643251,76.92307692307693,2.3357896317268922,-5.013791108695379,0.639732537783291
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
calibration,OPTIONS_DATA_PARTIAL,contracts_only,7,89.28571428571429,73.46857142857142,76.0757142857143,100.0,4,2.7445395831022203,4,3.748196094089459,0,,0,,0,
calibration,OPTIONS_DATA_PARTIAL,partial,42,82.14285714285714,72.25642857142857,74.73047619047618,100.0,15,-1.1459511323102687,12,-1.7002013199664823,0,,0,,0,
calibration,OPTIONS_DATA_PARTIAL,quote_only,70,85.71428571428571,72.47857142857141,74.97542857142858,100.0,44,-3.725409433857568,37,-1.9500008950345769,0,,0,,0,
calibration,OPTIONS_NOT_ELIGIBLE,unavailable,942,76.2208067940552,62.51188959660297,63.90243099787686,46.28450106157113,11,-2.4817740510985824,0,,0,,0,,0,
calibration,OPTIONS_UNAVAILABLE,unavailable,559,79.87477638640429,69.31057245080501,71.45561717352416,98.56887298747765,166,-4.691996749409335,117,-4.944447817405615,0,,0,,0,
```

Availability is reported separately from the formula value. Missing options
data is never classified as an observed score of 50.

## Portfolio Fit cohorts

```csv
partition,cohort,predictions,raw_score_mean,adjusted_score_mean,net_alpha_spy_1d_n,net_alpha_spy_1d_mean,net_alpha_spy_1d_median,net_alpha_spy_1d_win_rate,net_alpha_spy_1d_average_gain,net_alpha_spy_1d_average_loss,net_alpha_spy_1d_expectancy,net_alpha_spy_5d_n,net_alpha_spy_5d_mean,net_alpha_spy_5d_median,net_alpha_spy_5d_win_rate,net_alpha_spy_5d_average_gain,net_alpha_spy_5d_average_loss,net_alpha_spy_5d_expectancy,net_alpha_spy_10d_n,net_alpha_spy_10d_mean,net_alpha_spy_10d_median,net_alpha_spy_10d_win_rate,net_alpha_spy_10d_average_gain,net_alpha_spy_10d_average_loss,net_alpha_spy_10d_expectancy,net_alpha_spy_20d_n,net_alpha_spy_20d_mean,net_alpha_spy_20d_median,net_alpha_spy_20d_win_rate,net_alpha_spy_20d_average_gain,net_alpha_spy_20d_average_loss,net_alpha_spy_20d_expectancy,net_alpha_spy_60d_n,net_alpha_spy_60d_mean,net_alpha_spy_60d_median,net_alpha_spy_60d_win_rate,net_alpha_spy_60d_average_gain,net_alpha_spy_60d_average_loss,net_alpha_spy_60d_expectancy
calibration,missing,514,65.9663618677043,65.9663618677043,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,other_observed,413,59.2657627118644,57.951598062953984,67,-0.8386892943473975,-1.2152307880484987,35.82089552238806,1.6295771980770735,-2.2163264063982657,-0.8386892943473975,56,-0.12136742222963896,0.9233831693643251,51.78571428571429,2.684213262732409,-3.1347688986703557,-0.12136742222963896,0,,,,,,,0,,,,,,,0,,,,,,
calibration,raw_medium_fit_good,693,69.07632034632034,73.68063492063493,173,-5.318542866963795,-3.6809034806163945,14.450867052023122,1.8226125623697107,-6.52481912191878,-5.318542866963795,114,-5.695293715536107,-3.04046553612367,7.894736842105263,2.830799640993157,-6.426101717524332,-5.695293715536107,0,,,,,,,0,,,,,,,0,,,,,,
```

## Component contribution and redundancy

```csv
partition,horizon,component,n,pearson_forward_alpha,spearman_forward_alpha,max_abs_component_correlation,incremental_r2
calibration,1,technical_score,240,0.04611577650130917,0.08767463355749686,0.3733062816190155,
calibration,1,momentum_score,240,-0.08830902420481632,-0.13266752502289633,0.48876642452643576,
calibration,1,research_score,240,0.0008681099980130692,0.12353788813602481,0.35723484832195274,
calibration,1,volatility_score,240,-0.06236587370265753,-0.029046982853583366,0.27663097344962834,
calibration,1,liquidity_score,240,0.6630515735294755,0.7505572871486059,0.12395644679521174,
calibration,1,options_score,0,,,,
calibration,1,relative_opportunity_score,240,,,,
calibration,1,risk_reward_score,240,-0.11877400322423516,-0.1957123307551943,0.48876642452643576,
calibration,5,technical_score,170,0.23913205197050943,0.22730164760792343,0.3733062816190155,
calibration,5,momentum_score,170,-0.1819159811608314,-0.21349457363737276,0.48876642452643576,
calibration,5,research_score,170,0.08561940499073205,0.25658550525878326,0.35723484832195274,
calibration,5,volatility_score,170,-0.2903682534860898,-0.2676075517588771,0.27663097344962834,
calibration,5,liquidity_score,170,0.6388120083757756,0.7422928250039098,0.12395644679521174,
calibration,5,options_score,0,,,,
calibration,5,relative_opportunity_score,170,,,,
calibration,5,risk_reward_score,170,-0.04284078230984905,-0.11090150799611462,0.48876642452643576,
calibration,10,technical_score,0,,,0.3733062816190155,
calibration,10,momentum_score,0,,,0.48876642452643576,
calibration,10,research_score,0,,,0.35723484832195274,
calibration,10,volatility_score,0,,,0.27663097344962834,
calibration,10,liquidity_score,0,,,0.12395644679521174,
calibration,10,options_score,0,,,,
calibration,10,relative_opportunity_score,0,,,,
calibration,10,risk_reward_score,0,,,0.48876642452643576,
calibration,20,technical_score,0,,,0.3733062816190155,
calibration,20,momentum_score,0,,,0.48876642452643576,
calibration,20,research_score,0,,,0.35723484832195274,
calibration,20,volatility_score,0,,,0.27663097344962834,
calibration,20,liquidity_score,0,,,0.12395644679521174,
calibration,20,options_score,0,,,,
calibration,20,relative_opportunity_score,0,,,,
calibration,20,risk_reward_score,0,,,0.48876642452643576,
calibration,60,technical_score,0,,,0.3733062816190155,
calibration,60,momentum_score,0,,,0.48876642452643576,
calibration,60,research_score,0,,,0.35723484832195274,
calibration,60,volatility_score,0,,,0.27663097344962834,
calibration,60,liquidity_score,0,,,0.12395644679521174,
calibration,60,options_score,0,,,,
calibration,60,relative_opportunity_score,0,,,,
calibration,60,risk_reward_score,0,,,0.48876642452643576,
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
5522e100effd8a5697d20573,2026-09-10T21:10:03+00:00,calibration,TRGP,BUY,WAIT,73.1,100.0,77.13,-3.6307914717671,-5.172088677630468,,,
53c26794356af012cc307291,2026-09-11T06:44:58+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-19.383814384315958,-16.573916378354205,,,
8ca424c3afa2faff80cd5fa8,2026-09-11T08:54:52+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186612984672122,-4.216518636990093,,,
3457725c926d4c9bca6c86ef,2026-09-11T09:29:41+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186612984672122,-4.216518636990093,,,
62964736889913e1a2f9310e,2026-09-11T11:00:53+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186612984672122,-4.216518636990093,,,
f210d637d4e1bb82d574ae0b,2026-09-11T11:21:56+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186612984672122,-4.216518636990093,,,
67f32e63bb66249fa1c7fee3,2026-09-11T11:38:56+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186612984672122,-4.216518636990093,,,
fb9cc1abbfcca2453eec217b,2026-09-15T20:21:08+00:00,calibration,ELV,BUY,WAIT,67.59,100.0,72.45,-5.42223799596124,,,,
fabca3d3e4bba17e1172975c,2026-09-16T05:40:32+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
fabca3d3e4bba17e1172975c,2026-09-16T05:40:32+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302507087014,,,,
e1338d825a461549ab9e718a,2026-09-16T05:50:47+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
e1338d825a461549ab9e718a,2026-09-16T05:50:47+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302507087014,,,,
e991d1db51ca3517cd30ca69,2026-09-16T05:54:18+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
e991d1db51ca3517cd30ca69,2026-09-16T05:54:18+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302507087014,,,,
92e9fb98a9868fa5713aaf9d,2026-09-16T06:00:15+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
92e9fb98a9868fa5713aaf9d,2026-09-16T06:00:15+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302507087014,,,,
3f6b3bd68f68e3e0a4cb2309,2026-09-16T06:03:42+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
3f6b3bd68f68e3e0a4cb2309,2026-09-16T06:03:42+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302507087014,,,,
```

## BUY / WAIT / AVOID transition matrix

```csv
partition,baseline_decision,enhanced_decision,predictions
calibration,BUY,BUY,410
calibration,BUY,WAIT,18
calibration,BUY,AVOID,0
calibration,WAIT,BUY,0
calibration,WAIT,WAIT,1009
calibration,WAIT,AVOID,0
calibration,AVOID,BUY,0
calibration,AVOID,WAIT,0
calibration,AVOID,AVOID,183
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
