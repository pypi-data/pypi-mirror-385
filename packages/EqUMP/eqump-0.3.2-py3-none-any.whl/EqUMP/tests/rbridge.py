import json, subprocess, shutil, tempfile, logging
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

def run_rscript(payload: dict, rscript_path: str, module_path: str, rscript_exe: str = None) -> dict:
    """
    Run an R script with the given payload and return the output as a dictionary.
    
    Parameters
    ----------
    payload : dict
        The input data to be passed to the R script.
    rscript_path : str
        The path to the R script to be executed.
    module_path : str
        The path to the R module directory, used as the working directory for the script.
    rscript_exe : str, optional
        The path to the Rscript executable. If None, will try to find it automatically.

    Returns
    -------
    dict: The output from the R script as a dictionary.
    """
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json', dir=module_path) as temp_input_file:
        json.dump(payload, temp_input_file)
        temp_input_file_path = temp_input_file.name

    try:
        # Get the Rscript executable path
        if rscript_exe is None:
            rscript_exe = os.getenv("RSCRIPT") or shutil.which("Rscript")
            if not rscript_exe:
                raise FileNotFoundError("Rscript not found. Set RSCRIPT in .env or add to PATH")
        
        # Ensure rscript_path is absolute or relative to module_path
        rscript_full_path = Path(module_path) / rscript_path

        result = subprocess.run(
            [rscript_exe, str(rscript_full_path), temp_input_file_path],
            capture_output=True,
            text=True,
            check=True,
            cwd=module_path  # Set the working directory for the R script
        )
        if result.stderr:
            logging.warning("R script produced warnings:\n%s", result.stderr)
        
        output = json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error("R script failed with exit code %d:\n---STDOUT---\n%s\n---STDERR---\n%s", e.returncode, e.stdout, e.stderr)
        raise
    except json.JSONDecodeError as e:
        logging.error("Failed to decode JSON from R script output:\n%s", result.stdout)
        raise
    finally:
        Path(temp_input_file_path).unlink(missing_ok=True)

    return output