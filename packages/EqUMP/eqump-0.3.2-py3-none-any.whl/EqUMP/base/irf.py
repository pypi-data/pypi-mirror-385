from typing import Dict, Union, Literal, Mapping, overload, get_args, Hashable
import warnings
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import expit

# Model type literals
DichotomousItemType = Literal["Rasch", "1PL", "2PL", "3PL"]
PolytomousItemType = Literal["GRM", "GPCM", "GPCM2"]
ItemModelType = Union[DichotomousItemType, PolytomousItemType]

# Parameter type aliases - semantic distinction between item types
DichotomousParams = Dict[str, float]
PolytomousParams = Dict[str, Union[float, list, np.ndarray]]
ItemParams = Union[DichotomousParams, PolytomousParams]

# More flexible type for initialization (accepts int in addition to float)
ItemParamsInit = Dict[str, Union[float, int, list, np.ndarray]]

# Type alias for collections of items (used in linking/equating functions)
# Maps item IDs (hashable keys) to their parameter dictionaries
ItemParamsCollection = Dict[Hashable, ItemParams]

# Type alias for collections of IRF objects (new API)
# Maps item IDs (hashable keys) to IRF objects
ItemCollection = Dict[Hashable, 'IRF']

@overload
def irf(
    theta: float,
    params: DichotomousParams,
    model: DichotomousItemType,
    D: float = 1.702,
) -> pd.DataFrame: ...
@overload
def irf(
    theta: float,
    params: PolytomousParams,
    model: PolytomousItemType,
    D: float = 1.702,
) -> pd.DataFrame: ...

def irf(
    theta: float,
    params: ItemParams,
    model: ItemModelType,
    D: float = 1.702,  # scaling constant
) -> pd.DataFrame:
    """
    Compute the Probability of correct response by Item Response Function (IRF) for various IRT models.

    Parameters
    ----------
    theta : float
        Latent trait value.
    params : dict
        Item parameters. Required keys depend on the model:
            - Rasch: {"b": float}
            - 1PL: {"a": float, "b": float}
            - 2PL: {"a": float, "b": float}
            - 3PL: {"a": float, "b": float, "c": float}
            - GRM: {"a": float, "b": list[float] or np.ndarray}
            - GPCM: {"a": float, "b": list[float] or np.ndarray}
            - GPCM2: {"a": float, "b": float, "threshold": list[float] or np.ndarray}
    model : str
        IRT model name. One of {ItemModelType}.
    D : float, optional
        Scaling constant (default: 1.702).

    Returns
    -------
    pd.DataFrame
        IRF probabilities. Rows: theta values; Columns: item categories.

    Examples
    --------
    >>> irf(theta=0.0, params={"b": 0.0}, model="Rasch")
    >>> irf(theta=0.5, params={"a": 1.5, "b": 0.2}, model="1PL")
    >>> irf(theta=-0.3, params={"a": 1.2, "b": 0.5}, model="2PL")
    >>> irf(theta=0.1, params={"a": 1.0, "b": 0.3, "c": 0.2}, model="3PL")
    >>> irf(theta=0.0, params={"a": 1.1, "b": [-0.74, 0.3, 0.91]}, model="GPCM")
    """
    _typecheck_irf(theta, params, model)
    model = model.upper()
    params = {k.lower(): v for k, v in params.items()}
    model_map = {
        "RASCH": irf_rasch,
        "1PL": irf_1pl,
        "2PL": irf_2pl,
        "3PL": irf_3pl,
        "GRM": irf_grm,
        "GPCM": irf_GPCM,
        "GPCM2": irf_GPCM2,
    }
    return model_map[model](theta, params, D)

def _typecheck_irf(theta, params, model):
    # theta check
    if not isinstance(theta, (float, int)):
        raise TypeError(f"`theta` must be a float. But got {type(theta)}")

    # params & theta check
    if not isinstance(params, (dict, Mapping)):
        raise TypeError(
            f"params must be a dict or dict-like mapping. But got {type(params)}"
        )
    if not all(isinstance(key, str) for key in params.keys()):
        raise TypeError("All keys in `params(dictionary, Mapping)` must be strings.")
    
    # model check
    # In Python 3.9, get_args on a Union of Literals returns the Literal objects
    # themselves, not the inner strings. Collect from each Literal separately.
    valid_models = {
        m.upper() for m in (
            *get_args(DichotomousItemType),
            *get_args(PolytomousItemType),
        )
    }
    if model.upper() not in valid_models: 
        raise KeyError(
            f"`model` must be one of {valid_models}, but got '{model}'. "
        )
    
    # model specific check
    model_map = {
        "RASCH": _typecheck_rasch,
        "1PL": _typecheck_1pl,
        "2PL": _typecheck_2pl,
        "3PL": _typecheck_3pl,
        "GRM": _typecheck_grm,
        "GPCM": _typecheck_GPCM,
        "GPCM2": _typecheck_GPCM2,
    }
    model_map[model.upper()](params)

    return None

def irf_rasch(theta: float, params: DichotomousParams, D: float) -> pd.DataFrame:

    # parameters
    theta = float(theta)
    a = 1.0
    b = float(params["b"])

    # compute probability
    z = D * a * (theta - b)
    prob = 1 / (1.0 + np.exp(-z))

    # output
    output = pd.DataFrame(
        np.column_stack([1 - prob, prob]), index=[theta], columns=["0", "1"]
    )
    return output

def _typecheck_rasch(params) -> None:
    if "b" not in params or len(params) != 1:
        raise KeyError(
            f"Rasch model requires only 'b' parameter. But got {list(params.keys())}"
        )
    if not all(isinstance(val, (float, int)) for val in params.values()):
        typedict = {val: type(val) for val in params.values()}
        raise TypeError(
            f"Rasch model parameters must be float or int. But got {typedict}"
        )
    return None

def irf_1pl(theta: float, params: DichotomousParams, D: float) -> pd.DataFrame:

    ## parameters
    theta = float(theta)
    a = float(params["a"])
    b = float(params["b"])

    # compute probability
    z = D * a * (theta - b)
    prob = 1 / (1.0 + np.exp(-z))

    # output
    output = pd.DataFrame(
        np.column_stack([1 - prob, prob]), index=[theta], columns=["0", "1"]
    )

    return output

def _typecheck_1pl(params) -> None:
    if "a" not in params or "b" not in params or len(params) != 2:
        raise KeyError(
            f"1PL model requires 'a' and 'b' parameters. But got {list(params.keys())}"
        )
    if not all(isinstance(val, (float, int)) for val in params.values()):
        typedict = {val: type(val) for val in params.values()}
        raise TypeError(
            f"1PL model parameters must be float or int. But got {typedict}"
        )
    return None

def irf_2pl(theta: float, params: DichotomousParams, D: float) -> pd.DataFrame:

    ## parameters
    theta = float(theta)
    a = float(params["a"])
    b = float(params["b"])

    # compute probability
    z = D * a * (theta - b)
    prob = 1 / (1.0 + np.exp(-z))

    # output
    output = pd.DataFrame(
        np.column_stack([1 - prob, prob]), index=[theta], columns=["0", "1"]
    )

    return output

def _typecheck_2pl(params) -> None:
    if "a" not in params or "b" not in params or len(params) != 2:
        raise KeyError(
            f"2PL model requires 'a' and 'b' parameters. But got {list(params.keys())}"
        )
    if not all(isinstance(val, (float, int)) for val in params.values()):
        typedict = {val: type(val) for val in params.values()}
        raise TypeError(
            f"2PL model parameters must be float or int. But got {typedict}"
        )
    return None

def irf_3pl(theta: float, params: DichotomousParams, D: float) -> pd.DataFrame:

    ## parameters
    theta = float(theta)
    a = float(params.get("a", 1.0))
    b = float(params["b"])
    c = float(params.get("c", 0.0))

    # compute probability
    z = D * a * (theta - b)
    prob = c + (1.0 - c) * expit(z)

    # output
    output = pd.DataFrame(
        np.column_stack([1 - prob, prob]), index=[theta], columns=["0", "1"]
    )
    return output

def _typecheck_3pl(params) -> None:
    if (
        "a" not in params
        or "b" not in params
        or "c" not in params
        or len(params) != 3
    ):
        raise KeyError(
            f"3PL model requires 'a', 'b', and 'c' parameters. But got {list(params.keys())}"
        )
    if not all(isinstance(val, (float, int)) for val in params.values()):
        typedict = {val: type(val) for val in params.values()}
        raise TypeError(
            f"3PL model parameters must be float or int. But got {typedict}"
        )
    return None

def irf_grm(
    theta: float, 
    params: PolytomousParams, 
    D: float
) -> pd.DataFrame:
    """item response function for Graded Response Model

    References
    ----------
    Samejima, F. (1969). Estimation of latent ability using a response pattern of graded scores. Psychometrika Monograph Supplement, 34(4, Pt. 2), 100.
    """
    _typecheck_grm(params)
    theta = float(theta)
    a = float(params["a"])
    b = np.asarray(params["b"], dtype=float) #thresholds

    if not np.all(b[:-1] <= b[1:]):
        warnings.warn(
            f"Threshold parameters 'b' should be in ascending order. "
            f"Got: {b}. Sorting automatically.",
            UserWarning
        )
        b = np.sort(b)

    if a <= 0:
        raise ValueError(f"Discrimination parameter 'a' must be positive. Got: {a}")
    
    z = D * a * (theta - b)

    # 수치 안정성을 위한 클리핑
    z = np.clip(z, -500, 500)
    """
    이미 z=-500이면 확률이 0.0에 극도로 가까움.
    z = 500이면 확률이 1.0에 극도로 가까움.
    """

    # Compute probability (cumulative probability)
    prob = 1 / (1.0 + np.exp(-z))
    cumulative_prob = np.concatenate(([1.0], prob, [0.0]))
    categorical_prob = cumulative_prob[:-1] - cumulative_prob[1:]

    # 음수 확률 체크 (수치 오차로 인한)
    if np.any(categorical_prob < 0):
        # 아주 작은 음수는 0으로 처리
        categorical_prob = np.maximum(categorical_prob, 0)
        # 정규화하여 합이 1이 되도록
        categorical_prob = categorical_prob / categorical_prob.sum()

    # Output
    total_categories = len(b) + 1
    output = pd.DataFrame(
        categorical_prob.reshape(1, total_categories),
        index=[theta],
        columns=[str(k) for k in range(total_categories)]
    )
    return output

def _typecheck_grm(params) -> None:
    """
    Raises
    ------
    KeyError:
        Graded Response Model requires 'a' and 'b' parameters.
    TypeError:
        Graded Response Model parameter 'a' must be float or int.
    ValueError:
        Graded Response Model parameter 'b' must be list or np.ndarray.
    """
    if "a" not in params or "b" not in params or len(params) != 2:
        raise KeyError(
            f"Graded Response Model requires 'a' and 'b' parameters. But got {list(params.keys())}"
        )
    if not isinstance(params["a"], (float, int)):
        raise TypeError(
            f"Graded Response Model parameter 'a' must be float or int. But got {type(params['a'])}"
        )
    if not isinstance(params["b"], (list, np.ndarray)):
        raise TypeError(
            f"Graded Response Model parameter 'b' must be list or np.ndarray. But got {type(params['b'])}"
        )
    return None

def irf_GPCM(
    theta: float, params: PolytomousParams, D: float
) -> pd.DataFrame:
    """

    References
    ----------
    Muraki, E. (1992), A GENERALIZED PARTIAL CREDIT MODEL: APPLICATION OF AN EM ALGORITHM. ETS Research Report Series, 1992: i-30. https://doi.org/10.1002/j.2333-8504.1992.tb01436.x
    """
    theta = float(theta)
    a = float(params.get("a", 1.0))
    b = np.asarray(params["b"], dtype=float)

    # compute probability
    b_full = np.concatenate(([0.0], b))
    z = np.cumsum(D * a * (theta - b_full))
    numerator = np.exp(z)
    denominator = np.sum(numerator)
    prob = numerator / denominator

    m = len(b_full)
    output = pd.DataFrame(
        prob.reshape(1, m), index=[theta], columns=[str(k) for k in range(m)]
    )
    return output

def irf_GPCM2(
    theta: float, params: PolytomousParams, D: float
) -> pd.DataFrame:
    theta = float(theta)
    a = float(params.get("a", 1.0))
    b_location = float(params["b"])

    # check validity of threshold, sum = 0
    if not np.isclose(np.sum(params["threshold"]), 0.0):
        raise ValueError(f"Thresholds must sum to 0. But got {np.sum(params['threshold'])}")

    b_location = b_location - np.array(params["threshold"])

    output = irf_GPCM(theta, {"a": a, "b": b_location}, D)
    return output

def _typecheck_GPCM(params) -> None:
    if "a" not in params or "b" not in params or len(params) != 2:
        raise KeyError(
            f"Generalized Partial Credit Model requires 'a' and 'b' parameters. But got {list(params.keys())}"
        )
    if not isinstance(params["a"], (float, int)):
        raise TypeError(
            f"Generalized Partial Credit Model parameter 'a' must be float or int. But got {type(params['a'])}"
        )
    if not isinstance(params["b"], (list, np.ndarray)):
        raise TypeError(
            f"Generalized Partial Credit Model parameter 'b' must be list or np.ndarray. But got {type(params['b'])}"
        )

    return None

def _typecheck_GPCM2(params) -> None:
    if "a" not in params or "b" not in params or "threshold" not in params:
        raise KeyError(
            f"Generalized Partial Credit Model2 requires 'a', 'b', and 'threshold' parameters. But got {list(params.keys())}"
        )
    if not isinstance(params["a"], (float, int)):
        raise TypeError(
            f"Generalized Partial Credit Model2 parameter 'a' must be float or int. But got {type(params['a'])}"
        )
    if not isinstance(params["b"], (float, int)):
        raise TypeError(
            f"Generalized Partial Credit Model2 parameter 'b' must be float or int. But got {type(params['b'])}"
        )
    if not isinstance(params["threshold"], (list, np.ndarray)):
        raise TypeError(
            f"Generalized Partial Credit Model2 parameter 'threshold' must be list or np.ndarray. But got {type(params['threshold'])}"
        )

    return None


# ============================================================================
# Class-based IRF Interface
# ============================================================================

class IRF:
    """
    Object-oriented interface for Item Response Functions.
    
    This class encapsulates item parameters, model type, and provides methods
    for computing probabilities, plotting, and managing item metadata.
    
    Parameters
    ----------
    params : dict
        Item parameters. Required keys depend on the model:
            - Rasch: {"b": float}
            - 1PL: {"a": float, "b": float}
            - 2PL: {"a": float, "b": float}
            - 3PL: {"a": float, "b": float, "c": float}
            - GRM: {"a": float, "b": list[float] or np.ndarray}
            - GPCM: {"a": float, "b": list[float] or np.ndarray}
            - GPCM2: {"a": float, "b": float, "threshold": list[float] or np.ndarray}
    model : str
        IRT model name. One of {"Rasch", "1PL", "2PL", "3PL", "GRM", "GPCM", "GPCM2"}.
    D : float, optional
        Scaling constant (default: 1.702).
    scores : list or np.ndarray, optional
        Score values for each category. If None:
            - Dichotomous: [0, 1]
            - Polytomous: [0, 1, 2, ..., K] where K is the number of categories
        Custom scores allow for non-sequential scoring (e.g., [0, 2, 5]).
    item_id : str or int, optional
        Item identifier for labeling and tracking.
    
    Attributes
    ----------
    params : dict
        Item parameters (normalized with lowercase keys).
    model : str
        Model name (uppercase).
    D : float
        Scaling constant.
    scores : np.ndarray
        Score values for each category.
    item_id : str or int or None
        Item identifier.
    n_categories : int
        Number of response categories.
    is_dichotomous : bool
        Whether the item is dichotomous (2 categories).
    
    Methods
    -------
    prob(theta)
        Compute response probabilities for given theta value(s).
    expected_score(theta)
        Compute expected score for given theta value(s).
    information(theta)
        Compute Fisher information for given theta value(s).
    plot(theta_grid=None, **kwargs)
        Plot item response function.
    summary()
        Print item summary information.
    
    Examples
    --------
    >>> # Dichotomous item
    >>> item_2pl = IRF(params={"a": 1.2, "b": 0.5}, model="2PL")
    >>> probs = item_2pl.prob(theta=0.0)
    >>> print(probs)
    
    >>> # Polytomous item with custom scores
    >>> item_gpcm = IRF(
    ...     params={"a": 1.0, "b": [-0.5, 0.0, 0.5]},
    ...     model="GPCM",
    ...     scores=[0, 2, 5, 10]
    ... )
    >>> expected = item_gpcm.expected_score(theta=0.0)

    Todo
    ----
    - Test Information
    """
    
    def __init__(
        self,
        params: ItemParamsInit,
        model: ItemModelType,
        D: float = 1.702,
        scores: Union[list, np.ndarray, None] = None,
        item_id: Union[str, int, None] = None,
    ):
        # Normalize parameters first (lowercase keys)
        normalized_params = {k.lower(): v for k, v in params.items()}
        
        # Validate with normalized parameters
        _typecheck_irf(0.0, normalized_params, model)  # Use dummy theta for validation
        
        self._model = model.upper()
        self.params = normalized_params
        self.D = float(D)
        self.item_id = item_id
        
        # Determine n_categories from model and parameters first
        model_n_categories = self._get_n_categories_from_model()
        
        # Handle scores
        if scores is None:
            self._n_categories = model_n_categories
            self.scores = np.arange(self._n_categories, dtype=float)
        else:
            scores_arr = np.asarray(scores, dtype=float)
            # Validate that scores length matches model-derived categories
            if len(scores_arr) != model_n_categories:
                raise ValueError(
                    f"Length of scores ({len(scores_arr)}) must match the number of "
                    f"categories derived from model parameters ({model_n_categories})."
                )
            self._n_categories = model_n_categories
            self.scores = scores_arr
        
        # Validate model-category consistency
        self._validate_model_category_consistency()
    
    @property
    def model(self) -> str:
        """Get the IRT model name (uppercase)."""
        return self._model
    
    @model.setter
    def model(self, value: str) -> None:
        """
        Set the IRT model name with validation.
        
        Parameters
        ----------
        value : str
            Model name (case-insensitive).
        
        Raises
        ------
        ValueError
            If the model is not compatible with the current number of categories.
        """
        new_model = value.upper()
        
        # Validate model name
        valid_models = {
            m.upper() for m in (
                *get_args(DichotomousItemType),
                *get_args(PolytomousItemType),
            )
        }
        if new_model not in valid_models:
            raise ValueError(
                f"Invalid model '{value}'. Must be one of {valid_models}"
            )
        
        self._model = new_model
        
        if hasattr(self, '_n_categories'): # re-validate consistency
            self._validate_model_category_consistency()
    
    @property
    def n_categories(self) -> int:
        """Get the number of response categories (read-only)."""
        return self._n_categories
    
    @property
    def is_dichotomous(self) -> bool:
        """Check if the item is dichotomous (2 categories)."""
        return self._n_categories == 2
    
    def _validate_model_category_consistency(self) -> None:
        """
        Validate that the model type is consistent with the number of categories.
        
        Raises
        ------
        ValueError
            If a dichotomous model is used with non-dichotomous data, or vice versa.
        """
        dichotomous_models = {"RASCH", "1PL", "2PL", "3PL"}
        polytomous_models = {"GRM", "GPCM", "GPCM2"}
        
        if self.is_dichotomous and self._model not in dichotomous_models:
            raise ValueError(
                f"Dichotomous items (2 categories) must use dichotomous models "
                f"({dichotomous_models}), but got '{self._model}'."
            )
        
        if not self.is_dichotomous and self._model in dichotomous_models:
            raise ValueError(
                f"Polytomous items ({self._n_categories} categories) cannot use "
                f"dichotomous models ({dichotomous_models}). Use polytomous models "
                f"({polytomous_models}) instead."
            )
    
    def _get_n_categories_from_model(self) -> int:
        """Determine number of response categories from model and parameters."""
        if self.model in ("RASCH", "1PL", "2PL", "3PL"):
            return 2
        elif self.model in ("GRM", "GPCM"):
            b = np.asarray(self.params["b"], dtype=float)
            return len(b) + 1
        elif self.model == "GPCM2":
            threshold = np.asarray(self.params["threshold"], dtype=float)
            return len(threshold) + 1
        else:
            raise ValueError(f"Unknown model: {self.model}")

    def prob(
        self,
        theta: Union[float, int, np.ndarray, list]
    ) -> pd.DataFrame:
        """
        Compute response probabilities for given theta value(s).
        
        Parameters
        ----------
        theta : float, int, np.ndarray, or list
            Ability value(s) at which to evaluate probabilities.
            - If scalar: returns single-row DataFrame
            - If array: returns multi-row DataFrame with theta as index
        
        Returns
        -------
        pd.DataFrame
            Response probabilities. Rows correspond to theta values (index),
            columns correspond to categories ("0", "1", ...).
        
        Examples
        --------
        >>> item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        >>> item.prob(0.0)  # Single theta
        >>> item.prob([−1, 0, 1])  # Multiple thetas
        """
        if np.isscalar(theta): # handle scalar theta
            default_df = irf(float(theta), self.params, self.model, self.D)
            default_df.columns = [str(sc) for sc in self.scores]
            return default_df
        
        theta_arr = np.asarray(theta, dtype=float)
        if theta_arr.ndim != 1:
            raise ValueError(f"theta must be 1D array, got shape {theta_arr.shape}")
        
        rows = []
        for th in theta_arr:
            default_df_row = irf(float(th), self.params, self.model, self.D)
            default_df_row.columns = [str(sc) for sc in self.scores]
            rows.append(default_df_row)
        
        df = pd.concat(rows, axis=0)
        df.index = theta_arr
        df.index.name = "theta"
        
        return df
    
    def expected_score(
        self,
        theta: Union[float, int, np.ndarray, list]
    ) -> Union[float, np.ndarray]:
        """
        Compute expected score for given theta value(s).
        
        The expected score is the sum of probabilities weighted by score values:
        E[X|theta] = sum_k P(X=k|theta) * score_k
        
        Parameters
        ----------
        theta : float, int, np.ndarray, or list
            Ability value(s) at which to evaluate expected score.
        
        Returns
        -------
        float or np.ndarray
            Expected score(s). If theta is scalar, returns float.
            If theta is array, returns array of same length.
        
        Examples
        --------
        >>> item = IRF(params={"a": 1.0, "b": 0.0}, model="2PL")
        >>> item.expected_score(0.0)
        0.5
        
        >>> item_custom = IRF(
        ...     params={"a": 1.0, "b": [−0.5, 0.5]},
        ...     model="GPCM",
        ...     scores=[0, 2, 5]
        ... )
        >>> item_custom.expected_score(0.0)
        """
        prob_df = self.prob(theta)
        
        # Compute expected score: sum of prob * score
        prob_values = prob_df.values  # Shape: (n_theta, n_categories)
        expected = prob_values @ self.scores  # Matrix-vector product
        
        # Return scalar if input was scalar
        if np.isscalar(theta):
            return float(expected[0])
        else:
            return expected
    
    def information(
        self,
        theta: Union[float, int, np.ndarray, list]
    ) -> Union[float, np.ndarray]:
        """
        Compute Fisher information for given theta value(s).
        
        Parameters
        ----------
        theta : float, int, np.ndarray, or list
            Ability value(s) at which to evaluate information.
        
        Returns
        -------
        float or np.ndarray
            Fisher information value(s). If theta is scalar, returns float.
            If theta is array, returns array of same length.
        
        Notes
        -----
        For dichotomous models (2PL, 3PL):
            - 2PL: I(θ) = D² * a² * P(θ) * (1 - P(θ))
            - 3PL: I(θ) = D² * a² * {(P(θ) - c)² / ((1 - c)²} * {Q(θ) / P(θ)}
        
        Examples
        --------
        >>> item = IRF(params={"a": 1.2, "b": 0.0}, model="2PL")
        >>> item.information(0.0)  # Single theta
        >>> item.information([−1, 0, 1])  # Multiple thetas

        Todo
        ----
        - implement polytomous models (GRM, GPCM, GPCM2):
        """
        is_scalar = np.isscalar(theta)
        theta_arr = np.atleast_1d(theta).astype(float)
        
        # Get probabilities
        prob_df = self.prob(theta_arr)
        
        if self.model in ("RASCH", "1PL", "2PL"):
            a = float(self.params.get("a", 1.0))
            p = prob_df[str(self.scores[1])].values  # P(X=1)
            q = 1.0 - p
            info = (self.D ** 2) * (a ** 2) * p * q
        
        elif self.model == "3PL":
            a = float(self.params["a"])
            c = float(self.params["c"])
            p = prob_df[str(self.scores[1])].values
            q = 1.0 - p
            
            numerator = (p - c) ** 2 * q
            denominator = ((1.0 - c) ** 2) * p
            
            denominator = np.maximum(denominator, 1e-10) # avoid division by zero
            info = (self.D ** 2) * (a ** 2) * (numerator / denominator)
        
        elif self.model in ("GRM", "GPCM", "GPCM2"):
            raise ValueError(f"Information not implemented for model: {self.model}")
            
        else:
            raise ValueError(f"Information not implemented for model: {self.model}")
        
        if is_scalar:
            return float(info[0])
        else:
            return info
    
    def plot(
        self,
        theta_grid: Union[np.ndarray, list, None] = None,
        ax=None,
        categories: Union[list, None] = None,
        show: bool = True,
        title: Union[str, None] = None,
        legend: bool = True,
        grid: bool = True,
        xlim: Union[tuple, None] = None,
        ylim: Union[tuple, None] = (0.0, 1.0),
        linewidth: float = 2.0,
        linestyle: str = "-",
        alpha: float = 1.0,
        color=None,
        label: Union[str, list, None] = None,
        **mpl_kwargs
    ):
        """
        Plot item response function.
        
        Parameters
        ----------
        theta_grid : array-like, optional
            Theta values for plotting. If None, uses np.arange(-6, 6.05, 0.05).
        ax : matplotlib.axes.Axes, optional
            Axes to plot on. If None, creates new figure.
        categories : list, optional
            Which categories to plot. For dichotomous items, defaults to ["1"]
            (probability of correct response). For polytomous, plots all categories.
        show : bool
            Whether to call plt.show() (only if ax is None).
        title : str, optional
            Plot title. Defaults to "IRF - {model} - Item {item_id}".
        legend : bool
            Whether to show legend.
        grid : bool
            Whether to show grid.
        xlim, ylim : tuple, optional
            Axis limits.
        linewidth, linestyle, alpha : float/str
            Line styling parameters.
        color : color specification or list, optional
            Line color(s).
        label : str or list, optional
            Label(s) for legend.
        **mpl_kwargs
            Additional arguments passed to matplotlib plot().
        
        Returns
        -------
        matplotlib.axes.Axes
            The axes object.
        
        Examples
        --------
        >>> item = IRF(params={"a": 1.2, "b": 0.0}, model="2PL")
        >>> item.plot()
        
        >>> # Custom theta range and styling
        >>> item.plot(theta_grid=np.linspace(-3, 3, 100), linewidth=3)
        """
        import matplotlib.pyplot as plt
        
        # Default theta grid
        if theta_grid is None:
            theta_grid = np.arange(-6.0, 6.05, 0.05)
        
        theta_arr = np.asarray(theta_grid, dtype=float)
        
        # Compute probabilities
        prob_df = self.prob(theta_arr)
        
        # Create or use existing axes
        created_ax = False
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 6))
            created_ax = True
        
        # Determine which categories to plot
        if categories is None:
            if self.is_dichotomous:
                selected_cols = [str(self.scores[1])]  # P(correct)
            else:
                selected_cols = [str(sc) for sc in self.scores]
        else:
            selected_cols = [str(c) for c in categories]
            for col in selected_cols:
                if col not in prob_df.columns:
                    raise ValueError(
                        f"Category {col!r} not found. "
                        f"Available: {list(prob_df.columns)}"
                    )
        
        # Prepare labels
        if label is None:
            if self.is_dichotomous and selected_cols == [str(self.scores[1])]:
                labels = [f"P(X={self.scores[1]})"]
            else:
                labels = [f"Category {c}" for c in selected_cols]
        else:
            if isinstance(label, str):
                labels = [label] * len(selected_cols)
            else:
                labels = list(label)
                if len(labels) != len(selected_cols):
                    raise ValueError(
                        f"Length of label ({len(labels)}) must match "
                        f"number of selected categories ({len(selected_cols)})"
                    )
        
        # Prepare colors
        if color is None:
            colors = [None] * len(selected_cols)
        else:
            if isinstance(color, (str, tuple)):
                colors = [color] * len(selected_cols)
            else:
                colors = list(color)
                if len(colors) != len(selected_cols):
                    raise ValueError(
                        f"Length of color ({len(colors)}) must match "
                        f"number of selected categories ({len(selected_cols)})"
                    )
        
        # Plot each category
        x = prob_df.index.values
        for i, col in enumerate(selected_cols):
            y = prob_df[col].values
            y_plot = np.clip(y, 0.0, 1.0)  # Clip for numerical stability
            
            ax.plot(
                x, y_plot,
                label=labels[i],
                color=colors[i],
                linewidth=linewidth,
                linestyle=linestyle,
                alpha=alpha,
                **mpl_kwargs
            )
        
        # Styling
        ax.set_xlabel("Theta (θ)")
        ax.set_ylabel("Probability")
        
        if title is None:
            if self.item_id is not None:
                title = f"IRF - {self.model} - Item {self.item_id}"
            else:
                title = f"IRF - {self.model}"
        ax.set_title(title)
        
        if grid:
            ax.grid(True, linestyle="--", alpha=0.4)
        
        if xlim is not None:
            ax.set_xlim(*xlim)
        if ylim is not None:
            ax.set_ylim(*ylim)
        
        if legend and (len(selected_cols) > 1 or labels[0] is not None):
            ax.legend()
        
        if created_ax and show:
            plt.show()
        
        return ax
    
    def summary(self) -> str:
        """
        Return a text summary of the item.
        
        Returns
        -------
        str
            Summary string containing model, parameters, and metadata.
        
        Examples
        --------
        >>> item = IRF(params={"a": 1.2, "b": 0.5}, model="2PL", item_id="Item1")
        >>> print(item.summary())
        """
        lines = []
        lines.append("=" * 60)
        if self.item_id is not None:
            lines.append(f"Item: {self.item_id}")
        lines.append(f"Model: {self.model}")
        lines.append(f"D (scaling constant): {self.D}")
        lines.append(f"Number of categories: {self.n_categories}")
        lines.append(f"Scores: {self.scores.tolist()}")
        lines.append("-" * 60)
        lines.append("Parameters:")
        for key, val in self.params.items():
            if isinstance(val, np.ndarray):
                lines.append(f"  {key}: {val.tolist()}")
            else:
                lines.append(f"  {key}: {val}")
        lines.append("=" * 60)
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        """String representation for interactive use."""
        id_str = f", item_id={self.item_id!r}" if self.item_id else ""
        return f"IRF(model={self.model!r}, D={self.D}{id_str})"
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        return self.summary()
    
    def to_dict(self) -> dict:
        """
        Convert IRF object to a JSON-serializable dictionary.
        
        Returns
        -------
        dict
            Dictionary containing all necessary data to reconstruct the IRF object.
            NumPy arrays are converted to lists for JSON compatibility.
        
        Examples
        --------
        >>> item = IRF(params={"a": 1.2, "b": 0.5}, model="2PL", item_id="Item1")
        >>> data = item.to_dict()
        >>> print(data)
        {'model': '2PL', 'params': {'a': 1.2, 'b': 0.5}, 'D': 1.702, 
         'scores': [0.0, 1.0], 'item_id': 'Item1'}
        """
        # Convert params, handling numpy arrays
        serializable_params = {}
        for key, value in self.params.items():
            if isinstance(value, np.ndarray):
                serializable_params[key] = value.tolist()
            else:
                serializable_params[key] = value
        
        data = {
            "model": self.model,
            "params": serializable_params,
            "D": self.D,
            "scores": self.scores.tolist(),
            "item_id": self.item_id,
        }
        
        return data
    
    def to_json(self, filepath: Union[str, Path], pretty: bool = True) -> None:
        """
        Save IRF object to a JSON file.
        
        Parameters
        ----------
        filepath : str or Path
            Path to the output JSON file.
        pretty : bool, optional
            If True, format JSON with indentation for readability (default: True).
        
        Examples
        --------
        >>> item = IRF(params={"a": 1.2, "b": 0.5}, model="2PL")
        >>> item.to_json("item_2pl.json")
        
        >>> # Save without pretty printing
        >>> item.to_json("item_compact.json", pretty=False)
        """
        filepath = Path(filepath)
        data = self.to_dict()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'IRF':
        """
        Create an IRF object from a dictionary.
        
        Parameters
        ----------
        data : dict
            Dictionary containing IRF data. Must include 'model' and 'params'.
            Optional keys: 'D', 'scores', 'item_id'.
        
        Returns
        -------
        IRF
            Reconstructed IRF object.
        
        Raises
        ------
        KeyError
            If required keys ('model', 'params') are missing.
        ValueError
            If data is invalid or inconsistent.
        
        Examples
        --------
        >>> data = {
        ...     "model": "2PL",
        ...     "params": {"a": 1.2, "b": 0.5},
        ...     "D": 1.702,
        ...     "scores": [0.0, 1.0],
        ...     "item_id": "Item1"
        ... }
        >>> item = IRF.from_dict(data)
        """
        # Validate required keys
        if "model" not in data:
            raise KeyError("Missing required key: 'model'")
        if "params" not in data:
            raise KeyError("Missing required key: 'params'")
        
        # Extract data with defaults
        model = data["model"]
        params = data["params"]
        D = data.get("D", 1.702)
        scores = data.get("scores", None)  # Will use default if None
        item_id = data.get("item_id", None)
        
        # Create IRF object (validation happens in __init__)
        return cls(
            params=params,
            model=model,
            D=D,
            scores=scores,
            item_id=item_id
        )
    
    @classmethod
    def from_json(cls, filepath: Union[str, Path]) -> 'IRF':
        """
        Load an IRF object from a JSON file.
        
        Parameters
        ----------
        filepath : str or Path
            Path to the JSON file.
        
        Returns
        -------
        IRF
            Loaded IRF object.
        
        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        json.JSONDecodeError
            If the file is not valid JSON.
        KeyError
            If required keys are missing.
        
        Examples
        --------
        >>> item = IRF.from_json("item_2pl.json")
        >>> print(item.summary())
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
