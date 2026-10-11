# Data card

Source: user-supplied `u-dn619_jules_crop.daily.2006-2019.nc`, merged using CDO
1.9.7.1 on 21 February 2025, and seven-row `EC_flux_tower_sites.csv`.
No simulation namelist, executable version, crop management, forcing licence or
explicit redistribution licence was recovered. Raw data are not public by
inference from the thesis's nonconfidentiality statement.

Unit of series: six native model cells; seven location labels. Bounds are
standard-calendar daily intervals, 2006-2019, end-labelled. Required selected
weather/flux/state variables have no missing values across extracted sequences.
Finite coordinate and required-variable screening samples three time slabs
across the full native domain; it does not certify every variable in the cube.
All selected-cell sequences receive missingness QC.

Weather: daily air temperature K, shortwave W m-2, precipitation kg m-2 s-1,
wind m s-1. Additional weather humidity kg/kg and pressure Pa support approximate
daily VPD. State: four soil moisture layers, kg water m-2, requiring simulator
state at inference. They are not measured water-table depth.
Targets: simulated GPP, plant respiration, soil respiration. JULES carbon-mass
interpretation from output documentation; constant 12.0107 g/mol. Atmospheric
NEE positive release and negative uptake. Budget conversion integrates exact
durations; 1 μmol/s sustained daily = 1.03772448 g C/day per m2.

Full original CSV value `4-Feb` is preserved and unused. Source site coordinates
and official observational site coordinates can differ; locations are not exact
tower footprint replicas. Native NetCDF coordinate datum is undeclared.

Raw extracts and all derivatives stay ignored locally pending rights resolution.
Provide an authorized source path using `config/local.yaml`; never commit that
path. Test fixtures are synthetic and cannot support research findings. An
authentic smoke subset is generated locally, not redistributed without licence.
