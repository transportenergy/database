import logging

from item.util import convert_units, dropna_logged

log = logging.getLogger(__name__)

#: iTEM data flow matching the data from this source.
DATAFLOW = "ACTIVITY"
FETCH = True

#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    # TODO move the comments below into the #: comment above, so they also
    #      appear in the built documentation.
    # There is only one activity being perform in this dataset and that is the
    # "Freight Activity". We are setting, for each row, the variable "Freight
    # Activity"
    variable="Passenger Activity",
    # Add the same source to all rows since all data comes from the same source
    source="ATO",
    # Since all the data is associated to "Freight," the Service is "Freight"
    service="P",
    # The dataset does not provide any data about those two columns, so we
    # add the default value of "All" in both cases
    technology="_T",
    # Since all the data is about shipping, all rows have "Shipping" as mode
    mode="Aviation",
    # Since all the data in this dataset is associted to coastal shipping, the
    # vehicle type is "Coastal"
    vehicle="All",
    automation="_T",
    operator="_T",
    fleet="_T"
)

#: Columns to drop from the raw data.
COLUMNS = dict(
    drop=[
        "SCOPE",
        "MODE",
        "SECTOR",
        "UNITS",
        "SOURCE",
        "WEBSITE"
    ],
)


def check(df):
    # Input data have the expected units
    assert df["UNITS"].unique() == ["Million passenger kilometers"]


def process(df):
    # Drop rows with nulls in "Value"; log corresponding values in "Country"
    # TODO read the preferred units (here 'Gt km / year') from a common location
    df = df.pipe(dropna_logged, "value", ["ECONOMY"]).pipe(
        convert_units, "Mpassenger km/year", "Gpassenger km/year"
    )

    return df
