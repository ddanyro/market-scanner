# Enhanced Scoring forward validation

Generated: 2026-09-27T10:52:09+00:00

## Data coverage

```csv
partition,predictions,execution_eligible_pct,options_pct,options_partial_pct,portfolio_fit_pct,matured_1d,matured_5d,matured_10d,matured_20d,matured_60d
calibration,2888,92.97091412742382,0.0,5.43628808864266,80.22853185595568,2520,1923,715,0,0
holdout_locked,0,,,,,0,0,0,0,0
```

## Gross, net and benchmark alpha

```csv
partition,horizon,metric,n,mean,median,win_rate,average_gain,average_loss,expectancy
calibration,1,gross_return_pct,2343,-0.8311037463965785,-0.7721978264885965,38.45497225778916,2.0436633091125143,-2.6328121746473654,-0.8311037463965785
calibration,1,net_return_pct,313,-3.406927457457263,-2.081818406596427,22.044728434504794,2.1619450257427935,-4.981731561313016,-3.406927457457263
calibration,1,spy_return_pct,2343,0.24119553263741045,0.10900170807000009,50.61886470337175,1.015165675471848,-0.5521740346933095,0.24119553263741045
calibration,1,qqq_return_pct,2343,0.6834754492752984,0.06913851652496916,55.91122492530943,1.7506093106121798,-0.6698114416746676,0.6834754492752984
calibration,1,sector_return_pct,1242,0.18656370200265246,0.008530719416433019,50.1610305958132,1.4268793619989235,-1.0617669218708157,0.18656370200265246
calibration,1,cash_return_pct,2343,0.015344106539990647,0.015412308123874396,100.0,0.015344106539990647,,0.015344106539990647
calibration,1,gross_alpha_spy_pct,2343,-1.072299279033989,-0.8618184488195513,36.40631668800683,2.028800149163657,-2.8476266698075405,-1.072299279033989
calibration,1,net_alpha_spy_pct,313,-3.672077365569978,-2.10462766071475,19.808306709265175,2.2489757311436374,-5.1346482500171655,-3.672077365569978
calibration,1,net_alpha_qqq_pct,313,-3.9695111572247592,-2.447890325586834,21.405750798722046,2.094230358605175,-5.621017992836978,-3.9695111572247592
calibration,1,net_alpha_sector_pct,296,-3.862008538325837,-2.0894753965860815,19.93243243243243,1.2543872463160022,-5.135710442519375,-3.862008538325837
calibration,1,net_alpha_cash_pct,313,-3.4221967053676736,-2.0970512431030226,21.405750798722046,2.2108101980759662,-4.956389642484438,-3.4221967053676736
calibration,5,gross_return_pct,1786,-1.5829893147317005,-2.016718927643768,32.754759238521835,4.597516150132239,-4.593476989124211,-1.5829893147317005
calibration,5,net_return_pct,281,-3.9675965651750706,-2.9543835034436943,24.199288256227756,3.4154670110781247,-6.324630946326327,-3.9675965651750706
calibration,5,spy_return_pct,1786,0.8913778163670244,1.2105812974770869,68.86898096304591,1.4218965679298676,-0.2822517959032938,0.8913778163670244
calibration,5,qqq_return_pct,1786,2.889719427516728,3.3024831992218395,94.96080627099664,3.137279018439503,-1.7754035303168993,2.889719427516728
calibration,5,sector_return_pct,970,0.3009365261087139,0.3475938849169635,52.98969072164949,2.2755641414795695,-1.9248498649014167,0.3009365261087139
calibration,5,cash_return_pct,1786,0.07641159507231991,0.07660773700177703,100.0,0.07641159507231991,,0.07641159507231991
calibration,5,gross_alpha_spy_pct,1786,-2.474367131098725,-2.505706112781847,29.059350503919372,4.228426651188245,-5.220026146889522,-2.474367131098725
calibration,5,net_alpha_spy_pct,281,-4.696781219018564,-3.5206954873407925,20.99644128113879,3.220435351661752,-6.800906343658829,-4.696781219018564
calibration,5,net_alpha_qqq_pct,281,-6.378978076551673,-4.635253934637383,13.523131672597867,3.2754662014149467,-7.8887265644641476,-6.378978076551673
calibration,5,net_alpha_sector_pct,271,-4.476453806461015,-2.886106093227845,16.605166051660518,3.157058321816452,-5.996400911649006,-4.476453806461015
calibration,5,net_alpha_cash_pct,281,-4.043837587818339,-3.0292710873660282,24.199288256227756,3.339139018891668,-6.400844204045009,-4.043837587818339
calibration,10,gross_return_pct,676,-2.4958890298642302,-3.6904743739536894,28.402366863905325,7.2174584588940505,-6.349117785735284,-2.4958890298642302
calibration,10,net_return_pct,173,-2.88219744085763,-4.438800305997008,31.213872832369944,7.631033149529155,-7.652907120528944,-2.88219744085763
calibration,10,spy_return_pct,676,1.2639690956035985,1.174347293359923,100.0,1.2639690956035985,,1.2639690956035985
calibration,10,qqq_return_pct,676,4.266558044059697,4.251870987000683,100.0,4.266558044059697,,4.266558044059697
calibration,10,sector_return_pct,416,-0.14685580453770355,0.1982048149982374,50.96153846153846,2.9579085943751107,-3.3733756700745503,-0.14685580453770355
calibration,10,cash_return_pct,676,0.1509185044422963,0.1524328251811813,100.0,0.1509185044422963,,0.1509185044422963
calibration,10,gross_alpha_spy_pct,676,-3.7598581254678285,-5.074196214241589,26.035502958579883,6.561983096359207,-7.393146235550945,-3.7598581254678285
calibration,10,net_alpha_spy_pct,173,-4.3221572976271405,-5.636385236870611,30.63583815028902,6.425294306550317,-9.068948422805517,-4.3221572976271405
calibration,10,net_alpha_qqq_pct,173,-7.420033615774642,-8.83340270145495,23.699421965317917,4.917153824118853,-11.25203880543853,-7.420033615774642
calibration,10,net_alpha_sector_pct,170,-2.994116406719172,-2.5259132581690853,24.11764705882353,6.564660271622407,-6.032177211463394,-2.994116406719172
calibration,10,net_alpha_cash_pct,173,-3.0335008502838225,-4.591233131178189,31.213872832369944,7.479371161632197,-7.804047813674285,-3.0335008502838225
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
calibration,1,baseline_buy,511,-0.12429041175649409,36.399217221135025,54,-2.3026525301154437,27.77777777777778,54,-2.4639255623169243,42.592592592592595,54,-2.525342511138635,42.592592592592595,54,-2.347147070348296,42.592592592592595,54,-2.317846983078136,27.77777777777778,511,-1.7174650297667984,18.003913894324853,511,1.1426488322483532,63.405088062622305,511,0.0,0.0
calibration,1,enhanced_shadow_buy,492,0.04491491298239081,37.80487804878049,40,-0.019502008572020602,37.5,40,-0.09913480481823882,57.49999999999999,40,-0.0685174538253019,57.49999999999999,40,-0.19179542431570534,57.49999999999999,40,-0.03469498599551106,37.5,492,-1.572415846664271,18.69918699186992,492,1.2755186969071406,65.65040650406505,492,0.0,0.0
calibration,1,enhanced_raw_75,135,-1.1564532368385212,31.851851851851855,62,-0.5116322479391814,33.87096774193548,62,-0.6079704012155807,38.70967741935484,62,-0.4864446441639721,38.70967741935484,62,-0.7238415211108225,35.483870967741936,62,-0.5267808908601653,33.87096774193548,135,-3.208865271325155,18.51851851851852,135,0.9451642595460249,55.55555555555556,135,0.0,0.0
calibration,1,enhanced_adjusted_75,498,0.3718378103162018,53.21285140562249,133,-0.7173840755209868,29.32330827067669,133,-1.071674139522756,26.31578947368421,133,-1.305126864549972,29.32330827067669,133,-0.937928412404639,26.31578947368421,133,-0.7326186134509908,29.32330827067669,498,-1.198772839724725,23.895582329317268,498,1.8748582072128777,79.91967871485943,498,0.0,0.0
calibration,5,baseline_buy,460,-0.6234531573057596,40.869565217391305,50,-1.931502280280042,44.0,50,-2.488163482504279,44.0,50,-3.836738016302636,24.0,50,-1.4872192928629215,26.0,50,-2.0073768314391276,44.0,460,-3.7917061144697675,11.73913043478261,460,3.0030005386032337,90.0,460,-2.5695458318396054,0.0
calibration,5,enhanced_shadow_buy,442,-0.5642936152005541,41.40271493212669,37,-0.14454450729979515,59.45945945945946,37,-0.4730442363923748,59.45945945945946,37,-1.5100238561999764,32.432432432432435,37,0.20637348345437465,35.13513513513514,37,-0.2204094446313889,59.45945945945946,442,-3.6829600248068046,12.217194570135746,442,3.1297924273153583,92.3076923076923,442,-2.632561754627737,0.0
calibration,5,enhanced_raw_75,113,-1.0902006315440413,39.823008849557525,59,-0.469813633429881,52.54237288135594,59,-0.787736064244669,49.152542372881356,59,-1.7359741474038384,32.20338983050847,59,-0.35470793952380686,33.89830508474576,59,-0.5454913639327436,52.54237288135594,113,-4.513490397676213,15.929203539823009,113,3.202487249826857,74.33628318584071,113,-3.070825391978443,0.0
calibration,5,enhanced_adjusted_75,384,0.3643372862333103,48.69791666666667,126,-1.7506875594410498,34.12698412698413,126,-2.4005441284964766,26.984126984126984,126,-3.840465748209338,16.666666666666664,126,-2.1175857256972175,21.428571428571427,126,-1.8268107128298092,34.12698412698413,384,-2.754712612607095,15.885416666666666,384,4.164017898340851,94.53125,384,-3.127198261543643,0.0
calibration,10,baseline_buy,212,-1.4864038264803854,33.0188679245283,40,1.886069872004621,57.49999999999999,40,0.3914291252441112,55.00000000000001,40,-2.7250382962939215,30.0,40,1.5470373170092049,40.0,40,1.734937834740564,57.49999999999999,212,-6.870005242782518,14.150943396226415,212,4.603483159289876,91.0377358490566,212,-5.7484466187999,0.0
calibration,10,enhanced_shadow_buy,205,-1.2770268021470381,34.146341463414636,33,4.6114246244704935,69.6969696969697,33,3.2150687987916,66.66666666666666,33,0.10271459279021695,36.36363636363637,33,3.4030993517317376,48.484848484848484,33,4.460016662496743,69.6969696969697,205,-6.812194833284672,14.634146341463413,205,4.816891105353742,93.65853658536587,205,-5.784231317639507,0.0
calibration,10,enhanced_raw_75,62,2.61975807488992,58.06451612903226,56,2.5136792725448105,57.14285714285714,56,1.0876728532023259,55.35714285714286,56,-2.0323187012477173,37.5,56,1.76570921184445,48.214285714285715,56,2.362454321858102,57.14285714285714,62,-4.019137153714912,19.35483870967742,62,7.760214596307162,100.0,62,-4.741216884831087,0.0
calibration,10,enhanced_adjusted_75,222,2.4849521577705618,57.65765765765766,86,1.0487885719655625,48.837209302325576,86,-0.40769099164153494,47.674418604651166,86,-3.52550674512569,36.04651162790697,86,0.5437887828842625,37.2093023255814,86,0.8975960329379191,48.837209302325576,222,-3.717120358607069,13.513513513513514,222,7.262559469796698,100.0,222,-5.035346812915366,0.0
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
calibration,1,baseline,75-79,250,-4.0995291182581255,-2.762082806315366,14.399999999999999,2.0490366868905214,-5.13386729108687,-4.0995291182581255
calibration,1,baseline,80-84,0,,,,,,
calibration,1,baseline,85-89,0,,,,,,
calibration,1,baseline,90+,54,-2.4639255623169243,-1.5326589743804258,42.592592592592595,1.9040424149607615,-5.704675997071337,-2.4639255623169243
calibration,1,raw,0-49,9,0.9526716118046856,-1.635653061669053,33.33333333333333,7.292733019583067,-2.217359092084505,0.9526716118046856
calibration,1,raw,50-59,13,-4.865749250073437,-0.5917781237302198,30.76923076923077,4.389938816379541,-8.979388390719203,-4.865749250073437
calibration,1,raw,60-69,142,-6.247970415943748,-5.066480409554554,11.267605633802818,1.788563703139153,-7.268482685033639,-6.247970415943748
calibration,1,raw,70-74,87,-1.9514201809116392,-1.742285144192715,17.24137931034483,2.1514408733840993,-2.8061829005565846,-1.9514201809116392
calibration,1,raw,75-79,62,-0.6079704012155807,-1.2152276610414454,38.70967741935484,1.6295795273187583,-2.0211598297635835,-0.6079704012155807
calibration,1,raw,80-84,0,,,,,,
calibration,1,raw,85-89,0,,,,,,
calibration,1,raw,90+,0,,,,,,
calibration,1,adjusted,0-49,9,0.9526716118046856,-1.635653061669053,33.33333333333333,7.292733019583067,-2.217359092084505,0.9526716118046856
calibration,1,adjusted,50-59,8,1.920157241309937,1.2946865629019415,50.0,4.389938816379541,-0.549624333759666,1.920157241309937
calibration,1,adjusted,60-69,40,-10.995609388922194,-5.824435758528706,0.0,,-10.995609388922194,-10.995609388922194
calibration,1,adjusted,70-74,123,-4.8043779003797615,-3.902111740105438,16.260162601626014,1.9889955304617932,-6.123479537436373,-4.8043779003797615
calibration,1,adjusted,75-79,101,-1.4730579846227096,-1.2870567451621204,14.85148514851485,2.0365331334222767,-2.0851959703282303,-1.4730579846227096
calibration,1,adjusted,80-84,32,0.1951936215739729,0.22252073468191064,62.5,1.4835316698034062,-1.9520364588084151,0.1951936215739729
calibration,1,adjusted,85-89,0,,,,,,
calibration,1,adjusted,90+,0,,,,,,
calibration,5,baseline,0-49,0,,,,,,
calibration,5,baseline,50-59,9,5.331020449401777,6.323941978104684,100.0,5.331020449401777,,5.331020449401777
calibration,5,baseline,60-69,0,,,,,,
calibration,5,baseline,70-74,0,,,,,,
calibration,5,baseline,75-79,222,-5.600750146232516,-3.662551224860178,12.612612612612612,3.5899081032893005,-6.9272369038954595,-5.600750146232516
calibration,5,baseline,80-84,0,,,,,,
calibration,5,baseline,85-89,0,,,,,,
calibration,5,baseline,90+,50,-2.488163482504279,-1.6030679832651262,44.0,1.8867761277875892,-5.9256160334478905,-2.488163482504279
calibration,5,raw,0-49,9,5.331020449401777,6.323941978104684,100.0,5.331020449401777,,5.331020449401777
calibration,5,raw,50-59,6,-15.041015870985825,-12.239169682416694,16.666666666666664,5.683429225678907,-19.185904890318774,-15.041015870985825
calibration,5,raw,60-69,124,-7.2093486533468445,-5.819496044658447,12.096774193548388,4.361795237749523,-8.801707904415153,-7.2093486533468445
calibration,5,raw,70-74,83,-4.0613608500900416,-3.443099770630134,6.024096385542169,1.320480343341476,-4.406350670181806,-4.0613608500900416
calibration,5,raw,75-79,59,-0.787736064244669,-0.0697432738322592,49.152542372881356,2.217715248096491,-3.693005666174457,-0.787736064244669
calibration,5,raw,80-84,0,,,,,,
calibration,5,raw,85-89,0,,,,,,
calibration,5,raw,90+,0,,,,,,
calibration,5,adjusted,0-49,9,5.331020449401777,6.323941978104684,100.0,5.331020449401777,,5.331020449401777
calibration,5,adjusted,50-59,1,5.683429225678907,5.683429225678907,100.0,5.683429225678907,,5.683429225678907
calibration,5,adjusted,60-69,37,-12.067264927594536,-8.613522074090584,2.7027027027027026,3.0672009047650444,-12.48766675627119,-12.067264927594536
calibration,5,adjusted,70-74,108,-5.782414567619979,-5.258900856963094,12.962962962962962,4.45426626153413,-7.307026606004633,-5.782414567619979
calibration,5,adjusted,75-79,97,-3.025058809297759,-3.167853582291407,14.432989690721648,2.7794861263077277,-4.004138677954106,-3.025058809297759
calibration,5,adjusted,80-84,29,-0.31165019616114953,0.7860842697011732,68.96551724137932,1.6001669071598719,-4.560132647985642,-0.31165019616114953
calibration,5,adjusted,85-89,0,,,,,,
calibration,5,adjusted,90+,0,,,,,,
calibration,10,baseline,0-49,0,,,,,,
calibration,10,baseline,50-59,3,7.4894693503487515,7.4894693503487515,100.0,7.4894693503487515,,7.4894693503487515
calibration,10,baseline,60-69,0,,,,,,
calibration,10,baseline,70-74,0,,,,,,
calibration,10,baseline,75-79,130,-6.0450675811562,-6.972950522920805,21.53846153846154,4.47952656627718,-8.934171856922227,-6.0450675811562
calibration,10,baseline,80-84,0,,,,,,
calibration,10,baseline,85-89,0,,,,,,
calibration,10,baseline,90+,40,0.3914291252441112,1.0042993627665613,55.00000000000001,8.756611197289068,-9.832682296144167,0.3914291252441112
calibration,10,raw,0-49,3,7.4894693503487515,7.4894693503487515,100.0,7.4894693503487515,,7.4894693503487515
calibration,10,raw,50-59,1,-18.215448157666938,-18.215448157666938,0.0,,-18.215448157666938,-18.215448157666938
calibration,10,raw,60-69,72,-9.153931426737255,-9.587903222217474,12.5,4.4020868202925865,-11.09050546202723,-9.153931426737255
calibration,10,raw,70-74,41,-3.7515314496859156,-5.613147599356931,24.390243902439025,3.771157709148075,-6.17820537189043,-3.7515314496859156
calibration,10,raw,75-79,56,1.0876728532023259,1.0042993627665613,55.35714285714286,7.765865539419567,-7.19328607770705,1.0876728532023259
calibration,10,raw,80-84,0,,,,,,
calibration,10,raw,85-89,0,,,,,,
calibration,10,raw,90+,0,,,,,,
calibration,10,adjusted,0-49,3,7.4894693503487515,7.4894693503487515,100.0,7.4894693503487515,,7.4894693503487515
calibration,10,adjusted,50-59,0,,,,,,
calibration,10,adjusted,60-69,13,-14.117881144370898,-8.26571501765368,23.076923076923077,1.9760384591206492,-18.946057025418362,-14.117881144370898
calibration,10,adjusted,70-74,71,-7.769123103979547,-9.587903222217474,8.450704225352112,5.615111000878556,-9.004590867504911,-7.769123103979547
calibration,10,adjusted,75-79,60,-2.470706871307338,-4.793092183834324,35.0,5.874255400683412,-6.964148094686971,-2.470706871307338
calibration,10,adjusted,80-84,26,4.353114884510318,1.0042993627665613,76.92307692307693,7.754702269956783,-6.9855097336445615,4.353114884510318
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
calibration,OPTIONS_DATA_PARTIAL,contracts_only,7,89.28571428571429,73.46857142857142,76.0757142857143,100.0,4,2.7445426049249013,4,2.414249544618571,4,14.505105177147001,0,,0,
calibration,OPTIONS_DATA_PARTIAL,partial,58,82.75862068965517,72.34362068965518,74.82689655172416,100.0,24,-1.6943205052151893,15,-2.238598398340116,12,-3.8511844706078624,0,,0,
calibration,OPTIONS_DATA_PARTIAL,quote_only,92,84.78260869565217,73.01739130434781,75.57423913043479,100.0,56,-3.6028966242117457,56,-3.78185198065612,37,-2.835972901624091,0,,0,
calibration,OPTIONS_NOT_ELIGIBLE,unavailable,1616,72.4319306930693,61.63764232673267,62.93097772277227,66.64603960396039,25,0.7928833187843535,17,5.883036033254516,3,7.4894693503487515,0,,0,
calibration,OPTIONS_UNAVAILABLE,unavailable,1115,79.61883408071749,69.6673273542601,71.85189237668162,97.13004484304932,212,-4.442678232069822,196,-5.804859423985415,117,-5.7869814550576395,0,,0,
```

Availability is reported separately from the formula value. Missing options
data is never classified as an observed score of 50.

## Portfolio Fit cohorts

```csv
partition,cohort,predictions,raw_score_mean,adjusted_score_mean,net_alpha_spy_1d_n,net_alpha_spy_1d_mean,net_alpha_spy_1d_median,net_alpha_spy_1d_win_rate,net_alpha_spy_1d_average_gain,net_alpha_spy_1d_average_loss,net_alpha_spy_1d_expectancy,net_alpha_spy_5d_n,net_alpha_spy_5d_mean,net_alpha_spy_5d_median,net_alpha_spy_5d_win_rate,net_alpha_spy_5d_average_gain,net_alpha_spy_5d_average_loss,net_alpha_spy_5d_expectancy,net_alpha_spy_10d_n,net_alpha_spy_10d_mean,net_alpha_spy_10d_median,net_alpha_spy_10d_win_rate,net_alpha_spy_10d_average_gain,net_alpha_spy_10d_average_loss,net_alpha_spy_10d_expectancy,net_alpha_spy_20d_n,net_alpha_spy_20d_mean,net_alpha_spy_20d_median,net_alpha_spy_20d_win_rate,net_alpha_spy_20d_average_gain,net_alpha_spy_20d_average_loss,net_alpha_spy_20d_expectancy,net_alpha_spy_60d_n,net_alpha_spy_60d_mean,net_alpha_spy_60d_median,net_alpha_spy_60d_win_rate,net_alpha_spy_60d_average_gain,net_alpha_spy_60d_average_loss,net_alpha_spy_60d_expectancy
calibration,missing,571,65.96509632224166,65.96509632224166,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,other_observed,1048,59.839465648854954,57.38692748091603,87,-0.2054262288018064,-1.2152276610414454,37.93103448275862,2.6925191542167433,-1.9763928517575868,-0.2054262288018064,76,0.7044103259854119,0.7860842697011732,60.526315789473685,3.5722903208722836,-3.693005666174457,0.7044103259854119,59,1.413187929328415,1.0042993627665613,57.6271186440678,7.741477640383905,-7.19328607770705,1.413187929328415,0,,,,,,,0,,,,,,
calibration,raw_high_fit_weak,25,75.14040000000001,69.37280000000001,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,raw_medium_fit_good,1244,69.49917202572347,74.05509646302251,234,-4.852997234977602,-3.6802345298898302,13.247863247863249,1.9641494306770297,-5.894039336629295,-4.852997234977602,212,-6.259347679358849,-3.8379236503182153,9.433962264150944,3.601466514147512,-7.286515824515761,-6.259347679358849,114,-7.290450002805894,-7.517704836200489,16.666666666666664,4.070018867058632,-9.562543776778798,-7.290450002805894,0,,,,,,,0,,,,,,
```

## Component contribution and redundancy

```csv
partition,horizon,component,n,pearson_forward_alpha,spearman_forward_alpha,max_abs_component_correlation,incremental_r2
calibration,1,technical_score,321,0.005775237965109638,0.04666163786896467,0.252120335874734,
calibration,1,momentum_score,321,-0.1682089785470996,-0.23830611938347104,0.5656144004001342,
calibration,1,research_score,321,-0.1201651547523459,-0.029451644672129056,0.40029584711620164,
calibration,1,volatility_score,321,-0.08443503799923989,-0.011066130807717876,0.26168409091930445,
calibration,1,liquidity_score,321,0.6234776189026973,0.6496965899846113,0.13292852148417533,
calibration,1,options_score,0,,,,
calibration,1,relative_opportunity_score,321,,,,
calibration,1,risk_reward_score,321,-0.2217255441024103,-0.24219535849296378,0.5656144004001342,
calibration,5,technical_score,288,-0.05945126839190908,-0.044882155123428934,0.252120335874734,
calibration,5,momentum_score,288,-0.29462695852806087,-0.33397579730341453,0.5656144004001342,
calibration,5,research_score,288,-0.13689782077877818,-0.03855403288973415,0.40029584711620164,
calibration,5,volatility_score,288,-0.1162830620187472,-0.038131898355697615,0.26168409091930445,
calibration,5,liquidity_score,288,0.5007201873910895,0.5167631590494977,0.13292852148417533,
calibration,5,options_score,0,,,,
calibration,5,relative_opportunity_score,288,,,,
calibration,5,risk_reward_score,288,-0.2622945806036751,-0.27051834032089855,0.5656144004001342,
calibration,10,technical_score,173,0.20174246020820652,0.13724803365875998,0.252120335874734,
calibration,10,momentum_score,173,-0.1964753969216459,-0.1768844040455885,0.5656144004001342,
calibration,10,research_score,173,0.012307965107313785,0.12088430551723875,0.40029584711620164,
calibration,10,volatility_score,173,-0.33075654647747854,-0.35184368871845517,0.26168409091930445,
calibration,10,liquidity_score,173,0.5249752938884005,0.5638294297508469,0.13292852148417533,
calibration,10,options_score,0,,,,
calibration,10,relative_opportunity_score,173,,,,
calibration,10,risk_reward_score,173,-0.07302861655390845,-0.0442010263988074,0.5656144004001342,
calibration,20,technical_score,0,,,0.252120335874734,
calibration,20,momentum_score,0,,,0.5656144004001342,
calibration,20,research_score,0,,,0.40029584711620164,
calibration,20,volatility_score,0,,,0.26168409091930445,
calibration,20,liquidity_score,0,,,0.13292852148417533,
calibration,20,options_score,0,,,,
calibration,20,relative_opportunity_score,0,,,,
calibration,20,risk_reward_score,0,,,0.5656144004001342,
calibration,60,technical_score,0,,,0.252120335874734,
calibration,60,momentum_score,0,,,0.5656144004001342,
calibration,60,research_score,0,,,0.40029584711620164,
calibration,60,volatility_score,0,,,0.26168409091930445,
calibration,60,liquidity_score,0,,,0.13292852148417533,
calibration,60,options_score,0,,,,
calibration,60,relative_opportunity_score,0,,,,
calibration,60,risk_reward_score,0,,,0.5656144004001342,
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
5522e100effd8a5697d20573,2026-09-10T21:10:03+00:00,calibration,TRGP,BUY,WAIT,73.1,100.0,77.13,-3.6307928684466053,-5.172093404289288,-6.681789391928969,,
53c26794356af012cc307291,2026-09-11T06:44:58+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-19.383811230653382,-18.190478941420352,-23.970295596335056,,
8ca424c3afa2faff80cd5fa8,2026-09-11T08:54:52+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186609831009546,-5.896414748807773,-11.957604072418867,,
3457725c926d4c9bca6c86ef,2026-09-11T09:29:41+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186609831009546,-5.896414748807773,-11.957604072418867,,
62964736889913e1a2f9310e,2026-09-11T11:00:53+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186609831009546,-5.896414748807773,-11.957604072418867,,
f210d637d4e1bb82d574ae0b,2026-09-11T11:21:56+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186609831009546,-5.896414748807773,-11.957604072418867,,
67f32e63bb66249fa1c7fee3,2026-09-11T11:38:56+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186609831009546,-5.896414748807773,-11.957604072418867,,
fb9cc1abbfcca2453eec217b,2026-09-15T20:21:08+00:00,calibration,ELV,BUY,WAIT,67.59,100.0,72.45,-5.422241614795949,-10.599004550121446,,,
fabca3d3e4bba17e1172975c,2026-09-16T05:40:32+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
fabca3d3e4bba17e1172975c,2026-09-16T05:40:32+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,-8.692377347765227,,,
e1338d825a461549ab9e718a,2026-09-16T05:50:47+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
e1338d825a461549ab9e718a,2026-09-16T05:50:47+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,-8.692377347765227,,,
e991d1db51ca3517cd30ca69,2026-09-16T05:54:18+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
e991d1db51ca3517cd30ca69,2026-09-16T05:54:18+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,-8.692377347765227,,,
92e9fb98a9868fa5713aaf9d,2026-09-16T06:00:15+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
92e9fb98a9868fa5713aaf9d,2026-09-16T06:00:15+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,-8.692377347765227,,,
3f6b3bd68f68e3e0a4cb2309,2026-09-16T06:03:42+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
3f6b3bd68f68e3e0a4cb2309,2026-09-16T06:03:42+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,-8.692377347765227,,,
3280fe7e1c09eee6124d715f,2026-09-22T10:54:56+00:00,calibration,VRNS,BUY,WAIT,71.41,100.0,75.7,-1.5901812297277167,,,,
0caf45bef2ea59a325fb5a5c,2026-09-26T07:09:32+00:00,calibration,BIIB,BUY,WAIT,71.26,100.0,75.57,,,,,
```

## BUY / WAIT / AVOID transition matrix

```csv
partition,baseline_decision,enhanced_decision,predictions
calibration,BUY,BUY,543
calibration,BUY,WAIT,20
calibration,BUY,AVOID,0
calibration,WAIT,BUY,0
calibration,WAIT,WAIT,2008
calibration,WAIT,AVOID,0
calibration,AVOID,BUY,0
calibration,AVOID,WAIT,0
calibration,AVOID,AVOID,317
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
