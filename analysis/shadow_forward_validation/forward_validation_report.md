# Enhanced Scoring forward validation

Generated: 2026-09-26T08:22:57+00:00

## Data coverage

```csv
partition,predictions,execution_eligible_pct,options_pct,options_partial_pct,portfolio_fit_pct,matured_1d,matured_5d,matured_10d,matured_20d,matured_60d
calibration,2750,92.72727272727272,0.0,5.709090909090909,79.78181818181818,2433,1713,498,0,0
holdout_locked,0,,,,,0,0,0,0,0
```

## Gross, net and benchmark alpha

```csv
partition,horizon,metric,n,mean,median,win_rate,average_gain,average_loss,expectancy
calibration,1,gross_return_pct,2263,-0.7782712990244893,-0.7042286354984384,38.93062306672558,2.0537501399287508,-2.5892544038938716,-0.7782712990244893
calibration,1,net_return_pct,310,-3.4262637455138476,-2.2469089088789773,22.258064516129032,2.1619450257427935,-5.02620733562467,-3.4262637455138476
calibration,1,spy_return_pct,2263,0.27054431193948514,0.24789671462555063,52.408307556341136,1.015165675471848,-0.5494379881063667,0.27054431193948514
calibration,1,qqq_return_pct,2263,0.7128399820063621,0.09091013277680027,57.00397702165267,1.776026804193567,-0.6967293917053481,0.7128399820063621
calibration,1,sector_return_pct,1242,0.18656370200265246,0.008530719416433019,50.1610305958132,1.4268793619989235,-1.0617669218708157,0.18656370200265246
calibration,1,cash_return_pct,2263,0.015335807634299408,0.015412308123874396,100.0,0.015335807634299408,,0.015335807634299408
calibration,1,gross_alpha_spy_pct,2263,-1.0488156109639744,-0.8417835849050981,36.809544851966415,2.027152377979721,-2.8406207401878194,-1.0488156109639744
calibration,1,net_alpha_spy_pct,310,-3.7018867130716533,-2.1331375897688227,20.0,2.2489757311436374,-5.189602324125476,-3.7018867130716533
calibration,1,net_alpha_qqq_pct,310,-3.9947747093698993,-2.710624348754663,21.612903225806452,2.094230358605175,-5.673636189017349,-3.9947747093698993
calibration,1,net_alpha_sector_pct,296,-3.862008538325837,-2.0894753965860815,19.93243243243243,1.2543872463160022,-5.135710442519375,-3.862008538325837
calibration,1,net_alpha_cash_pct,310,-3.4415307962587267,-2.262143569192856,21.612903225806452,2.2108101980759662,-4.999995185643191,-3.4415307962587267
calibration,5,gross_return_pct,1609,-1.3121111668601597,-1.754385730089436,33.99627097576135,4.448480195731787,-4.279195418590664,-1.3121111668601597
calibration,5,net_return_pct,277,-4.169550868432181,-2.9543835034436943,23.104693140794225,3.00282501580927,-6.324630946326327,-4.169550868432181
calibration,5,spy_return_pct,1609,0.8290706893790737,1.1473904879768293,65.44437538844002,1.4158658477997732,-0.2822517959032938,0.8290706893790737
calibration,5,qqq_return_pct,1609,2.7660099849562227,3.3024831992218395,94.40646364201368,3.035086493431918,-1.7754035303168993,2.7660099849562227
calibration,5,sector_return_pct,970,0.3009365261087139,0.3475938849169635,52.98969072164949,2.2755641414795695,-1.9248498649014167,0.3009365261087139
calibration,5,cash_return_pct,1609,0.07630935171334577,0.07660773700177703,100.0,0.07630935171334577,,0.07630935171334577
calibration,5,gross_alpha_spy_pct,1609,-2.1411818562392337,-2.260232996224454,30.018645121193288,4.125411572841309,-4.829249907967388,-2.1411818562392337
calibration,5,net_alpha_spy_pct,277,-4.883092174391279,-3.6235112159675,19.855595667870034,2.8579031997431956,-6.800906343658829,-4.883092174391279
calibration,5,net_alpha_qqq_pct,277,-6.546734872083831,-4.635253934637383,12.274368231046932,3.04455869404608,-7.8887265644641476,-6.546734872083831
calibration,5,net_alpha_sector_pct,271,-4.476453806461015,-2.886106093227845,16.605166051660518,3.157058321816452,-5.996400911649006,-4.476453806461015
calibration,5,net_alpha_cash_pct,277,-4.245776389792019,-3.0292710873660282,23.104693140794225,2.926558679518709,-6.400844204045009,-4.245776389792019
calibration,10,gross_return_pct,494,-1.5843528397735211,-2.6983848591862203,32.59109311740891,6.863804872180172,-5.668897559366748,-1.5843528397735211
calibration,10,net_return_pct,170,-3.085950630585271,-4.857261281012856,30.0,7.570281179283301,-7.652907120528944,-3.085950630585271
calibration,10,spy_return_pct,494,1.223265642147575,1.174347293359923,100.0,1.223265642147575,,1.223265642147575
calibration,10,qqq_return_pct,494,4.204144121914402,4.251870987000683,100.0,4.204144121914402,,4.204144121914402
calibration,10,sector_return_pct,416,-0.14685580453770355,0.1982048149982374,50.96153846153846,2.9579085943751107,-3.3733756700745503,-0.14685580453770355
calibration,10,cash_return_pct,494,0.15086479986002838,0.1524328251811813,100.0,0.15086479986002838,,0.15086479986002838
calibration,10,gross_alpha_spy_pct,494,-2.807618481921096,-3.783713522191068,29.75708502024291,6.229644182991983,-6.636084221812227,-2.807618481921096
calibration,10,net_alpha_spy_pct,170,-4.530597767885539,-6.031608574372779,29.411764705882355,6.36144380392241,-9.068948422805517,-4.530597767885539
calibration,10,net_alpha_qqq_pct,170,-7.628833249994924,-9.10913226801354,22.35294117647059,4.957038679440763,-11.25203880543853,-7.628833249994924
calibration,10,net_alpha_sector_pct,170,-2.994116406719172,-2.5259132581690853,24.11764705882353,6.564660271622407,-6.032177211463394,-2.994116406719172
calibration,10,net_alpha_cash_pct,170,-3.2372341091451986,-5.009694106194037,30.0,7.418664534756002,-7.804047813674285,-3.2372341091451986
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
calibration,5,baseline_buy,444,-0.5458252404241004,41.21621621621622,50,-1.931502280280042,44.0,50,-2.488163482504279,44.0,50,-3.836738016302636,24.0,50,-1.4872192928629215,26.0,50,-2.0073768314391276,44.0,444,-3.718171567324141,12.162162162162163,444,3.0567544891930707,89.63963963963964,444,-2.525333938760813,0.0
calibration,5,enhanced_shadow_buy,426,-0.48116369085985006,41.78403755868544,37,-0.14454450729979515,59.45945945945946,37,-0.4730442363923748,59.45945945945946,37,-1.5100238561999764,32.432432432432435,37,0.20637348345437465,35.13513513513514,37,-0.2204094446313889,59.45945945945946,426,-3.6022340239446793,12.676056338028168,426,3.1905798082573336,92.01877934272301,426,-2.5888485486127752,0.0
calibration,5,enhanced_raw_75,101,-0.4911659970702899,44.554455445544555,59,-0.469813633429881,52.54237288135594,59,-0.787736064244669,49.152542372881356,59,-1.7359741474038384,32.20338983050847,59,-0.35470793952380686,33.89830508474576,59,-0.5454913639327436,52.54237288135594,101,-3.8728365387040613,17.82178217821782,101,3.7623193020148897,83.16831683168317,101,-3.1672400975232717,0.0
calibration,5,enhanced_adjusted_75,382,0.39834991847378887,48.952879581151834,126,-1.7506875594410498,34.12698412698413,126,-2.4005441284964766,26.984126984126984,126,-3.840465748209338,16.666666666666664,126,-2.1175857256972175,21.428571428571427,126,-1.8268107128298092,34.12698412698413,382,-2.7172730955141557,15.968586387434556,382,4.193721827247116,95.02617801047121,382,-3.131742048496003,0.0
calibration,10,baseline_buy,112,2.241645215408536,60.71428571428571,40,1.886069872004621,57.49999999999999,40,0.3914291252441112,55.00000000000001,40,-2.7250382962939215,30.0,40,1.5470373170092049,40.0,40,1.734937834740564,57.49999999999999,112,-4.479471023726114,26.785714285714285,112,7.258698670883933,83.03571428571429,112,-4.353228022288211,0.0
calibration,10,enhanced_shadow_buy,105,2.8989655323757595,64.76190476190476,33,4.6114246244704935,69.6969696969697,33,3.2150687987916,66.66666666666666,33,0.10271459279021695,36.36363636363637,33,3.4030993517317376,48.484848484848484,33,4.460016662496743,69.6969696969697,105,-4.207234133436085,28.57142857142857,105,7.85236664730537,87.61904761904762,105,-4.330078813588568,0.0
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
calibration,1,baseline,75-79,247,-4.1421333813495576,-2.762082806315366,14.5748987854251,2.0490366868905214,-5.1984467579213245,-4.1421333813495576
calibration,1,baseline,80-84,0,,,,,,
calibration,1,baseline,85-89,0,,,,,,
calibration,1,baseline,90+,54,-2.4639255623169243,-1.5326589743804258,42.592592592592595,1.9040424149607615,-5.704675997071337,-2.4639255623169243
calibration,1,raw,0-49,9,0.9526716118046856,-1.635653061669053,33.33333333333333,7.292733019583067,-2.217359092084505,0.9526716118046856
calibration,1,raw,50-59,10,-6.147940587976402,-3.1526484826768915,40.0,4.389938816379541,-13.173193524213694,-6.147940587976402
calibration,1,raw,60-69,142,-6.247970415943748,-5.066480409554554,11.267605633802818,1.788563703139153,-7.268482685033639,-6.247970415943748
calibration,1,raw,70-74,87,-1.9514201809116392,-1.742285144192715,17.24137931034483,2.1514408733840993,-2.8061829005565846,-1.9514201809116392
calibration,1,raw,75-79,62,-0.6079704012155807,-1.2152276610414454,38.70967741935484,1.6295795273187583,-2.0211598297635835,-0.6079704012155807
calibration,1,raw,80-84,0,,,,,,
calibration,1,raw,85-89,0,,,,,,
calibration,1,raw,90+,0,,,,,,
calibration,1,adjusted,0-49,9,0.9526716118046856,-1.635653061669053,33.33333333333333,7.292733019583067,-2.217359092084505,0.9526716118046856
calibration,1,adjusted,50-59,5,3.427318460334032,4.849073058622091,80.0,4.389938816379541,-0.42316296384800456,3.427318460334032
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
calibration,5,baseline,75-79,221,-5.651809781399536,-3.662551224860178,12.217194570135746,3.5123702839415376,-6.9272369038954595,-5.651809781399536
calibration,5,baseline,80-84,0,,,,,,
calibration,5,baseline,85-89,0,,,,,,
calibration,5,baseline,90+,50,-2.488163482504279,-1.6030679832651262,44.0,1.8867761277875892,-5.9256160334478905,-2.488163482504279
calibration,5,raw,0-49,6,3.4736005846878846,3.473600584687884,100.0,3.4736005846878846,,3.4736005846878846
calibration,5,raw,50-59,5,-19.185904890318774,-15.864817290742806,0.0,,-19.185904890318774,-19.185904890318774
calibration,5,raw,60-69,124,-7.2093486533468445,-5.819496044658447,12.096774193548388,4.361795237749523,-8.801707904415153,-7.2093486533468445
calibration,5,raw,70-74,83,-4.0613608500900416,-3.443099770630134,6.024096385542169,1.320480343341476,-4.406350670181806,-4.0613608500900416
calibration,5,raw,75-79,59,-0.787736064244669,-0.0697432738322592,49.152542372881356,2.217715248096491,-3.693005666174457,-0.787736064244669
calibration,5,raw,80-84,0,,,,,,
calibration,5,raw,85-89,0,,,,,,
calibration,5,raw,90+,0,,,,,,
calibration,5,adjusted,0-49,6,3.4736005846878846,3.473600584687884,100.0,3.4736005846878846,,3.4736005846878846
calibration,5,adjusted,50-59,0,,,,,,
calibration,5,adjusted,60-69,37,-12.067264927594536,-8.613522074090584,2.7027027027027026,3.0672009047650444,-12.48766675627119,-12.067264927594536
calibration,5,adjusted,70-74,108,-5.782414567619979,-5.258900856963094,12.962962962962962,4.45426626153413,-7.307026606004633,-5.782414567619979
calibration,5,adjusted,75-79,97,-3.025058809297759,-3.167853582291407,14.432989690721648,2.7794861263077277,-4.004138677954106,-3.025058809297759
calibration,5,adjusted,80-84,29,-0.31165019616114953,0.7860842697011732,68.96551724137932,1.6001669071598719,-4.560132647985642,-0.31165019616114953
calibration,5,adjusted,85-89,0,,,,,,
calibration,5,adjusted,90+,0,,,,,,
calibration,10,baseline,0-49,0,,,,,,
calibration,10,baseline,50-59,0,,,,,,
calibration,10,baseline,60-69,0,,,,,,
calibration,10,baseline,70-74,0,,,,,,
calibration,10,baseline,75-79,130,-6.0450675811562,-6.972950522920805,21.53846153846154,4.47952656627718,-8.934171856922227,-6.0450675811562
calibration,10,baseline,80-84,0,,,,,,
calibration,10,baseline,85-89,0,,,,,,
calibration,10,baseline,90+,40,0.3914291252441112,1.0042993627665613,55.00000000000001,8.756611197289068,-9.832682296144167,0.3914291252441112
calibration,10,raw,0-49,0,,,,,,
calibration,10,raw,50-59,1,-18.215448157666938,-18.215448157666938,0.0,,-18.215448157666938,-18.215448157666938
calibration,10,raw,60-69,72,-9.153931426737255,-9.587903222217474,12.5,4.4020868202925865,-11.09050546202723,-9.153931426737255
calibration,10,raw,70-74,41,-3.7515314496859156,-5.613147599356931,24.390243902439025,3.771157709148075,-6.17820537189043,-3.7515314496859156
calibration,10,raw,75-79,56,1.0876728532023259,1.0042993627665613,55.35714285714286,7.765865539419567,-7.19328607770705,1.0876728532023259
calibration,10,raw,80-84,0,,,,,,
calibration,10,raw,85-89,0,,,,,,
calibration,10,raw,90+,0,,,,,,
calibration,10,adjusted,0-49,0,,,,,,
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
calibration,OPTIONS_NOT_ELIGIBLE,unavailable,1550,73.01612903225806,61.790058064516124,63.100445161290324,65.6774193548387,22,0.9817007882181589,11,4.769210308968247,0,,0,,0,
calibration,OPTIONS_UNAVAILABLE,unavailable,1043,79.43432406519655,69.56692233940555,71.74041227229147,97.69894534995206,212,-4.442678232069822,196,-5.804859423985416,117,-5.786981455057641,0,,0,
```

Availability is reported separately from the formula value. Missing options
data is never classified as an observed score of 50.

## Portfolio Fit cohorts

```csv
partition,cohort,predictions,raw_score_mean,adjusted_score_mean,net_alpha_spy_1d_n,net_alpha_spy_1d_mean,net_alpha_spy_1d_median,net_alpha_spy_1d_win_rate,net_alpha_spy_1d_average_gain,net_alpha_spy_1d_average_loss,net_alpha_spy_1d_expectancy,net_alpha_spy_5d_n,net_alpha_spy_5d_mean,net_alpha_spy_5d_median,net_alpha_spy_5d_win_rate,net_alpha_spy_5d_average_gain,net_alpha_spy_5d_average_loss,net_alpha_spy_5d_expectancy,net_alpha_spy_10d_n,net_alpha_spy_10d_mean,net_alpha_spy_10d_median,net_alpha_spy_10d_win_rate,net_alpha_spy_10d_average_gain,net_alpha_spy_10d_average_loss,net_alpha_spy_10d_expectancy,net_alpha_spy_20d_n,net_alpha_spy_20d_mean,net_alpha_spy_20d_median,net_alpha_spy_20d_win_rate,net_alpha_spy_20d_average_gain,net_alpha_spy_20d_average_loss,net_alpha_spy_20d_expectancy,net_alpha_spy_60d_n,net_alpha_spy_60d_mean,net_alpha_spy_60d_median,net_alpha_spy_60d_win_rate,net_alpha_spy_60d_average_gain,net_alpha_spy_60d_average_loss,net_alpha_spy_60d_expectancy
calibration,missing,556,66.00203237410072,66.00203237410072,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,other_observed,989,59.94431749241658,57.53064711830131,84,-0.1916279468400773,-1.2152276610414454,39.285714285714285,2.6925191542167433,-2.057840776935667,-0.1916279468400773,70,0.08549836583164656,0.7860842697011732,57.14285714285714,2.9193763898362244,-3.693005666174457,0.08549836583164656,56,1.0876728532023259,1.0042993627665613,55.35714285714286,7.765865539419567,-7.19328607770705,1.0876728532023259,0,,,,,,,0,,,,,,
calibration,raw_high_fit_weak,25,75.14040000000001,69.37280000000001,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,raw_medium_fit_good,1180,69.40688983050848,73.97564406779662,234,-4.852997234977602,-3.6802345298898302,13.247863247863249,1.9641494306770297,-5.894039336629295,-4.852997234977602,212,-6.259347679358849,-3.8379236503182153,9.433962264150944,3.601466514147512,-7.286515824515761,-6.259347679358849,114,-7.290450002805894,-7.517704836200489,16.666666666666664,4.070018867058632,-9.562543776778798,-7.290450002805894,0,,,,,,,0,,,,,,
```

## Component contribution and redundancy

```csv
partition,horizon,component,n,pearson_forward_alpha,spearman_forward_alpha,max_abs_component_correlation,incremental_r2
calibration,1,technical_score,318,0.0070074523694187265,0.0476395491829455,0.21544275960461232,
calibration,1,momentum_score,318,-0.1629446908726787,-0.23047964947470007,0.5672947168300564,
calibration,1,research_score,318,-0.11227903165339577,-0.015299516747020106,0.3902255998385608,
calibration,1,volatility_score,318,-0.08717314137852933,-0.015975511279707092,0.26631421498492225,
calibration,1,liquidity_score,318,0.6231999184354087,0.6540912216094003,0.14520235574068727,
calibration,1,options_score,0,,,,
calibration,1,relative_opportunity_score,318,,,,
calibration,1,risk_reward_score,318,-0.2171671512625816,-0.23279475043351983,0.5672947168300563,
calibration,5,technical_score,282,0.006400389149426634,0.01763977708886445,0.21544275960461232,
calibration,5,momentum_score,282,-0.24302568660724028,-0.29232338301519717,0.5672947168300564,
calibration,5,research_score,282,-0.04526506077875929,0.030137061285887255,0.3902255998385608,
calibration,5,volatility_score,282,-0.1419022752060798,-0.07151097965249643,0.26631421498492225,
calibration,5,liquidity_score,282,0.5114848053852133,0.5454475324465673,0.14520235574068727,
calibration,5,options_score,0,,,,
calibration,5,relative_opportunity_score,282,,,,
calibration,5,risk_reward_score,282,-0.1880267621694291,-0.22023426884266536,0.5672947168300563,
calibration,10,technical_score,170,0.2815168580574372,0.202988287291653,0.21544275960461232,
calibration,10,momentum_score,170,-0.15161786391879195,-0.13481338043605046,0.5672947168300564,
calibration,10,research_score,170,0.09193678304786901,0.1739052268056878,0.3902255998385608,
calibration,10,volatility_score,170,-0.35032298345556656,-0.38826394409424186,0.26631421498492225,
calibration,10,liquidity_score,170,0.5376645806612715,0.592264367939793,0.14520235574068727,
calibration,10,options_score,0,,,,
calibration,10,relative_opportunity_score,170,,,,
calibration,10,risk_reward_score,170,-0.005503318469233192,0.007007280668612272,0.5672947168300563,
calibration,20,technical_score,0,,,0.21544275960461232,
calibration,20,momentum_score,0,,,0.5672947168300564,
calibration,20,research_score,0,,,0.3902255998385608,
calibration,20,volatility_score,0,,,0.26631421498492225,
calibration,20,liquidity_score,0,,,0.14520235574068727,
calibration,20,options_score,0,,,,
calibration,20,relative_opportunity_score,0,,,,
calibration,20,risk_reward_score,0,,,0.5672947168300563,
calibration,60,technical_score,0,,,0.21544275960461232,
calibration,60,momentum_score,0,,,0.5672947168300564,
calibration,60,research_score,0,,,0.3902255998385608,
calibration,60,volatility_score,0,,,0.26631421498492225,
calibration,60,liquidity_score,0,,,0.14520235574068727,
calibration,60,options_score,0,,,,
calibration,60,relative_opportunity_score,0,,,,
calibration,60,risk_reward_score,0,,,0.5672947168300563,
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
calibration,BUY,BUY,522
calibration,BUY,WAIT,20
calibration,BUY,AVOID,0
calibration,WAIT,BUY,0
calibration,WAIT,WAIT,1907
calibration,WAIT,AVOID,0
calibration,AVOID,BUY,0
calibration,AVOID,WAIT,0
calibration,AVOID,AVOID,301
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
