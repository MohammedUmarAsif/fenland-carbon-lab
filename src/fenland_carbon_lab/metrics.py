"""Regenerable metrics and paired, shared-day block uncertainty."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import r2_score

from .data import ATOMIC_C


def metrics(y, p):
    y, p = np.asarray(y), np.asarray(p)
    if y.shape != p.shape or not np.isfinite(y).all() or not np.isfinite(p).all():
        raise ValueError("Invalid metric arrays")
    e = p - y
    return {
        "n": len(y),
        "rmse": float(np.sqrt(np.mean(e**2))),
        "mae": float(np.mean(abs(e))),
        "bias": float(e.mean()),
        "r2": float(r2_score(y, p)),
        "sign_accuracy": float(np.mean((p >= 0) == (y >= 0))),
    }


def interval_metrics(y, p, width, level):
    lo, hi = p - width, p + width
    alpha = 1 - level
    score = hi - lo + 2 / alpha * (np.maximum(lo - y, 0) + np.maximum(y - hi, 0))
    return {
        "coverage": float(np.mean((y >= lo) & (y <= hi))),
        "mean_width": float(np.mean(hi - lo)),
        "interval_score": float(np.mean(score)),
    }


def monthly(frame, target="nee"):
    f = frame.copy()
    f["month"] = pd.to_datetime(f.start).dt.to_period("M").astype(str)
    factor = ATOMIC_C * 1e-6 * f.seconds
    f["reference_gC"] = f[f"{target}_true"] * factor
    f["predicted_gC"] = f[f"{target}_pred"] * factor
    out = f.groupby(["cell", "month", "split"], as_index=False).agg(
        reference_gC=("reference_gC", "sum"),
        predicted_gC=("predicted_gC", "sum"),
        n=("key", "size"),
    )
    out["expected_days"] = pd.to_datetime(out.month).dt.days_in_month
    out["complete"] = out.n == out.expected_days
    return out


def paired_blocks(a, b, length=30, reps=300, seed=101):
    merged = a[["key", "start", "nee_true", "nee_pred"]].merge(
        b[["key", "nee_true", "nee_pred"]], on="key", suffixes=("_a", "_b"), validate="one_to_one"
    )
    if (
        len(merged) != len(a)
        or len(a) != len(b)
        or not np.allclose(merged.nee_true_a, merged.nee_true_b)
    ):
        raise ValueError("Pairwise keys or references differ")
    merged["ea"] = (merged.nee_pred_a - merged.nee_true_a) ** 2
    merged["eb"] = (merged.nee_pred_b - merged.nee_true_b) ** 2
    daily = merged.groupby("start")[["ea", "eb"]].mean().to_numpy()
    rng = np.random.default_rng(seed)
    n = len(daily)
    values = []
    for _ in range(reps):
        starts = rng.integers(0, n, size=int(np.ceil(n / length)))
        indices = ((starts[:, None] + np.arange(length)) % n).ravel()[:n]
        x = np.sqrt(daily[indices].mean(axis=0))
        values.append(x[0] - x[1])
    return {
        "difference_rmse_a_minus_b": float(
            np.sqrt(daily[:, 0].mean()) - np.sqrt(daily[:, 1].mean())
        ),
        "lower95": float(np.quantile(values, 0.025)),
        "upper95": float(np.quantile(values, 0.975)),
        "block_days": length,
        "replicates": reps,
        "shared_days": n,
    }
