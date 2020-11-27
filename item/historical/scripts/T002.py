"""Data cleaning code and configuration for T002."""
from .util.managers.dataframe import ColumnName
from functools import lru_cache
import pandas as pd

#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    # Add the same source to all rows since all data comes from the same source
    source="International Transport Forum",
    # Since all the data is associated to "Freight," the Service is "Freight"
    service="Freight",
    # The dataset does not provide any data on the following columns, so we
    # add the default value of "All" in both cases
    technology="All",
    fuel="All",
    vehicle_type="Container",
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

    # Assign the 'Mode' and 'Variable' columns
    df = pd.concat([df, df["Variable"].apply(mode_and_variable)], axis=1)

    # TODO Find a way on dealing with the "Variable" columns case in a better way
    # When the value for the "Variable" column is not unique, the code breaks.
    del df["Variable"]
    df.rename({"Var 2": ColumnName.VARIABLE.value}, axis=1, inplace=True)

    # Assign the 'Unit' column
    df = pd.concat([df, df["Unit"].apply(unit)], axis=1)

    # TODO same as in 'Variable' column
    del df["Unit"]
    df.rename({"Unit 2": ColumnName.UNIT.value}, axis=1, inplace=True)

    # 1. Drop null values.
    # 2. Convert to the preferred iTEM units.
    df = df.dropna()

    return df


@lru_cache()
def mode_and_variable(variable_name):

    # Mode
    if "Rail" in variable_name:
        mode = "Rail"
    else:
        mode = "Shipping"

    # Variable
    if "TEU" in variable_name:
        variable = "Freight (TEU)"
    else:
        variable = "Freight (Weight)"

    return pd.Series(
        [mode, variable],
        index=[ColumnName.MODE.value, "Var 2"],
    )


@lru_cache()
def unit(unit_name):

    if unit_name == "Tonnes":
        unit = "10^3 tonnes / yr"
    else:
        unit = unit_name

    return pd.Series(
        [unit],
        index=["Unit 2"],
    )
