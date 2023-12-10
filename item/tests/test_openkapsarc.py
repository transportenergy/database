import os

import pandas as pd
import pytest
from click.testing import CliRunner

import item.cli
from item.remote import OpenKAPSARC


@pytest.fixture(scope="module")
def ok():
    yield OpenKAPSARC(api_key=os.environ.get("OK_API_KEY", None))


def test_datasets(ok):
    ok.datasets()


@pytest.mark.xfail(reason="As of 2023-12-10, KAPSARC no longer provides this dataset")
def test_dataset(ok):
    # Retrieve single dataset
    result = ok.table("modal-split-of-freight-transport")
    assert isinstance(result, pd.DataFrame)
    # NB sometimes 1406, sometimes 1458
    assert len(result) > 1400


@pytest.mark.xfail(reason="As of 2023-12-10, KAPSARC no longer provides this dataset")
def test_cli(ok):
    runner = CliRunner()
    result = runner.invoke(item.cli.main, ["remote", "demo"])
    assert result.exit_code == 0, result.output
