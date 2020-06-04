import pandas as pd


def import_data(data_path, metadata_path):
    input_fn = data_path

    data = pd.read_excel(input_fn, sheetname="data")
    data = data

    # Some of the cells in the 'Region' column contain excess white space;
    # remove it
    data["Region"] = data["Region"].astype(str).apply(lambda s: s.strip())

    data["Model"] = "ExxonMobil"
    data["Scenario"] = "Base"

    # Read comments sheet
    notes = (
        pd.read_excel(input_fn, "comments")
        .dropna(subset=["comments"])
        .drop(["Scenario", "Region"], axis="columns")
    )
    notes["Model"] = "ExxonMobil"

    return data, notes
