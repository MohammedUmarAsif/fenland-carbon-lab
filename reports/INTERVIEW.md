# Interview walkthrough and measured CV claims

## CV bullets for the 2026 extension

* Built an auditable daily JULES carbon-flux pipeline across six native Fenland
  cells, correcting interval alignment, kg C conversion, NEE sign and duplicate-cell weighting.
* Completed 101 controlled model runs across temporal, state and grouped-transfer
  tasks; validation-selected weather-only model achieved reserved-test NEE RMSE
  2.096 μmol CO2 m-2 s-1 and R² 0.712 on 6,216 cell-days.
* Delivered an interactive static evidence site with keyed prediction downloads,
  reproducible benchmarks and separately calibrated uncertainty: nominal 95%
  intervals achieved 97.47% empirical test coverage.

These bullets describe an AI-assisted 2026 extension, not experiments completed
during the 2025 MSc. Do not say deployed until a verified public URL exists.

## A five-minute evidence walkthrough

Open the history-length chart; explain simulator emulation versus tower truth.
Show the Redmere duplicate-cell mapping and why split grouping matters. Select
the test split and a model, then download rows to demonstrate interval keys.
Compare full-lag tabular inputs with LSTM inputs. Explain why state-conditioned
accuracy changes the deployment contract. Show nominal versus empirical coverage
and seasonal bias. Finish with the frozen protocol, run registry and limitations.

## Be ready to defend

Explain why end labels differ from represented days; derive kg C to μmol and daily
budgets using carbon atomic mass, not CO2 molecular mass. Draw horizon-zero and
horizon-one alignment. Explain training-only transforms and rolling/nested cell
selection. Describe why overlapping windows/shared-day forcing invalidate IID
replicate counts. Discuss direct versus component errors and cancellation.
Explain calibration's distribution-shift limits, inference benchmark boundary,
why crop mismatch prevents tower validation, and the role of AI assistance.
Read the package and recreate at least the smoke tests and one real run before
claiming independent command of the implementation. Do not claim JULES development,
tower data collection, regional causal interventions, carbon savings or speedup.
