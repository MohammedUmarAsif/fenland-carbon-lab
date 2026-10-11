"""Allowlisted aggregate research-results edition; no source series or thesis copy."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pandas as pd

REPORTS = (
    "RESEARCH_REPORT.md",
    "PROTOCOL.md",
    "CORRECTIONS.md",
    "DATA_CARD.md",
    "MODEL_CARD.md",
    "OBSERVATIONAL_FEASIBILITY.md",
    "INTERVIEW.md",
    "CLAIM_LEDGER.csv",
    "EXPERIMENT_LINEAGE.csv",
    "BIBLIOGRAPHY.json",
    "EXPERIMENT_STATUS.json",
    "VALIDATION.md",
    "PUBLICATION.md",
)
FILES = {
    "research.json",
    "metrics.csv",
    "coverage.csv",
    "diagnostics.csv",
    "paired_comparisons.json",
    "robots.txt",
    "PACKAGE_MANIFEST.json",
    *REPORTS,
}


def export_public(
    local: Path, destination: Path, reports: Path = Path("reports"), approval: dict | None = None
):
    destination.mkdir(parents=True, exist_ok=True)
    # Refuse mixed packages; never remove an existing local/private asset.
    existing = {
        p.relative_to(destination).as_posix() for p in destination.rglob("*") if p.is_file()
    }
    if existing - FILES:
        raise ValueError(
            "Aggregate destination contains non-allowlisted files; use a separate folder"
        )
    runs = local / "runs"
    selected = json.loads((runs / "selected.json").read_text())
    coverage = pd.read_csv(runs / "coverage.csv")
    diagnostics = pd.read_csv(runs / "diagnostics.csv")
    metadata = json.loads((local / "data/qc.json").read_text())
    data = {
        "publication_mode": "aggregate",
        "generated": "2026-10-12",
        "selected": selected,
        "metrics": json.loads(pd.read_csv(runs / "metrics.csv").to_json(orient="records")),
        "coverage": json.loads(
            coverage[coverage.run_id.eq(selected["run_id"]) & coverage.group.ne("cell")].to_json(
                orient="records"
            )
        ),
        "diagnostics": json.loads(
            diagnostics[
                diagnostics.run_id.eq(selected["run_id"]) & diagnostics.group.ne("cell")
            ].to_json(orient="records")
        ),
        "paired": json.loads((runs / "paired_comparisons.json").read_text()),
        "bibliography": json.loads((reports / "BIBLIOGRAPHY.json").read_text()),
        "qc": {"cells": metadata["cells"], "rows": metadata["rows"]},
        "status": json.loads((reports / "EXPERIMENT_STATUS.json").read_text()),
        "scope": "New code, methods and aggregate research findings. No source observations/simulator rows, daily predictions, weights, scaler statistics or dissertation reproduction.",
        "rights": "Research/educational access asserted by author; public redistribution licence for source materials not established. No source-data licence is granted by this package. Aggregate publication must still comply with the original access agreement.",
    }
    if approval and approval.get("approved") is True:
        data["status"]["publication"] = (
            "Author-approved aggregate release; source materials remain private"
        )
    (destination / "research.json").write_text(
        json.dumps(data, ensure_ascii=False), encoding="utf-8"
    )
    for name in ("metrics.csv", "coverage.csv", "diagnostics.csv", "paired_comparisons.json"):
        shutil.copyfile(runs / name, destination / name)
    for name in REPORTS:
        shutil.copyfile(reports / name, destination / name)
    (destination / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
    # Canonical LF bytes make manifest hashes portable without changing values.
    for path in destination.iterdir():
        if path.is_file() and path.name != "PACKAGE_MANIFEST.json":
            path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
    manifest = {
        "profile": "aggregate",
        "date": "2026-10-12",
        "public_release_approved": bool(
            approval and approval.get("approved") is True and approval.get("profile") == "aggregate"
        ),
        "approval_reference": approval.get("approval_reference") if approval else None,
        "scope": data["scope"],
        "rights": data["rights"],
        "files": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in destination.iterdir()
            if p.is_file() and p.name != "PACKAGE_MANIFEST.json"
        },
    }
    (destination / "PACKAGE_MANIFEST.json").write_bytes(json.dumps(manifest, indent=2).encode("utf-8"))
    assert {p.name for p in destination.iterdir() if p.is_file()} <= FILES
    print(
        f"Prepared aggregate candidate: {len(manifest['files'])} files; no daily series or thesis media"
    )
