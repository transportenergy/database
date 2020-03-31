import pandas as pd

from item.common import paths
from item.historical.scripts.util.managers.country_code import \
    CountryCodeManager
from item.historical.scripts.util.managers.dataframe import (
    ColumnName,
    DataframeManager,
)


# Variables used all over the notebook
DATASET_ID = "T001"
dataframeManager = DataframeManager(DATASET_ID)
countryCodeManager = CountryCodeManager()


# Dimensions and attributes which do not vary across this data set
COMMON = dict(
    variable='Freight Activity',
    # Rule: Add the same source to all rows since all data comes from the same
    # source
    source='International Transport Forum',
    # Rule: Since all the data is associated to "Freight," the Service is
    # "Freight"
    service='Freight',
    # Rule: The dataset does not provide any data about those two columns, so
    # we added the default value of "All" in both cases
    technology='All',
    fuel='All',
    # Rule: Since all the data is about shipping, all rows have "Shipping" as
    # mode
    mode='Shipping',
    # Rule: Since all the data in this dataset is associted to coastal
    # shipping, the vehicle type is "Coastal"
    vehicle_type='Coastal',
)


def assign(dim):
    """Assign a single value for dimension *dim*."""
    name = getattr(ColumnName, dim.upper()).value
    value = COMMON[dim]

    # Use the DataframeManager class
    # dataframeManager.simple_column_insert(df, name, value)

    # Use built-in pandas functionality, which is more efficient
    global df
    df = df.assign(**{name: value})

    # The Jupyter notebook echoes the data frame after each such step
    # print(df)


# Creating the dataframe and viewing the data

# Creating a dataframe from the csv data
path = paths['data'] / 'historical' / 'input' / 'T001_input.csv'
df = pd.read_csv(path)

# Removing all unnecessary columns
#
# Rule: To comply with the latest template, we will drop all the
# unnecessary columns and rename others.

# Droping the repeated columns
columns_to_delete = [
    "COUNTRY",
    "YEAR",
    "VARIABLE",
    "Reference Period Code",
    "Unit Code",
    "Reference Period",
    "Flag Codes",
    "Flags",
    "PowerCode Code",
]
df.drop(columns=columns_to_delete, inplace=True)

# Getting a generic idea of what countries are missing values and dropping
# NaN values
#
# Rule: Erase all value with NaN

list_of_countries_with_missing_values = list(
    set(df[df['Value'].isnull()]["Country"]))
print(">> Number of countries missing values: {}"
      .format(len(list_of_countries_with_missing_values)))
print(">> Countries missing values:")
print(list_of_countries_with_missing_values)
print(">> Number of rows to erase: {}".format(len(df[df['Value'].isnull()])))

# Dropping the values
df.dropna(inplace=True)

# Insert columns
assign('source')
assign('service')
assign('technology')
assign('fuel')

# Setting the correct unit name in the "Unit" column
#
# Rule: Based on the template, the correct unit for "Fraight Activity" is
# "10^9 tonne-km / yr", so we will assign those units to the data

# Dropping the current "Unit" column
df.drop(columns=["Unit"], inplace=True)

# Adding the new "Unit" column
df[ColumnName.UNIT.value] = ["10^9 tonne-km / yr"]*len(df)

# Setting the correct magnitude of the "Value" column
#
# Rule: The current data is in million. We will convert all values to billions.
# In which (1M = 0.001B)

# Removing the "PowerCode" column since it is not necessary
df.drop(columns=["PowerCode"], inplace=True)

# Looping though each row and convert each value to billion magnitude
for index, row in df.iterrows():
    current_value = row.Value
    new_value = current_value * float(0.001)
    df.Value[index] = new_value

# Insert columns
assign('mode')
assign('vehicle_type')

# Renaming the column "Variable"
#
# Rule: There is only one activity being perform in this dataset and that is
# the "Freight Activity". We are setting, for each row, the variable "Freight
# Activity"

# Dropping the current "Variable" column
df.drop(columns=["Variable"], inplace=True)

# Adding the new "Variable" column with the new data
assign('variable')

# Getting the ISO code for each country
# Rule: For each country, we need to assign their respective ISO Code

# Determining which countries do not appear in the list of ISO Code
#
# As seen from the code below, four countries appear to not have ISO code.
# However, the reason is because the countries are written in a format that is
# not understandable. So, this is how each those "missing" countries will be
# called in order to obtain their ISO code
#
#     Original Name --> New name
#         > Montenegro, Republic of --> Montenegro
#         > Korea --> Korea, Republic of
#         > Serbia, Republic of --> Serbia

# Getting the list of countries available
list_of_countries = list(set(df["Country"]))

# Getting the list of countries with no ISO code
countries_with_no_ISO_code = \
    countryCodeManager.get_list_of_countries_with_no_iso_code(
        list_of_countries)

# Print this list of countries with no ISO codes
countries_with_no_ISO_code

# Adding the ISO column to the df

dirty_list_of_all_countries = df["Country"]
clean_list_of_all_countries = []

for country in dirty_list_of_all_countries:
    if country == "Montenegro, Republic of":
        clean_list_of_all_countries.append("Montenegro")
    elif country == "Bosnia-Herzegovina":
        clean_list_of_all_countries.append("Bosnia and Herzegovina")
    elif country == "Korea":
        clean_list_of_all_countries.append("Korea, Republic of")
    elif country == "Serbia, Republic of":
        clean_list_of_all_countries.append("Serbia")
    else:
        clean_list_of_all_countries.append(country)

# Ensure the size of the cleaned list is the same as the dirty list
assert len(clean_list_of_all_countries) == len(dirty_list_of_all_countries)

# Assert that for all elements in the new list, no country is left without an
# ISO code
assert len(
    countryCodeManager.get_list_of_countries_with_no_iso_code(
        clean_list_of_all_countries)) == 0

# Getting the list of iso codes
list_of_iso_codes = \
    countryCodeManager.get_list_of_iso_for_countries(
        clean_list_of_all_countries)

# Adding the column to the dataframe
df[ColumnName.ISO_CODE.value] = list_of_iso_codes

# Getting the ITEM region for each country
#
# Rule: For each country, we need to assign an ITEM region

# Determining which countries are missing an ITEM region
#
# As seen from the cell below, there is no country that does no have a
# respective ITEM region. Therefore, no further cleaning needs to be done to
# get the item regions.

# Getting the list of ISO codes
list_of_iso_codes = list(set(df["ISO Code"]))

# Getting the list of ISO code with no region
iso_code_with_no_region = \
    countryCodeManager.get_list_of_iso_codes_with_no_region(list_of_iso_codes)

# printing the list of ISO codes
iso_code_with_no_region

# Adding the ITEM region column to the dataset

# Getting the complete list of iso codes
list_of_all_codes = df["ISO Code"]

item_region = \
    countryCodeManager.get_list_of_regions_for_iso_codes(list_of_all_codes)

# Adding the column to the dataframe
df[ColumnName.ITEM_REGION.value] = item_region

# Reordering the columns
#
# Rule: The columns should follow the order established in the latest
# template

df = dataframeManager.reorder_columns(df)

# Exporting results

# Programming Friendly View
dataframeManager.create_programming_friendly_file(df)

# User Friendly View
dataframeManager.create_user_friendly_file(df)
