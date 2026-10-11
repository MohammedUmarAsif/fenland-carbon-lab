import numpy as np
import pandas as pd
import pytest

from fenland_carbon_lab.data import (
    ATOMIC_C,
    carbon_umol,
    coordinates,
    distances,
    nee,
    samples,
    split_for,
    spread_inverse,
    validate_intervals,
)
from fenland_carbon_lab.metrics import interval_metrics, metrics, monthly, paired_blocks
from fenland_carbon_lab.smoke import fixture, smoke


def test_carbon_sign_and_budget():
    assert carbon_umol(ATOMIC_C * 1e-9) == pytest.approx(1)
    assert nee([4, 1, 2]) == -1
    assert ATOMIC_C * 1e-6 * 86400 == pytest.approx(1.03772448)


@pytest.mark.parametrize(
    "text,expected", [("52.461°N, 0.1851°W", (52.461, -0.1851)), ("1°S, 3°E", (-1, 3))]
)
def test_coordinates(text, expected):
    assert coordinates(text) == expected


@pytest.mark.parametrize("text", ["91°N, 0°E", "52.4, .2", "0°E, 50°N"])
def test_malformed_coordinates(text):
    with pytest.raises(ValueError):
        coordinates(text)


def test_geodesic():
    assert distances(0, 0, 0, 1) == pytest.approx(111.19508, rel=1e-6)


def test_end_label_year():
    a = pd.date_range("2019-12-31", periods=1)
    b = a + pd.Timedelta(days=1)
    assert validate_intervals(a, b, b)[0] == 86400
    assert split_for(a)[0] == "test"
    with pytest.raises(ValueError):
        validate_intervals(a, b, a)


def test_window_alignment_nowcast_and_forecast():
    f = fixture()
    x, y, m = samples(f, 7)
    keyed = f.set_index("key").loc[m.key]
    np.testing.assert_allclose(x[:, -1, 0], keyed.tair)
    np.testing.assert_allclose(y[:, 0], keyed.gpp)
    assert (pd.to_datetime(m.feature_end) == pd.to_datetime(m.end)).all()
    x, y, m = samples(f, 7, horizon=1)
    assert ((pd.to_datetime(m.start) - pd.to_datetime(m.feature_end)).dt.total_seconds() == 0).all()


def test_no_cross_cell_split_or_gap():
    f = fixture()
    f = f.drop(f[(f.cell == "synthetic_a") & (f.split == "train")].index[65])
    _, _, m = samples(f, 24)
    g = m[m.cell.eq("synthetic_a") & m.split.eq("train")]
    assert len(g) == 6  # Only targets before missing day; later context remains incomplete.
    assert m.key.is_unique
    assert (pd.to_datetime(m.feature_start).dt.year == pd.to_datetime(m.start).dt.year).all()


def test_matched_history_targets():
    manifests = [samples(fixture(), length)[2] for length in [1, 7, 24, 60]]
    for m in manifests[1:]:
        assert m.key.tolist() == manifests[0].key.tolist()


def test_train_only_and_group_isolation(tmp_path):
    from fenland_carbon_lab.experiments import fit_predict

    f = fixture()
    f.loc[f.split == "test", "tair"] = 99999
    x, y, m = samples(f, 7)
    train = (m.split.eq("train") & m.cell.eq("synthetic_a")).to_numpy()
    evaluate = (m.split.eq("test") & m.cell.eq("synthetic_b")).to_numpy()
    _, s = fit_predict(
        "ridge",
        x,
        y,
        m,
        17,
        {},
        tmp_path,
        "isolation",
        train_override=train,
        eval_override=evaluate,
    )
    assert s["feature_mean"][0] < 300
    assert s["train_cells"] == ["synthetic_a"]
    assert s["train_last"].startswith("2014")


def test_spread_and_ordered_intervals():
    assert spread_inverse(0.1, 3.6) == pytest.approx(0.36)
    with pytest.raises(ValueError):
        spread_inverse(-0.1, 3.6)
    r = interval_metrics(np.array([0, 1]), np.array([0, 0]), 0.5, 0.95)
    assert r["coverage"] == 0.5 and r["mean_width"] == 1
    assert r["interval_score"] == pytest.approx(11)


def test_monthly_interval_not_label():
    d = pd.date_range("2019-12-01", periods=31)
    f = pd.DataFrame(
        {
            "cell": "a",
            "start": d,
            "end": d + pd.Timedelta(days=1),
            "split": "test",
            "key": d.astype(str),
            "seconds": 86400,
            "nee_true": 1.0,
            "nee_pred": 2.0,
        }
    )
    m = monthly(f)
    assert m.month.iloc[0] == "2019-12" and m.complete.iloc[0]
    assert m.reference_gC.iloc[0] == pytest.approx(31 * 1.03772448)
    assert not monthly(f.iloc[:-1]).complete.iloc[0]


def test_negative_r2_and_pair_keys():
    assert metrics([1, 2, 3], [9, 9, 9])["r2"] < 0
    a = pd.DataFrame(
        {
            "key": ["a", "b"],
            "start": ["2017-01-01", "2017-01-02"],
            "nee_true": [1, 2],
            "nee_pred": [2, 3],
        }
    )
    b = a.copy()
    b.nee_pred = b.nee_true
    result = paired_blocks(a, b, 1, reps=20)
    assert result["difference_rmse_a_minus_b"] == 1
    with pytest.raises(ValueError):
        paired_blocks(a, b.iloc[:1])


def test_smoke(tmp_path):
    smoke(tmp_path)
