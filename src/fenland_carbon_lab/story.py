"""Project story summaries from verified private artifacts; no raw rows/state."""

import json


def story_summary(local, reports, selected):
    runs = local / "runs"
    stats_path = runs / (selected["run_id"] + ".json")
    if not stats_path.exists():
        return None
    stats = json.loads(stats_path.read_text())
    covariance = json.loads((runs / "component_covariance.json").read_text())
    selected_cov = next(r for r in covariance if r["run_id"] == selected["run_id"])
    return {
        "version": 2,
        "learning_curve": stats["history"],
        "covariance": selected_cov,
        "monthly": json.loads((runs / "selected_monthly_metrics.json").read_text()),
        "support": json.loads((local / "support/summary.json").read_text()),
        "audit": json.loads((reports / "REVISED_DISSERTATION_AUDIT.json").read_text()),
        "media": json.loads((reports / "ASSET_REGISTER.json").read_text()),
        "sources": [
            "metrics.csv",
            "diagnostics.csv",
            "coverage.csv",
            "SUPPLEMENTARY_PROTOCOL.md",
            "REVISED_DISSERTATION_AUDIT.md",
            "PUBLICATION_PATHWAY.md",
        ],
    }
