# Publication readiness and rights

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
