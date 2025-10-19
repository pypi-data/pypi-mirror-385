# SPDX-License-Identifier: MIT
from __future__ import annotations

import warnings
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union, Literal
import numpy as np
import pandas as pd

from EqUMP.base.irf import IRF, ItemParamsInit

def make_irf_object(
    theta_grid: Optional[Sequence[float]] = None,
    params: Optional[ItemParamsInit] = None,
    model: Optional[str] = None,
    D: float = 1.702,
) -> IRF:
    """
    Create an IRF object for plotting and inspection.
    
    DEPRECATED: This function is maintained for backward compatibility.
    Use IRF class directly: IRF(params=params, model=model, D=D)
    
    Parameters
    ----------
    theta_grid : sequence of float, optional
        The theta values to evaluate. Defaults to np.arange(-6, 6.05, 0.05).
        Note: This parameter is ignored. The IRF class computes probabilities on-demand.
    params : dict
        Item parameters accepted by IRF class.
    model : str
        One of {"Rasch", "1PL", "2PL", "3PL", "GPCM", "GRM", "GPCM2"}.
    D : float
        Scaling constant (default: 1.702).
    
    Returns
    -------
    IRF
        IRF object with plotting and computation capabilities.
    
    Examples
    --------
    >>> # Old way (still works)
    >>> obj = make_irf_object(params={"a": 1.2, "b": 0.5}, model="2PL")
    >>> obj.plot()
    
    >>> # New way (recommended)
    >>> item = IRF(params={"a": 1.2, "b": 0.5}, model="2PL")
    >>> item.plot()
    """
    warnings.warn(
        "make_irf_object() is deprecated and will be removed in a future version. "
        "Use IRF class directly: IRF(params=params, model=model, D=D)",
        DeprecationWarning,
        stacklevel=2
    )
    
    if params is None or model is None:
        raise ValueError("Both 'params' and 'model' must be provided.")
    
    # theta_grid is ignored - kept for backward compatibility
    return IRF(params=params, model=model, D=D)

if __name__ == "__main__":
    obj = make_irf_object(params={"a": 1.2, "b": 0.0}, model="2PL", D=1.702)
    obj.plot()

    # obj = make_irf_object(params={"a": 1.0, "b": [-1.0, 0.5, 1.2]}, model="GPCM", D=1.702)
    # obj.plot()