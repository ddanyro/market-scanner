# Enhanced Scoring forward validation

Generated: 2026-09-24T07:35:34+00:00

## Data coverage

```csv
partition,predictions,execution_eligible_pct,options_pct,options_partial_pct,portfolio_fit_pct,matured_1d,matured_5d,matured_10d,matured_20d,matured_60d
calibration,2474,92.64349232012935,0.0,6.1034761519805985,77.52627324171382,2278,1175,14,0,0
holdout_locked,0,,,,,0,0,0,0,0
```

## Gross, net and benchmark alpha

```csv
partition,horizon,metric,n,mean,median,win_rate,average_gain,average_loss,expectancy
calibration,1,gross_return_pct,2108,-0.736192265431658,-0.6896525963969613,39.08918406072106,2.0996463578719906,-2.5560762417573635,-0.736192265431658
calibration,1,net_return_pct,286,-3.360461170220259,-1.6613930059688193,23.076923076923077,2.0833797474524767,-4.9936134455220795,-3.360461170220259
calibration,1,spy_return_pct,2108,0.28659885679743097,0.24789671462555063,52.46679316888046,1.0458299283038774,-0.5514346412925191,0.28659885679743097
calibration,1,qqq_return_pct,2108,0.7416211055005115,0.09091013277680027,56.64136622390892,1.8751268099305296,-0.7391292348599275,0.7416211055005115
calibration,1,sector_return_pct,1090,0.16460437701588915,-0.0921488989446606,48.53211009174312,1.5295420033564584,-1.1224758446136314,0.16460437701588915
calibration,1,cash_return_pct,2108,0.01531243709508499,0.015347402188981007,100.0,0.01531243709508499,,0.01531243709508499
calibration,1,gross_alpha_spy_pct,2108,-1.0227911222290889,-0.8116954905658558,37.80834914611006,2.022731989901514,-2.8742647456982655,-1.0227911222290889
calibration,1,net_alpha_spy_pct,286,-3.727778336556066,-2.1022909812115596,19.58041958041958,2.2163076566338424,-5.175034056637087,-3.727778336556066
calibration,1,net_alpha_qqq_pct,286,-3.980866781900591,-2.447890325586834,22.377622377622377,2.007696715843869,-5.707299501971067,-3.980866781900591
calibration,1,net_alpha_sector_pct,272,-3.8405959390578026,-2.0430879028668674,19.485294117647058,1.1574111086655399,-5.050159288506831,-3.8405959390578026
calibration,1,net_alpha_cash_pct,286,-3.3757089842431456,-1.676625842475415,22.377622377622377,2.1328066983085363,-4.963749541375162,-3.3757089842431456
calibration,5,gross_return_pct,1087,-1.9248462723945767,-2.08588887987351,30.358785648574056,3.482877750814724,-4.282242478020824,-1.9248462723945767
calibration,5,net_return_pct,189,-3.7860376585715585,-2.9122457545384752,26.455026455026452,2.522350794792903,-6.0552421381990635,-3.7860376585715585
calibration,5,spy_return_pct,1087,0.5395363097420639,-0.09270593630656965,48.85004599816008,1.4000150041654518,-0.2822517959032938,0.5395363097420639
calibration,5,qqq_return_pct,1087,2.0477700508019887,0.9190367823633139,91.72033118675253,2.392891036058458,-1.7754035303168993,2.0477700508019887
calibration,5,sector_return_pct,538,-0.49076271680796696,-1.2708482463150483,36.80297397769517,1.7440663525285562,-1.7922219983627656,-0.49076271680796696
calibration,5,cash_return_pct,1087,0.07588916860062546,0.07618738999861652,100.0,0.07588916860062546,,0.07588916860062546
calibration,5,gross_alpha_spy_pct,1087,-2.4643825821366403,-2.159921802228293,27.782888684452622,3.2436404339204357,-4.660335385766242,-2.4643825821366403
calibration,5,net_alpha_spy_pct,189,-4.122850237749344,-3.167853582291407,21.693121693121693,2.7501077849218984,-6.026845365651513,-4.122850237749344
calibration,5,net_alpha_qqq_pct,189,-5.246310361930903,-4.202132435641859,14.814814814814813,2.746410243603436,-6.63634872811079,-5.246310361930903
calibration,5,net_alpha_sector_pct,178,-3.587469153081078,-1.9929380983985538,16.292134831460675,3.2672155699041667,-4.921602421313106,-3.587469153081078
calibration,5,net_alpha_cash_pct,189,-3.86177029753247,-2.9884331445370917,26.455026455026452,2.446375647225251,-6.130887543848196,-3.86177029753247
calibration,10,gross_return_pct,14,-9.564279976244563,-10.48593350383632,0.0,,-9.564279976244563,-9.564279976244563
calibration,10,net_return_pct,0,,,,,,
calibration,10,spy_return_pct,14,0.8410792987952157,0.8584817081878526,100.0,0.8410792987952157,,0.8410792987952157
calibration,10,qqq_return_pct,14,3.4366767075496534,3.4020851620080395,100.0,3.4366767075496534,,3.4366767075496534
calibration,10,sector_return_pct,6,-4.240234443741339,-4.224977667623198,0.0,,-4.240234443741339,-4.240234443741339
calibration,10,cash_return_pct,14,0.14814700226399222,0.14810871859305408,100.0,0.14814700226399222,,0.14814700226399222
calibration,10,gross_alpha_spy_pct,14,-10.40535927503978,-11.331214395143864,0.0,,-10.40535927503978,-10.40535927503978
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
calibration,1,baseline_buy,477,-0.05862944804244133,36.68763102725367,51,-2.66694862883575,23.52941176470588,51,-2.8857710296694763,39.21568627450981,51,-2.9056733296867727,39.21568627450981,51,-2.7182869521737234,39.21568627450981,51,-2.6821253267757403,23.52941176470588,477,-1.6819531687776303,18.448637316561843,477,1.1688263292836174,63.312368972746334,477,0.0,0.0
calibration,1,enhanced_shadow_buy,458,0.12586089711497886,38.209606986899566,37,-0.33651956181811116,32.432432432432435,37,-0.488857684885377,54.054054054054056,37,-0.39355519906895176,54.054054054054056,37,-0.5286083712075704,54.054054054054056,37,-0.3516879464638879,32.432432432432435,458,-1.524662942914666,19.213973799126638,458,1.312645861719847,65.72052401746726,458,0.0,0.0
calibration,1,enhanced_raw_75,130,-1.218339037780008,32.30769230769231,59,-0.42061946108410087,35.59322033898305,59,-0.5634019052667595,40.67796610169492,59,-0.3966884328482853,40.67796610169492,59,-0.6472724145468864,37.28813559322034,59,-0.4357504271189335,35.59322033898305,130,-3.276112933205413,19.230769230769234,130,0.9932492896780983,56.92307692307692,130,0.0,0.0
calibration,1,enhanced_adjusted_75,424,0.6111195367117591,58.25471698113207,127,-0.7888076718142777,28.346456692913385,127,-1.1984374034640057,25.196850393700785,127,-1.4066753291147078,28.346456692913385,127,-1.0231659036320013,25.196850393700785,127,-0.8040298435827716,28.346456692913385,424,-1.0759073469260276,25.943396226415093,424,2.099601510634279,83.01886792452831,424,0.0,0.0
calibration,5,baseline_buy,352,-1.2245877131060345,38.92045454545455,41,-1.4833485479774826,53.65853658536586,41,-1.8399973654091815,53.65853658536586,41,-2.83650980912393,29.268292682926827,41,-0.9705988335239961,31.70731707317073,41,-1.5589237864317225,53.65853658536586,352,-3.9001041052172227,8.806818181818182,352,2.163877615431676,88.92045454545455,352,-2.330995410708594,0.0
calibration,5,enhanced_shadow_buy,344,-1.1630640960530458,39.825581395348834,33,-0.12147851165283478,66.66666666666666,33,-0.3360716610138596,66.66666666666666,33,-1.2521695150594814,36.36363636363637,33,0.3532385231983991,39.39393939393939,33,-0.19715385683352188,66.66666666666666,344,-3.8314687076821796,9.011627906976743,344,2.2529419068636143,90.69767441860465,344,-2.3536403498592695,0.0
calibration,5,enhanced_raw_75,91,-1.650342913493722,43.956043956043956,56,-0.3573200081614653,55.35714285714286,56,-0.6243331578478718,51.78571428571429,56,-1.514391806854286,33.92857142857143,56,-0.11410693213168496,35.714285714285715,56,-0.432903916767522,55.35714285714286,91,-4.349793481123855,13.186813186813188,91,2.9126095689386133,82.41758241758241,91,-3.4085260522242886,0.0
calibration,5,enhanced_adjusted_75,279,-0.4671110603408773,48.74551971326165,94,-1.1214954360381908,42.5531914893617,94,-1.5417316257326552,32.97872340425532,94,-2.691418447831559,22.340425531914892,89,-1.0943563745228366,26.96629213483146,94,-1.197192307063638,42.5531914893617,279,-3.0792212655932905,12.903225806451612,279,3.408913506694632,93.9068100358423,279,-3.390656498748054,0.0
calibration,10,baseline_buy,2,-6.922768191749351,0.0,0,,,0,,,0,,,0,,,0,,,2,-7.643057528187047,0.0,2,3.3813488774416145,100.0,2,-9.718172839370698,0.0
calibration,10,enhanced_shadow_buy,2,-6.922768191749351,0.0,0,,,0,,,0,,,0,,,0,,,2,-7.643057528187047,0.0,2,3.3813488774416145,100.0,2,-9.718172839370698,0.0
calibration,10,enhanced_raw_75,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,,0,,
calibration,10,enhanced_adjusted_75,2,-6.922768191749351,0.0,0,,,0,,,0,,,0,,,0,,,2,-7.643057528187047,0.0,2,3.3813488774416145,100.0,2,-9.718172839370698,0.0
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
calibration,1,baseline,75-79,226,-4.104178434726256,-2.762082806315366,14.601769911504425,2.1989211005053897,-5.181910479610423,-4.104178434726256
calibration,1,baseline,80-84,0,,,,,,
calibration,1,baseline,85-89,0,,,,,,
calibration,1,baseline,90+,51,-2.8857710296694763,-2.161647518822895,39.21568627450981,1.4835316698034062,-5.704675997071337,-2.8857710296694763
calibration,1,raw,0-49,9,0.9526716118046856,-1.635653061669053,33.33333333333333,7.292733019583067,-2.217359092084505,0.9526716118046856
calibration,1,raw,50-59,10,-6.13232798648699,-3.0745854752298367,40.0,4.389938816379541,-13.147172521731344,-6.13232798648699
calibration,1,raw,60-69,124,-6.4214416015994065,-5.066480409554554,10.483870967741936,2.108930372218887,-7.420494175109657,-6.4214416015994065
calibration,1,raw,70-74,84,-2.1892368796112143,-1.7586431735828363,14.285714285714285,1.5124392460610077,-2.8061829005565846,-2.1892368796112143
calibration,1,raw,75-79,59,-0.5634019052667595,-1.2152276610414454,40.67796610169492,1.6295795273187583,-2.0671606018968283,-0.5634019052667595
calibration,1,raw,80-84,0,,,,,,
calibration,1,raw,85-89,0,,,,,,
calibration,1,raw,90+,0,,,,,,
calibration,1,adjusted,0-49,9,0.9526716118046856,-1.635653061669053,33.33333333333333,7.292733019583067,-2.217359092084505,0.9526716118046856
calibration,1,adjusted,50-59,5,3.4585436633128537,4.849073058622091,80.0,4.389938816379541,-0.2670369489538955,3.4585436633128537
calibration,1,adjusted,60-69,37,-11.405314044384847,-5.7667375155516325,0.0,,-11.405314044384847,-11.405314044384847
calibration,1,adjusted,70-74,108,-4.794566640700678,-3.902111740105438,15.74074074074074,2.2693521292855854,-6.1141998175113,-4.794566640700678
calibration,1,adjusted,75-79,98,-1.6622571285196233,-1.4493845699370018,12.244897959183673,1.368804571108729,-2.0851959703282303,-1.6622571285196233
calibration,1,adjusted,80-84,29,0.368953391551528,0.22252073468191064,68.96551724137932,1.4835316698034062,-2.1078872267859783,0.368953391551528
calibration,1,adjusted,85-89,0,,,,,,
calibration,1,adjusted,90+,0,,,,,,
calibration,5,baseline,0-49,0,,,,,,
calibration,5,baseline,50-59,6,3.4736005846878846,3.473600584687884,100.0,3.4736005846878846,,3.4736005846878846
calibration,5,baseline,60-69,0,,,,,,
calibration,5,baseline,70-74,0,,,,,,
calibration,5,baseline,75-79,142,-5.102960608880119,-3.2242386953988245,9.15492957746479,3.87721083556489,-6.007939126537369,-5.102960608880119
calibration,5,baseline,80-84,0,,,,,,
calibration,5,baseline,85-89,0,,,,,,
calibration,5,baseline,90+,41,-1.8399973654091815,0.7860842697011732,53.65853658536586,1.8867761277875892,-6.15520877858439,-1.8399973654091815
calibration,5,raw,0-49,6,3.4736005846878846,3.473600584687884,100.0,3.4736005846878846,,3.4736005846878846
calibration,5,raw,50-59,1,-15.864817290742806,-15.864817290742806,0.0,,-15.864817290742806,-15.864817290742806
calibration,5,raw,60-69,77,-7.81342567421577,-5.896414748807773,5.194805194805195,5.400447814749844,-8.537473536624846,-7.81342567421577
calibration,5,raw,70-74,49,-3.012225457100317,-2.4945493083065085,4.081632653061225,2.998641109936457,-3.2680070131444348,-3.012225457100317
calibration,5,raw,75-79,56,-0.6243331578478718,0.7860842697011732,51.78571428571429,2.217715248096491,-3.676903667936261,-0.6243331578478718
calibration,5,raw,80-84,0,,,,,,
calibration,5,raw,85-89,0,,,,,,
calibration,5,raw,90+,0,,,,,,
calibration,5,adjusted,0-49,6,3.4736005846878846,3.473600584687884,100.0,3.4736005846878846,,3.4736005846878846
calibration,5,adjusted,50-59,0,,,,,,
calibration,5,adjusted,60-69,13,-12.864843314630892,-10.096415573715527,7.6923076923076925,3.0672009047650444,-14.192513666247223,-12.864843314630892
calibration,5,adjusted,70-74,76,-6.419665296495819,-4.248599981916837,3.9473684210526314,6.178196784744778,-6.937385655998857,-6.419665296495819
calibration,5,adjusted,75-79,68,-2.167627765899278,-2.4990459288589695,16.176470588235293,3.4825169337703383,-3.2580065675899057,-2.167627765899278
calibration,5,adjusted,80-84,26,0.09522751008774268,0.7860842697011732,76.92307692307693,1.6001669071598719,-4.921237146819355,0.09522751008774268
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
calibration,OPTIONS_DATA_PARTIAL,contracts_only,7,89.28571428571429,73.46857142857142,76.0757142857143,100.0,4,2.7445426049249013,4,2.414249544618571,0,,0,,0,
calibration,OPTIONS_DATA_PARTIAL,partial,55,82.72727272727273,72.29418181818181,74.772,100.0,16,-1.173716386230126,15,-2.204415414089698,0,,0,,0,
calibration,OPTIONS_DATA_PARTIAL,quote_only,89,85.11235955056179,72.89516853932584,75.43842696629214,100.0,56,-3.6028966242117457,37,-2.844728193101443,0,,0,,0,
calibration,OPTIONS_NOT_ELIGIBLE,unavailable,1402,74.69686162624822,62.22816690442225,63.587246790299574,62.05420827389444,22,0.9958940622994412,11,4.769210308968248,0,,0,,0,
calibration,OPTIONS_UNAVAILABLE,unavailable,921,79.20738327904452,69.3988056460369,71.55356134636266,97.39413680781759,196,-4.502285022255108,127,-5.286583639882905,0,,0,,0,
```

Availability is reported separately from the formula value. Missing options
data is never classified as an observed score of 50.

## Portfolio Fit cohorts

```csv
partition,cohort,predictions,raw_score_mean,adjusted_score_mean,net_alpha_spy_1d_n,net_alpha_spy_1d_mean,net_alpha_spy_1d_median,net_alpha_spy_1d_win_rate,net_alpha_spy_1d_average_gain,net_alpha_spy_1d_average_loss,net_alpha_spy_1d_expectancy,net_alpha_spy_5d_n,net_alpha_spy_5d_mean,net_alpha_spy_5d_median,net_alpha_spy_5d_win_rate,net_alpha_spy_5d_average_gain,net_alpha_spy_5d_average_loss,net_alpha_spy_5d_expectancy,net_alpha_spy_10d_n,net_alpha_spy_10d_mean,net_alpha_spy_10d_median,net_alpha_spy_10d_win_rate,net_alpha_spy_10d_average_gain,net_alpha_spy_10d_average_loss,net_alpha_spy_10d_expectancy,net_alpha_spy_20d_n,net_alpha_spy_20d_mean,net_alpha_spy_20d_median,net_alpha_spy_20d_win_rate,net_alpha_spy_20d_average_gain,net_alpha_spy_20d_average_loss,net_alpha_spy_20d_expectancy,net_alpha_spy_60d_n,net_alpha_spy_60d_mean,net_alpha_spy_60d_median,net_alpha_spy_60d_win_rate,net_alpha_spy_60d_average_gain,net_alpha_spy_60d_average_loss,net_alpha_spy_60d_expectancy
calibration,missing,556,66.00203237410072,66.00203237410072,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,other_observed,836,60.2533014354067,57.91235645933015,81,-0.13988942024877898,-1.2152276610414454,40.74074074074074,2.6925191542167433,-2.0871703151938252,-0.13988942024877898,67,0.26117397849507323,0.7860842697011732,59.70149253731343,2.9193763898362244,-3.676903667936261,0.26117397849507323,0,,,,,,,0,,,,,,,0,,,,,,
calibration,raw_high_fit_weak,25,75.14040000000001,69.37280000000001,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,,0,,,,,,
calibration,raw_medium_fit_good,1057,69.24401135288552,73.83474929044465,213,-4.970754247263391,-3.6307928684466053,11.737089201877934,1.8226146316631047,-5.8741277683972335,-4.970754247263391,127,-6.024390878765929,-3.6235112159675,4.724409448818897,4.599845579812048,-6.551212521340041,-6.024390878765929,0,,,,,,,0,,,,,,,0,,,,,,
```

## Component contribution and redundancy

```csv
partition,horizon,component,n,pearson_forward_alpha,spearman_forward_alpha,max_abs_component_correlation,incremental_r2
calibration,1,technical_score,294,-0.020791236373678686,0.014044664132823178,0.2671680924101423,
calibration,1,momentum_score,294,-0.1528338110156348,-0.21038271475819206,0.5627508419368589,
calibration,1,research_score,294,-0.11749687443553784,-0.015003634311513588,0.37554063945579746,
calibration,1,volatility_score,294,-0.024257905446496978,0.01726537947693117,0.30700958669185435,
calibration,1,liquidity_score,294,0.6157256832058886,0.6393687199126987,0.12349914013941009,
calibration,1,options_score,0,,,,
calibration,1,relative_opportunity_score,294,,,,
calibration,1,risk_reward_score,294,-0.21964573987781466,-0.25368579493993265,0.5627508419368589,
calibration,5,technical_score,194,-0.01846471104036107,-0.001986476033026452,0.2671680924101423,
calibration,5,momentum_score,194,-0.3095274493481191,-0.31335397440640006,0.5627508419368589,
calibration,5,research_score,194,-0.15237532046678876,0.00797423674639388,0.37554063945579746,
calibration,5,volatility_score,194,-0.2496184632571353,-0.20589853295121432,0.30700958669185435,
calibration,5,liquidity_score,194,0.5886157462984609,0.6304697450859925,0.12349914013941009,
calibration,5,options_score,0,,,,
calibration,5,relative_opportunity_score,194,,,,
calibration,5,risk_reward_score,194,-0.21368787237997766,-0.24508886717171333,0.5627508419368589,
calibration,10,technical_score,0,,,0.2671680924101423,
calibration,10,momentum_score,0,,,0.5627508419368589,
calibration,10,research_score,0,,,0.37554063945579746,
calibration,10,volatility_score,0,,,0.30700958669185435,
calibration,10,liquidity_score,0,,,0.12349914013941009,
calibration,10,options_score,0,,,,
calibration,10,relative_opportunity_score,0,,,,
calibration,10,risk_reward_score,0,,,0.5627508419368589,
calibration,20,technical_score,0,,,0.2671680924101423,
calibration,20,momentum_score,0,,,0.5627508419368589,
calibration,20,research_score,0,,,0.37554063945579746,
calibration,20,volatility_score,0,,,0.30700958669185435,
calibration,20,liquidity_score,0,,,0.12349914013941009,
calibration,20,options_score,0,,,,
calibration,20,relative_opportunity_score,0,,,,
calibration,20,risk_reward_score,0,,,0.5627508419368589,
calibration,60,technical_score,0,,,0.2671680924101423,
calibration,60,momentum_score,0,,,0.5627508419368589,
calibration,60,research_score,0,,,0.37554063945579746,
calibration,60,volatility_score,0,,,0.30700958669185435,
calibration,60,liquidity_score,0,,,0.12349914013941009,
calibration,60,options_score,0,,,,
calibration,60,relative_opportunity_score,0,,,,
calibration,60,risk_reward_score,0,,,0.5627508419368589,
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
fabca3d3e4bba17e1172975c,2026-09-16T05:40:32+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,,,,
e1338d825a461549ab9e718a,2026-09-16T05:50:47+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
e1338d825a461549ab9e718a,2026-09-16T05:50:47+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,,,,
e991d1db51ca3517cd30ca69,2026-09-16T05:54:18+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
e991d1db51ca3517cd30ca69,2026-09-16T05:54:18+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,,,,
92e9fb98a9868fa5713aaf9d,2026-09-16T06:00:15+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
92e9fb98a9868fa5713aaf9d,2026-09-16T06:00:15+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,,,,
3f6b3bd68f68e3e0a4cb2309,2026-09-16T06:03:42+00:00,calibration,DE,BUY,WAIT,68.51,100.0,73.23,,,,,
3f6b3bd68f68e3e0a4cb2309,2026-09-16T06:03:42+00:00,calibration,EL,BUY,WAIT,70.5,100.0,74.93,-12.625302414742594,,,,
3280fe7e1c09eee6124d715f,2026-09-22T10:54:56+00:00,calibration,VRNS,BUY,WAIT,71.41,100.0,75.7,-1.5901812297277051,,,,
```

## BUY / WAIT / AVOID transition matrix

```csv
partition,baseline_decision,enhanced_decision,predictions
calibration,BUY,BUY,474
calibration,BUY,WAIT,19
calibration,BUY,AVOID,0
calibration,WAIT,BUY,0
calibration,WAIT,WAIT,1742
calibration,WAIT,AVOID,0
calibration,AVOID,BUY,0
calibration,AVOID,WAIT,0
calibration,AVOID,AVOID,239
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
