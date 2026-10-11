"""Synthetic end-to-end workflow. Never used for scientific findings."""

from pathlib import Path

import numpy as np
import pandas as pd

from .data import samples
from .experiments import fit_predict


def fixture():
    rng = np.random.default_rng(7)
    frames = []
    for cell in ["synthetic_a", "synthetic_b"]:
        for split, year in [
            ("train", 2014),
            ("validation", 2015),
            ("calibration", 2016),
            ("test", 2017),
        ]:
            dates = pd.date_range(f"{year}-01-01", periods=90)
            t = np.arange(90)
            frame = pd.DataFrame(
                {
                    "cell": cell,
                    "start": dates,
                    "end": dates + pd.Timedelta(days=1),
                    "split": split,
                    "seconds": 86400,
                    "tair": 280 + t / 10,
                    "sw": 100 + 20 * np.sin(t / 10),
                    "pr": rng.random(90) / 1000,
                    "wind": rng.random(90) * 5,
                    "gpp": 2 + np.sin(t / 10),
                    "rp": 1 + np.sin(t / 10) / 3,
                    "rs": np.ones(90),
                }
            )
            frame["key"] = cell + ":" + frame.start.dt.strftime("%Y-%m-%d")
            frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def smoke(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    x, y, m = samples(fixture(), 7)
    f, s = fit_predict("ridge", x, y, m, 17, {}, out, "SYNTHETIC-SMOKE")
    assert len(f) == 186 and s["train_n"] == 62
    assert f.key.is_unique
    print("Synthetic smoke completed; not a full-data model run.")
