# Enhanced Scoring forward validation

Generated: 2026-09-25T08:04:34+00:00

## Data coverage

```csv
partition,predictions,execution_eligible_pct,options_pct,options_partial_pct,portfolio_fit_pct,matured_1d,matured_5d,matured_10d,matured_20d,matured_60d
calibration,2651,92.7951716333459,0.0,5.809128630705394,79.02678234628442,2419,1427,137,0,0
holdout_locked,0,,,,,0,0,0,0,0
```

## Gross, net and benchmark alpha

```csv
partition,horizon,metric,n,mean,median,win_rate,average_gain,average_loss,expectancy
calibration,1,gross_return_pct,2240,-0.807329489124487,-0.6896525963969724,39.464285714285715,2.0506467296188244,-2.670493926712309,-0.807329489124487
calibration,1,net_return_pct,313,-3.397386159329207,-2.081818406596427,22.364217252396166,2.1432225385113357,-4.993446278048705,-3.397386159329207
calibration,1,spy_return_pct,2240,0.23792701214672926,-0.015513266604716414,49.375,1.0458299283038774,-0.5500276838583904,0.23792701214672926
calibration,1,qqq_return_pct,2240,0.6941278843106127,0.06913851652496916,54.776785714285715,1.8270235321936916,-0.6780961630265425,0.6941278843106127
calibration,1,sector_return_pct,1162,0.1566953563490268,-0.0718497725542,48.45094664371773,1.4687860135184252,-1.0765384332776367,0.1566953563490268
calibration,1,cash_return_pct,2240,0.015328319078452703,0.015412308123874396,100.0,0.015328319078452703,,0.015328319078452703
calibration,1,gross_alpha_spy_pct,2240,-1.0452565012712163,-0.8393324762050347,37.76785714285714,2.0335004762645834,-2.9137130313969593,-1.0452565012712163
calibration,1,net_alpha_spy_pct,313,-3.6625360674419216,-2.10462766071475,20.12779552715655,2.238467998252856,-5.149589091997005,-3.6625360674419216
calibration,1,net_alpha_qqq_pct,313,-3.9599698590967027,-2.447890325586834,21.72523961661342,2.07646858163169,-5.635389507951932,-3.9599698590967027
calibration,1,net_alpha_sector_pct,296,-3.862008538325837,-2.0894753965860815,19.93243243243243,1.2543872463160022,-5.135710442519375,-3.862008538325837
calibration,1,net_alpha_cash_pct,313,-3.412655407239617,-2.0970512431030226,21.72523961661342,2.190590557386497,-4.967842042319519,-3.412655407239617
calibration,5,gross_return_pct,1323,-1.7247509110248864,-2.08588887987351,30.990173847316704,4.376842074993218,-4.464787191712096,-1.7247509110248864
calibration,5,net_return_pct,221,-4.282249113067128,-3.2605595185979768,24.8868778280543,2.9767707278856403,-6.687346048322563,-4.282249113067128
calibration,5,spy_return_pct,1321,0.7151817887752245,0.6480235179316507,57.9106737320212,1.4401139104500693,-0.2822517959032938,0.7151817887752245
calibration,5,qqq_return_pct,1321,2.557143185438691,1.1612893399005841,93.18697956093868,2.8739012718871098,-1.7754035303168993,2.557143185438691
calibration,5,sector_return_pct,690,-0.15058386580038124,-0.6930432223184901,43.188405797101446,2.07889231497025,-1.8454407583249939,-0.15058386580038124
calibration,5,cash_return_pct,1323,0.07608407006666253,0.07618738999861652,100.0,0.07608407006666253,,0.07608407006666253
calibration,5,gross_alpha_spy_pct,1321,-2.403202588858845,-2.1706685492901445,28.160484481453445,4.072698355681224,-4.941701167751264,-2.403202588858845
calibration,5,net_alpha_spy_pct,221,-4.809265602072803,-3.299650096714246,20.81447963800905,3.091776672323096,-6.8861109999140115,-4.809265602072803
calibration,5,net_alpha_qqq_pct,221,-6.300207618538056,-4.299662118721261,14.93212669683258,2.664608933870405,-7.873819034652308,-6.300207618538056
calibration,5,net_alpha_sector_pct,213,-4.201185556809355,-2.399578576923475,15.96244131455399,3.641900295418947,-5.690933707511936,-4.201185556809355
calibration,5,net_alpha_cash_pct,221,-4.358179340633169,-3.3367469085965933,24.8868778280543,2.9006946575327905,-6.7632279544833365,-4.358179340633169
calibration,10,gross_return_pct,133,-5.511814919743191,-7.1428548722040075,21.052631578947366,6.578747868714883,-8.735964996665343,-5.511814919743191
calibration,10,net_return_pct,7,-2.647816764573721,-11.53846360546772,28.57142857142857,20.25685193014327,-11.809684242460516,-2.647816764573721
calibration,10,spy_return_pct,111,0.9290489372059283,0.8584817081878526,100.0,0.9290489372059283,,0.9290489372059283
calibration,10,qqq_return_pct,111,3.5993620111648075,3.4020851620080395,100.0,3.5993620111648075,,3.5993620111648075
calibration,10,sector_return_pct,50,0.1694284254581855,2.3284472661142086,60.0,2.9811493304320984,-4.048152932002684,0.1694284254581855
calibration,10,cash_return_pct,133,0.14889802725289314,0.14830014630902166,100.0,0.14889802725289314,,0.14889802725289314
calibration,10,gross_alpha_spy_pct,111,-5.969968055357315,-7.297171521749923,18.91891891891892,7.704306716807544,-9.160632168862449,-5.969968055357315
calibration,10,net_alpha_spy_pct,7,-3.837956827001119,-12.344106572774106,28.57142857142857,18.775700470611923,-12.883419746046334,-3.837956827001119
calibration,10,net_alpha_qqq_pct,7,-6.7538262046807205,-14.880064473074096,28.57142857142857,15.57466599365279,-15.685223084014126,-6.7538262046807205
calibration,10,net_alpha_sector_pct,3,-7.7075837380769,-7.692835121151699,0.0,,-7.7075837380769,-7.7075837380769
calibration,10,net_alpha_cash_pct,7,-2.7968660296759427,-11.686457463180702,28.57142857142857,20.10702068079634,-11.958420713864856,-2.7968660296759427
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
calibration,1,baseline_buy,491,-0.022265855238077233,37.06720977596741,54,-2.3026525301154437,27.77777777777778,54,-2.4639255623169243,42.592592592592595,54,-2.525342511138635,42.592592592592595,54,-2.347147070348296,42.592592592592595,54,-2.317846983078136,27.77777777777778,491,-1.6682787118343723,17.515274949083505,491,1.1999817123816505,63.747454175152754,491,0.0,0.0
calibration,1,enhanced_shadow_buy,472,0.15821610735806949,38.559322033898304,40,-0.019502008572020602,37.5,40,-0.09913480481823882,57.49999999999999,40,-0.0685174538253019,57.49999999999999,40,-0.19179542431570534,57.49999999999999,40,-0.03469498599551106,37.5,472,-1.515103419192085,18.220338983050848,472,1.3407895474127014,66.10169491525424,472,0.0,0.0
calibration,1,enhanced_raw_75,133,-1.1539182049431027,31.57894736842105,62,-0.5116322479391814,33.87096774193548,62,-0.6079704012155807,38.70967741935484,62,-0.4864446441639721,38.70967741935484,62,-0.7238415211108225,35.483870967741936,62,-0.5267808908601653,33.87096774193548,133,-3.214542359535754,18.796992481203006,133,0.9666427215614422,55.639097744360896,133,0.0,0.0
calibration,1,enhanced_adjusted_75,453,0.5673797923914471,56.95364238410596,133,-0.7173840755209866,29.32330827067669,133,-1.0716741395227558,26.31578947368421,133,-1.305126864549972,29.32330827067669,133,-0.937928412404639,26.31578947368421,133,-0.7326186134509907,29.32330827067669,453,-1.0924283823301448,25.607064017660043,453,2.0297272051223745,81.45695364238411,453,0.0,0.0
calibration,5,baseline_buy,407,-1.4509205251837722,36.36363636363637,46,-2.45874814092932,47.82608695652174,46,-2.953533881444542,47.82608695652174,46,-4.242484097543285,26.08695652173913,46,-1.8079569035122878,28.26086956521739,46,-2.5344875163129723,47.82608695652174,407,-4.049463430679339,7.862407862407863,407,2.340630495360312,89.1891891891892,407,-2.6257104038804453,0.0
calibration,5,enhanced_shadow_buy,389,-1.3492850023492309,38.04627249357326,33,-0.12147851165283478,66.66666666666666,33,-0.3360716610138596,66.66666666666666,33,-1.2521695150594814,36.36363636363637,33,0.3532385231983991,39.39393939393939,33,-0.19715385683352188,66.66666666666666,389,-3.9348133854795515,8.226221079691516,389,2.454047857911434,91.77377892030847,389,-2.6479545055675957,0.0
calibration,5,enhanced_raw_75,91,-1.650342913493722,43.956043956043956,56,-0.3573200081614653,55.35714285714286,56,-0.6243331578478718,51.78571428571429,56,-1.514391806854286,33.92857142857143,56,-0.11410693213168496,35.714285714285715,56,-0.432903916767522,55.35714285714286,91,-4.349793481123855,13.186813186813188,91,2.9126095689386133,82.41758241758241,91,-3.4085260522242886,0.0
calibration,5,enhanced_adjusted_75,302,-0.31563997115400966,50.66225165562914,99,-1.6520484648438571,40.4040404040404,99,-2.133258004038606,31.313131313131315,99,-3.4110889234884474,21.21212121212121,99,-1.8093384227206686,24.242424242424242,99,-1.7278154584541217,40.4040404040404,302,-3.0887962287776274,12.251655629139073,302,3.621303846473506,92.71523178807946,302,-3.408780717410738,0.0
calibration,10,baseline_buy,23,-3.8172223937115444,13.043478260869565,4,4.0201683660967795,50.0,4,2.5390169065654318,50.0,4,-0.662017570393699,50.0,0,,,4,3.870337116749848,50.0,23,-7.608068302768052,8.695652173913043,23,3.4087567634463194,60.86956521739131,23,-7.287210730467416,0.0
calibration,10,enhanced_shadow_buy,23,-3.8172223937115444,13.043478260869565,4,4.0201683660967795,50.0,4,2.5390169065654318,50.0,4,-0.662017570393699,50.0,0,,,4,3.870337116749848,50.0,23,-7.608068302768052,8.695652173913043,23,3.4087567634463194,60.86956521739131,23,-7.287210730467416,0.0
calibration,10,enhanced_raw_75,4,4.657836897776196,50.0,4,4.0201683660967795,50.0,4,2.5390169065654318,50.0,4,-0.662017570393699,50.0,0,,,4,3.870337116749848,50.0,4,-6.080845004337348,50.0,4,12.039055249967067,100.0,4,-7.991812936861931,0.0
calibration,10,enhanced_adjusted_75,31,1.2371513175169038,54.83870967741935,4,4.0201683660967795,50.0,4,2.5390169065654318,50.0,4,-0.662017570393699,50.0,0,,,4,3.870337116749848,50.0,31,-4.585339896688455,6.451612903225806,31,7.1587768253144,100.0,31,-7.310168269604306,0.0
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
calibration,1,baseline,50-59,9,0.9526716118046856,-1.635653061669053,33.33333333333333,7.292733019583067,-2.217359092084505,0.9526716118046856
calibration,1,baseline,60-69,0,,,,,,
calibration,1,baseline,70-74,0,,,,,,
calibration,1,baseline,75-79,250,-4.087583413001799,-2.762082806315366,14.799999999999999,2.0365488996508967,-5.151399824119872,-4.087583413001799
calibration,1,baseline,80-84,0,,,,,,
calibration,1,baseline,85-89,0,,,,,,
calibration,1,baseline,90+,54,-2.4639255623169243,-1.53265897438042,42.592592592592595,1.9040424149607615,-5.704675997071337,-2.4639255623169243
calibration,1,raw,0-49,9,0.9526716118046856,-1.635653061669053,33.33333333333333,7.292733019583067,-2.217359092084505,0.9526716118046856
calibration,1,raw,50-59,13,-4.636024148990229,-0.26635319332712437,38.46153846153847,3.829348764908515,-9.926882220176942,-4.636024148990229
calibration,1,raw,60-69,142,-6.247970415943748,-5.066480409554554,11.267605633802818,1.788563703139153,-7.268482685033639,-6.247970415943748
calibration,1,raw,70-74,87,-1.9514201809116392,-1.742285144192715,17.24137931034483,2.1514408733840993,-2.8061829005565846,-1.9514201809116392
calibration,1,raw,75-79,62,-0.6079704012155807,-1.2152276610414454,38.70967741935484,1.6295795273187583,-2.0211598297635835,-0.6079704012155807
calibration,1,raw,80-84,0,,,,,,
calibration,1,raw,85-89,0,,,,,,
calibration,1,raw,90+,0,,,,,,
calibration,1,adjusted,0-49,9,0.9526716118046856,-1.635653061669053,33.33333333333333,7.292733019583067,-2.217359092084505,0.9526716118046856
calibration,1,adjusted,50-59,8,2.2934605305701496,2.2997623243381495,62.5,3.829348764908515,-0.26635319332712437,2.2934605305701496
calibration,1,adjusted,60-69,40,-10.995609388922194,-5.824435758528706,0.0,,-10.995609388922194,-10.995609388922194
calibration,1,adjusted,70-74,123,-4.8043779003797615,-3.902111740105438,16.260162601626014,1.9889955304617932,-6.123479537436373,-4.8043779003797615
calibration,1,adjusted,75-79,101,-1.4730579846227096,-1.2870567451621204,14.85148514851485,2.0365331334222767,-2.0851959703282303,-1.4730579846227096
calibration,1,adjusted,80-84,32,0.1951936215739729,0.22252073468191064,62.5,1.4835316698034062,-1.9520364588084151,0.1951936215739729
calibration,1,adjusted,85-89,0,,,,,,
calibration,1,adjusted,90+,0,,,,,,
calibration,5,baseline,0-49,0,,,,,,
calibration,5,baseline,50-59,6,3.4736005846878846,3.473600584687884,100.0,3.4736005846878846,,3.4736005846878846
calibration,5,baseline,60-69,0,,,,,,
calibration,5,baseline,70-74,0,,,,,,
calibration,5,baseline,75-79,169,-5.608442266389158,-3.5206954873407925,10.650887573964498,4.437280478189341,-6.805945639915074,-5.608442266389158
calibration,5,baseline,80-84,0,,,,,,
calibration,5,baseline,85-89,0,,,,,,
calibration,5,baseline,90+,46,-2.953533881444542,-2.048202105298268,47.82608695652174,1.8867761277875892,-7.390484723240664,-2.953533881444542
calibration,5,raw,0-49,6,3.4736005846878846,3.473600584687884,100.0,3.4736005846878846,,3.4736005846878846
calibration,5,raw,50-59,1,-15.864817290742806,-15.864817290742806,0.0,,-15.864817290742806,-15.864817290742806
calibration,5,raw,60-69,99,-7.662326705984371,-5.896414748807773,9.090909090909092,5.674344333784884,-8.995993809961298,-7.662326705984371
calibration,5,raw,70-74,59,-4.649008195653229,-2.7645620441158267,3.389830508474576,2.998641109936457,-4.917346767779183,-4.649008195653229
calibration,5,raw,75-79,56,-0.6243331578478718,0.7860842697011732,51.78571428571429,2.217715248096491,-3.676903667936261,-0.6243331578478718
calibration,5,raw,80-84,0,,,,,,
calibration,5,raw,85-89,0,,,,,,
calibration,5,raw,90+,0,,,,,,
calibration,5,adjusted,0-49,6,3.4736005846878846,3.473600584687884,100.0,3.4736005846878846,,3.4736005846878846
calibration,5,adjusted,50-59,0,,,,,,
calibration,5,adjusted,60-69,23,-12.692098755712315,-10.096415573715527,4.3478260869565215,3.0672009047650444,-13.408430558461287,-12.692098755712315
calibration,5,adjusted,70-74,93,-6.242779438548511,-5.896414748807773,8.60215053763441,6.000237262412364,-7.395063363344828,-6.242779438548511
calibration,5,adjusted,75-79,73,-2.9269651734534707,-2.7465521102130506,15.068493150684931,3.4825169337703383,-4.064131353767372,-2.9269651734534707
calibration,5,adjusted,80-84,26,0.09522751008774268,0.7860842697011732,76.92307692307693,1.6001669071598719,-4.921237146819355,0.09522751008774268
calibration,5,adjusted,85-89,0,,,,,,
calibration,5,adjusted,90+,0,,,,,,
calibration,10,baseline,0-49,0,,,,,,
calibration,10,baseline,50-59,0,,,,,,
calibration,10,baseline,60-69,0,,,,,,
calibration,10,baseline,70-74,0,,,,,,
calibration,10,baseline,75-79,3,-12.340588471756519,-12.344106572774106,0.0,,-12.340588471756519,-12.340588471756519
calibration,10,baseline,80-84,0,,,,,,
calibration,10,baseline,85-89,0,,,,,,
calibration,10,baseline,90+,4,2.5390169065654318,2.5390169065654318,50.0,18.775700470611923,-13.697666657481058,2.5390169065654318
calibration,10,raw,0-49,0,,,,,,
calibration,10,raw,50-59,0,,,,,,
calibration,10,raw,60-69,3,-12.340588471756519,-12.344106572774106,0.0,,-12.340588471756519,-12.340588471756519
calibration,10,raw,70-74,0,,,,,,
calibration,10,raw,75-79,4,2.5390169065654318,2.5390169065654318,50.0,18.775700470611923,-13.697666657481058,2.5390169065654318
calibration,10,raw,80-84,0,,,,,,
calibration,10,raw,85-89,0,,,,,,
calibration,10,raw,90+,0,,,,,,
calibration,10,adjusted,0-49,0,,,,,,
calibration,10,adjusted,50-59,0,,,,,,
calibration,10,adjusted,60-69,0,,,,,,
calibration,10,adjusted,70-74,3,-12.340588471756519,-12.344106572774106,0.0,,-12.340588471756519,-12.340588471756519
calibration,10,adjusted,75-79,2,18.775700470611923,18.775700470611923,100.0,18.775700470611923,,18.775700470611923
calibration,10,adjusted,80-84,2,-13.697666657481058,-13.697666657481058,0.0,,-13.697666657481058,-13.697666657481058
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
calibration,OPTIONS_DATA_PARTIAL,contracts_only,7,89.28571428571429,73.46857142857142,76.0757142857143,100.0,4,2.7445426049249013,4,2.414249544618571,0,,0,,0,
calibration,OPTIONS_DATA_PARTIAL,partial,58,82.75862068965517,72.34362068965518,74.82689655172416,100.0,24,-1.6943205052151888,15,-2.204415414089698,0,,0,,0,
calibration,OPTIONS_DATA_PARTIAL,quote_only,89,85.11235955056179,72.89516853932584,75.43842696629214,100.0,56,-3.6028966242117457,41,-3.5975070206615234,0,,0,,0,
calibration,OPTIONS_NOT_ELIGIBLE,unavailable,1499,73.46564376250834,61.94784523015344,63.27575717144762,64.50967311541027,25,0.992746432262518,11,4.769210308968248,0,,0,,0,
calibration,OPTIONS_UNAVAILABLE,unavailable,998,79.33366733466934,69.50568136272545,71.67236472945892,97.59519038076152,212,-4.442678232069822,155,-5.888917939911117,7,-3.837956827001118,0,,0,
```

Availability is reported separately from the formula value. Missing options
data is never classified as an observed score of 50.

## Portfolio Fit cohorts

```csv
partition,cohort,predictions,raw_score_mean,adjusted_score_mean,net_alpha_spy_1d_n,net_alpha_spy_1d_mean,net_alpha_spy_1d_median,net_alpha_spy_1d_win_rate,net_alpha_spy_1d_average_gain,net_alpha_spy_1d_average_loss,net_alpha_spy_1d_expectancy,net_alpha_spy_5d_n,net_alpha_spy_5d_mean,net_alpha_spy_5d_median,net_alpha_spy_5d_win_rate,net_alpha_spy_5d_average_gain,net_alpha_spy_5d_average_loss,net_alpha_spy_5d_expectancy,net_alpha_spy_10d_n,net_alpha_spy_10d_mean,net_alpha_spy_10d_median,net_alpha_spy_10d_win_rate,net_alpha_spy_10d_average_gain,net_alpha_spy_10d_average_loss,net_alpha_spy_10d_expectancy,net_alpha_spy_20d_n,net_alpha_spy_20d_mean,net_alpha_spy_20d_median,net_alpha_spy_20d_win_rate,net_alpha_spy_20d_average_gain,net_alpha_spy_20d_average_loss,net_alpha_spy_20d_expectancy,net_alpha_spy_60d_n,net_alpha_spy_60d_mean,net_alpha_spy_60d_median,net_alpha_spy_60d_win_rate,net_alpha_spy_60d_average_gain,net_alpha_spy_60d_average_loss,net_alpha_spy_60d_expectancy
calibration,missing,556,66.00203237410072,66.00203237410072,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,other_observed,935,60.04119786096257,57.6383422459893,87,-0.1479942996414142,-1.2152276610414454,40.229885057471265,2.6293459773486094,-2.017357947615469,-0.1479942996414142,67,0.26117397849507323,0.7860842697011732,59.70149253731343,2.9193763898362244,-3.676903667936261,0.26117397849507323,4,2.5390169065654318,2.5390169065654318,50.0,18.775700470611923,-13.697666657481058,2.5390169065654318,0,,,,,,,0,,,,,,
calibration,raw_high_fit_weak,25,75.14040000000001,69.37280000000001,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,raw_medium_fit_good,1135,69.3482026431718,73.92495154185022,234,-4.852997234977602,-3.6802345298898302,13.247863247863249,1.9641494306770297,-5.894039336629295,-4.852997234977602,159,-6.595765061174441,-4.928000557592984,6.918238993710692,5.1878528385397145,-7.471574499666709,-6.595765061174441,3,-12.340588471756519,-12.344106572774106,0.0,,-12.340588471756519,-12.340588471756519,0,,,,,,,0,,,,,,
```

## Component contribution and redundancy

```csv
partition,horizon,component,n,pearson_forward_alpha,spearman_forward_alpha,max_abs_component_correlation,incremental_r2
calibration,1,technical_score,321,0.005095424202080288,0.04510891392715425,0.19451598381505944,
calibration,1,momentum_score,321,-0.1739364506846959,-0.2440594218356875,0.566057283632239,
calibration,1,research_score,321,-0.12631131965477216,-0.035549385328254204,0.38057791013405023,
calibration,1,volatility_score,321,-0.08292262704676359,-0.007681509662559651,0.27426588739955143,
calibration,1,liquidity_score,321,0.6231173455900144,0.6469333116532614,0.14982170179399004,
calibration,1,options_score,0,,,,
calibration,1,relative_opportunity_score,321,,,,
calibration,1,risk_reward_score,321,-0.22744898916878498,-0.24802639974210175,0.5660572836322391,
calibration,5,technical_score,226,-0.036592681284257814,-0.035511283127759155,0.19451598381505944,
calibration,5,momentum_score,226,-0.250278242204549,-0.2791365717575399,0.566057283632239,
calibration,5,research_score,226,-0.17860458880400976,-0.017375264649076926,0.38057791013405023,
calibration,5,volatility_score,226,-0.19925740660281652,-0.1143251935166101,0.27426588739955143,
calibration,5,liquidity_score,226,0.5126309267750905,0.5737419700678337,0.14982170179399004,
calibration,5,options_score,0,,,,
calibration,5,relative_opportunity_score,226,,,,
calibration,5,risk_reward_score,226,-0.18439490725735153,-0.21049505319948913,0.5660572836322391,
calibration,10,technical_score,7,0.5144560387247271,0.0,0.19451598381505944,
calibration,10,momentum_score,7,-0.6464691538383279,-0.9449111825230683,0.566057283632239,
calibration,10,research_score,7,0.9992291036877058,0.7905694150420949,0.38057791013405023,
calibration,10,volatility_score,7,-0.8844569611806689,-0.3779644730092273,0.27426588739955143,
calibration,10,liquidity_score,7,0.9856208139167636,0.3779644730092273,0.14982170179399004,
calibration,10,options_score,0,,,,
calibration,10,relative_opportunity_score,7,,,,
calibration,10,risk_reward_score,7,,,0.5660572836322391,
calibration,20,technical_score,0,,,0.19451598381505944,
calibration,20,momentum_score,0,,,0.566057283632239,
calibration,20,research_score,0,,,0.38057791013405023,
calibration,20,volatility_score,0,,,0.27426588739955143,
calibration,20,liquidity_score,0,,,0.14982170179399004,
calibration,20,options_score,0,,,,
calibration,20,relative_opportunity_score,0,,,,
calibration,20,risk_reward_score,0,,,0.5660572836322391,
calibration,60,technical_score,0,,,0.19451598381505944,
calibration,60,momentum_score,0,,,0.566057283632239,
calibration,60,research_score,0,,,0.38057791013405023,
calibration,60,volatility_score,0,,,0.27426588739955143,
calibration,60,liquidity_score,0,,,0.14982170179399004,
calibration,60,options_score,0,,,,
calibration,60,relative_opportunity_score,0,,,,
calibration,60,risk_reward_score,0,,,0.5660572836322391,
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
fb9cc1abbfcca2453eec217b,2026-09-15T20:21:08+00:00,calibration,ELV,BUY,WAIT,67.59,100.0,72.45,-5.422241614795949,-11.50488107857057,,,
fabca3d3e4bba17e1172975c,2026-09-16T05:40:32+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
fabca3d3e4bba17e1172975c,2026-09-16T05:40:32+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,-12.084533312934504,,,
e1338d825a461549ab9e718a,2026-09-16T05:50:47+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
e1338d825a461549ab9e718a,2026-09-16T05:50:47+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,-12.084533312934504,,,
e991d1db51ca3517cd30ca69,2026-09-16T05:54:18+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
e991d1db51ca3517cd30ca69,2026-09-16T05:54:18+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,-12.084533312934504,,,
92e9fb98a9868fa5713aaf9d,2026-09-16T06:00:15+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
92e9fb98a9868fa5713aaf9d,2026-09-16T06:00:15+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,-12.084533312934504,,,
3f6b3bd68f68e3e0a4cb2309,2026-09-16T06:03:42+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
3f6b3bd68f68e3e0a4cb2309,2026-09-16T06:03:42+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,-12.084533312934504,,,
3280fe7e1c09eee6124d715f,2026-09-22T10:54:56+00:00,calibration,VRNS,BUY,WAIT,71.41,100.0,75.7,-1.5901812297277051,,,,
```

## BUY / WAIT / AVOID transition matrix

```csv
partition,baseline_decision,enhanced_decision,predictions
calibration,BUY,BUY,504
calibration,BUY,WAIT,19
calibration,BUY,AVOID,0
calibration,WAIT,BUY,0
calibration,WAIT,WAIT,1843
calibration,WAIT,AVOID,0
calibration,AVOID,BUY,0
calibration,AVOID,WAIT,0
calibration,AVOID,AVOID,285
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
