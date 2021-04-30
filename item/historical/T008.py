from functools import lru_cache

from item.structure import column_name

#: Separator character for :func:`pandas.read_csv`.
CSV_SEP = ";"


#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    source="UNECE",
    variable="Stock",
    service="Passenger",
    technology="All",
    fuel="All",
    mode="Road",
)


#: Columns to drop from the raw data.
COLUMNS = dict(
    drop=["Frequency"],
)


def check(df):
    # Canary checks for expected contents
    assert (df["Frequency"] == "Annual").all()


def process(df):
    return (
        df.rename(columns=dict(Date=column_name("YEAR")))
        .assign(
            unit=df["Measurement"].apply(map_unit),
            vehicle_type=df["Vehicle Category"].apply(map_vehicle_type),
        )
        .drop(columns=["Measurement", "Vehicle Category"])
    )


@lru_cache()
def map_unit(value):
    return {
        "absolute value": "10^6 vehicle",
        "per 1000 inhabitants": "vehicle / kiloperson",
    }.get(value)


@lru_cache()
def map_vehicle_type(value):
    return {
        "Passenger cars": "LDV",
        "Motor coaches, buses and trolley bus": "Bus",
    }.get(value, value)
