import pandas as pd

from .common import ModelInfo

INFO = ModelInfo(
    id="eia",
    format="xlsx",
    org="United States Department of Energy (DoE) Energy Information Administration (EIA)",
    versions=(2, 3),
)


def import_data(data_path, metadata_path):
    input_fn = data_path

    # Read data sheet
    data = pd.read_excel(input_fn, sheetname="data1")

    # Read comments sheet
    notes = (
        pd.read_excel(input_fn, "comments1")
        .dropna(subset=["Comments"])
        .drop(["Scenario", "Region"], axis="columns")
    )
    notes["Model"] = "WEPS+"

    return data, notes
