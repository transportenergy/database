from functools import lru_cache

#: Separator character for :func:`pandas.read_csv`.
CSV_SEP = ";"

#: iTEM data flow matching the data from this source.
DATAFLOW = "STOCK"

#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    source="UNECE",
    variable="Stock",
    fuel="_T",
    mode="Road",
    service="P",
    technology="_T",
)


#: Columns to drop from the raw data.
COLUMNS = dict(drop=["Frequency"])


def check(df):
    # Canary checks for expected contents
    assert (df["Frequency"] == "Annual").all()


def process(df):
    return (
        df.rename(columns=dict(Date="TIME_PERIOD"))
        .assign(
            UNIT=df["Measurement"].apply(map_unit),
            VEHICLE=df["Vehicle Category"].apply(map_vehicle),
        )
        .drop(columns=["Measurement", "Vehicle Category"])
    )


@lru_cache()
def map_unit(value):
    return {
        "absolute value": "vehicle",
        "per 1000 inhabitants": "vehicle / kiloperson",
    }.get(value)


@lru_cache()
def map_vehicle(value):
    return {
        "Passenger cars": "LDV",
        "Motor coaches, buses and trolley bus": "Bus",
    }.get(value, value)
