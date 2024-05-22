"""Data cleaning code and configuration for T004.

Notes:

- The input data is does not express the units, which are single vehicles.

.. todo::
   - The input data have labels like "- LPG" in the "Fuel type" column, with the hyphen
     possibly indicating a hierarchical code list. Find a reference to this code list.
   - The code currently uses some inconsistent labels, such as:

     - "Liquid-Bio" (no spaces) vs. "Liquid - Fossil" (spaces).
     - "Natural Gas Vehicle" vs. "Conventional" (word "Vehicle" is omitted).

     Fix these after :pull:`62` is merged by using code lists for these dimensions.
   - Add code to fetch this source automatically. It does not have a clearly-defined
     API.
   - Capture and preserve the metadata provided by the UNECE data interface.

"""

from functools import lru_cache

import pandas as pd

#: Separator character for :func:`pandas.read_csv`.
CSV_SEP = ";"

#: iTEM data flow matching the data from this source.
DATAFLOW = "SALES"

#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    source="UNECE",  # Agency id, not full name
    variable="Sales",
    unit="vehicle",
    mode="Road",
    fleet="NEW",
)

#: Columns to drop from the raw data.
COLUMNS = dict(drop=["Frequency"])

#: Mapping between existing values and values to be assigned.
MAP = {
    "Type of vehicle": {
        # Dimensions to which the values should be assigned
        "_dims": ("SERVICE", "VEHICLE"),
        # Key is the value appearing in the variable column; values are a tuple for the
        # two columns
        "New lorries (vehicle wt over 3500 kg)": ("F", "Heavy Truck"),
        "New road tractors": ("F", "Medium Truck"),
        "New passenger cars": ("P", "LDV"),
        "New motor coaches, buses and trolley buses": ("F", "Bus"),
        "New light goods vehicles": ("F", "Light Truck"),
    },
    "Fuel type": {
        "_dims": ("TECHNOLOGY", "FUEL"),
        "Diesel": ("IC", "DIESEL"),
        "- Diesel (excluding hybrids)": ("NONHYB", "DIESEL"),
        "- Biodiesel": ("IC", "BIODIESEL"),
        "- Hybrid electric-diesel": ("HYBRID", "DIESEL"),
        "- Plug-in hybrid diesel-electric": ("PHEV-G", "ELEC"),
        "Petrol": ("IC", "GASOLINE"),
        "- Petrol (excluding hybrids)": ("NONHYB", "GASOLINE"),
        "- Bioethanol": ("IC", "BIOETH"),
        "- Hybrid electric-petrol": ("HYBRID", "PETROL"),
        "- Plug-in hybrid petrol-electric": ("PHEV-D", "ELEC"),
        "Alternative (total)": ("Alternative", "Alternative"),
        "- Bi-fuel vehicles": ("IC", "BIOFUEL"),
        "- Compressed natural gas (CNG)": ("IC", "CNG"),
        "- Electricity": ("BEV", "ELEC"),
        "- Hydrogen and fuel cells": ("FC", "H2"),
        "- Liquefied natural gas (LNG)": ("IC", "LNG"),
        "- LPG": ("IC", "LPG"),
        "Total": ("_T", "_T"),
    },
}


def process(df):
    df = df.rename(columns={"Date": "TIME_PERIOD"})

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
    return pd.Series(MAP[column][value], index=MAP[column]["_dims"])
