"""Config-driven entry points; paths remain local, never committed."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def main():
    p = argparse.ArgumentParser(description="Fenland Carbon Lab")
    p.add_argument(
        "command",
        choices=[
            "audit",
            "extract",
            "forensic",
            "sources",
            "run",
            "summarize",
            "export",
            "smoke",
            "report",
            "evidence",
        ],
    )
    p.add_argument("--config", type=Path, default=Path("config/local.yaml"))
    args = p.parse_args()
    if args.command == "smoke":
        from .smoke import smoke

        smoke(Path("local/smoke"))
        return
    cfg = yaml.safe_load(args.config.read_text())
    source = Path(cfg.get("source", ""))
    local = Path(cfg.get("output", "local"))
    if args.command == "audit":
        from .archive_audit import archive_audit
        from .audit import audit

        audit(source, local / "audit")
        archive_audit(source, local / "audit")
    elif args.command == "extract":
        from .data import extract

        extract(next(source.rglob("*.nc")), source / "EC_flux_tower_sites.csv", local / "data")
    elif args.command == "forensic":
        from .forensics import forensic

        forensic(source, local / "forensic")
    elif args.command == "sources":
        from .sources import retrieve

        retrieve(local / "sources")
    elif args.command == "run":
        from .experiments import run

        run(local / "data/cells.csv", local / "runs")
    elif args.command == "summarize":
        from .experiments import load_data, summarize

        summarize(local / "runs", load_data(local / "data/cells.csv"))
    elif args.command == "export":
        from .export import export

        export(source, local, Path("website/public"))
    elif args.command == "report":
        from .report import report

        report(local, Path("reports"))
    elif args.command == "evidence":
        from .evidence import evidence

        evidence(source, local, Path("reports"))


if __name__ == "__main__":
    main()
