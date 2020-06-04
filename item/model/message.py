import pandas as pd


def import_data(data_path, metadata_path):
    input_fn = data_path

    data = pd.read_excel(input_fn, sheetname=["data_Base", "data_2C"])

    # Read comments sheet
    notes = (
        pd.read_excel(input_fn, "comments")
        .dropna(subset=["comments"])
        .drop(["Scenario", "Region"], axis="columns")
    )
    notes["Model"] = "MESSAGE"

    return pd.concat(data.values()), None
