import pandas as pd

from item.common import log


def import_data(data_path, metadata_path):
    input_fn = data_path

    # Read data sheets
    data = pd.read_excel(input_fn, ["data"] + ["data%d" % i for i in range(2, 8)])
    for sheet, df in data.items():
        log("Sheet %s: %d rows" % (sheet, df.shape[0]))
        data[sheet] = df

    # Read comments sheet
    notes = (
        pd.read_excel(input_fn, "comments")
        .dropna(subset=["comments"])
        .drop(["Scenario", "Region"], axis="columns")
    )
    notes["Model"] = "GET"
    notes["comments"] = notes["comments"].apply(str.strip)

    # Combine the sheets
    return pd.concat(data.values()), notes
