from os.path import join
import shutil
import tempfile

import pytest


def pytest_addoption(parser):
    parser.addoption('--run-slow', action='store_true',
                     help='run slow tests')
    parser.addoption('--local-data',
                     required=True,
                     help='path for local data for testing')


# From xarray
@pytest.fixture(scope='session')
def item_tmp_dir():
    """Create a temporary iTEM directory with the structure:

    <path>
    |- model
    |  |- database
    |  |- raw
    |  |- processed

    """
    from item.common import init_paths, make_database_dirs

    local_data = pytest.config.getoption('--local-data')

    path = tempfile.mkdtemp()
    try:
        # Create the directories
        make_database_dirs(path, False)

        # Override configuration for the test suite
        paths = {
            'log': path,
            'model': path,
            'model raw': join(local_data, 'model', 'raw'),
            'model database': join(local_data, 'model', 'database'),
            }
        init_paths(**paths)

        # For use by test functions
        yield path
    finally:
        # Remove the whole tree
        shutil.rmtree(path)
