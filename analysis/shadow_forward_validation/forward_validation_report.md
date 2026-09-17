# Enhanced Scoring forward validation

Generated: 2026-09-17T14:52:43+00:00

## Data coverage

```csv
partition,predictions,execution_eligible_pct,options_pct,options_partial_pct,portfolio_fit_pct,matured_1d,matured_5d,matured_10d,matured_20d,matured_60d
calibration,1536,92.96875,0.0,7.747395833333333,67.51302083333334,1287,148,0,0,0
holdout_locked,0,,,,,0,0,0,0,0
```

## Gross, net and benchmark alpha

```csv
partition,horizon,metric,n,mean,median,win_rate,average_gain,average_loss,expectancy
calibration,1,gross_return_pct,1199,-0.9086266534968784,-0.9158617959411863,37.53127606338615,1.2749030226019247,-2.2204936151049712,-0.9086266534968784
calibration,1,net_return_pct,219,-3.5938062119868555,-2.081818406596427,17.80821917808219,1.9008909081164056,-4.784323921342562,-3.5938062119868555
calibration,1,spy_return_pct,1199,-0.2316198267011161,-0.4461622179203206,30.85904920767306,0.4861084372645475,-0.5519569288329563,-0.2316198267011161
calibration,1,qqq_return_pct,1199,-0.3067203510345299,-0.6542788880757655,34.361968306922435,0.6395162318487645,-0.8020818150090118,-0.3067203510345299
calibration,1,sector_return_pct,690,-0.1892173089808266,-0.38428160821506463,37.391304347826086,1.162108684512081,-0.996259221761313,-0.1892173089808266
calibration,1,cash_return_pct,1199,0.015193522534723527,0.015232836506595682,100.0,0.015193522534723527,,0.015193522534723527
calibration,1,gross_alpha_spy_pct,1199,-0.6770068267957624,-0.6138842509889386,39.28273561301084,1.4970099277870694,-2.083547886422842,-0.6770068267957624
calibration,1,net_alpha_spy_pct,219,-3.6114340683741677,-1.8786635032186374,20.091324200913242,1.8795117181145884,-4.992014723262769,-3.6114340683741677
calibration,1,net_alpha_qqq_pct,219,-3.5596667883157953,-1.6610677632172655,26.027397260273972,1.7142219808382833,-5.415294318203341,-3.5596667883157953
calibration,1,net_alpha_sector_pct,213,-3.5461527411141565,-1.9405441129238934,22.065727699530516,1.2868216489963826,-4.914525008193647,-3.5461527411141565
calibration,1,net_alpha_cash_pct,219,-3.608985189655878,-2.0970512431030226,16.894977168949772,1.9878071123409946,-4.746794613688207,-3.608985189655878
calibration,5,gross_return_pct,148,-2.027185754559726,-2.504552695732065,28.37837837837838,3.040488687777612,-4.035132231712256,-2.027185754559726
calibration,5,net_return_pct,27,-2.7852026304240347,-3.0831637146971667,25.925925925925924,4.473110571482557,-5.325612251091343,-2.7852026304240347
calibration,5,spy_return_pct,148,-0.5727788403753892,-1.1704097671122682,32.432432432432435,0.4216070339918776,-1.0500840600716774,-0.5727788403753892
calibration,5,qqq_return_pct,148,-0.722767365153095,-1.6509688779556608,32.432432432432435,0.9184329317076542,-1.5105435076462548,-0.722767365153095
calibration,5,sector_return_pct,112,-0.35167360926556934,-0.05810123756689878,49.107142857142854,1.064199183893371,-1.717866655296126,-0.35167360926556934
calibration,5,cash_return_pct,148,0.07430970278064332,0.07412260235359902,100.0,0.07430970278064332,,0.07430970278064332
calibration,5,gross_alpha_spy_pct,148,-1.4544069141843372,-1.6586079630954154,33.78378378378378,2.8260435484053352,-3.638310211423966,-1.4544069141843372
calibration,5,net_alpha_spy_pct,27,-3.0175863087542556,-3.498041223484127,18.51851851851852,5.779108795662623,-5.016835196121727,-3.0175863087542556
calibration,5,net_alpha_qqq_pct,27,-3.42732931496065,-4.0370377905206905,18.51851851851852,5.24233346518972,-5.39770721954028,-3.42732931496065
calibration,5,net_alpha_sector_pct,27,-2.6056840786149795,-1.7091090054106053,18.51851851851852,4.9728471680234065,-4.328077543760068,-2.6056840786149795
calibration,5,net_alpha_cash_pct,27,-2.8599889214116128,-3.1580512986195006,25.925925925925924,4.3982229875602235,-5.400363089551755,-2.8599889214116128
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
calibration,1,baseline_buy,371,-0.8952762195085878,31.266846361185983,46,-2.7182069322430484,26.08695652173913,46,-2.819235589979695,43.47826086956522,46,-2.710352012108383,43.47826086956522,46,-2.6806006274687424,43.47826086956522,46,-2.7333502197312605,26.08695652173913,371,-2.1045748591466644,10.242587601078167,371,0.15662519161879143,54.17789757412399,371,0.0,0.0
calibration,1,enhanced_shadow_buy,353,-0.6998888508005371,32.86118980169972,33,-0.23547690111075387,36.36363636363637,33,-0.21834311679324186,60.60606060606061,33,0.04991170417915346,60.60606060606061,33,-0.4018039912114806,60.60606060606061,33,-0.2506073904974392,36.36363636363637,353,-1.944941453868802,10.764872521246458,353,0.2997305530394474,56.657223796033996,353,0.0,0.0
calibration,1,enhanced_raw_75,91,-0.854460216158775,36.26373626373626,56,-0.4485695400460165,32.142857142857146,56,-0.5159405028427005,42.857142857142854,56,-0.26896307589285345,42.857142857142854,56,-0.4786001849425455,39.285714285714285,56,-0.4636817531612893,32.142857142857146,91,-2.1534603093876794,17.582417582417584,91,1.285134183909824,71.42857142857143,91,0.0,0.0
calibration,1,enhanced_adjusted_75,299,0.058952073225209255,57.859531772575245,99,-0.696202556203096,22.22222222222222,99,-0.7851179152697806,27.27272727272727,99,-0.6820869402383779,36.36363636363637,99,-0.6786859375647423,32.323232323232325,99,-0.711351363999576,22.22222222222222,299,-1.3146861093712825,19.063545150501675,299,1.5742095454413239,86.2876254180602,299,0.0,0.0
calibration,5,baseline_buy,36,-2.9776387386803838,16.666666666666664,8,-2.344793561052555,25.0,8,-2.762091049484569,25.0,8,-3.298667636876079,25.0,8,-1.9467910637130328,25.0,8,-2.419681144974889,25.0,36,-5.308235292639623,5.555555555555555,36,0.9177673958349539,63.888888888888886,36,-3.237509232988074,0.0
calibration,5,enhanced_shadow_buy,35,-2.979997180100014,17.142857142857142,7,-2.032271523347929,28.57142857142857,7,-2.449143133748387,28.57142857142857,7,-2.986145599171453,28.57142857142857,7,-1.785327609565621,28.57142857142857,7,-2.1071591072702627,28.57142857142857,35,-5.338159145861504,5.714285714285714,35,0.9335765788481604,62.857142857142854,35,-3.2760657439999576,0.0
calibration,5,enhanced_raw_75,17,-0.04139562487097425,47.05882352941176,15,-0.829953189571479,26.666666666666668,15,-1.24652195337172,26.666666666666668,15,-1.783827265395003,26.666666666666668,15,-0.775353975207382,26.666666666666668,15,-0.9048407734938132,26.666666666666668,17,-3.127349972072865,11.76470588235294,17,4.3083770919129485,100.0,17,-4.216403061890876,0.0
calibration,5,enhanced_adjusted_75,71,0.636897340353806,54.929577464788736,20,-0.6565650735182776,35.0,20,-1.0736638188688992,25.0,20,-1.6104391493418018,25.0,20,-0.6320276116085811,25.0,20,-0.7314526574406115,35.0,71,-2.410731001430457,9.859154929577464,71,4.767729116841769,100.0,71,-4.524405380409631,0.0
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
calibration,1,baseline,75-79,167,-3.879730841439086,-1.8786635032186374,14.37125748502994,2.209497653719629,-4.901699260206983,-3.879730841439086
calibration,1,baseline,80-84,0,,,,,,
calibration,1,baseline,85-89,0,,,,,,
calibration,1,baseline,90+,46,-2.819235589979695,-1.471143355246887,43.47826086956522,1.4835285953885387,-6.129054194109104,-2.819235589979695
calibration,1,raw,0-49,6,-2.2173622190915583,-2.2173622190915583,0.0,,-2.2173622190915583,-2.2173622190915583
calibration,1,raw,50-59,1,-13.59503346612777,-13.59503346612777,0.0,,-13.59503346612777,-13.59503346612777
calibration,1,raw,60-69,97,-6.457319512273781,-5.0396620680464075,13.402061855670103,2.108927245211834,-7.783048177122745,-6.457319512273781
calibration,1,raw,70-74,59,-1.843257514296911,-1.2771626823191136,11.864406779661017,2.31037266506261,-2.4024000384414617,-1.843257514296911
calibration,1,raw,75-79,56,-0.5159405028427005,-1.0040555130259843,42.857142857142854,1.6295771980770735,-2.125078778532531,-0.5159405028427005
calibration,1,raw,80-84,0,,,,,,
calibration,1,raw,85-89,0,,,,,,
calibration,1,raw,90+,0,,,,,,
calibration,1,adjusted,0-49,6,-2.2173622190915583,-2.2173622190915583,0.0,,-2.2173622190915583,-2.2173622190915583
calibration,1,adjusted,50-59,0,,,,,,
calibration,1,adjusted,60-69,23,-12.106563529343285,-5.537543318021666,0.0,,-12.106563529343285,-12.106563529343285
calibration,1,adjusted,70-74,91,-4.631013767832851,-4.190568120372015,18.681318681318682,2.269349002278532,-6.216232242047628,-4.631013767832851
calibration,1,adjusted,75-79,73,-1.2708824385990423,-1.2152307880484987,9.58904109589041,2.064144378648008,-1.6245974040646383,-1.2708824385990423
calibration,1,adjusted,80-84,26,0.5787594002316084,0.22251760767485734,76.92307692307693,1.4835285953885387,-2.4371379169581595,0.5787594002316084
calibration,1,adjusted,85-89,0,,,,,,
calibration,1,adjusted,90+,0,,,,,,
calibration,5,baseline,0-49,0,,,,,,
calibration,5,baseline,50-59,0,,,,,,
calibration,5,baseline,60-69,0,,,,,,
calibration,5,baseline,70-74,0,,,,,,
calibration,5,baseline,75-79,19,-3.125163260025703,-3.503442349350071,15.789473684210526,7.187544628838047,-5.058795989187656,-3.125163260025703
calibration,5,baseline,80-84,0,,,,,,
calibration,5,baseline,85-89,0,,,,,,
calibration,5,baseline,90+,8,-2.762091049484569,-3.4940663618562735,25.0,3.6664550458994847,-4.904939747945921,-2.762091049484569
calibration,5,raw,0-49,0,,,,,,
calibration,5,raw,50-59,0,,,,,,
calibration,5,raw,60-69,7,-8.571650565569561,-9.8368824863319,0.0,,-8.571650565569561,-8.571650565569561
calibration,5,raw,70-74,5,-0.5550894153604364,-0.25491048699706226,20.0,6.869258216204413,-2.4111763232516488,-0.5550894153604364
calibration,5,raw,75-79,15,-1.24652195337172,-3.49009150022842,26.666666666666668,5.506571440527175,-3.702192278425864,-1.24652195337172
calibration,5,raw,80-84,0,,,,,,
calibration,5,raw,85-89,0,,,,,,
calibration,5,raw,90+,0,,,,,,
calibration,5,adjusted,0-49,0,,,,,,
calibration,5,adjusted,50-59,0,,,,,,
calibration,5,adjusted,60-69,0,,,,,,
calibration,5,adjusted,70-74,7,-8.571650565569561,-9.8368824863319,0.0,,-8.571650565569561,-8.571650565569561
calibration,5,adjusted,75-79,15,0.2002423767106465,-0.6798322897357514,33.33333333333333,5.779108795662623,-2.589190832765341,0.2002423767106465
calibration,5,adjusted,80-84,5,-4.895382405607537,-3.498041223484127,0.0,,-4.895382405607537,-4.895382405607537
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
calibration,OPTIONS_DATA_PARTIAL,partial,42,82.14285714285714,72.25642857142857,74.73047619047618,100.0,15,-1.1459511323102687,9,-0.1741408727678907,0,,0,,0,
calibration,OPTIONS_DATA_PARTIAL,quote_only,70,85.71428571428571,72.47857142857141,74.97542857142858,100.0,41,-3.4672217851983858,0,,0,,0,,0,
calibration,OPTIONS_NOT_ELIGIBLE,unavailable,898,76.39198218262806,62.61961024498886,64.02212694877505,44.43207126948775,11,-2.481774051098582,0,,0,,0,,0,
calibration,OPTIONS_UNAVAILABLE,unavailable,519,79.96146435452793,69.34290944123315,71.49150289017342,100.0,153,-4.112631933424931,18,-4.439309026747439,0,,0,,0,
```

Availability is reported separately from the formula value. Missing options
data is never classified as an observed score of 50.

## Portfolio Fit cohorts

```csv
partition,cohort,predictions,raw_score_mean,adjusted_score_mean,net_alpha_spy_1d_n,net_alpha_spy_1d_mean,net_alpha_spy_1d_median,net_alpha_spy_1d_win_rate,net_alpha_spy_1d_average_gain,net_alpha_spy_1d_average_loss,net_alpha_spy_1d_expectancy,net_alpha_spy_5d_n,net_alpha_spy_5d_mean,net_alpha_spy_5d_median,net_alpha_spy_5d_win_rate,net_alpha_spy_5d_average_gain,net_alpha_spy_5d_average_loss,net_alpha_spy_5d_expectancy,net_alpha_spy_10d_n,net_alpha_spy_10d_mean,net_alpha_spy_10d_median,net_alpha_spy_10d_win_rate,net_alpha_spy_10d_average_gain,net_alpha_spy_10d_average_loss,net_alpha_spy_10d_expectancy,net_alpha_spy_20d_n,net_alpha_spy_20d_mean,net_alpha_spy_20d_median,net_alpha_spy_20d_win_rate,net_alpha_spy_20d_average_gain,net_alpha_spy_20d_average_loss,net_alpha_spy_20d_expectancy,net_alpha_spy_60d_n,net_alpha_spy_60d_mean,net_alpha_spy_60d_median,net_alpha_spy_60d_win_rate,net_alpha_spy_60d_average_gain,net_alpha_spy_60d_average_loss,net_alpha_spy_60d_expectancy
calibration,missing,499,65.95661322645292,65.95661322645292,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,other_observed,376,59.196063829787235,58.092207446808516,67,-0.8386892943473975,-1.2152307880484987,35.82089552238806,1.6295771980770735,-2.2163264063982657,-0.8386892943473975,15,-1.24652195337172,-3.49009150022842,26.666666666666668,5.506571440527175,-3.702192278425864,-1.24652195337172,0,,,,,,,0,,,,,,,0,,,,,,
calibration,raw_medium_fit_good,661,69.09812405446294,73.69760968229954,157,-4.768835792994918,-2.9900202601292225,12.738853503184714,2.1794331421596054,-5.7831816229444835,-4.768835792994918,12,-5.231416752982425,-5.902556576964851,8.333333333333332,6.869258216204413,-6.331478113817592,-5.231416752982425,0,,,,,,,0,,,,,,,0,,,,,,
```

## Component contribution and redundancy

```csv
partition,horizon,component,n,pearson_forward_alpha,spearman_forward_alpha,max_abs_component_correlation,incremental_r2
calibration,1,technical_score,224,0.03475110750235509,0.079390057854857,0.3698265292783915,
calibration,1,momentum_score,224,-0.05365560507488189,-0.09678406572823658,0.4811910985447782,
calibration,1,research_score,224,-0.09324403655221847,0.07901165196361976,0.35715414795192696,
calibration,1,volatility_score,224,-0.08407973369025092,-0.03583169789457392,0.27118395157836317,
calibration,1,liquidity_score,224,0.6588368997463513,0.7305415255680633,0.12827528074637354,
calibration,1,options_score,0,,,,
calibration,1,relative_opportunity_score,224,,,,
calibration,1,risk_reward_score,224,-0.11023450106464706,-0.2208671962204706,0.4811910985447782,
calibration,5,technical_score,27,0.03066239732295481,0.020827307784882405,0.3698265292783915,
calibration,5,momentum_score,27,0.0023571332486507,0.09436217659241672,0.4811910985447782,
calibration,5,research_score,27,0.5431347076447985,0.4645257966832583,0.35715414795192696,
calibration,5,volatility_score,27,-0.7158262129401632,-0.6336560478293971,0.27118395157836317,
calibration,5,liquidity_score,27,0.371404564933097,0.38311008304453553,0.12827528074637354,
calibration,5,options_score,0,,,,
calibration,5,relative_opportunity_score,27,,,,
calibration,5,risk_reward_score,27,0.44748007588056804,0.39644618191145775,0.4811910985447782,
calibration,10,technical_score,0,,,0.3698265292783915,
calibration,10,momentum_score,0,,,0.4811910985447782,
calibration,10,research_score,0,,,0.35715414795192696,
calibration,10,volatility_score,0,,,0.27118395157836317,
calibration,10,liquidity_score,0,,,0.12827528074637354,
calibration,10,options_score,0,,,,
calibration,10,relative_opportunity_score,0,,,,
calibration,10,risk_reward_score,0,,,0.4811910985447782,
calibration,20,technical_score,0,,,0.3698265292783915,
calibration,20,momentum_score,0,,,0.4811910985447782,
calibration,20,research_score,0,,,0.35715414795192696,
calibration,20,volatility_score,0,,,0.27118395157836317,
calibration,20,liquidity_score,0,,,0.12827528074637354,
calibration,20,options_score,0,,,,
calibration,20,relative_opportunity_score,0,,,,
calibration,20,risk_reward_score,0,,,0.4811910985447782,
calibration,60,technical_score,0,,,0.3698265292783915,
calibration,60,momentum_score,0,,,0.4811910985447782,
calibration,60,research_score,0,,,0.35715414795192696,
calibration,60,volatility_score,0,,,0.27118395157836317,
calibration,60,liquidity_score,0,,,0.12827528074637354,
calibration,60,options_score,0,,,,
calibration,60,relative_opportunity_score,0,,,,
calibration,60,risk_reward_score,0,,,0.4811910985447782,
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
5522e100effd8a5697d20573,2026-09-10T21:10:03+00:00,calibration,TRGP,BUY,WAIT,73.1,100.0,77.13,-3.6307914717671,-4.952726459637843,,,
53c26794356af012cc307291,2026-09-11T06:44:58+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-19.383814384315958,,,,
8ca424c3afa2faff80cd5fa8,2026-09-11T08:54:52+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186612984672122,,,,
3457725c926d4c9bca6c86ef,2026-09-11T09:29:41+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186612984672122,,,,
62964736889913e1a2f9310e,2026-09-11T11:00:53+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186612984672122,,,,
f210d637d4e1bb82d574ae0b,2026-09-11T11:21:56+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186612984672122,,,,
67f32e63bb66249fa1c7fee3,2026-09-11T11:38:56+00:00,calibration,TRGP,BUY,WAIT,69.31,100.0,73.91,-7.186612984672122,,,,
fb9cc1abbfcca2453eec217b,2026-09-15T20:21:08+00:00,calibration,ELV,BUY,WAIT,67.59,100.0,72.45,-5.42223799596124,,,,
fabca3d3e4bba17e1172975c,2026-09-16T05:40:32+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
fabca3d3e4bba17e1172975c,2026-09-16T05:40:32+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-11.62192110189681,,,,
e1338d825a461549ab9e718a,2026-09-16T05:50:47+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
e1338d825a461549ab9e718a,2026-09-16T05:50:47+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-11.62192110189681,,,,
e991d1db51ca3517cd30ca69,2026-09-16T05:54:18+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
e991d1db51ca3517cd30ca69,2026-09-16T05:54:18+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-11.62192110189681,,,,
92e9fb98a9868fa5713aaf9d,2026-09-16T06:00:15+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
92e9fb98a9868fa5713aaf9d,2026-09-16T06:00:15+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-11.62192110189681,,,,
3f6b3bd68f68e3e0a4cb2309,2026-09-16T06:03:42+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
3f6b3bd68f68e3e0a4cb2309,2026-09-16T06:03:42+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-11.62192110189681,,,,
```

## BUY / WAIT / AVOID transition matrix

```csv
partition,baseline_decision,enhanced_decision,predictions
calibration,BUY,BUY,399
calibration,BUY,WAIT,18
calibration,BUY,AVOID,0
calibration,WAIT,BUY,0
calibration,WAIT,WAIT,945
calibration,WAIT,AVOID,0
calibration,AVOID,BUY,0
calibration,AVOID,WAIT,0
calibration,AVOID,AVOID,174
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
