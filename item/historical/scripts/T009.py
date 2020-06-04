"""Data cleaning code and configuration for T009."""
#: Fetch directly from the source, or cache.
FETCH = True

COMMON_DIMS = dict(
    mode="Road",
    service="Freight",
    source="United Nations Economic Commission for Europe",
    variable="Stock",
    unit="10^3 vehicle"
)


COLUMNS = dict(
    drop=["frequency"],
    country_name="country_name",
    rename=dict(
        value="Value",
        date="Year",
        fuel_type_name="Fuel",
        type_of_vehicle_name="Vehicle Type",
    )
)


def process(df):
    df = df.rename(columns=COLUMNS["rename"])

    # Strip "- " prefix from Fuel strings
    df["Fuel"] = df["Fuel"].str.lstrip("- ")

    # TODO fill "Technology" dimension based on "Fuel" dimension

    return df
