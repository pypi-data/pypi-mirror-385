from typing import Dict, Union, List
import numpy as np
import pandas as pd
from EqUMP.base.irf import IRF, ItemModelType, ItemParams

def create_prob_df(
    theta: float,
    items: List[ItemParams],
    model: Union[ItemModelType, List[ItemModelType]],
    D: float = 1.702,
    ) -> pd.DataFrame:
    """
    Create a probability dataframe from items and a theta value.

    Best practice: do not auto-infer item models from parameter keys. Instead,
    require explicit model specification to avoid ambiguity (e.g., 1PL vs 2PL).

    Parameters
    ----------
    theta : float
        Ability value at which to evaluate item response probabilities.
    items : List[ItemParams]
        A list of item parameter dictionaries. Each item may also include a
        'model' key, but the function requires the `model` argument explicitly.
    model : Union[ItemModelType, List[ItemModelType]]
        Model specification.
        - If a string, the same model is applied to all items.
        - If a list of strings, each entry corresponds to the respective item.
    D : float, default 1.702
        Scaling constant.

    Returns
    ----------
    pd.DataFrame
        Probability dataframe; each row corresponds to an item (evaluated at
        the provided theta), and columns correspond to categories.
    
    Examples
    ----------
    
    # Single item, single model
    item1 = {"a": 1.2, "b": [0.3, 0.5], "model": "GPCM"}
    df1 = create_prob_df(theta=0.0, items=[item1], model="GPCM", D=1.702)
    
    # Multiple items, multiple models
    item2 = {"a": 1.1, "b": [-0.74, 0.3, 0.91], "model": "GPCM"}
    item3 = {"a": 1.0, "b": [0.0, 0.5], "model": "GPCM2"}
    df2 = create_prob_df(
        theta=0.0, items=[item2, item3], model=["GPCM", "GPCM2"], D=1.702
    )

    # Multiple items, single model
    item4 = {"a": 1.0, "b": [-0.1, 0.5, 0.9]}
    item5 = {"a": 0.4, "b": [-0.5, 0.6, 0.9]}
    df3 = create_prob_df(
        theta=0.0, items=[item4, item5], model="GPCM", D=1.702
    )
    """
    # Validate model argument length if list
    if isinstance(model, list) and len(model) != len(items):
        raise ValueError(
            "Length of `model` list must match length of `items`. "
            f"Got {len(model)} vs {len(items)}."
        )
    _validate_models(model)

    dfs = []
    for idx, item in enumerate(items):
        # Determine the model to use for this item
        if isinstance(model, list):
            item_model = model[idx]
        else:
            item_model = model

        # Remove 'model' key from params (case-insensitive) before creating IRF object
        params = {k: v for k, v in item.items() if k.lower() != "model"}

        # Create IRF object and compute probabilities
        irf_obj = IRF(params=params, model=str(item_model), D=D)
        eachdf = irf_obj.prob(theta=theta)
        dfs.append(eachdf)

    output = pd.concat(dfs, axis=0)
    return output

def trf(prob_df: pd.DataFrame) -> float:
    r"""
    Compute the total response function (TRF) from the probability dataframe.

    Parameters
    ----------
    prob_df : pd.DataFrame
        The probability dataframe.

    Returns
    ----------
    float
        The total response function (TRF).

    Examples
    ----------
    >>> import pandas as pd
    >>> prob_df = pd.DataFrame(
    ...     {
    ...         "0": [0.2, 0.3, 0.5],
    ...         "1": [0.8, 0.7, 0.5],
    ...     },
    ...     index=[0.0, 1.0, 2.0],
    ... )
    >>> trf(prob_df)
    2.0
    """
    if not all(isinstance(idx, (float, int)) for idx in prob_df.index):
        invalid_indices = [idx for idx in prob_df.index if not isinstance(idx, (float, int))]
        raise TypeError(
            f"All indices in `prob_df` must be float or int representing theta values. "
            f"Found invalid indices: {invalid_indices} with types: {[type(idx).__name__ for idx in invalid_indices]}"
        )
    output = float((prob_df * prob_df.columns.astype(float)).sum().sum())

    return output

def _validate_models(models: List[str]) -> None:
    """
    Verify item model combinations are safe
    - '1PL' and 'Rasch' models cannot be used together.

    Parameters
    ----------
    models : List[str]
        List of item models.

    Raises
    ----------
    ValueError
        If '1PL' and 'Rasch' models are used together.
    """
    if isinstance(models, list):
        if "1PL" in models and "Rasch" in models:
            raise ValueError("Cannot use '1PL' and 'Rasch' models together.")
