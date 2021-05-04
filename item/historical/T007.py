from functools import lru_cache

import pandas as pd

#: Separator character for :func:`pandas.read_csv`.
CSV_SEP = ";"

#: iTEM data flow matching the data from this source.
DATAFLOW = "ACTIVITY"

#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    source="Eurostat",
    service="P",
    variable="Activity, share of distance",
    unit="percent",
    technology="_T",
    automation="_T",
    operator="_T",
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
    return pd.concat(
        [df.drop(columns=["Vehicle"]), df["Vehicle"].apply(map_mode_vehicle_type)],
        axis=1,
    ).rename(columns=dict(Geo="Country", Date="TIME_PERIOD"))


@lru_cache()
def map_mode_vehicle_type(value):
    return pd.Series(
        {
            "Trains": ["Rail", "_T"],
            "Passenger cars": ["Road", "LDV"],
            "Motor coaches, buses and trolley buses": ["Road", "BUS"],
        }.get(value),
        index=["MODE", "VEHICLE"],
    )
