# Manuscript and future research agenda

## Working title
When does weather suffice? A reproducible reliability study of daily JULES carbon-flux emulation.

## Draft abstract (research extension; not submitted or peer reviewed)
Environmental simulator emulators need evaluation that separates the information
available to a model from its architecture. This study evaluates daily simulated
carbon uptake, plant respiration and soil respiration across six unique Fenland
model cells, deriving net ecosystem exchange through component accounting. A
fixed chronological benchmark compares seasonal climatology, ridge regression,
Random Forest, boosting and a compact LSTM on a common target intersection and
matched weather-history inputs. Additional experiments examine simulator soil
moisture, direct net-flux prediction, held-cell transfer and residual-quantile
intervals. Multiple seeds and dependent block comparisons temper claims of
architectural superiority. A separately recorded exploratory supplement examines
performance on unusual weather summaries using a training-fitted support rule.
The results establish a reproducible simulator-fidelity benchmark and identify
input availability, transfer and uncertainty as practical limits. Six nearby
cells, shared forcing, inspected historical evaluation data and incomplete
simulator provenance limit generalisation. Observational accuracy, causal
management effects and acceleration relative to JULES are not established.

## Research questions and evidence
| Question | Experiment/evidence | Interpretation limit |
|---|---|---|
| Does history help beyond seasonal structure? | Climatology, ridge, RF, boosting, LSTM; 1/7/24/60-day common target set | Dependence; history includes current-day weather |
| Does architecture explain gains? | Matched daily lags, seeds 17/29/43, paired blocks 7/30/90 days | No robust general LSTM superiority |
| What does extra information contribute? | Calendar, antecedent rain, approximate VPD and moisture RF ablations | Moisture is a distinct state-conditional task; no causal attribution |
| Can component errors hide in net exchange? | Direct/component experiments and signed error covariance | Accounting identity, not full physical conservation |
| Does skill transfer? | Nested six-cell spatial and joint transfer | Nearby cells share forcing; not independent regional validation |
| Are intervals useful? | Calibration year distinct from evaluation, coverage/width/interval score | Conditional simulator residuals; no exact IID guarantee |
| Do unusual inputs coincide with error? | Frozen eight-summary training-support diagnostic | Exploratory after historical test inspection; small dependent tail group |

## Manuscript structure and figure list
1. Introduction: carbon modelling motivation; distinguish observational upscaling,
   simulator emulation and deployment. Compare primary JULES, validation and
   emulator studies; no unverified first-method claim.
2. Data/provenance: native paired coordinate geometry, six unique cells, interval
   bounds, carbon mass units, missingness, duplicate site labels and unresolved settings.
3. Methods: frozen splits, target intersection, comparable inputs, selection,
   seeds, nested transfer, accounting, dependent comparisons and calibration.
4. Results: architecture/history contrasts, input ablations, component errors,
   transfer, interval quality, complete-month summaries; exploratory supplement separate.
5. Discussion: information constraints versus architecture, simulator/reality gap,
   limitations, reproducibility and next experiments.
6. Availability/credits: authorized-data reproduction, aggregate-only public assets,
   author and acknowledged guidance, explicit AI assistance.

Figures: (1) task/data/split schematic; (2) matched baseline and history comparisons;
(3) seed variation and paired differences; (4) input and direct/component contrasts;
(5) component covariance decomposition; (6) transfer/season/event diagnostics;
(7) coverage versus width; (8) exploratory support-group error and counts.
Each figure uses versioned aggregate outputs, units, n and visible provenance.

## Limitations and submission gates
- Revised dissertation results/code lineage inconsistent; the extension does not
  retrospectively certify those scores. Source run configuration/crop/management unknown.
- Six nearby cells do not establish broad independent ecological replication.
- Historical evaluation was inspected; all new diagnostics are exploratory.
- Daily means/current-day weather support retrospective emulation, not forecasting.
- Component bookkeeping does not establish full conservation or intervention validity.
- No compatible tower validation, causal scenario experiment or paired JULES runtime.
- Uncertainty is simulator residual uncertainty, not full environmental uncertainty.
- Exact original access agreement absent; new data acquisition and manuscript
  publication must document applicable terms. Aggregate release approval is scoped.
- Before submission: resolve simulator provenance, compare complete primary literature,
  seek independent domain review, document data access and add genuinely external
  evaluation or narrow the manuscript's claim accordingly. Journal selection follows
  the resulting study; no acceptance or publication-ready claim is made.

## Proposed funding work packages
### WP1 - Establish simulator provenance
Hypothesis: reproducible configuration and matched workloads make emulator fidelity
and computational tradeoffs interpretable. Required data: run/version, crop,
management, soil initialization, forcing and authorized executable configuration.
Experiment: rerun a documented reference case and time paired JULES/emulator
workloads including setup and inference. Deliverable: versioned provenance and
runtime benchmark. Success: reference reproducible within declared tolerance and
speed comparison reports workload, hardware and variability; no success requires
an emulator speed advantage.

### WP2 - Test wider generalisation
Hypothesis: input/state information governs transfer as much as architecture.
Required data: independently specified locations/configurations or later periods,
with documented access and no overlap with model selection. Experiment:
preregister held-region/configuration evaluation, matched baselines, seeds and
uncertainty before fitting. Deliverable: external benchmark and failure analysis.
Success: all prespecified comparisons and uncertainty metrics reported on the
independent dataset, including negative findings; no arbitrary R² target.

### WP3 - Connect observations and decisions
Hypothesis: configuration-aware emulation can support useful diagnostics when
observational alignment and scenario validity are established. Required data:
QA-controlled tower fluxes, footprints, compatible crop/management/weather and
paired simulator management scenarios. Experiment: preregister aligned tower
evaluation separately from emulator fidelity; compare surrogate responses with
paired simulator interventions. Deliverable: observational validation protocol
and tested scenario workflow. Success: coverage/accuracy and scenario discrepancies
reported under explicit tolerances; incompatible data excluded with reasons.
Carbon savings or land-management advice require further evidence.

These packages are proposals, not funded or completed projects. A future funding
application should cost staff, data, compute and stakeholder evaluation from
actual quotes and requirements rather than invented budgets.
