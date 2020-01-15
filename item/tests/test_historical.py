from pathlib import Path

import pytest

import item
from item.common import paths
from item.historical import input_file
from item.historical.util import run_notebook


def test_import():
    # All historical database classes can be imported
    from item.historical.scripts.util.managers.CountryCodeManager \
        import CountryCodeManager
    from item.historical.scripts.util.managers.DataframeManager \
        import DataframeManager
    from item.historical.scripts.util.managers.UnitConverterManager \
        import UnitConverterManager

    CountryCodeManager()
    DataframeManager(dataset_id=None)
    UnitConverterManager()


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


@pytest.mark.parametrize('dataset_id', [
    'T000',
    'T001',
    'T002',
    'T003',
    'T004',
    'T005',
    'T006',
])
def test_run_notebook(dataset_id, tmp_path):
    # Notebook runs top-to-bottom without cell errors
    nb, errors = run_notebook(nb_path / f'{dataset_id}.ipynb', tmp_path)
    assert errors == []
