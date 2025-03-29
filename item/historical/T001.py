"""Data cleaning code and configuration for T001.

This module:

- Detects and corrects :issue:`32`, a data error in the upstream source where China
  observation values for years 1990 to 2001 inclusive are too low by 2 orders of
  magnitude (see also :issue:`57`).

"""

import logging

from item.util import convert_units, dropna_logged

log = logging.getLogger(__name__)

#: iTEM data flow matching the data from this source.
DATAFLOW = "ACTIVITY"

#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    # TODO move the comments below into the #: comment above, so they also
    #      appear in the built documentation.
    # There is only one activity being perform in this dataset and that is the
    # "Freight Activity". We are setting, for each row, the variable "Freight
    # Activity"
    variable="Activity",
    # Add the same source to all rows since all data comes from the same source
    source="International Transport Forum",
    # Since all the data is associated to "Freight," the Service is "Freight"
    service="F",
    # The dataset does not provide any data about those two columns, so we
    # add the default value of "All" in both cases
    technology="_T",
    # Since all the data is about shipping, all rows have "Shipping" as mode
    mode="Shipping",
    # Since all the data in this dataset is associted to coastal shipping, the
    # vehicle type is "Coastal"
    vehicle="Coastal",
    automation="_T",
    operator="_T",
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
)

#: Flag for whether :issue:`32` is detected by :func:`check` and should be fixed by
#: :func:`process`.
FIX_32 = False


def check(df):
    """Check data set T001."""
    # Input data contain only the expected variable name
    assert df["Variable"].unique() == ["Coastal shipping (national transport)"], (
        "Values in 'Variable' column"
    )

    # Input data have the expected units
    assert df["PowerCode"].unique() == ["Millions"], "Values in 'PowerCode' column"
    assert df["Unit"].unique() == ["Tonnes-kilometres"], "Values in 'Unit' column"

    # Detect #32
    global FIX_32

    # Data for CHN, including one year before and after the error
    obs = df.query("COUNTRY == 'CHN' and Year >= 1985 and Year <= 2002").set_index(
        "Year"
    )["Value"]
    # Delete the erroneous data
    empty = obs.copy()
    empty.iloc[1:-1] = None

    # Expected values: interpolated between the two correct values
    expected = empty.interpolate("index")

    # Ratio of interpolated and observed values is about 100 for the years containing
    # the error
    check = (expected / obs).iloc[1:-1] >= 95

    if check.all():
        log.info("Confirmed 10² magnitude error in China 1990–2001")
        FIX_32 = True
    elif not check.any():
        log.info("10² magnitude error in China 1990–2001 absent")
    else:
        raise AssertionError(f"Ambiguous:\n{repr(check)}")


def process(df):
    """Process data set T001.

    - Drop null values.
    - Convert from Mt km / year to Gt km / year.
    """
    # Drop rows with nulls in "Value"; log corresponding values in "Country"
    # TODO read the preferred units (here 'Gt km / year') from a common location
    df = df.pipe(dropna_logged, "Value", ["Country"]).pipe(
        convert_units, "Mt km / year", "Gt km / year"
    )

    # Correct #32
    if FIX_32:
        corrected = df.query(
            "Country == 'China' and Year > 1985 and Year < 2002"
        ).copy()
        corrected["Value"] *= 100.0
        df.update(corrected)

    return df
