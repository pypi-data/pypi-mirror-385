import numpy as np
import pandas as pd
import pytest

from EqUMP.base import IRF
from EqUMP.linking import mean_sigma
from EqUMP.tests.rbridge import run_rscript

def test_ms_output_structure_and_types():
    # Use at least two common items per form to avoid zero std in MS
    items_old = {
        "i1": IRF({"a": 1.0, "b": 0.0}, "2PL"),
        "i2": IRF({"a": 1.0, "b": 2.0}, "2PL"),
    }
    items_new = {
        "j1": IRF({"a": 1.0, "b": 1.0}, "2PL"),
        "j2": IRF({"a": 1.0, "b": 4.0}, "2PL"),
    }
    common_old = ["i1", "i2"]
    common_new = ["j1", "j2"]

    out = mean_sigma(items_new, items_old, common_new, common_old)

    # Structure
    assert isinstance(out, tuple), f"out is {type(out)}"
    assert len(out) == 2

    # Types
    A, B = out
    assert isinstance(A, (float, np.floating))
    assert isinstance(B, (float, np.floating))


def test_ms_raises_on_missing_keys():
    # Missing 'b' should raise KeyError at IRF construction
    with pytest.raises(KeyError, match="2PL model requires 'a' and 'b' parameters"):
        IRF({"a": 1.0}, "2PL")  # Missing 'b'
    
    # Missing 'a' should also raise KeyError at IRF construction
    with pytest.raises(KeyError, match="2PL model requires 'a' and 'b' parameters"):
        IRF({"b": 0.0}, "2PL")  # Missing 'a'

from pathlib import Path
class TestMS_R:
    @pytest.mark.rbridge
    def test_compare_SNSequate(self, tol=1e-4):
        from EqUMP.tests.linking.helper import load_SNSequate_data
        SNS_param_x, SNS_param_y = load_SNSequate_data()
        SNS_param_new_raw = SNS_param_x[["a","b","c"]].to_dict(orient="index") # SNSequate에서 y가 구 검사형, X가 신 검사형에 주의
        SNS_param_old_raw = SNS_param_y[["a","b","c"]].to_dict(orient="index")
        
        # Convert to IRF objects
        items_new = {k: IRF(v, "3PL") for k, v in SNS_param_new_raw.items()}
        items_old = {k: IRF(v, "3PL") for k, v in SNS_param_old_raw.items()}
        
        res_python = mean_sigma(
            items_new=items_new,
            items_old=items_old,
            common_new=[3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
            common_old=[3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]
        )

        test_dir = Path(__file__).parent
        res_r = run_rscript(
            payload={}, rscript_path="../SNSequate.R", module_path=str(test_dir)
        )

        A_python = res_python[0]
        B_python = res_python[1]
        A_r = res_r["ms"]["A"]
        B_r = res_r["ms"]["B"]

        assert abs(A_python - A_r) < tol, (
            f"A constants differ: Python={A_python:.6f}, R={A_r:.6f}, "
            f"difference={abs(A_python - A_r):.6f}"
        )
        assert abs(B_python - B_r) < tol, (
            f"B constants differ: Python={B_python:.6f}, R={B_r:.6f}, "
            f"difference={abs(B_python - B_r):.6f}"
        )

        print(f"\nMean-sigma Comparison Results:")
        print(f"Python: A={A_python:.6f}, B={B_python:.6f}")
        print(f"R:      A={A_r:.6f}, B={B_r:.6f}")
        print(f"Differences: ΔA={abs(A_python - A_r):.6f}, ΔB={abs(B_python - B_r):.6f}")
    
    @pytest.mark.skip(reason="Temporarily disabled while debugging")
    def test_compare_KB(self):
        pass
