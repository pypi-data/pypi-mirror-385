"""Tests for IRF (Item Response Model) functions in base module."""

import numpy as np
import pandas as pd
import pytest
from EqUMP.base.irf import irf


class TestIRF:

    def test_irf_rasch_model(self):
        params = {"b": 0.0}
        theta = 0.0
        result = irf(theta, params, model="Rasch")
        expected = pd.DataFrame([[0.5, 0.5]], index=[theta], columns=["0", "1"])
        pd.testing.assert_frame_equal(result, expected)

    def test_irf_2pl_model(self):
        params = {"a": 1.0, "b": 0.0}
        theta = 0.0
        result = irf(theta, params, model="2PL")
        expected = pd.DataFrame([[0.5, 0.5]], index=[theta], columns=["0", "1"])
        pd.testing.assert_frame_equal(result, expected)

    def test_irf_3pl_model(self):
        params = {"a": 1.0, "b": 0.0, "c": 0.2}
        theta = 0.0
        result = irf(theta, params, model="3PL")
        expected_prob = 0.2 + (1.0 - 0.2) * 0.5
        expected = pd.DataFrame(
            [[1 - expected_prob, expected_prob]], index=[theta], columns=["0", "1"]
        )
        pd.testing.assert_frame_equal(result, expected)

    def test_irf_rasch_vs_2pl_not_equal_off_midpoint(self):
        theta, b = 1.0, 0.0
        p1pl = irf(theta, {'b': b}, model="Rasch").loc[theta, '1']
        p2pl = irf(theta, {'a': 2.5, 'b': b}, model="2PL").loc[theta, '1']
        assert p2pl > p1pl

    def test_irf_grm_model(self):
        params = {"a": 1.0, "b": [-0.5, 0.5, 0.9]}
        theta = 0.0
        out = irf(theta, params, model="GRM")
        p = out.to_numpy().ravel()
        assert out.shape == (1, 4)              # 임계값 3개 → 범주 4개
        assert np.all(p >= 0) and np.all(p <= 1)
        assert np.isclose(p.sum(), 1.0)

    def test_irf_gpcm_model(self):
        params = {"a": 1.0, "b": [-0.3, 0.4, 1.2]}
        theta = 0.0
        params_clean = {"a": params["a"], "b": [0 if np.isnan(x) else x for x in params["b"]]}
        result = irf(theta, params_clean, model="GPCM")
        assert isinstance(result, pd.DataFrame)
        assert result.shape[1] == 4  # 3 points 4 categories
        for idx, row in result.iterrows():
            assert abs(row.sum() - 1.0) < 1e-8
    
    @pytest.mark.skip("Not implemented yet")
    def test_irf_gpcm2_model(self):
        params = {"a": 1.0, "b": [-0.5, 0.5, 0.9]}
        theta = 0.0
        with pytest.raises(NotImplementedError):
            irf(theta, params, model="GPCM2")

    def test_irf_default_scaling_factor(self):
        params = {"a": 1.0, "b": 0.0}
        theta = 1.0
        result_default = irf(theta, params, model="2PL")
        result_d1 = irf(theta, params, D=1.0, model="2PL")
        assert not result_default.equals(result_d1)

    def test_irf_missing_required_parameter(self):
        params = {"a": 1.0}  # Missing 'b'
        theta = 0.0
        with pytest.raises(KeyError):
            irf(theta, params, model="2PL")

    def test_irf_unknown_parameter(self):
        params = {"a": 1.0, "b": 0.0, "unknown": 0.5}
        theta = 0.0
        with pytest.raises(KeyError):
            irf(theta, params, model="2PL")

    def test_irf_invalid_params_type(self):
        params = [1.0, 0.0]  # List instead of dict
        theta = 0.0
        with pytest.raises(TypeError):
            irf(theta, params)

    def test_irf_extreme_values(self):
        params = {"a": 1.0, "b": 0.0}
        result_high = irf(10.0, params, model="2PL")
        prob_high = result_high.loc[10.0, "1"]
        assert prob_high > 0.99
        result_low = irf(-10.0, params, model="2PL")
        prob_low = result_low.loc[-10.0, "1"]
        assert prob_low < 0.01


if __name__ == "__main__":
    pytest.main([__file__])
