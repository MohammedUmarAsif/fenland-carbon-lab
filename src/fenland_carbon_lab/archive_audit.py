"""Archive member fingerprints and model metadata, without executing models."""

import hashlib
import io
import json
import zipfile
from pathlib import Path

import h5py
import pandas as pd


def archive_audit(source: Path, out: Path):
    entries = []
    metadata = []

    def walk(archive, parent, depth=0):
        if depth > 4:
            raise ValueError("Unexpected deeply nested archive")
        for m in archive.infolist():
            blob = b"" if m.is_dir() else archive.read(m)
            name = parent + "::" + m.filename
            entries.append(
                {
                    "archive_member": name,
                    "bytes": m.file_size,
                    "sha256": hashlib.sha256(blob).hexdigest(),
                    "directory": m.is_dir(),
                }
            )
            if m.filename.endswith((".keras", ".zip")) and blob:
                with zipfile.ZipFile(io.BytesIO(blob)) as child:
                    walk(child, name, depth + 1)
            if m.filename.endswith(".h5") and blob:
                with h5py.File(io.BytesIO(blob), "r") as h:
                    metadata.append(
                        {
                            "source": name,
                            "attributes": {k: str(v) for k, v in h.attrs.items()},
                            "top_level_groups": list(h.keys()),
                            "inspection": "Metadata only; never Keras/pickle execution",
                        }
                    )

    for p in source.rglob("*"):
        if p.is_file() and p.suffix.lower() in [".zip", ".docx", ".pptx", ".keras"]:
            with zipfile.ZipFile(p) as z:
                walk(z, p.relative_to(source).as_posix())
    pd.DataFrame(entries).to_csv(out / "all_archive_members_hashed.csv", index=False)
    (out / "safe_h5_metadata.json").write_text(json.dumps(metadata, indent=2))
    print("Hashed archive members:", len(entries), "H5 metadata records:", len(metadata))
