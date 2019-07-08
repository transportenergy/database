from pathlib import Path
import shutil

import pytest


def pytest_addoption(parser):
    parser.addoption('--local-data', action='store', default=None,
                     help='path to local data for testing')
    parser.addoption('--stats-server', action='store', default=None,
                     help='address of statistics server')


# From xarray
@pytest.fixture(scope='session')
def item_tmp_dir(tmp_path_factory, pytestconfig):
    """Create a temporary iTEM directory with the structure:

    <path>
    |- model
    |  |- database
    |  |- raw
    |  |- processed

    """
    from item.common import init_paths, make_database_dirs

    local_data = Path(pytestconfig.getoption('--local-data', skip=True))

    tmp_path = tmp_path_factory.mktemp('item-user-data')
    try:
        # Create the directories
        make_database_dirs(tmp_path, False)

        # Override configuration for the test suite
        init_paths(**{
            'log': tmp_path,
            'model': tmp_path,
            'model raw': local_data / 'model' / 'raw',
            'model database': local_data / 'model' / 'database',
            'output': tmp_path / 'output',
            })

        # For use by test functions
        yield tmp_path
    finally:
        # Remove the whole tree
        shutil.rmtree(tmp_path)
