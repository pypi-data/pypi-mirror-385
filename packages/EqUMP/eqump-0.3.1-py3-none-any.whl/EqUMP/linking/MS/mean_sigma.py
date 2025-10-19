import numpy as np
from typing import Hashable, List, Tuple
from EqUMP.base import ItemCollection


def mean_sigma(
    items_new: ItemCollection,
    items_old: ItemCollection,
    common_new: List[Hashable],
    common_old: List[Hashable],
) -> Tuple[float, float]:
    """
    Transform the IRT scale of the new test form to the old test form in common-item nonequivalent groups (CINEG) / nonequivalent groups with anchor test (NEAT) design.
    Estimate scale linking coefficients using parameters of the common items.
    The Mean–Sig
    ma (MS) method uses the mean and standard deviation of common-item difficulty parameters.

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

    Returns
    -------
    Tuple[float, float]
        A : Slope of linear linking function
        B : Intercept of linear linking function
    
    References
    ----------
    Marco, G. L. (1977). Item characteristic curve solutions to three intractable testing problems 1. ETS Research Bulletin Series, 1977(1), i-41.
    
    Examples
    --------
    >>> from EqUMP.base import IRF
    >>> items_new = {1: IRF({"a": 1.2, "b": 0.5}, "2PL")}
    >>> items_old = {1: IRF({"a": 1.1, "b": 0.48}, "2PL")}
    >>> A, B = mean_sigma(items_new, items_old, [1], [1])
    """
    # Extract b parameters for common items from IRF objects
    b_new = np.concatenate(
        [
            np.atleast_1d(np.asarray(items_new[item].params["b"], dtype=float)).ravel()
            for item in common_new
        ]
    )
    b_old = np.concatenate(
        [
            np.atleast_1d(np.asarray(items_old[item].params["b"], dtype=float)).ravel()
            for item in common_old
        ]
    )

    # compute A and B
    sigma_b_new = float(np.std(b_new, ddof=0))
    sigma_b_old = float(np.std(b_old, ddof=0))
    mean_b_new = float(np.mean(b_new))
    mean_b_old = float(np.mean(b_old))

    A = sigma_b_old / sigma_b_new
    B = mean_b_old - A * mean_b_new

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
    
    res2 = mean_sigma(
        items_new=KIM_dic_items_new,
        items_old=KIM_dic_items_old,
        common_new=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        common_old=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    )
    print(res2)

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

    res3 = mean_sigma(
        items_new=KIM_poly_items_new,
        items_old=KIM_poly_items_old,
        common_new=[2, 5, 8, 11, 14, 17, 20],
        common_old=[2, 5, 8, 11, 14, 17, 20]
    )
    print(res3)