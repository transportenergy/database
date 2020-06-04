import io
import os
import subprocess
import sys
from pathlib import Path

import nbformat


def run_notebook(nb_path, tmp_path, env=os.environ, kernel=None):
    """Execute a Jupyter notebook via nbconvert and collect output.

    Copied from ixmp.testing.

    Parameters
    ----------
    nb_path : path-like
        The notebook file to execute.
    tmp_path : path-like
        A directory in which to create temporary output.
    env : dict-like
        Execution environment for `nbconvert`.
    kernel : str
        Jupyter kernel to use. Default: `python2` or `python3`, matching the
        current Python version.

    Returns
    -------
    nb : :class:`nbformat.NotebookNode`
        Parsed and executed notebook.
    errors : list
        Any execution errors.
    """
    # IPython kernel
    kernel = kernel or "python{}".format(sys.version_info[0])

    # Temporary notebook to contain execution output
    fname = Path(tmp_path) / "test.ipynb"

    command = [
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        "--ExecutePreprocessor.timeout=600",
        f"--ExecutePreprocessor.kernel_name={kernel}",
        "--output",
        str(fname),
        str(nb_path),
    ]

    # Change to directory containing the notebook to be executed
    os.chdir(nb_path.parent)

    # Execute
    subprocess.check_call(command, env=env)

    # Read the output notebook
    nb = nbformat.read(io.open(fname, encoding="utf-8"), nbformat.current_nbformat)

    # Store errors
    errors = []
    for cell in nb.cells:
        for output in cell.get("outputs", []):
            if output.output_type == "error":
                errors.append(output)

    # Remove output
    fname.unlink()

    return nb, errors
