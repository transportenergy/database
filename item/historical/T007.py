#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    source="Eurostat",
    service="Passenger",
    technology="All",
    fuel="All",
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


def process(df):
    raise NotImplementedError
    # TODO rename "Geo" → "Country"
    # TODO rename "Date" → "Year"
    # TODO map the following:
    # - Vehicle --> Mode --> Vehicle Type
    # - Trains --> Rail --> All
    # - Passenger cars --> Road --> LDV
    # - Motor coaches, buses and trolley buses --> Road --> Bus
    # TODO the Jupyter notebook assigned units "% in total inland passenger-km / yr"
    #      —it's unclear what this means. Check.
