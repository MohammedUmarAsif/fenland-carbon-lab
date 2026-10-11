"""Public candidate cannot accidentally contain a source series or old thesis asset."""

import json

import pandas as pd
import pytest

from fenland_carbon_lab.public_export import FILES, REPORTS, export_public


def test_aggregate_allowlist_and_mixed_destination_rejected(tmp_path):
    local, reports, output = (tmp_path / name for name in ("local", "reports", "output"))
    runs = local / "runs"
    runs.mkdir(parents=True)
    (local / "data").mkdir()
    reports.mkdir()
    (runs / "selected.json").write_text(json.dumps({"run_id": "weather-test"}))
    (local / "data/qc.json").write_text(
        json.dumps({"cells": 6, "rows": 100, "private": "not exported"})
    )
    pd.DataFrame([{"run_id": "weather-test", "target": "nee", "rmse": 2.0}]).to_csv(
        runs / "metrics.csv", index=False
    )
    for name in ("coverage.csv", "diagnostics.csv"):
        pd.DataFrame(
            [{"run_id": "weather-test", "target": "nee", "group": "pooled", "n": 100}]
        ).to_csv(runs / name, index=False)
    (runs / "paired_comparisons.json").write_text("[]")
    (runs / "predictions.csv").write_text("key,nee_true,nee_pred\nPRIVATE,1,2")
    for name in REPORTS:
        (reports / name).write_text(
            "[]"
            if name == "BIBLIOGRAPHY.json"
            else "{}"
            if name.endswith(".json")
            else "New authored methods"
        )
    export_public(local, output, reports)
    assert {p.name for p in output.iterdir()} == FILES
    data = json.loads((output / "research.json").read_text())
    assert set(data["qc"]) == {"cells", "rows"}
    assert "mapping" not in data and "assets" not in data and "runs" not in data
    assert "PRIVATE" not in "".join(p.read_text() for p in output.iterdir())
    assert (
        json.loads((output / "PACKAGE_MANIFEST.json").read_text())["public_release_approved"]
        is False
    )
    (output / "thesis.html").write_text("Private reading edition")
    with pytest.raises(ValueError, match="non-allowlisted"):
        export_public(local, output, reports)
    assert (output / "thesis.html").exists()
