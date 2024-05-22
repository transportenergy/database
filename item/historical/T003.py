"""Data cleaning code and configuration for T003.

The input data contains the variable names in :data:`VARIABLE_MAP`. A new sum is
computed, mode="Inland ex. pipeline" that is the sum of the variables in
:data:`PARTIAL`, i.e. excluding "Pipelines transport".
"""

from functools import lru_cache

import pandas as pd

from item.util import convert_units, dropna_logged

#: iTEM data flow matching the data from this source.
DATAFLOW = "ACTIVITY"

#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    source="International Transport Forum",
    variable="Activity",
    service="F",
    unit="Gt km / year",
    technology="_T",
    automation="_T",
)

#: Columns to drop from the raw data.
COLUMNS = dict(
    drop=[
        "COUNTRY",
        "VARIABLE",
        "YEAR",
        "Flag Codes",
        "Flags",
        "PowerCode",
        "PowerCode Code",
        "Reference Period Code",
        "Reference Period",
        "Unit Code",
        "Unit",
    ],
)

#: Mapping from Variable to mode and vehicle_type dimensions.
VARIABLE_MAP = {
    "Pipelines transport": dict(mode="Pipeline", vehicle="Pipeline"),
    "Rail freight transport": dict(mode="Rail"),
    "Road freight transport": dict(mode="Road"),
    "Road freight transport for hire and reward": dict(mode="Road", operator="HIRE"),
    "Road freight transport on own account": dict(mode="Road", operator="OWN"),
    "Inland waterways freight transport": dict(mode="Shipping", vehicle="Inland"),
    "Total inland freight transport": dict(mode="Inland"),
}

#: Variables to include in a partial sum.
PARTIAL = [
    "Rail freight transport",
    "Road freight transport",
    "Inland waterways freight transport",
]


def check(df):
    # Input data have the expected units
    assert df["PowerCode"].unique() == ["Millions"]
    assert df["Unit"].unique() == ["Tonnes-kilometres"]


def process(df):
    """Process data set T003.

    - Remove null values.
    - Convert units from Mt km / year to Gt km / year.
    - Lookup and assign “MODE” and “VEHICLE” dimensions based on “VARIABLE”, using
      :data:`VARIABLE_MAP`.
    - Compute partial sums that exclude pipelines.
    - Concatenate the partial sums to the original data.
    - Sort.
    """
    df = (
        df.pipe(dropna_logged, "Value", ["Country"])
        .pipe(convert_units, "Mt km / year", "Gt km / year")
        .rename(columns={"Year": "TIME_PERIOD"})
    )

    # Lookup and assign the mode and vehicle dimensions
    @lru_cache()
    def lookup(value):
        return pd.Series(VARIABLE_MAP[value])

    df = pd.concat([df, df["Variable"].apply(lookup)], axis=1)

    # Compute partial sums that exclude pipelines
    df0 = (
        # Select only the subset of variables, then group by Country and TIME_PERIOD
        df[df["Variable"].isin(PARTIAL)]
        .groupby(["Country", "TIME_PERIOD"])
        # Sum only the groups with all three variables
        .sum(min_count=len(PARTIAL))
        .dropna()
        # Return Country and Year to columns
        .reset_index()
        # Assign other dimensions for this sum
        .assign(mode="Inland ex. pipeline")
    )

    # - Concatenate with the original data.
    # - Fill "operator" and "vehicle" key values.
    # - Sort.
    return (
        pd.concat([df, df0], ignore_index=True)
        .fillna({"operator": "_T", "vehicle": "_T"})
        .sort_values(by=["Country", "TIME_PERIOD", "mode", "vehicle"])
    )
