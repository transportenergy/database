"""Data cleaning code and configuration for T009."""

from functools import lru_cache

#: Fetch directly from the source, or cache.
FETCH = True

#: iTEM data flow matching the data from this source.
DATAFLOW = "STOCK"

COMMON_DIMS = dict(
    mode="Road",
    source="United Nations Economic Commission for Europe",
    variable="Stock",
    unit="10^3 vehicle",
)


COLUMNS = dict(
    rename=dict(
        country_name="Country",
        date="TIME_PERIOD",
        type_of_vehicle_name="VEHICLE",
        value="VALUE",
    ),
)


@lru_cache()
def map_service(value):
    """Determine 'service' dimension based on a vehicle type."""
    if value in [
        "Light goods road vehicles",
        "Lorries (vehicle wt over 3500 kg)",
        "Road tractors",
    ]:
        return "F"
    elif value in ["Motor coaches, buses and trolleybuses", "Passenger cars"]:
        return "P"
    else:
        raise ValueError(value)


def process(df):
    """Process input data for data set T009.

    - Assign “SERVICE” based on “VEHICLE” values.
    - Assign “TECHNOLOGY” by stripping "- " prefix from “fuel_type_name” values.
    """
    return (
        df.rename(columns=COLUMNS["rename"])
        .assign(
            SERVICE=lambda df_: df_["VEHICLE"].apply(map_service),
            TECHNOLOGY=lambda df_: df_["fuel_type_name"]
            .str.lstrip("- ")
            .replace({"Total": "_T"}),
        )
        .drop(columns=["fuel_type_name"])
    )
