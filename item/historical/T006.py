from functools import lru_cache

import pandas as pd

from item.structure import column_name

#: Separator character for :func:`pandas.read_csv`.
CSV_SEP = ";"


#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    source="Eurostat",
    service="Freight",
    technology="All",
    vehicle_type="All",
    variable="Activity, share of volume",
    unit="percent",
)

#: Columns to drop from the raw data.
COLUMNS = dict(
    drop=["Frequency", "Measure"],
)


def check(df):
    # Canary checks for expected contents
    assert (df["Frequency"] == "Annual").all()
    assert (df["Measure"] == "Percentage").all()


def process(df):
    # TODO handle the following:
    # - 'European Union (current composition)'
    # - 'Germany (until 1990 former territory of the FRG)'
    return (
        pd.concat([df, df["Tra Mode"].apply(map_mode_vehicle_type)], axis=1)
        .rename(columns={"Tra Mode": "Tra_Mode"})
        .query("Tra_Mode != 'Railways, inland waterways - sum of available data'")
        .drop(columns=["Tra_Mode"])
        .rename(columns=dict(Geo=column_name("COUNTRY"), Date=column_name("YEAR")))
    )


@lru_cache
def map_mode_vehicle_type(value):
    return pd.Series(
        {
            "Railways": ["Rail", "All"],
            "Roads": ["Road", "LDV"],
            "Inland waterways": ["Shipping", "All"],
        }.get(value),
        index=[column_name("MODE"), column_name("VEHICLE_TYPE")],
    )
