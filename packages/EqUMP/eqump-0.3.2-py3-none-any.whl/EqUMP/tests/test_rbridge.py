import pytest
import json
import subprocess
from pathlib import Path
from .rbridge import run_rscript
from typing import Generator

# Assuming rbridge.py is in the same 'tests' directory.
# If rbridge.py is in the parent EqUMP directory, use: from ..rbridge import run_rscript

import shutil, os
import tempfile

@pytest.mark.rbridge
def test_rscript_available():
    rscript = os.getenv("RSCRIPT") or shutil.which("Rscript")
    if not rscript:
        pytest.skip("Rscript not found. Set RSCRIPT in .env or add to PATH")
    print(f"Using Rscript at: {rscript}")

@pytest.mark.rbridge
def test_rscript_run():
    """Test that we can actually run an R script via subprocess and get clean output."""
    # Check if Rscript is available
    rscript = os.getenv("RSCRIPT") or shutil.which("Rscript")
    if not rscript:
        pytest.skip("Rscript not found. Set RSCRIPT in .env or add to PATH")
    
    # Create a temporary directory for our test
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a simple R script that prints JSON output
        r_script_content = '''
# Simple R script for testing
cat('{"result": 1, "message": "Hello from R"}')
'''
        
        # Write the R script to a temporary file
        r_script_path = Path(temp_dir) / "test_script.R"
        with open(r_script_path, 'w') as f:
            f.write(r_script_content)
        
        # Create a dummy payload (though this script doesn't use it)
        test_payload = {"test": "data"}
        
        try:
            # Run the R script using our run_rscript function
            result = run_rscript(
                payload=test_payload,
                rscript_path="test_script.R",
                module_path=temp_dir,
                rscript_exe=rscript
            )
            
            # Verify the output
            assert isinstance(result, dict), "Result should be a dictionary"
            assert result["result"] == 1, "Result should contain expected value"
            assert result["message"] == "Hello from R", "Result should contain expected message"
            
        except subprocess.CalledProcessError as e:
            pytest.fail(f"R script execution failed: {e}")
        except json.JSONDecodeError as e:
            pytest.fail(f"Failed to parse R script JSON output: {e}")

@pytest.mark.rbridge
def test_r_packages():
    """Test that required R packages (equateIRT and jsonlite) are installed."""
    # Check if Rscript is available
    rscript = os.getenv("RSCRIPT") or shutil.which("Rscript")
    if not rscript:
        pytest.skip("Rscript not found. Set RSCRIPT in .env or add to PATH")
    
    # Create a temporary directory for our test
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create an R script that checks for required packages
        r_script_content = '''
# Check if required packages are installed
required_packages <- c("jsonlite", "irt", "mirt", "SNSequate", "equateIRT", "kequate")
installed_packages <- installed.packages()[, "Package"]

results <- list()
for (pkg in required_packages) {
    results[[pkg]] <- pkg %in% installed_packages
}

# Output results as JSON
library(jsonlite)
cat(toJSON(results, auto_unbox = TRUE))
'''
        
        # Write the R script to a temporary file
        r_script_path = Path(temp_dir) / "check_packages.R"
        with open(r_script_path, 'w') as f:
            f.write(r_script_content)
        
        # Create a dummy payload
        test_payload = {"check": "packages"}
        
        try:
            # Run the R script using our run_rscript function
            result = run_rscript(
                payload=test_payload,
                rscript_path="check_packages.R",
                module_path=temp_dir,
                rscript_exe=rscript
            )
            
            # Verify the packages are installed
            assert isinstance(result, dict), "Result should be a dictionary"
            assert "equateIRT" in result, "Result should contain equateIRT package status"
            assert "jsonlite" in result, "Result should contain jsonlite package status"
            assert "irt" in result, "Result should contain irt package status"
            assert "mirt" in result, "Result should contain mirt package status"
            assert "SNSequate" in result, "Result should contain SNSequate package status"
            assert "kequate" in result, "Result should contain kequate package status"
            
            # Check that both packages are installed
            if not result["equateIRT"]:
                pytest.fail("equateIRT package is not installed. Please install it with: install.packages('equateIRT')")
            if not result["jsonlite"]:
                pytest.fail("jsonlite package is not installed. Please install it with: install.packages('jsonlite')")
            if not result["irt"]:
                pytest.fail("irt package is not installed. Please install it with: install.packages('irt')")
            if not result["mirt"]:
                pytest.fail("mirt package is not installed. Please install it with: install.packages('mirt')")
            if not result["SNSequate"]:
                pytest.fail("SNSequate package is not installed. Please install it with: install.packages('SNSequate')")
            if not result["kequate"]:
                pytest.fail("kequate package is not installed. Please install it with: install.packages('kequate')")
            
            print("All required R packages are installed:")
            print(f"  - equateIRT: {'✓' if result['equateIRT'] else '✗'}")
            print(f"  - jsonlite: {'✓' if result['jsonlite'] else '✗'}")
            print(f"  - irt: {'✓' if result['irt'] else '✗'}")
            print(f"  - mirt: {'✓' if result['mirt'] else '✗'}")
            print(f"  - SNSequate: {'✓' if result['SNSequate'] else '✗'}")
            print(f"  - kequate: {'✓' if result['kequate'] else '✗'}")
            
        except subprocess.CalledProcessError as e:
            pytest.fail(f"R script execution failed: {e}")
        except json.JSONDecodeError as e:
            pytest.fail(f"Failed to parse R script JSON output: {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error during package check: {e}")
