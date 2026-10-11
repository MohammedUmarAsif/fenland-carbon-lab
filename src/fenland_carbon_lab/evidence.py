"""Generate lineage, claim ledger and safe media/duplicate classifications."""

from __future__ import annotations

import io
import math
import zipfile
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw


def evidence(source: Path, local: Path, reports: Path):
    reports.mkdir(exist_ok=True)
    inventory = pd.read_csv(local / "audit/inventory.csv")
    duplicates = inventory[inventory.sha256.duplicated(keep=False)].copy()
    duplicates.to_csv(local / "audit/physical_duplicates.csv", index=False)
    family = []
    for _, r in inventory.iterrows():
        path = r.path.lower()
        kind = (
            "private administrative"
            if r["private"]
            else "raw input"
            if path.endswith(".nc")
            else "submitted historical"
            if "_gy7720_dissertation." in path
            else "legacy code"
            if path.endswith(".py")
            else "archive"
            if path.endswith(".zip")
            else "draft/context"
            if path.endswith((".docx", ".pdf"))
            else "media"
            if path.endswith((".png", ".mp4"))
            else "result artifact"
        )
        family.append(
            {**r.to_dict(), "family": kind, "duplicate_sha": r.sha256 in set(duplicates.sha256)}
        )
    pd.DataFrame(family).to_csv(local / "audit/classified_inventory.csv", index=False)
    media = []
    thumbnails = []

    def inspect(name, blob):
        if name.endswith(".mp4"):
            media.append(
                {
                    "path": name,
                    "bytes": len(blob),
                    "status": "No usable media payload (tiny container)"
                    if len(blob) < 1024
                    else "Not published; playback not certified",
                }
            )
        if name.endswith(".png"):
            try:
                image = Image.open(io.BytesIO(blob)).convert("RGB")
                w, h = image.size
                image.thumbnail((155, 110))
                canvas = Image.new("RGB", (180, 140), "#ffffff")
                canvas.paste(image, ((180 - image.width) // 2, 0))
                ImageDraw.Draw(canvas).text((3, 114), Path(name).name[:26], fill="#222222")
                thumbnails.append(canvas)
                media.append(
                    {
                        "path": name,
                        "bytes": len(blob),
                        "width": w,
                        "height": h,
                        "status": "Decoded; historical content requires interpretation",
                    }
                )
            except Exception as exc:
                media.append({"path": name, "status": "Decode failure", "error": str(exc)})

    for p in source.rglob("*"):
        if p.is_file() and p.suffix in [".png", ".mp4"]:
            inspect(p.relative_to(source).as_posix(), p.read_bytes())
        elif p.is_file() and p.suffix == ".zip":
            with zipfile.ZipFile(p) as z:
                for m in z.infolist():
                    if m.filename.endswith((".png", ".mp4")):
                        inspect(p.name + "::" + m.filename, z.read(m))
    for sheet in range(math.ceil(len(thumbnails) / 60)):
        subset = thumbnails[sheet * 60 : (sheet + 1) * 60]
        canvas = Image.new("RGB", (1800, 140 * math.ceil(len(subset) / 10)), "#dedede")
        for i, tile in enumerate(subset):
            canvas.paste(tile, ((i % 10) * 180, (i // 10) * 140))
        canvas.save(local / "audit" / f"media-contact-{sheet}.png")
    pd.DataFrame(media).to_csv(local / "audit/media_audit.csv", index=False)
    lineage = [
        {
            "run_id": "submitted-2025",
            "code": "Submitted appendix pp. 34 onward; extracted verbatim, never executed",
            "input": "Native nearest-cell component/weather extraction described; prediction artifact missing",
            "split": "Printed site-sorted positional 70/15/15; executed lineage unresolved",
            "scaler": "Printed full combined fit",
            "target": "GPP/Rp/Rs; identity NEE",
            "window": "24 preceding daily steps, excludes target row; horizon default 0",
            "seed": "Config/code, not tied to recovered run",
            "units": "Raw kg apparent, printed μmol labels unverified",
            "status": "historical report; not reproduced",
        },
        {
            "run_id": "july-colab",
            "code": "Standalone Colab export; magics not executed",
            "input": "Spatial averages; includes flux predictors",
            "split": "Legacy chronological slices after preprocessing",
            "scaler": "Full-data fit before splitting in export",
            "target": "Direct NEE",
            "window": "20 steps in legacy export; July archives may differ",
            "seed": "No proven link across files",
            "units": "Inspect historic code; no reuse as corrected units",
            "status": "Separate legacy experiment",
        },
        {
            "run_id": "august-20250827",
            "code": "Training code unavailable; JSON config and Keras config safely inspected",
            "input": "gpp,ra,rh,tair,sw,pr,wind",
            "split": "Paired test arrays; chronological/site alignment not proven",
            "scaler": "Full scaled table has zero means; stored target stats; train-only origin unproven",
            "target": "Direct alternate-sign NEE_umol",
            "window": "L=34,H=1 metadata; flux timing unresolved",
            "seed": "42 in configuration",
            "units": "Historic 1e9/12, opposite atmospheric sign",
            "status": "Saved RMSE/MAE/R² and uncertainty reproduced, not corrected retraining",
        },
        {
            "run_id": "corrected-20261012",
            "code": "New package data.py/experiments.py; frozen protocol",
            "input": "Six native cells; weather-only primary, state/weather ablations separated",
            "split": "Global 2006-14 train/2015 validation/2016 calibration/2017-19 evaluation; nested grouped transfer",
            "scaler": "Eligible training windows and targets only",
            "target": "Three carbon components / direct atmospheric NEE",
            "window": "1/7/24/60 days, includes current weather; common60 eligibility",
            "seed": "17/29/43",
            "units": "kg C→μmol with 12.0107; budget exact interval durations",
            "status": "See per-run registry; completion asserted only for actual artifacts",
        },
    ]
    pd.DataFrame(lineage).to_csv(reports / "EXPERIMENT_LINEAGE.csv", index=False)
    claims = [
        (
            "Daily interval geometry",
            "NetCDF time/time_bnds/latitude/longitude",
            "Metadata and bounded coordinate reads",
            "reproduced artifact",
            "Daily end-labelled paired native coordinates",
            "24 steps are 24 days; mesh topology is not established",
        ),
        (
            "Train-only historic scaling",
            "Submitted appendix pp.41-42",
            "Code inspection and positional-slice demonstration",
            "historical report",
            "Full fit and site-sorted slices differ from prose",
            "Printed implementation does not prove leakage-safe submitted metrics",
        ),
        (
            "Historic nowcast",
            "Appendix Xs[i-window:i]",
            "Index reasoning versus explicit alignment tests",
            "historical report",
            "Weather ends before target row",
            "New task explicitly includes current interval weather",
        ),
        (
            "LSTM universally best",
            "August saved test CSVs",
            "Metric recomputation",
            "reproduced artifact",
            "RF lower RMSE in this different direct-NEE experiment",
            "No universal model superiority claim",
        ),
        (
            "Reliable historic uncertainty",
            "uncertainty_test.csv and scaler JSON",
            "Scale-only spread transformation and coverage calculation",
            "reproduced artifact",
            "Repaired bounds still under-cover",
            "Historic intervals are not calibrated",
        ),
        (
            "Seven independent sites",
            "Site CSV, raw nearest cells, August exports",
            "Geodesic match and exact equality checks",
            "reproduced artifact",
            "Redmere labels share a native cell",
            "Seven labels describe six simulated cells",
        ),
        (
            "Atmospheric sign",
            "August all_sites_timeseries.csv",
            "35,791-row identity residual",
            "reproduced artifact",
            "Historic sign opposite",
            "Positive=new release; historic alternate sign labelled",
        ),
        (
            "Physical carbon units",
            "Raw variables and JULES docs",
            "Metadata and atomic mass tests",
            "newly validated result",
            "Convert numeric values, retain raw",
            "Component fluxes standardized as carbon with declared mass constant",
        ),
        (
            "Exact course title",
            "Final cover and July draft",
            "Document text comparison",
            "unresolved",
            "Final cover says Master of Science; draft names Satellite Data Science",
            "University of Leicester MSc dissertation (2025)",
        ),
        (
            "Crop/management and run version",
            "cpft and global NetCDF metadata",
            "Search inventory/metadata; no namelist recovered",
            "unresolved",
            "cpft=1 insufficient",
            "Scenario-specific crop/management comparability unverified",
        ),
        (
            "Wicken peat depth",
            "EC_flux_tower_sites.csv",
            "Original value inspection",
            "unresolved",
            "4-Feb retained; verified replacement not found",
            "Peat depth omitted from predictors and interpretation",
        ),
        (
            "Regional generalisation",
            "Six cells and forcing correlation tables",
            "Grouped held-cell tests and nested tuning",
            "newly validated result",
            "Limited native-cell transfer task",
            "Transfer evidence is bounded to these nearby simulated cells",
        ),
        (
            "Observational validation",
            "EIDC supporting RTF/CSV records",
            "Coordinates/management/QA/overlap assessment",
            "unresolved",
            "Configuration mismatch gate",
            "No direct tower validation score is reported",
        ),
        (
            "JULES speedup/carbon savings",
            "No comparable run timing/interventions",
            "Evidence absence",
            "unresolved",
            "Only local inference measured",
            "No acceleration over JULES or avoided emissions claim",
        ),
        (
            "Original work versus extension",
            "2025 dissertation, 2026 code registry",
            "Dated provenance and contribution notes",
            "newly validated result",
            "AI-assisted extension distinct",
            "Do not date later experiments to the MSc",
        ),
    ]
    pd.DataFrame(
        claims,
        columns=[
            "claim",
            "source_locator",
            "verification_method",
            "status",
            "correction",
            "allowed_public_wording",
        ],
    ).to_csv(reports / "CLAIM_LEDGER.csv", index=False)
    (reports / "APPENDIX_RECOVERY.md").write_text(
        "# Appendix recovery and repair record\n\nDOCX paragraph text extracted verbatim to an ignored local text file. PDF text independently confirms scaler/window/split statements at pp. 41-42. Extraction is not executed: notebook magics, machine-specific paths and unsafe legacy deserialization are excluded. The reusable implementation is a new auditable rewrite, not a claim that extracted code reproduces submitted predictions. Repairs cover bound-based time labels, kg C numeric conversion, atmospheric sign, geodesic native-cell selection, shared-cell grouping, explicit horizon and current-weather alignment, global calendar/group splits and train-only transforms. Tests exercise these corrections. Matching submitted prediction artifacts remain missing.\n",
        encoding="utf-8",
    )
    print(
        f"Classified {len(inventory)} files, {len(media)} media entries; {len(duplicates)} physical duplicate entries."
    )
