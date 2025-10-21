"""Tests for TRF (Total Response Function) functions in base module."""

import numpy as np
import pandas as pd
import pytest
from EqUMP.base.trf import trf, create_prob_df


class TestTRF:

    def test_create_prob_df(self):
        theta = 0.0
        items = [
            {"a": 1.2, "b": 0.2},
            {"a": 0.5, "b": 1.2},
            {"a": 1.0, "b": 0.0, "c": 0.2},
            {"a": 1.0, "b": [-0.7, 0.0, 0.5]},
        ]
        models = ["1PL", "2PL", "3PL", "GPCM"]
        result = create_prob_df(theta, items, model=models)
        assert isinstance(result, pd.DataFrame)
        assert result.shape[0] == len(items)        
        for _, row in result.iterrows():
            assert abs(row.sum() - 1.0) < 1e-8

    def test_trf_basic(self):
        theta = np.array([0.0, 1.0, -1.0])
        prob_df = pd.DataFrame(
            {"0": [0.5, 0.3, 0.7], "1": [0.5, 0.7, 0.3]}, index=theta
        )
        result = trf(prob_df)
        expected = float((prob_df * prob_df.columns.astype(float)).sum().sum())
        assert abs(result - expected) < 1e-10

    def test_trf_single_item(self):
        theta = 0.0
        prob_df = pd.DataFrame({"0": [0.5], "1": [0.5]}, index=[theta])
        result = trf(prob_df)
        expected = float((prob_df * prob_df.columns.astype(float)).sum().sum())
        assert abs(result - expected) < 1e-10

    def test_trf_multiple_items(self):
        theta = [0.0, 1.0]
        prob_df = pd.DataFrame({"0": [0.5, 0.3], "1": [0.5, 0.7]}, index=theta)
        result = trf(prob_df)
        expected = float((prob_df * prob_df.columns.astype(float)).sum().sum())
        assert abs(result - expected) < 1e-10

    def test_trf_monotonic_property(self):
        theta = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
        prob_df = pd.DataFrame(
            {"0": [0.9, 0.7, 0.5, 0.3, 0.1], "1": [0.1, 0.3, 0.5, 0.7, 0.9]},
            index=theta,
        )
        results = [trf(prob_df.loc[[t]]) for t in theta]
        for i in range(len(results) - 1):
            assert results[i] <= results[i + 1]

    def test_trf_invalid_theta_type(self):
        prob_df = pd.DataFrame({"0": [0.5], "1": [0.5]}, index=["not_a_float"])
        with pytest.raises(Exception):
            trf(prob_df)

    def test_trf_empty_arrays(self):
        prob_df = pd.DataFrame({"0": [], "1": []})
        result = trf(prob_df)
        assert result == 0.0


if __name__ == "__main__":
    pytest.main([__file__])