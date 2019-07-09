import pandas as pd
import pytest

from item.openkapsarc import OpenKAPSARC


@pytest.fixture(scope='module')
def ok():
    yield OpenKAPSARC()


def test_datasets(ok):
    ok.datasets()


def test_dataset(ok):
    # Retrieve single dataset
    result = ok.table('modal-split-of-freight-transport')
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1285
