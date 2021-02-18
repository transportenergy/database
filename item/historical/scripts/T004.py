"""Data cleaning code and configuration for T004.

Notes:

- The input data is does not express the units, which are single vehicles.
- Created during the tutorial on 2021-02-05.

"""
from functools import lru_cache

import pandas as pd

from .util.managers.dataframe import ColumnName

#: Separator character for :func:`pandas.read_csv`.
CSV_SEP = ";"

#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    mode="Road",
    source="UNECE",  # Agency id, not full name
    unit="vehicle",
    variable="Sales (New Vehicles)",
)

#: Columns to drop from the raw data.
COLUMNS = dict(
    drop=[
        "Frequency",
    ],
)

#: Mapping between existing values and values to be assigned.
MAP = {
    "Type of vehicle": {
        # Columns to which the values should be assigned
        "_columns": (ColumnName.SERVICE.value, ColumnName.VEHICLE_TYPE.value),
        # Key is the value appearing in the variable column; values are a tuple for the
        # two columns
        "New lorries (vehicle wt over 3500 kg)": ("Freight", "Heavy Truck"),
        "New road tractors": ("Freight", "Medium Truck"),
        "New passenger cars": ("Passenger", "LDV"),
        "New motor coaches, buses and trolley buses": ("Freight", "Bus"),
        "New light goods vehicles": ("Freight", "Light Truck"),
    },
    "Fuel type": {
        "_columns": (ColumnName.TECHNOLOGY.value, ColumnName.FUEL.value),
        "- LPG": ("Natural Gas Vehicle", "Natural Gas"),
        "- Compressed natural gas (CNG)": ("Natural Gas Vehicle", "Natural Gas"),
        "- Liquefied natural gas (LNG)": ("Natural Gas Vehicle", "Natural Gas"),
        "- Bioethanol": ("Conventional", "Liquid-Bio"),
        "- Bi-fuel vehicles": ("Conventional", "Liquid-Bio"),
        "- Biodiesel": ("Conventional", "Liquid - Fossil"),
        "- Diesel (excluding hybrids)": ("Conventional", "Liquid - Fossil"),
        "- Hybrid electric-diesel": ("Conventional", "Liquid - Fossil"),
        "- Hybrid electric-petrol": ("Conventional", "Liquid - Fossil"),
        "Diesel": ("Conventional", "Liquid - Fossil"),
        "Petrol": ("Conventional", "Liquid - Fossil"),
        "- Petrol (excluding hybrids)": ("Conventional", "Liquid - Fossil"),
        "- Plug-in hybrid diesel-electric": ("PHEV", "Electricity"),
        "- Plug-in hybrid petrol-electric": ("PHEV", "Electricity"),
        "- Hydrogen and fuel cells": ("Fuel Cell", "Hydrogen"),
        "- Electricity": ("BEV", "Electricity"),
        "Total": ("All", "All"),
        "Alternative (total)": ("Alternative", "Alternative"),
    },
}


def process(df):
    df = df.rename(columns={"Date": ColumnName.YEAR.value})

    # U
    return pd.concat(
        [
            df,
            df["Type of vehicle"].apply(map_column, args=("Type of vehicle",)),
            df["Fuel type"].apply(map_column, args=("Fuel type",)),
        ],
        axis=1,
    )


@lru_cache()
def map_column(value, column):
    """Apply mapping to `value` in `column`."""
    return pd.Series(MAP[column][value], index=MAP[column]["_columns"])
