"""Historical checks, without unsafe deserialization or assumed sample alignment."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from docx import Document

from .metrics import metrics


def forensic(source: Path, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    z = zipfile.ZipFile(next(source.glob("*20250827*.zip")))

    def read(name):
        return z.read(next(n for n in z.namelist() if n.endswith("/" + name)))

    table = pd.read_csv(io.BytesIO(read("all_sites_timeseries.csv")))
    identity = (table.gpp - table.ra - table.rh) * 1e9 / 12
    red1 = table[table.site_name == "Redmere farm 1"].reset_index(drop=True)
    red2 = table[table.site_name == "Redmere farm 2"].reset_index(drop=True)
    results = {
        "historical_rows": len(table),
        "alternate_sign_identity_max_error": float(abs(identity - table.NEE_umol).max()),
        "redmere_identical": bool(
            np.array_equal(
                red1[["gpp", "ra", "rh", "tair", "sw", "pr", "wind", "NEE_umol"]],
                red2[["gpp", "ra", "rh", "tair", "sw", "pr", "wind", "NEE_umol"]],
            )
        ),
        "metrics": {},
        "alignment": "Saved test files lack cell/time identifiers. Metrics reproduce their paired rows only; no site/time index is assigned.",
    }
    for name in [
        "predictions_test.csv",
        "predictions_test_rf.csv",
        "predictions_test_xgb.csv",
        "predictions_test_gru.csv",
        "predictions_test_tcnn.csv",
    ]:
        f = pd.read_csv(io.BytesIO(read(name)))
        results["metrics"][name] = metrics(f.y_true_umol, f.y_pred_umol)
    u = pd.read_csv(io.BytesIO(read("uncertainty_test.csv")))
    stats = json.loads(read("target_scaler_stats.json"))["NEE_umol"]
    sd = u.y_std_scaled * stats["std"]
    mean = u.y_mean_scaled * stats["std"] + stats["mean"]
    results["uncertainty"] = {
        "n": len(u),
        "negative_std": int((u.y_std_umol < 0).sum()),
        "reversed95": int((u.lo95_umol > u.hi95_umol).sum()),
        "corrected_std_mean": float(sd.mean()),
        "coverage95_repaired": float((abs(u.y_true_umol - mean) <= 1.96 * sd).mean()),
        "coverage68_repaired": float((abs(u.y_true_umol - mean) <= sd).mean()),
        "affine_spread_error_max": float(abs(u.y_std_umol - (sd + stats["mean"])).max()),
    }
    cols = ["gpp", "ra", "rh", "tair", "sw", "pr", "wind", "NEE_umol"]
    raw = pd.read_csv(io.BytesIO(read("ml_master_raw.csv")))
    scaled = pd.read_csv(io.BytesIO(read("ml_master_scaled.csv")))
    results["august_scaled_full_table_means"] = scaled[cols].mean().to_dict()
    results["august_raw_full_target_mean"] = float(raw.NEE_umol.mean())
    for n in z.namelist():
        if n.endswith(".keras"):
            with zipfile.ZipFile(io.BytesIO(z.read(n))) as model:
                config = json.loads(model.read("config.json"))
                (out / (Path(n).stem + "_config.json")).write_text(json.dumps(config, indent=2))
    doc = Document(next(source.glob("*_GY7720_Dissertation.docx")))
    text = "\n".join(p.text for p in doc.paragraphs)
    (out / "submitted_docx.txt").write_text(text, encoding="utf-8")
    appendix = text[text.find("#!/usr/bin/env python3") :]
    (out / "appendix_verbatim.py.txt").write_text(appendix, encoding="utf-8")
    # Never execute extracted appendix. New implementation explicitly repairs the verified failure modes.
    sorted_raw = raw.sort_values(["site_name", "time"]).reset_index(drop=True)
    n = len(sorted_raw)
    effects = []
    for label, a, b in [
        ("train", 0, int(0.7 * n)),
        ("validation", int(0.7 * n), int(0.85 * n)),
        ("test", int(0.85 * n), n),
    ]:
        part = sorted_raw.iloc[a:b]
        effects.append(
            {
                "slice": label,
                "rows": len(part),
                "site_counts": part.site_name.value_counts().to_dict(),
                "time_min": part.time.min(),
                "time_max": part.time.max(),
            }
        )
    results["appendix_positional_split_demonstration_on_august_rows"] = effects
    results["demonstration_limit"] = (
        "Demonstrates the printed algorithm on available site rows; does not prove provenance of submitted scores."
    )
    results["rf_rmse_improvement_percent"] = 100 * (
        1
        - results["metrics"]["predictions_test_rf.csv"]["rmse"]
        / results["metrics"]["predictions_test.csv"]["rmse"]
    )
    (out / "historical_checks.json").write_text(json.dumps(results, indent=2))
    # Near duplicate and shared forcing audit uses raw exports, separately from six-cell extraction.
    pairs = []
    for a in table.site_name.unique():
        for b in table.site_name.unique():
            if a >= b:
                continue
            aa = table[table.site_name == a].sort_values("time")
            bb = table[table.site_name == b].sort_values("time")
            pairs.append(
                {
                    "a": a,
                    "b": b,
                    "forcing_exact": bool(
                        np.array_equal(
                            aa[["tair", "sw", "pr", "wind"]], bb[["tair", "sw", "pr", "wind"]]
                        )
                    ),
                    "flux_exact": bool(
                        np.array_equal(aa[["gpp", "ra", "rh"]], bb[["gpp", "ra", "rh"]])
                    ),
                    "temperature_correlation": float(np.corrcoef(aa.tair, bb.tair)[0, 1]),
                }
            )
    pd.DataFrame(pairs).to_csv(out / "historical_series_pairs.csv", index=False)
    print(json.dumps(results["uncertainty"]))
