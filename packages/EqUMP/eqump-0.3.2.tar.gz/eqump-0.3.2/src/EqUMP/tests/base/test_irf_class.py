"""Comprehensive tests for the IRF class."""
import numpy as np
import pandas as pd
import pytest

# Use headless backend for matplotlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from EqUMP.base.irf import IRF


class TestIRFClass:
    """Test suite for the IRF class."""

    def test_irf_2pl_creation(self):
        """Test creating a 2PL IRF object."""
        item = IRF(params={"a": 1.2, "b": 0.5}, model="2PL")
        assert item.model == "2PL"
        assert item.params["a"] == 1.2
        assert item.params["b"] == 0.5
        assert item.D == 1.702
        assert item.n_categories == 2
        assert item.is_dichotomous is True
        assert np.array_equal(item.scores, np.array([0.0, 1.0]))

    def test_irf_3pl_creation(self):
        """Test creating a 3PL IRF object."""
        item = IRF(params={"a": 1.5, "b": -0.2, "c": 0.2}, model="3PL", item_id="Q1")
        assert item.model == "3PL"
        assert item.params["c"] == 0.2
        assert item.item_id == "Q1"

    def test_irf_rasch_creation(self):
        """Test creating a Rasch IRF object."""
        item = IRF(params={"b": 1.0}, model="Rasch")
        assert item.model == "RASCH"
        assert "b" in item.params
        assert item.n_categories == 2

    def test_irf_gpcm_creation(self):
        """Test creating a GPCM IRF object."""
        item = IRF(params={"a": 1.0, "b": [-0.5, 0.0, 0.5]}, model="GPCM")
        assert item.model == "GPCM"
        assert item.n_categories == 4
        assert item.is_dichotomous is False
        assert np.array_equal(item.scores, np.array([0.0, 1.0, 2.0, 3.0]))

    def test_irf_custom_scores_dichotomous(self):
        """Test custom scores for dichotomous item."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL", scores=[0, 2])
        assert np.array_equal(item.scores, np.array([0.0, 2.0]))

    def test_irf_custom_scores_polytomous(self):
        """Test custom scores for polytomous item."""
        item = IRF(
            params={"a": 1.0, "b": [-0.5, 0.0, 0.5]},
            model="GPCM",
            scores=[0, 2, 5, 10]
        )
        assert np.array_equal(item.scores, np.array([0.0, 2.0, 5.0, 10.0]))

    def test_irf_custom_scores_wrong_length(self):
        """Test that wrong-length custom scores raise ValueError."""
        with pytest.raises(ValueError, match="Length of scores"):
            IRF(
                params={"a": 1.0, "b": [-0.5, 0.0, 0.5]},
                model="GPCM",
                scores=[0, 1, 2]  # Should be length 4, not 3
            )

    def test_prob_single_theta(self):
        """Test prob() with single theta value."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        prob = item.prob(theta=0.0)
        assert isinstance(prob, pd.DataFrame)
        assert prob.shape == (1, 2)
        assert "0.0" in prob.columns and "1.0" in prob.columns
        # At theta=b=0, with a=1, D=1.702, should be close to 0.5
        assert 0.4 < prob.loc[0.0, "1.0"] < 0.6

    def test_prob_array_theta(self):
        """Test prob() with array of theta values."""
        item = IRF(params={"a": 1.2, "b": 0.5}, model="2PL")
        theta = np.array([-1.0, 0.0, 1.0])
        prob = item.prob(theta=theta)
        assert isinstance(prob, pd.DataFrame)
        assert prob.shape == (3, 2)
        assert np.array_equal(prob.index.values, theta)
        # Probabilities should be monotonically increasing with theta
        p1_vals = prob["1.0"].values
        assert np.all(np.diff(p1_vals) > 0)

    def test_prob_list_theta(self):
        """Test prob() with list of theta values."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        prob = item.prob(theta=[-2, -1, 0, 1, 2])
        assert prob.shape == (5, 2)

    def test_prob_polytomous(self):
        """Test prob() for polytomous item."""
        item = IRF(params={"a": 1.0, "b": [-0.5, 0.0, 0.5]}, model="GPCM")
        prob = item.prob(theta=0.0)
        assert prob.shape == (1, 4)
        assert list(prob.columns) == ["0.0", "1.0", "2.0", "3.0"]
        # Probabilities should sum to 1
        assert np.isclose(prob.sum(axis=1).values[0], 1.0)

    def test_expected_score_single_theta_default_scores(self):
        """Test expected_score() with single theta and default scores."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        e_score = item.expected_score(theta=0.0)
        assert isinstance(e_score, float)
        # Should be close to 0.5 for symmetric item at theta=b
        assert 0.4 < e_score < 0.6

    def test_expected_score_array_theta_default_scores(self):
        """Test expected_score() with array theta and default scores."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        theta = np.array([-2, -1, 0, 1, 2])
        e_scores = item.expected_score(theta=theta)
        assert isinstance(e_scores, np.ndarray)
        assert e_scores.shape == (5,)
        # Expected scores should increase with theta
        assert np.all(np.diff(e_scores) > 0)

    def test_expected_score_custom_scores(self):
        """Test expected_score() with custom scores."""
        item = IRF(
            params={"a": 1.0, "b": [-0.5, 0.0, 0.5]},
            model="GPCM",
            scores=[0, 2, 5, 10]
        )
        e_score = item.expected_score(theta=0.0)
        # Should be between 0 and 10
        assert 0 <= e_score <= 10
        # Exact value depends on probabilities, but should be reasonable
        assert 2 < e_score < 8

    def test_expected_score_polytomous_consistency(self):
        """Test that expected score matches manual calculation."""
        item = IRF(params={"a": 1.0, "b": [-0.5, 0.5]}, model="GPCM")
        theta = 0.0
        prob_df = item.prob(theta=theta)
        # Manual calculation: sum of prob * score
        manual_e_score = sum(
            prob_df.loc[theta, str(float(k))] * k 
            for k in range(3)
        )
        e_score = item.expected_score(theta=theta)
        assert np.isclose(e_score, manual_e_score)

    def test_plot_creates_figure(self):
        """Test that plot() creates a figure."""
        item = IRF(params={"a": 1.2, "b": 0.0}, model="2PL")
        ax = item.plot(show=False)
        assert ax is not None
        assert len(ax.lines) == 1
        plt.close('all')

    def test_plot_on_existing_axes(self):
        """Test plotting on existing axes."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        fig, ax = plt.subplots()
        result_ax = item.plot(ax=ax, show=False)
        assert result_ax is ax
        assert len(ax.lines) == 1
        plt.close('all')

    def test_plot_polytomous_all_categories(self):
        """Test plotting all categories for polytomous item."""
        item = IRF(params={"a": 1.0, "b": [-1.0, 0.0, 1.0]}, model="GPCM")
        ax = item.plot(show=False)
        # Should have 4 lines (4 categories)
        assert len(ax.lines) == 4
        plt.close('all')

    def test_plot_custom_theta_grid(self):
        """Test plotting with custom theta grid."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        theta_grid = np.linspace(-2, 2, 50)
        ax = item.plot(theta_grid=theta_grid, show=False)
        line = ax.lines[0]
        x_data = line.get_xdata()
        assert len(x_data) == 50
        assert x_data[0] == -2.0
        assert x_data[-1] == 2.0
        plt.close('all')

    def test_plot_styling_options(self):
        """Test that plot styling options work."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        ax = item.plot(
            show=False,
            color='red',
            linewidth=3,
            linestyle='--',
            alpha=0.5,
            title="Test Title",
            xlim=(-3, 3),
            ylim=(0, 1)
        )
        assert ax.get_title() == "Test Title"
        assert ax.get_xlim() == (-3.0, 3.0)
        assert ax.get_ylim() == (0.0, 1.0)
        plt.close('all')

    def test_summary_output(self):
        """Test that summary() returns a string."""
        item = IRF(
            params={"a": 1.2, "b": 0.5},
            model="2PL",
            item_id="Q1"
        )
        summary = item.summary()
        assert isinstance(summary, str)
        assert "Q1" in summary
        assert "2PL" in summary
        assert "1.2" in summary
        assert "0.5" in summary

    def test_repr(self):
        """Test __repr__ method."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL", item_id="Q1")
        repr_str = repr(item)
        assert "IRF" in repr_str
        assert "2PL" in repr_str
        assert "Q1" in repr_str

    def test_str(self):
        """Test __str__ method."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        str_output = str(item)
        assert "2PL" in str_output
        assert "1.0" in str_output

    def test_case_insensitive_model(self):
        """Test that model names are case-insensitive."""
        item1 = IRF(params={"a": 1.0, "b": 0.0}, model="2pl")
        item2 = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        item3 = IRF(params={"a": 1.0, "b": 0.0}, model="2Pl")
        assert item1.model == item2.model == item3.model == "2PL"

    def test_case_insensitive_params(self):
        """Test that parameter keys are normalized to lowercase."""
        item = IRF(params={"A": 1.0, "B": 0.0}, model="2PL")
        assert "a" in item.params
        assert "b" in item.params
        assert item.params["a"] == 1.0

    def test_invalid_model(self):
        """Test that invalid model raises error."""
        with pytest.raises(KeyError):
            IRF(params={"a": 1.0, "b": 0.0}, model="InvalidModel")

    def test_invalid_params_2pl(self):
        """Test that invalid parameters for 2PL raise error."""
        with pytest.raises(KeyError):
            IRF(params={"a": 1.0}, model="2PL")  # Missing b

    def test_invalid_params_3pl(self):
        """Test that invalid parameters for 3PL raise error."""
        with pytest.raises(KeyError):
            IRF(params={"a": 1.0, "b": 0.0}, model="3PL")  # Missing c

    def test_D_parameter(self):
        """Test custom D parameter."""
        item1 = IRF(params={"a": 1.0, "b": 0.0}, model="2PL", D=1.0)
        item2 = IRF(params={"a": 1.0, "b": 0.0}, model="2PL", D=1.702)
        assert item1.D == 1.0
        assert item2.D == 1.702
        # Different D values should give different probabilities
        p1 = item1.prob(theta=0.5)
        p2 = item2.prob(theta=0.5)
        assert not np.allclose(p1.values, p2.values)

    def test_grm_model(self):
        """Test GRM (Graded Response Model)."""
        item = IRF(params={"a": 1.5, "b": [-1.0, 0.0, 1.0]}, model="GRM")
        assert item.model == "GRM"
        assert item.n_categories == 4
        prob = item.prob(theta=0.0)
        assert prob.shape == (1, 4)
        # Probabilities should sum to 1
        assert np.isclose(prob.sum(axis=1).values[0], 1.0)

    def test_prob_2d_theta_raises_error(self):
        """Test that 2D theta array raises error."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        theta_2d = np.array([[0, 1], [2, 3]])
        with pytest.raises(ValueError, match="1D array"):
            item.prob(theta=theta_2d)

    def test_multiple_items_independent(self):
        """Test that multiple IRF instances are independent."""
        item1 = IRF(params={"a": 1.0, "b": 0.0}, model="2PL", item_id="Item1")
        item2 = IRF(params={"a": 1.5, "b": 0.5}, model="2PL", item_id="Item2")
        assert item1.params != item2.params
        assert item1.item_id != item2.item_id

    def test_extreme_theta_values(self):
        """Test IRF at extreme theta values."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        # Very low theta
        prob_low = item.prob(theta=-10.0)
        assert prob_low.loc[-10.0, "1.0"] < 0.01  # Probability of correct is very low
        # Very high theta
        prob_high = item.prob(theta=10.0)
        assert prob_high.loc[10.0, "1.0"] > 0.99  # Probability of correct is very high

    def test_expected_score_monotonicity(self):
        """Test that expected score increases monotonically with theta."""
        item = IRF(params={"a": 1.2, "b": 0.0}, model="2PL")
        theta_range = np.linspace(-3, 3, 50)
        e_scores = item.expected_score(theta=theta_range)
        # Check monotonicity
        assert np.all(np.diff(e_scores) >= 0)  # Allow for numerical precision

    def test_polytomous_category_probabilities_ordered(self):
        """Test that polytomous category probabilities behave reasonably."""
        item = IRF(params={"a": 1.0, "b": [-1.0, 0.0, 1.0]}, model="GPCM")
        # At low theta, lower categories should have higher probability
        prob_low = item.prob(theta=-3.0)
        assert prob_low.loc[-3.0, "0.0"] > prob_low.loc[-3.0, "3.0"]
        # At high theta, higher categories should have higher probability
        prob_high = item.prob(theta=3.0)
        assert prob_high.loc[3.0, "3.0"] > prob_high.loc[3.0, "0.0"]

    # ========================================================================
    # Tests for information() method
    # ========================================================================

    def test_information_2pl_single_theta(self):
        """Test information() for 2PL model with single theta."""
        item = IRF(params={"a": 1.2, "b": 0.0}, model="2PL")
        info = item.information(theta=0.0)
        assert isinstance(info, float)
        assert info > 0
        # At theta=b, 2PL info should be D^2 * a^2 * 0.25
        expected = (1.702 ** 2) * (1.2 ** 2) * 0.25
        assert np.isclose(info, expected, rtol=0.01)

    def test_information_2pl_array_theta(self):
        """Test information() for 2PL model with array theta."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        theta_arr = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
        info = item.information(theta=theta_arr)
        assert isinstance(info, np.ndarray)
        assert info.shape == (5,)
        assert np.all(info > 0)
        # Information should be symmetric around b=0
        assert np.isclose(info[0], info[4], rtol=0.01)
        assert np.isclose(info[1], info[3], rtol=0.01)

    def test_information_2pl_list_theta(self):
        """Test information() with list of theta values."""
        item = IRF(params={"a": 1.5, "b": 0.5}, model="2PL")
        info = item.information(theta=[-1, 0, 1, 2])
        assert isinstance(info, np.ndarray)
        assert info.shape == (4,)
        assert np.all(info > 0)

    def test_information_rasch_model(self):
        """Test information() for Rasch model."""
        item = IRF(params={"b": 1.0}, model="Rasch")
        info = item.information(theta=1.0)
        assert isinstance(info, float)
        assert info > 0
        # Rasch is 1PL with a=1, so info at theta=b should be D^2 * 1^2 * 0.25
        expected = (1.702 ** 2) * 0.25
        assert np.isclose(info, expected, rtol=0.01)

    def test_information_1pl_model(self):
        """Test information() for 1PL model."""
        item = IRF(params={"a": 1.0, "b": -0.5}, model="1PL")
        info = item.information(theta=-0.5)
        assert isinstance(info, float)
        assert info > 0

    def test_information_3pl_single_theta(self):
        """Test information() for 3PL model with single theta."""
        item = IRF(params={"a": 1.0, "b": 0.0, "c": 0.2}, model="3PL")
        info = item.information(theta=0.0)
        assert isinstance(info, float)
        assert info > 0

    def test_information_3pl_array_theta(self):
        """Test information() for 3PL model with array theta."""
        item = IRF(params={"a": 1.5, "b": 0.5, "c": 0.25}, model="3PL")
        theta_arr = np.array([-1.0, 0.0, 1.0, 2.0])
        info = item.information(theta=theta_arr)
        assert isinstance(info, np.ndarray)
        assert info.shape == (4,)
        assert np.all(info > 0)

    def test_information_3pl_vs_2pl(self):
        """Test that 3PL with c=0 gives same information as 2PL."""
        params_2pl = {"a": 1.2, "b": 0.5}
        params_3pl = {"a": 1.2, "b": 0.5, "c": 0.0}
        item_2pl = IRF(params=params_2pl, model="2PL")
        item_3pl = IRF(params=params_3pl, model="3PL")
        
        theta_arr = np.array([-1.0, 0.0, 1.0])
        info_2pl = item_2pl.information(theta=theta_arr)
        info_3pl = item_3pl.information(theta=theta_arr)
        
        # Should be very close when c=0
        assert np.allclose(info_2pl, info_3pl, rtol=0.01)

    def test_information_maximum_at_difficulty(self):
        """Test that 2PL information is maximum near difficulty parameter."""
        item = IRF(params={"a": 1.5, "b": 0.5}, model="2PL")
        # Test around b=0.5
        theta_range = np.linspace(-0.5, 1.5, 50)
        info = item.information(theta=theta_range)
        # Find maximum
        max_idx = np.argmax(info)
        max_theta = theta_range[max_idx]
        # Maximum should be close to b=0.5
        assert np.isclose(max_theta, 0.5, atol=0.1)

    def test_information_increases_with_discrimination(self):
        """Test that information increases with discrimination parameter."""
        item1 = IRF(params={"a": 0.5, "b": 0.0}, model="2PL")
        item2 = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        item3 = IRF(params={"a": 2.0, "b": 0.0}, model="2PL")
        
        theta = 0.0
        info1 = item1.information(theta=theta)
        info2 = item2.information(theta=theta)
        info3 = item3.information(theta=theta)
        
        # Higher discrimination should give more information
        assert info1 < info2 < info3

    def test_information_with_custom_D(self):
        """Test information() with custom D parameter."""
        item1 = IRF(params={"a": 1.0, "b": 0.0}, model="2PL", D=1.0)
        item2 = IRF(params={"a": 1.0, "b": 0.0}, model="2PL", D=1.702)
        
        # At theta = b, P(theta) = 0.5 regardless of D, so I(theta) scales exactly by D^2
        theta = 0.0  # theta = b
        info1 = item1.information(theta=theta)
        info2 = item2.information(theta=theta)
        
        # Different D values should give different information
        assert info1 != info2
        # At theta = b, the ratio should be exactly (D2/D1)^2
        assert np.isclose(info2 / info1, (1.702 / 1.0) ** 2, rtol=0.01)

    def test_information_extreme_theta_values(self):
        """Test information at extreme theta values."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        # At extreme theta, information should be very low
        info_low = item.information(theta=-10.0)
        info_high = item.information(theta=10.0)
        info_center = item.information(theta=0.0)
        
        assert info_low < info_center
        assert info_high < info_center
        # Information should approach zero at extremes
        assert info_low < 0.01
        assert info_high < 0.01

    def test_information_3pl_lower_than_2pl(self):
        """Test that 3PL information is lower than equivalent 2PL (when c > 0)."""
        params_2pl = {"a": 1.5, "b": 0.0}
        params_3pl = {"a": 1.5, "b": 0.0, "c": 0.2}
        item_2pl = IRF(params=params_2pl, model="2PL")
        item_3pl = IRF(params=params_3pl, model="3PL")
        
        theta = 0.0
        info_2pl = item_2pl.information(theta=theta)
        info_3pl = item_3pl.information(theta=theta)
        
        # 3PL with guessing provides less information
        assert info_3pl < info_2pl

    def test_information_polytomous_not_implemented(self):
        """Test that polytomous models raise NotImplementedError."""
        item_gpcm = IRF(params={"a": 1.0, "b": [-0.5, 0.0, 0.5]}, model="GPCM")
        item_grm = IRF(params={"a": 1.5, "b": [-1.0, 0.0, 1.0]}, model="GRM")
        item_gpcm2 = IRF(
            params={"a": 1.0, "b": 0.0, "threshold": [-0.5, 0.0, 0.5]},
            model="GPCM2"
        )
        
        with pytest.raises(ValueError, match="not implemented"):
            item_gpcm.information(theta=0.0)
        
        with pytest.raises(ValueError, match="not implemented"):
            item_grm.information(theta=0.0)
        
        with pytest.raises(ValueError, match="not implemented"):
            item_gpcm2.information(theta=0.0)

    def test_information_return_type_consistency(self):
        """Test that return type is consistent with input type."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        
        # Scalar input -> float output
        info_scalar = item.information(theta=0.0)
        assert isinstance(info_scalar, float)
        
        # List input -> ndarray output
        info_list = item.information(theta=[0.0])
        assert isinstance(info_list, np.ndarray)
        
        # Array input -> ndarray output
        info_array = item.information(theta=np.array([0.0]))
        assert isinstance(info_array, np.ndarray)

    def test_information_positive_values(self):
        """Test that information is always non-negative."""
        item = IRF(params={"a": 1.5, "b": 0.5, "c": 0.1}, model="3PL")
        theta_range = np.linspace(-5, 5, 100)
        info = item.information(theta=theta_range)
        
        # All information values should be non-negative
        assert np.all(info >= 0)

    def test_to_dict_2pl_basic(self):
        """Test to_dict() for basic 2PL model."""
        item = IRF(params={"a": 1.2, "b": 0.5}, model="2PL", item_id="Item1")
        data = item.to_dict()
        
        assert isinstance(data, dict)
        assert data["model"] == "2PL"
        assert data["params"]["a"] == 1.2
        assert data["params"]["b"] == 0.5
        assert data["D"] == 1.702
        assert data["scores"] == [0.0, 1.0]
        assert data["item_id"] == "Item1"

    def test_to_dict_3pl(self):
        """Test to_dict() for 3PL model."""
        item = IRF(params={"a": 1.5, "b": -0.2, "c": 0.25}, model="3PL", item_id="Q1")
        data = item.to_dict()
        
        assert data["model"] == "3PL"
        assert data["params"]["a"] == 1.5
        assert data["params"]["b"] == -0.2
        assert data["params"]["c"] == 0.25
        assert data["item_id"] == "Q1"

    def test_to_dict_rasch(self):
        """Test to_dict() for Rasch model."""
        item = IRF(params={"b": 1.0}, model="Rasch")
        data = item.to_dict()
        
        assert data["model"] == "RASCH"
        assert "b" in data["params"]
        assert data["params"]["b"] == 1.0

    def test_to_dict_gpcm_polytomous(self):
        """Test to_dict() for polytomous GPCM model."""
        item = IRF(params={"a": 1.0, "b": [-0.5, 0.0, 0.5]}, model="GPCM")
        data = item.to_dict()
        
        assert data["model"] == "GPCM"
        assert data["params"]["a"] == 1.0
        assert data["params"]["b"] == [-0.5, 0.0, 0.5]
        assert data["scores"] == [0.0, 1.0, 2.0, 3.0]

    def test_to_dict_custom_scores(self):
        """Test to_dict() with custom scores."""
        item = IRF(
            params={"a": 1.0, "b": [-0.5, 0.0, 0.5]},
            model="GPCM",
            scores=[0, 2, 5, 10]
        )
        data = item.to_dict()
        
        assert data["scores"] == [0.0, 2.0, 5.0, 10.0]

    def test_to_dict_custom_D(self):
        """Test to_dict() with custom D parameter."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL", D=1.0)
        data = item.to_dict()
        
        assert data["D"] == 1.0

    def test_to_dict_no_item_id(self):
        """Test to_dict() when item_id is None."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        data = item.to_dict()
        
        assert data["item_id"] is None

    def test_to_dict_numpy_array_conversion(self):
        """Test that numpy arrays in params are converted to lists."""
        # Create item with numpy array in params
        b_array = np.array([-0.5, 0.0, 0.5])
        item = IRF(params={"a": 1.0, "b": b_array}, model="GPCM")
        data = item.to_dict()
        
        # Check that b is now a list, not numpy array
        assert isinstance(data["params"]["b"], list)
        assert data["params"]["b"] == [-0.5, 0.0, 0.5]

    def test_from_dict_2pl_basic(self):
        """Test from_dict() for basic 2PL model."""
        data = {
            "model": "2PL",
            "params": {"a": 1.2, "b": 0.5},
            "D": 1.702,
            "scores": [0.0, 1.0],
            "item_id": "Item1"
        }
        item = IRF.from_dict(data)
        
        assert item.model == "2PL"
        assert item.params["a"] == 1.2
        assert item.params["b"] == 0.5
        assert item.D == 1.702
        assert np.array_equal(item.scores, np.array([0.0, 1.0]))
        assert item.item_id == "Item1"

    def test_from_dict_3pl(self):
        """Test from_dict() for 3PL model."""
        data = {
            "model": "3PL",
            "params": {"a": 1.5, "b": -0.2, "c": 0.25},
            "item_id": "Q1"
        }
        item = IRF.from_dict(data)
        
        assert item.model == "3PL"
        assert item.params["c"] == 0.25
        assert item.item_id == "Q1"

    def test_from_dict_minimal_data(self):
        """Test from_dict() with only required fields."""
        data = {
            "model": "2PL",
            "params": {"a": 1.0, "b": 0.0}
        }
        item = IRF.from_dict(data)
        
        assert item.model == "2PL"
        assert item.params["a"] == 1.0
        assert item.params["b"] == 0.0
        assert item.D == 1.702  # Default value
        assert item.item_id is None  # Default value

    def test_from_dict_gpcm_polytomous(self):
        """Test from_dict() for polytomous GPCM model."""
        data = {
            "model": "GPCM",
            "params": {"a": 1.0, "b": [-0.5, 0.0, 0.5]},
            "scores": [0.0, 1.0, 2.0, 3.0]
        }
        item = IRF.from_dict(data)
        
        assert item.model == "GPCM"
        assert item.n_categories == 4
        assert np.array_equal(item.scores, np.array([0.0, 1.0, 2.0, 3.0]))

    def test_from_dict_custom_D(self):
        """Test from_dict() with custom D parameter."""
        data = {
            "model": "2PL",
            "params": {"a": 1.0, "b": 0.0},
            "D": 1.0
        }
        item = IRF.from_dict(data)
        
        assert item.D == 1.0

    def test_from_dict_missing_model(self):
        """Test from_dict() raises KeyError when 'model' is missing."""
        data = {
            "params": {"a": 1.0, "b": 0.0}
        }
        with pytest.raises(KeyError, match="Missing required key: 'model'"):
            IRF.from_dict(data)

    def test_from_dict_missing_params(self):
        """Test from_dict() raises KeyError when 'params' is missing."""
        data = {
            "model": "2PL"
        }
        with pytest.raises(KeyError, match="Missing required key: 'params'"):
            IRF.from_dict(data)

    def test_to_dict_from_dict_roundtrip_2pl(self):
        """Test roundtrip: to_dict() -> from_dict() for 2PL."""
        original = IRF(params={"a": 1.2, "b": 0.5}, model="2PL", item_id="Item1")
        data = original.to_dict()
        restored = IRF.from_dict(data)
        
        assert original.model == restored.model
        assert original.params == restored.params
        assert original.D == restored.D
        assert np.array_equal(original.scores, restored.scores)
        assert original.item_id == restored.item_id

    def test_to_dict_from_dict_roundtrip_3pl(self):
        """Test roundtrip: to_dict() -> from_dict() for 3PL."""
        original = IRF(
            params={"a": 1.5, "b": -0.2, "c": 0.25},
            model="3PL",
            item_id="Q1",
            D=1.7
        )
        data = original.to_dict()
        restored = IRF.from_dict(data)
        
        assert original.model == restored.model
        assert original.params["c"] == restored.params["c"]
        assert original.D == restored.D
        assert original.item_id == restored.item_id

    def test_to_dict_from_dict_roundtrip_gpcm(self):
        """Test roundtrip: to_dict() -> from_dict() for GPCM."""
        original = IRF(
            params={"a": 1.0, "b": [-0.5, 0.0, 0.5]},
            model="GPCM",
            scores=[0, 2, 5, 10]
        )
        data = original.to_dict()
        restored = IRF.from_dict(data)
        
        assert original.model == restored.model
        assert np.array_equal(original.scores, restored.scores)
        # Check probabilities are the same
        theta = np.array([0.0, 1.0])
        prob_original = original.prob(theta=theta)
        prob_restored = restored.prob(theta=theta)
        assert np.allclose(prob_original.values, prob_restored.values)

    def test_to_json_creates_file(self, tmp_path):
        """Test to_json() creates a JSON file."""
        item = IRF(params={"a": 1.2, "b": 0.5}, model="2PL", item_id="Item1")
        filepath = tmp_path / "item_2pl.json"
        
        item.to_json(filepath)
        
        assert filepath.exists()
        assert filepath.is_file()

    def test_to_json_content_valid(self, tmp_path):
        """Test to_json() creates valid JSON content."""
        import json
        
        item = IRF(params={"a": 1.2, "b": 0.5}, model="2PL", item_id="Item1")
        filepath = tmp_path / "item_2pl.json"
        
        item.to_json(filepath)
        
        # Read and parse JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data["model"] == "2PL"
        assert data["params"]["a"] == 1.2
        assert data["params"]["b"] == 0.5
        assert data["item_id"] == "Item1"

    def test_to_json_pretty_formatting(self, tmp_path):
        """Test to_json() with pretty formatting."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        filepath = tmp_path / "item_pretty.json"
        
        item.to_json(filepath, pretty=True)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pretty JSON should have newlines and indentation
        assert '\n' in content
        assert '  ' in content  # Indentation

    def test_to_json_compact_formatting(self, tmp_path):
        """Test to_json() with compact formatting."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        filepath = tmp_path / "item_compact.json"
        
        item.to_json(filepath, pretty=False)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Compact JSON should be mostly on one line (minimal newlines)
        # Count newlines - should be fewer than pretty version
        assert content.count('\n') < 5

    def test_to_json_str_path(self, tmp_path):
        """Test to_json() accepts string path."""
        item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        filepath = str(tmp_path / "item.json")
        
        item.to_json(filepath)
        
        import os
        assert os.path.exists(filepath)

    def test_from_json_basic(self, tmp_path):
        """Test from_json() loads IRF object correctly."""
        import json
        
        # Create a JSON file
        data = {
            "model": "2PL",
            "params": {"a": 1.2, "b": 0.5},
            "D": 1.702,
            "scores": [0.0, 1.0],
            "item_id": "Item1"
        }
        filepath = tmp_path / "item.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        
        # Load IRF from JSON
        item = IRF.from_json(filepath)
        
        assert item.model == "2PL"
        assert item.params["a"] == 1.2
        assert item.params["b"] == 0.5
        assert item.item_id == "Item1"

    def test_from_json_str_path(self, tmp_path):
        """Test from_json() accepts string path."""
        import json
        
        data = {
            "model": "2PL",
            "params": {"a": 1.0, "b": 0.0}
        }
        filepath = tmp_path / "item.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        
        # Load with string path
        item = IRF.from_json(str(filepath))
        
        assert item.model == "2PL"

    def test_from_json_file_not_found(self, tmp_path):
        """Test from_json() raises FileNotFoundError for non-existent file."""
        filepath = tmp_path / "nonexistent.json"
        
        with pytest.raises(FileNotFoundError, match="File not found"):
            IRF.from_json(filepath)

    def test_from_json_invalid_json(self, tmp_path):
        """Test from_json() raises JSONDecodeError for invalid JSON."""
        import json
        
        filepath = tmp_path / "invalid.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("This is not valid JSON {{{")
        
        with pytest.raises(json.JSONDecodeError):
            IRF.from_json(filepath)

    def test_from_json_missing_required_keys(self, tmp_path):
        """Test from_json() raises KeyError for missing required keys."""
        import json
        
        # Missing 'model'
        data = {"params": {"a": 1.0, "b": 0.0}}
        filepath = tmp_path / "missing_model.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        
        with pytest.raises(KeyError, match="Missing required key: 'model'"):
            IRF.from_json(filepath)

    def test_to_json_from_json_roundtrip(self, tmp_path):
        """Test roundtrip: to_json() -> from_json()."""
        original = IRF(
            params={"a": 1.2, "b": 0.5},
            model="2PL",
            item_id="Item1",
            D=1.702
        )
        filepath = tmp_path / "roundtrip.json"
        
        # Save and load
        original.to_json(filepath)
        restored = IRF.from_json(filepath)
        
        # Verify all attributes match
        assert original.model == restored.model
        assert original.params == restored.params
        assert original.D == restored.D
        assert np.array_equal(original.scores, restored.scores)
        assert original.item_id == restored.item_id
        
        # Verify probabilities match
        theta = np.array([-1.0, 0.0, 1.0])
        prob_original = original.prob(theta=theta)
        prob_restored = restored.prob(theta=theta)
        assert np.allclose(prob_original.values, prob_restored.values)

    def test_to_json_from_json_roundtrip_gpcm(self, tmp_path):
        """Test roundtrip: to_json() -> from_json() for GPCM with custom scores."""
        original = IRF(
            params={"a": 1.0, "b": [-0.5, 0.0, 0.5]},
            model="GPCM",
            scores=[0, 2, 5, 10],
            item_id="PolyItem"
        )
        filepath = tmp_path / "gpcm_roundtrip.json"
        
        # Save and load
        original.to_json(filepath)
        restored = IRF.from_json(filepath)
        
        # Verify all attributes match
        assert original.model == restored.model
        assert np.array_equal(original.scores, restored.scores)
        assert original.item_id == restored.item_id
        
        # Verify expected scores match
        theta = np.array([0.0, 1.0, 2.0])
        e_score_original = original.expected_score(theta=theta)
        e_score_restored = restored.expected_score(theta=theta)
        assert np.allclose(e_score_original, e_score_restored)

    def test_serialization_preserves_functionality(self, tmp_path):
        """Test that serialization/deserialization preserves all functionality."""
        original = IRF(
            params={"a": 1.5, "b": -0.2, "c": 0.25},
            model="3PL",
            item_id="Q1"
        )
        filepath = tmp_path / "functional_test.json"
        
        # Save and load
        original.to_json(filepath)
        restored = IRF.from_json(filepath)
        
        # Test various methods produce same results
        theta = np.linspace(-3, 3, 20)
        
        # Test prob()
        prob_orig = original.prob(theta=theta)
        prob_rest = restored.prob(theta=theta)
        assert np.allclose(prob_orig.values, prob_rest.values)
        
        # Test expected_score()
        e_score_orig = original.expected_score(theta=theta)
        e_score_rest = restored.expected_score(theta=theta)
        assert np.allclose(e_score_orig, e_score_rest)
        
        # Test information()
        info_orig = original.information(theta=theta)
        info_rest = restored.information(theta=theta)
        assert np.allclose(info_orig, info_rest)
