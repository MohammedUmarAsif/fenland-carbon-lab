"""Single-source website assets and a locally readable historical dissertation."""

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from docx import Document

from .data import COMPONENTS, nee, samples
from .experiments import Sequence, load_data


def records(path):
    return json.loads(pd.read_csv(path).to_json(orient="records"))


def training_predictions(x, y, m, r, out):
    tr = m.split.eq("train").to_numpy()
    z = ((x[tr] - np.array(r["feature_mean"])) / np.array(r["feature_scale"])).astype(np.float32)
    rid = r["run_id"]
    kind = r["model"]
    if kind == "climatology":
        month = pd.to_datetime(m.start[tr]).dt.month.to_numpy()
        monthly_means = {v: y[tr][month == v].mean(axis=0) for v in np.unique(month)}
        p = np.array([monthly_means[v] for v in month])
    elif kind == "lstm":
        own = torch.load(out / (rid + ".pt"), map_location="cpu", weights_only=True)
        model = Sequence(own["inputs"], own["outputs"])
        model.load_state_dict(own["state_dict"])
        model.eval()
        with torch.no_grad():
            p = np.concatenate([model(b).numpy() for b in torch.from_numpy(z).split(512)])
        p = p * np.array(r["target_scale"]) + np.array(r["target_mean"])
    else:
        import joblib

        own = joblib.load(
            out / (rid + ".joblib")
        )  # Only artifacts produced locally by this package.
        p = own["sy"].inverse_transform(
            np.asarray(own["model"].predict(z.reshape(len(z), -1))).reshape(len(z), -1)
        )
    f = m.loc[tr].copy()
    for j, c in enumerate(COMPONENTS):
        f[c + "_true"] = y[tr, j]
        if not r["direct"]:
            f[c + "_pred"] = p[:, j]
    f["nee_true"] = nee(y[tr])
    f["nee_pred"] = p[:, 0] if r["direct"] else nee(p)
    return f


def dissertation(source, public):
    dest = public / "thesis"
    dest.mkdir(parents=True, exist_ok=True)
    doc = Document(next(source.glob("*_GY7720_Dissertation.docx")))
    # Exact source paragraphs preserved; front administrative and personal acknowledgements excluded.
    body = []
    chapters = []
    started = False
    code = False
    namespace = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    }
    source_image = 0
    for child in doc.element.body:
        text = "".join(n.text or "" for n in child.findall(".//w:t", namespace))
        text = re.sub(r"\b\d{9}\b", "[identifier removed]", text)
        if text.strip() == "Abstract":
            started = True
        if text.strip() == "Acknowledgements":
            started = False
        if text.strip() in [
            "Abbreviations",
            "List of Abbreviations",
            "List of Figures",
            "Table of Abbreviations",
            "Table of Contents",
            "Contents",
        ]:
            started = True
        if re.match(r"^(1\.?\s+)?Introduction", text.strip()):
            started = True
        if not started:
            continue
        heading = child.find(".//w:pStyle", namespace) is not None and "Heading" in str(
            child.find(".//w:pStyle", namespace).attrib
        )
        chapter = re.match(
            r"^[1-7]\.\s+(Introduction|Background|Data and Study Area|Methods|Results|Discussion|Conclusions?)\s*$",
            text.strip(),
        )
        if text.strip() in ["Abstract", "References", "Appendix", "Code"] or heading or chapter:
            ident = "chapter-" + str(len(chapters))
            chapters.append({"title": text.strip(), "id": ident})
            body.append(f'<h2 id="{ident}">{html.escape(text)}</h2>')
            if text.strip() == "Code":
                code = True
        elif child.tag.endswith("}tbl"):
            rows = []
            for row in child.findall("./w:tr", namespace):
                cells = []
                for cell in row.findall("./w:tc", namespace):
                    paragraphs = [
                        "".join(n.text or "" for n in p.findall(".//w:t", namespace))
                        for p in cell.findall("./w:p", namespace)
                    ]
                    cells.append("<td>" + "<br>".join(html.escape(p) for p in paragraphs) + "</td>")
                rows.append("<tr>" + "".join(cells) + "</tr>")
            body.append(
                '<div style="overflow:auto"><table border="1">' + "".join(rows) + "</table></div>"
            )
        elif not code and re.match(r"^[1-7]\.\d+(?:\.\d+)?\s+", text.strip()):
            body.append("<h3>" + html.escape(text) + "</h3>")
        elif text.strip():
            body.append(
                ("<pre>" if code else "<p>") + html.escape(text) + ("</pre>" if code else "</p>")
            )
        math = " ".join(n.text or "" for n in child.findall(".//m:t", namespace))
        if math:
            body.append('<p class="equation">' + html.escape(math) + "</p>")
        for node in child.findall(".//a:blip", namespace):
            rel = node.attrib.get(
                "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
            )
            if rel and rel in doc.part.related_parts:
                part = doc.part.related_parts[rel]
                extension = part.partname.split(".")[-1]
                name = f"figure-{source_image}.{extension}"
                source_image += 1
                (dest / name).write_bytes(part.blob)
                body.append(
                    f'<figure><img src="{name}" alt="Historical dissertation figure {source_image}; source claims may require correction" loading="lazy"><figcaption>Historical submitted figure {source_image}, preserved from DOCX.</figcaption></figure>'
                )
    nav = "".join(
        f'<a href="#{c["id"]}">{html.escape(c["title"])}</a>' for c in chapters if c["title"]
    )
    (dest / "index.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Submitted dissertation, historical reading edition</title><style>body{max-width:850px;margin:auto;padding:24px;font:18px/1.7 Georgia;color:#222;background:#faf9f5}nav{display:flex;gap:16px;flex-wrap:wrap}img{max-width:100%;height:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.6 monospace}h2{scroll-margin:24px}a{color:#245b49}.note{background:#e6eee7;padding:20px}figcaption{font:14px system-ui}p{overflow-wrap:anywhere}</style><body><a href="../..">Return to Fenland Carbon Lab</a><h1>Submitted dissertation</h1><p class="note">Historical reading edition of the 2025 DOCX. Published claims are preserved as historical statements. See the 12 October 2026 corrections and extension on the main site. Administrative front matter and personal acknowledgements omitted. Student identifier removed. Images and equations extracted; Word pagination and formatting are not preserved. Local preview only: publication rights unresolved.</p><nav>'
        + nav
        + "</nav>"
        + "".join(body)
        + "</body></html>",
        encoding="utf-8",
    )
    return {
        "chapters": len(chapters),
        "figures": source_image,
        "status": "Local sanitized reading edition; permission unresolved",
    }


def export(source: Path, local: Path, public: Path):
    public.mkdir(parents=True, exist_ok=True)
    assets = public / "assets-data"
    assets.mkdir(exist_ok=True)
    out = local / "runs"
    registry = json.loads((out / "registry.json").read_text())
    selected = json.loads((out / "selected.json").read_text())
    data = load_data(local / "data/cells.csv")
    main = [
        r
        for r in registry
        if r["seed"] == 17
        and (r["run_id"].startswith(("weather-", "direct-", "spatial-", "joint-")))
    ]
    all_columns = (
        ["key", "cell", "start", "end", "split"]
        + [c + suffix for c in COMPONENTS + ["nee"] for suffix in ["_true", "_pred"]]
        + ["nee_lo95", "nee_hi95"]
    )
    sources = []
    for r in main:
        rid = r["run_id"]
        f = pd.read_csv(out / (rid + ".csv"), parse_dates=["start", "end"])
        if rid.startswith(("weather-", "direct-")):
            x, y, m = samples(data, r["length_days"])
            train = training_predictions(x, y, m, r, out)
            f = pd.concat([train, f], ignore_index=True)
        if rid == selected["run_id"]:
            bounds = pd.read_csv(out / "selected_test_intervals.csv")[
                ["key", "nee_lo95", "nee_hi95"]
            ]
            f = f.merge(bounds, on="key", how="left", validate="one_to_one")
        else:
            f["nee_lo95"] = np.nan
            f["nee_hi95"] = np.nan
        for c in all_columns:
            if c not in f:
                f[c] = np.nan
        for c in ["start", "end"]:
            f[c] = pd.to_datetime(f[c]).dt.strftime("%Y-%m-%d")
        f[all_columns].to_json(assets / (rid + ".json"), orient="values", double_precision=6)
        partitions = {}
        for (cell, split), group in f.groupby(["cell", "split"]):
            name = f"{rid}-{cell}-{split}.json"
            group[all_columns].to_json(assets / name, orient="values", double_precision=6)
            partitions[f"{cell}|{split}"] = "assets-data/" + name
        sources.append(
            {
                "run_id": rid,
                "path": "assets-data/" + rid + ".json",
                "rows": len(f),
                "partitions": partitions,
                "sha256": hashlib.sha256((assets / (rid + ".json")).read_bytes()).hexdigest(),
            }
        )
    summary = {
        "generated": "2026-10-12",
        "columns": all_columns,
        "selected": selected,
        "metrics": records(out / "metrics.csv"),
        "coverage": [r for r in records(out / "coverage.csv") if r["run_id"] == selected["run_id"]],
        "diagnostics": [
            r for r in records(out / "diagnostics.csv") if r["run_id"] == selected["run_id"]
        ],
        "mapping": records(local / "data/mapping.csv"),
        "qc": json.loads((local / "data/qc.json").read_text()),
        "runs": registry,
        "assets": sources,
        "paired": json.loads((out / "paired_comparisons.json").read_text()),
        "covariance": json.loads((out / "component_covariance.json").read_text()),
        "historical": json.loads((local / "forensic/historical_checks.json").read_text()),
        "bibliography": json.loads((local / "sources/bibliography.json").read_text()),
        "dissertation": dissertation(source, public),
        "publication": "Local preview. Raw simulator and dissertation rights unresolved.",
    }
    (public / "research.json").write_text(json.dumps(summary, ensure_ascii=False), encoding="utf-8")
    (public / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
    for file in [
        "metrics.csv",
        "coverage.csv",
        "diagnostics.csv",
        "selected_monthly.csv",
        "selected_monthly_metrics.json",
        "paired_comparisons.json",
    ]:
        shutil.copyfile(out / file, public / file)
    for p in Path("reports").iterdir():
        if p.suffix in {".md", ".json", ".csv"}:
            shutil.copyfile(p, public / p.name)
    (local / "website_asset_manifest.json").write_text(json.dumps(sources, indent=2))
    print(
        f"Exported {len(sources)} authentic run assets; thesis {summary['dissertation']}",
        flush=True,
    )
