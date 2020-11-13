"""Data cleaning code and configuration for T000."""
from item.utils import convert_units
from .util.managers.dataframe import ColumnName
from functools import lru_cache
import pandas as pd

#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    variable="Passenger Activity",
    # Add the same source to all rows since all data comes from the same source
    source="International Transport Forum",
    # Since all the data is associated to "Freight," the Service is "Freight"
    service="Passenger",
    # The dataset does not provide any data on the following columns, so we
    # add the default value of "All" in both cases
    technology="All",
    fuel="All",
    unit="10^9 passenger-km / yr",
)

#: Columns to drop from the raw data.
COLUMNS = dict(
    drop=[
        "COUNTRY",
        "VARIABLE",
        "YEAR",
        "Unit",
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


def check(df):
    # Input data have the expected units
    assert df["PowerCode"].unique() == ["Millions"]
    assert df["Unit"].unique() == ["Passenger-kilometres"]


def process(df):
    """Process data set T000."""
    # TODO The code below for identifying missing values is repeated in other
    # cleaning scripts. We should consider moving this code into the
    # 'item.historical import process' so that it applies to all scripts.

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

    # Assigning mode and vehicle type based on the variable name
    df = pd.concat([df, df["Variable"].apply(mode_and_vehicle_type)], axis=1)

    # 1. Drop null values.
    # 2. Convert to the preferred iTEM units.
    df = df.dropna().pipe(convert_units, "Mpassenger km/year", "Gpassenger km/year")

    return df


@lru_cache()
def mode_and_vehicle_type(variable_name):
    """Determine 'mode' and 'vehicle type' from 'variable'.

    The rules implemented are:

    ============================================= ===== ============
    Variable                                      Mode  Vehicle type
    ============================================= ===== ============
    Rail passenger transport                      Rail  All
    Road passenger transport by buses and coaches Road  Bus
    Road passenger transport by passenger cars    Road  LDV
    Total inland passenger transport              All   All
    ============================================= ===== ============
    """
    if "Rail" in variable_name:
        mode = "Rail"
        vehicle_type = "All"
    elif "Road" in variable_name:
        mode = "Road"

        if "by buses" in variable_name:
            vehicle_type = "Bus"
        elif "by passenger" in variable_name:
            vehicle_type = "LDV"
        else:
            vehicle_type = "All"
    else:
        mode = "All"
        vehicle_type = "All"

    return pd.Series(
        [vehicle_type, mode],
        index=[ColumnName.VEHICLE_TYPE.value, ColumnName.MODE.value],
    )
