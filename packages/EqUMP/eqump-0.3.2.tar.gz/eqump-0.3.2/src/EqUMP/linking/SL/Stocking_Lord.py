from typing import Dict, Hashable, Union, List, Literal, Tuple, Optional
import numpy as np
from scipy.optimize import minimize
from EqUMP.base import gauss_hermite_quadrature, fixed_point_quadrature, ItemCollection
from EqUMP.linking.helper import transform_items, validate_and_prepare_custom_quadrature

def stocking_lord_loss(
    items_new: ItemCollection,
    items_old: ItemCollection,
    common_new: List[Hashable],
    common_old: List[Hashable],
    A: float = 1.0,
    B: float = 0.0,
    nodes_new: Optional[np.ndarray] = None,
    weights_new: Optional[np.ndarray] = None,
    nodes_old: Optional[np.ndarray] = None,
    weights_old: Optional[np.ndarray] = None,
    symmetry: bool = True,
) -> float:
    # new -> old: transform new items to old scale
    items_new_t = transform_items(items_new, A, B, direction="to_old")
    
    # Extract common items
    items_new_t_common = [items_new_t[c] for c in common_new]
    items_old_common = [items_old[c] for c in common_old]
    
    diff1 = 0.0
    for x, w in zip(nodes_old, weights_old):
        x = float(x); w = float(w)
        
        # Compute TRF for transformed new items
        T_new_t = sum(item.expected_score(x) for item in items_new_t_common)
        
        # Compute TRF for old items
        T_old = sum(item.expected_score(x) for item in items_old_common)
        
        diff1 += pow((T_new_t - T_old), 2) * w
    
    S1 = float(np.sum(weights_old))
    loss1 = diff1 / S1
    
    # old -> new: transform old items to new scale
    items_old_t = transform_items(items_old, A, B, direction="to_new")
    
    items_new_common = [items_new[c] for c in common_new]
    items_old_t_common = [items_old_t[c] for c in common_old]
    
    diff2 = 0.0
    for x, w in zip(nodes_new, weights_new):
        x = float(x); w = float(w)
        
        # Compute TRF for new items
        T_new = sum(item.expected_score(x) for item in items_new_common)
        
        # Compute TRF for transformed old items
        T_old_t = sum(item.expected_score(x) for item in items_old_t_common)
        
        diff2 += pow((T_new - T_old_t), 2) * w
    
    S2 = float(np.sum(weights_new))
    
    loss2 = diff2 / S2

    if symmetry == True:
        output = float(loss1 + loss2)
    elif symmetry == False:
        output = float(loss1)

    return output

def stocking_lord(
    items_new: ItemCollection,
    items_old: ItemCollection,
    common_new: List[Hashable],
    common_old: List[Hashable],
    A0: float = 1.0,
    B0: float = 0.0,
    quadrature: Literal["gauss_hermite", "fixed_point", "custom"] = "gauss_hermite",
    nq: Optional[int] = 30,
    theta_range: Tuple[float, float] = (-4.0, 4.0),
    custom_quadrature: Optional[Dict[str, Union[np.ndarray, List[float]]]] = None,
    symmetry: bool = True,
) -> Tuple[float, float]:
    """
    Transform the IRT scale of the new test form to the old test form in common-item nonequivalent groups (CINEG) / nonequivalent groups with anchor test (NEAT) design. 
    Estimate scale linking coefficients using parameters of the common items.
    The Stocking-Lord method uses the test response function of common items.
    
    Parameters
    ----------
    items_new : ItemCollection
        Dictionary mapping item IDs to IRF objects for the new test form.
    items_old : ItemCollection
        Dictionary mapping item IDs to IRF objects for the old test form.
    common_new : List[Hashable]
        List of common item identifiers in the new test form.
    common_old : List[Hashable]
        List of common item identifiers in the old test form.
    A0 : float, optional
        Initial value of scaling coefficient (A) (default 1.0).
    B0 : float, optional
        Initial value of scaling coefficient (B) (default 0.0).
    quadrature : str, optional
        Method for numerical integration.
        One of {"gauss_hermite", "fixed_point", "custom"} (default "gauss_hermite").
    nq : int, optional
        Number of quadrature nodes (default 30). 
        Used if quadrature="gauss_hermite" or "fixed_point".
    theta_range : Tuple[float, float], optional
        Lower and upper bounds of the latent trait (default -4 to 4).
        Used if quadrature="fixed_point".
    custom_quadrature : Dict, optional
        Custom quadrature specification used if quadrature="custom".
        Expected keys: {
            "nodes_new", "weights_new", "nodes_old", "weights_old"
        }. Values may be sequences or numpy arrays. All arrays must be 1D, same length within each form, weights non-negative, and contain no NaNs/Inf.
    symmetry : bool, optional
        If True, the loss function considers both directions (new → old and old → new). 
        If False, the loss function considers only new → old.
    
    Returns
    -------
    Tuple[float, float]
        A : Slope of linear linking function
        B : Intercept of linear linking function
    
    References
    ----------
    Stocking, M., & Lord, F.M. (1983). Developing a common metric in item response theory. Applied Psychological Measurement, 7(2), 201-210. https://doi.org/10.1177/014662168300700208

    Examples
    --------
    >>> from EqUMP.base import IRF
    >>> # Create IRF objects for new form
    >>> items_new = {
    ...     1: IRF({"a": 1.2, "b": 0.5, "c": 0.2}, "3PL", D=1.7),
    ...     2: IRF({"a": 1.0, "b": -0.3, "c": 0.15}, "3PL", D=1.7),
    ... }
    >>> # Create IRF objects for old form
    >>> items_old = {
    ...     1: IRF({"a": 1.15, "b": 0.48, "c": 0.18}, "3PL", D=1.7),
    ...     2: IRF({"a": 0.95, "b": -0.28, "c": 0.14}, "3PL", D=1.7),
    ... }
    >>> A, B = stocking_lord(
    ...     items_new=items_new,
    ...     items_old=items_old,
    ...     common_new=[1, 2],
    ...     common_old=[1, 2],
    ...     quadrature="gauss_hermite",
    ...     nq=30,
    ...     symmetry=True
    ... )
    """
    if quadrature == "gauss_hermite":
        if nq is None:
            nq = 30
        nodes, weights = gauss_hermite_quadrature(nq=nq)
        nodes_new = nodes_old = nodes
        weights_new = weights_old = weights

    elif quadrature == "fixed_point":
        if nq is None:
            nq = 40
        nodes, weights = fixed_point_quadrature(nq=nq, theta_range=theta_range)
        nodes_new = nodes_old = nodes
        weights_new = weights_old = weights

    elif quadrature == "custom":
        if custom_quadrature is None:
            raise ValueError("custom_quadrature must be provided when quadrature='custom'.")
        nodes_new, weights_new, nodes_old, weights_old = validate_and_prepare_custom_quadrature(custom_quadrature)
    else:
        raise ValueError("quadrature must be one of {'gauss_hermite', 'fixed_point', 'custom' }.")
    
    def obj(v: Tuple[float, float]) -> float:
        return stocking_lord_loss(
            items_new=items_new,
            items_old=items_old,
            common_new=common_new,
            common_old=common_old,
            A=float(v[0]),
            B=float(v[1]),
            nodes_new=nodes_new,
            weights_new=weights_new,
            nodes_old=nodes_old,
            weights_old=weights_old,
            symmetry=symmetry,
        )

    res = minimize(obj, x0=([A0, B0]), method="BFGS",
                   options = {
                       "gtol": 1e-6,
                       "maxiter": 1000,
                       "eps": 1e-8  
                   })

    # output
    A, B = float(res.x[0]), float(res.x[1])
    output = A, B
    return output

if __name__ == "__main__":
    from EqUMP.base import IRF
    from EqUMP.tests.linking.helper import load_KIM_dichotomous_data
    
    # Load data (old format with model in dict)
    KIM_dic_param_new_raw, KIM_dic_param_old_raw = load_KIM_dichotomous_data()
    
    # Convert to IRF objects
    KIM_dic_items_new = {
        k: IRF(params={pk: pv for pk, pv in v.items() if pk != "model"}, 
               model=v["model"], D=1.7)
        for k, v in KIM_dic_param_new_raw.items()
    }
    KIM_dic_items_old = {
        k: IRF(params={pk: pv for pk, pv in v.items() if pk != "model"}, 
               model=v["model"], D=1.7)
        for k, v in KIM_dic_param_old_raw.items()
    }

    res2 = stocking_lord(
        items_new=KIM_dic_items_new,
        items_old=KIM_dic_items_old,
        common_new=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        common_old=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        quadrature="fixed_point",
        nq=31,
        symmetry=True,
    )
    print(res2)
    
    res3 = stocking_lord(
        items_new=KIM_dic_items_new,
        items_old=KIM_dic_items_old,
        common_new=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        common_old=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        quadrature="fixed_point",
        nq=31,
        symmetry=False,
    )   
    print(res3)

    from EqUMP.tests.linking.helper import load_KIM_polytomous_data
    KIM_poly_param_new_raw, KIM_poly_param_old_raw = load_KIM_polytomous_data()
    
    # Convert to IRF objects
    KIM_poly_items_new = {
        k: IRF(params={pk: pv for pk, pv in v.items() if pk != "model"}, 
               model=v["model"], D=1.7)
        for k, v in KIM_poly_param_new_raw.items()
    }
    KIM_poly_items_old = {
        k: IRF(params={pk: pv for pk, pv in v.items() if pk != "model"}, 
               model=v["model"], D=1.7)
        for k, v in KIM_poly_param_old_raw.items()
    }

    res4 = stocking_lord(
        items_new=KIM_poly_items_new,
        items_old=KIM_poly_items_old,
        common_new=[2, 5, 8, 11, 14, 17, 20],
        common_old=[2, 5, 8, 11, 14, 17, 20],
        quadrature="custom",
        custom_quadrature={
            "nodes_new": np.linspace(-4, 4, 25),
            "nodes_old": np.linspace(-4, 4, 25),
            "weights_new": [
                0.00005, 0.00018, 0.00058, 0.00162, 0.00407, 0.00909,
                0.01802, 0.03208, 0.05242, 0.07958, 0.10850, 0.12790,
                0.13530, 0.12830, 0.10380, 0.07739, 0.05391, 0.03367,
                0.01853, 0.00898, 0.00384, 0.00146, 0.00049, 0.00015,
                0.00004,
            ],
            "weights_old": [
                0.00005, 0.00018, 0.00058, 0.00162, 0.00400, 0.00882,
                0.01755, 0.03207, 0.05363, 0.08041, 0.10810, 0.13070,
                0.13850, 0.12570, 0.09952, 0.07580, 0.05455, 0.03494,
                0.01900, 0.00873, 0.00355, 0.00132, 0.00045, 0.00014,
                0.0004,
            ],
        },
        symmetry=True,
    )
    print(res4)

    res5 = stocking_lord(
        items_new=KIM_poly_items_new,
        items_old=KIM_poly_items_old,
        common_new=[2, 5, 8, 11, 14, 17, 20],
        common_old=[2, 5, 8, 11, 14, 17, 20],
        quadrature="custom",
        custom_quadrature={
            "nodes_new": np.linspace(-4, 4, 25),
            "nodes_old": np.linspace(-4, 4, 25),
            "weights_new": [
                0.00005, 0.00018, 0.00058, 0.00162, 0.00407, 0.00909,
                0.01802, 0.03208, 0.05242, 0.07958, 0.10850, 0.12790,
                0.13530, 0.12830, 0.10380, 0.07739, 0.05391, 0.03367,
                0.01853, 0.00898, 0.00384, 0.00146, 0.00049, 0.00015,
                0.00004,
            ],
            "weights_old": [
                0.00005, 0.00018, 0.00058, 0.00162, 0.00400, 0.00882,
                0.01755, 0.03207, 0.05363, 0.08041, 0.10810, 0.13070,
                0.13850, 0.12570, 0.09952, 0.07580, 0.05455, 0.03494,
                0.01900, 0.00873, 0.00355, 0.00132, 0.00045, 0.00014,
                0.0004,
            ],
        },
        symmetry=False,
    )
    print(res5)
