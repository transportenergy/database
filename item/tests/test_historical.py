from pathlib import Path

import pytest

import item
from item.common import paths
from item.historical import SCRIPTS, fetch_source, input_file
from item.historical.util import run_notebook


@pytest.mark.parametrize('source_id', [
    # OECD via SDMX
    1, 2, 3,
    # OpenKAPSARC
    5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
])
def test_fetch(source_id):
    """Raw data can be fetched from individual sources."""
    fetch_source(source_id)


def test_import():
    # All historical database classes can be imported
    from item.historical.scripts.util.managers.country_code \
        import CountryCodeManager
    from item.historical.scripts.util.managers.dataframe \
        import DataframeManager

    CountryCodeManager()
    DataframeManager(dataset_id=None)


def test_input_file(item_tmp_dir):
    # Create some temporary files in any order
    files = [
        'T001_foo.csv',
        'T001_bar.csv',
    ]
    for name in files:
        (paths['historical input'] / name).write_text('(empty)')

    # input_file retrieves the last-sorted file:
    assert input_file(1) == paths['historical input'] / 'T001_foo.csv'


# Path to IPython notebooks
nb_path = Path(item.__file__).parent / 'historical' / 'scripts'


@pytest.mark.parametrize('dataset_id', SCRIPTS)
def test_run_notebook(dataset_id, tmp_path):
    # Notebook runs top-to-bottom without cell errors
    nb, errors = run_notebook(nb_path / f'{dataset_id}.ipynb', tmp_path)
    assert errors == []
