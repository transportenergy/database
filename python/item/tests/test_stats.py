import pandas as pd
import pytest

from item.stats import OpenKAPSARC

# Replace this with the string address of the server
# FIXME use a command-line argument via pytest
server = 'http://0.0.0.0:8080'


@pytest.fixture
def ok():
    return OpenKAPSARC(server)


def test_datarepo(ok):
    ok.datarepo()


def test_dataset(ok):
    args = {
        'repo': 'ik2_open_data',
        'name': 'modal_split_of_freight_transport',
        }

    # Default number of rows is 20
    result = ok.table(**args)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 20

    # Other numbers of rows
    assert len(ok.table(**args, rows=10)) == 10
    assert len(ok.table(**args, rows=30)) == 30
