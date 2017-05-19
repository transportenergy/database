from os.path import join
import shutil
import tempfile

import pytest


def pytest_addoption(parser):
    parser.addoption('--run-slow', action='store_true',
                     help='run slow tests')
    parser.addoption('--local-data',
                     help='path to local data for testing')


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

    if local_data is None:
        pytest.skip('needs full database (give --local-data)')

    tmp_dir = tempfile.mkdtemp()
    try:
        # Create the directories
        make_database_dirs(tmp_dir, False)

        # Override configuration for the test suite
        paths = {
            'log': tmp_dir,
            'model': tmp_dir,
            'model raw': join(local_data, 'model', 'raw'),
            'model database': join(local_data, 'model', 'database'),
            }
        init_paths(**paths)

        # For use by test functions
        yield tmp_dir
    finally:
        # Remove the whole tree
        shutil.rmtree(tmp_dir)
