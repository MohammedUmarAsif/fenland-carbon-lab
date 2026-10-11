"""Authentic result tests run locally; synthetic fixtures are never mistaken for results."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from fenland_carbon_lab.metrics import metrics

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / "local"
pytestmark = pytest.mark.skipif(
    not (LOCAL / "runs/metrics.csv").exists(), reason="Authentic private outputs unavailable"
)


def test_all_metrics_regenerate():
    reported = pd.read_csv(LOCAL / "runs/metrics.csv")
    for rid, g in reported.groupby("run_id"):
        predictions = pd.read_csv(LOCAL / "runs" / f"{rid}.csv")
        assert predictions.key.is_unique
        for _, r in g.iterrows():
            p = predictions[predictions.split == r["split"]]
            regenerated = metrics(p[r.target + "_true"], p[r.target + "_pred"])
            for field in ["rmse", "mae", "bias", "r2", "n"]:
                assert regenerated[field] == pytest.approx(r[field], rel=1e-7, abs=1e-7)


def test_matches_across_weather_models():
    registry = json.loads((LOCAL / "runs/registry.json").read_text())
    manifests = []
    for r in registry:
        if r["run_id"].startswith("weather-"):
            f = pd.read_csv(LOCAL / "runs" / (r["run_id"] + ".csv"))
            manifests.append(f.key.tolist())
            assert r["train_last"].startswith("2014")
    assert all(m == manifests[0] for m in manifests)


def test_duplicate_cell_and_transfer_isolation():
    mapping = pd.read_csv(LOCAL / "data/mapping.csv")
    assert mapping.cell.nunique() == 6
    assert mapping[mapping.site.str.startswith("Redmere")].cell.nunique() == 1
    registry = json.loads((LOCAL / "runs/registry.json").read_text())
    for r in registry:
        if r["run_id"].startswith(("joint-", "spatial-")):
            f = pd.read_csv(LOCAL / "runs" / (r["run_id"] + ".csv"))
            assert set(f.cell).isdisjoint(r["train_cells"])
            assert "excludes held cell" in r["transfer_selection_note"]


def test_website_metrics_and_intervals():
    p = ROOT / "website/public/research.json"
    if not p.exists():
        pytest.skip("Export not generated yet")
    d = json.loads(p.read_text(encoding="utf-8"))
    reported = pd.read_csv(LOCAL / "runs/metrics.csv")
    assert len(d["metrics"]) == len(reported)
    for a in d["assets"]:
        values = json.loads((ROOT / "website/public" / a["path"]).read_text())
        frame = pd.DataFrame(values, columns=d["columns"])
        assert len(frame) == a["rows"]
        assert frame.key.is_unique
        if a["run_id"].startswith("weather-"):
            f = frame[frame.split.eq("test")]
            score = metrics(f.nee_true, f.nee_pred)
            r = reported[
                reported.run_id.eq(a["run_id"])
                & reported.target.eq("nee")
                & reported.split.eq("test")
            ].iloc[0]
            assert score["rmse"] == pytest.approx(r.rmse, abs=2e-6)
            np.testing.assert_allclose(
                frame.nee_pred, frame.rp_pred + frame.rs_pred - frame.gpp_pred, atol=2e-6
            )
        filled = frame[frame.nee_lo95.notna()]
        assert (filled.nee_lo95 <= filled.nee_hi95).all()


def test_website_partitions_preserve_keyed_values():
    public = ROOT / "website/public"
    if not (public / "research.json").exists():
        pytest.skip("Export not generated yet")
    data = json.loads((public / "research.json").read_text(encoding="utf-8"))
    for asset in data["assets"]:
        full = {row[0]: row for row in json.loads((public / asset["path"]).read_text())}
        rebuilt = {}
        for identity, path in asset["partitions"].items():
            cell, split = identity.split("|")
            values = json.loads((public / path).read_text())
            part = pd.DataFrame(values, columns=data["columns"])
            assert part.cell.eq(cell).all() and part.split.eq(split).all()
            for row in values:
                assert row[0] not in rebuilt
                rebuilt[row[0]] = row
        assert full == rebuilt
