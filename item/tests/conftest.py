import os
import shutil
from pathlib import Path

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--local-data",
        action="store",
        default=None,
        help="path to local data for testing",
    )


def pytest_report_header(config, start_path):
    msg = "OpenKAPSARC API key: "
    msg += "present" if "OK_API_KEY" in os.environ else "MISSING"
    return msg


# From xarray
@pytest.fixture(scope="session")
def item_tmp_dir(tmp_path_factory, pytestconfig):
    """Create a temporary iTEM directory with the structure:

    <path>
    |- model
    |  |- database
    |  |- raw
    |  |- processed

    """
    from item.common import config, init_paths, make_database_dirs

    local_data = pytestconfig.getoption("--local-data")

    tmp_path = tmp_path_factory.mktemp("item-user-data")
    try:
        # Create the directories
        make_database_dirs(tmp_path, False)

        # Override configuration for the test suite
        init_paths(
            **{
                "log": tmp_path,
                "model": tmp_path / "model",
                "historical": tmp_path / "historical",
                "output": tmp_path / "output",
            }
        )

        if local_data:
            local_data = Path(local_data)
            shutil.copytree(local_data / "model" / "raw", config["model raw"])
            shutil.copytree(local_data / "model" / "database", config["model database"])

        # For use by test functions
        yield tmp_path
    finally:
        pass
