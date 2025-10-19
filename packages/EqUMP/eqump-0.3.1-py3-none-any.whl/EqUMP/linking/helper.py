import numpy as np
from typing import Hashable, Dict, Union, Literal, Tuple, List
from EqUMP.base.irf import ItemParamsCollection, IRF, ItemCollection

def transform_item_params(
    params: ItemParamsCollection,
    A: float = 1.0,
    B: float = 0.0,
    direction: Literal["to_old", "to_new"] = "to_old",
) -> ItemParamsCollection:
    """
    Transform the IRT scale according to the linking coefficient A, B.

    Parameters
    ----------
    params : Dict
        Item parameters for the new/old test form.
        - "a": discrimination parameter
        - "b":
            Dichotomous: difficulty parameter
            Polytomous: step difficulties parameter
        - "c": pseudo-guessing parameter
    A/B: float
        Linking coefficients.
    direction: {"to_old", "to_new"}, optional
        to_old: transform item parameters of the new test form to the old test form
        to_new: transform item parameters of the old test form to the new test form

    Returns
    -------
    Dict[item_id -> {'a': float, 'b': float|np.ndarray, 'c': float}]
    """

    output: ItemParamsCollection = {}

    if direction == "to_old":
        for key, par in params.items():
            a = float(par["a"])
            b = np.asarray(par["b"], dtype=float)

            a_t = a / A
            b_t = A * b + B
            b_t = float(b_t) if b_t.shape == () else b_t

            item = {"a": a_t, "b": b_t}
            if "c" in par:
                item["c"] = float(par["c"])

            output[key] = item

    elif direction == "to_new":
        for key, par in params.items():
            a = float(par["a"])
            b = np.asarray(par["b"], dtype=float)

            a_t = A * a
            b_t = (b - B) / A
            b_t = float(b_t) if b_t.shape == () else b_t

            item = {"a": a_t, "b": b_t}
            if "c" in par:
                item["c"] = float(par["c"])

            output[key] = item
    return output

def transform_items(
    items: ItemCollection,
    A: float = 1.0,
    B: float = 0.0,
    direction: Literal["to_old", "to_new"] = "to_old",
) -> ItemCollection:
    """
    Transform IRF items according to linking coefficients A, B.
    
    Parameters
    ----------
    items : ItemCollection
        Dictionary of IRF objects to transform.
    A : float
        Slope of linear linking function.
    B : float
        Intercept of linear linking function.
    direction : {"to_old", "to_new"}
        Direction of transformation.
        - "to_old": transform new form to old form scale
        - "to_new": transform old form to new form scale
    
    Returns
    -------
    ItemCollection
        Dictionary of transformed IRF objects.
    
    Examples
    --------
    >>> items = {1: IRF({"a": 1.0, "b": 0.5}, "2PL")}
    >>> items_t = transform_items(items, A=1.2, B=0.3, direction="to_old")
    """
    # Extract params, transform, rebuild IRF objects
    params = {k: v.params for k, v in items.items()}
    params_transformed = transform_item_params(params, A, B, direction)
    
    items_transformed = {
        k: IRF(
            params=params_transformed[k],
            model=items[k].model,
            D=items[k].D,
            scores=items[k].scores,
            item_id=items[k].item_id
        )
        for k in items.keys()
    }
    
    return items_transformed


def validate_and_prepare_custom_quadrature(
    custom_quadrature: Dict[str, Union[np.ndarray, List[float]]]
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Validate and prepare custom quadrature inputs for linking methods.

    Parameters
    ----------
    custom_quadrature : Dict
        Expected keys: {"nodes_new", "weights_new", "nodes_old", "weights_old"}
        Values may be sequences or numpy arrays.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
        nodes_new, weights_new, nodes_old, weights_old

    Notes
    -----
    - Ensures arrays are 1D float numpy arrays with finite values
    - Ensures matching lengths within each form
    - Ensures non-negative weights
    - Sorts node-weight pairs by nodes for stability if unsorted
    """
    if custom_quadrature is None:
        raise ValueError("custom_quadrature must be provided when quadrature='custom'.")

    required_keys = {"nodes_new", "weights_new", "nodes_old", "weights_old"}
    missing = required_keys.difference(custom_quadrature.keys())
    if missing:
        raise ValueError(f"custom_quadrature is missing required keys: {sorted(missing)}")

    nodes_new = np.asarray(custom_quadrature["nodes_new"], dtype=float)
    nodes_old = np.asarray(custom_quadrature["nodes_old"], dtype=float)
    weights_new = np.asarray(custom_quadrature["weights_new"], dtype=float)
    weights_old = np.asarray(custom_quadrature["weights_old"], dtype=float)

    for name, arr in (
        ("nodes_new", nodes_new),
        ("nodes_old", nodes_old),
        ("weights_new", weights_new),
        ("weights_old", weights_old),
    ):
        if arr.ndim != 1:
            raise ValueError(f"{name} must be a 1D array.")
        if not np.all(np.isfinite(arr)):
            raise ValueError(f"{name} contains non-finite values.")

    if len(nodes_new) != len(weights_new):
        raise ValueError("Length mismatch: nodes_new and weights_new must have the same length.")
    if len(nodes_old) != len(weights_old):
        raise ValueError("Length mismatch: nodes_old and weights_old must have the same length.")
    if len(nodes_new) == 0 or len(nodes_old) == 0:
        raise ValueError("Custom quadrature arrays must be non-empty.")
    if np.any(weights_new < 0.0) or np.any(weights_old < 0.0):
        raise ValueError("Quadrature weights must be non-negative.")

    # Sort pairs together if nodes are not sorted (stability)
    if not (np.all(np.diff(nodes_new) >= 0)):
        idx_new = np.argsort(nodes_new)
        nodes_new = nodes_new[idx_new]
        weights_new = weights_new[idx_new]
    if not (np.all(np.diff(nodes_old) >= 0)):
        idx_old = np.argsort(nodes_old)
        nodes_old = nodes_old[idx_old]
        weights_old = weights_old[idx_old]

    return nodes_new, weights_new, nodes_old, weights_old

class SLResult:
    def plot(self):
        """plot linking result, 
        - transformed anchor items ICC,
        - transformed TCC
        """
        pass

    def summary(self):
        """_summary_
        """        
        pass