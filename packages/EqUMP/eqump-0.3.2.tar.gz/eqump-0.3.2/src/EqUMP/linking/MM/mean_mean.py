import numpy as np
from typing import Hashable, List, Tuple
from EqUMP.base import ItemCollection

def mean_mean(
    items_new: ItemCollection,
    items_old: ItemCollection,
    common_new: List[Hashable],
    common_old: List[Hashable],
) -> Tuple[float, float]:
    """
    Transform the IRT scale in common-item nonequivalent groups (CINEG) / nonequivalent groups with anchor test (NEAT) design.
    Estimate scale linking coefficients using parameters of the common items.
    The Mean–Mean (MM) method uses the mean of common-item discrimination and difficulty parameters.

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
    Loyd, B. H., & Hoover, H. D. (1980). Vertical equating using the Rasch model. Journal of Educational Measurement, 17(3), 179–193. https://doi.org/10.1111/j.1745-3984.1980.tb00825.x
    
    Examples
    --------
    >>> from EqUMP.base import IRF
    >>> items_new = {1: IRF({"a": 1.2, "b": 0.5}, "2PL")}
    >>> items_old = {1: IRF({"a": 1.1, "b": 0.48}, "2PL")}
    >>> A, B = mean_mean(items_new, items_old, [1], [1])
    """
    # Extract a and b parameters for common items from IRF objects
    a_new = np.array([items_new[item].params["a"] for item in common_new])
    a_old = np.array([items_old[item].params["a"] for item in common_old])

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
    mean_a_new = float(np.mean(a_new))
    mean_a_old = float(np.mean(a_old))
    mean_b_new = float(np.mean(b_new))
    mean_b_old = float(np.mean(b_old))

    A = mean_a_new / mean_a_old
    B = mean_b_old - A * mean_b_new

    # output
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

    res2 = mean_mean(
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

    res3 = mean_mean(
        items_new=KIM_poly_items_new,
        items_old=KIM_poly_items_old,
        common_new=[2, 5, 8, 11, 14, 17, 20],
        common_old=[2, 5, 8, 11, 14, 17, 20]
    )
    print(res3)
