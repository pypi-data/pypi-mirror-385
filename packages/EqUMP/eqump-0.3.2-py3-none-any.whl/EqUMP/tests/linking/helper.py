from pathlib import Path
import pandas as pd
from typing import Tuple

def load_SNSequate_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load SNSequate data files from the parent directory.

    Returns
    -------
    SNS_param_x : pd.DataFrame
        Parameter estimates for the old form (X)
    SNS_param_y : pd.DataFrame
        Parameter estimates for the new form (Y)

    Notes
    -----
    This data only contains dichotomous items
    """        
    current_dir = Path(__file__).parent
    
    try:
        SNS_param_x = pd.read_csv(current_dir / "KBformX_par.csv", index_col=0)
        SNS_param_y = pd.read_csv(current_dir / "KBformY_par.csv", index_col=0)
    except FileNotFoundError:
        raise FileNotFoundError("SNSequate data files not found")
    
    SNS_param_x = _add_model_into_SNSequate_data(SNS_param_x)
    SNS_param_y = _add_model_into_SNSequate_data(SNS_param_y)
    return SNS_param_x, SNS_param_y

def load_KIM_dichotomous_data() -> Tuple[dict, dict]:
    r"""
    load data from Kim(2022) textbook, dichotomous items only

    References
    ----------
    김성훈 (2022). 문항반응이론 검사동등화. 공동체, p146-148.
    """
    import warnings
    warnings.warn("This data is not functioing due to change of API")
    KIM_param_new = {
        1: {"a": 0.834, "b": -1.435, "c": 0.197},
        2: {"a": 0.866, "b": -1.399, "c": 0.201},
        3: {"a": 1.008, "b": -0.683, "c": 0.213},
        4: {"a": 1.389, "b": -0.209, "c": 0.224},
        5: {"a": 1.291, "b": -0.094, "c": 0.215},
        6: {"a": 1.535, "b": 0.449, "c": 0.161},
        7: {"a": 1.511, "b": 0.671, "c": 0.202},
        8: {"a": 1.032, "b": 1.036, "c": 0.175},
        9: {"a": 1.298, "b": 1.315, "c": 0.165},
        10: {"a": 1.032, "b": 1.684, "c": 0.317},
    }

    KIM_param_old = {
        1: {"a": 0.586, "b": -2.177, "c": 0.202},
        2: {"a": 0.763, "b": -1.654, "c": 0.209},
        3: {"a": 0.930, "b": -0.927, "c": 0.233},
        4: {"a": 1.168, "b": -0.599, "c": 0.182},
        5: {"a": 1.266, "b": -0.287, "c": 0.205},
        6: {"a": 1.410, "b": 0.150, "c": 0.149},
        7: {"a": 1.119, "b": 0.500, "c": 0.199},
        8: {"a": 0.838, "b": 1.067, "c": 0.142},
        9: {"a": 1.042, "b": 1.440, "c": 0.174},
        10: {"a": 0.764, "b": 2.063, "c": 0.332},
    }
    return KIM_param_new, KIM_param_old

def load_KIM_polytomous_data() -> Tuple[dict, dict]:
    r"""
    load data from Kim(2022) textbook, polytomous items included

    References
    ----------
    김성훈 (2022). 문항반응이론 검사동등화. 공동체, p146-148.
    """
    import warnings
    warnings.warn("This data is not functioing due to change of API")
    KIM_param_X = {
        1: {"a": 1.035, "b": -1.663, "c": 0.201},
        2: {"a": 1.266, "b": -1.173, "c": 0.254},
        3: {"a": 0.921, "b": -1.250, "c": 0.333},
        4: {"a": 1.128, "b": -0.445, "c": 0.355},
        5: {"a": 1.052, "b": -0.464, "c": 0.360},
        6: {"a": 1.027, "b": -0.193, "c": 0.302},
        7: {"a": 1.572, "b": -0.279, "c": 0.337},
        8: {"a": 2.042, "b": -0.031, "c": 0.209},
        9: {"a": 1.651, "b": 0.045, "c": 0.325},
        10: {"a": 1.402, "b": 0.102, "c": 0.167},
        11: {"a": 1.534, "b": 0.521, "c": 0.209},
        12: {"a": 1.387, "b": 0.875, "c": 0.305},
        13: {"a": 1.674, "b": 0.962, "c": 0.189},
        14: {"a": 0.767, "b": 1.450, "c": 0.303},
        15: {"a": 1.474, "b": 1.782, "c": 0.240},
        # GPC items
        16: {"a": 1.450, "b": [-1.560, -0.198]},
        17: {"a": 0.434, "b": [-1.178, -0.086]},
        18: {"a": 1.106, "b": [-0.440, 0.856]},
        19: {"a": 0.618, "b": [-0.998, 0.519, -1.522]},
        20: {"a": 0.710, "b": [0.324, -0.782, 0.398]},
        21: {"a": 0.677, "b": [-0.417, 1.004, 1.999]},
    }

    KIM_param_Y = {
        1: {"a": 1.331, "b": -1.799, "c": 0.204},
        2: {"a": 1.059, "b": -1.115, "c": 0.262},
        3: {"a": 0.847, "b": -0.727, "c": 0.302},
        4: {"a": 0.936, "b": -0.480, "c": 0.314},
        5: {"a": 0.718, "b": -0.530, "c": 0.269},
        6: {"a": 0.681, "b": -0.081, "c": 0.263},
        7: {"a": 1.725, "b": -0.063, "c": 0.242},
        8: {"a": 1.613, "b": 0.258, "c": 0.203},
        9: {"a": 1.196, "b": 0.566, "c": 0.329},
        10: {"a": 0.775, "b": 0.735, "c": 0.087},
        11: {"a": 1.281, "b": 0.977, "c": 0.204},
        12: {"a": 1.458, "b": 0.971, "c": 0.084},
        13: {"a": 1.308, "b": 1.440, "c": 0.123},
        14: {"a": 0.540, "b": 1.982, "c": 0.283},
        15: {"a": 0.657, "b": 2.595, "c": 0.288},
        # GPC items
        16: {"a": 0.643, "b": [0.305, -2.141]},
        17: {"a": 0.370, "b": [-1.139, 0.241]},
        18: {"a": 1.551, "b": [-0.157, 1.677]},
        19: {"a": 0.425, "b": [0.956, -2.354, -0.657]},
        20: {"a": 0.615, "b": [0.621, -0.479, 0.698]},
        21: {"a": 0.715, "b": [1.242, 1.325, 1.603]},
    }
    return KIM_param_X, KIM_param_Y

def _add_model_into_SNSequate_data(df: pd.DataFrame) -> pd.DataFrame:
    df["model"] = "3PL"
    return df
