import netCDF4 as nc
import numpy as np
import pandas as pd
import pytest

from fenland_carbon_lab.data import EXPECTED_UNITS, VARIABLES, extract


def raw_fixture(path):
    with nc.Dataset(path, "w") as ds:
        for name, size in [("time", 5), ("bnds", 2), ("y", 1), ("x", 2), ("soil", 4)]:
            ds.createDimension(name, size)
        t = ds.createVariable("time", "f8", ("time",))
        t.units = "seconds since 2006-01-01 00:00:00"
        t.calendar = "standard"
        t.bounds = "time_bnds"
        t[:] = np.arange(1, 6) * 86400
        b = ds.createVariable("time_bnds", "f8", ("time", "bnds"))
        b[:] = np.column_stack([np.arange(5) * 86400, np.arange(1, 6) * 86400])
        ds.createVariable("latitude", "f8", ("y", "x"))[:] = [[52, 52]]
        ds.createVariable("longitude", "f8", ("y", "x"))[:] = [[-0.2, 0.2]]
        for key, name in VARIABLES.items():
            v = ds.createVariable(name, "f8", ("time", "y", "x"), fill_value=-1e20)
            v.units = EXPECTED_UNITS[key]
            v.cell_methods = "time : mean"
            v[:] = 1e-8 if key in ["gpp", "rp", "rs"] else 1
        v = ds.createVariable("smcl", "f8", ("time", "soil", "y", "x"))
        v.units = "kg m-2"
        v[:] = 1


def test_extract_native_west_duplicate_and_bounds(tmp_path):
    raw = tmp_path / "test.nc"
    raw_fixture(raw)
    sites = tmp_path / "sites.csv"
    pd.DataFrame(
        {
            "Site Name": ["synthetic west A", "synthetic west B"],
            "Site code": ["A", "B"],
            "Coordinates": ["52°N, 0.2°W", "52°N, 0.2°W"],
            "Peat depth (m)": ["1", "4-Feb"],
        }
    ).to_csv(sites, index=False)
    d = extract(raw, sites, tmp_path / "out")
    assert len(d) == 5 and d.cell.nunique() == 1
    assert d.cell.iloc[0] == "x0_y0"
    assert d.start.iloc[0] == pd.Timestamp("2006-01-01")
    assert d.end.iloc[0] == pd.Timestamp("2006-01-02")
    m = pd.read_csv(tmp_path / "out/mapping.csv")
    assert m.distance_km.eq(0).all()
    assert "unresolved" in m.peat_depth_status.iloc[1]


def test_bad_units_rejected(tmp_path):
    raw = tmp_path / "test.nc"
    raw_fixture(raw)
    with nc.Dataset(raw, "a") as ds:
        ds["gpp_gb"].units = "kg CO2 m-2 s-1"
    sites = tmp_path / "sites.csv"
    pd.DataFrame(
        {
            "Site Name": ["a"],
            "Site code": ["a"],
            "Coordinates": ["52°N, 0.2°W"],
            "Peat depth (m)": ["1"],
        }
    ).to_csv(sites, index=False)
    with pytest.raises(ValueError, match="units/dimensions"):
        extract(raw, sites, tmp_path / "out")
