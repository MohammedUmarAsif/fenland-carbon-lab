"""Read-only source inventory and safe artifact inspection."""

from __future__ import annotations

import hashlib
import io
import json
import zipfile
from pathlib import Path

import h5py
import netCDF4 as nc
import numpy as np
import pandas as pd
from docx import Document
from pypdf import PdfReader


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b""):
            h.update(block)
    return h.hexdigest()


def audit(source: Path, output: Path):
    output.mkdir(parents=True, exist_ok=True)
    rows, members, docs = [], [], {}
    for p in sorted(source.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(source).as_posix()
        rows.append(
            {
                "path": rel,
                "bytes": p.stat().st_size,
                "sha256": digest(p),
                "private": "supervis" in rel.lower() or "form" in rel.lower(),
            }
        )
        if p.suffix.lower() == ".zip":
            with zipfile.ZipFile(p) as z:
                for m in z.infolist():
                    members.append(
                        {
                            "archive": rel,
                            "path": m.filename,
                            "bytes": m.file_size,
                            "crc32": m.CRC,
                            "directory": m.is_dir(),
                        }
                    )
        elif p.suffix.lower() == ".docx":
            doc = Document(p)
            docs[rel] = "\n".join(x.text for x in doc.paragraphs)
            (output / (p.stem + ".txt")).write_text(docs[rel], encoding="utf-8")
        elif p.suffix.lower() == ".pdf":
            try:
                pages = PdfReader(p).pages
                text = "\n".join(
                    f"\n[PAGE {i + 1}]\n" + (x.extract_text() or "") for i, x in enumerate(pages)
                )
                (output / (p.stem + ".txt")).write_text(text, encoding="utf-8")
            except Exception as e:
                (output / (p.stem + ".error.txt")).write_text(str(e), encoding="utf-8")
        elif p.suffix.lower() == ".pptx":
            import xml.etree.ElementTree as ET

            with zipfile.ZipFile(p) as z:
                slides = [
                    n
                    for n in z.namelist()
                    if n.startswith("ppt/slides/slide") and n.endswith(".xml")
                ]
                text = "\n".join(" ".join(ET.fromstring(z.read(n)).itertext()) for n in slides)
                (output / (p.stem + ".txt")).write_text(text, encoding="utf-8")
    pd.DataFrame(rows).to_csv(output / "inventory.csv", index=False)
    pd.DataFrame(members).to_csv(output / "archive_members.csv", index=False)
    raw = next(source.rglob("*.nc"))
    with nc.Dataset(raw) as ds:
        metadata = {
            "bytes": raw.stat().st_size,
            "dimensions": {k: len(v) for k, v in ds.dimensions.items()},
            "global": {k: str(ds.getncattr(k)) for k in ds.ncattrs()},
            "variables": {
                k: {
                    "dimensions": v.dimensions,
                    "shape": v.shape,
                    "attributes": {a: str(v.getncattr(a)) for a in v.ncattrs()},
                }
                for k, v in ds.variables.items()
            },
        }
        t = ds["time"]
        metadata["time_first_last"] = [
            str(x)
            for x in nc.num2date(t[[0, -1]], t.units, calendar=getattr(t, "calendar", "standard"))
        ]
        metadata["time_differences"] = np.unique(np.diff(t[:])).tolist()
        if hasattr(t, "bounds"):
            metadata["bounds_first_last"] = ds[t.bounds][[0, -1]].tolist()
    (output / "netcdf_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    august = next(source.glob("*20250827*.zip"))
    with zipfile.ZipFile(august) as z:
        text_names = [n for n in z.namelist() if n.endswith((".json", ".csv", ".txt", ".py"))]
        (output / "august_text_members.json").write_text(json.dumps(text_names, indent=2))
        for n in text_names:
            if any(
                s in n
                for s in [
                    "model_config",
                    "scaler",
                    "predictions_test",
                    "uncertainty_test",
                    "metrics_by_site",
                ]
            ):
                dest = output / "august" / Path(n).name
                dest.parent.mkdir(exist_ok=True)
                dest.write_bytes(z.read(n))
        for n in z.namelist():
            if n.endswith(".h5"):
                try:
                    with h5py.File(io.BytesIO(z.read(n)), "r") as h:
                        attrs = {k: str(v) for k, v in h.attrs.items()}
                        (output / (Path(n).stem + "_metadata.json")).write_text(
                            json.dumps(attrs, indent=2)
                        )
                except Exception:
                    pass
    print(
        json.dumps(
            {"files": len(rows), "members": len(members), "dimensions": metadata["dimensions"]}
        )
    )
