# Enhanced Scoring forward validation

Generated: 2026-09-21T23:11:06+00:00

## Data coverage

```csv
partition,predictions,execution_eligible_pct,options_pct,options_partial_pct,portfolio_fit_pct,matured_1d,matured_5d,matured_10d,matured_20d,matured_60d
calibration,2139,92.56661991584852,0.0,6.545114539504442,74.0065451145395,1711,761,0,0,0
holdout_locked,0,,,,,0,0,0,0,0
```

## Gross, net and benchmark alpha

```csv
partition,horizon,metric,n,mean,median,win_rate,average_gain,average_loss,expectancy
calibration,1,gross_return_pct,1609,-0.3813154394053929,-0.39907590738684773,43.443132380360474,1.851676781753579,-2.0965479257681636,-0.3813154394053929
calibration,1,net_return_pct,277,-3.636084788284677,-2.081818406596427,21.299638989169676,1.4927291220737806,-5.02415827778536,-3.636084788284677
calibration,1,spy_return_pct,1609,0.13908935854083368,-0.3515226069689459,48.47731510254817,0.8735486202479629,-0.5519579564550178,0.13908935854083368
calibration,1,qqq_return_pct,1609,0.3641970994476644,0.025547549996507435,51.08763206960846,1.4808169360381807,-0.8020818150090118,0.3641970994476644
calibration,1,sector_return_pct,970,0.14266380808606288,-0.019886140024105714,49.79381443298969,1.4843766366631368,-1.188028791919536,0.14266380808606288
calibration,1,cash_return_pct,1609,0.015257213204416253,0.01531685456093168,100.0,0.015257213204416253,,0.015257213204416253
calibration,1,gross_alpha_spy_pct,1609,-0.5204047979462266,-0.6210694874053457,40.95711622125544,1.8776924138462987,-2.1839269690738834,-0.5204047979462266
calibration,1,net_alpha_spy_pct,277,-3.984568022771852,-2.720621269863953,17.689530685920577,1.7280668469198268,-5.21228341143366,-3.984568022771852
calibration,1,net_alpha_qqq_pct,277,-4.193334998907917,-2.673846599402447,20.577617328519857,1.7142219808382833,-5.723929307296706,-4.193334998907917
calibration,1,net_alpha_sector_pct,271,-3.7943674087826844,-1.9551209754170484,21.771217712177123,1.1024343812557493,-5.157156586199041,-3.7943674087826844
calibration,1,net_alpha_cash_pct,277,-3.651325245693604,-2.0970512431030226,20.577617328519857,1.529401036733534,-4.993604327958817,-3.651325245693604
calibration,5,gross_return_pct,722,-1.084429592739586,-1.5384600712702867,31.71745152354571,2.9817362411987873,-2.973175994305281,-1.084429592739586
calibration,5,net_return_pct,173,-4.0432739916631695,-2.9543835034436943,23.121387283236995,2.501694476475541,-6.011685561028196,-4.0432739916631695
calibration,5,spy_return_pct,722,0.04619938686258654,-0.09270593630656965,34.62603878116344,0.7300026287490682,-0.31598453362813456,0.04619938686258654
calibration,5,qqq_return_pct,722,0.8193165065543054,0.919036364296022,87.53462603878116,1.1888169807286517,-1.7753979343144377,0.8193165065543054
calibration,5,sector_return_pct,448,-0.6691216645229613,-1.2741809243906443,32.36607142857143,1.2803499765541118,-1.602037136325521,-0.6691216645229613
calibration,5,cash_return_pct,722,0.07549297598650019,0.07618738999861652,100.0,0.07549297598650019,,0.07549297598650019
calibration,5,gross_alpha_spy_pct,722,-1.1306289796021727,-1.445754134963717,31.994459833795013,2.9121521353356408,-3.032629870743996,-1.1306289796021727
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
calibration,1,baseline_buy,444,-0.09639181841726382,36.26126126126126,50,-2.6737716621718817,24.0,50,-2.9116828638119556,40.0,50,-2.9094063029220893,40.0,50,-2.6995773128049065,40.0,50,-2.688941968303699,24.0,444,-1.7873807866248221,17.117117117117118,444,1.0514084808282613,61.261261261261254,444,0.0,0.0
calibration,1,enhanced_shadow_buy,426,0.09781128396013683,37.79342723004695,37,-0.3365196133635758,32.432432432432435,37,-0.48885773643084174,54.054054054054056,37,-0.38197964755150077,54.054054054054056,37,-0.49951305650131683,54.054054054054056,37,-0.3516879980093525,32.432432432432435,426,-1.6282367243939122,17.84037558685446,426,1.196406523451907,63.6150234741784,426,0.0,0.0
calibration,1,enhanced_raw_75,101,-0.14185321451676783,41.584158415841586,59,-0.42061949340922267,35.59322033898305,59,-0.5634019375918813,40.67796610169492,59,-0.3912452889526632,40.67796610169492,59,-0.6299182907014204,37.28813559322034,59,-0.4357504594440553,35.59322033898305,101,-1.8784025472433572,24.752475247524753,101,1.9707662199171827,73.26732673267327,101,0.0,0.0
calibration,1,enhanced_adjusted_75,382,0.6755857619834865,59.947643979057595,126,-0.7766093441141593,28.57142857142857,126,-1.1953283406141526,25.396825396825395,126,-1.376712007881013,28.57142857142857,126,-0.9408153348198991,30.158730158730158,126,-0.7918293403542394,28.57142857142857,382,-1.0430508718071494,27.225130890052355,382,2.194555400331416,86.38743455497382,382,0.0,0.0
calibration,5,baseline_buy,223,-0.362999712329255,47.98206278026906,40,-1.291760182037305,55.00000000000001,40,-1.598375115957635,55.00000000000001,40,-2.5236893236587647,30.0,40,-0.7395626195683157,32.5,40,-1.3672976689977807,55.00000000000001,223,-3.391768552655567,13.901345291479823,223,2.0888703612367965,88.78923766816143,223,-1.7458543675997908,0.0
calibration,5,enhanced_shadow_buy,216,-0.2624741395426732,49.53703703703704,33,-0.1214783218073662,66.66666666666666,33,-0.3360714711683909,66.66666666666666,33,-1.2521701763782536,36.36363636363637,33,0.3532363499809302,39.39393939393939,33,-0.19715366698805317,66.66666666666666,216,-3.2813514395021026,14.351851851851851,216,2.2130088398395986,91.20370370370371,216,-1.7697097825058978,0.0
calibration,5,enhanced_raw_75,64,0.009341491327365281,54.6875,56,-0.3573198962882427,55.35714285714286,56,-0.6243330459746492,51.78571428571429,56,-1.514392879763463,33.92857142857143,56,-0.11410899106801309,35.714285714285715,56,-0.43290380489429936,55.35714285714286,64,-3.0650047719892455,18.75,64,3.6335389479930287,92.1875,64,-2.9693398792836696,0.0
calibration,5,enhanced_adjusted_75,235,-0.06531146488090593,49.361702127659576,86,-1.2328018174958864,38.372093023255815,86,-1.515251198991465,36.04651162790697,86,-2.423420108279167,24.418604651162788,86,-1.0001550491733786,27.906976744186046,86,-1.3083695325046478,38.372093023255815,235,-2.6705557769873907,15.319148936170212,235,3.581538379163991,97.44680851063829,235,-3.4500291722415892,0.0
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
calibration,1,baseline,75-79,221,-4.2752807446366425,-2.7664778710478655,13.122171945701359,1.8967117603848174,-5.207508779249259,-4.2752807446366425
calibration,1,baseline,80-84,0,,,,,,
calibration,1,baseline,85-89,0,,,,,,
calibration,1,baseline,90+,50,-2.9116828638119556,-2.1656394859849155,40.0,1.4835317223955924,-5.841825921283655,-2.9116828638119556
calibration,1,raw,0-49,6,-2.217359092084505,-2.217359092084505,0.0,,-2.217359092084505,-2.217359092084505
calibration,1,raw,50-59,5,-15.723199636286832,-13.595030339120717,0.0,,-15.723199636286832,-15.723199636286832
calibration,1,raw,60-69,124,-6.4214416015994065,-5.066480409554554,10.483870967741936,2.108930372218887,-7.420494175109657,-6.4214416015994065
calibration,1,raw,70-74,83,-2.196454417561618,-1.7750012029729576,14.457831325301203,1.5124392460610077,-2.823309684652766,-2.196454417561618
calibration,1,raw,75-79,59,-0.5634019375918813,-1.2152276610414454,40.67796610169492,1.62957957114558,-2.0671606864404257,-0.5634019375918813
calibration,1,raw,80-84,0,,,,,,
calibration,1,raw,85-89,0,,,,,,
calibration,1,raw,90+,0,,,,,,
calibration,1,adjusted,0-49,6,-2.217359092084505,-2.217359092084505,0.0,,-2.217359092084505,-2.217359092084505
calibration,1,adjusted,50-59,0,,,,,,
calibration,1,adjusted,60-69,37,-11.405314044384847,-5.7667375155516325,0.0,,-11.405314044384847,-11.405314044384847
calibration,1,adjusted,70-74,108,-4.794566640700678,-3.902111740105438,15.74074074074074,2.2693521292855854,-6.1141998175113,-4.794566640700678
calibration,1,adjusted,75-79,97,-1.6630002095280543,-1.4493845699370018,12.371134020618557,1.368804571108729,-2.0910197079708945,-1.6630002095280543
calibration,1,adjusted,80-84,29,0.3689534278220013,0.22252073468191064,68.96551724137932,1.4835317223955924,-2.1078872267859783,0.3689534278220013
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
calibration,OPTIONS_DATA_PARTIAL,quote_only,88,85.22727272727273,72.9003409090909,75.44420454545455,100.0,56,-3.602896612941992,37,-2.8447280814975597,0,,0,,0,
calibration,OPTIONS_NOT_ELIGIBLE,unavailable,1211,75.9289843104872,62.556870355078445,63.9524525185797,56.06936416184971,11,-2.481770924091528,3,0.6232591912710841,0,,0,,0,
calibration,OPTIONS_UNAVAILABLE,unavailable,788,79.37817258883248,69.36600253807106,71.51701776649746,96.95431472081218,196,-4.502285037352178,117,-5.268531623844132,0,,0,,0,
```

Availability is reported separately from the formula value. Missing options
data is never classified as an observed score of 50.

## Portfolio Fit cohorts

```csv
partition,cohort,predictions,raw_score_mean,adjusted_score_mean,net_alpha_spy_1d_n,net_alpha_spy_1d_mean,net_alpha_spy_1d_median,net_alpha_spy_1d_win_rate,net_alpha_spy_1d_average_gain,net_alpha_spy_1d_average_loss,net_alpha_spy_1d_expectancy,net_alpha_spy_5d_n,net_alpha_spy_5d_mean,net_alpha_spy_5d_median,net_alpha_spy_5d_win_rate,net_alpha_spy_5d_average_gain,net_alpha_spy_5d_average_loss,net_alpha_spy_5d_expectancy,net_alpha_spy_10d_n,net_alpha_spy_10d_mean,net_alpha_spy_10d_median,net_alpha_spy_10d_win_rate,net_alpha_spy_10d_average_gain,net_alpha_spy_10d_average_loss,net_alpha_spy_10d_expectancy,net_alpha_spy_20d_n,net_alpha_spy_20d_mean,net_alpha_spy_20d_median,net_alpha_spy_20d_win_rate,net_alpha_spy_20d_average_gain,net_alpha_spy_20d_average_loss,net_alpha_spy_20d_expectancy,net_alpha_spy_60d_n,net_alpha_spy_60d_mean,net_alpha_spy_60d_median,net_alpha_spy_60d_win_rate,net_alpha_spy_60d_average_gain,net_alpha_spy_60d_average_loss,net_alpha_spy_60d_expectancy
calibration,missing,556,66.00203237410072,66.00203237410072,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,other_observed,640,60.14981250000001,58.103296875,70,-0.8648599211846829,-1.2152276610414454,34.285714285714285,1.62957957114558,-2.1663066128352546,-0.8648599211846829,59,-0.5608961525553747,0.6232591912710841,54.23728813559322,2.0682351885472485,-3.676903667936261,-0.5608961525553747,0,,,,,,,0,,,,,,,0,,,,,,
calibration,raw_high_fit_weak,25,75.14040000000001,69.37280000000001,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,raw_medium_fit_good,918,69.19944444444444,73.79334422657952,212,-4.986700346402711,-3.6555136991682176,11.79245283018868,1.8226146316631047,-5.897036573416857,-4.986700346402711,114,-6.169540763319214,-3.6235112159675,5.263157894736842,4.599845579812048,-6.767840004604283,-6.169540763319214,0,,,,,,,0,,,,,,,0,,,,,,
```

## Component contribution and redundancy

```csv
partition,horizon,component,n,pearson_forward_alpha,spearman_forward_alpha,max_abs_component_correlation,incremental_r2
calibration,1,technical_score,282,0.04569006282436067,0.082441870705152,0.3217841343995315,
calibration,1,momentum_score,282,-0.06776672085104608,-0.13470338580700586,0.555514452235283,
calibration,1,research_score,282,0.008834443732113888,0.10135356271935667,0.3658574051465053,
calibration,1,volatility_score,282,-0.053007618342490286,-0.030699247387007078,0.2889342130691483,
calibration,1,liquidity_score,282,0.6373210790454408,0.6905236343630345,0.11938650388320636,
calibration,1,options_score,0,,,,
calibration,1,relative_opportunity_score,282,,,,
calibration,1,risk_reward_score,282,-0.11540093855521331,-0.1705922199436849,0.555514452235283,
calibration,5,technical_score,173,0.17096525227400217,0.19816494927669653,0.3217841343995315,
calibration,5,momentum_score,173,-0.20207035338705326,-0.23904593116773096,0.555514452235283,
calibration,5,research_score,173,0.025664113232908965,0.16668288973230172,0.3658574051465053,
calibration,5,volatility_score,173,-0.31083794143874616,-0.3194143027212238,0.2889342130691483,
calibration,5,liquidity_score,173,0.6382212914508598,0.7245783050980464,0.11938650388320636,
calibration,5,options_score,0,,,,
calibration,5,relative_opportunity_score,173,,,,
calibration,5,risk_reward_score,173,-0.06444951383267632,-0.1287176311736731,0.555514452235283,
calibration,10,technical_score,0,,,0.3217841343995315,
calibration,10,momentum_score,0,,,0.555514452235283,
calibration,10,research_score,0,,,0.3658574051465053,
calibration,10,volatility_score,0,,,0.2889342130691483,
calibration,10,liquidity_score,0,,,0.11938650388320636,
calibration,10,options_score,0,,,,
calibration,10,relative_opportunity_score,0,,,,
calibration,10,risk_reward_score,0,,,0.555514452235283,
calibration,20,technical_score,0,,,0.3217841343995315,
calibration,20,momentum_score,0,,,0.555514452235283,
calibration,20,research_score,0,,,0.3658574051465053,
calibration,20,volatility_score,0,,,0.2889342130691483,
calibration,20,liquidity_score,0,,,0.11938650388320636,
calibration,20,options_score,0,,,,
calibration,20,relative_opportunity_score,0,,,,
calibration,20,risk_reward_score,0,,,0.555514452235283,
calibration,60,technical_score,0,,,0.3217841343995315,
calibration,60,momentum_score,0,,,0.555514452235283,
calibration,60,research_score,0,,,0.3658574051465053,
calibration,60,volatility_score,0,,,0.2889342130691483,
calibration,60,liquidity_score,0,,,0.11938650388320636,
calibration,60,options_score,0,,,,
calibration,60,relative_opportunity_score,0,,,,
calibration,60,risk_reward_score,0,,,0.555514452235283,
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
calibration,BUY,BUY,449
calibration,BUY,WAIT,18
calibration,BUY,AVOID,0
calibration,WAIT,BUY,0
calibration,WAIT,WAIT,1485
calibration,WAIT,AVOID,0
calibration,AVOID,BUY,0
calibration,AVOID,WAIT,0
calibration,AVOID,AVOID,187
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
