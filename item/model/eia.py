import pandas as pd


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
