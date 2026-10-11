"""Read the revised PDF and retrieve three explicitly licensed contextual assets."""

import hashlib
import io
import json
import logging
import re
import urllib.request
from pathlib import Path

from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
PDF = Path(r"C:\Users\sayed\OneDrive\Desktop\Docs\diss\249045803_GY7720_Dissertation.pdf")
logging.getLogger("pypdf").setLevel(logging.ERROR)
reader = PdfReader(PDF)
pages = [p.extract_text() for p in reader.pages]
private = ROOT / "local/updated-pdf-review"
private.mkdir(exist_ok=True)
(private / "extraction.txt").write_text("\n\n".join(pages), encoding="utf-8")
claims = [
    {
        "topic": "Document identity",
        "pages": "1",
        "status": "reproduced",
        "reported": "Revised meteorology-driven component surrogate dissertation, cover 2026",
        "evidence": "PDF cover inspected; distinct from earlier 2025 materials.",
    },
    {
        "topic": "NEE headline scores",
        "pages": "2, 28",
        "status": "contradicted",
        "reported": "Abstract NEE R² approximately 0.76; Table 2 gives 0.804",
        "evidence": "Internal inconsistency. These reported scores are not adopted as current verified results.",
    },
    {
        "topic": "History window",
        "pages": "25, 44",
        "status": "contradicted",
        "reported": "Methods 24 daily steps; appendix config window=30",
        "evidence": "Document text/config conflict; appendix execution lineage unresolved.",
    },
    {
        "topic": "Baseline information",
        "pages": "26, 47",
        "status": "unresolved",
        "reported": "Methods same-window engineered summaries; appendix comment last-step snapshots",
        "evidence": "Supporting original baseline module/execution lineage required. Current benchmark gives all daily lags to tabular models.",
    },
    {
        "topic": "Units",
        "pages": "25, 44, 46",
        "status": "contradicted",
        "reported": "Methods no conversion, kg units; appendix includes carbon-to-micromole conversion",
        "evidence": "Document/appendix inconsistency. Current source metadata and exact 12.0107 carbon mass conversion audited.",
    },
    {
        "topic": "Chronological split and scaling",
        "pages": "25",
        "status": "reported",
        "reported": "70/15/15 chronology and train-only scaling",
        "evidence": "Narrative inspected; original executed artifacts do not establish this revised claim. Current pipeline verifies explicit year partitions and training-only fitting.",
    },
    {
        "topic": "Carbon accounting",
        "pages": "10, 24, 28",
        "status": "reproduced",
        "reported": "NEE = plant respiration + soil respiration minus uptake",
        "evidence": "Identity explicitly implemented and tested in current pipeline; not proof of all historical execution.",
    },
    {
        "topic": "Monthly results",
        "pages": "30, 49",
        "status": "unresolved",
        "reported": "Monthly improvements; appendix calls approximate index bins",
        "evidence": "Historical timestamp lineage unresolved. Current analysis uses exact calendar months and excludes incomplete months.",
    },
    {
        "topic": "Miscanthus and simulator configuration",
        "pages": "1, 24",
        "status": "unresolved",
        "reported": "Miscanthus-parameterised JULES-Crop",
        "evidence": "Retained as dissertation-described setting; source run/version/crop and management configuration not established by available NetCDF metadata.",
    },
    {
        "topic": "Observational accuracy and speedup",
        "pages": "2, 37, 38",
        "status": "unresolved",
        "reported": "Simulator fidelity, with potential acceleration and future diagnostics",
        "evidence": "No aligned observational validation or paired JULES runtime benchmark; no current field-accuracy or speedup claim.",
    },
]
audit = {
    "source_sha256": hashlib.sha256(PDF.read_bytes()).hexdigest(),
    "pages": len(pages),
    "cover_year": 2026,
    "title": "Meteorology Driven LSTM Surrogates for Emulating JULES-Crop Carbon Flux Components in Miscanthus Simulations",
    "claims": claims,
    "status_meaning": "Reproduced refers to the identified document fact or current implementation; never implies reproduction of all revised dissertation scores.",
}
(ROOT / "reports/REVISED_DISSERTATION_AUDIT.json").write_text(
    json.dumps(audit, indent=2), encoding="utf-8"
)
lines = [
    "# Revised dissertation reconciliation",
    "",
    f"Source SHA-256: `{audit['source_sha256']}`. 50 pages; cover 2026.",
    "",
    audit["title"],
    "",
    audit["status_meaning"],
    "",
    "| Topic | PDF pages | Status | Reported | Evidence |",
    "|---|---|---|---|---|",
]
lines += [
    f"| {c['topic']} | {c['pages']} | {c['status']} | {c['reported']} | {c['evidence']} |"
    for c in claims
]
lines += [
    "",
    "Acknowledgements (page 3): Professor Heiko Balzter, supervision and scientific standards; Dr Asima Khan, data preparation and component accounting guidance; Dr Muhammad Ali, technical guidance on native geometry and clean splits. These are author acknowledgements, not endorsement of the later extension.",
    "",
    "Original PDF is preserved privately. No original PDF text, figure or administrative content is redistributed. New explanations and this factual reconciliation are authored for the extension.",
]
(ROOT / "reports/REVISED_DISSERTATION_AUDIT.md").write_text(
    "\n".join(lines) + "\n", encoding="utf-8"
)


def retrieve(url):
    request = urllib.request.Request(
        url, headers={"User-Agent": "FenlandCarbonLab/1.0 (educational research portfolio)"}
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


assets = [
    {
        "file": "fen-landscape.jpg",
        "creator": "Ashley Dace",
        "title": "Fen Landscape",
        "source": "https://commons.wikimedia.org/wiki/File:Fen_Landscape_-_geograph.org.uk_-_2445197.jpg",
        "licence": "CC BY-SA 2.0",
        "licence_url": "https://creativecommons.org/licenses/by-sa/2.0/",
        "alt": "Open agricultural Fenland landscape near Wicken, photographed in 2011.",
    },
    {
        "file": "fen-soil.jpg",
        "creator": "N Chadwick",
        "title": "Dark fenland soil",
        "source": "https://commons.wikimedia.org/wiki/File:Dark_fenland_soil_-_geograph.org.uk_-_4322530.jpg",
        "licence": "CC BY-SA 2.0",
        "licence_url": "https://creativecommons.org/licenses/by-sa/2.0/",
        "alt": "Dark soil in an agricultural field near Wicken, photographed in 2014.",
    },
    {
        "file": "england-peat-map.png",
        "creator": "Natural England",
        "title": "England Peat Map: peat depth",
        "source": "https://naturalengland.blog.gov.uk/2025/05/12/a-new-peat-map-for-england/",
        "licence": "Open Government Licence v3.0",
        "licence_url": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "licence_evidence": "https://publications.naturalengland.org.uk/publication/5075614867128320",
        "alt": "Natural England's national peat-depth map, with a displayed regional detail for East Anglia.",
    },
]
media = ROOT / "local/story-media"
media.mkdir(exist_ok=True)
for asset in assets:
    path = media / asset["file"]
    if not path.exists():
        html = retrieve(asset["source"]).decode("utf-8")
        if asset["file"].endswith(".jpg"):
            urls = re.findall(r'href="(https://upload.wikimedia.org/[^"?]+\.jpg)(?:[^"]*)"', html)
            url = next(u for u in urls if "/thumb/" not in u)
        else:
            url = "https://naturalengland.blog.gov.uk/wp-content/uploads/sites/183/2025/05/The-England-Peat-Map.-Peat-depth-across-England-c-Natural-England-620x770.png"
        content = retrieve(url)
        Image.open(io.BytesIO(content)).verify()
        path.write_bytes(content)
    image = Image.open(path)
    asset.update(
        {
            "width": image.width,
            "height": image.height,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "changes": "Original bytes retained. Responsive CSS display crops the opening landscape photograph; photograph adaptations remain CC BY-SA 2.0. Map also shown as a labelled CSS regional crop; full map and source accessible.",
            "attribution": f"{asset['title']} by {asset['creator']}; {asset['licence']}.",
            "retrieved": "2026-10-12",
        }
    )
(ROOT / "reports/ASSET_REGISTER.json").write_text(json.dumps(assets, indent=2), encoding="utf-8")
print("Revised PDF audited and preserved:", audit["source_sha256"])
print("Licensed media:", [(a["file"], a["width"], a["height"]) for a in assets])
