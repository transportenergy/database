from os.path import exists, join

import pytest
import xarray as xr

from item.common import paths
from item.model import (
    get_model_names,
    load_model_data,
    load_model_regions,
    load_model_scenarios,
    load_models_info,
    make_regions_csv,
    process_raw,
    select,
    squash_scenarios,
)

item1_size = 928541
item2_size = 1994943


@pytest.fixture(scope="session")
def item1_data(item_tmp_dir):
    yield load_model_data(1)


@pytest.mark.skip("Requires synthetic model data.")
@pytest.mark.parametrize(
    "model", ["bp", "eia", "exxonmobil", "gcam", "get", "itf", "message", "roadmap"]
)
def test_process_raw(item_tmp_dir, model):
    process_raw(2, [model])
    assert exists(join(paths["model processed"], "2", "%s.csv" % model))


@pytest.mark.skip("Requires synthetic model data.")
@pytest.mark.slow
@pytest.mark.parametrize("model", ["eppa5"])
def test_process_raw_slow(item_tmp_dir, model):
    process_raw(2, [model])
    assert exists(join(paths["model processed"], "2", "%s.csv" % model))


@pytest.mark.skip("Requires synthetic model data.")
@pytest.mark.slow
def test_item1_dataframe(item_tmp_dir):
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


@pytest.mark.skip("Requires synthetic model data.")
@pytest.mark.slow
def test_item2(item_tmp_dir):
    # As a pd.DataFrame
    data = load_model_data(2, skip_cache=True)
    assert len(data) == item2_size


@pytest.mark.slow
@pytest.mark.xfail(reason="causes a MemoryError")
def test_item2_xr(item_tmp_dir):
    # As a dict() of xr.DataArray
    data = load_model_data(2, fmt=xr.DataArray)
    size = sum([d.notnull().sum() for d in data.values()])
    assert size == item2_size


@pytest.mark.parametrize("arg", [(1,), (2,), tuple()])
def test_get_model_names(arg):
    get_model_names(*arg)


def test_invalid_version():
    # Load an invalid model database version
    with pytest.raises(ValueError):
        load_model_data(99)


@pytest.mark.parametrize(
    "model",
    [
        "item",
        "message",
        pytest.param("foo", marks=pytest.mark.xfail(raises=ValueError)),
    ],
)
@pytest.mark.parametrize("version", [1, 2])
def test_load_model_regions(model, version):
    load_models_info()
    load_model_regions(model, version)


@pytest.mark.parametrize(
    "model",
    ["message", pytest.param("foo", marks=pytest.mark.xfail(raises=ValueError))],
)
@pytest.mark.parametrize("version", [1, 2])
def test_load_model_scenarios(model, version):
    load_models_info()
    load_model_scenarios(model, version)


def test_make_regions_csv(tmp_path):
    make_regions_csv(tmp_path / "output.csv")


@pytest.mark.skip("Requires synthetic model data.")
def test_select(item1_data):
    from item.model.dimensions import PAX

    data = select(item1_data, "energy", tech="All", fuel="All", mode=PAX)
    # print(data.head(), len(data))
    assert len(data) == 6752


@pytest.mark.skip("Requires synthetic model data.")
def test_squash_scenarios(item1_data):
    # The input data has multiple scenario names
    assert len(item1_data["scenario"].unique()) > 2

    squashed = squash_scenarios(item1_data, 1)

    assert sorted(squashed["scenario"].unique()) == ["policy", "reference"]
