from typing import Dict, Hashable, Union, List, Literal, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import root_scalar
from EqUMP.base import ItemCollection

def tse_bound(
    items: ItemCollection,
) -> Tuple[float, float]:
    """
    Calculate the lower and upper bounds for true scores.
    
    Parameters
    ----------
    items : ItemCollection
        Dictionary mapping item IDs to IRF objects.
    
    Returns
    -------
    Tuple[float, float]
        Lower and upper bounds for true scores.
    """
    lower = sum(float(item.params.get("c", 0.0)) for item in items.values())
    upper = sum(item.n_categories - 1 for item in items.values())
    
    return lower, upper

def tse_loss(
    ts: float,
    items: ItemCollection,
    theta: float = 0.0,
) -> float:
    """
    Compute the difference between target score and true score at theta.
    
    Parameters
    ----------
    ts : float
        Target test score.
    items : ItemCollection
        Dictionary mapping item IDs to IRF objects.
    theta : float
        Ability level.
    
    Returns
    -------
    float
        Difference between target score and true score.
    """
    T = sum(item.expected_score(theta) for item in items.values())
    return ts - T

def tse(
    ts: float,
    items_new: ItemCollection,
    items_old: ItemCollection,
    common_new: List[Hashable],
    common_old: List[Hashable],
    theta: float = 0.0,
    anchor: Literal["internal", "external"] = "internal"
) -> Tuple[float, float]:
    """
    Performs true score equating of the new test form to the old test form under a common-item nonequivalent groups (CINEG) / nonequivalent groups with anchor test (NEAT) design. 
    Calculate the latent trait level and the true score on the old test form that corresponds to a given score on the new form.

    Parameters
    ----------
    ts : float
        Test score on the new test form.
    items_new : ItemCollection
        Dictionary mapping item IDs to IRF objects for the new test form.
    items_old : ItemCollection
        Dictionary mapping item IDs to IRF objects for the old test form.
    common_new : List[Hashable]
        Common item identifiers in the new test form.
    common_old : List[Hashable]
        Common item identifiers in the old test form.
    theta : float, optional
        Initial value of theta (not used in current implementation).
    anchor : Literal["internal", "external"], optional
        Anchor type:
        - "internal": Include anchor items in equating
        - "external": Exclude anchor items from equating

    Returns
    -------
    Tuple[float, float]
        theta_updated : Estimated theta value corresponding to the test score
        T_old : Equivalent true score on the old test form

    Examples
    --------
    >>> from EqUMP.base import IRF
    >>> # Create IRF objects for new form
    >>> items_new = {
    ...     0: IRF({"a": 1.2, "b": -0.5}, "2PL"),
    ...     1: IRF({"a": 1.0, "b": 0.0}, "2PL"),
    ...     2: IRF({"a": 1.5, "b": 0.8}, "2PL"),
    ...     3: IRF({"a": 0.9, "b": -1.2}, "2PL")
    ... }
    >>> # Create IRF objects for old form
    >>> items_old = {
    ...     0: IRF({"a": 1.15, "b": -0.47}, "2PL"),
    ...     1: IRF({"a": 0.95, "b": 0.05}, "2PL"),
    ...     2: IRF({"a": 1.45, "b": 0.85}, "2PL"),
    ...     3: IRF({"a": 0.85, "b": -1.15}, "2PL")
    ... }
    >>> # Common items are items 0, 1, 2
    >>> common_new = [0, 1, 2]
    >>> common_old = [0, 1, 2]
    >>> # Equate a test score of 2.5 on the new form
    >>> theta_eq, score_old = tse(
    ...     ts=2.5,
    ...     items_new=items_new,
    ...     items_old=items_old,
    ...     common_new=common_new,
    ...     common_old=common_old,
    ...     anchor="internal"
    ... )
    """
    # Filter items based on anchor type
    if anchor == "external":
        items_new_filtered = {k: v for k, v in items_new.items() if k not in common_new}
        items_old_filtered = {k: v for k, v in items_old.items() if k not in common_old}
    else:
        items_new_filtered = items_new
        items_old_filtered = items_old

    def obj(v: float) -> float:
        return tse_loss(ts=ts, items=items_new_filtered, theta=v)
    
    res = root_scalar(obj, bracket=[-10.0, 10.0], method='brentq', xtol=1e-7)
    theta_updated = float(res.root)
    
    # Compute true score on old form at estimated theta
    T_old = sum(item.expected_score(theta_updated) for item in items_old_filtered.values())
    
    return theta_updated, T_old
