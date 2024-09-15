"""Data cleaning code and configuration for T002."""

from functools import lru_cache

import pandas as pd

from item.util import dropna_logged

#: iTEM data flow matching the data from this source.
DATAFLOW = "ACTIVITY"

#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    # Add the same source to all rows since all data comes from the same source
    source="International Transport Forum",
    # Since all the data is associated to "Freight," the Service is "Freight"
    service="Freight",
    vehicle="Container",
    # The dataset does not provide any data on the following columns, so we
    # add the default value of "All" in both cases
    automation="_T",
    fuel="_T",
    operator="_T",
    technology="_T",
)

#: Columns to drop from the raw data.
COLUMNS = dict(
    drop=[
        "COUNTRY",
        "VARIABLE",
        "YEAR",
        "Unit Code",
        "PowerCode Code",
        "PowerCode",
        "Reference Period Code",
        "Reference Period",
        "Flag Codes",
        "Flags",
    ],
    # Column containing country name for determining ISO 3166 alpha-3 codes and
    # iTEM regions. Commented, because this is the default value.
    # country_name='Country',
)


def process(df):
    """Process data set T002."""
    df = df.pipe(dropna_logged, "Value", ["Country"])

    # Assign 'Mode', 'Variable', and 'Unit' values
    return pd.concat(
        [
            df.drop(columns=["Variable", "Unit"]),
            df["Variable"].apply(map_variable),
            df["Unit"].apply(map_unit),
        ],
        axis=1,
    )


@lru_cache()
def map_variable(value):
    return pd.Series(
        {
            "MODE": "Rail" if "Rail" in value else "Shipping",
            "VARIABLE": "Freight ({})".format("TEU" if "TEU" in value else "Weight"),
        }
    )


@lru_cache()
def map_unit(value):
    return pd.Series({"UNIT": "10^3 tonne / year" if value == "Tonnes" else value})
