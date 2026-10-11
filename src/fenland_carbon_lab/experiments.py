"""Frozen bounded benchmark. Results/checkpoints written after each run."""

from __future__ import annotations

import copy
import json
import platform
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

from .data import COMPONENTS, WEATHER, nee, samples
from .metrics import interval_metrics, metrics, monthly, paired_blocks

SEEDS = [17, 29, 43]
torch.set_num_threads(4)


class Sequence(torch.nn.Module):
    def __init__(self, inputs, outputs):
        super().__init__()
        self.rnn = torch.nn.LSTM(inputs, 16, batch_first=True)
        self.head = torch.nn.Linear(16, outputs)

    def forward(self, x):
        return self.head(self.rnn(x)[0][:, -1])


def fit_predict(
    kind,
    x,
    y,
    meta,
    seed,
    config,
    out,
    run_id,
    direct=False,
    train_override=None,
    eval_override=None,
):
    train = (meta.split == "train").to_numpy() if train_override is None else train_override
    val = (meta.split == "validation").to_numpy()
    if train_override is not None:
        val = val & ~np.isin(meta.cell, meta.cell[eval_override].unique())
    evaluate = ~train if eval_override is None else eval_override
    if not train.any() or not evaluate.any():
        raise ValueError("Empty train/evaluation")
    saved = out / f"{run_id}.json"
    if saved.exists() and (out / f"{run_id}.csv").exists():
        previous = json.loads(saved.read_text())
        if (
            previous["config"] == config
            and previous["seed"] == seed
            and previous["direct"] == direct
            and previous["train_n"] == int(train.sum())
            and previous["length_days"] == x.shape[1]
            and previous["features"] == x.shape[2]
        ):
            cached = pd.read_csv(
                out / f"{run_id}.csv", parse_dates=["start", "end", "feature_start", "feature_end"]
            )
            if cached.key.tolist() == meta.loc[evaluate, "key"].tolist():
                return cached, previous
    t0 = time.perf_counter()
    yt = nee(y)[:, None] if direct else y
    sx, sy = StandardScaler(), StandardScaler()
    # Repeated window entries are eligible training data only. Their weighting is explicit.
    sx.fit(x[train].reshape(-1, x.shape[-1]))
    sy.fit(yt[train])
    z = sx.transform(x.reshape(-1, x.shape[-1])).reshape(x.shape).astype(np.float32)
    target = sy.transform(yt).astype(np.float32)
    history = []
    if kind == "climatology":
        months = pd.to_datetime(meta.start).dt.month.to_numpy()
        means = {m: yt[train & (months == m)].mean(axis=0) for m in range(1, 13)}
        prediction = np.array([means[m] for m in months[evaluate]])
        model = None
    elif kind == "lstm":
        torch.manual_seed(seed)
        torch.use_deterministic_algorithms(True)
        model = Sequence(x.shape[-1], yt.shape[-1])
        optimizer = torch.optim.Adam(model.parameters(), lr=0.003)
        tx, ty = torch.from_numpy(z[train]), torch.from_numpy(target[train])
        vx, vy = torch.from_numpy(z[val]), torch.from_numpy(target[val])
        generator = torch.Generator().manual_seed(seed)
        best, best_state, patience = float("inf"), None, 0
        for epoch in range(15):
            model.train()
            total = 0.0
            order = torch.randperm(len(tx), generator=generator)
            for batch in order.split(256):
                optimizer.zero_grad()
                loss = torch.nn.functional.mse_loss(model(tx[batch]), ty[batch])
                loss.backward()
                optimizer.step()
                total += float(loss.detach()) * len(batch)
            model.eval()
            with torch.no_grad():
                vloss = float(torch.nn.functional.mse_loss(model(vx), vy))
            history.append(
                {
                    "epoch": epoch + 1,
                    "train_mse_scaled": total / len(tx),
                    "validation_mse_scaled": vloss,
                }
            )
            if vloss < best:
                best, best_state, patience = vloss, copy.deepcopy(model.state_dict()), 0
            else:
                patience += 1
            if patience >= 4:
                break
        model.load_state_dict(best_state)
        with torch.no_grad():
            scaled = np.concatenate(
                [model(b).numpy() for b in torch.from_numpy(z[evaluate]).split(512)]
            )
        prediction = sy.inverse_transform(scaled)
        torch.save(
            {"state_dict": model.state_dict(), "inputs": x.shape[-1], "outputs": yt.shape[-1]},
            out / f"{run_id}.pt",
        )
    else:
        flat = z.reshape(len(z), -1)
        if kind == "ridge":
            model = Ridge(alpha=config.get("alpha", 1))
        elif kind == "rf":
            model = RandomForestRegressor(
                n_estimators=80,
                max_depth=14,
                min_samples_leaf=config.get("leaf", 3),
                random_state=seed,
                n_jobs=4,
            )
        elif kind == "boosting":
            model = MultiOutputRegressor(
                HistGradientBoostingRegressor(
                    max_iter=120,
                    max_depth=4,
                    learning_rate=0.08,
                    l2_regularization=1,
                    random_state=seed,
                    early_stopping=False,
                )
            )
        else:
            raise ValueError(kind)
        with threadpool_limits(limits=4):
            model.fit(flat[train], target[train])
            prediction = sy.inverse_transform(
                np.asarray(model.predict(flat[evaluate])).reshape(-1, yt.shape[-1])
            )
        import joblib

        joblib.dump({"model": model, "sx": sx, "sy": sy}, out / f"{run_id}.joblib")
    elapsed = time.perf_counter() - t0
    f = meta.loc[evaluate].copy()
    for j, c in enumerate(COMPONENTS):
        f[c + "_true"] = y[evaluate, j]
        if not direct:
            f[c + "_pred"] = prediction[:, j]
    f["nee_true"] = nee(y[evaluate])
    f["nee_pred"] = prediction[:, 0] if direct else nee(prediction)
    f["model"] = kind
    f["seed"] = seed
    f["run_id"] = run_id
    f.to_csv(out / f"{run_id}.csv", index=False)
    stats = {
        "run_id": run_id,
        "model": kind,
        "direct": direct,
        "seed": seed,
        "config": config,
        "length_days": x.shape[1],
        "features": x.shape[2],
        "train_n": int(train.sum()),
        "train_first": str(meta.start[train].min()),
        "train_last": str(meta.start[train].max()),
        "train_cells": sorted(meta.cell[train].unique().tolist()),
        "elapsed_seconds": elapsed,
        "feature_mean": sx.mean_.tolist(),
        "feature_scale": sx.scale_.tolist(),
        "target_mean": sy.mean_.tolist(),
        "target_scale": sy.scale_.tolist(),
        "history": history,
        "hardware": platform.processor(),
        "platform": platform.platform(),
        "torch_threads": 4,
        "python": platform.python_version(),
        "peak_memory_note": "Process peak recorded at programme end; not isolated per-model peak.",
    }
    stats["scores"] = {split: metrics(g.nee_true, g.nee_pred) for split, g in f.groupby("split")}
    (out / f"{run_id}.json").write_text(json.dumps(stats, indent=2))
    print(run_id, stats["scores"], round(elapsed, 1), flush=True)
    return f, stats


def load_data(path):
    return pd.read_csv(path, parse_dates=["start", "end", "label"])


def select(data, out):
    scores = []
    for year in [2010, 2012]:
        d = data[data.start.dt.year <= year + 1].copy()
        d["split"] = np.where(d.start.dt.year <= year, "train", "validation")
        x, y, m = samples(d, 24)
        for kind, options in [
            ("ridge", [{"alpha": 1}, {"alpha": 100}]),
            ("rf", [{"leaf": 3}, {"leaf": 10}]),
        ]:
            for config in options:
                rid = f"rolling-{year}-{kind}-{next(iter(config.values()))}"
                _, s = fit_predict(kind, x, y, m, 17, config, out, rid)
                # Selection uses mean of component RMSE, not NEE cancellation.
                p = pd.read_csv(out / f"{rid}.csv")
                score = np.mean(
                    [metrics(p[c + "_true"], p[c + "_pred"])["rmse"] for c in COMPONENTS]
                )
                scores.append(
                    {
                        "kind": kind,
                        "config": config,
                        "fold": year,
                        "mean_component_rmse": float(score),
                    }
                )
    best = {}
    for kind in ["ridge", "rf"]:
        options = {json.dumps(r["config"], sort_keys=True) for r in scores if r["kind"] == kind}
        choice = min(
            options,
            key=lambda k: np.mean(
                [
                    r["mean_component_rmse"]
                    for r in scores
                    if r["kind"] == kind and json.dumps(r["config"], sort_keys=True) == k
                ]
            ),
        )
        best[kind] = json.loads(choice)
    (out / "selection.json").write_text(json.dumps({"folds": scores, "selected": best}, indent=2))
    return best


def run(data_path: Path, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    data = load_data(data_path)
    best = select(data, out)
    registry = []
    for length in [1, 7, 24, 60]:
        x, y, m = samples(data, length)
        m.to_csv(out / f"samples-{length}.csv", index=False)
        for kind in ["climatology", "ridge", "rf", "boosting", "lstm"]:
            for seed in SEEDS if kind in ["rf", "boosting", "lstm"] else [17]:
                rid = f"weather-{kind}-L{length}-s{seed}"
                _, s = fit_predict(kind, x, y, m, seed, best.get(kind, {}), out, rid)
                registry.append(s)
        (out / "registry.json").write_text(json.dumps(registry, indent=2))
    # Direct target comparison with identical weather/splits and matched model budgets.
    x, y, m = samples(data, 24)
    for kind in ["rf", "boosting", "lstm"]:
        for seed in SEEDS:
            rid = f"direct-{kind}-L24-s{seed}"
            _, s = fit_predict(kind, x, y, m, seed, best.get(kind, {}), out, rid, direct=True)
            registry.append(s)
    # One controlled feature family at a time, without test-target-driven tuning.
    doy = data.start.dt.dayofyear
    data["doy_sin"] = np.sin(2 * np.pi * doy / 365.2425)
    data["doy_cos"] = np.cos(2 * np.pi * doy / 365.2425)
    for days in [7, 30]:
        data[f"rain{days}"] = data.groupby(["cell", "split"]).pr.transform(
            lambda s: s.shift(1).rolling(days).sum()
        )
    # FAO-56 saturation equation and ideal mixing-ratio conversion; daily-mean approximation.
    tc = data.tair - 273.15
    e = data.humidity * data.pressure / (0.622 + 0.378 * data.humidity) / 1000
    data["vpd"] = np.maximum(0.6108 * np.exp(17.27 * tc / (tc + 237.3)) - e, 0)
    for name, extras in [
        ("calendar", ["doy_sin", "doy_cos"]),
        ("rain", ["rain7", "rain30"]),
        ("vpd", ["vpd"]),
        ("state", ["sm0", "sm1", "sm2", "sm3"]),
    ]:
        x, y, m = samples(data, 24, WEATHER + extras)
        for seed in SEEDS:
            _, s = fit_predict(
                "rf", x, y, m, seed, best["rf"], out, f"ablation-{name}-rf-L24-s{seed}"
            )
            registry.append(s)
    # Preselected architecture; held-cell exclusion includes validation used for selection.
    x, y, m = samples(data, 24)
    for cell in sorted(m.cell.unique()):
        nested = out / f"selection-{cell}"
        nested.mkdir(exist_ok=True)
        cell_best = select(data[data.cell.ne(cell)], nested)
        train = (m.split.eq("train") & m.cell.ne(cell)).to_numpy()
        for task, split in [("spatial", "validation"), ("joint", "test")]:
            evaluate = (m.cell.eq(cell) & m.split.eq(split)).to_numpy()
            for seed in SEEDS:
                _, s = fit_predict(
                    "rf",
                    x,
                    y,
                    m,
                    seed,
                    cell_best["rf"],
                    out,
                    f"{task}-{cell}-s{seed}",
                    train_override=train,
                    eval_override=evaluate,
                )
                s["transfer_selection_note"] = (
                    "Rolling hyperparameter selection excludes held cell entirely; nested pre-test group isolation."
                )
                registry.append(s)
    (out / "registry.json").write_text(json.dumps(registry, indent=2))
    summarize(out, data)


def summarize(out, data=None):
    registry = json.loads((out / "registry.json").read_text())
    scores, coverage, diagnostics, covariances = [], [], [], []
    # Choose final model on validation component score, seed 17; fixed test remains reporting only.
    candidates = [r for r in registry if r["run_id"].startswith("weather-") and r["seed"] == 17]

    def val_score(r):
        f = pd.read_csv(out / (r["run_id"] + ".csv"))
        f = f[f.split == "validation"]
        return np.mean([metrics(f[c + "_true"], f[c + "_pred"])["rmse"] for c in COMPONENTS])

    chosen = min(candidates, key=val_score)["run_id"]
    for r in registry:
        f = pd.read_csv(out / (r["run_id"] + ".csv"), parse_dates=["start", "end"])
        if data is not None:
            f = f.merge(data[["key", "tair", "pr"]], on="key", validate="one_to_one")
        for split, g in f.groupby("split"):
            for target in ["nee"] + ([] if r["direct"] else COMPONENTS):
                row = {
                    "run_id": r["run_id"],
                    "model": r["model"],
                    "seed": r["seed"],
                    "length": r["length_days"],
                    "target": target,
                    "split": split,
                    **metrics(g[target + "_true"], g[target + "_pred"]),
                }
                by = [
                    metrics(c[target + "_true"], c[target + "_pred"])["rmse"]
                    for _, c in g.groupby("cell")
                ]
                row["cell_balanced_rmse"] = float(np.mean(by))
                row["budget_error_gC_m2_cell_mean"] = float(
                    ((g[target + "_pred"] - g[target + "_true"]) * g.seconds * 12.0107e-6)
                    .groupby(g.cell)
                    .sum()
                    .mean()
                )
                scores.append(row)
                if split == "test":
                    for cell, c in g.groupby("cell"):
                        diagnostics.append(
                            {
                                "run_id": r["run_id"],
                                "target": target,
                                "group": "cell",
                                "label": cell,
                                **metrics(c[target + "_true"], c[target + "_pred"]),
                            }
                        )
                    for season, c in g.groupby(
                        ((g.start.dt.month % 12) // 3).map(
                            {0: "winter", 1: "spring", 2: "summer", 3: "autumn"}
                        )
                    ):
                        diagnostics.append(
                            {
                                "run_id": r["run_id"],
                                "target": target,
                                "group": "season",
                                "label": season,
                                **metrics(c[target + "_true"], c[target + "_pred"]),
                            }
                        )
            if split == "test" and not r["direct"]:
                errors = np.column_stack([g[c + "_pred"] - g[c + "_true"] for c in COMPONENTS])
                covariances.append(
                    {
                        "run_id": r["run_id"],
                        "signed_error_covariance": np.cov(errors, rowvar=False).tolist(),
                        "nee_error_variance": float(np.var(errors @ np.array([-1, 1, 1]), ddof=1)),
                        "component_mean_errors": errors.mean(axis=0).tolist(),
                    }
                )
        cal = f[f.split == "calibration"].copy()
        test = f[f.split == "test"].copy()
        if len(cal) and len(test):
            for target in ["nee"] + ([] if r["direct"] else COMPONENTS):
                residual = abs(cal[target + "_pred"] - cal[target + "_true"]).to_numpy()
                for level in [0.68, 0.8, 0.9, 0.95]:
                    q = min(1, np.ceil((len(residual) + 1) * level) / len(residual))
                    width = float(np.quantile(residual, q, method="higher"))
                    test[f"{target}_lo{int(level * 100)}"] = test[target + "_pred"] - width
                    test[f"{target}_hi{int(level * 100)}"] = test[target + "_pred"] + width
                    groups = [("pooled", "all", test)]
                    groups += [("cell", str(k), g) for k, g in test.groupby("cell")]
                    groups += [
                        ("season", str(k), g)
                        for k, g in test.groupby(
                            ((test.start.dt.month % 12) // 3).map(
                                {0: "winter", 1: "spring", 2: "summer", 3: "autumn"}
                            )
                        )
                    ]
                    for group, label, g in groups:
                        coverage.append(
                            {
                                "run_id": r["run_id"],
                                "target": target,
                                "level": level,
                                "calibration_n": len(cal),
                                "group": group,
                                "label": label,
                                "n": len(g),
                                **interval_metrics(
                                    g[target + "_true"].to_numpy(),
                                    g[target + "_pred"].to_numpy(),
                                    width,
                                    level,
                                ),
                            }
                        )
            if r["run_id"] == chosen:
                test.to_csv(out / "selected_test_intervals.csv", index=False)
        if r["run_id"] == chosen:
            mo = monthly(f)
            mo.to_csv(out / "selected_monthly.csv", index=False)
            full = mo[mo.complete & mo.split.eq("test")]
            (out / "selected_monthly_metrics.json").write_text(
                json.dumps(metrics(full.reference_gC, full.predicted_gC), indent=2)
            )
            if data is not None:
                eligible = samples(data, 24)[2]
                eligible_keys = eligible.loc[eligible.split.eq("train"), "key"]
                train = data[data.key.isin(eligible_keys)]
                thresholds = {
                    "warm_tair": float(train.tair.quantile(0.95)),
                    "dry_pr": float(train.pr.quantile(0.25)),
                    "wet_pr": float(train.pr.quantile(0.75)),
                    "tail_nee": float(abs(train.nee).quantile(0.95)),
                }
                for label, mask in [
                    ("warm", test.tair >= thresholds["warm_tair"]),
                    ("dry", test.pr <= thresholds["dry_pr"]),
                    ("wet", test.pr >= thresholds["wet_pr"]),
                    ("high_flux", abs(test.nee_true) >= thresholds["tail_nee"]),
                ]:
                    g = test[mask]
                    diagnostics.append(
                        {
                            "run_id": chosen,
                            "target": "nee",
                            "group": "event",
                            "label": label,
                            **metrics(g.nee_true, g.nee_pred),
                        }
                    )
                (out / "event_thresholds.json").write_text(json.dumps(thresholds, indent=2))
    pd.DataFrame(scores).to_csv(out / "metrics.csv", index=False)
    pd.DataFrame(coverage).to_csv(out / "coverage.csv", index=False)
    pd.DataFrame(diagnostics).to_csv(out / "diagnostics.csv", index=False)
    (out / "component_covariance.json").write_text(json.dumps(covariances, indent=2))
    comparisons = []
    for other in [
        "weather-rf-L24-s17",
        "weather-lstm-L24-s17",
        "weather-boosting-L24-s17",
        "weather-rf-L60-s17",
        "weather-boosting-L60-s17",
    ]:
        a = pd.read_csv(out / (chosen + ".csv"))
        a = a[a.split == "test"]
        b = pd.read_csv(out / (other + ".csv"))
        b = b[b.split == "test"]
        for block in [7, 30, 90]:
            comparisons.append({"a": chosen, "b": other, **paired_blocks(a, b, block)})
    (out / "paired_comparisons.json").write_text(json.dumps(comparisons, indent=2))
    (out / "selected.json").write_text(
        json.dumps(
            {
                "run_id": chosen,
                "selection": "2015 mean component RMSE, seed 17; compare seeds separately",
            },
            indent=2,
        )
    )
