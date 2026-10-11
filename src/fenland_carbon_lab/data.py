"""Metadata-aware bounded extraction; every sample retains interval provenance."""

from __future__ import annotations

import json
import re
from pathlib import Path

import netCDF4 as nc
import numpy as np
import pandas as pd

ATOMIC_C = 12.0107
COMPONENTS = ["gpp", "rp", "rs"]
WEATHER = ["tair", "sw", "pr", "wind"]
VARIABLES = {
    "gpp": "gpp_gb",
    "rp": "resp_p_gb",
    "rs": "resp_s_gb",
    "tair": "t1p5m_gb",
    "sw": "sw_down",
    "pr": "precip",
    "wind": "wind",
    "humidity": "q1p5m_gb",
    "pressure": "pstar",
}
EXPECTED_UNITS = {
    "gpp": "kg m-2 s-1",
    "rp": "kg m-2 s-1",
    "rs": "kg m-2 s-1",
    "tair": "K",
    "sw": "W m-2",
    "pr": "kg m-2 s-1",
    "wind": "m s-1",
    "humidity": "kg kg-1",
    "pressure": "Pa",
}


def carbon_umol(value):
    return np.asarray(value) * 1e9 / ATOMIC_C


def nee(components):
    c = np.asarray(components)
    return c[..., 1] + c[..., 2] - c[..., 0]


def spread_inverse(value, scale):
    if np.any(np.asarray(value) < 0) or np.any(np.asarray(scale) <= 0):
        raise ValueError("Spread and scale must be nonnegative/positive")
    return np.asarray(value) * scale


def coordinates(text):
    matches = re.findall(r"([\d.]+)\s*°?\s*([NSEW])", text)
    if len(matches) != 2 or matches[0][1] not in "NS" or matches[1][1] not in "EW":
        raise ValueError(f"Malformed coordinates: {text}")
    a, b = (float(v) * (-1 if d in "SW" else 1) for v, d in matches)
    if abs(a) > 90 or abs(b) > 180:
        raise ValueError("Coordinates outside geographic domain")
    return a, b


def distances(lat, lon, a, b):
    lat, lon, a, b = map(np.deg2rad, [lat, lon, a, b])
    hav = np.sin((lat - a) / 2) ** 2 + np.cos(lat) * np.cos(a) * np.sin((lon - b) / 2) ** 2
    return 6371.0088 * 2 * np.arcsin(np.sqrt(np.clip(hav, 0, 1)))


def split_for(dates):
    year = pd.DatetimeIndex(dates).year
    if np.any((year < 2006) | (year > 2019)):
        raise ValueError("Intervals outside protocol")
    return np.select(
        [year <= 2014, year == 2015, year == 2016],
        ["train", "validation", "calibration"],
        default="test",
    )


def validate_intervals(start, end, labels):
    start, end, labels = map(pd.DatetimeIndex, [start, end, labels])
    duration = (end - start).total_seconds().to_numpy()
    if np.any(duration != 86400) or not np.array_equal(end.asi8, labels.asi8):
        raise ValueError("Expected end-labelled standard daily means")
    if start.has_duplicates or np.any(np.diff(start.asi8) <= 0):
        raise ValueError("Duplicate or unsorted intervals")
    return duration


def extract(raw: Path, sites_path: Path, output: Path):
    output.mkdir(parents=True, exist_ok=True)
    sites = pd.read_csv(sites_path)
    mapping, frames = [], []
    with nc.Dataset(raw) as ds:
        if getattr(ds["time"], "calendar", "standard") not in ("standard", "gregorian"):
            raise ValueError("Unsupported calendar")
        for key, variable in VARIABLES.items():
            v = ds[variable]
            if v.units != EXPECTED_UNITS[key] or v.dimensions != ("time", "y", "x"):
                raise ValueError(f"Unexpected units/dimensions: {variable}")
            if "mean" not in getattr(v, "cell_methods", ""):
                raise ValueError(f"Missing time mean: {variable}")
        if ds["smcl"].dimensions != ("time", "soil", "y", "x") or ds["smcl"].units != "kg m-2":
            raise ValueError("Unexpected soil moisture metadata")
        t = ds["time"]
        bounds = ds[t.bounds][:]

        def convert(a):
            return pd.to_datetime([str(d) for d in nc.num2date(a, t.units, calendar=t.calendar)])

        start, end, labels = convert(bounds[:, 0]), convert(bounds[:, 1]), convert(t[:])
        durations = validate_intervals(start, end, labels)
        lat = np.ma.filled(ds["latitude"][:], np.nan)
        lon = np.ma.filled(ds["longitude"][:], np.nan)
        if lat.shape != lon.shape or lat.shape != (
            len(ds.dimensions["y"]),
            len(ds.dimensions["x"]),
        ):
            raise ValueError("Coordinate dimensions mismatch")
        # Coordinate validity plus actual required-variable validity, bounded one-day slabs.
        valid = np.isfinite(lat) & np.isfinite(lon) & (abs(lat) <= 90) & (abs(lon) <= 360)
        for variable in VARIABLES.values():
            for i in [0, len(start) // 2, len(start) - 1]:
                valid &= np.isfinite(np.ma.filled(ds[variable][i], np.nan))
        for _, site in sites.iterrows():
            a, b = coordinates(site["Coordinates"])
            d = np.where(valid, distances(lat, lon, a, b), np.inf)
            y, x = np.unravel_index(np.argmin(d), d.shape)
            if not np.isfinite(d[y, x]):
                raise ValueError("No valid native cell")
            mapping.append(
                {
                    "site": site["Site Name"],
                    "code": site["Site code"],
                    "site_lat": a,
                    "site_lon": b,
                    "grid_lat": float(lat[y, x]),
                    "grid_lon": float(lon[y, x]),
                    "x": int(x),
                    "y": int(y),
                    "cell": f"x{x}_y{y}",
                    "distance_km": float(d[y, x]),
                    "peat_depth_original": site["Peat depth (m)"],
                    "peat_depth_status": "unresolved spreadsheet coercion"
                    if site["Peat depth (m)"] == "4-Feb"
                    else "source CSV",
                }
            )
        for m in {r["cell"]: r for r in mapping}.values():
            frame = pd.DataFrame(
                {
                    "start": start,
                    "end": end,
                    "label": labels,
                    "seconds": durations,
                    "cell": m["cell"],
                    "split": split_for(start),
                }
            )
            for key, variable in VARIABLES.items():
                # Slab selects exactly one native cell; never materializes full 4.57GB cube.
                value = np.ma.filled(ds[variable][:, m["y"], m["x"]], np.nan)
                frame[key + "_raw"] = value
                frame[key] = carbon_umol(value) if key in COMPONENTS else value
            for layer in range(4):
                frame[f"sm{layer}"] = np.ma.filled(ds["smcl"][:, layer, m["y"], m["x"]], np.nan)
            frame["key"] = frame["cell"] + ":" + frame["start"].dt.strftime("%Y-%m-%d")
            frame["nee"] = nee(frame[COMPONENTS])
            frame["nee_raw"] = frame["rp_raw"] + frame["rs_raw"] - frame["gpp_raw"]
            frames.append(frame)
    data = pd.concat(frames, ignore_index=True)
    if data.key.duplicated().any():
        raise ValueError("Duplicate cell/interval keys")
    data.to_csv(output / "cells.csv", index=False)
    pd.DataFrame(mapping).to_csv(output / "mapping.csv", index=False)
    numeric = data.select_dtypes("number")
    qc = {
        "rows": len(data),
        "cells": data.cell.nunique(),
        "sites": len(mapping),
        "missingness": numeric.isna().sum().to_dict(),
        "split_counts": data.groupby("split").size().to_dict(),
        "geometry": "Native paired latitude/longitude vectors encoded as (y=1,x=12392). No polygon bounds or CRS grid mapping; not evidence of a conventional curvilinear mesh.",
        "valid_coordinate_and_sampled_variable_cells": int(valid.sum()),
        "validity_limit": "Full selected-cell sequences QC; three time slabs across grid. Not exhaustive cube QC.",
    }
    corr = data.pivot(index="start", columns="cell", values="tair").corr()
    corr.to_csv(output / "forcing_temperature_correlations.csv")
    (output / "qc.json").write_text(json.dumps(qc, indent=2))
    return data


def samples(data, length=24, features=WEATHER, horizon=0, common_length=60):
    if length < 1 or horizon < 0 or common_length < length:
        raise ValueError("Invalid length/horizon/common length")
    xs, ys, meta = [], [], []
    for _, g in data.groupby(["cell", "split"], sort=True):
        g = g.sort_values("start").reset_index(drop=True)
        weather = g[features].to_numpy(dtype=np.float32)
        target = g[COMPONENTS].to_numpy(dtype=np.float32)
        if len(g) < common_length + horizon:
            continue
        i = np.arange(common_length - 1, len(g) - horizon)
        j = i + horizon
        time_ns = pd.DatetimeIndex(g.start).as_unit("ns").asi8
        gaps = np.concatenate([[0], np.cumsum(np.diff(time_ns) != 86400 * 10**9)])
        windows = np.lib.stride_tricks.sliding_window_view(weather, length, axis=0).swapaxes(1, 2)
        chosen = windows[i - length + 1]
        valid = (
            (gaps[j] - gaps[i - common_length + 1] == 0)
            & np.isfinite(chosen).all(axis=(1, 2))
            & np.isfinite(target[j]).all(axis=1)
        )
        if set(WEATHER).issubset(g.columns):
            missing = np.concatenate(
                [[0], np.cumsum(~np.isfinite(g[WEATHER].to_numpy()).all(axis=1))]
            )
            valid &= missing[i + 1] - missing[i - common_length + 1] == 0
        i, j, chosen = i[valid], j[valid], chosen[valid]
        xs.append(chosen)
        ys.append(target[j])
        rows = g.iloc[j][["key", "cell", "start", "end", "seconds", "split"]].reset_index(drop=True)
        rows["feature_start"] = g.iloc[i - length + 1].start.to_numpy()
        rows["feature_end"] = g.iloc[i].end.to_numpy()
        rows["horizon_days"] = horizon
        meta.append(rows)
    if not meta:
        return (
            np.empty((0, length, len(features))),
            np.empty((0, 3)),
            pd.DataFrame(
                columns=[
                    "key",
                    "cell",
                    "start",
                    "end",
                    "seconds",
                    "split",
                    "feature_start",
                    "feature_end",
                    "horizon_days",
                ]
            ),
        )
    return np.concatenate(xs), np.concatenate(ys), pd.concat(meta, ignore_index=True)
