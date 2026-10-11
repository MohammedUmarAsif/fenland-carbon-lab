# Exploratory input-support protocol

Recorded 2026-10-11 23:20 UTC (12 October in Bahrain), before supplementary computation.
The original benchmark, selected model and checkpoints are frozen. Existing
evaluation results have already been inspected; this is exploratory, not a new
unseen-test experiment or preregistration of the historical benchmark.

Use the common eligible 60-day windows and four weather variables. Represent
each by its current-day values and 60-day means (eight features). Fit a
StandardScaler and Ledoit-Wolf covariance to training windows only. Freeze the
99th percentile of training squared Mahalanobis distances as the flag threshold.
Do not tune this threshold on validation, calibration or evaluation errors.

Join flags to existing predictions by unique key, validating complete one-to-one
alignment and matching split. Evaluate the selected LSTM and matched 60-day RF
and boosting, all seed 17. Use their existing fixed 2016-calibrated 95% NEE
intervals. Report split, flag proportion, n, RMSE, MAE, bias, coverage and width.
Below 30 samples export n and proportion but null performance measures and an
insufficient-evidence label. No model fitting or selection changes.

Keep all input rows, fitted scaling/covariance/thresholds, distances and flags
private. Export only aggregate group statistics. The eight-feature projection
does not characterize support across the entire sequence. A flag is neither
a guarantee of failure nor a calibrated probability of correctness. Temporal
dependence and training-derived thresholds prevent a nominal false-alarm claim.

Expected implementation checks: non-finite inputs rejected; train-only fitting;
frozen thresholds; duplicate/missing keys rejected; split mismatch rejected;
small groups suppressed; private fields absent from the public package.
