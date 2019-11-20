import os

from click.testing import CliRunner
import pandas as pd
import pytest

import item.cli
from item.openkapsarc import OpenKAPSARC


@pytest.fixture(scope='module')
def ok():
    yield OpenKAPSARC(api_key=os.environ.get('OK_API_KEY', None))


def test_datasets(ok):
    ok.datasets()


def test_dataset(ok):
    # Retrieve single dataset
    result = ok.table('modal-split-of-freight-transport')
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1406


def test_cli(ok):
    runner = CliRunner()
    result = runner.invoke(item.cli.main, ['historical', 'demo'])
    assert result.exit_code == 0
