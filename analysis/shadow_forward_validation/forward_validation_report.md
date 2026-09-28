# Enhanced Scoring forward validation

Generated: 2026-09-28T12:09:15+00:00

## Data coverage

```csv
partition,predictions,execution_eligible_pct,options_pct,options_partial_pct,portfolio_fit_pct,matured_1d,matured_5d,matured_10d,matured_20d,matured_60d
calibration,3000,93.0,0.0,5.333333333333334,78.83333333333333,2730,2012,828,0,0
holdout_locked,0,,,,,0,0,0,0,0
```

## Gross, net and benchmark alpha

```csv
partition,horizon,metric,n,mean,median,win_rate,average_gain,average_loss,expectancy
calibration,1,gross_return_pct,2529,-0.8341127455660674,-0.7760153151921134,38.43416370106761,2.022857822867333,-2.6227084539019514,-0.8341127455660674
calibration,1,net_return_pct,315,-3.39229990140852,-2.081818406596427,21.904761904761905,2.1619450257427935,-4.950197868780228,-3.39229990140852
calibration,1,spy_return_pct,2431,0.25288004842586237,0.24789671462555063,52.406417112299465,0.984000593299396,-0.5521740346933095,0.25288004842586237
calibration,1,qqq_return_pct,2431,0.6807317339530456,0.09587341486660961,57.50719868366927,1.6786652821815347,-0.6698114416746676,0.6807317339530456
calibration,1,sector_return_pct,1242,0.18656370200265246,0.008530719416433019,50.1610305958132,1.4268793619989235,-1.0617669218708157,0.18656370200265246
calibration,1,cash_return_pct,2529,0.015375618019691442,0.015412308123874396,100.0,0.015375618019691442,,0.015375618019691442
calibration,1,gross_alpha_spy_pct,2431,-1.1051304509279667,-0.8618184488195513,36.48704236939531,2.0117346817056942,-2.895712946165051,-1.1051304509279667
calibration,1,net_alpha_spy_pct,314,-3.6619319640998813,-2.10462766071475,19.745222929936308,2.2489757311436374,-5.116202904993128,-3.6619319640998813
calibration,1,net_alpha_qqq_pct,314,-3.958363792034739,-2.447890325586834,21.337579617834397,2.094230358605175,-5.600160585933017,-3.958363792034739
calibration,1,net_alpha_sector_pct,296,-3.862008538325837,-2.0894753965860815,19.93243243243243,1.2543872463160022,-5.135710442519375,-3.862008538325837
calibration,1,net_alpha_cash_pct,315,-3.407572213962533,-2.0970512431030226,21.26984126984127,2.2108101980759662,-4.925441655924547,-3.407572213962533
calibration,5,gross_return_pct,1868,-1.7978932739010947,-2.0652178651797914,31.852248394004285,4.631523199411234,-4.8030015234068575,-1.7978932739010947
calibration,5,net_return_pct,284,-3.8716005209445354,-2.9122457545384752,25.0,3.487490755200837,-6.324630946326327,-3.8716005209445354
calibration,5,spy_return_pct,1868,0.9079205347995151,1.2682290118779083,70.2355460385439,1.41229234567662,-0.2822517959032938,0.9079205347995151
calibration,5,qqq_return_pct,1868,2.9078386080733765,3.3024831992218395,95.18201284796574,3.1448981088917822,-1.7754035303168993,2.9078386080733765
calibration,5,sector_return_pct,970,0.3009365261087139,0.3475938849169635,52.98969072164949,2.2755641414795695,-1.9248498649014167,0.3009365261087139
calibration,5,cash_return_pct,1868,0.07645625950237817,0.07660773700177703,100.0,0.07645625950237817,,0.07645625950237817
calibration,5,gross_alpha_spy_pct,1868,-2.7058138087006105,-2.5929360890808884,28.31905781584582,4.24967957971691,-5.453727178732625,-2.7058138087006105
calibration,5,net_alpha_spy_pct,284,-4.606479305330646,-3.4818976289854633,21.830985915492956,3.2509852512638164,-6.800906343658829,-4.606479305330646
calibration,5,net_alpha_qqq_pct,284,-6.292395078319501,-4.635253934637383,14.43661971830986,3.168789095659743,-7.8887265644641476,-6.292395078319501
calibration,5,net_alpha_sector_pct,271,-4.476453806461015,-2.886106093227845,16.605166051660518,3.157058321816452,-5.996400911649006,-4.476453806461015
calibration,5,net_alpha_cash_pct,284,-3.947854093411042,-2.9884331445370917,25.0,3.411116238490855,-6.400844204045009,-3.947854093411042
calibration,10,gross_return_pct,774,-3.0107205212124857,-4.265531282722507,26.22739018087855,7.248312976649827,-6.657977614147774,-3.0107205212124857
calibration,10,net_return_pct,176,-2.703418430793327,-4.438800305997008,32.38636363636363,7.629724623216119,-7.652907120528944,-2.703418430793327
calibration,10,spy_return_pct,774,1.2526216322704202,1.174347293359923,100.0,1.2526216322704202,,1.2526216322704202
calibration,10,qqq_return_pct,774,4.264698442519926,4.251870987000683,100.0,4.264698442519926,,4.264698442519926
calibration,10,sector_return_pct,416,-0.14685580453770355,0.1982048149982374,50.96153846153846,2.9579085943751107,-3.3733756700745503,-0.14685580453770355
calibration,10,cash_return_pct,774,0.15111024014308536,0.1524328251811813,100.0,0.15111024014308536,,0.15111024014308536
calibration,10,gross_alpha_spy_pct,774,-4.263342153482904,-5.729285350344138,24.160206718346252,6.564955694569618,-7.712902115298617,-4.263342153482904
calibration,10,net_alpha_spy_pct,176,-4.138850800686538,-5.62074940573898,31.818181818181817,6.425644103854133,-9.068948422805517,-4.138850800686538
calibration,10,net_alpha_qqq_pct,176,-7.23638019909813,-8.762036997226321,25.0,4.8105956199230775,-11.25203880543853,-7.23638019909813
calibration,10,net_alpha_sector_pct,170,-2.994116406719172,-2.5259132581690853,24.11764705882353,6.564660271622407,-6.032177211463394,-2.994116406719172
calibration,10,net_alpha_cash_pct,176,-2.8547410916244336,-4.591233131178189,32.38636363636363,7.47802206493578,-7.804047813674285,-2.8547410916244336
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
calibration,1,baseline_buy,520,-0.128774018902654,36.53846153846153,54,-2.3026525301154437,27.77777777777778,54,-2.4639255623169243,42.592592592592595,54,-2.525342511138635,42.592592592592595,54,-2.347147070348296,42.592592592592595,54,-2.317846983078136,27.77777777777778,520,-1.7068485443962522,17.692307692307693,520,1.1165745461635954,63.07692307692307,520,0.0,0.0
calibration,1,enhanced_shadow_buy,501,0.03722165222659631,37.924151696606785,40,-0.019502008572020602,37.5,40,-0.09913480481823882,57.49999999999999,40,-0.0685174538253019,57.49999999999999,40,-0.19179542431570534,57.49999999999999,40,-0.03469498599551106,37.5,501,-1.564002414039997,18.36327345309381,501,1.2460686818452582,65.26946107784431,501,0.0,0.0
calibration,1,enhanced_raw_75,135,-1.1564532368385212,31.851851851851855,62,-0.5116322479391814,33.87096774193548,62,-0.6079704012155807,38.70967741935484,62,-0.4864446441639721,38.70967741935484,62,-0.7238415211108225,35.483870967741936,62,-0.5267808908601653,33.87096774193548,135,-3.208865271325155,18.51851851851852,135,0.9451642595460249,55.55555555555556,135,0.0,0.0
calibration,1,enhanced_adjusted_75,498,0.3718378103162018,53.21285140562249,133,-0.7173840755209868,29.32330827067669,133,-1.071674139522756,26.31578947368421,133,-1.305126864549972,29.32330827067669,133,-0.937928412404639,26.31578947368421,133,-0.7326186134509908,29.32330827067669,498,-1.198772839724725,23.895582329317268,498,1.8748582072128777,79.91967871485943,498,0.0,0.0
calibration,5,baseline_buy,460,-0.6234531573057596,40.869565217391305,50,-1.931502280280042,44.0,50,-2.488163482504279,44.0,50,-3.836738016302636,24.0,50,-1.4872192928629215,26.0,50,-2.0073768314391276,44.0,460,-3.7917061144697675,11.73913043478261,460,3.0030005386032337,90.0,460,-2.5695458318396054,0.0
calibration,5,enhanced_shadow_buy,442,-0.5642936152005541,41.40271493212669,37,-0.14454450729979515,59.45945945945946,37,-0.4730442363923748,59.45945945945946,37,-1.5100238561999764,32.432432432432435,37,0.20637348345437465,35.13513513513514,37,-0.2204094446313889,59.45945945945946,442,-3.6829600248068046,12.217194570135746,442,3.1297924273153583,92.3076923076923,442,-2.632561754627737,0.0
calibration,5,enhanced_raw_75,125,-1.7100696728026052,36.0,59,-0.469813633429881,52.54237288135594,59,-0.787736064244669,49.152542372881356,59,-1.7359741474038384,32.20338983050847,59,-0.35470793952380686,33.89830508474576,59,-0.5454913639327436,52.54237288135594,125,-5.03113871572571,14.399999999999999,125,2.623350360635931,67.2,125,-3.134376136698982,0.0
calibration,5,enhanced_adjusted_75,384,0.3643372862333103,48.69791666666667,126,-1.7506875594410498,34.12698412698413,126,-2.4005441284964766,26.984126984126984,126,-3.840465748209338,16.666666666666664,126,-2.1175857256972175,21.428571428571427,126,-1.8268107128298092,34.12698412698413,384,-2.754712612607095,15.885416666666666,384,4.164017898340851,94.53125,384,-3.127198261543643,0.0
calibration,10,baseline_buy,251,-2.312229128313802,27.88844621513944,40,1.886069872004621,57.49999999999999,40,0.3914291252441112,55.00000000000001,40,-2.7250382962939215,30.0,40,1.5470373170092049,40.0,40,1.734937834740564,57.49999999999999,251,-7.305270625825681,11.952191235059761,251,4.144398028448371,92.43027888446214,251,-6.0756329466303285,0.0
calibration,10,enhanced_shadow_buy,244,-2.1600098132502685,28.688524590163933,33,4.6114246244704935,69.6969696969697,33,3.2150687987916,66.66666666666666,33,0.10271459279021695,36.36363636363637,33,3.4030993517317376,48.484848484848484,33,4.460016662496743,69.6969696969697,244,-7.269187526375862,12.295081967213115,244,4.310525212986082,94.67213114754098,244,-6.1150844530112,0.0
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
calibration,1,baseline,75-79,251,-4.085134266408331,-2.762082806315366,14.342629482071715,2.0490366868905214,-5.112251263239766,-4.085134266408331
calibration,1,baseline,80-84,0,,,,,,
calibration,1,baseline,85-89,0,,,,,,
calibration,1,baseline,90+,54,-2.4639255623169243,-1.5326589743804258,42.592592592592595,1.9040424149607615,-5.704675997071337,-2.4639255623169243
calibration,1,raw,0-49,9,0.9526716118046856,-1.635653061669053,33.33333333333333,7.292733019583067,-2.217359092084505,0.9526716118046856
calibration,1,raw,50-59,14,-4.552940111065301,-0.5917781237302198,28.57142857142857,4.389938816379541,-8.130091682043238,-4.552940111065301
calibration,1,raw,60-69,142,-6.247970415943748,-5.066480409554554,11.267605633802818,1.788563703139153,-7.268482685033639,-6.247970415943748
calibration,1,raw,70-74,87,-1.9514201809116392,-1.742285144192715,17.24137931034483,2.1514408733840993,-2.8061829005565846,-1.9514201809116392
calibration,1,raw,75-79,62,-0.6079704012155807,-1.2152276610414454,38.70967741935484,1.6295795273187583,-2.0211598297635835,-0.6079704012155807
calibration,1,raw,80-84,0,,,,,,
calibration,1,raw,85-89,0,,,,,,
calibration,1,raw,90+,0,,,,,,
calibration,1,adjusted,0-49,9,0.9526716118046856,-1.635653061669053,33.33333333333333,7.292733019583067,-2.217359092084505,0.9526716118046856
calibration,1,adjusted,50-59,9,1.652759625168884,-0.42316296384800456,44.44444444444444,4.389938816379541,-0.536983727799641,1.652759625168884
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
calibration,5,baseline,75-79,225,-5.474716145036911,-3.662551224860178,13.777777777777779,3.6152524749165704,-6.9272369038954595,-5.474716145036911
calibration,5,baseline,80-84,0,,,,,,
calibration,5,baseline,85-89,0,,,,,,
calibration,5,baseline,90+,50,-2.488163482504279,-1.6030679832651262,44.0,1.8867761277875892,-5.9256160334478905,-2.488163482504279
calibration,5,raw,0-49,9,5.331020449401777,6.323941978104684,100.0,5.331020449401777,,5.331020449401777
calibration,5,raw,50-59,9,-8.7434105995113,-8.613522074090584,44.44444444444444,4.309707263998041,-19.185904890318774,-8.7434105995113
calibration,5,raw,60-69,124,-7.2093486533468445,-5.819496044658447,12.096774193548388,4.361795237749523,-8.801707904415153,-7.2093486533468445
calibration,5,raw,70-74,83,-4.0613608500900416,-3.443099770630134,6.024096385542169,1.320480343341476,-4.406350670181806,-4.0613608500900416
calibration,5,raw,75-79,59,-0.787736064244669,-0.0697432738322592,49.152542372881356,2.217715248096491,-3.693005666174457,-0.787736064244669
calibration,5,raw,80-84,0,,,,,,
calibration,5,raw,85-89,0,,,,,,
calibration,5,raw,90+,0,,,,,,
calibration,5,adjusted,0-49,9,5.331020449401777,6.323941978104684,100.0,5.331020449401777,,5.331020449401777
calibration,5,adjusted,50-59,4,4.309707263998041,3.8517999434377526,100.0,4.309707263998041,,4.309707263998041
calibration,5,adjusted,60-69,37,-12.067264927594536,-8.613522074090584,2.7027027027027026,3.0672009047650444,-12.48766675627119,-12.067264927594536
calibration,5,adjusted,70-74,108,-5.782414567619979,-5.258900856963094,12.962962962962962,4.45426626153413,-7.307026606004633,-5.782414567619979
calibration,5,adjusted,75-79,97,-3.025058809297759,-3.167853582291407,14.432989690721648,2.7794861263077277,-4.004138677954106,-3.025058809297759
calibration,5,adjusted,80-84,29,-0.31165019616114953,0.7860842697011732,68.96551724137932,1.6001669071598719,-4.560132647985642,-0.31165019616114953
calibration,5,adjusted,85-89,0,,,,,,
calibration,5,adjusted,90+,0,,,,,,
calibration,10,baseline,0-49,0,,,,,,
calibration,10,baseline,50-59,6,6.960646603285157,6.960646603285156,100.0,6.960646603285157,,6.960646603285157
calibration,10,baseline,60-69,0,,,,,,
calibration,10,baseline,70-74,0,,,,,,
calibration,10,baseline,75-79,130,-6.0450675811562,-6.972950522920805,21.53846153846154,4.47952656627718,-8.934171856922227,-6.0450675811562
calibration,10,baseline,80-84,0,,,,,,
calibration,10,baseline,85-89,0,,,,,,
calibration,10,baseline,90+,40,0.3914291252441112,1.0042993627665613,55.00000000000001,8.756611197289068,-9.832682296144167,0.3914291252441112
calibration,10,raw,0-49,6,6.960646603285157,6.960646603285156,100.0,6.960646603285157,,6.960646603285157
calibration,10,raw,50-59,1,-18.215448157666938,-18.215448157666938,0.0,,-18.215448157666938,-18.215448157666938
calibration,10,raw,60-69,72,-9.153931426737255,-9.587903222217474,12.5,4.4020868202925865,-11.09050546202723,-9.153931426737255
calibration,10,raw,70-74,41,-3.7515314496859156,-5.613147599356931,24.390243902439025,3.771157709148075,-6.17820537189043,-3.7515314496859156
calibration,10,raw,75-79,56,1.0876728532023259,1.0042993627665613,55.35714285714286,7.765865539419567,-7.19328607770705,1.0876728532023259
calibration,10,raw,80-84,0,,,,,,
calibration,10,raw,85-89,0,,,,,,
calibration,10,raw,90+,0,,,,,,
calibration,10,adjusted,0-49,6,6.960646603285157,6.960646603285156,100.0,6.960646603285157,,6.960646603285157
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
calibration,OPTIONS_DATA_PARTIAL,quote_only,95,84.47368421052632,73.00463157894735,75.56010526315791,100.0,56,-3.6028966242117457,56,-3.78185198065612,37,-2.835972901624091,0,,0,
calibration,OPTIONS_NOT_ELIGIBLE,unavailable,1672,71.97966507177034,61.49208133971292,62.76923444976076,65.84928229665071,29,0.616427508750713,20,5.578350619782002,11,6.720272627347158,0,,0,
calibration,OPTIONS_UNAVAILABLE,unavailable,1168,79.73030821917808,69.72489726027396,71.91584760273972,94.52054794520548,212,-4.442678232069821,196,-5.804859423985415,117,-5.78698145505764,0,,0,
```

Availability is reported separately from the formula value. Missing options
data is never classified as an observed score of 50.

## Portfolio Fit cohorts

```csv
partition,cohort,predictions,raw_score_mean,adjusted_score_mean,net_alpha_spy_1d_n,net_alpha_spy_1d_mean,net_alpha_spy_1d_median,net_alpha_spy_1d_win_rate,net_alpha_spy_1d_average_gain,net_alpha_spy_1d_average_loss,net_alpha_spy_1d_expectancy,net_alpha_spy_5d_n,net_alpha_spy_5d_mean,net_alpha_spy_5d_median,net_alpha_spy_5d_win_rate,net_alpha_spy_5d_average_gain,net_alpha_spy_5d_average_loss,net_alpha_spy_5d_expectancy,net_alpha_spy_10d_n,net_alpha_spy_10d_mean,net_alpha_spy_10d_median,net_alpha_spy_10d_win_rate,net_alpha_spy_10d_average_gain,net_alpha_spy_10d_average_loss,net_alpha_spy_10d_expectancy,net_alpha_spy_20d_n,net_alpha_spy_20d_mean,net_alpha_spy_20d_median,net_alpha_spy_20d_win_rate,net_alpha_spy_20d_average_gain,net_alpha_spy_20d_average_loss,net_alpha_spy_20d_expectancy,net_alpha_spy_60d_n,net_alpha_spy_60d_mean,net_alpha_spy_60d_median,net_alpha_spy_60d_win_rate,net_alpha_spy_60d_average_gain,net_alpha_spy_60d_average_loss,net_alpha_spy_60d_expectancy
calibration,missing,635,65.79732283464567,65.79732283464567,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,other_observed,1072,59.77915111940298,57.31515858208955,91,-0.21777766067687165,-0.7928801551700186,36.26373626373626,2.6925191542167433,-1.873636193288756,-0.21777766067687165,79,0.823931450698792,0.7860842697011732,62.0253164556962,3.589403154906904,-3.693005666174457,0.823931450698792,67,2.0124280400022236,1.0042993627665613,62.68656716417911,7.492019776733933,-7.19328607770705,2.0124280400022236,0,,,,,,,0,,,,,,
calibration,raw_high_fit_weak,25,75.14040000000001,69.37280000000001,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,raw_medium_fit_good,1268,69.52368296529968,74.07630914826498,234,-4.852997234977602,-3.6802345298898302,13.247863247863249,1.9641494306770297,-5.894039336629295,-4.852997234977602,212,-6.259347679358849,-3.8379236503182153,9.433962264150944,3.601466514147512,-7.286515824515761,-6.259347679358849,114,-7.290450002805894,-7.517704836200489,16.666666666666664,4.070018867058632,-9.562543776778798,-7.290450002805894,0,,,,,,,0,,,,,,
```

## Component contribution and redundancy

```csv
partition,horizon,component,n,pearson_forward_alpha,spearman_forward_alpha,max_abs_component_correlation,incremental_r2
calibration,1,technical_score,325,0.004116656517494185,0.0454014833084055,0.2805292235335663,
calibration,1,momentum_score,325,-0.17466873457486187,-0.24882416012643155,0.5670940691515898,
calibration,1,research_score,325,-0.1303743699485156,-0.04860249962781031,0.4090394121408049,
calibration,1,volatility_score,325,-0.08076089873413021,-0.004284391904764618,0.2805292235335663,
calibration,1,liquidity_score,325,0.6238288920886543,0.6436748350360159,0.1237164788338282,
calibration,1,options_score,0,,,,
calibration,1,relative_opportunity_score,325,,,,
calibration,1,risk_reward_score,325,-0.22798799168013076,-0.25517483791124385,0.5670940691515898,
calibration,5,technical_score,291,-0.06207599265626191,-0.05187831175813024,0.2805292235335663,
calibration,5,momentum_score,291,-0.30902625324038085,-0.35176093310394146,0.5670940691515898,
calibration,5,research_score,291,-0.16114027267331607,-0.06713976177483118,0.4090394121408049,
calibration,5,volatility_score,291,-0.10864254167165405,-0.02454082083437082,0.2805292235335663,
calibration,5,liquidity_score,291,0.4945153675408607,0.5025561917393968,0.1237164788338282,
calibration,5,options_score,0,,,,
calibration,5,relative_opportunity_score,291,,,,
calibration,5,risk_reward_score,291,-0.28097207187542517,-0.29156694340160055,0.5670940691515898,
calibration,10,technical_score,181,0.05951155037031543,-0.0006217153983923571,0.2805292235335663,
calibration,10,momentum_score,181,-0.27687696785934507,-0.2689830808308649,0.5670940691515898,
calibration,10,research_score,181,-0.11763997870614924,0.0038902560264001866,0.4090394121408049,
calibration,10,volatility_score,181,-0.2890681804666541,-0.2693984813818138,0.2805292235335663,
calibration,10,liquidity_score,181,0.49875294726950714,0.5003644043827151,0.1237164788338282,
calibration,10,options_score,0,,,,
calibration,10,relative_opportunity_score,181,,,,
calibration,10,risk_reward_score,181,-0.18485469132901358,-0.15428364798462715,0.5670940691515898,
calibration,20,technical_score,0,,,0.2805292235335663,
calibration,20,momentum_score,0,,,0.5670940691515898,
calibration,20,research_score,0,,,0.4090394121408049,
calibration,20,volatility_score,0,,,0.2805292235335663,
calibration,20,liquidity_score,0,,,0.1237164788338282,
calibration,20,options_score,0,,,,
calibration,20,relative_opportunity_score,0,,,,
calibration,20,risk_reward_score,0,,,0.5670940691515898,
calibration,60,technical_score,0,,,0.2805292235335663,
calibration,60,momentum_score,0,,,0.5670940691515898,
calibration,60,research_score,0,,,0.4090394121408049,
calibration,60,volatility_score,0,,,0.2805292235335663,
calibration,60,liquidity_score,0,,,0.1237164788338282,
calibration,60,options_score,0,,,,
calibration,60,relative_opportunity_score,0,,,,
calibration,60,risk_reward_score,0,,,0.5670940691515898,
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
calibration,BUY,BUY,559
calibration,BUY,WAIT,20
calibration,BUY,AVOID,0
calibration,WAIT,BUY,0
calibration,WAIT,WAIT,2088
calibration,WAIT,AVOID,0
calibration,AVOID,BUY,0
calibration,AVOID,WAIT,0
calibration,AVOID,AVOID,333
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
