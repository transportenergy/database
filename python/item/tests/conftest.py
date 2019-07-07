from pathlib import Path
import shutil

import pytest


# From xarray
@pytest.fixture(scope='session')
def item_tmp_dir(tmp_path_factory):
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
    else:
        local_data = Path(local_data)

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
            })

        # For use by test functions
        yield tmp_path
    finally:
        # Remove the whole tree
        shutil.rmtree(tmp_path)
