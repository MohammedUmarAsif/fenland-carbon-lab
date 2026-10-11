"""Numerical report generated exclusively from validated keyed experiment outputs."""

from __future__ import annotations

import hashlib
import json
import platform
import time
from pathlib import Path

import numpy as np
import pandas as pd
import psutil

from .data import samples
from .experiments import load_data
from .export import training_predictions


def markdown_table(frame, columns):
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, r in frame.iterrows():
        values = [
            f"{r[c]:.4f}" if isinstance(r[c], (float, np.floating)) else str(r[c]) for c in columns
        ]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def report(local: Path, reports: Path):
    out = local / "runs"
    m = pd.read_csv(out / "metrics.csv")
    coverage = pd.read_csv(out / "coverage.csv")
    registry = json.loads((out / "registry.json").read_text())
    excluded = {"feature_mean", "feature_scale", "target_mean", "target_scale"}
    public_registry = [{k: v for k, v in r.items() if k not in excluded} for r in registry]
    (reports / "RUN_REGISTRY.json").write_text(json.dumps(public_registry, indent=2))
    memory_path = local / "training_memory.json"
    if memory_path.exists():
        (reports / "TRAINING_MEMORY.json").write_text(memory_path.read_text())
    rid = json.loads((out / "selected.json").read_text())["run_id"]
    approval_path = Path("config/public-release.json")
    approval = json.loads(approval_path.read_text()) if approval_path.exists() else {}
    aggregate_approved = approval.get("approved") is True and approval.get("profile") == "aggregate"
    publication = (
        "Author-approved aggregate-results release; underlying data, daily rows, weights, scaler statistics and historical dissertation materials remain private. Repository: https://github.com/MohammedUmarAsif/fenland-carbon-lab."
        if aggregate_approved
        else "Local preview; publication pending scoped approval and applicable content/data rights."
    )
    chosen = m[m.run_id.eq(rid) & m.target.eq("nee") & m.split.eq("test")].iloc[0]

    def metric(run):
        return m[m.run_id.eq(run) & m.target.eq("nee") & m.split.eq("test")].iloc[0]

    rf1, rf24, rf60 = map(metric, ["weather-rf-L1-s17", "weather-rf-L24-s17", "weather-rf-L60-s17"])
    state = metric("ablation-state-rf-L24-s17")
    direct = metric("direct-rf-L24-s17")
    seed_rows = m[
        m.run_id.str.startswith("weather-lstm-L60-") & m.target.eq("nee") & m.split.eq("test")
    ]
    boost60 = metric("weather-boosting-L60-s17")
    cov = coverage[
        coverage.run_id.eq(rid)
        & coverage.target.eq("nee")
        & coverage.level.eq(0.95)
        & coverage.group.eq("pooled")
    ].iloc[0]
    rows = m[
        m.run_id.str.startswith("weather-")
        & m.target.eq("nee")
        & m.split.eq("test")
        & m.seed.eq(17)
    ]
    ablation = m[m.run_id.str.startswith("ablation-") & m.target.eq("nee") & m.split.eq("test")]
    transfer = m[m.run_id.str.startswith(("joint-", "spatial-")) & m.target.eq("nee")]
    timing = sum(r["elapsed_seconds"] for r in registry)
    selection_count = len(list(out.rglob("rolling-*.json")))
    source_hashes = pd.read_csv(local / "audit/inventory.csv")
    raw_hash = source_hashes[source_hashes.path.str.endswith(".nc")].sha256.iloc[0]
    historical = json.loads((local / "forensic/historical_checks.json").read_text())
    media = pd.read_csv(local / "audit/media_audit.csv")
    duplicate_count = int(source_hashes.sha256.duplicated(keep=False).sum())
    # Full training batches include standardization and prediction, excluding I/O/window construction.
    r = next(r for r in registry if r["run_id"] == rid)
    data = load_data(local / "data/cells.csv")
    x, y, meta = samples(data, r["length_days"])
    counts = meta.groupby("split").size().to_dict()
    timings = []
    for _ in range(6):
        t = time.perf_counter()
        training_predictions(x, y, meta, r, out)
        timings.append(time.perf_counter() - t)
    timing_report = {
        "run_id": rid,
        "batch_size": int(meta.split.eq("train").sum()),
        "repeats": 5,
        "warmup": 1,
        "median_seconds": float(np.median(timings[1:])),
        "includes": "Scaler application, local checkpoint loading, prediction, dataframe assembly; excludes extraction/window construction",
        "hardware": platform.processor(),
        "platform": platform.platform(),
        "logical_cpus": psutil.cpu_count(),
        "ram_bytes": psutil.virtual_memory().total,
        "process_rss_after_bytes": psutil.Process().memory_info().rss,
        "thread_budget": 4,
        "jules_comparable_timing": None,
    }
    (reports / "INFERENCE_BENCHMARK.json").write_text(json.dumps(timing_report, indent=2))
    text = f"""# Fenland Carbon Lab research report

Generated 12 October 2026 from keyed predictions; extension of Mohammed Umar
Asif Sayed's University of Leicester 2025 MSc dissertation. AI assistance is
credited separately. This is simulator emulation, not observational validation.

## Principal measured result

The pre-test validation-selected weather-only component model **{rid}** achieves
NEE RMSE **{chosen.rmse:.4f} μmol CO2 m-2 s-1**, MAE {chosen.mae:.4f}, signed bias
{chosen.bias:.4f}, and R² **{chosen.r2:.4f}** on **{int(chosen.n)}** reserved test
cell-days. Mean per-cell RMSE is {chosen.cell_balanced_rmse:.4f}. The reserved
period is retrospective within an already inspected dataset, not prospective.

The strongest contribution is controlled, auditable comparison, not a universal
LSTM superiority claim. Old scores cannot be compared directly to these results:
inputs, targets, physical conversion, validation and sample weighting differ.

Across three seeds, 60-day LSTM RMSE spans {seed_rows.rmse.min():.4f}–{seed_rows.rmse.max():.4f},
with mean {seed_rows.rmse.mean():.4f}; deterministic 60-day boosting achieves
{boost60.rmse:.4f}. The selected seed's advantage does not establish robust LSTM
superiority. Seed 17 was fixed before comparison, not chosen on test performance.

## Evidence recovery

{len(source_hashes)} physical files, source ZIP archives and office documents inventoried.
Physical SHA-256 duplicate inspection identifies {duplicate_count} repeated file entries.
{int(media.path.str.endswith(".png").sum())} historical PNGs decode; a four-sheet visual review identifies blank July
emissions maps. Six MP4 entries are classified by size; tiny containers have
no useful playback payload. None are used in the new website. Source SHA-256
for raw NetCDF: `{raw_hash}`. Separate submitted, July and August evidence
families appear in EXPERIMENT_LINEAGE.csv and the individual CLAIM_LEDGER.csv.
Source artifacts remain untouched and administrative documents remain private.

Historical August RF RMSE {historical["metrics"]["predictions_test_rf.csv"]["rmse"]:.7f}, LSTM RMSE {historical["metrics"]["predictions_test.csv"]["rmse"]:.7f}, in stored alternate-sign
units, are reproduced to saved precision. That model uses seven features,
including fluxes. Its flux input timestamps remain unresolved; sequence metadata
H=1 does not substitute for recovered construction code. Repaired nominal 95%
uncertainty covers {historical["uncertainty"]["coverage95_repaired"] * 100:.4f}% of {historical["uncertainty"]["n"]:,} paired saved targets. No dates are assigned
to identifier-free test predictions. Submitted component predictions remain
missing, so the submitted model's headline scores are historical reports.

## Frozen experimental methods

Time interval bounds define standard-calendar daily means, 2006-2019. Native
point selection uses spherical geodesic distance and actual validity checks.
Seven labels map to six unique cells; duplicate Redmere labels receive one weight.
The complete selected extract has {len(data):,} rows. No missing required values occur.
Grid-wide screening checks coordinates and three variable time slabs; it does
not validate every variable throughout the 4.57 GB cube.

Primary inputs: current and past temperature, shortwave, precipitation, wind.
Current daily means are available after the day. This is a same-interval
retrospective emulator, not an operational weather forecast. State ablations
require soil moisture from a simulator or independently compatible input.
Carbon conversion uses 12.0107 g/mol; NEE = Rp+Rs−GPP, positive atmospheric release.

Global train 2006-2014; selection/early stopping 2015; calibration 2016;
evaluation 2017-2019. Windows never cross cells, gaps or split boundaries. Common
60-day target eligibility gives {counts["train"]:,} training, {counts["validation"]:,} validation, {counts["calibration"]:,} calibration
and {counts["test"]:,} test samples. Scalers use eligible training windows/targets only;
repeated window entries weight feature statistics but never use nontraining data.
Train-only imputation is unnecessary for these complete extracted series.
Ridge/RF hyperparameters use two rolling-origin folds; per-cell transfer tuning
excludes the held cell in both fitting and selection. Seed 17 is fixed for final
model selection on validation mean component RMSE; seeds 29/43 quantify variance.
Boosting seed replicas are identical because no stochastic subsampling is used.

## A. What survives corrected evaluation?

All listed results are newly trained, weather-only benchmark evaluations; none
inherit a legacy scaler or use carbon-component inputs.

{markdown_table(rows, ["run_id", "n", "rmse", "mae", "bias", "r2"])}

## B. Does memory add value?

RF RMSE changes from {rf1.rmse:.4f} at one day to {rf60.rmse:.4f} at 60 days
({100 * (1 - rf60.rmse / rf1.rmse):.2f}% lower) on exactly matched targets. RF/boosting
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

At 24 days, weather RF RMSE {rf24.rmse:.4f} changes to {state.rmse:.4f} with four
simulator soil moisture layers. This is a state-conditional experiment, with
different deployment requirements. Calendar, antecedent precipitation and
approximate daily VPD are controlled single-family changes, not cherry-picked
combinations. Rainfall summaries are causal within each split. VPD uses verified
K, Pa, kg/kg metadata and the FAO-56 saturation equation; clamped at zero. Daily
means approximate atmospheric dryness and cannot recover mean subdaily VPD.

{markdown_table(ablation, ["run_id", "seed", "rmse", "mae", "bias", "r2"])}

Seasonal, high-flux, precipitation quartile and warm-tail diagnostics are in
diagnostics.csv. Thresholds are fixed from training. No extra recurrent
architecture or Huber loss is justified within the frozen compute programme.
Null/negative ablations remain visible rather than being suppressed.

## D. Transfer

Spatial folds predict a held native cell in shared 2015 years after training on
other cells in 2006-2014. Joint folds predict that excluded cell in 2017-2019.
Every fold uses nested pre-test rolling selection without the held cell. Both
Redmere labels stay together. Per-cell and seed results:

{markdown_table(transfer, ["run_id", "seed", "split", "n", "rmse", "bias", "r2"])}

Highly related nearby forcing limits independence. These tests demonstrate
specific simulator-cell transfer, not a continuous regional emissions map.

## E. Direct versus component-first

Matched 24-day RF direct NEE RMSE is {direct.rmse:.4f}, versus {rf24.rmse:.4f}
from component accounting. All three model families receive direct/component
comparisons with matched seeds and architecture budgets. Component metrics,
signed biases and error covariance are retained. Algebraic identity is exact
within floating precision; opposite component errors can cancel in net exchange.
It is not full conservation, a PINN, or correct simulator hydrology.

## F. Empirical uncertainty reliability

The selected model's fixed 2016 residual quantiles yield {cov.coverage * 100:.2f}%
test coverage at nominal 95%; mean width {cov.mean_width:.4f} and interval score
{cov.interval_score:.4f} μmol CO2 m-2 s-1. Coverage/width/score are evaluated at
68/80/90/95%, by cell and season. Calibration targets are separate from test.
Temporal dependence, shared-day spatial correlation and distribution shift mean
this simple residual-quantile method has no exact IID guarantee. It is not the
EnbPI algorithm. Simulator structural uncertainty relative to nature is separate.

## Carbon budgets, cost and reproducibility

Daily carbon amounts integrate actual interval durations; complete calendar-month
budgets and monthly RMSE are regenerated in selected_monthly.csv and its metrics
JSON. Incomplete months remain labelled and excluded from monthly scoring. Mean
cumulative test NEE budget error is {chosen.budget_error_gC_m2_cell_mean:.3f}
g C m-2 per cell across the sampled test intervals. This excludes the first
59 days of the test partition and is not a full 2017-2019 balance. NEE also
excludes harvest and other net ecosystem carbon balance terms.

{len(registry)} primary/ablation/transfer model runs and {selection_count} rolling-selection
fits completed. Summed recorded fit/evaluation time for registry runs is
{timing / 60:.2f} minutes (not programme wall time). CPU budget four threads; hardware
and library lockfiles are recorded. Local inference median
{timing_report["median_seconds"]:.4f} seconds for a {timing_report["batch_size"]}-sample
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

The research experiments used local CPU compute. No paid compute or collaborator
messages were used. Publication status: {publication}
The complete local site is separate from the aggregate-results profile. No
underlying source-data licence is inferred. Read README for commands and
PUBLICATION.md for the exact release scope and remaining source-content limits.
"""
    (reports / "RESEARCH_REPORT.md").write_text(text, encoding="utf-8")
    status = {
        "date": "2026-10-12",
        "registry_runs_completed": len(registry),
        "rolling_selection_fits_completed": selection_count,
        "A": "completed",
        "B": "completed",
        "C": "completed controlled RF ablations/diagnostics",
        "D": "completed nested six-cell spatial and joint transfer, three seeds",
        "E": "completed direct/component three-family, three-seed comparisons",
        "F": "completed residual quantile calibration/evaluation; no IID guarantee",
        "observations": "feasibility complete; incompatible/unverified simulation management, no score",
        "pending_compute": [],
        "publication": publication,
    }
    (reports / "EXPERIMENT_STATUS.json").write_text(json.dumps(status, indent=2))
    walkthrough = f"""# Interview walkthrough and measured CV claims

## CV bullets for the 2026 extension

* Built an auditable daily JULES carbon-flux pipeline across six native Fenland
  cells, correcting interval alignment, kg C conversion, NEE sign and duplicate-cell weighting.
* Completed {len(registry)} controlled model runs across temporal, state and grouped-transfer
  tasks; validation-selected weather-only model achieved reserved-test NEE RMSE
  {chosen.rmse:.3f} μmol CO2 m-2 s-1 and R² {chosen.r2:.3f} on {int(chosen.n):,} cell-days.
* Delivered an interactive static evidence site with keyed prediction downloads,
  reproducible benchmarks and separately calibrated uncertainty: nominal 95%
  intervals achieved {cov.coverage * 100:.2f}% empirical test coverage.

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
"""
    (reports / "INTERVIEW.md").write_text(walkthrough, encoding="utf-8")
    checks = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob("*.csv")}
    (reports / "RESULT_CHECKSUMS.json").write_text(json.dumps(checks, indent=2))
    print("Generated report/status/CV walkthrough from", len(registry), "completed runs.")
