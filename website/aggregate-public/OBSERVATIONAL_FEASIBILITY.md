# Observational validation feasibility, 12 October 2026

Decision: **no direct observational validation score is scientifically defensible
yet**. Both candidates have usable licensed data and supporting documentation;
the simulator crop, management, version and footprint compatibility are missing.
No tower measurements were collected by this project. A contextual comparison
would conflate emulator error with simulator-to-nature and management mismatch.

## Deep-peat arable field

[EIDC record](https://catalogue.ceh.ac.uk/documents/13896773-01e5-48e6-bfab-c319de46b221),
Cumming et al. (2020), OGL. Supporting RTF downloaded and inspected. It places
EF-DA at 52°31′N, 0°29′E (52.5167, 0.4833), differing slightly from the dissertation
CSV. Half-hour means are end-labelled. The overlap is 2012-06-22 through the end
of 2019. NEE is μmol CO2 m-2 s-1, with positive release implied by removal of
negative nighttime fluxes. `NEE` and `NEE_filled` distinguish measured/QC versus
gap-filled values. QC removes outliers, nonstationarity and inappropriate
footprints; retained fluxes must have >70% target-field contribution. The listed
rotations are lettuce, leek, celery, sugar beet and potatoes. NEE partitioning
estimates GEP and total respiration, not independently measured Rp and Rs.

## Ten-site network

[EIDC record](https://catalogue.ceh.ac.uk/documents/06d7c463-298c-4c7e-a4c3-55d003aa91cb),
Cooper et al. (2024), OGL. Supporting site metadata, data dictionary and RTF
downloaded and inspected. Actual matching locations:

| Site | Official coordinates | Record interval | Overlap with JULES |
|---|---|---|---|
| Great Fen EF-GF | 52.4705, -0.1930 | 2018-03-01 to 2021-04-06 | 2018-2019 |
| Woodwalton EF-NE | 52.4600, -0.1851 | 2020-08-12 to 2023-02-28 | None |
| Redmere 1 EF-SA | 52.4430, 0.4195 | 2021-04-29 to 2023-02-28 | None in this record |

Great Fen is grassland, not a verified Miscanthus scenario. Other regional sites
must be matched by their actual metadata, not dissertation labels alone.
Flux blocks are 30 minutes, use stationarity/turbulence and USTAR checks, and
>80% target footprint contribution. Missing values are -9999. Timestamp start/end,
measured and filled NEE, gap-filling flags and partitioned products have separate
dictionary entries. Documented partitioning is not independent component truth.

## Required harmonization if configuration becomes available

Acquire only matching-site/overlap rows, preserving source QA and measured/filled
status. Resolve UTC/local time convention and NEE sign against actual headers.
Integrate half-hour fluxes with interval seconds, require declared daily coverage,
report measured-only and filled sensitivity, then align to JULES daily bounds.
Keep surrogate→JULES, JULES→tower and surrogate→tower scores separate. Evaluate
NEE only unless independent component observations exist. Record footprint versus
native-cell mismatch and management differences. Do not use 2020-2023 as matched
evaluation of runs ending 2019. Flux observations were not downloaded for scoring
because management compatibility fails the present feasibility gate.

Retrieval checksums and exact supporting-file names are retained locally in the
source evidence bundle. The OGL permissions on these records do not establish
rights to the user-supplied simulator outputs.
