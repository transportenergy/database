"""Data cleaning code and configuration for T010."""
from item.utils import convert_units
from .util.managers.dataframe import ColumnName
from functools import lru_cache
import pandas as pd

#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    source="International Organization of Motor Vehicle Manufacturers",
    variable="Stock",
    service="Freight",
    fuel="All",
    technology="All",
    vehicle_type="All",
    unit="10^6 vehicle",
    mode="Road",
)

#: Columns to drop from the raw data.
COLUMNS = dict(
    drop=[],
    # Column containing country name for determining ISO 3166 alpha-3 codes and
    # iTEM regions. Commented, because this is the default value.
    # country_name='Country',
)


def process(df):
    """Process data set T010."""

    # Set the Country column
    df = pd.concat([df, df["REGIONS/COUNTRIES"].apply(country_column)], axis=1)

    # Transform the dataframe to PF format.
    df = transform_df_to_PF_format(df)

    # Remove the ',' from the values in the 'Value' column
    df["Value"] = df["Value"].apply(
        lambda x: x if type(x) != str else float(x.replace(",", ""))
    )

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
    df = df.dropna().pipe(convert_units, "Mvehicle ", "Gvehicle ")

    return df


@lru_cache()
def country_column(country):
    return pd.Series(
        [country.capitalize()],
        index=[ColumnName.COUNTRY.value],
    )


def transform_df_to_PF_format(df):
    all_data_frames = []
    counter = 0
    for index, row in df.iterrows():
        original_row = dict(row)
        list_of_year_value = []
        for column in list(original_row.keys()):
            if column.isdigit():
                list_of_year_value.append(column)
                del original_row[column]

        for year in list_of_year_value:
            newdict = original_row.copy()
            newdict[ColumnName.YEAR.value] = year
            newdict[ColumnName.VALUE.value] = row[year]
            local_df = pd.DataFrame(newdict, index=[counter])
            all_data_frames.append(local_df)
            counter = counter + 1

    df_new = pd.concat(all_data_frames)
    return df_new
