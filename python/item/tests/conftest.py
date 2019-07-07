from os.path import join
import shutil

import pytest


# From xarray
@pytest.fixture(scope='session')
def item_tmp_dir(tmp_path):
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

    try:
        # Create the directories
        make_database_dirs(tmp_path, False)

        # Override configuration for the test suite
        paths = {
            'log': tmp_path,
            'model': tmp_path,
            'model raw': join(local_data, 'model', 'raw'),
            'model database': join(local_data, 'model', 'database'),
            }
        init_paths(**paths)

        # For use by test functions
        yield tmp_path
    finally:
        # Remove the whole tree
        shutil.rmtree(tmp_path)
