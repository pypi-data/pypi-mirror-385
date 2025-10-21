"""Comprehensive tests for custom scoring functionality in IRF.prob() method.

This test suite focuses on the custom scoring implementation in lines 662-675 of irf.py,
which allows users to specify non-sequential score values for item response categories.
"""
import numpy as np
import pandas as pd
import pytest

from EqUMP.base.irf import IRF


class TestIRFCustomScoring:
    """Test suite for custom scoring functionality in IRF.prob() method."""

    # ========================================================================
    # Tests for dichotomous items with custom scores
    # ========================================================================

    def test_prob_dichotomous_custom_scores_scalar_theta(self):
        """Test prob() with custom scores for dichotomous item (scalar theta)."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL", scores=[0, 5])
        prob = item.prob(theta=0.0)
        
        # Check that columns are labeled with custom scores
        assert list(prob.columns) == ["0.0", "5.0"]
        assert prob.shape == (1, 2)
        
        # Probabilities should still sum to 1
        assert np.isclose(prob.sum(axis=1).values[0], 1.0)

    def test_prob_dichotomous_custom_scores_array_theta(self):
        """Test prob() with custom scores for dichotomous item (array theta)."""
        item = IRF(params={"a": 1.2, "b": 0.5}, model="2PL", scores=[0, 10])
        theta = np.array([-1.0, 0.0, 1.0, 2.0])
        prob = item.prob(theta=theta)
        
        # Check shape and columns
        assert prob.shape == (4, 2)
        assert list(prob.columns) == ["0.0", "10.0"]
        
        # Check index is theta values
        assert np.array_equal(prob.index.values, theta)
        assert prob.index.name == "theta"
        
        # All rows should sum to 1
        assert np.allclose(prob.sum(axis=1).values, 1.0)

    def test_prob_dichotomous_custom_scores_list_theta(self):
        """Test prob() with custom scores for dichotomous item (list theta)."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL", scores=[1, 2])
        prob = item.prob(theta=[-2, -1, 0, 1, 2])
        
        assert prob.shape == (5, 2)
        assert list(prob.columns) == ["1.0", "2.0"]
        assert np.allclose(prob.sum(axis=1).values, 1.0)

    def test_prob_dichotomous_negative_scores(self):
        """Test prob() with negative custom scores."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL", scores=[-5, 5])
        prob = item.prob(theta=0.0)
        
        assert list(prob.columns) == ["-5.0", "5.0"]
        assert np.isclose(prob.sum(axis=1).values[0], 1.0)
    
    # ========================================================================
    # Tests for polytomous items with custom scores
    # ========================================================================

    def test_prob_polytomous_custom_scores_scalar_theta(self):
        """Test prob() with custom scores for polytomous item (scalar theta)."""
        item = IRF(
            params={"a": 1.0, "b": [-0.5, 0.0, 0.5]},
            model="GPCM",
            scores=[0, 2, 5, 10]
        )
        prob = item.prob(theta=0.0)
        
        # Check columns are labeled with custom scores
        assert list(prob.columns) == ["0.0", "2.0", "5.0", "10.0"]
        assert prob.shape == (1, 4)
        
        # Probabilities should sum to 1
        assert np.isclose(prob.sum(axis=1).values[0], 1.0)

    def test_prob_polytomous_custom_scores_array_theta(self):
        """Test prob() with custom scores for polytomous item (array theta)."""
        item = IRF(
            params={"a": 1.0, "b": [-1.0, 0.0, 1.0]},
            model="GPCM",
            scores=[0, 1, 3, 6]
        )
        theta = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
        prob = item.prob(theta=theta)
        
        # Check shape and columns
        assert prob.shape == (5, 4)
        assert list(prob.columns) == ["0.0", "1.0", "3.0", "6.0"]
        
        # Check index
        assert np.array_equal(prob.index.values, theta)
        assert prob.index.name == "theta"
        
        # All rows should sum to 1
        assert np.allclose(prob.sum(axis=1).values, 1.0)

    def test_prob_polytomous_custom_scores_list_theta(self):
        """Test prob() with custom scores for polytomous item (list theta)."""
        item = IRF(
            params={"a": 1.0, "b": [-0.5, 0.5]},
            model="GPCM",
            scores=[0, 5, 10]
        )
        prob = item.prob(theta=[-1, 0, 1])
        
        assert prob.shape == (3, 3)
        assert list(prob.columns) == ["0.0", "5.0", "10.0"]
        assert np.allclose(prob.sum(axis=1).values, 1.0)

    def test_prob_polytomous_nonsequential_scores(self):
        """Test prob() with non-sequential custom scores."""
        item = IRF(
            params={"a": 1.0, "b": [-1.0, 0.0, 1.0]},
            model="GPCM",
            scores=[0, 3, 7, 15]  # Non-sequential
        )
        prob = item.prob(theta=0.0)
        
        assert list(prob.columns) == ["0.0", "3.0", "7.0", "15.0"]
        assert np.isclose(prob.sum(axis=1).values[0], 1.0)

    def test_prob_polytomous_negative_scores(self):
        """Test prob() with negative custom scores for polytomous item."""
        item = IRF(
            params={"a": 1.0, "b": [-0.5, 0.5]},
            model="GPCM",
            scores=[-2, 0, 2]
        )
        prob = item.prob(theta=0.0)
        
        assert list(prob.columns) == ["-2.0", "0.0", "2.0"]
        assert np.isclose(prob.sum(axis=1).values[0], 1.0)

    # ========================================================================
    # Tests for GRM model with custom scores
    # ========================================================================

    def test_prob_grm_custom_scores_scalar_theta(self):
        """Test prob() with custom scores for GRM model (scalar theta)."""
        item = IRF(
            params={"a": 1.5, "b": [-1.0, 0.0, 1.0]},
            model="GRM",
            scores=[0, 2, 4, 8]
        )
        prob = item.prob(theta=0.0)
        
        assert list(prob.columns) == ["0.0", "2.0", "4.0", "8.0"]
        assert prob.shape == (1, 4)
        assert np.isclose(prob.sum(axis=1).values[0], 1.0)

    def test_prob_grm_custom_scores_array_theta(self):
        """Test prob() with custom scores for GRM model (array theta)."""
        item = IRF(
            params={"a": 1.0, "b": [-0.5, 0.0, 0.5]},
            model="GRM",
            scores=[1, 2, 3, 4]
        )
        theta = np.array([-1.0, 0.0, 1.0])
        prob = item.prob(theta=theta)
        
        assert prob.shape == (3, 4)
        assert list(prob.columns) == ["1.0", "2.0", "3.0", "4.0"]
        assert np.allclose(prob.sum(axis=1).values, 1.0)

    # ========================================================================
    # Tests for default scores (no custom scores provided)
    # ========================================================================

    def test_prob_default_scores_dichotomous(self):
        """Test prob() with default scores for dichotomous item."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        prob = item.prob(theta=0.0)
        
        # Default scores should be [0, 1]
        assert list(prob.columns) == ["0.0", "1.0"]

    def test_prob_default_scores_polytomous(self):
        """Test prob() with default scores for polytomous item."""
        item = IRF(
            params={"a": 1.0, "b": [-0.5, 0.0, 0.5]},
            model="GPCM"
        )
        prob = item.prob(theta=0.0)
        
        # Default scores should be [0, 1, 2, 3]
        assert list(prob.columns) == ["0.0", "1.0", "2.0", "3.0"]

    # ========================================================================
    # Tests for consistency between scalar and array theta
    # ========================================================================

    def test_prob_custom_scores_scalar_vs_array_consistency(self):
        """Test that scalar and array theta give consistent results with custom scores."""
        item = IRF(
            params={"a": 1.2, "b": 0.5},
            model="2PL",
            scores=[0, 10]
        )
        
        # Scalar theta
        prob_scalar = item.prob(theta=0.5)
        
        # Array theta with single value
        prob_array = item.prob(theta=np.array([0.5]))
        
        # Values should be the same
        assert np.allclose(prob_scalar.values, prob_array.values)
        
        # Columns should be the same
        assert list(prob_scalar.columns) == list(prob_array.columns)

    def test_prob_custom_scores_multiple_theta_consistency(self):
        """Test consistency when extracting single theta from array result."""
        item = IRF(
            params={"a": 1.0, "b": [-0.5, 0.5]},
            model="GPCM",
            scores=[0, 5, 10]
        )
        
        theta_val = 0.0
        
        # Get prob for single theta
        prob_single = item.prob(theta=theta_val)
        
        # Get prob for array including that theta
        theta_array = np.array([-1.0, 0.0, 1.0])
        prob_array = item.prob(theta=theta_array)
        
        # Extract the row for theta=0.0
        prob_extracted = prob_array.loc[[0.0]]
        
        # Values should match
        assert np.allclose(prob_single.values, prob_extracted.values)
        
        # Columns should match
        assert list(prob_single.columns) == list(prob_extracted.columns)

    # ========================================================================
    # Tests for edge cases
    # ========================================================================

    def test_prob_custom_scores_extreme_theta(self):
        """Test prob() with custom scores at extreme theta values."""
        item = IRF(
            params={"a": 1.0, "b": 0.0},
            model="2PL",
            scores=[0, 100]
        )
        
        # Very low theta
        prob_low = item.prob(theta=-10.0)
        assert list(prob_low.columns) == ["0.0", "100.0"]
        assert prob_low.loc[-10.0, "0.0"] > 0.99  # Almost certainly score 0
        
        # Very high theta
        prob_high = item.prob(theta=10.0)
        assert list(prob_high.columns) == ["0.0", "100.0"]
        assert prob_high.loc[10.0, "100.0"] > 0.99  # Almost certainly score 100

    def test_prob_custom_scores_zero_scores(self):
        """Test prob() with all-zero custom scores."""
        item = IRF(
            params={"a": 1.0, "b": 0.0},
            model="2PL",
            scores=[0, 0]
        )
        prob = item.prob(theta=0.0)
        
        # Should still work, columns will be "0.0" for both
        assert prob.shape == (1, 2)
        assert np.isclose(prob.sum(axis=1).values[0], 1.0)

    def test_prob_custom_scores_large_values(self):
        """Test prob() with very large custom score values."""
        item = IRF(
            params={"a": 1.0, "b": [-0.5, 0.5]},
            model="GPCM",
            scores=[0, 1000, 10000]
        )
        prob = item.prob(theta=0.0)
        
        assert list(prob.columns) == ["0.0", "1000.0", "10000.0"]
        assert np.isclose(prob.sum(axis=1).values[0], 1.0)

    # ========================================================================
    # Tests for different IRT models with custom scores
    # ========================================================================

    def test_prob_rasch_custom_scores(self):
        """Test prob() with custom scores for Rasch model."""
        item = IRF(params={"b": 1.0}, model="Rasch", scores=[0, 3])
        prob = item.prob(theta=1.0)
        
        assert list(prob.columns) == ["0.0", "3.0"]
        assert np.isclose(prob.sum(axis=1).values[0], 1.0)

    def test_prob_1pl_custom_scores(self):
        """Test prob() with custom scores for 1PL model."""
        item = IRF(params={"a": 1.0, "b": 0.5}, model="1PL", scores=[0, 7])
        prob = item.prob(theta=0.5)
        
        assert list(prob.columns) == ["0.0", "7.0"]
        assert np.isclose(prob.sum(axis=1).values[0], 1.0)

    def test_prob_3pl_custom_scores(self):
        """Test prob() with custom scores for 3PL model."""
        item = IRF(
            params={"a": 1.5, "b": 0.0, "c": 0.2},
            model="3PL",
            scores=[0, 5]
        )
        prob = item.prob(theta=0.0)
        
        assert list(prob.columns) == ["0.0", "5.0"]
        assert np.isclose(prob.sum(axis=1).values[0], 1.0)

    def test_prob_gpcm2_custom_scores(self):
        """Test prob() with custom scores for GPCM2 model."""
        item = IRF(
            params={"a": 1.0, "b": 0.0, "threshold": [-0.5, 0.0, 0.5]},
            model="GPCM2",
            scores=[0, 2, 4, 6]
        )
        prob = item.prob(theta=0.0)
        
        assert list(prob.columns) == ["0.0", "2.0", "4.0", "6.0"]
        assert np.isclose(prob.sum(axis=1).values[0], 1.0)

    # ========================================================================
    # Tests for column name formatting
    # ========================================================================

    def test_prob_custom_scores_column_names_are_strings(self):
        """Test that column names are string representations of scores."""
        item = IRF(
            params={"a": 1.0, "b": [-0.5, 0.5]},
            model="GPCM",
            scores=[0, 2, 5]
        )
        prob = item.prob(theta=0.0)
        
        # All column names should be strings
        for col in prob.columns:
            assert isinstance(col, str)

    def test_prob_custom_scores_column_access(self):
        """Test that columns can be accessed by score string."""
        item = IRF(
            params={"a": 1.0, "b": 0.0},
            model="2PL",
            scores=[0, 10]
        )
        prob = item.prob(theta=0.0)
        
        # Should be able to access columns by string
        assert "0.0" in prob.columns
        assert "10.0" in prob.columns
        
        # Should be able to get values
        p0 = prob.loc[0.0, "0.0"]
        p10 = prob.loc[0.0, "10.0"]
        
        assert isinstance(p0, (float, np.floating))
        assert isinstance(p10, (float, np.floating))
        assert np.isclose(p0 + p10, 1.0)

    # ========================================================================
    # Tests for integration with expected_score
    # ========================================================================

    def test_expected_score_uses_custom_scores(self):
        """Test that expected_score() correctly uses custom scores from prob()."""
        item = IRF(
            params={"a": 1.0, "b": 0.0},
            model="2PL",
            scores=[0, 10]
        )
        
        # Get probabilities
        prob = item.prob(theta=0.0)
        p0 = prob.loc[0.0, "0.0"]
        p10 = prob.loc[0.0, "10.0"]
        
        # Manual calculation
        manual_expected = 0 * p0 + 10 * p10
        
        # Method calculation
        method_expected = item.expected_score(theta=0.0)
        
        # Should match
        assert np.isclose(manual_expected, method_expected)

    def test_expected_score_polytomous_custom_scores(self):
        """Test expected_score() with polytomous item and custom scores."""
        item = IRF(
            params={"a": 1.0, "b": [-0.5, 0.0, 0.5]},
            model="GPCM",
            scores=[0, 2, 5, 10]
        )
        
        theta = 0.0
        prob = item.prob(theta=theta)
        
        # Manual calculation
        manual_expected = sum(
            prob.loc[theta, str(float(score))] * score
            for score in [0, 2, 5, 10]
        )
        
        # Method calculation
        method_expected = item.expected_score(theta=theta)
        
        # Should match
        assert np.isclose(manual_expected, method_expected)

    # ========================================================================
    # Tests for multiple theta values with custom scores
    # ========================================================================

    def test_prob_custom_scores_monotonicity(self):
        """Test that probabilities change monotonically with theta for custom scores."""
        item = IRF(
            params={"a": 1.2, "b": 0.0},
            model="2PL",
            scores=[0, 5]
        )
        
        theta = np.array([-2, -1, 0, 1, 2])
        prob = item.prob(theta=theta)
        
        # Probability of higher score should increase with theta
        p_high = prob["5.0"].values
        assert np.all(np.diff(p_high) > 0)
        
        # Probability of lower score should decrease with theta
        p_low = prob["0.0"].values
        assert np.all(np.diff(p_low) < 0)

    def test_prob_custom_scores_large_theta_array(self):
        """Test prob() with custom scores and large theta array."""
        item = IRF(
            params={"a": 1.0, "b": [-0.5, 0.5]},
            model="GPCM",
            scores=[0, 3, 7]
        )
        
        theta = np.linspace(-3, 3, 100)
        prob = item.prob(theta=theta)
        
        # Check shape
        assert prob.shape == (100, 3)
        
        # Check columns
        assert list(prob.columns) == ["0.0", "3.0", "7.0"]
        
        # All rows should sum to 1
        assert np.allclose(prob.sum(axis=1).values, 1.0)

    # ========================================================================
    # Tests for error handling
    # ========================================================================

    def test_prob_custom_scores_wrong_length_raises_error(self):
        """Test that wrong-length custom scores raise ValueError during initialization."""
        with pytest.raises(ValueError, match="Length of scores"):
            IRF(
                params={"a": 1.0, "b": [-0.5, 0.0, 0.5]},
                model="GPCM",
                scores=[0, 1, 2]  # Should be length 4, not 3
            )

    def test_prob_2d_theta_raises_error_with_custom_scores(self):
        """Test that 2D theta array raises error even with custom scores."""
        item = IRF(
            params={"a": 1.0, "b": 0.0},
            model="2PL",
            scores=[0, 5]
        )
        
        theta_2d = np.array([[0, 1], [2, 3]])
        with pytest.raises(ValueError, match="1D array"):
            item.prob(theta=theta_2d)

    # ========================================================================
    # Tests for DataFrame properties
    # ========================================================================

    def test_prob_custom_scores_dataframe_index_name(self):
        """Test that DataFrame index is named 'theta' for array input."""
        item = IRF(
            params={"a": 1.0, "b": 0.0},
            model="2PL",
            scores=[0, 10]
        )
        
        theta = np.array([-1.0, 0.0, 1.0])
        prob = item.prob(theta=theta)
        
        assert prob.index.name == "theta"

    def test_prob_custom_scores_dataframe_dtypes(self):
        """Test that DataFrame has correct dtypes with custom scores."""
        item = IRF(
            params={"a": 1.0, "b": [-0.5, 0.5]},
            model="GPCM",
            scores=[0, 5, 10]
        )
        
        prob = item.prob(theta=np.array([0.0, 1.0]))
        
        # All columns should be numeric
        for col in prob.columns:
            assert np.issubdtype(prob[col].dtype, np.number)

    # ========================================================================
    # Tests for special score patterns
    # ========================================================================

    def test_prob_custom_scores_descending_order(self):
        """Test prob() with custom scores in descending order."""
        # Note: This tests that the implementation uses scores as labels,
        # not that it reorders them
        item = IRF(
            params={"a": 1.0, "b": [-0.5, 0.5]},
            model="GPCM",
            scores=[10, 5, 0]  # Descending
        )
        prob = item.prob(theta=0.0)
        
        # Columns should reflect the order of scores as provided
        assert list(prob.columns) == ["10.0", "5.0", "0.0"]
        assert np.isclose(prob.sum(axis=1).values[0], 1.0)

    def test_prob_custom_scores_with_duplicates_allowed_in_init(self):
        """Test that duplicate scores are allowed (though not recommended)."""
        # The implementation doesn't prevent duplicate scores
        item = IRF(
            params={"a": 1.0, "b": 0.0},
            model="2PL",
            scores=[1, 1]  # Duplicate scores
        )
        prob = item.prob(theta=0.0)
        
        # Both columns will have the same name
        assert prob.shape == (1, 2)
        assert np.isclose(prob.sum(axis=1).values[0], 1.0)

    def test_prob_custom_scores_integer_vs_float(self):
        """Test that integer scores are converted to float strings in columns."""
        item = IRF(
            params={"a": 1.0, "b": 0.0},
            model="2PL",
            scores=[0, 5]  # Integers
        )
        prob = item.prob(theta=0.0)
        
        # Columns should be float strings
        assert list(prob.columns) == ["0.0", "5.0"]
