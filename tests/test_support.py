import numpy as np
import pandas as pd
import pytest

from fenland_carbon_lab.support import (
    aggregate_group,
    align_predictions,
    fit_support,
    representation,
    score_support,
)


def test_training_only_and_frozen_threshold():
    rng = np.random.default_rng(17)
    x = rng.normal(size=(100, 8))
    train = np.arange(100) < 80
    first = fit_support(x, train)
    changed = x.copy()
    changed[~train] = 1e6
    second = fit_support(changed, train)
    np.testing.assert_array_equal(first[0].mean_, second[0].mean_)
    np.testing.assert_array_equal(first[1].covariance_, second[1].covariance_)
    assert first[2] == second[2]
    _, flags = score_support(changed, first)
    assert flags[~train].all()
    assert first[2] == second[2]


def test_representation_and_nonfinite():
    x = np.arange(2 * 60 * 4).reshape(2, 60, 4).astype(float)
    result = representation(x)
    np.testing.assert_array_equal(result[:, :4], x[:, -1])
    np.testing.assert_array_equal(result[:, 4:], x.mean(axis=1))
    x[0, 0, 0] = np.nan
    with pytest.raises(ValueError):
        representation(x)
    with pytest.raises(ValueError):
        score_support(np.array([[np.nan] * 8]), None)


def test_key_join_and_split_integrity():
    p = pd.DataFrame({"key": ["b", "a"], "split": ["test", "validation"]})
    f = pd.DataFrame(
        {
            "key": ["a", "b", "c"],
            "split": ["validation", "test", "train"],
            "flagged": [False, True, False],
        }
    )
    assert align_predictions(p, f).flagged.tolist() == [True, False]
    with pytest.raises(ValueError):
        align_predictions(pd.concat([p, p]), f)
    with pytest.raises(ValueError):
        align_predictions(p.iloc[:1], f)
    f.loc[0, "split"] = "calibration"
    with pytest.raises(ValueError):
        align_predictions(p, f)


def test_small_groups_and_intervals():
    p = pd.DataFrame({"nee_true": [0.0] * 30, "nee_pred": [1.0] * 30})
    assert aggregate_group(p.iloc[:29], 100, 4)["rmse"] is None
    assert aggregate_group(p.iloc[:0], 100, 4)["interpretation"] == "insufficient evidence"
    row = aggregate_group(p, 100, 4)
    assert row["rmse"] == 1 and row["coverage95"] == 1 and row["proportion"] == 0.3
    assert set(row) == {
        "n",
        "proportion",
        "rmse",
        "mae",
        "bias",
        "coverage95",
        "mean_width95",
        "interpretation",
    }
    assert not any(isinstance(value, (list, np.ndarray)) for value in row.values())
