# Frozen protocol: 12 October 2026, before corrected model fitting

Primary task: emulate simulated daily GPP, plant respiration, soil respiration
and derived atmospheric NEE, conditional on daily-mean weather for that same
interval. Horizon zero includes current-day weather. Such weather is known after
the interval, so this is retrospective emulation, not an operational forecast.
Targets: kg C converted with 12.0107 g/mol; NEE = Rp + Rs - GPP.

Training intervals 2006-2014; model selection 2015; calibration 2016;
retrospectively reserved evaluation 2017-2019. Earlier artifacts may already have
used these years: this is a locked evaluation within an inspected historical
dataset, not prospective evidence. No test-target-driven changes are allowed.
No windows cross partitions, cells, gaps, or missing values. All history lengths
use the intersection of 60-day-eligible targets, including climatology/current
weather models. This excludes the first 59 days of every partition per cell.

Weather inputs: temperature, shortwave, precipitation, wind. Baselines:
training-only calendar-month climatology, standardized ridge, random forest,
histogram gradient boosting; current-day and history-aware versions. History
tabular models use every daily lag (same information as the LSTM).
Lengths 1, 7, 24, 60 days. LSTM: single 16-unit layer, three component outputs,
MSE, Adam 0.003, batch 256, at most 15 epochs, validation patience 4.
Standardizers fit training rows only; target transform fit eligible training
targets. Seeds 17, 29, 43. RF 80 trees, max depth 14, min leaf selected 3 or 10.
Boosting max iter 120, depth 4, l2 1, learning rate .08.
Ridge alpha 1 or 100. Two rolling validation folds: train through 2010/evaluate
2011 and train through 2012/evaluate 2013. Select configurations on pre-test
mean component RMSE, never NEE test performance. Budget: CPU, four threads,
no paid compute. Skip extra recurrent architectures and robust losses unless
validation diagnostics justify them; no test-driven additions.

Controlled 24-day RF ablations: calendar sin/cos, antecedent precipitation
(previous 7/30 days), daily-mean approximate VPD, all four simulator moisture
layers (separate state-conditional task). Direct NEE versus component accounting
for RF/boosting/LSTM, identical inputs and split; equal architectures except
output dimension. Spatial interpolation: omit cell from 2006-2014 training,
predict its 2015 intervals. Joint transfer: omit cell, predict its 2017-2019
intervals. Redmere labels grouped. Transfer uses preselected RF at 24 days,
three seeds; results cannot establish broad regional independence.

Uncertainty: fixed symmetric absolute-residual quantiles from 2016 calibration,
68/80/90/95%; component and NEE separately. Report coverage/width/interval score
by season/cell; do not assert IID guarantees. Paired circular moving-block
bootstrap, synchronized days across all cells, 300 replicates and lengths
7/30/90 days; seed 101. Diagnose seasonal, temperature 95th percentile,
precipitation low/high quartiles and absolute-flux 95th percentile thresholds
fixed on eligible training samples. Daily and calendar-month budgets use exact
interval durations. Only complete months enter monthly metrics.

Checkpoints: each run emits keyed predictions, metrics, training statistics,
configuration, hardware and elapsed time. No run is complete without artifacts.
Publication is blocked until content/data redistribution rights are recorded.
