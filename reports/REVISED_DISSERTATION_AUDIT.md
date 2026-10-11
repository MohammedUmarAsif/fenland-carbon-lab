# Revised dissertation reconciliation

Source SHA-256: `591b093fcdde219d3d4a3e1d0688fb628a5e23d258d3c8bb7e9ea4f0370e740e`. 50 pages; cover 2026.

Meteorology Driven LSTM Surrogates for Emulating JULES-Crop Carbon Flux Components in Miscanthus Simulations

Reproduced refers to the identified document fact or current implementation; never implies reproduction of all revised dissertation scores.

| Topic | PDF pages | Status | Reported | Evidence |
|---|---|---|---|---|
| Document identity | 1 | reproduced | Revised meteorology-driven component surrogate dissertation, cover 2026 | PDF cover inspected; distinct from earlier 2025 materials. |
| NEE headline scores | 2, 28 | contradicted | Abstract NEE R² approximately 0.76; Table 2 gives 0.804 | Internal inconsistency. These reported scores are not adopted as current verified results. |
| History window | 25, 44 | contradicted | Methods 24 daily steps; appendix config window=30 | Document text/config conflict; appendix execution lineage unresolved. |
| Baseline information | 26, 47 | unresolved | Methods same-window engineered summaries; appendix comment last-step snapshots | Supporting original baseline module/execution lineage required. Current benchmark gives all daily lags to tabular models. |
| Units | 25, 44, 46 | contradicted | Methods no conversion, kg units; appendix includes carbon-to-micromole conversion | Document/appendix inconsistency. Current source metadata and exact 12.0107 carbon mass conversion audited. |
| Chronological split and scaling | 25 | reported | 70/15/15 chronology and train-only scaling | Narrative inspected; original executed artifacts do not establish this revised claim. Current pipeline verifies explicit year partitions and training-only fitting. |
| Carbon accounting | 10, 24, 28 | reproduced | NEE = plant respiration + soil respiration minus uptake | Identity explicitly implemented and tested in current pipeline; not proof of all historical execution. |
| Monthly results | 30, 49 | unresolved | Monthly improvements; appendix calls approximate index bins | Historical timestamp lineage unresolved. Current analysis uses exact calendar months and excludes incomplete months. |
| Miscanthus and simulator configuration | 1, 24 | unresolved | Miscanthus-parameterised JULES-Crop | Retained as dissertation-described setting; source run/version/crop and management configuration not established by available NetCDF metadata. |
| Observational accuracy and speedup | 2, 37, 38 | unresolved | Simulator fidelity, with potential acceleration and future diagnostics | No aligned observational validation or paired JULES runtime benchmark; no current field-accuracy or speedup claim. |

Acknowledgements (page 3): Professor Heiko Balzter, supervision and scientific standards; Dr Asima Khan, data preparation and component accounting guidance; Dr Muhammad Ali, technical guidance on native geometry and clean splits. These are author acknowledgements, not endorsement of the later extension.

Original PDF is preserved privately. No original PDF text, figure or administrative content is redistributed. New explanations and this factual reconciliation are authored for the extension.
