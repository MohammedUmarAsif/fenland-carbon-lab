"""Bounded retrieval of primary bibliographic records and observational documentation."""

from __future__ import annotations

import io
import json
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

from pypdf import PdfReader

DOIS = [
    (
        "Clark et al.",
        "10.5194/gmd-4-701-2011",
        "Carbon definitions; does not identify run settings.",
    ),
    (
        "Osborne et al.",
        "10.5194/gmd-8-1139-2015",
        "Crop parameterisation; crop type here unresolved.",
    ),
    (
        "Roberts et al.",
        "10.1111/ecog.02881",
        "Blocked validation for structured data; task-specific extrapolation.",
    ),
    (
        "Evans et al.",
        "10.1038/s41586-021-03523-1",
        "Water-table motivation; rainfall is not water-table intervention.",
    ),
    (
        "Khan et al.",
        "10.1016/j.rsase.2025.101728",
        "Prior Fenland observational upscaling; not our simulator target.",
    ),
    (
        "Digital Twin study",
        "10.3390/rs17213615",
        "Operational GeoML interface precedent; no dashboard novelty claim.",
    ),
    (
        "ecLand emulator study",
        "10.5194/gmd-18-921-2025",
        "Sequence versus boosting tradeoffs in another simulator; no direct score comparison.",
    ),
    (
        "Beer et al.",
        "10.1126/science.1184984",
        "Global GPP controls; submitted Nature volume/pages are incorrect.",
    ),
    ("Best et al.", "10.5194/gmd-4-677-2011", "JULES energy/water science."),
    ("Breiman", "10.1023/A:1010933404324", "Random forest method."),
    (
        "Brenowitz and Bretherton",
        "10.1029/2018GL078510",
        "Prognostic neural parameterisation; not proof of this emulator stability.",
    ),
    (
        "Brenowitz and Bretherton 2019",
        "10.1029/2019MS001711",
        "Spatially extensive network training; separate system.",
    ),
    (
        "Clifton-Brown and Lewandowski",
        "10.1006/anbo.2000.1183",
        "Water-use efficiency of three Miscanthus genotypes; does not identify this simulation crop.",
    ),
    (
        "Heaton et al.",
        "10.1111/j.1365-2486.2008.01662.x",
        "Bioenergy crop yields; does not verify simulated crop.",
    ),
    ("Hochreiter and Schmidhuber", "10.1162/neco.1997.9.8.1735", "LSTM method."),
    ("Hoyer and Hamman", "10.5334/jors.148", "xarray data structures."),
    (
        "Lasslop et al.",
        "10.1111/j.1365-2486.2009.02041.x",
        "Flux partitioning; not independent component observations.",
    ),
    ("Rasp et al.", "10.1073/pnas.1810286115", "Climate subgrid neural parameterisation."),
    (
        "Reichstein et al. 2005",
        "10.1111/j.1365-2486.2005.001002.x",
        "NEE partitioning limitations.",
    ),
    (
        "Reichstein et al. 2019",
        "10.1038/s41586-019-0912-1",
        "Earth-system deep learning perspective.",
    ),
    ("Wilkinson et al.", "10.1038/sdata.2016.18", "FAIR principles; FAIR is not a data licence."),
]


DOIS.extend(
    [
        (
            "XGBoost",
            "10.1145/2939672.2939785",
            "Historic XGBoost method; corrected benchmark uses histogram boosting.",
        ),
        (
            "2026 flux upscaling",
            "10.5194/essd-18-7367-2026",
            "Contemporary observational LSTM upscaling, not comparable JULES target skill.",
        ),
        (
            "Prechelt",
            "10.1007/3-540-49430-8_3",
            "Validation early stopping; no protection against contaminated validation.",
        ),
    ]
)


def fetch(url, limit=20 * 1024**2):
    request = urllib.request.Request(
        url, headers={"User-Agent": "FenlandCarbonLab/0.1 research metadata audit"}
    )
    with urllib.request.urlopen(request, timeout=40) as response:
        if int(response.headers.get("Content-Length", "0")) > limit:
            raise ValueError("Download exceeds explicit byte budget")
        data = response.read(limit + 1)
        if len(data) > limit:
            raise ValueError("Download exceeds explicit byte budget")
        return data


def retrieve(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for author, doi, decision in DOIS:
        try:
            m = json.loads(
                fetch("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""))
            )["message"]
            records.append(
                {
                    "label": author,
                    "doi": doi,
                    "title": m.get("title", [""])[0],
                    "authors": [
                        a.get("given", "") + " " + a.get("family", "") for a in m.get("author", [])
                    ],
                    "year": m.get("published", {}).get("date-parts", [[None]])[0][0],
                    "journal": m.get("container-title", [""])[0],
                    "volume": m.get("volume"),
                    "pages": m.get("page"),
                    "decision": decision,
                    "verification": "Crossref publisher-deposited metadata; claim relevance bounded to primary abstracts/documentation where accessible.",
                    "checked": "2026-10-12",
                    "url": "https://doi.org/" + doi,
                }
            )
        except Exception as exc:
            records.append(
                {
                    "label": author,
                    "doi": doi,
                    "status": "retrieval failed",
                    "error": str(exc),
                    "decision": decision,
                }
            )
    (out / "bibliography.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    for uid in ["13896773-01e5-48e6-bfab-c319de46b221", "06d7c463-298c-4c7e-a4c3-55d003aa91cb"]:
        meta = json.loads(fetch(f"https://catalogue.ceh.ac.uk/documents/{uid}?format=json"))
        (out / (uid + ".json")).write_text(json.dumps(meta, indent=2), encoding="utf-8")
        for resource in meta.get("onlineResources", []):
            if resource.get("function") == "information" and resource["url"].endswith(".zip"):
                try:
                    content = fetch(resource["url"])
                    (out / (uid + "-support.zip")).write_bytes(content)
                    with zipfile.ZipFile(io.BytesIO(content)) as z:
                        members = []
                        for n in z.namelist():
                            members.append(n)
                            if n.lower().endswith(".pdf"):
                                reader = PdfReader(io.BytesIO(z.read(n)))
                                text = "\n".join(
                                    f"[PAGE {i + 1}]\n" + (p.extract_text() or "")
                                    for i, p in enumerate(reader.pages)
                                )
                                (out / (uid + "-" + Path(n).stem + ".txt")).write_text(
                                    text, encoding="utf-8"
                                )
                            elif n.lower().endswith((".txt", ".csv")):
                                (out / (uid + "-" + Path(n).name)).write_bytes(z.read(n))
                        (out / (uid + "-support-members.json")).write_text(
                            json.dumps(members, indent=2)
                        )
                except Exception as exc:
                    (out / (uid + "-support-error.txt")).write_text(str(exc))
    print("Primary records/supporting documentation retrieval finished", flush=True)
