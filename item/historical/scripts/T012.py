"""Data cleaning code and configuration for T012."""
from item.utils import convert_units
from .util.managers.dataframe import ColumnName
import pandas as pd

#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    source="United Nations",
    variable="Population",
    unit="10^6 people",
)

#: Columns to drop from the raw data.
COLUMNS = dict(
    drop=[
        "Index",
        "Variant",
        "Notes",
        "Country code",
        "Parent code",
    ],
    # Column containing country name for determining ISO 3166 alpha-3 codes and
    # iTEM regions. Commented, because this is the default value.
    # country_name='Country',
)


def process(df):
    """Process data set T012."""

    # Erase unnecessary rows
    remove_unwanted_rows(df)

    # Rename the column with country names to to 'Country'
    df.rename(
        {"Region, subregion, country or area *": ColumnName.COUNTRY.value},
        axis=1,
        inplace=True,
    )

    # Transform the dataframe to PF format.
    df = transform_df_to_PF_format(df)

    # Remove the ',' from the values in the 'Value' column
    df["Value"] = df["Value"].apply(lambda x: int(x.replace(" ", "").replace(",", "")))

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
    df = df.dropna().pipe(convert_units, "Mpassenger", "Gpassenger")

    return df


def remove_unwanted_rows(df):
    # Getting the rows to be erased
    rows_to_erase = []

    # Getting all the rows to be erased
    for index, row in df.iterrows():
        if row["Type"] != "Country/Area":
            rows_to_erase.append(index)

    # Removing the unwanted rows
    df.drop(df.index[rows_to_erase], inplace=True)


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

    # Asserting that no info was missing. The 11 represents the default 11
    # non-numeric columns from the schema of the UF view
    # assert len(all_data_frames) == ((df.shape[1] - 11) * df.shape[0])
    df_new = pd.concat(all_data_frames)
    return df_new
