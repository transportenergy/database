import pandas as pd

from .common import ModelInfo

INFO = ModelInfo(
    id="bp",
    format="xlsx",
    versions=(2,),
)


def import_data(data_path, metadata_path):
    input_fn = data_path

    # Read data sheet
    data = pd.read_excel(input_fn, sheetname="data")

    # Read comments sheet
    notes = (
        pd.read_excel(input_fn, "comments")
        .dropna(subset=["comments"])
        .drop(["Scenario", "Region"], axis="columns")
    )
    notes["Model"] = "BP"

    return data, notes
