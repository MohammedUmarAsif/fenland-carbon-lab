# Delivery validation: 12 October 2026

## Aggregate candidate follow-up

Prepared a separate 2.7 MB aggregate-results edition following the author's
research/educational access clarification. Latest pytest: **24 passed**. New
test verifies the export allowlist, omission of source series/private metadata,
unapproved candidate state and refusal to overwrite a mixed/private destination.
Ruff and both build profiles pass. The complete private site's browser checks
continue to pass.

The aggregate edition passes desktop, mobile and dark-mode axe A/AA checks,
overflow checks, query-state restoration, benchmark controls, unavailable-result
state, metric downloads, all local links and 200% equivalent layout. Package
hashes agree; prohibited daily-value fields and source-series assets are absent.
Desktop/mobile/dark screenshots were inspected, including chart axis contrast.
Lighthouse mobile simulation: **96 performance / 100 accessibility / 100 best
practices / 100 SEO**. Detailed evidence is `local/public-review/`.

The aggregate Pages workflow verifies a separately approved release scope and
the exact package before deployment. No public release has been approved or
made. The author's specific source access agreement remains unavailable; a
research-results publication design does not establish contractual permission.

## Original complete local edition

All A–F experiment stages completed: 101 primary/ablation/transfer runs and
56 rolling-selection fits. No research compute remains pending.

* `uv run pytest -q`: **23 passed**, including authentic metric regeneration,
  matched model keys, duplicate-cell and nested-transfer isolation, website
  numerical agreement and partition reconstruction. NetCDF4 emits 26 upstream
  NumPy 2.5 shape-setting deprecation warnings in synthetic fixture writes.
* `uv run ruff check .` and `uv run ruff format --check .`: passed.
* `uv run fenland-carbon-lab smoke`: passed; synthetic, separate from research.
* `npm run build`: passed. ECharts produces a 622.5 kB minified JavaScript
  bundle (209.8 kB gzip); Vite flags its size. No build failure.
* `node website/scripts/check-data.mjs`: 35 authentic run exports,
  **681,078 keyed rows**, SHA-256, partition reconstruction, component
  accounting within documented numerical rounding and test metrics verified.
* `npm run check`: passed at 1440×1000 desktop, 390×844 mobile and dark desktop.
  No failed resource requests, page exceptions, document overflow or axe
  WCAG A/AA violations. Checked control changes, training-fit labelling,
  unavailable-target state, CSV download, query-state restoration, local links,
  six spatial folds, all thesis image requests and missing-asset error state.
* Visual review: desktop/mobile overview and explorer, dark explorer and
  200% equivalent layout. Charts use distinct line/point forms, scrollable
  legends, accessible tables and downloadable values. Keyboard-focusable
  tables and code blocks support horizontal scrolling. The zoom check uses a
  720×500 effective CSS viewport, rather than claiming an actual browser zoom
  interaction. Historical reader: all seven chapters, 11 navigation entries,
  20 figures and both DOCX tables.
* Lighthouse 13.5.0, local mobile simulation: performance **91**, accessibility
  **100**, best practices **100**, SEO **100**; FCP 2.0 s, LCP 3.0 s,
  blocking time 130 ms, CLS 0. The prior run scored 92/100/100/100.
  This is a lab measurement, not live-site Core Web Vitals or a measured INP.
  LCP remains above the visual contract's 2.5 s target; further delivery/bundle
  optimisation is an explicit performance limitation.
* All **86 original physical files rehashed unchanged** after implementation.
  The source folder and unrelated iOS work were preserved.
* GitHub workflow YAML parses; CI and manual Pages workflows are prepared.
  They have not run on GitHub. Deployment requires approved redistribution
  rights and deliberately tracked assets. Public site/repository not created.

Private detailed logs, screenshots and Lighthouse JSON are in
`local/ui-review/`; source inventories, archive hashes, checkpoints and keyed
prediction CSVs remain in `local/`. Public-facing summaries are in `reports/`.
No raw NetCDF, original thesis, model binaries, private forms, source archive
contents or machine-specific data path are staged in Git. No authentic fixture
is redistributed while its data rights remain unresolved; CI's synthetic
fixture is labelled accordingly.

Scientific limits: these scores measure retrospective JULES emulation, six
nearby cells share forcing, and source crop/management/run version remain
unverified. Tower validation is therefore gated by comparability, and no JULES
simulation speedup, physical intervention or carbon-savings claim is made.
