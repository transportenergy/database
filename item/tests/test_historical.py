from importlib import import_module
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import item
from item.common import paths
from item.historical import fetch_source, input_file, process, source_str
from item.historical.diagnostic import coverage


@pytest.mark.slow
@pytest.mark.parametrize(
    "source_id",
    [
        # OECD via SDMX
        0,
        1,
        2,
        3,
        # OpenKAPSARC
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        pytest.param(16, marks=pytest.mark.slow),  # 1.2m records/161 MiB
        pytest.param(17, marks=pytest.mark.slow),  # 2.5m records/317 MiB
        18,
        19,
        20,
        21,
        22,
        23,
        24,
    ],
    ids=source_str,
)
def test_fetch(source_id):
    """Raw data can be fetched from individual sources."""
    fetch_source(source_id, use_cache=False)


def test_input_file(item_tmp_dir):
    # Create some temporary files in any order
    files = [
        "T001_foo.csv",
        "T001_bar.csv",
    ]
    for name in files:
        (paths["historical input"] / name).write_text("(empty)")

    # input_file retrieves the last-sorted file:
    assert input_file(1) == paths["historical input"] / "T001_foo.csv"


@pytest.mark.parametrize(
    "dataset_id",
    [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        pytest.param(
            9,
            marks=pytest.mark.xfail(
                reason="As of 2023-12-10, KAPSARC no longer provides this dataset"
            ),
        ),
        10,
        12,
    ],
)
def test_process(caplog, dataset_id):
    """Test common interface for processing scripts."""
    # Always use the path from within the repo
    paths["historical input"] = Path(item.__file__).parent.joinpath(
        "data", "historical", "input"
    )

    process(dataset_id)

    # Processing produced valid results that can be pivoted to wide format
    assert "Processing produced non-unique keys; no -wide output" not in caplog.messages


@pytest.mark.xfail(
    reason="Temporary, pending https://github.com/transportenergy/database/issues/88"
)
@pytest.mark.parametrize("dataset_id, N_areas", [(0, 59), (1, 39), (2, 54), (3, 59)])
def test_coverage(dataset_id, N_areas):
    """Test the historical.diagnostics.coverage method."""
    df = pd.read_csv(fetch_source(dataset_id, use_cache=True))
    result = coverage(df)
    assert result.startswith(f"{N_areas} areas: ")


@pytest.mark.parametrize(
    "id, N, query, expected",
    (
        ("A001", 1234, "REF_AREA == 'USA' and TIME_PERIOD == 2015", 0.9134),
        ("A002", 620, "REF_AREA == 'USA' and TIME_PERIOD == 2015", 51.737),
        pytest.param(
            "A003",
            950,
            "REF_AREA == 'USA' and TIME_PERIOD == 2015",
            0.02098,
            marks=pytest.mark.xfail(
                reason="As of 2023-12-10, KAPSARC no longer provides this dataset"
            ),
        ),
    ),
)
def test_diagnostic(id, N, query, expected):
    """Test checks from :mod:`.historical.diagnostic`."""
    module = import_module(f"item.historical.diagnostic.{id}")

    # Generate inputs
    inputs = [process(arg) for arg in module.ARGS]

    # Diagnostic can be computed
    result = module.compute(*inputs)

    # Number of unique values computed
    assert N <= len(result), result

    # A specific value is present and as expected
    obs = result.query(query)["VALUE"].squeeze()
    assert np.isclose(obs, expected, rtol=1e-3), result.query(query)
