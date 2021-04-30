from functools import lru_cache

import pandas as pd

from item.structure import column_name

#: Separator character for :func:`pandas.read_csv`.
CSV_SEP = ";"

#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    source="Eurostat",
    service="Passenger",
    technology="All",
    fuel="All",
    variable="Activity, share of distance",
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
    return pd.concat([df, df["Vehicle"].apply(map_mode_vehicle_type)], axis=1).rename(
        columns=dict(Geo=column_name("COUNTRY"), Date=column_name("YEAR"))
    )


@lru_cache
def map_mode_vehicle_type(value):
    return pd.Series(
        {
            "Trains": ["Rail", "All"],
            "Passenger cars": ["Road", "LDV"],
            "Motor coaches, buses and trolley buses": ["Road", "LDV"],
        }.get(value),
        index=[column_name("MODE"), column_name("VEHICLE_TYPE")],
    )
