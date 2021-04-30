#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    source="Eurostat",
    service="Freight",
    technology="All",
    vehicle_type="All",
    variable="Activity",
)

#: Columns to drop from the raw data.
COLUMNS = dict(
    drop=["Frequency", "Measure"],
)


def check(df):
    # Canary checks for expected contents
    assert (df["Frequency"] == "Annual").all()
    assert (df["Measure"] == "Percentage").all()
    assert (df["Variable"] == "Freight Activity").all()


def process(df):
    raise NotImplementedError

    df = df.query("'Tra Mode' != 'Railways, inland waterways - sum of available data'")
    # TODO rename "Geo" → "Country"
    # TODO rename "Date" → "Year"
    # TODO handle the following:
    # - 'European Union (current composition)'
    # - 'Germany (until 1990 former territory of the FRG)'
    # TODO the Jupyter notebook assigned units "% tonne-kilometres / year" —it's
    #      unclear what this means. Check.
    # TODO map the following
    #      Tra Mode --> Mode --> Vehicle Type
    #      Railways -> Rail --> All
    #      Roads -> Road --> All
    #      Inland waterways --> Shipping -> Inland Waterway
