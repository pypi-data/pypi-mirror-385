from .qudarature import gauss_hermite_quadrature, fixed_point_quadrature
from .irf import (
    irf, 
    IRF,
    # Semantic type aliases for better type hints
    DichotomousParams,
    PolytomousParams,
    ItemParams,
    ItemParamsInit,
    ItemParamsCollection,
    ItemCollection,
    # Model type literals
    DichotomousItemType,
    PolytomousItemType,
    ItemModelType,
)
from .trf import trf, create_prob_df
from .estimation import mmle_em, MMLEEMResult
from .plot import make_irf_object  # Deprecated: Use IRF class directly