# Enhanced Scoring forward validation

Generated: 2026-09-20T22:07:09+00:00

## Data coverage

```csv
partition,predictions,execution_eligible_pct,options_pct,options_partial_pct,portfolio_fit_pct,matured_1d,matured_5d,matured_10d,matured_20d,matured_60d
calibration,2005,92.76807980049875,0.0,6.982543640897755,73.76558603491273,1491,559,0,0,0
holdout_locked,0,,,,,0,0,0,0,0
```

## Gross, net and benchmark alpha

```csv
partition,horizon,metric,n,mean,median,win_rate,average_gain,average_loss,expectancy
calibration,1,gross_return_pct,1389,-0.5243427229642977,-0.5063274238683024,43.196544276457885,1.6681201526355496,-2.1916148717094286,-0.5243427229642977
calibration,1,net_return_pct,235,-4.003656988830963,-2.324825721138958,18.72340425531915,1.8079730430982257,-5.342461812940306,-4.003656988830963
calibration,1,spy_return_pct,1389,-0.08675432947839959,-0.4461653449273739,40.31677465802736,0.601913182599487,-0.5519579564550178,-0.08675432947839959
calibration,1,qqq_return_pct,1389,-0.03509186343026528,-0.6288984941619669,43.34053275737941,0.9676009802449398,-0.8020818150090118,-0.03509186343026528
calibration,1,sector_return_pct,754,-0.09962294216560373,-0.3652088639392925,41.777188328912466,1.1723649769650617,-1.0123249798106142,-0.09962294216560373
calibration,1,cash_return_pct,1389,0.015222372313946348,0.015232836506595682,100.0,0.015222372313946348,,0.015222372313946348
calibration,1,gross_alpha_spy_pct,1389,-0.4375883934858982,-0.5492597658596776,43.84449244060475,1.7558550315543628,-2.15016152919041,-0.4375883934858982
calibration,1,net_alpha_spy_pct,235,-4.137311823620472,-2.042934443600224,20.851063829787233,1.7280668469198268,-5.682492226074636,-4.137311823620472
calibration,1,net_alpha_qqq_pct,235,-4.164550322140223,-1.691761454212497,24.25531914893617,1.7142219808382833,-6.047078531520982,-4.164550322140223
calibration,1,net_alpha_sector_pct,229,-4.041174976573309,-1.9551209754170484,20.52401746724891,1.2868216489963826,-5.417086193066581,-4.041174976573309
calibration,1,net_alpha_cash_pct,235,-4.018854451979368,-2.3400585576455537,17.872340425531917,1.8782826213280834,-5.302169255497052,-4.018854451979368
calibration,5,gross_return_pct,520,-1.419862502081604,-1.5932502773702784,30.0,2.426469026785078,-3.068290300167325,-1.419862502081604
calibration,5,net_return_pct,173,-4.0432739916631695,-2.9543835034436943,23.121387283236995,2.501694476475541,-6.011685561028196,-4.0432739916631695
calibration,5,spy_return_pct,520,-0.10787021701188577,-0.09270593630656965,27.500000000000004,0.5790186637988816,-0.3684142752504527,-0.10787021701188577
calibration,5,qqq_return_pct,520,0.5302344594610093,0.919036364296022,82.6923076923077,1.0128086814140103,-1.7753979343144377,0.5302344594610093
calibration,5,sector_return_pct,416,-0.7180021051040657,-1.2741809243906443,31.009615384615387,1.1809939449258733,-1.5715578209711811,-0.7180021051040657
calibration,5,cash_return_pct,520,0.0754163030548582,0.07618738999861652,100.0,0.0754163030548582,,0.0754163030548582
calibration,5,gross_alpha_spy_pct,520,-1.311992285069718,-1.4504627935390813,31.153846153846153,2.4667358272376583,-3.0219195314211005,-1.311992285069718
calibration,5,net_alpha_spy_pct,173,-4.256766011671429,-3.167853582291407,21.965317919075144,2.467963145062744,-6.149652737270679,-4.256766011671429
calibration,5,net_alpha_qqq_pct,173,-5.1822477497847474,-4.179595882893999,14.450867052023122,2.43851503391336,-6.469538760544563,-5.1822477497847474
calibration,5,net_alpha_sector_pct,170,-3.5103110106774853,-1.9863785942073324,16.470588235294116,3.3652666937407085,-4.866058727041636,-3.5103110106774853
calibration,5,net_alpha_cash_pct,173,-4.118897099853652,-3.0292710873660282,23.121387283236995,2.425929523451716,-6.087266009118425,-4.118897099853652
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
calibration,1,baseline_buy,408,-0.6745313388514651,35.53921568627451,46,-2.8045238076260133,26.08695652173913,46,-2.928296915459608,43.47826086956522,46,-2.8193474336692788,43.47826086956522,46,-2.8207916143407714,43.47826086956522,46,-2.819667095114226,26.08695652173913,408,-1.9597379345158026,15.196078431372548,408,0.5260623916336625,59.068627450980394,408,0.0,0.0
calibration,1,enhanced_shadow_buy,390,-0.4890851587361908,37.17948717948718,33,-0.23547690111075387,36.36363636363637,33,-0.21834094449955546,60.60606060606061,33,0.04991170417915346,60.60606060606061,33,-0.4018039912114806,60.60606060606061,33,-0.2506073904974392,36.36363636363637,390,-1.793858596443162,15.897435897435896,390,0.660198126382817,61.53846153846154,390,0.0,0.0
calibration,1,enhanced_raw_75,91,-0.854460216158775,36.26373626373626,56,-0.4485695400460165,32.142857142857146,56,-0.5159385822876784,42.857142857142854,56,-0.26896307589285345,42.857142857142854,56,-0.4786001849425455,39.285714285714285,56,-0.4636817531612893,32.142857142857146,91,-2.1534603093876794,17.582417582417584,91,1.285134183909824,71.42857142857143,91,0.0,0.0
calibration,1,enhanced_adjusted_75,307,0.1254458657456987,57.98045602605863,99,-0.6542877578167923,27.27272727272727,99,-0.764339404158258,32.323232323232325,99,-0.6612471544618674,36.36363636363637,99,-0.623043265121955,32.323232323232325,99,-0.6694365656132722,27.27272727272727,307,-1.3134547104434386,19.54397394136808,307,1.6279805042284041,85.99348534201955,307,0.0,0.0
calibration,5,baseline_buy,112,-0.25104691203734314,60.71428571428571,40,-1.291760182037305,55.00000000000001,40,-1.598375115957635,55.00000000000001,40,-2.5236893236587647,30.0,40,-0.7395626195683157,32.5,40,-1.3672976689977807,55.00000000000001,112,-2.8377392364307665,26.785714285714285,112,2.3992674305855273,78.57142857142857,112,-2.07686985129587,0.0
calibration,5,enhanced_shadow_buy,105,-0.03678792799977093,64.76190476190476,33,-0.1214783218073662,66.66666666666666,33,-0.3360714711683909,66.66666666666666,33,-1.2521701763782536,36.36363636363637,33,0.3532363499809302,39.39393939393939,33,-0.19715366698805317,66.66666666666666,105,-2.5736601730524615,28.57142857142857,105,2.6753311530964448,82.85714285714286,105,-2.148011546587219,0.0
calibration,5,enhanced_raw_75,62,0.1340952296609611,56.451612903225815,56,-0.3573198962882427,55.35714285714286,56,-0.6243330459746492,51.78571428571429,56,-1.514392879763463,33.92857142857143,56,-0.11410899106801309,35.714285714285715,56,-0.43290380489429936,55.35714285714286,62,-2.9149710843639918,19.35483870967742,62,3.631275673221175,91.93548387096774,62,-2.934688193763207,0.0
calibration,5,enhanced_adjusted_75,222,-0.10140286572942489,48.1981981981982,86,-1.2328018174958864,38.372093023255815,86,-1.515251198991465,36.04651162790697,86,-2.423420108279167,24.418604651162788,86,-1.0001550491733786,27.906976744186046,86,-1.3083695325046478,38.372093023255815,222,-2.6415671882081666,15.765765765765765,222,3.599719754507012,97.74774774774775,222,-3.518215762978445,0.0
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
calibration,1,baseline,50-59,6,-2.217359092084505,-2.217359092084505,0.0,,-2.217359092084505,-2.217359092084505
calibration,1,baseline,60-69,0,,,,,,
calibration,1,baseline,70-74,0,,,,,,
calibration,1,baseline,75-79,183,-4.504166480257715,-2.042934443600224,15.846994535519126,1.8967117603848174,-5.709526668430659,-4.504166480257715
calibration,1,baseline,80-84,0,,,,,,
calibration,1,baseline,85-89,0,,,,,,
calibration,1,baseline,90+,46,-2.928296915459608,-1.4711447518711145,43.47826086956522,1.4835317223955924,-6.322011252271301,-2.928296915459608
calibration,1,raw,0-49,6,-2.217359092084505,-2.217359092084505,0.0,,-2.217359092084505,-2.217359092084505
calibration,1,raw,50-59,5,-15.723199636286832,-13.595030339120717,0.0,,-15.723199636286832,-15.723199636286832
calibration,1,raw,60-69,109,-6.786637291257339,-5.066480409554554,11.926605504587156,2.108930372218887,-7.991245412353078,-6.786637291257339
calibration,1,raw,70-74,59,-1.8934254315543997,-1.277164078998619,20.33898305084746,1.5124392460610077,-2.7630079024349294,-1.8934254315543997
calibration,1,raw,75-79,56,-0.5159385822876784,-1.0040546478622103,42.857142857142854,1.62957957114558,-2.1250771973626223,-0.5159385822876784
calibration,1,raw,80-84,0,,,,,,
calibration,1,raw,85-89,0,,,,,,
calibration,1,raw,90+,0,,,,,,
calibration,1,adjusted,0-49,6,-2.217359092084505,-2.217359092084505,0.0,,-2.217359092084505,-2.217359092084505
calibration,1,adjusted,50-59,0,,,,,,
calibration,1,adjusted,60-69,31,-12.520104560441176,-5.882134001505778,0.0,,-12.520104560441176,-12.520104560441176
calibration,1,adjusted,70-74,99,-5.001730117302624,-3.902111740105438,17.17171717171717,2.2693521292855854,-6.50914960744896,-5.001730117302624
calibration,1,adjusted,75-79,73,-1.2427041661413227,-1.2152276610414454,16.43835616438356,1.368804571108729,-1.756443589862645,-1.2427041661413227
calibration,1,adjusted,80-84,26,0.5787616583326556,0.22252073468191064,76.92307692307693,1.4835317223955924,-2.4371385552104665,0.5787616583326556
calibration,1,adjusted,85-89,0,,,,,,
calibration,1,adjusted,90+,0,,,,,,
calibration,5,baseline,0-49,0,,,,,,
calibration,5,baseline,50-59,3,0.6232591912710841,0.6232591912710841,100.0,0.6232591912710841,,0.6232591912710841
calibration,5,baseline,60-69,0,,,,,,
calibration,5,baseline,70-74,0,,,,,,
calibration,5,baseline,75-79,130,-5.187348407343579,-3.258087673825673,10.0,3.87721083556489,-6.194521656555629,-5.187348407343579
calibration,5,baseline,80-84,0,,,,,,
calibration,5,baseline,85-89,0,,,,,,
calibration,5,baseline,90+,40,-1.598375115957635,0.7860842697011732,55.00000000000001,1.8867764125557913,-5.85800476191849,-1.598375115957635
calibration,5,raw,0-49,3,0.6232591912710841,0.6232591912710841,100.0,0.6232591912710841,,0.6232591912710841
calibration,5,raw,50-59,1,-15.864817290742806,-15.864817290742806,0.0,,-15.864817290742806,-15.864817290742806
calibration,5,raw,60-69,72,-7.7010409134782645,-5.896414748807773,5.555555555555555,5.400447814749844,-8.471716721021094,-7.7010409134782645
calibration,5,raw,70-74,41,-3.2436069257856683,-2.4990459288589695,4.878048780487805,2.998641109936457,-3.563722209668855,-3.2436069257856683
calibration,5,raw,75-79,56,-0.6243330459746492,0.7860842697011732,51.78571428571429,2.2177154641275414,-3.676903667936261,-0.6243330459746492
calibration,5,raw,80-84,0,,,,,,
calibration,5,raw,85-89,0,,,,,,
calibration,5,raw,90+,0,,,,,,
calibration,5,adjusted,0-49,3,0.6232591912710841,0.6232591912710841,100.0,0.6232591912710841,,0.6232591912710841
calibration,5,adjusted,50-59,0,,,,,,
calibration,5,adjusted,60-69,13,-12.864843314630892,-10.096415573715527,7.6923076923076925,3.0672009047650444,-14.192513666247223,-12.864843314630892
calibration,5,adjusted,70-74,71,-6.207545512528212,-4.176102745578122,4.225352112676056,6.178196784744778,-6.753975319760844,-6.207545512528212
calibration,5,adjusted,75-79,60,-2.213125420963112,-2.7505352504460165,18.333333333333332,3.4825168776486124,-3.491738998202479,-2.213125420963112
calibration,5,adjusted,80-84,26,0.09522777478925976,0.7860842697011732,76.92307692307693,1.6001672512718443,-4.921237146819355,0.09522777478925976
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
calibration,OPTIONS_DATA_PARTIAL,contracts_only,7,89.28571428571429,73.46857142857142,76.0757142857143,100.0,4,2.7445427101092736,4,2.4142502328425155,0,,0,,0,
calibration,OPTIONS_DATA_PARTIAL,partial,45,82.22222222222223,72.22933333333334,74.70022222222222,100.0,15,-1.1459520633302875,12,-2.1895132932639645,0,,0,,0,
calibration,OPTIONS_DATA_PARTIAL,quote_only,88,85.22727272727273,72.9003409090909,75.44420454545455,100.0,44,-3.7561349123621643,37,-2.8447280814975597,0,,0,,0,
calibration,OPTIONS_NOT_ELIGIBLE,unavailable,1141,75.98597721297108,62.62868536371604,64.03222611744084,54.601226993865026,11,-2.481770924091528,3,0.6232591912710841,0,,0,,0,
calibration,OPTIONS_UNAVAILABLE,unavailable,724,79.55801104972376,69.34834254143647,71.49744475138122,98.89502762430939,166,-4.743873962318381,117,-5.268531623844132,0,,0,,0,
```

Availability is reported separately from the formula value. Missing options
data is never classified as an observed score of 50.

## Portfolio Fit cohorts

```csv
partition,cohort,predictions,raw_score_mean,adjusted_score_mean,net_alpha_spy_1d_n,net_alpha_spy_1d_mean,net_alpha_spy_1d_median,net_alpha_spy_1d_win_rate,net_alpha_spy_1d_average_gain,net_alpha_spy_1d_average_loss,net_alpha_spy_1d_expectancy,net_alpha_spy_5d_n,net_alpha_spy_5d_mean,net_alpha_spy_5d_median,net_alpha_spy_5d_win_rate,net_alpha_spy_5d_average_gain,net_alpha_spy_5d_average_loss,net_alpha_spy_5d_expectancy,net_alpha_spy_10d_n,net_alpha_spy_10d_mean,net_alpha_spy_10d_median,net_alpha_spy_10d_win_rate,net_alpha_spy_10d_average_gain,net_alpha_spy_10d_average_loss,net_alpha_spy_10d_expectancy,net_alpha_spy_20d_n,net_alpha_spy_20d_mean,net_alpha_spy_20d_median,net_alpha_spy_20d_win_rate,net_alpha_spy_20d_average_gain,net_alpha_spy_20d_average_loss,net_alpha_spy_20d_expectancy,net_alpha_spy_60d_n,net_alpha_spy_60d_mean,net_alpha_spy_60d_median,net_alpha_spy_60d_win_rate,net_alpha_spy_60d_average_gain,net_alpha_spy_60d_average_loss,net_alpha_spy_60d_expectancy
calibration,missing,526,65.95994296577948,65.95994296577948,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,other_observed,587,60.1576660988075,58.24175468483816,67,-0.8386871757181611,-1.2152276610414454,35.82089552238806,1.62957957114558,-2.2163244297816447,-0.8386871757181611,59,-0.5608961525553747,0.6232591912710841,54.23728813559322,2.0682351885472485,-3.676903667936261,-0.5608961525553747,0,,,,,,,0,,,,,,,0,,,,,,
calibration,raw_high_fit_weak,22,75.14000000000003,69.37272727272725,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,raw_medium_fit_good,870,69.18022988505747,73.77566666666667,173,-5.376136204567594,-3.680900326953819,14.450867052023122,1.8226146316631047,-6.5921414133903475,-5.376136204567594,114,-6.169540763319214,-3.6235112159675,5.263157894736842,4.599845579812048,-6.767840004604283,-6.169540763319214,0,,,,,,,0,,,,,,,0,,,,,,
```

## Component contribution and redundancy

```csv
partition,horizon,component,n,pearson_forward_alpha,spearman_forward_alpha,max_abs_component_correlation,incremental_r2
calibration,1,technical_score,240,0.04786587161965675,0.08853900578389579,0.3344803784857106,
calibration,1,momentum_score,240,-0.08996406839936223,-0.13619635251880713,0.5393165737562317,
calibration,1,research_score,240,0.006669856510667462,0.12330120469492672,0.35957958163107556,
calibration,1,volatility_score,240,-0.06175703559659863,-0.024042152137533683,0.28778237520827343,
calibration,1,liquidity_score,240,0.6648842161859633,0.7534772428223343,0.12575039116870063,
calibration,1,options_score,0,,,,
calibration,1,relative_opportunity_score,240,,,,
calibration,1,risk_reward_score,240,-0.11643165254904153,-0.1905101458766028,0.5393165737562318,
calibration,5,technical_score,173,0.17096525227400217,0.19816494927669653,0.3344803784857106,
calibration,5,momentum_score,173,-0.20207035338705326,-0.23904593116773096,0.5393165737562317,
calibration,5,research_score,173,0.025664113232908965,0.16668288973230172,0.35957958163107556,
calibration,5,volatility_score,173,-0.31083794143874616,-0.3194143027212238,0.28778237520827343,
calibration,5,liquidity_score,173,0.6382212914508598,0.7245783050980464,0.12575039116870063,
calibration,5,options_score,0,,,,
calibration,5,relative_opportunity_score,173,,,,
calibration,5,risk_reward_score,173,-0.06444951383267632,-0.1287176311736731,0.5393165737562318,
calibration,10,technical_score,0,,,0.3344803784857106,
calibration,10,momentum_score,0,,,0.5393165737562317,
calibration,10,research_score,0,,,0.35957958163107556,
calibration,10,volatility_score,0,,,0.28778237520827343,
calibration,10,liquidity_score,0,,,0.12575039116870063,
calibration,10,options_score,0,,,,
calibration,10,relative_opportunity_score,0,,,,
calibration,10,risk_reward_score,0,,,0.5393165737562318,
calibration,20,technical_score,0,,,0.3344803784857106,
calibration,20,momentum_score,0,,,0.5393165737562317,
calibration,20,research_score,0,,,0.35957958163107556,
calibration,20,volatility_score,0,,,0.28778237520827343,
calibration,20,liquidity_score,0,,,0.12575039116870063,
calibration,20,options_score,0,,,,
calibration,20,relative_opportunity_score,0,,,,
calibration,20,risk_reward_score,0,,,0.5393165737562318,
calibration,60,technical_score,0,,,0.3344803784857106,
calibration,60,momentum_score,0,,,0.5393165737562317,
calibration,60,research_score,0,,,0.35957958163107556,
calibration,60,volatility_score,0,,,0.28778237520827343,
calibration,60,liquidity_score,0,,,0.12575039116870063,
calibration,60,options_score,0,,,,
calibration,60,relative_opportunity_score,0,,,,
calibration,60,risk_reward_score,0,,,0.5393165737562318,
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
5522e100effd8a5697d20573,2026-09-10T21:10:03+00:00,calibration,TRGP,BUY,WAIT,73.1,100.0,77.13,-3.6307928684466053,-5.172093404289288,,,
53c26794356af012cc307291,2026-09-11T06:44:58+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-19.383811230653382,-18.190478941420352,,,
8ca424c3afa2faff80cd5fa8,2026-09-11T08:54:52+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186609831009546,-5.896414748807773,,,
3457725c926d4c9bca6c86ef,2026-09-11T09:29:41+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186609831009546,-5.896414748807773,,,
62964736889913e1a2f9310e,2026-09-11T11:00:53+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186609831009546,-5.896414748807773,,,
f210d637d4e1bb82d574ae0b,2026-09-11T11:21:56+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186609831009546,-5.896414748807773,,,
67f32e63bb66249fa1c7fee3,2026-09-11T11:38:56+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186609831009546,-5.896414748807773,,,
fb9cc1abbfcca2453eec217b,2026-09-15T20:21:08+00:00,calibration,ELV,BUY,WAIT,67.59,100.0,72.45,-5.422241614795949,,,,
fabca3d3e4bba17e1172975c,2026-09-16T05:40:32+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
fabca3d3e4bba17e1172975c,2026-09-16T05:40:32+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,,,,
e1338d825a461549ab9e718a,2026-09-16T05:50:47+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
e1338d825a461549ab9e718a,2026-09-16T05:50:47+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,,,,
e991d1db51ca3517cd30ca69,2026-09-16T05:54:18+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
e991d1db51ca3517cd30ca69,2026-09-16T05:54:18+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,,,,
92e9fb98a9868fa5713aaf9d,2026-09-16T06:00:15+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
92e9fb98a9868fa5713aaf9d,2026-09-16T06:00:15+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,,,,
3f6b3bd68f68e3e0a4cb2309,2026-09-16T06:03:42+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
3f6b3bd68f68e3e0a4cb2309,2026-09-16T06:03:42+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,,,,
```

## BUY / WAIT / AVOID transition matrix

```csv
partition,baseline_decision,enhanced_decision,predictions
calibration,BUY,BUY,440
calibration,BUY,WAIT,18
calibration,BUY,AVOID,0
calibration,WAIT,BUY,0
calibration,WAIT,WAIT,1363
calibration,WAIT,AVOID,0
calibration,AVOID,BUY,0
calibration,AVOID,WAIT,0
calibration,AVOID,AVOID,184
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
