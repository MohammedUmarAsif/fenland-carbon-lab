# Fenland Carbon Lab

Reproducible daily carbon-flux emulation and generalisation: a 12 October 2026
AI-assisted extension of Mohammed Umar Asif Sayed's University of Leicester
2025 MSc dissertation. The reference is JULES, not observed tower fluxes.

Read [the generated research report](reports/RESEARCH_REPORT.md),
[delivery validation](reports/VALIDATION.md),
[experiment status](reports/EXPERIMENT_STATUS.json),
[dated corrections](reports/CORRECTIONS.md), and
[the frozen protocol](reports/PROTOCOL.md). Numerical findings come from keyed
prediction artifacts and are regenerated into the website; a synthetic smoke
test is never described as a full-data experiment.

## Reproduce

Python 3.12+, uv, Node 22+. `uv.lock` and `website/package-lock.json` pin the
environment. A four-thread CPU budget and declared seeds bound the experiments.

```powershell
uv sync --locked
Copy-Item config/example.yaml config/local.yaml
# Edit local.yaml to point to your authorized Dissertation directory.
uv run fenland-carbon-lab audit
uv run fenland-carbon-lab extract
uv run fenland-carbon-lab forensic
uv run fenland-carbon-lab evidence
uv run fenland-carbon-lab sources
uv run fenland-carbon-lab run
uv run fenland-carbon-lab report
uv run fenland-carbon-lab export
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv run fenland-carbon-lab smoke
cd website
npm ci
npm run build
node scripts/check-data.mjs
npm run preview
# In another terminal with the preview server running:
npm run check
```

The raw NetCDF and site CSV are user-supplied, not downloaded from an invented
public source. Source redistribution rights are unresolved; see the data card.
The CLI never executes legacy notebook commands or loads source pickle. Cached
runs are reused only for matching config, seed, dimensions, training count and
evaluation keys. For a numerical-method change, use a fresh output directory;
cache reuse is a resumption facility, not automatic code-version invalidation.

Browser checks need a Playwright Chromium installation (`npx playwright install chromium`),
or an existing executable supplied using `BROWSER_EXECUTABLE`.

`audit` creates a private source inventory/extracted text/metadata bundle.
`extract` reads single native-cell slabs, preserves raw and standardized units,
and logs site distance/grouping. `run` writes each completed checkpoint and
keyed CSV/JSON. `sources` retrieves primary bibliographic records and bounded
observational supporting documents. `export` writes authentic compact assets
and a sanitized historical reading edition, locally only.

`local/` and `website/public/` are ignored pending data/content rights. The
generated report and status are tracked methodology/results summaries; they do
not license source data. Tests without access to private outputs skip authentic
artifact checks explicitly; they still validate scientific failure modes and a
synthetic end-to-end workflow. Training fits are distinguished from held-out
predictions on the site. Only eligible complete months receive monthly scores.

## Scientific boundaries

Current daily weather is known after the daily interval, so the primary task is
retrospective same-interval emulation. Seven labels map to six simulated cells,
including duplicate Redmere labels. No diurnal dynamics can be learned from
daily means. Spatial and joint future/cell transfer are distinct tasks with
nested group isolation. Simulator-state ablations require state at inference.
Component accounting is an identity, not a full conservation constraint or PINN.
Residual intervals quantify agreement with JULES; nature-relative uncertainty
is unmeasured. No causal management recommendations, carbon savings or JULES
simulation speedup are claimed.

The original dissertation is unchanged. The website's locally generated reading
edition omits administrative front matter and personal acknowledgements; source
text and claims remain historical and are accompanied by dated corrections.
The final cover verifies an MSc; the exact course title is not independently
confirmed by the available final document.

## Delivery and publication

There is no public repository or live Pages URL yet. Local preview uses the
URL printed by `npm run preview`. CI checks Python and the static build; the
manual Pages workflow requires a reviewed rights record and approved assets.
See [publication requirements](reports/PUBLICATION.md) for the concrete gate,
[contribution and interview walkthrough](reports/INTERVIEW.md),
[claim ledger](reports/CLAIM_LEDGER.csv), and
[experiment lineage](reports/EXPERIMENT_LINEAGE.csv).

MIT applies to newly written code/methods documentation, not the thesis or data.
Supervisor/data-provider/JULES community and AI contributions are distinguished
in the report and site. Cite the extension using CITATION.cff, separately from
the 2025 thesis.
