# Enhanced Scoring forward validation

Generated: 2026-10-03T11:56:50+00:00

## Data coverage

```csv
partition,predictions,execution_eligible_pct,options_pct,options_partial_pct,portfolio_fit_pct,matured_1d,matured_5d,matured_10d,matured_20d,matured_60d
calibration,3471,92.79746470757708,0.0,5.185825410544512,80.66839527513685,3267,2836,1867,0,0
holdout_locked,0,,,,,0,0,0,0,0
```

## Gross, net and benchmark alpha

```csv
partition,horizon,metric,n,mean,median,win_rate,average_gain,average_loss,expectancy
calibration,1,gross_return_pct,3042,-0.6110481371173706,-0.6896525963969613,37.93556870479947,2.427156768665242,-2.4985240451210355,-0.6110481371173706
calibration,1,net_return_pct,359,-3.177298607166456,-1.6613930059688193,21.16991643454039,2.004036061956339,-4.568752440570457,-3.177298607166456
calibration,1,spy_return_pct,3042,0.11046601924185194,-0.2054445292507423,43.39250493096647,0.9705505874001029,-0.5488322560014067,0.11046601924185194
calibration,1,qqq_return_pct,3042,0.46225881405603353,0.06913851652496916,53.41880341880342,1.5073506932797334,-0.7362410474390353,0.46225881405603353
calibration,1,sector_return_pct,1568,0.06266115839120598,-0.09244939357592186,47.640306122448976,1.2756579079178734,-1.0410033627981006,0.06266115839120598
calibration,1,cash_return_pct,3042,0.015446686522473324,0.015481020533281153,100.0,0.015446686522473324,,0.015446686522473324
calibration,1,gross_alpha_spy_pct,3042,-0.7215141563592224,-0.6866526466853873,38.823142669296516,2.351899170913901,-2.671917777804445,-0.7215141563592224
calibration,1,net_alpha_spy_pct,359,-3.355728253260988,-1.878660376211584,20.055710306406684,2.0288954981005856,-4.706574629909188,-3.355728253260988
calibration,1,net_alpha_qqq_pct,359,-3.6663970708114264,-2.1906404920605356,19.498607242339833,2.04465419795667,-5.049696686083976,-3.6663970708114264
calibration,1,net_alpha_sector_pct,340,-3.5039847985450217,-1.9405481746950572,20.294117647058822,1.189175212241563,-4.698922218265591,-3.5039847985450217
calibration,1,net_alpha_cash_pct,359,-3.1926344104842435,-1.676625842475415,20.055710306406684,2.0994752676950847,-4.520271681665119,-3.1926344104842435
calibration,5,gross_return_pct,2657,-1.693403595045599,-1.9879795656541521,34.06097101994731,4.283037478910377,-4.780549241124456,-1.693403595045599
calibration,5,net_return_pct,320,-3.8876692703624274,-2.9333146289910847,24.0625,3.448010791016262,-6.2121440223219295,-3.8876692703624274
calibration,5,spy_return_pct,2657,0.47545317571851,0.5146428785030244,53.40609710199473,1.339136672313002,-0.514503917712495,0.47545317571851
calibration,5,qqq_return_pct,2657,2.117400156485183,1.1442506226506444,84.49378998870907,2.654094244369278,-0.8070615602618846,2.117400156485183
calibration,5,sector_return_pct,1394,0.0339850375927537,-0.1600591782876859,48.56527977044476,2.0383764911375164,-1.8585854143595537,0.0339850375927537
calibration,5,cash_return_pct,2657,0.0770141599307334,0.07718079693765922,100.0,0.0770141599307334,,0.0770141599307334
calibration,5,gross_alpha_spy_pct,2657,-2.168856770764109,-2.1917857868334,32.5555137372977,4.055800279501514,-5.173504286656835,-2.168856770764109
calibration,5,net_alpha_spy_pct,320,-4.408938130959743,-3.4818976289854633,23.125,3.1155362287603316,-6.672397897704807,-4.408938130959743
calibration,5,net_alpha_qqq_pct,320,-6.028722230173448,-4.635253934637383,14.374999999999998,3.2119251003975147,-7.580071782021127,-6.028722230173448
calibration,5,net_alpha_sector_pct,303,-4.360364192150203,-2.9236598362492643,17.491749174917494,3.0659816483492257,-5.934749510336082,-4.360364192150203
calibration,5,net_alpha_cash_pct,320,-3.9641004250753857,-3.00885211595156,24.0625,3.3715045184905033,-6.288551374271162,-3.9641004250753857
calibration,10,gross_return_pct,1763,-3.191692492329068,-3.4418623576792595,24.50368689733409,6.93251747069964,-6.477687010757619,-3.191692492329068
calibration,10,net_return_pct,277,-3.7714521185290866,-4.761044881880585,25.27075812274368,7.077730903047065,-7.440257971235997,-3.7714521185290866
calibration,10,spy_return_pct,1763,1.0935379400872627,1.1180757022497767,100.0,1.0935379400872627,,1.0935379400872627
calibration,10,qqq_return_pct,1763,4.365452846962998,4.251870987000683,100.0,4.365452846962998,,4.365452846962998
calibration,10,sector_return_pct,970,0.1438725746316785,-0.6074088526833554,43.81443298969072,3.534357436076714,-2.5000835099814225,0.1438725746316785
calibration,10,cash_return_pct,1763,0.1528575124110455,0.1532741614572286,100.0,0.1528575124110455,,0.1528575124110455
calibration,10,gross_alpha_spy_pct,1763,-4.285230432416331,-4.521065893213905,20.703346568349403,7.029533093727534,-7.23937112414917,-4.285230432416331
calibration,10,net_alpha_spy_pct,277,-5.084448010850873,-6.085872221857872,24.187725631768952,6.107998884069333,-8.65537154399208,-5.084448010850873
calibration,10,net_alpha_qqq_pct,277,-8.35703559568806,-9.20534866714581,19.855595667870034,4.044445588473348,-11.429474627800118,-8.35703559568806
calibration,10,net_alpha_sector_pct,271,-4.249056278082654,-4.53968847519115,19.92619926199262,6.251346896156728,-6.8620598329625,-4.249056278082654
calibration,10,net_alpha_cash_pct,277,-3.9239612736087506,-4.913477707061766,24.548736462093864,7.131151059092666,-7.5208399273106465,-3.9239612736087506
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
calibration,1,baseline_buy,655,0.5259095282220354,39.38931297709924,64,-2.180244741440216,26.5625,64,-2.2520944294607457,39.0625,64,-2.3939467341328466,35.9375,64,-2.117173460190341,39.0625,64,-2.195531843892546,26.5625,655,-1.0510138890534286,18.62595419847328,655,1.7659329655885472,69.16030534351145,655,0.0,0.0
calibration,1,enhanced_shadow_buy,635,0.6775065122690916,40.62992125984252,49,-0.2975048811392132,34.69387755102041,49,-0.2938129795512415,51.02040816326531,49,-0.3930722190512024,46.93877551020408,49,-0.30004386045285514,51.02040816326531,49,-0.3128061293338775,34.69387755102041,635,-0.9179433967711605,19.212598425196852,635,1.8892867199876477,71.02362204724409,635,0.0,0.0
calibration,1,enhanced_raw_75,180,0.9918342776621288,33.88888888888889,84,-0.6522541402045304,30.952380952380953,84,-0.619486050394453,34.523809523809526,84,-0.6540122375975953,32.142857142857146,84,-0.7277405669711252,29.761904761904763,84,-0.6675699611363486,30.952380952380953,180,-0.9148860706527886,17.77777777777778,180,2.95135764555161,61.111111111111114,180,0.0,0.0
calibration,1,enhanced_adjusted_75,685,0.7329354643372271,49.63503649635037,168,-0.8760263450573421,26.190476190476193,168,-1.0697409497338128,23.809523809523807,168,-1.343840225905647,25.0,168,-0.9691310759982844,23.809523809523807,168,-0.8913765072905429,26.190476190476193,685,-0.7663915998184504,22.62773722627737,685,2.211937856842973,79.41605839416059,685,0.0,0.0
calibration,5,baseline_buy,553,-0.5735918920151604,40.50632911392405,55,-1.6593556252733188,45.45454545454545,55,-2.0628674527392907,45.45454545454545,55,-3.3826082787391716,27.27272727272727,55,-1.2292460126820781,29.09090909090909,55,-1.7354089820898873,45.45454545454545,553,-3.8257717798276936,10.488245931283906,553,2.9599462201440727,90.41591320072332,553,-2.63028935490023,0.0
calibration,5,enhanced_shadow_buy,533,-0.510624592090781,41.088180112570356,40,0.2516349928880299,62.5,40,0.05317023976557263,62.5,40,-0.9942383241073427,37.5,40,0.5415923340166791,40.0,40,0.1756470164343164,62.5,533,-3.727112588317658,10.881801125703564,533,3.075057063841952,92.4953095684803,533,-2.679091041877203,0.0
calibration,5,enhanced_raw_75,138,-1.5858395478063205,34.05797101449276,64,-0.39762754094629515,51.5625,64,-0.6179112140944568,53.125,64,-1.5754454466333159,31.25,64,-0.360991945014083,32.8125,64,-0.4735005556147889,51.5625,138,-5.085960364644241,13.768115942028986,138,2.3966158165158418,65.21739130434783,138,-2.848684236185188,0.0
calibration,5,enhanced_adjusted_75,577,0.049652570453158844,46.2738301559792,138,-1.5694522440699576,34.78260869565217,138,-2.0849550069594303,30.434782608695656,138,-3.488805254452567,18.115942028985508,138,-1.922353490935159,22.463768115942027,138,-1.6457564592532223,34.78260869565217,577,-3.13026820718202,14.038128249566725,577,3.489356626683862,91.85441941074524,577,-2.8123712096500175,0.0
calibration,10,baseline_buy,460,-2.3759233801084423,24.347826086956523,50,-0.04999926522536145,46.0,50,-1.4462592468047797,44.0,50,-4.667427142811323,24.0,50,-0.08608147175900058,32.0,50,-0.2018059449988793,46.0,460,-6.608044804114127,11.73913043478261,460,4.363023792775036,91.08695652173913,460,-6.343467147098242,0.0
calibration,10,enhanced_shadow_buy,442,-2.1911368517595085,25.339366515837103,37,4.048001314804401,62.16216216216216,37,2.689766836797996,59.45945945945946,37,-0.40650836522467537,32.432432432432435,37,2.9284790021378613,43.24324324324324,37,3.8962138786909546,62.16216216216216,442,-6.561824218213978,12.217194570135746,442,4.543690844495646,93.43891402714932,442,-6.37285431326996,0.0
calibration,10,enhanced_raw_75,113,-0.32703644132626075,37.16814159292036,59,2.1928275738763907,54.23728813559322,59,0.7862587677356404,52.54237288135594,59,-2.3257818645829578,35.59322033898305,59,1.488690358723188,45.76271186440678,59,2.041414836050061,54.23728813559322,113,-5.856831815696881,15.929203539823009,113,5.535054012419241,78.76106194690266,113,-5.481711646757808,0.0
calibration,10,enhanced_adjusted_75,384,1.2637431164404134,48.69791666666667,126,-0.06571207357802164,34.92063492063492,126,-1.3854417011477527,32.53968253968254,126,-4.567551106638419,24.6031746031746,126,-0.9501413756456613,26.984126984126984,126,-0.21801633729229908,33.33333333333333,384,-4.082596398104394,14.583333333333334,384,6.471688040520021,95.83333333333334,384,-5.265379013393883,0.0
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
calibration,5,baseline,75-79,256,-5.255397172074502,-3.662551224860178,15.625,3.0357988171107677,-6.790803836738442,-5.255397172074502
calibration,5,baseline,80-84,0,,,,,,
calibration,5,baseline,85-89,0,,,,,,
calibration,5,baseline,90+,55,-2.0628674527392907,-1.6030737459526534,45.45454545454545,2.4455417679687144,-5.8198751366626285,-2.0628674527392907
calibration,5,raw,0-49,9,5.331020449401777,6.323941978104684,100.0,5.331020449401777,,5.331020449401777
calibration,5,raw,50-59,13,-6.111961346925171,-0.08011766427946188,38.46153846153847,3.342875986880999,-12.02123468055403,-6.111961346925171
calibration,5,raw,60-69,143,-7.058795344135605,-5.819496044658447,12.587412587412588,3.798910753414268,-8.622305022182784,-7.058795344135605
calibration,5,raw,70-74,91,-3.6310971047062615,-3.275196031318681,8.791208791208792,3.278983888074783,-4.297129007624916,-3.6310971047062615
calibration,5,raw,75-79,64,-0.6179112140944568,0.76284974086213,53.125,2.095407420093779,-3.693005666174457,-0.6179112140944568
calibration,5,raw,80-84,0,,,,,,
calibration,5,raw,85-89,0,,,,,,
calibration,5,raw,90+,0,,,,,,
calibration,5,adjusted,0-49,9,5.331020449401777,6.323941978104684,100.0,5.331020449401777,,5.331020449401777
calibration,5,adjusted,50-59,8,2.059253367695826,2.633646132944677,62.5,3.342875986880999,-0.08011766427946188,2.059253367695826
calibration,5,adjusted,60-69,41,-11.521483326702135,-8.613522074090584,2.4390243902439024,3.0672009047650444,-11.886200432488815,-11.521483326702135
calibration,5,adjusted,70-74,124,-5.767812947887994,-5.409167351489323,13.709677419354838,3.8419525092171636,-7.294598113970121,-5.767812947887994
calibration,5,adjusted,75-79,104,-2.7463081284626765,-3.167853582291407,16.346153846153847,3.443663244482298,-3.955842764555372,-2.7463081284626765
calibration,5,adjusted,80-84,34,-0.06199251765538533,0.7860842697011732,73.52941176470588,1.557337929263507,-4.560132647985642,-0.06199251765538533
calibration,5,adjusted,85-89,0,,,,,,
calibration,5,adjusted,90+,0,,,,,,
calibration,10,baseline,0-49,0,,,,,,
calibration,10,baseline,50-59,6,6.463555843523658,6.463555843523658,100.0,6.463555843523658,,6.463555843523658
calibration,10,baseline,60-69,0,,,,,,
calibration,10,baseline,70-74,0,,,,,,
calibration,10,baseline,75-79,221,-6.221088107360157,-6.376659377376404,17.647058823529413,4.559208816183179,-8.53115173383373,-6.221088107360157
calibration,10,baseline,80-84,0,,,,,,
calibration,10,baseline,85-89,0,,,,,,
calibration,10,baseline,90+,50,-1.4462592468047797,-1.6439743496492454,44.0,8.756611197289068,-9.46280031002137,-1.4462592468047797
calibration,10,raw,0-49,6,6.463555843523658,6.463555843523658,100.0,6.463555843523658,,6.463555843523658
calibration,10,raw,50-59,5,-20.502437522889686,-18.215448157666938,0.0,,-20.502437522889686,-20.502437522889686
calibration,10,raw,60-69,124,-8.407372889833587,-7.268544553484,16.129032258064516,4.600059067900804,-10.908802112474815,-8.407372889833587
calibration,10,raw,70-74,83,-4.199232233848473,-3.5643250257619306,12.048192771084338,3.771157709148075,-5.291066472615124,-4.199232233848473
calibration,10,raw,75-79,59,0.7862587677356404,1.0042993627665613,52.54237288135594,7.765865539419567,-6.941163015200132,0.7862587677356404
calibration,10,raw,80-84,0,,,,,,
calibration,10,raw,85-89,0,,,,,,
calibration,10,raw,90+,0,,,,,,
calibration,10,adjusted,0-49,6,6.463555843523658,6.463555843523658,100.0,6.463555843523658,,6.463555843523658
calibration,10,adjusted,50-59,0,,,,,,
calibration,10,adjusted,60-69,37,-13.741037129959798,-8.743205107719607,8.108108108108109,1.9760384591206492,-15.127837917231602,-13.741037129959798
calibration,10,adjusted,70-74,108,-7.0758278325343,-6.972950522920805,15.74074074074074,5.063121528273775,-9.343543647190753,-7.0758278325343
calibration,10,adjusted,75-79,97,-2.8167652459686354,-3.2472006158222193,21.649484536082475,5.874255400683412,-5.218231477280384,-2.8167652459686354
calibration,10,adjusted,80-84,29,3.4020887763565786,1.0042993627665613,68.96551724137932,7.754702269956783,-6.270385653866093,3.4020887763565786
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
calibration,OPTIONS_DATA_PARTIAL,quote_only,98,84.6938775510204,73.00459183673469,75.56010204081633,100.0,59,-3.44432088903265,59,-3.5157828430109386,56,-4.169339731615607,0,,0,
calibration,OPTIONS_NOT_ELIGIBLE,unavailable,1935,70.8656330749354,61.182857881136954,62.42556072351421,68.63049095607235,32,0.22416262438775664,25,4.52750693302742,11,5.997231522239526,0,,0,
calibration,OPTIONS_UNAVAILABLE,unavailable,1356,80.89970501474926,69.9104646017699,72.12216076696164,95.28023598820059,238,-4.1311781435725,216,-5.671131868121192,196,-6.221084056961869,0,,0,
```

Availability is reported separately from the formula value. Missing options
data is never classified as an observed score of 50.

## Portfolio Fit cohorts

```csv
partition,cohort,predictions,raw_score_mean,adjusted_score_mean,net_alpha_spy_1d_n,net_alpha_spy_1d_mean,net_alpha_spy_1d_median,net_alpha_spy_1d_win_rate,net_alpha_spy_1d_average_gain,net_alpha_spy_1d_average_loss,net_alpha_spy_1d_expectancy,net_alpha_spy_5d_n,net_alpha_spy_5d_mean,net_alpha_spy_5d_median,net_alpha_spy_5d_win_rate,net_alpha_spy_5d_average_gain,net_alpha_spy_5d_average_loss,net_alpha_spy_5d_expectancy,net_alpha_spy_10d_n,net_alpha_spy_10d_mean,net_alpha_spy_10d_median,net_alpha_spy_10d_win_rate,net_alpha_spy_10d_average_gain,net_alpha_spy_10d_average_loss,net_alpha_spy_10d_expectancy,net_alpha_spy_20d_n,net_alpha_spy_20d_mean,net_alpha_spy_20d_median,net_alpha_spy_20d_win_rate,net_alpha_spy_20d_average_gain,net_alpha_spy_20d_average_loss,net_alpha_spy_20d_expectancy,net_alpha_spy_60d_n,net_alpha_spy_60d_mean,net_alpha_spy_60d_median,net_alpha_spy_60d_win_rate,net_alpha_spy_60d_average_gain,net_alpha_spy_60d_average_loss,net_alpha_spy_60d_expectancy
calibration,missing,671,65.28760059612519,65.28760059612519,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,other_observed,1346,60.357109955423475,58.1555720653789,116,-0.3867553814890159,-1.1529169977709504,32.758620689655174,2.480818334570675,-1.7837784739283522,-0.3867553814890159,89,0.8274309620633734,0.7860842697011732,62.92134831460674,3.29771211788772,-3.364561302365821,0.8274309620633734,70,1.6051259148719645,1.0042993627665613,60.0,7.3026518682533625,-6.941163015200132,1.6051259148719645,0,,,,,,,0,,,,,,
calibration,raw_high_fit_weak,25,75.14040000000001,69.37280000000001,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,raw_medium_fit_good,1429,69.57384884534639,74.12118264520645,256,-4.58147591108259,-3.027009386936208,14.0625,1.7254068960775415,-5.613511279526975,-4.58147591108259,239,-6.0073937037291,-4.176102745578122,10.87866108786611,3.6389332563867347,-7.184879623743241,-6.0073937037291,212,-7.045107081902057,-6.700691499509045,14.150943396226415,4.3237586149832286,-8.919095933036996,-7.045107081902057,0,,,,,,,0,,,,,,
```

## Component contribution and redundancy

```csv
partition,horizon,component,n,pearson_forward_alpha,spearman_forward_alpha,max_abs_component_correlation,incremental_r2
calibration,1,technical_score,372,0.014791335215354027,0.06300817775918338,0.31527520287111394,
calibration,1,momentum_score,372,-0.13918726697876832,-0.16885586360864266,0.5417427210853833,
calibration,1,research_score,372,-0.10253660274777167,0.0010162870046754523,0.4241463347413493,
calibration,1,volatility_score,372,-0.11146350721362136,-0.06273599158125645,0.315275202871114,
calibration,1,liquidity_score,372,0.6267331231495132,0.6247564050597175,0.16696495573877732,
calibration,1,options_score,0,,,,
calibration,1,relative_opportunity_score,372,,,,
calibration,1,risk_reward_score,372,-0.18421610507646918,-0.18366639819272026,0.5417427210853833,
calibration,5,technical_score,328,-0.03416684462713946,-0.020207772372322984,0.31527520287111394,
calibration,5,momentum_score,328,-0.31451556229433514,-0.36501155856563994,0.5417427210853833,
calibration,5,research_score,328,-0.161072619525089,-0.06285804970843883,0.4241463347413493,
calibration,5,volatility_score,328,-0.1523017177438159,-0.04963968283620156,0.315275202871114,
calibration,5,liquidity_score,328,0.5126385713327832,0.5310673254100309,0.16696495573877732,
calibration,5,options_score,0,,,,
calibration,5,relative_opportunity_score,328,,,,
calibration,5,risk_reward_score,328,-0.2635815205253268,-0.25635480202484356,0.5417427210853833,
calibration,10,technical_score,282,0.046148925498524666,-0.02163158127368171,0.31527520287111394,
calibration,10,momentum_score,282,-0.20868846891854992,-0.15749819759109054,0.5417427210853833,
calibration,10,research_score,282,-0.037299724765362426,0.003993946899557997,0.4241463347413493,
calibration,10,volatility_score,282,-0.19626407758014255,-0.17916232577024038,0.315275202871114,
calibration,10,liquidity_score,282,0.4816451398409765,0.4903829667930371,0.16696495573877732,
calibration,10,options_score,0,,,,
calibration,10,relative_opportunity_score,282,,,,
calibration,10,risk_reward_score,282,-0.15800291893245513,-0.1460443375907629,0.5417427210853833,
calibration,20,technical_score,0,,,0.31527520287111394,
calibration,20,momentum_score,0,,,0.5417427210853833,
calibration,20,research_score,0,,,0.4241463347413493,
calibration,20,volatility_score,0,,,0.315275202871114,
calibration,20,liquidity_score,0,,,0.16696495573877732,
calibration,20,options_score,0,,,,
calibration,20,relative_opportunity_score,0,,,,
calibration,20,risk_reward_score,0,,,0.5417427210853833,
calibration,60,technical_score,0,,,0.31527520287111394,
calibration,60,momentum_score,0,,,0.5417427210853833,
calibration,60,research_score,0,,,0.4241463347413493,
calibration,60,volatility_score,0,,,0.315275202871114,
calibration,60,liquidity_score,0,,,0.16696495573877732,
calibration,60,options_score,0,,,,
calibration,60,relative_opportunity_score,0,,,,
calibration,60,risk_reward_score,0,,,0.5417427210853833,
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
0caf45bef2ea59a325fb5a5c,2026-09-26T07:09:32+00:00,calibration,BIIB,BUY,WAIT,71.26,100.0,75.57,-0.6506193150925426,-5.0202442564038545,,,
8a474d0fe7e76b1f968ebf69,2026-10-03T11:19:04+00:00,calibration,IEX,BUY,WAIT,66.92,100.0,71.88,,,,,
```

## BUY / WAIT / AVOID transition matrix

```csv
partition,baseline_decision,enhanced_decision,predictions
calibration,BUY,BUY,724
calibration,BUY,WAIT,21
calibration,BUY,AVOID,0
calibration,WAIT,BUY,0
calibration,WAIT,WAIT,2280
calibration,WAIT,AVOID,0
calibration,AVOID,BUY,0
calibration,AVOID,WAIT,0
calibration,AVOID,AVOID,446
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
