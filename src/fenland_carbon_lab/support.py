"""Frozen exploratory support diagnostic; fitted state and flags stay private."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf
from sklearn.preprocessing import StandardScaler

from .data import samples
from .metrics import metrics


def representation(windows):
    x = np.asarray(windows, dtype=float)
    if x.ndim != 3 or x.shape[1:] != (60, 4) or not np.isfinite(x).all():
        raise ValueError("Expected finite 60-day, four-weather windows")
    return np.concatenate([x[:, -1], x.mean(axis=1)], axis=1)


def fit_support(features, train):
    features, train = np.asarray(features), np.asarray(train, dtype=bool)
    if not np.isfinite(features).all() or len(features) != len(train) or train.sum() < 30:
        raise ValueError("Invalid features/training membership")
    scaler = StandardScaler().fit(features[train])
    covariance = LedoitWolf().fit(scaler.transform(features[train]))
    threshold = float(np.quantile(covariance.mahalanobis(scaler.transform(features[train])), 0.99))
    return scaler, covariance, threshold


def score_support(features, fitted):
    if not np.isfinite(features).all():
        raise ValueError("Non-finite inputs")
    scaler, covariance, threshold = fitted
    distances = covariance.mahalanobis(scaler.transform(features))
    return distances, distances > threshold


def align_predictions(predictions, flags):
    if predictions.key.duplicated().any() or flags.key.duplicated().any():
        raise ValueError("Duplicate keys")
    expected = flags.loc[flags.split.ne("train")]
    if set(predictions.key) != set(expected.key):
        raise ValueError("Incomplete prediction/flag key alignment")
    result = predictions.merge(expected, on="key", validate="one_to_one", suffixes=("", "_flag"))
    if not result.split.eq(result.split_flag).all():
        raise ValueError("Split mismatch")
    return result


def aggregate_group(group, total, width):
    n = len(group)
    row = {
        "n": n,
        "proportion": n / total,
        "interpretation": "sufficient sample" if n >= 30 else "insufficient evidence",
    }
    row.update(dict.fromkeys(["rmse", "mae", "bias", "coverage95", "mean_width95"]))
    if n >= 30:
        row.update(
            {
                k: v
                for k, v in metrics(group.nee_true, group.nee_pred).items()
                if k in ["rmse", "mae", "bias"]
            }
        )
        row["coverage95"] = float((abs(group.nee_pred - group.nee_true) <= width / 2).mean())
        row["mean_width95"] = width
    return row


def run_support(local: Path, reports: Path):
    from .experiments import load_data

    protocol = reports / "SUPPLEMENTARY_PROTOCOL.md"
    if not protocol.exists():
        raise ValueError("Record supplementary protocol before computation")
    x, _, meta = samples(load_data(local / "data/cells.csv"), 60)
    features = representation(x)
    fitted = fit_support(features, meta.split.eq("train"))
    distance, flagged = score_support(features, fitted)
    private = local / "support"
    private.mkdir(exist_ok=True)
    flags = meta[["key", "split"]].copy()
    flags["flagged"] = flagged
    flags["distance"] = distance
    flags.to_csv(private / "flags.csv", index=False)
    scaler, covariance, threshold = fitted
    (private / "fitted.json").write_text(
        json.dumps(
            {
                "mean": scaler.mean_.tolist(),
                "scale": scaler.scale_.tolist(),
                "covariance": covariance.covariance_.tolist(),
                "location": covariance.location_.tolist(),
                "threshold": threshold,
            }
        )
    )
    selected = json.loads((local / "runs/selected.json").read_text())["run_id"]
    rows = []
    coverage = pd.read_csv(local / "runs/coverage.csv")
    for run in [selected, "weather-rf-L60-s17", "weather-boosting-L60-s17"]:
        predictions = pd.read_csv(local / "runs" / (run + ".csv"))
        joined = align_predictions(predictions, flags)
        width = float(
            coverage.loc[
                coverage.run_id.eq(run)
                & coverage.target.eq("nee")
                & coverage.group.eq("pooled")
                & coverage.level.eq(0.95),
                "mean_width",
            ].iloc[0]
        )
        for split, group in joined.groupby("split"):
            for flag in [False, True]:
                subset = group[group.flagged.eq(flag)]
                rows.append(
                    {
                        "run_id": run,
                        "split": split,
                        "group": "unusual" if flag else "within training support",
                        **aggregate_group(subset, len(group), width),
                    }
                )
    summary = {
        "analysis": "exploratory input-support analysis",
        "protocol_sha256": hashlib.sha256(protocol.read_bytes()).hexdigest(),
        "minimum_group_n": 30,
        "rows": rows,
        "limitation": "Eight input summaries do not describe every sequence; flags are not failure guarantees or calibrated confidence.",
    }
    (private / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run_support(Path("local"), Path("reports"))
