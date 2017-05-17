from os.path import exists, join
import pytest
import xarray as xr

from item.common import paths
from item.model import load_model_data, process_raw, select


slow = pytest.mark.skipif(
    not pytest.config.getoption('--run-slow'),
    reason='need --runslow option to run'
    )


item1_size = 928541
item2_size = 1994943


@pytest.fixture(scope='session')
def item1_data():
    yield load_model_data(1)


@slow
@pytest.mark.parametrize('model', ['bp', 'eppa5'])
def test_process_raw(item_tmp_dir, model):
    process_raw([model])
    assert exists(join(paths['model processed'], '%s.csv' % model))


@slow
def test_item1_dataframe():
    # As a pd.DataFrame
    data = load_model_data(1, skip_cache=True)
    assert len(data) == item1_size

    # As a dict() of xr.DataArray
    data = load_model_data(1, fmt=xr.DataArray)
    size = sum([d.notnull().sum() for d in data.values()])
    assert size == 875589  # Omits intensity_new

    # As a xr.Dataset
    data = load_model_data(1, fmt=xr.Dataset)
    assert data.notnull().sum() == 875589  # Omits intensity_new


@slow
def test_item2():
    # As a pd.DataFrame
    data = load_model_data(2, skip_cache=True)
    assert len(data) == item2_size


@slow
@pytest.mark.xfail(reason='causes a MemoryError')
def test_item2_xr():
    # As a dict() of xr.DataArray
    data = load_model_data(2, fmt=xr.DataArray)
    size = sum([d.notnull().sum() for d in data.values()])
    assert size == item2_size


def test_invalid_version():
    # Load an invalid model database version
    with pytest.raises(ValueError):
        load_model_data(99)


def test_select(item1_data):
    from item.model.dimensions import PAX

    data = select(item1_data, 'energy', tech='All', fuel='All', mode=PAX)
    # print(data.head(), len(data))
    assert len(data) == 6752


def test_scenarios():
    from item.model.common import SCENARIOS

    assert len(SCENARIOS) == 28
