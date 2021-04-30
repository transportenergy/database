"""Data cleaning code and configuration for T003.

The input data contains the variable names in :data:`VARIABLE_MAP`. A new sum is
computed, mode="Inland ex. pipeline" that is the sum of the variables in
:data:`PARTIAL`, i.e. excluding "Pipelines transport".
"""
from functools import lru_cache

import pandas as pd

from item.historical.util import dropna_logged
from item.utils import convert_units

#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    source="International Transport Forum",
    fuel="All",
    technology="All",
    unit="Gt km / year",
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
    "Pipelines transport": dict(mode="Pipeline", vehicle_type="Pipeline"),
    "Rail freight transport": dict(mode="Rail", vehicle_type="All"),
    "Road freight transport": dict(mode="Road", vehicle_type="All"),
    "Road freight transport for hire and reward": dict(
        mode="Road", vehicle_type="For Hire and Reward"
    ),
    "Road freight transport on own account": dict(
        mode="Road", vehicle_type="For Own Account"
    ),
    "Inland waterways freight transport": dict(mode="Shipping", vehicle_type="Inland"),
    "Total inland freight transport": dict(mode="Inland", vehicle_type="All"),
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
    df = (
        # Remove rows with null values
        df.pipe(dropna_logged, "Value", ["Country"])
        # Set service dimension; overridden below
        .assign(Service="Freight")
        # Convert units
        .pipe(convert_units, "Mt km / year", "Gt km / year")
    )

    # Use "Pipeline" in the service dimension for some values of 'variable'
    df.loc[df["Variable"] == "Pipelines transport", "Service"] == "Pipeline"

    # Lookup and assign the mode and vehicle_type dimensions
    @lru_cache()
    def lookup(variable):
        return pd.Series(VARIABLE_MAP[variable])

    df = pd.concat([df, df["Variable"].apply(lookup)], axis=1)

    return (
        # Compute partial sums that exclude pipelines
        # Select only the subset of variables, then group by Country and Year
        df[df["Variable"].isin(PARTIAL)]
        .groupby(["Country", "Year"])
        # Sum only the groups with all three variables
        .sum(min_count=len(PARTIAL))
        .dropna()
        # Assign other dimensions
        .assign(
            mode="Inland ex. pipeline",
            Service="Freight",
            vehicle_type="All",
            Unit="Gt km / year",
        )
        # Return Country and Year to columns
        .reset_index()
        # Concatenate with the original data
        .append(df, ignore_index=True)
        # Assign common Variable value
        .assign(Variable="Freight Activity")
        # Rename columns
        .rename(
            columns=dict(mode="Mode", service="Service", vehicle_type="Vehicle Type")
        )
        # Sort
        .sort_values(by=["Country", "Year", "Mode", "Vehicle Type"])
    )
