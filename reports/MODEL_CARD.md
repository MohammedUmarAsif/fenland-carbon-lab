# Model card

Intended use: inspect weather-to-simulated-daily-carbon emulation under explicit
time and cell holdouts. Not a validated replacement for coupled JULES dynamics,
an observational carbon accounting tool, or management advice.

Core inputs: current interval's temperature/shortwave/precipitation/wind and
preceding weather in the same split/cell; available from simulator meteorology,
or compatible daily weather supplied by a user after the interval. No target
components are inputs. The state ablation additionally requires all four JULES
soil moisture layers. VPD uses humidity/pressure/temperature and the FAO-56
saturation expression, with specific-humidity mixing conversion; calculated
from daily means, it approximates daily dryness, not mean subdaily VPD.

Train 2006-2014, validation 2015, calibration 2016, reserved retrospective test
2017-2019. Common 60-day eligibility excludes first 59 days of each partition.
Models: pooled month climatology, ridge, RF, histogram boosting, 16-unit LSTM.
RF/boosting use all permitted weather lags, with current-day variants at L=1.
Three declared seeds for RF/boosting/LSTM; boosting is deterministic here.
RF and ridge tuning use two rolling pre-test folds. Spatial tasks use nested
rolling selection excluding the held cell; no training/selection uses that cell.

Outputs are three components or direct NEE. Derived NEE accounting can conceal
compensating component errors; covariance is reported. No target clipping is
applied: this model imposes an accounting identity, not physical nonnegativity.
Selected model is chosen on seed-17 validation mean component RMSE; seed
sensitivity is reported separately, not cherry-picked on the test set.

Fixed residual quantiles use calibration data only. Reported empirical coverage
does not imply exact distribution-free protection under temporal dependence or
shift. This uncertainty addresses simulator targets; structural uncertainty
relative to nature remains unmeasured. No prospective data collection occurred.

Artifacts contain configuration, scaler statistics, keyed predictions, training
history, seeds, hardware and elapsed times. Local inference timing includes
transformation/prediction but excludes NetCDF extraction and window construction.
There is no comparable JULES simulation timing, so no speedup is claimed.
