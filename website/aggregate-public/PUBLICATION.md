# Publication readiness and rights

## Recorded scoped release approval

On 12 October 2026, Mohammed Umar Asif Sayed explicitly approved publication of
the reviewed **aggregate-results edition** in this conversation. The exact
scope and author approval are recorded in `config/public-release.json`.
This approval does not grant a licence to redistribute the underlying data,
daily series, weights, scaler statistics or historical dissertation materials.
Those remain outside this release. The original access agreement was not
provided or independently verified; its terms remain applicable.

## Aggregate research-results alternative, prepared 12 October 2026

The author reports that the source data were provided for research and educational
use; no exact agreement or public redistribution licence has been supplied.
That statement is recorded as an access assertion, not converted into a new licence.

New research findings and statistical facts are different from reproducing the
source dataset. Copyright does not automatically protect every numerical fact
or model prediction. A source agreement can nevertheless impose additional
publication or confidentiality terms; these remain unknown here. See
[UK guidance on facts and copyright](https://www.gov.uk/government/publications/knowledge-asset-management-in-government/knowledge-assets-classes-and-types-annex-a)
and [research/private-study exceptions](https://www.gov.uk/guidance/exceptions-to-copyright).
This is a scoped release design, not a guarantee that all access agreements permit it.

The recommended public candidate shares newly written code, methods, aggregate
evaluation statistics, newly rendered benchmark charts, citations, corrections
and contribution credit. It includes no raw NetCDF/CSV, daily simulator reference
or prediction rows, weather/state series, trained weights, fitted scaler
statistics, original dissertation text/figures/PDF or administrative documents.
The full local research site and reading edition remain available separately.

Build and inspect this candidate:

```powershell
uv run fenland-carbon-lab export-public
cd website
npm run build -- --mode aggregate
npm run preview -- --mode aggregate --port 4174
# Another terminal, from website:
node scripts/check-public.mjs
```

The source allowlist is `public_export.py`; the candidate manifest lists every
copied asset and SHA-256. The complete build is about 2.7 MB. Results are generated
from the completed artifacts; no synthetic flux plot substitutes for the data.
There is no daily-data explorer in this edition. Aggregate benchmark controls,
query-state links, metric downloads and the methodological walkthrough remain.

Public release of this alternative requires the author's approval of this exact
scope and confirmation that the original access agreement does not prohibit
publication of aggregate findings. This profile does not assert blanket source
redistribution permission. Record the scoped approval in
`config/public-release.json` using the example. Deliberately stage the reviewed
`website/aggregate-public` assets, create/push the real repository, then dispatch
the aggregate Pages workflow. The full-content workflow retains its original gate.

## Full-content local edition

No repository or public Pages URL has been created. Local work is complete only
after the validation record and run registry confirm actual outputs.

The concrete publication package has three rights categories:

1. Newly written code: MIT licence. No source notebooks or private documents
   included in tracked files.
2. Dissertation text/figures: author/third-party rights not established by a
   local file. The local reading edition is labelled sanitized and historical;
   student identifier, administrative front matter and personal acknowledgements
   are omitted. Original PDF remains unchanged in the source folder.
3. Simulator data and compact derivatives: origin/licence unresolved. Source
   raw file, extracted datasets, models and generated website research assets
   stay ignored until the data provider's redistribution terms are recorded.
   EIDC observation supporting documents explicitly use OGL with attribution;
   that does not license the separate JULES run.

Before publication, record author permission for the dissertation and data
provider permission/license for compact derivatives in `config/rights.yaml`.
Review the sanitized reading edition and any third-party figures. If approval
excludes the thesis, omit `website/public/thesis` and its link. If approval
excludes derivatives, publish code and methodology only, with an access recipe;
do not expose a website asset under a guessed data licence.

Then stage approved assets deliberately, create a repository on the chosen
GitHub account, add its real remote, push, select GitHub Actions for Pages,
dispatch the Pages workflow and verify the returned deployment URL. No remote
account, domain or repository identity is fabricated. The workflow refuses to
deploy until a rights record and validated research assets are tracked.

[GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits):
published site ≤1 GB. [GitHub large file policy](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)
blocks ordinary repository files over 100 MiB; browser upload ≤25 MiB. The 4.57 GB
raw NetCDF belongs outside both repository and static site.
