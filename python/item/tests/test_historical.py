import pandas as pd
import pytest
from requests import HTTPError

from item.historical import OpenKAPSARC


@pytest.fixture(scope='module')
def ok(pytestconfig):
    yield OpenKAPSARC(pytestconfig.getoption('--server', skip=True))


def test_datarepo(ok):
    ok.datarepo()


args = {
    'repo': 'ik2_open_data',
    'name': 'modal_split_of_freight_transport',
    }
total_rows = 1448


def test_dataset(ok):
    # Default number of rows is 20
    result = ok.table(**args)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 20

    # Other numbers of rows
    assert len(ok.table(**args, rows=10)) == 10
    assert len(ok.table(**args, rows=30)) == 30

    # Large number of rows returns all the rows in the table
    assert len(ok.table(**args, rows=5000)) == total_rows


def test_dataset_offset(ok):
    # Using an offset, only the remainder of rows in the table are returned
    offset = 100
    assert (len(ok.table(**args, rows=5000, offset=offset)) ==
            total_rows - offset)


def test_dataset_invalid_param(ok):
    # Invalid parameter value
    with pytest.raises(HTTPError,
                       message="500 Server Error: Internal Server Error"):
        ok.table(**args, rows=-1)
