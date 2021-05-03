from functools import lru_cache

import pandas as pd

#: Separator character for :func:`pandas.read_csv`.
CSV_SEP = ";"

#: iTEM data flow matching the data from this source.
DATAFLOW = "ACTIVITY"

#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    source="Eurostat",
    service="F",
    variable="Activity, share of volume",
    unit="percent",
    technology="_T",
    automation="_T",
    operator="_T",
)

#: Columns to drop from the raw data.
COLUMNS = dict(drop=["Frequency", "Measure"])


def check(df):
    # Canary checks for expected contents
    assert (df["Frequency"] == "Annual").all()
    assert (df["Measure"] == "Percentage").all()


def process(df):
    return (
        pd.concat([df, df["Tra Mode"].apply(map_mode_vehicle_type)], axis=1)
        .rename(columns={"Tra Mode": "Tra_Mode"})
        .query("Tra_Mode != 'Railways, inland waterways - sum of available data'")
        .drop(columns=["Tra_Mode"])
        .rename(columns=dict(Geo="Country", Date="TIME_PERIOD"))
    )


@lru_cache()
def map_mode_vehicle_type(value):
    return pd.Series(
        {
            "Railways": ["Rail", "_T"],
            "Roads": ["Road", "LDV"],
            "Inland waterways": ["Shipping", "_T"],
        }.get(value),
        index=["MODE", "VEHICLE"],
    )
