# Enhanced Scoring forward validation

Generated: 2026-10-02T08:09:07+00:00

## Data coverage

```csv
partition,predictions,execution_eligible_pct,options_pct,options_partial_pct,portfolio_fit_pct,matured_1d,matured_5d,matured_10d,matured_20d,matured_60d
calibration,3355,92.78688524590164,0.0,5.275707898658719,80.0,3250,2537,1495,0,0
holdout_locked,0,,,,,0,0,0,0,0
```

## Gross, net and benchmark alpha

```csv
partition,horizon,metric,n,mean,median,win_rate,average_gain,average_loss,expectancy
calibration,1,gross_return_pct,3020,-0.7527134887120592,-0.6896525963969669,37.64900662251656,2.096117421472585,-2.498111718951045,-0.7527134887120592
calibration,1,net_return_pct,359,-3.177298607166456,-1.6613930059688193,21.16991643454039,2.004036061956339,-4.568752440570457,-3.177298607166456
calibration,1,spy_return_pct,3020,0.10312909240194393,-0.2054445292507423,42.81456953642384,0.972161634834025,-0.5475131064195272,0.10312909240194393
calibration,1,qqq_return_pct,3020,0.4549278608892665,0.06913851652496916,53.04635761589404,1.5089333728241858,-0.7358456441317072,0.4549278608892665
calibration,1,sector_return_pct,1545,0.05432922540490839,-0.09737794132130828,47.313915857605174,1.2751010146672015,-1.04196583350263,0.05432922540490839
calibration,1,cash_return_pct,3020,0.01544565920753705,0.015481020533281153,100.0,0.01544565920753705,,0.01544565920753705
calibration,1,gross_alpha_spy_pct,3020,-0.8558425811140032,-0.7012600588032658,38.70860927152318,2.0329173431646215,-2.680240393908013,-0.8558425811140032
calibration,1,net_alpha_spy_pct,359,-3.355728253260988,-1.878660376211584,20.055710306406684,2.0288954981005856,-4.706574629909188,-3.355728253260988
calibration,1,net_alpha_qqq_pct,359,-3.6663970708114264,-2.1906404920605356,19.498607242339833,2.04465419795667,-5.049696686083976,-3.6663970708114264
calibration,1,net_alpha_sector_pct,340,-3.5039847985450217,-1.9405481746950572,20.294117647058822,1.189175212241563,-4.698922218265591,-3.5039847985450217
calibration,1,net_alpha_cash_pct,359,-3.1926344104842435,-1.676625842475415,20.055710306406684,2.0994752676950847,-4.520271681665119,-3.1926344104842435
calibration,5,gross_return_pct,2358,-1.952524820092994,-2.1411951981005206,31.552162849872772,4.430074044740281,-4.894689352581196,-1.952524820092994
calibration,5,net_return_pct,313,-3.9034290749338227,-2.9543835034436943,24.920127795527154,3.377519675450951,-6.32008440484877,-3.9034290749338227
calibration,5,spy_return_pct,2353,0.5607237363902509,0.7589325694125737,58.606034849128775,1.3686792098531024,-0.5831885817876471,0.5607237363902509
calibration,5,qqq_return_pct,2353,2.306463829615649,1.8005070143081614,82.49043773905652,2.9673460865087677,-0.8070615602618846,2.306463829615649
calibration,5,sector_return_pct,1242,0.08287144604356333,-0.1103509522067947,49.033816425120776,2.0919830431673088,-1.8500653037958692,0.08287144604356333
calibration,5,cash_return_pct,2358,0.07675721839405368,0.07708529820482646,100.0,0.07675721839405368,,0.07675721839405368
calibration,5,gross_alpha_spy_pct,2353,-2.550124943426188,-2.403902261304214,29.494262643433917,4.0725100956320075,-5.320534055606048,-2.550124943426188
calibration,5,net_alpha_spy_pct,313,-4.441313500137853,-3.5206954873407925,23.961661341853034,3.0969588809553437,-6.816819502583187,-4.441313500137853
calibration,5,net_alpha_qqq_pct,313,-6.077105020933934,-4.635253934637383,15.335463258785943,3.0751682815096366,-7.734875279489751,-6.077105020933934
calibration,5,net_alpha_sector_pct,296,-4.426248701197778,-3.05885613190865,17.22972972972973,3.139761339455138,-6.0012140565989975,-4.426248701197778
calibration,5,net_alpha_cash_pct,313,-3.9797986368837392,-3.0292710873660282,24.920127795527154,3.3010436639236707,-6.396418634598539,-3.9797986368837392
calibration,10,gross_return_pct,1391,-3.376437280730655,-4.458598726114649,25.233644859813083,7.430249725740836,-7.078141386852107,-3.376437280730655
calibration,10,net_return_pct,235,-4.099183074704236,-5.480918311015358,26.382978723404253,7.5450399241748105,-8.27225721303083,-4.099183074704236
calibration,10,spy_return_pct,1389,1.0910084048072017,1.174347293359923,100.0,1.0910084048072017,,1.0910084048072017
calibration,10,qqq_return_pct,1389,4.386911695890437,4.251870987000683,100.0,4.386911695890437,,4.386911695890437
calibration,10,sector_return_pct,754,-0.02549430455142816,-0.5566741982733547,47.87798408488064,3.3026200304354076,-3.0826171415240693,-0.02549430455142816
calibration,10,cash_return_pct,1391,0.1523314227553844,0.1524328251811813,100.0,0.1523314227553844,,0.1523314227553844
calibration,10,gross_alpha_spy_pct,1389,-4.451100809713925,-5.691160796737749,22.03023758099352,7.348986550423981,-7.7851975153484565,-4.451100809713925
calibration,10,net_alpha_spy_pct,235,-5.460302483493101,-6.449359233391095,25.957446808510635,6.361062691371299,-9.604574182727173,-5.460302483493101
calibration,10,net_alpha_qqq_pct,235,-8.788109195806179,-10.050474216561565,20.851063829787233,4.469696873923019,-12.280757031379997,-8.788109195806179
calibration,10,net_alpha_sector_pct,229,-4.490209224823516,-4.53968847519115,20.087336244541483,6.540066598476704,-7.262846863467287,-4.490209224823516
calibration,10,net_alpha_cash_pct,235,-4.251261695346354,-5.630749560362291,26.382978723404253,7.393133538510495,-8.424397559503145,-4.251261695346354
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
calibration,1,baseline_buy,644,-0.0572725836997668,38.50931677018634,64,-2.180244741440216,26.5625,64,-2.2520944294607457,39.0625,64,-2.3939467341328466,35.9375,64,-2.117173460190341,39.0625,64,-2.195531843892546,26.5625,644,-1.619302955575938,17.391304347826086,644,1.1461170162585157,68.63354037267081,644,0.0,0.0
calibration,1,enhanced_shadow_buy,624,0.07830504872242039,39.743589743589745,49,-0.2975048811392132,34.69387755102041,49,-0.2938129795512415,51.02040816326531,49,-0.3930722190512024,46.93877551020408,49,-0.30004386045285514,51.02040816326531,49,-0.3128061293338775,34.69387755102041,624,-1.5021010625169795,17.94871794871795,624,1.2517793801316377,70.51282051282051,624,0.0,0.0
calibration,1,enhanced_raw_75,177,-0.9351009553443375,32.7683615819209,84,-0.6522541402045304,30.952380952380953,84,-0.619486050394453,34.523809523809526,84,-0.6540122375975953,32.142857142857146,84,-0.7277405669711252,29.761904761904763,84,-0.6675699611363486,30.952380952380953,177,-2.8696822713508583,16.38418079096045,177,1.0045334525170682,60.451977401129945,177,0.0,0.0
calibration,1,enhanced_adjusted_75,672,0.17440161365994136,48.660714285714285,168,-0.8760263450573421,26.190476190476193,168,-1.0697409497338128,23.809523809523807,168,-1.343840225905647,25.0,168,-0.9691310759982844,23.809523809523807,168,-0.8913765072905429,26.190476190476193,672,-1.3276551966317984,21.13095238095238,672,1.6491868527045501,79.01785714285714,672,0.0,0.0
calibration,5,baseline_buy,511,-0.5054272597115858,43.05283757338552,54,-1.5930116831684662,46.2962962962963,54,-2.0081012156343916,46.2962962962963,54,-3.3355405073559306,27.77777777777778,54,-1.2039726871556196,29.629629629629626,54,-1.669007042312794,46.2962962962963,511,-3.7533964079819286,11.350293542074363,511,3.1018547536185017,89.82387475538161,511,-2.6114443748282494,0.0
calibration,5,enhanced_shadow_buy,492,-0.4415090480314676,43.69918699186992,40,0.2516349928880299,62.5,40,0.05317023976557263,62.5,40,-0.9942383241073427,37.5,40,0.5415923340166791,40.0,40,0.1756470164343164,62.5,492,-3.6441013847767496,11.788617886178862,492,3.227344698796215,92.07317073170732,492,-2.6660690306278836,0.0
calibration,5,enhanced_raw_75,135,-1.653018050829489,33.33333333333333,62,-0.47816701615006046,50.0,62,-0.7127077188362755,51.61290322580645,62,-1.6719680983270233,30.64516129032258,62,-0.39098050118715644,32.25806451612903,62,-0.5539331851266486,50.0,135,-5.12934034484467,13.333333333333334,135,2.396620089433234,65.18518518518519,135,-2.873434399405524,0.0
calibration,5,enhanced_adjusted_75,498,0.00835002024848358,44.77911646586345,133,-1.5936954886887826,34.58646616541353,133,-2.1369120487745326,30.075187969924812,133,-3.5595527688414594,18.045112781954884,133,-1.960769808592526,22.55639097744361,133,-1.669891395002337,34.58646616541353,498,-3.068662167297676,13.253012048192772,498,3.674577968262219,91.16465863453816,498,-2.965775856827665,0.0
calibration,10,baseline_buy,408,-3.054977997440723,19.852941176470587,46,-0.002152158728361063,50.0,46,-1.4290666291661305,47.82608695652174,46,-4.672629697069045,26.08695652173913,46,-0.007728653476163409,34.78260869565217,46,-0.15368828041558194,50.0,408,-7.035502972142632,7.8431372549019605,408,3.7609259924948533,90.19607843137256,408,-6.267222676391756,0.0
calibration,10,enhanced_shadow_buy,390,-2.8768942476503456,20.76923076923077,33,4.6114246244704935,69.6969696969697,33,3.2150687987916,66.66666666666666,33,0.10271459279021695,36.36363636363637,33,3.4030993517317376,48.484848484848484,33,4.460016662496743,69.6969696969697,390,-7.00284847998019,8.205128205128204,390,3.9378928552011763,92.82051282051282,390,-6.297009155815301,0.0
calibration,10,enhanced_raw_75,91,-0.5464194576033946,39.56043956043956,56,2.5136792725448105,57.14285714285714,56,1.0876728532023259,55.35714285714286,56,-2.0323187012477173,37.5,56,1.76570921184445,48.214285714285715,56,2.362454321858102,57.14285714285714,91,-5.7110370665757495,13.186813186813188,91,5.822695071363062,87.91208791208791,91,-5.681646703826263,0.0
calibration,10,enhanced_adjusted_75,307,1.3469280388625098,50.814332247557005,99,0.477306407391828,42.42424242424242,99,-0.9176949295946363,41.41414141414141,99,-4.1593914222559505,31.313131313131315,99,-0.2791894732754304,32.323232323232325,99,0.32571500750982,42.42424242424242,307,-4.074074104859891,11.400651465798045,307,6.507037119499187,95.76547231270358,307,-5.126709230207172,0.0
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
calibration,1,baseline,75-79,286,-3.7382742795155566,-2.0122407526049924,15.384615384615385,1.7985361279634189,-4.744967080875371,-3.7382742795155566
calibration,1,baseline,80-84,0,,,,,,
calibration,1,baseline,85-89,0,,,,,,
calibration,1,baseline,90+,64,-2.2520944294607457,-1.4711447518711145,39.0625,1.802667486964101,-4.851300786143339,-2.2520944294607457
calibration,1,raw,0-49,9,0.9526716118046856,-1.635653061669053,33.33333333333333,7.292733019583067,-2.217359092084505,0.9526716118046856
calibration,1,raw,50-59,15,-4.466788275872935,-0.5917781237302198,26.666666666666668,4.389938816379541,-7.68741630941929,-4.466788275872935
calibration,1,raw,60-69,150,-6.005918477961475,-5.039658941039354,14.000000000000002,1.421096912287143,-7.2149674949786915,-6.005918477961475
calibration,1,raw,70-74,101,-1.9143966669454229,-1.742285144192715,14.85148514851485,2.1514408733840993,-2.623554377468014,-1.9143966669454229
calibration,1,raw,75-79,84,-0.619486050394453,-1.0705711405419258,34.523809523809526,1.5354439062132177,-1.7557218456966792,-0.619486050394453
calibration,1,raw,80-84,0,,,,,,
calibration,1,raw,85-89,0,,,,,,
calibration,1,raw,90+,0,,,,,,
calibration,1,adjusted,0-49,9,0.9526716118046856,-1.635653061669053,33.33333333333333,7.292733019583067,-2.217359092084505,0.9526716118046856
calibration,1,adjusted,50-59,10,1.161417404334013,-0.5074705437891122,40.0,4.389938816379541,-0.9909302036963382,1.161417404334013
calibration,1,adjusted,60-69,41,-10.855141598536099,-5.7667375155516325,0.0,,-10.855141598536099,-10.855141598536099
calibration,1,adjusted,70-74,131,-4.581048674618447,-3.902111740105438,19.083969465648856,1.6402370606815768,-6.048333046151473,-4.581048674618447
calibration,1,adjusted,75-79,124,-1.462562045125336,-1.36854702965149,13.709677419354838,1.914812116770412,-1.9991542016882118,-1.462562045125336
calibration,1,adjusted,80-84,44,0.037300319096843296,0.22252073468191064,52.27272727272727,1.4384690885581908,-1.4973130950751088,0.037300319096843296
calibration,1,adjusted,85-89,0,,,,,,
calibration,1,adjusted,90+,0,,,,,,
calibration,5,baseline,0-49,0,,,,,,
calibration,5,baseline,50-59,9,5.331020449401777,6.323941978104684,100.0,5.331020449401777,,5.331020449401777
calibration,5,baseline,60-69,0,,,,,,
calibration,5,baseline,70-74,0,,,,,,
calibration,5,baseline,75-79,250,-5.318691375774026,-3.662551224860178,16.400000000000002,3.003760678727242,-6.951325510867577,-5.318691375774026
calibration,5,baseline,80-84,0,,,,,,
calibration,5,baseline,85-89,0,,,,,,
calibration,5,baseline,90+,54,-2.0081012156343916,-1.6030737459526534,46.2962962962963,2.4455417679687144,-5.847448615292241,-2.0081012156343916
calibration,5,raw,0-49,9,5.331020449401777,6.323941978104684,100.0,5.331020449401777,,5.331020449401777
calibration,5,raw,50-59,13,-5.603949885230676,2.1212653363966876,61.53846153846154,2.884771992949382,-19.185904890318774,-5.603949885230676
calibration,5,raw,60-69,142,-7.041893242502813,-5.819496044658447,12.676056338028168,3.798910753414268,-8.615558338684322,-7.041893242502813
calibration,5,raw,70-74,87,-3.691060253753065,-3.275196031318681,9.195402298850574,3.278983888074783,-4.396887508621708,-3.691060253753065
calibration,5,raw,75-79,62,-0.7127077188362755,0.76284974086213,51.61290322580645,2.08132160679327,-3.693005666174457,-0.7127077188362755
calibration,5,raw,80-84,0,,,,,,
calibration,5,raw,85-89,0,,,,,,
calibration,5,raw,90+,0,,,,,,
calibration,5,adjusted,0-49,9,5.331020449401777,6.323941978104684,100.0,5.331020449401777,,5.331020449401777
calibration,5,adjusted,50-59,8,2.884771992949382,2.633646132944677,100.0,2.884771992949382,,2.884771992949382
calibration,5,adjusted,60-69,40,-11.573048065469886,-8.402603692507896,2.5,3.0672009047650444,-11.948439064706681,-11.573048065469886
calibration,5,adjusted,70-74,123,-5.805343580695534,-5.559433846015553,13.821138211382115,3.8419525092171636,-7.352551444172097,-5.805343580695534
calibration,5,adjusted,75-79,101,-2.7471286734745135,-3.167853582291407,16.831683168316832,3.443663244482298,-4.000027037822916,-2.7471286734745135
calibration,5,adjusted,80-84,32,-0.21091582706521705,0.7860842697011732,71.875,1.4909516245992969,-4.560132647985642,-0.21091582706521705
calibration,5,adjusted,85-89,0,,,,,,
calibration,5,adjusted,90+,0,,,,,,
calibration,10,baseline,0-49,0,,,,,,
calibration,10,baseline,50-59,6,6.463555843523658,6.463555843523658,100.0,6.463555843523658,,6.463555843523658
calibration,10,baseline,60-69,0,,,,,,
calibration,10,baseline,70-74,0,,,,,,
calibration,10,baseline,75-79,183,-6.864564774537589,-6.972950522920805,18.0327868852459,4.745395235519633,-9.418755976750179,-6.864564774537589
calibration,10,baseline,80-84,0,,,,,,
calibration,10,baseline,85-89,0,,,,,,
calibration,10,baseline,90+,46,-1.4290666291661305,-2.033323236293636,47.82608695652174,8.756611197289068,-10.765937970083394,-1.4290666291661305
calibration,10,raw,0-49,6,6.463555843523658,6.463555843523658,100.0,6.463555843523658,,6.463555843523658
calibration,10,raw,50-59,5,-20.502437522889686,-18.215448157666938,0.0,,-20.502437522889686,-20.502437522889686
calibration,10,raw,60-69,109,-9.183551185956878,-8.860531778860278,12.844036697247708,5.056434307072864,-11.28207536387705,-9.183551185956878
calibration,10,raw,70-74,59,-4.734624264027168,-5.613147599356931,16.94915254237288,3.771157709148075,-6.470498136103749,-4.734624264027168
calibration,10,raw,75-79,56,1.0876728532023259,1.0042993627665613,55.35714285714286,7.765865539419567,-7.19328607770705,1.0876728532023259
calibration,10,raw,80-84,0,,,,,,
calibration,10,raw,85-89,0,,,,,,
calibration,10,raw,90+,0,,,,,,
calibration,10,adjusted,0-49,6,6.463555843523658,6.463555843523658,100.0,6.463555843523658,,6.463555843523658
calibration,10,adjusted,50-59,0,,,,,,
calibration,10,adjusted,60-69,31,-14.994519090696148,-9.892205043557745,9.67741935483871,1.9760384591206492,-16.812793113890805,-14.994519090696148
calibration,10,adjusted,70-74,99,-7.740106351924961,-8.860531778860278,11.11111111111111,5.896542265605288,-9.444687429116241,-7.740106351924961
calibration,10,adjusted,75-79,73,-2.7949696579059897,-3.957833155547619,28.767123287671232,5.874255400683412,-6.2960028546440165,-2.7949696579059897
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
calibration,OPTIONS_DATA_PARTIAL,partial,75,82.33333333333333,73.2272,75.80893333333333,100.0,39,-1.2676282376101409,24,-2.190614159164659,15,-3.4918903093614015,0,,0,
calibration,OPTIONS_DATA_PARTIAL,quote_only,95,84.47368421052632,73.00463157894735,75.56010526315791,100.0,59,-3.4443208890326495,56,-3.78185198065612,44,-3.9904347880852638,0,,0,
calibration,OPTIONS_NOT_ELIGIBLE,unavailable,1871,70.96472474612507,61.21574024585784,62.46213789417424,67.55745590593266,32,0.22416262438775658,25,4.791672893108557,11,5.997231522239526,0,,0,
calibration,OPTIONS_UNAVAILABLE,unavailable,1307,80.70007651109411,69.89022953328232,72.0996480489671,95.10328997704667,238,-4.1311781435725,212,-5.690976570628012,166,-6.939851530568891,0,,0,
```

Availability is reported separately from the formula value. Missing options
data is never classified as an observed score of 50.

## Portfolio Fit cohorts

```csv
partition,cohort,predictions,raw_score_mean,adjusted_score_mean,net_alpha_spy_1d_n,net_alpha_spy_1d_mean,net_alpha_spy_1d_median,net_alpha_spy_1d_win_rate,net_alpha_spy_1d_average_gain,net_alpha_spy_1d_average_loss,net_alpha_spy_1d_expectancy,net_alpha_spy_5d_n,net_alpha_spy_5d_mean,net_alpha_spy_5d_median,net_alpha_spy_5d_win_rate,net_alpha_spy_5d_average_gain,net_alpha_spy_5d_average_loss,net_alpha_spy_5d_expectancy,net_alpha_spy_10d_n,net_alpha_spy_10d_mean,net_alpha_spy_10d_median,net_alpha_spy_10d_win_rate,net_alpha_spy_10d_average_gain,net_alpha_spy_10d_average_loss,net_alpha_spy_10d_expectancy,net_alpha_spy_20d_n,net_alpha_spy_20d_mean,net_alpha_spy_20d_median,net_alpha_spy_20d_win_rate,net_alpha_spy_20d_average_gain,net_alpha_spy_20d_average_loss,net_alpha_spy_20d_expectancy,net_alpha_spy_60d_n,net_alpha_spy_60d_mean,net_alpha_spy_60d_median,net_alpha_spy_60d_win_rate,net_alpha_spy_60d_average_gain,net_alpha_spy_60d_average_loss,net_alpha_spy_60d_expectancy
calibration,missing,671,65.28760059612519,65.28760059612519,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,other_observed,1275,60.277435294117645,58.031254901960786,116,-0.3867553814890159,-1.1529169977709504,32.758620689655174,2.480818334570675,-1.7837784739283522,-0.3867553814890159,87,0.8690108478145389,0.7860842697011732,65.51724137931035,3.270072170966641,-3.693005666174457,0.8690108478145389,67,1.8937197988651493,1.0042993627665613,62.68656716417911,7.3026518682533625,-7.19328607770705,1.8937197988651493,0,,,,,,,0,,,,,,
calibration,raw_high_fit_weak,25,75.14040000000001,69.37280000000001,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,raw_medium_fit_good,1384,69.56843930635839,74.11602601156068,256,-4.58147591108259,-3.027009386936208,14.0625,1.7254068960775415,-5.613511279526975,-4.58147591108259,234,-6.05555814941671,-4.176102745578122,11.11111111111111,3.6389332563867347,-7.26736957514214,-6.05555814941671,173,-7.993422534458675,-7.268544553484,13.872832369942195,4.520902391270869,-10.00915272383793,-7.993422534458675,0,,,,,,,0,,,,,,
```

## Component contribution and redundancy

```csv
partition,horizon,component,n,pearson_forward_alpha,spearman_forward_alpha,max_abs_component_correlation,incremental_r2
calibration,1,technical_score,372,0.014791335215354027,0.06300817775918338,0.29947691122518794,
calibration,1,momentum_score,372,-0.13918726697876832,-0.16885586360864266,0.5501881417760589,
calibration,1,research_score,372,-0.10253660274777167,0.0010162870046754523,0.4226843821555764,
calibration,1,volatility_score,372,-0.11146350721362136,-0.06273599158125645,0.29947691122518794,
calibration,1,liquidity_score,372,0.6267331231495132,0.6247564050597175,0.15904575825824283,
calibration,1,options_score,0,,,,
calibration,1,relative_opportunity_score,372,,,,
calibration,1,risk_reward_score,372,-0.18421610507646918,-0.18366639819272026,0.5501881417760589,
calibration,5,technical_score,321,-0.032669438129012206,-0.016810520087659306,0.29947691122518794,
calibration,5,momentum_score,321,-0.32556088742640166,-0.3831331775126378,0.5501881417760589,
calibration,5,research_score,321,-0.1747355896422454,-0.08196144719977572,0.4226843821555764,
calibration,5,volatility_score,321,-0.14867192340201005,-0.03549722678728943,0.29947691122518794,
calibration,5,liquidity_score,321,0.5077503747101182,0.5205593092097563,0.15904575825824283,
calibration,5,options_score,0,,,,
calibration,5,relative_opportunity_score,321,,,,
calibration,5,risk_reward_score,321,-0.2849311171321336,-0.28198924878789194,0.5501881417760589,
calibration,10,technical_score,240,0.04724456525016947,-0.03656071982812505,0.29947691122518794,
calibration,10,momentum_score,240,-0.22750148193014405,-0.19543497496374881,0.5501881417760589,
calibration,10,research_score,240,-0.04537938642686183,0.014477539670027288,0.4226843821555764,
calibration,10,volatility_score,240,-0.22476445240264356,-0.20515550442034056,0.29947691122518794,
calibration,10,liquidity_score,240,0.4973579704926013,0.5077003520357672,0.15904575825824283,
calibration,10,options_score,0,,,,
calibration,10,relative_opportunity_score,240,,,,
calibration,10,risk_reward_score,240,-0.14745989463726786,-0.1252882907635463,0.5501881417760589,
calibration,20,technical_score,0,,,0.29947691122518794,
calibration,20,momentum_score,0,,,0.5501881417760589,
calibration,20,research_score,0,,,0.4226843821555764,
calibration,20,volatility_score,0,,,0.29947691122518794,
calibration,20,liquidity_score,0,,,0.15904575825824283,
calibration,20,options_score,0,,,,
calibration,20,relative_opportunity_score,0,,,,
calibration,20,risk_reward_score,0,,,0.5501881417760589,
calibration,60,technical_score,0,,,0.29947691122518794,
calibration,60,momentum_score,0,,,0.5501881417760589,
calibration,60,research_score,0,,,0.4226843821555764,
calibration,60,volatility_score,0,,,0.29947691122518794,
calibration,60,liquidity_score,0,,,0.15904575825824283,
calibration,60,options_score,0,,,,
calibration,60,relative_opportunity_score,0,,,,
calibration,60,risk_reward_score,0,,,0.5501881417760589,
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
fb9cc1abbfcca2453eec217b,2026-09-15T20:21:08+00:00,calibration,ELV,BUY,WAIT,67.59,100.0,72.45,-5.422241614795949,-10.599004550121446,-11.654560559623091,,
fabca3d3e4bba17e1172975c,2026-09-16T05:40:32+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
fabca3d3e4bba17e1172975c,2026-09-16T05:40:32+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,-8.692377347765227,-13.947933878356672,,
e1338d825a461549ab9e718a,2026-09-16T05:50:47+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
e1338d825a461549ab9e718a,2026-09-16T05:50:47+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,-8.692377347765227,-13.947933878356672,,
e991d1db51ca3517cd30ca69,2026-09-16T05:54:18+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
e991d1db51ca3517cd30ca69,2026-09-16T05:54:18+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,-8.692377347765227,-13.947933878356672,,
92e9fb98a9868fa5713aaf9d,2026-09-16T06:00:15+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
92e9fb98a9868fa5713aaf9d,2026-09-16T06:00:15+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,-8.692377347765227,-13.947933878356672,,
3f6b3bd68f68e3e0a4cb2309,2026-09-16T06:03:42+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
3f6b3bd68f68e3e0a4cb2309,2026-09-16T06:03:42+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,-8.692377347765227,-13.947933878356672,,
3280fe7e1c09eee6124d715f,2026-09-22T10:54:56+00:00,calibration,VRNS,BUY,WAIT,71.41,100.0,75.7,-1.5901812297277167,-3.6587378561839694,,,
0caf45bef2ea59a325fb5a5c,2026-09-26T07:09:32+00:00,calibration,BIIB,BUY,WAIT,71.26,100.0,75.57,-0.6506193150925426,,,,
```

## BUY / WAIT / AVOID transition matrix

```csv
partition,baseline_decision,enhanced_decision,predictions
calibration,BUY,BUY,685
calibration,BUY,WAIT,20
calibration,BUY,AVOID,0
calibration,WAIT,BUY,0
calibration,WAIT,WAIT,2229
calibration,WAIT,AVOID,0
calibration,AVOID,BUY,0
calibration,AVOID,WAIT,0
calibration,AVOID,AVOID,421
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
