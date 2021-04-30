"""Data cleaning code and configuration for T009."""
from functools import lru_cache

#: Fetch directly from the source, or cache.
FETCH = True

COMMON_DIMS = dict(
    fuel="All",
    mode="Road",
    source="United Nations Economic Commission for Europe",
    variable="Stock",
    unit="10^3 vehicle",
)


COLUMNS = dict(
    rename=dict(
        country_name="Country",
        date="Year",
        type_of_vehicle_name="Vehicle type",
        value="Value",
    ),
)


@lru_cache()
def service(value):
    """Determine 'service' dimension based on a vehicle type."""
    if value in [
        "Light goods road vehicles",
        "Lorries (vehicle wt over 3500 kg)",
        "Road tractors",
    ]:
        return "Freight"
    elif value in ["Motor coaches, buses and trolleybuses", "Passenger cars"]:
        return "Passenger"
    else:
        raise ValueError(value)


def process(df):
    df = df.rename(columns=COLUMNS["rename"])

    # Strip "- " prefix from Fuel strings
    df["Technology"] = df["fuel_type_name"].str.lstrip("- ").replace({"Total": "All"})

    df["Service"] = df["Vehicle type"].apply(service)

    return df
