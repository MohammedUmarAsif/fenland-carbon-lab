# Methods and corrections, 12 October 2026

The 2025 dissertation is preserved unchanged. This later AI-assisted extension
corrects methods and verifies saved artifacts. It is not a silent revision of the
submitted work. Printed appendix code cannot establish which code generated the
submitted scores: their matching keyed prediction artifacts are not recovered.

* Raw size 4,567,944,867 bytes; dimensions time=5113, x=12392, y=1, soil=4,
  cpft=1. Paired coordinates have shape (1,12392), with no cell polygon bounds or
  grid-mapping declaration. They represent native point locations, not proof of
  a conventional curvilinear mesh.
* Fluxes are daily means. Coordinates label interval ends: 2006-01-02 through
  2020-01-01; bounds cover 2006-01-01 through 2019-12-31 daily periods. A 24-step
  history is 24 days. Dawn/noon/night learning is not demonstrated.
* Submitted appendix pp. 41-42 sorts by site/time, fits full-table scalers, and
  slices rows 70/15/15. This code has different information access and validation
  from the prose. The new implementation fits transforms only to eligible
  training data and uses common calendar boundaries.
* Printed `Xs[i-window:i]` excludes target-row weather. The corrected primary
  task includes current-day daily weather and predicts that interval. Such
  weather is available after the day; this is retrospective emulation. A
  horizon argument explicitly moves the target beyond the last input interval.
* Historic flux metadata abbreviates kg m-2 s-1. JULES documentation identifies
  carbon mass: conversion is kg C × 1e9/12.0107 to μmol CO2 m-2 s-1. Raw values
  remain alongside standardized columns. Label changes alone would not repair
  the dissertation's apparent omitted conversion. Exact submitted prediction
  arrays are missing, so corrected submitted scores cannot be asserted.
* Atmospheric NEE = plant + soil respiration − GPP. August arrays use the
  opposite sign and carbon mass constant 12. Their metric check preserves
  original stored values; new ecological interpretations use atmospheric sign.
* The July Colab export includes magics, spatial means, flux predictors and
  scaling before splitting. The August model uses 34 days and seven inputs,
  including fluxes, with one NEE output. Neither proves the submitted four-input,
  three-output design. August sequence metadata says H=1, but actual window
  construction code is missing: timing of flux predictors remains unresolved.
* Both Redmere labels are identical native cell series and are grouped together.
  Six nearby cells, with highly correlated forcing, are a small simulated sample.
* Negative August predictive spreads result from an affine location added to
  standard deviations. Correct means use scale and location; spreads use scale
  only. Repair does not establish calibration. New uncertainty uses a separate
  2016 residual calibration set and reports empirical coverage.
* Per-site August n=5079 matches the full sequence span; these are not held-out
  site scores. Test arrays lack proven site/time keys; no dates are invented.
* Wicken peat depth `4-Feb` remains unchanged and flagged, not guessed. cpft=1
  does not identify Miscanthus or management. Crop and model version are missing.

Source locators and individual claim statuses appear in the claim ledger and
experiment lineage. Corrected results are generated from keyed prediction files.
Accounting consistency is not a PINN, full conservation law or intervention model.

Source: [JULES output definitions](https://metoffice.github.io/jules/latest/output-variables.html),
local submitted appendix, raw NetCDF, and safe August JSON/CSV inspection.
