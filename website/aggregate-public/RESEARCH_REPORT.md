# Fenland Carbon Lab research report

Generated 12 October 2026 from keyed predictions; extension of Mohammed Umar
Asif Sayed's University of Leicester 2025 MSc dissertation. AI assistance is
credited separately. This is simulator emulation, not observational validation.

## Principal measured result

The pre-test validation-selected weather-only component model **weather-lstm-L60-s17** achieves
NEE RMSE **2.0961 μmol CO2 m-2 s-1**, MAE 1.5248, signed bias
-0.3408, and R² **0.7120** on **6216** reserved test
cell-days. Mean per-cell RMSE is 2.0861. The reserved
period is retrospective within an already inspected dataset, not prospective.

The strongest contribution is controlled, auditable comparison, not a universal
LSTM superiority claim. Old scores cannot be compared directly to these results:
inputs, targets, physical conversion, validation and sample weighting differ.

Across three seeds, 60-day LSTM RMSE spans 2.0961–2.3743,
with mean 2.2386; deterministic 60-day boosting achieves
2.1676. The selected seed's advantage does not establish robust LSTM
superiority. Seed 17 was fixed before comparison, not chosen on test performance.

## Evidence recovery

86 physical files, source ZIP archives and office documents inventoried.
Physical SHA-256 duplicate inspection identifies 16 repeated file entries.
234 historical PNGs decode; a four-sheet visual review identifies blank July
emissions maps. Six MP4 entries are classified by size; tiny containers have
no useful playback payload. None are used in the new website. Source SHA-256
for raw NetCDF: `1cd7b76dd184d16f1dac87e3128806c51e873a527e514ad6d398942c50dc0b08`. Separate submitted, July and August evidence
families appear in EXPERIMENT_LINEAGE.csv and the individual CLAIM_LEDGER.csv.
Source artifacts remain untouched and administrative documents remain private.

Historical August RF RMSE 0.9469327, LSTM RMSE 1.0209841, in stored alternate-sign
units, are reproduced to saved precision. That model uses seven features,
including fluxes. Its flux input timestamps remain unresolved; sequence metadata
H=1 does not substitute for recovered construction code. Repaired nominal 95%
uncertainty covers 47.6378% of 5,334 paired saved targets. No dates are assigned
to identifier-free test predictions. Submitted component predictions remain
missing, so the submitted model's headline scores are historical reports.

## Frozen experimental methods

Time interval bounds define standard-calendar daily means, 2006-2019. Native
point selection uses spherical geodesic distance and actual validity checks.
Seven labels map to six unique cells; duplicate Redmere labels receive one weight.
The complete selected extract has 30,678 rows. No missing required values occur.
Grid-wide screening checks coordinates and three variable time slabs; it does
not validate every variable throughout the 4.57 GB cube.

Primary inputs: current and past temperature, shortwave, precipitation, wind.
Current daily means are available after the day. This is a same-interval
retrospective emulator, not an operational weather forecast. State ablations
require soil moisture from a simulator or independently compatible input.
Carbon conversion uses 12.0107 g/mol; NEE = Rp+Rs−GPP, positive atmospheric release.

Global train 2006-2014; selection/early stopping 2015; calibration 2016;
evaluation 2017-2019. Windows never cross cells, gaps or split boundaries. Common
60-day target eligibility gives 19,368 training, 1,836 validation, 1,842 calibration
and 6,216 test samples. Scalers use eligible training windows/targets only;
repeated window entries weight feature statistics but never use nontraining data.
Train-only imputation is unnecessary for these complete extracted series.
Ridge/RF hyperparameters use two rolling-origin folds; per-cell transfer tuning
excludes the held cell in both fitting and selection. Seed 17 is fixed for final
model selection on validation mean component RMSE; seeds 29/43 quantify variance.
Boosting seed replicas are identical because no stochastic subsampling is used.

## A. What survives corrected evaluation?

All listed results are newly trained, weather-only benchmark evaluations; none
inherit a legacy scaler or use carbon-component inputs.

| run_id | n | rmse | mae | bias | r2 |
| --- | --- | --- | --- | --- | --- |
| weather-climatology-L1-s17 | 6216 | 2.9659 | 1.9990 | 0.1696 | 0.4233 |
| weather-ridge-L1-s17 | 6216 | 3.4620 | 2.4202 | 0.0168 | 0.2143 |
| weather-rf-L1-s17 | 6216 | 3.2732 | 2.1694 | -0.1398 | 0.2977 |
| weather-boosting-L1-s17 | 6216 | 3.2272 | 2.1435 | -0.0969 | 0.3173 |
| weather-lstm-L1-s17 | 6216 | 3.3302 | 2.3128 | 0.0714 | 0.2730 |
| weather-climatology-L7-s17 | 6216 | 2.9659 | 1.9990 | 0.1696 | 0.4233 |
| weather-ridge-L7-s17 | 6216 | 3.3990 | 2.4160 | -0.0218 | 0.2426 |
| weather-rf-L7-s17 | 6216 | 2.7680 | 1.9384 | -0.2301 | 0.4977 |
| weather-boosting-L7-s17 | 6216 | 2.7582 | 1.9326 | -0.1582 | 0.5013 |
| weather-lstm-L7-s17 | 6216 | 2.8084 | 1.9471 | -0.2465 | 0.4830 |
| weather-climatology-L24-s17 | 6216 | 2.9659 | 1.9990 | 0.1696 | 0.4233 |
| weather-ridge-L24-s17 | 6216 | 3.3338 | 2.3913 | -0.0658 | 0.2714 |
| weather-rf-L24-s17 | 6216 | 2.3850 | 1.7506 | -0.2554 | 0.6271 |
| weather-boosting-L24-s17 | 6216 | 2.2386 | 1.6652 | -0.1737 | 0.6715 |
| weather-lstm-L24-s17 | 6216 | 2.2996 | 1.6193 | -0.3831 | 0.6533 |
| weather-climatology-L60-s17 | 6216 | 2.9659 | 1.9990 | 0.1696 | 0.4233 |
| weather-ridge-L60-s17 | 6216 | 3.2709 | 2.3854 | 0.0514 | 0.2986 |
| weather-rf-L60-s17 | 6216 | 2.2665 | 1.6641 | -0.0688 | 0.6632 |
| weather-boosting-L60-s17 | 6216 | 2.1676 | 1.6229 | -0.0788 | 0.6920 |
| weather-lstm-L60-s17 | 6216 | 2.0961 | 1.5248 | -0.3408 | 0.7120 |

## B. Does memory add value?

RF RMSE changes from 3.2732 at one day to 2.2665 at 60 days
(30.75% lower) on exactly matched targets. RF/boosting
receive every daily lag, not merely the last time step. LSTM uses the same
input sequence; this is a fair information comparison, not necessarily equal
parameter counts. Calendar climatology is a training-derived pooled monthly
baseline. No observed-target persistence is mislabelled weather-only.

The paired block result file compares selected-model NEE RMSE with 24-day RF,
boosting and LSTM and matched 60-day RF/boosting, synchronized days across cells,
300 replicates and 7/30/90-day
blocks. These intervals are conditional temporal sampling evidence, not six
independent ecological populations. Seed sensitivity is separately tabulated.

## C. Diagnosed limitations and controlled features

At 24 days, weather RF RMSE 2.3850 changes to 1.8999 with four
simulator soil moisture layers. This is a state-conditional experiment, with
different deployment requirements. Calendar, antecedent precipitation and
approximate daily VPD are controlled single-family changes, not cherry-picked
combinations. Rainfall summaries are causal within each split. VPD uses verified
K, Pa, kg/kg metadata and the FAO-56 saturation equation; clamped at zero. Daily
means approximate atmospheric dryness and cannot recover mean subdaily VPD.

| run_id | seed | rmse | mae | bias | r2 |
| --- | --- | --- | --- | --- | --- |
| ablation-calendar-rf-L24-s17 | 17 | 2.2598 | 1.5916 | -0.0177 | 0.6652 |
| ablation-calendar-rf-L24-s29 | 29 | 2.2213 | 1.5767 | -0.0341 | 0.6765 |
| ablation-calendar-rf-L24-s43 | 43 | 2.2106 | 1.5734 | -0.0395 | 0.6796 |
| ablation-rain-rf-L24-s17 | 17 | 2.3135 | 1.7027 | -0.2695 | 0.6491 |
| ablation-rain-rf-L24-s29 | 29 | 2.3190 | 1.7108 | -0.2897 | 0.6475 |
| ablation-rain-rf-L24-s43 | 43 | 2.3440 | 1.7187 | -0.2759 | 0.6398 |
| ablation-vpd-rf-L24-s17 | 17 | 2.4072 | 1.7648 | -0.2774 | 0.6201 |
| ablation-vpd-rf-L24-s29 | 29 | 2.4406 | 1.7833 | -0.2728 | 0.6095 |
| ablation-vpd-rf-L24-s43 | 43 | 2.4394 | 1.7814 | -0.2685 | 0.6099 |
| ablation-state-rf-L24-s17 | 17 | 1.8999 | 1.1288 | -0.3481 | 0.7634 |
| ablation-state-rf-L24-s29 | 29 | 1.8948 | 1.1285 | -0.3440 | 0.7646 |
| ablation-state-rf-L24-s43 | 43 | 1.8863 | 1.1325 | -0.3368 | 0.7667 |

Seasonal, high-flux, precipitation quartile and warm-tail diagnostics are in
diagnostics.csv. Thresholds are fixed from training. No extra recurrent
architecture or Huber loss is justified within the frozen compute programme.
Null/negative ablations remain visible rather than being suppressed.

## D. Transfer

Spatial folds predict a held native cell in shared 2015 years after training on
other cells in 2006-2014. Joint folds predict that excluded cell in 2017-2019.
Every fold uses nested pre-test rolling selection without the held cell. Both
Redmere labels stay together. Per-cell and seed results:

| run_id | seed | split | n | rmse | bias | r2 |
| --- | --- | --- | --- | --- | --- | --- |
| spatial-x1180_y0-s17 | 17 | validation | 306 | 2.6271 | 2.0180 | 0.3982 |
| spatial-x1180_y0-s29 | 29 | validation | 306 | 2.6318 | 2.0169 | 0.3961 |
| spatial-x1180_y0-s43 | 43 | validation | 306 | 2.6067 | 2.0041 | 0.4075 |
| joint-x1180_y0-s17 | 17 | test | 1036 | 2.3633 | 1.4306 | 0.4845 |
| joint-x1180_y0-s29 | 29 | test | 1036 | 2.3758 | 1.4476 | 0.4791 |
| joint-x1180_y0-s43 | 43 | test | 1036 | 2.3706 | 1.4522 | 0.4814 |
| spatial-x1283_y0-s17 | 17 | validation | 306 | 1.9116 | 0.5103 | 0.7311 |
| spatial-x1283_y0-s29 | 29 | validation | 306 | 1.9739 | 0.5328 | 0.7133 |
| spatial-x1283_y0-s43 | 43 | validation | 306 | 1.9415 | 0.5696 | 0.7226 |
| joint-x1283_y0-s17 | 17 | test | 1036 | 2.0326 | -0.1894 | 0.7076 |
| joint-x1283_y0-s29 | 29 | test | 1036 | 2.0707 | -0.1945 | 0.6965 |
| joint-x1283_y0-s43 | 43 | test | 1036 | 2.0135 | -0.1930 | 0.7131 |
| spatial-x2827_y0-s17 | 17 | validation | 306 | 2.0335 | -0.9787 | 0.6612 |
| spatial-x2827_y0-s29 | 29 | validation | 306 | 2.0551 | -0.9660 | 0.6540 |
| spatial-x2827_y0-s43 | 43 | validation | 306 | 2.0588 | -0.9722 | 0.6527 |
| joint-x2827_y0-s17 | 17 | test | 1036 | 2.7384 | -1.5224 | 0.4850 |
| joint-x2827_y0-s29 | 29 | test | 1036 | 2.7826 | -1.5374 | 0.4682 |
| joint-x2827_y0-s43 | 43 | test | 1036 | 2.7542 | -1.5255 | 0.4790 |
| spatial-x2888_y0-s17 | 17 | validation | 306 | 1.7928 | -0.9553 | 0.6907 |
| spatial-x2888_y0-s29 | 29 | validation | 306 | 1.7861 | -0.9790 | 0.6930 |
| spatial-x2888_y0-s43 | 43 | validation | 306 | 1.8232 | -0.9640 | 0.6801 |
| joint-x2888_y0-s17 | 17 | test | 1036 | 2.6767 | -1.3572 | 0.5536 |
| joint-x2888_y0-s29 | 29 | test | 1036 | 2.6856 | -1.3442 | 0.5506 |
| joint-x2888_y0-s43 | 43 | test | 1036 | 2.6412 | -1.3395 | 0.5654 |
| spatial-x2989_y0-s17 | 17 | validation | 306 | 1.7891 | -0.9603 | 0.6853 |
| spatial-x2989_y0-s29 | 29 | validation | 306 | 1.7983 | -0.9678 | 0.6821 |
| spatial-x2989_y0-s43 | 43 | validation | 306 | 1.7737 | -0.9469 | 0.6907 |
| joint-x2989_y0-s17 | 17 | test | 1036 | 2.7065 | -1.3932 | 0.5444 |
| joint-x2989_y0-s29 | 29 | test | 1036 | 2.6999 | -1.3641 | 0.5466 |
| joint-x2989_y0-s43 | 43 | test | 1036 | 2.6974 | -1.3766 | 0.5475 |
| spatial-x3749_y0-s17 | 17 | validation | 306 | 2.5600 | 1.9634 | 0.4359 |
| spatial-x3749_y0-s29 | 29 | validation | 306 | 2.6224 | 2.0141 | 0.4080 |
| spatial-x3749_y0-s43 | 43 | validation | 306 | 2.5622 | 1.9750 | 0.4349 |
| joint-x3749_y0-s17 | 17 | test | 1036 | 2.4128 | 1.4604 | 0.5307 |
| joint-x3749_y0-s29 | 29 | test | 1036 | 2.4222 | 1.4492 | 0.5270 |
| joint-x3749_y0-s43 | 43 | test | 1036 | 2.4351 | 1.4684 | 0.5220 |

Highly related nearby forcing limits independence. These tests demonstrate
specific simulator-cell transfer, not a continuous regional emissions map.

## E. Direct versus component-first

Matched 24-day RF direct NEE RMSE is 2.3604, versus 2.3850
from component accounting. All three model families receive direct/component
comparisons with matched seeds and architecture budgets. Component metrics,
signed biases and error covariance are retained. Algebraic identity is exact
within floating precision; opposite component errors can cancel in net exchange.
It is not full conservation, a PINN, or correct simulator hydrology.

## F. Empirical uncertainty reliability

The selected model's fixed 2016 residual quantiles yield 97.47%
test coverage at nominal 95%; mean width 10.1613 and interval score
12.2863 μmol CO2 m-2 s-1. Coverage/width/score are evaluated at
68/80/90/95%, by cell and season. Calibration targets are separate from test.
Temporal dependence, shared-day spatial correlation and distribution shift mean
this simple residual-quantile method has no exact IID guarantee. It is not the
EnbPI algorithm. Simulator structural uncertainty relative to nature is separate.

## Carbon budgets, cost and reproducibility

Daily carbon amounts integrate actual interval durations; complete calendar-month
budgets and monthly RMSE are regenerated in selected_monthly.csv and its metrics
JSON. Incomplete months remain labelled and excluded from monthly scoring. Mean
cumulative test NEE budget error is -366.386
g C m-2 per cell across the sampled test intervals. This excludes the first
59 days of the test partition and is not a full 2017-2019 balance. NEE also
excludes harvest and other net ecosystem carbon balance terms.

101 primary/ablation/transfer model runs and 56 rolling-selection
fits completed. Summed recorded fit/evaluation time for registry runs is
16.54 minutes (not programme wall time). CPU budget four threads; hardware
and library lockfiles are recorded. Local inference median
0.0831 seconds for a 19368-sample
batch under the explicitly stated preprocessing/I/O boundary. No equivalent
JULES simulation timing exists, so acceleration over JULES is not claimed.

## Observations, rights and remaining limitations

Both EIDC records' supporting documentation, actual site coordinates, QA, measured
versus filled products, footprints and rotations were inspected. Crop/management
and simulation version are unresolved; thus no direct tower score is reported.
Woodwalton and this network's Redmere 1 have no matching pre-2020 overlap. See
OBSERVATIONAL_FEASIBILITY.md. Missing exact course confirmation, source run settings,
Wicken peat-depth repair and some incomplete original references are explicit
ledger entries. These limitations do not prevent local code/experiment completion.

No paid compute, public repository, live deployment, collaborator messages or
account changes were used. Public redistribution of simulation derivatives and
dissertation content awaits recorded rights. The local site is fully generated;
publication remains gated. Read README for commands and PUBLICATION.md for the
concrete final deployment step.
