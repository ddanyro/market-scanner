# Enhanced Scoring forward validation

Generated: 2026-10-06T11:16:30+00:00

## Data coverage

```csv
partition,predictions,execution_eligible_pct,options_pct,options_partial_pct,portfolio_fit_pct,matured_1d,matured_5d,matured_10d,matured_20d,matured_60d
calibration,3719,92.44420543156762,0.0,4.920677601505781,81.95751546114548,3579,3044,2120,0,0
holdout_locked,0,,,,,0,0,0,0,0
```

## Gross, net and benchmark alpha

```csv
partition,horizon,metric,n,mean,median,win_rate,average_gain,average_loss,expectancy
calibration,1,gross_return_pct,3316,-0.30189045260324027,-0.5760647021098908,40.5307599517491,2.7871548356984928,-2.435610487435156,-0.30189045260324027
calibration,1,net_return_pct,365,-3.223562314992833,-1.6613930059688193,21.095890410958905,1.9851025619046074,-4.616156743885551,-3.223562314992833
calibration,1,spy_return_pct,3316,0.16340055139012938,-0.027482565078118526,47.91917973462002,0.9360549799850176,-0.5475131064195272,0.16340055139012938
calibration,1,qqq_return_pct,3316,0.5093691727676299,0.1900755733859283,57.237635705669476,1.4396719179537523,-0.7358456441317072,0.5093691727676299
calibration,1,sector_return_pct,1667,0.09490363803602331,0.017573947314764027,50.749850029994,1.1972436471197296,-1.0410033627981006,0.09490363803602331
calibration,1,cash_return_pct,3316,0.015456137789465496,0.015481020533281153,100.0,0.015456137789465496,,0.015456137789465496
calibration,1,gross_alpha_spy_pct,3316,-0.46529100399336965,-0.6020570829206151,41.073582629674306,2.6288114876630795,-2.621978615884917,-0.46529100399336965
calibration,1,net_alpha_spy_pct,365,-3.4101439369134376,-1.878660376211584,19.726027397260275,2.0288954981005856,-4.746699702514154,-3.4101439369134376
calibration,1,net_alpha_qqq_pct,365,-3.7191385120163942,-2.036221536598835,19.17808219178082,2.04465419795667,-5.086818138111698,-3.7191385120163942
calibration,1,net_alpha_sector_pct,346,-3.558485630601033,-1.906273395105545,19.942196531791907,1.189175212241563,-4.741115948854243,-3.558485630601033
calibration,1,net_alpha_cash_pct,365,-3.238901446560047,-1.676625842475415,20.0,2.0779840761670476,-4.568122827241821,-3.238901446560047
calibration,5,gross_return_pct,2834,-1.419756678965843,-1.7839870057113294,36.48553281580805,4.32966895746871,-4.722482294562136,-1.419756678965843
calibration,5,net_return_pct,343,-3.543188648456592,-2.6078547276420796,26.53061224489796,3.509249411917189,-6.089902392480459,-3.543188648456592
calibration,5,spy_return_pct,2834,0.471054657805238,0.45116240333478164,54.37544107268878,1.2885270756787346,-0.5032106136124407,0.471054657805238
calibration,5,qqq_return_pct,2834,2.081068561844812,1.1442506226506444,85.4622441778405,2.5723607213443827,-0.8070615602618846,2.081068561844812
calibration,5,sector_return_pct,1458,0.061115250698946105,-0.1103509522067947,49.17695473251029,2.0391471175238896,-1.8528508066741771,0.061115250698946105
calibration,5,cash_return_pct,2834,0.07714290153060914,0.07727629116887069,100.0,0.07714290153060914,,0.07714290153060914
calibration,5,gross_alpha_spy_pct,2834,-1.890811336771081,-2.031346908740217,34.89767113620324,4.114315929946629,-5.109819936653907,-1.890811336771081
calibration,5,net_alpha_spy_pct,343,-4.0912398032702075,-3.3344973598515564,24.78134110787172,3.2422074900857893,-6.507298020073539,-4.0912398032702075
calibration,5,net_alpha_qqq_pct,343,-5.696298149020639,-4.56226993223638,15.743440233236154,3.328006746169358,-7.382500447775863,-5.696298149020639
calibration,5,net_alpha_sector_pct,324,-4.064196154108538,-2.6791054438460717,18.51851851851852,3.145219664606277,-5.702699749270996,-4.064196154108538
calibration,5,net_alpha_cash_pct,343,-3.619786954630643,-2.68679189826201,25.65597667638484,3.550455059697887,-6.0942234144773515,-3.619786954630643
calibration,10,gross_return_pct,1974,-2.8847682723522463,-3.0991723714781205,26.342451874366766,6.877822126960438,-6.384986277990882,-2.8847682723522463
calibration,10,net_return_pct,284,-3.36198547767366,-4.438800305997008,27.11267605633803,7.601682134890028,-7.440257971235997,-3.36198547767366
calibration,10,spy_return_pct,1974,1.0913276681705792,1.0437333597083764,100.0,1.0913276681705792,,1.0913276681705792
calibration,10,qqq_return_pct,1974,4.313150732983925,4.251870987000683,100.0,4.313150732983925,,4.313150732983925
calibration,10,sector_return_pct,1034,0.17359125334577424,-0.6057389921431677,44.00386847195358,3.488215465655649,-2.43116525201,0.17359125334577424
calibration,10,cash_return_pct,1974,0.15307894847556658,0.15358005952033071,100.0,0.15307894847556658,,0.15307894847556658
calibration,10,gross_alpha_spy_pct,1974,-3.9760959405228258,-4.078136182017844,21.27659574468085,7.3241136502516255,-7.030206640732136,-3.9760959405228258
calibration,10,net_alpha_spy_pct,284,-4.673901722273994,-5.632368224495821,26.056338028169012,6.624863988007061,-8.65537154399208,-4.673901722273994
calibration,10,net_alpha_qqq_pct,284,-7.948070478170741,-8.83340270145495,21.830985915492956,4.517602444695749,-11.429474627800118,-7.948070478170741
calibration,10,net_alpha_sector_pct,271,-4.249056278082654,-4.53968847519115,19.92619926199262,6.251346896156728,-6.8620598329625,-4.249056278082654
calibration,10,net_alpha_cash_pct,284,-3.5145507778282337,-4.591233131178189,26.408450704225352,7.649641652062756,-7.5208399273106465,-3.5145507778282337
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
calibration,1,baseline_buy,727,0.6648584483613148,42.50343878954608,66,-2.6033294685638686,25.757575757575758,66,-2.693436484488241,37.878787878787875,66,-2.8373180850388215,34.84848484848485,66,-2.551999687629187,37.878787878787875,66,-2.618624182209299,25.757575757575758,727,-0.8755851597672418,21.320495185694636,727,1.9081344950427315,72.07702888583218,727,0.0,0.0
calibration,1,enhanced_shadow_buy,706,0.8111383979070358,43.76770538243626,50,-0.31289621430869985,34.0,50,-0.3227649809294343,50.0,50,-0.4242154170126344,46.0,50,-0.3265950109730774,50.0,50,-0.3282022029759636,34.0,706,-0.7451548862443474,21.95467422096317,706,2.0289605554424477,73.93767705382436,706,0.0,0.0
calibration,1,enhanced_raw_75,189,0.9294801780428094,34.39153439153439,86,-0.6763475704132026,30.23255813953488,86,-0.6600238898742279,33.72093023255814,86,-0.6986033999019928,31.3953488372093,86,-0.7631140767166306,29.069767441860467,86,-0.6916685646215979,30.23255813953488,189,-0.9308902379248314,17.46031746031746,189,2.8967216192327996,62.96296296296296,189,0.0,0.0
calibration,1,enhanced_adjusted_75,731,0.6783764139190677,48.97400820793434,171,-0.8853985094023923,25.730994152046783,171,-1.087545165029229,23.391812865497073,171,-1.3604991744026433,24.561403508771928,171,-0.9892904452841289,23.391812865497073,171,-0.9007519718038636,25.730994152046783,731,-0.8019064746406686,21.751025991792066,731,2.188156029651326,80.71135430916553,731,0.0,0.0
calibration,5,baseline_buy,579,-0.5088654269841442,40.75993091537133,58,-1.708415923671703,43.103448275862064,58,-2.1449843188859767,43.103448275862064,58,-3.47205856605268,25.862068965517242,58,-1.18287103980672,27.586206896551722,58,-1.7846184432712042,43.103448275862064,579,-3.814028891448625,10.01727115716753,579,2.932364087208106,90.84628670120898,579,-2.587934741926315,0.0
calibration,5,enhanced_shadow_buy,559,-0.44651104387088025,41.32379248658318,43,0.052135710060347826,58.139534883720934,43,-0.20522258149076178,58.139534883720934,43,-1.2815226619696438,34.883720930232556,43,0.4805977616137609,37.2093023255814,43,-0.024058024125892405,58.139534883720934,559,-3.7195383604246,10.37567084078712,559,3.0411340997881586,92.84436493738819,559,-2.632951212229084,0.0
calibration,5,enhanced_raw_75,154,-1.3252761512624922,37.01298701298701,76,-0.21584826923187733,55.26315789473685,76,-0.5659722261881935,52.63157894736842,76,-1.6030832065196179,30.263157894736842,76,-0.4257476723869349,31.57894736842105,76,-0.29220509799796635,51.31578947368421,154,-4.895144637417031,12.337662337662337,154,2.436960277226563,68.83116883116884,154,-2.73990642243482,0.0
calibration,5,enhanced_adjusted_75,619,0.08723382532618387,46.52665589660743,156,-1.4411638257732975,36.53846153846153,156,-2.0174861318601174,30.76923076923077,156,-3.4279906163992493,17.94871794871795,156,-1.8309961661531788,22.435897435897438,156,-1.5177718435069472,34.61538461538461,619,-3.134164413561812,13.5702746365105,619,3.422033361151087,91.92245557350566,619,-2.7389787572780455,0.0
calibration,10,baseline_buy,466,-2.248836895819084,24.892703862660944,50,-0.04999926522536145,46.0,50,-1.4462592468047797,44.0,50,-4.667427142811323,24.0,50,-0.08608147175900058,32.0,50,-0.2018059449988793,46.0,466,-6.484066040831237,12.446351931330472,466,4.477539647449782,91.20171673819742,466,-6.365751178196891,0.0
calibration,10,enhanced_shadow_buy,448,-2.061419033659626,25.892857142857146,37,4.048001314804401,62.16216216216216,37,2.689766836797996,59.45945945945946,37,-0.40650836522467537,32.432432432432435,37,2.9284790021378613,43.24324324324324,37,3.8962138786909546,62.16216216216216,448,-6.433483191038921,12.946428571428573,448,4.660388134603029,93.52678571428571,448,-6.395640106785452,0.0
calibration,10,enhanced_raw_75,128,-0.30197816536143296,42.1875,59,2.1928275738763907,54.23728813559322,59,0.7862587677356404,52.54237288135594,59,-2.3257818645829578,35.59322033898305,59,1.488690358723188,45.76271186440678,59,2.041414836050061,54.23728813559322,128,-6.364470523736288,14.0625,128,4.996969115621882,81.25,128,-5.154454434668951,0.0
calibration,10,enhanced_adjusted_75,400,1.2613503954316572,48.25,126,-0.06571207357802164,34.92063492063492,126,-1.3854417011477527,32.53968253968254,126,-4.567551106638419,24.6031746031746,126,-0.9501413756456613,26.984126984126984,126,-0.21801633729229908,33.33333333333333,400,-4.0786251485849085,14.499999999999998,400,6.395882546409454,96.0,400,-5.236887753267988,0.0
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
calibration,1,baseline,75-79,290,-3.7086543913911147,-1.9980572252951636,15.172413793103448,1.7985361279634189,-4.693680337942333,-3.7086543913911147
calibration,1,baseline,80-84,0,,,,,,
calibration,1,baseline,85-89,0,,,,,,
calibration,1,baseline,90+,66,-2.693436484488241,-1.5326589743804258,37.878787878787875,1.802667486964101,-5.434963296349426,-2.693436484488241
calibration,1,raw,0-49,9,0.9526716118046856,-1.635653061669053,33.33333333333333,7.292733019583067,-2.217359092084505,0.9526716118046856
calibration,1,raw,50-59,15,-4.466788275872935,-0.5917781237302198,26.666666666666668,4.389938816379541,-7.68741630941929,-4.466788275872935
calibration,1,raw,60-69,152,-6.148039060074602,-5.039658941039354,13.815789473684212,1.421096912287143,-7.361412002208928,-6.148039060074602
calibration,1,raw,70-74,103,-1.893308404670195,-1.742285144192715,14.563106796116504,2.1514408733840993,-2.5827543043385406,-1.893308404670195
calibration,1,raw,75-79,86,-0.6600238898742279,-1.1239976046873685,33.72093023255814,1.5354439062132177,-1.7770162773573144,-0.6600238898742279
calibration,1,raw,80-84,0,,,,,,
calibration,1,raw,85-89,0,,,,,,
calibration,1,raw,90+,0,,,,,,
calibration,1,adjusted,0-49,9,0.9526716118046856,-1.635653061669053,33.33333333333333,7.292733019583067,-2.217359092084505,0.9526716118046856
calibration,1,adjusted,50-59,10,1.161417404334013,-0.5074705437891122,40.0,4.389938816379541,-0.9909302036963382,1.161417404334013
calibration,1,adjusted,60-69,41,-10.855141598536099,-5.7667375155516325,0.0,,-10.855141598536099,-10.855141598536099
calibration,1,adjusted,70-74,134,-4.730296468380665,-3.902111740105438,18.65671641791045,1.6402370606815768,-6.191428011743567,-4.730296468380665
calibration,1,adjusted,75-79,126,-1.4751589223158599,-1.4493845699370018,13.492063492063492,1.914812116770412,-2.003870001806379,-1.4751589223158599
calibration,1,adjusted,80-84,45,-0.0022266446266616226,0.22252073468191064,51.11111111111111,1.4384690885581908,-1.5084085475017346,-0.0022266446266616226
calibration,1,adjusted,85-89,0,,,,,,
calibration,1,adjusted,90+,0,,,,,,
calibration,5,baseline,0-49,0,,,,,,
calibration,5,baseline,50-59,9,5.331020449401777,6.323941978104684,100.0,5.331020449401777,,5.331020449401777
calibration,5,baseline,60-69,0,,,,,,
calibration,5,baseline,70-74,0,,,,,,
calibration,5,baseline,75-79,276,-4.807483137938081,-3.6235112159675,18.478260869565215,3.2641158512442785,-6.6370455754860815,-4.807483137938081
calibration,5,baseline,80-84,0,,,,,,
calibration,5,baseline,85-89,0,,,,,,
calibration,5,baseline,90+,58,-2.1449843188859767,-1.6030737459526534,43.103448275862064,2.4455417679687144,-5.622655596806198,-2.1449843188859767
calibration,5,raw,0-49,9,5.331020449401777,6.323941978104684,100.0,5.331020449401777,,5.331020449401777
calibration,5,raw,50-59,15,-4.863190022688352,-0.08011766427946188,46.666666666666664,3.3174324434438494,-12.02123468055403,-4.863190022688352
calibration,5,raw,60-69,146,-6.7215505916841085,-5.778200448085514,14.383561643835616,4.592463875569923,-8.622305022182784,-6.7215505916841085
calibration,5,raw,70-74,97,-3.649137223193702,-3.3344973598515564,8.24742268041237,3.278983888074783,-4.2718896826335655,-3.649137223193702
calibration,5,raw,75-79,76,-0.5659722261881935,0.76284974086213,52.63157894736842,2.042820325425062,-3.4646306168695884,-0.5659722261881935
calibration,5,raw,80-84,0,,,,,,
calibration,5,raw,85-89,0,,,,,,
calibration,5,raw,90+,0,,,,,,
calibration,5,adjusted,0-49,9,5.331020449401777,6.323941978104684,100.0,5.331020449401777,,5.331020449401777
calibration,5,adjusted,50-59,10,2.2981674111268555,2.633646132944677,70.0,3.3174324434438494,-0.08011766427946188,2.2981674111268555
calibration,5,adjusted,60-69,41,-11.521483326702135,-8.613522074090584,2.4390243902439024,3.0672009047650444,-11.886200432488815,-11.521483326702135
calibration,5,adjusted,70-74,127,-5.410609903248817,-5.258900856963094,15.748031496062993,4.668727024110166,-7.294598113970121,-5.410609903248817
calibration,5,adjusted,75-79,116,-2.7852504457216307,-3.167853582291407,14.655172413793101,3.443663244482298,-3.8548618874738203,-2.7852504457216307
calibration,5,adjusted,80-84,40,0.20903037833827254,0.7860842697011732,77.5,1.5936260956581185,-4.560132647985642,0.20903037833827254
calibration,5,adjusted,85-89,0,,,,,,
calibration,5,adjusted,90+,0,,,,,,
calibration,10,baseline,0-49,0,,,,,,
calibration,10,baseline,50-59,9,8.5884379222179,7.4894693503487515,100.0,8.5884379222179,,8.5884379222179
calibration,10,baseline,60-69,0,,,,,,
calibration,10,baseline,70-74,0,,,,,,
calibration,10,baseline,75-79,225,-5.921649191491272,-6.12782497350505,19.11111111111111,5.1232220342372585,-8.53115173383373,-5.921649191491272
calibration,10,baseline,80-84,0,,,,,,
calibration,10,baseline,85-89,0,,,,,,
calibration,10,baseline,90+,50,-1.4462592468047797,-1.6439743496492454,44.0,8.756611197289068,-9.46280031002137,-1.4462592468047797
calibration,10,raw,0-49,9,8.5884379222179,7.4894693503487515,100.0,8.5884379222179,,8.5884379222179
calibration,10,raw,50-59,9,-6.669198219265581,-11.759695064525399,44.44444444444444,10.622350910264545,-20.502437522889686,-6.669198219265581
calibration,10,raw,60-69,124,-8.407372889833587,-7.268544553484,16.129032258064516,4.600059067900804,-10.908802112474815,-8.407372889833587
calibration,10,raw,70-74,83,-4.199232233848473,-3.5643250257619306,12.048192771084338,3.771157709148075,-5.291066472615124,-4.199232233848473
calibration,10,raw,75-79,59,0.7862587677356404,1.0042993627665613,52.54237288135594,7.765865539419567,-6.941163015200132,0.7862587677356404
calibration,10,raw,80-84,0,,,,,,
calibration,10,raw,85-89,0,,,,,,
calibration,10,raw,90+,0,,,,,,
calibration,10,adjusted,0-49,9,8.5884379222179,7.4894693503487515,100.0,8.5884379222179,,8.5884379222179
calibration,10,adjusted,50-59,4,10.622350910264545,11.113754683599067,100.0,10.622350910264545,,10.622350910264545
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
calibration,OPTIONS_DATA_PARTIAL,partial,78,82.6923076923077,73.20961538461539,75.78935897435898,100.0,39,-1.2676282376101409,33,-1.3663918398025339,15,-3.4918903093614015,0,,0,
calibration,OPTIONS_DATA_PARTIAL,quote_only,98,84.6938775510204,73.00459183673469,75.56010204081633,100.0,62,-3.8682501643750187,59,-3.5157828430109386,56,-4.169339731615607,0,,0,
calibration,OPTIONS_NOT_ELIGIBLE,unavailable,2077,71.03996148290804,61.16994222436206,62.411169956668274,70.77515647568609,32,0.2241626243877567,32,4.288137526135862,20,8.447994914718972,0,,0,
calibration,OPTIONS_UNAVAILABLE,unavailable,1459,81.03152844413982,69.88786154900616,72.09705277587389,95.61343385880741,241,-4.093775578774441,228,-5.400837677214521,196,-6.221084056961872,0,,0,
```

Availability is reported separately from the formula value. Missing options
data is never classified as an observed score of 50.

## Portfolio Fit cohorts

```csv
partition,cohort,predictions,raw_score_mean,adjusted_score_mean,net_alpha_spy_1d_n,net_alpha_spy_1d_mean,net_alpha_spy_1d_median,net_alpha_spy_1d_win_rate,net_alpha_spy_1d_average_gain,net_alpha_spy_1d_average_loss,net_alpha_spy_1d_expectancy,net_alpha_spy_5d_n,net_alpha_spy_5d_mean,net_alpha_spy_5d_median,net_alpha_spy_5d_win_rate,net_alpha_spy_5d_average_gain,net_alpha_spy_5d_average_loss,net_alpha_spy_5d_expectancy,net_alpha_spy_10d_n,net_alpha_spy_10d_mean,net_alpha_spy_10d_median,net_alpha_spy_10d_win_rate,net_alpha_spy_10d_average_gain,net_alpha_spy_10d_average_loss,net_alpha_spy_10d_expectancy,net_alpha_spy_20d_n,net_alpha_spy_20d_mean,net_alpha_spy_20d_median,net_alpha_spy_20d_win_rate,net_alpha_spy_20d_average_gain,net_alpha_spy_20d_average_loss,net_alpha_spy_20d_expectancy,net_alpha_spy_60d_n,net_alpha_spy_60d_mean,net_alpha_spy_60d_median,net_alpha_spy_60d_win_rate,net_alpha_spy_60d_average_gain,net_alpha_spy_60d_average_loss,net_alpha_spy_60d_expectancy
calibration,missing,671,65.28760059612519,65.28760059612519,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,other_observed,1490,60.43857718120806,58.26102684563758,118,-0.4202444961760625,-1.195445549277958,32.20338983050847,2.480818334570675,-1.7982493407807627,-0.4202444961760625,108,0.8722825152411564,0.7860842697011732,63.888888888888886,3.1764285050172236,-3.2042834666703475,0.8722825152411564,79,2.725938804946611,4.097391012531979,64.55696202531645,8.033367255223252,-6.941163015200132,2.725938804946611,0,,,,,,,0,,,,,,
calibration,raw_high_fit_weak,25,75.14040000000001,69.37280000000001,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,raw_medium_fit_good,1533,69.57303979125896,74.12173515981735,260,-4.6466488499761684,-3.027009386936208,13.846153846153847,1.7254068960775415,-5.6707292377347995,-4.6466488499761684,248,-5.771137989867994,-4.007013197948169,11.693548387096774,4.230124568674712,-7.0955060912275325,-5.771137989867994,212,-7.045107081902057,-6.700691499509045,14.150943396226415,4.3237586149832286,-8.919095933036996,-7.045107081902057,0,,,,,,,0,,,,,,
```

## Component contribution and redundancy

```csv
partition,horizon,component,n,pearson_forward_alpha,spearman_forward_alpha,max_abs_component_correlation,incremental_r2
calibration,1,technical_score,378,-0.009803249232747198,0.05287191267167055,0.3474800886164778,
calibration,1,momentum_score,378,-0.11933911044582997,-0.15711768498862863,0.535050351261163,
calibration,1,research_score,378,-0.09991343890890629,0.002703653025931063,0.428295239743896,
calibration,1,volatility_score,378,-0.1180039516896287,-0.06884714886189636,0.3474800886164777,
calibration,1,liquidity_score,378,0.6221023124128005,0.6213124892175368,0.16390040169423045,
calibration,1,options_score,0,,,,
calibration,1,relative_opportunity_score,378,,,,
calibration,1,risk_reward_score,378,-0.17659815772149587,-0.18656370629452737,0.5350503512611631,
calibration,5,technical_score,356,-0.04642630628833599,-0.04642147998599391,0.3474800886164778,
calibration,5,momentum_score,356,-0.29298611755517584,-0.33981610316021893,0.535050351261163,
calibration,5,research_score,356,-0.18021544466979264,-0.08187070300495797,0.428295239743896,
calibration,5,volatility_score,356,-0.18715051164129853,-0.05058301650503771,0.3474800886164777,
calibration,5,liquidity_score,356,0.5190448026788382,0.5112637712815111,0.16390040169423045,
calibration,5,options_score,0,,,,
calibration,5,relative_opportunity_score,356,,,,
calibration,5,risk_reward_score,356,-0.26032260115314143,-0.2471540243174577,0.5350503512611631,
calibration,10,technical_score,291,-0.028647715004605046,-0.07119140855697662,0.3474800886164778,
calibration,10,momentum_score,291,-0.2887763816454076,-0.23029085319248152,0.535050351261163,
calibration,10,research_score,291,-0.1716949647806451,-0.08108359451263372,0.428295239743896,
calibration,10,volatility_score,291,-0.15485726858862894,-0.1306363428001908,0.3474800886164777,
calibration,10,liquidity_score,291,0.45979967876598427,0.45436699709459366,0.16390040169423045,
calibration,10,options_score,0,,,,
calibration,10,relative_opportunity_score,291,,,,
calibration,10,risk_reward_score,291,-0.2711104116541518,-0.2231496670643041,0.5350503512611631,
calibration,20,technical_score,0,,,0.3474800886164778,
calibration,20,momentum_score,0,,,0.535050351261163,
calibration,20,research_score,0,,,0.428295239743896,
calibration,20,volatility_score,0,,,0.3474800886164777,
calibration,20,liquidity_score,0,,,0.16390040169423045,
calibration,20,options_score,0,,,,
calibration,20,relative_opportunity_score,0,,,,
calibration,20,risk_reward_score,0,,,0.5350503512611631,
calibration,60,technical_score,0,,,0.3474800886164778,
calibration,60,momentum_score,0,,,0.535050351261163,
calibration,60,research_score,0,,,0.428295239743896,
calibration,60,volatility_score,0,,,0.3474800886164777,
calibration,60,liquidity_score,0,,,0.16390040169423045,
calibration,60,options_score,0,,,,
calibration,60,relative_opportunity_score,0,,,,
calibration,60,risk_reward_score,0,,,0.5350503512611631,
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
8a474d0fe7e76b1f968ebf69,2026-10-03T11:19:04+00:00,calibration,IEX,BUY,WAIT,66.92,100.0,71.88,-31.891351442275305,,,,
```

## BUY / WAIT / AVOID transition matrix

```csv
partition,baseline_decision,enhanced_decision,predictions
calibration,BUY,BUY,804
calibration,BUY,WAIT,21
calibration,BUY,AVOID,0
calibration,WAIT,BUY,0
calibration,WAIT,WAIT,2406
calibration,WAIT,AVOID,0
calibration,AVOID,BUY,0
calibration,AVOID,WAIT,0
calibration,AVOID,AVOID,488
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
