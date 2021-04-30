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
    raise NotImplementedError
    # TODO rename "Date" → "Year"
    # TODO map "Measurement" column to "Unit":
    # - "absolute value" → "10^6 vehicle"
    # - "per 1000 inhabitants" → "vehicle / 1000 capita"
    # TODO map "Vehicle category" values to vehicle_type:
    # - Special purpose vehicles ---> Special purpose vehicles
    # - Passenger cars ---> LDV
    # - Trams ---> Trams
    # - Motorcycles ---> Motorcycles
    # - Motor coaches, buses and trolley bus ---> Bus
    # - Mopeds ---> Mopeds
