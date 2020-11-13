"""Data cleaning code and configuration for T001.

This module:

- Detects and corrects :issue:`32`, a data error in the upstream source where China
  observation values for years 1990 to 2001 inclusive are too low by 2 orders of
  magnitude.

"""
import logging

from item.utils import convert_units

log = logging.getLogger(__name__)


#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    # TODO move the comments below into the #: comment above, so they also
    #      appear in the built documentation.
    # There is only one activity being perform in this dataset and that is the
    # "Freight Activity". We are setting, for each row, the variable "Freight
    # Activity"
    variable="Freight Activity",
    # Add the same source to all rows since all data comes from the same source
    source="International Transport Forum",
    # Since all the data is associated to "Freight," the Service is "Freight"
    service="Freight",
    # The dataset does not provide any data about those two columns, so we
    # add the default value of "All" in both cases
    technology="All",
    fuel="All",
    # Since all the data is about shipping, all rows have "Shipping" as mode
    mode="Shipping",
    # Since all the data in this dataset is associted to coastal shipping, the
    # vehicle type is "Coastal"
    vehicle_type="Coastal",
)

#: Columns to drop from the raw data.
COLUMNS = dict(
    drop=[
        "COUNTRY",
        "VARIABLE",
        "YEAR",
        "Flag Codes",
        "Flags",
        "PowerCode Code",
        "PowerCode",
        "Reference Period Code",
        "Reference Period",
        "Unit Code",
        "Unit",
    ],
    # Column containing country name for determining ISO 3166 alpha-3 codes and
    # iTEM regions. Commented, because this is the default value.
    # country_name='Country',
)


def check(df):
    """Check data set T001."""
    # Input data contain only the expected variable name
    assert df["Variable"].unique() == ["Coastal shipping (national transport)"]

    # Input data have the expected units
    assert df["PowerCode"].unique() == ["Millions"]
    assert df["Unit"].unique() == ["Tonnes-kilometres"]

    # Detect #32
    # Data for CHN, including one year before and after the error
    obs = (
        df.query("COUNTRY == 'CHN' and Year >= 1985 and Year <= 2002")
        .set_index("Year")["Value"]
    )
    # Delete the erroneous data
    empty = obs.copy()
    empty.iloc[1:-1] = None

    # Expected values: interpolated between the two correct values
    expected = empty.interpolate("index")

    # Ratio of interpolated and observed values is about 100 for the years containing
    # the error.
    # TODO if the data is corrected in the original, this assertion will fail;
    #      then remove this code and the corresponding correction in process(), below.
    assert ((expected / obs).iloc[1:-1] >= 95).all()
    log.info("Confirmed 10² magnitude error in China 1990–2001")


def process(df):
    """Process data set T001."""
    # Getting a generic idea of what countries are missing values and dropping
    # NaN values
    #
    # Rule: Erase all value with NaN

    list_of_countries_with_missing_values = list(
        set(df[df["Value"].isnull()]["Country"])
    )
    print(
        ">> Number of countries missing values: {}".format(
            len(list_of_countries_with_missing_values)
        )
    )
    print(">> Countries missing values:")
    print(list_of_countries_with_missing_values)
    print(">> Number of rows to erase: {}".format(len(df[df["Value"].isnull()])))

    # 1. Drop null values.
    # 2. Convert to the preferred iTEM units.
    #    TODO read the preferred units (here 'Gt km / year') from a common
    #    location
    df = df.dropna().pipe(convert_units, "Mt km / year", "Gt km / year")

    # Correct #32
    corrected = df.query("Country == 'China' and Year > 1985 and Year < 2002")
    corrected["Value"] *= 100.0
    df.update(corrected)

    return df
