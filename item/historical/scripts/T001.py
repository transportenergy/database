from item.historical.scripts.util.managers.dataframe import ColumnName


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

# Columns to drop
DROP_COLUMNS = [
    'COUNTRY',
    'YEAR',
    'VARIABLE',
    'Reference Period Code',
    'Unit Code',
    'Reference Period',
    'Flag Codes',
    'Flags',
    'PowerCode Code',
]


def assign(df, dim):
    """Assign a single value for dimension *dim*."""
    name = getattr(ColumnName, dim.upper()).value
    value = COMMON[dim]

    # Use the DataframeManager class
    # dataframeManager.simple_column_insert(df, name, value)

    # Use built-in pandas functionality, which is more efficient
    return df.assign(**{name: value})

    # The Jupyter notebook echoes the data frame after each such step
    # print(df)


def process(df):
    """Process data set T001."""
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
    print(">> Number of rows to erase: {}"
          .format(len(df[df['Value'].isnull()])))

    # Dropping the values
    df.dropna(inplace=True)

    # Insert columns
    df = df.pipe(assign, 'source') \
           .pipe(assign, 'service') \
           .pipe(assign, 'technology') \
           .pipe(assign, 'fuel')

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
    # Rule: The current data is in million. We will convert all values to
    # billions. In which (1M = 0.001B)

    # Removing the "PowerCode" column since it is not necessary
    df.drop(columns=["PowerCode"], inplace=True)

    # Looping though each row and convert each value to billion magnitude
    for index, row in df.iterrows():
        current_value = row.Value
        new_value = current_value * float(0.001)
        df.Value[index] = new_value

    # Insert columns
    df = df.pipe(assign, 'mode') \
           .pipe(assign, 'vehicle_type')

    # Renaming the column "Variable"
    #
    # Rule: There is only one activity being perform in this dataset and that
    # is the "Freight Activity". We are setting, for each row, the variable
    # "Freight Activity"

    # Dropping the current "Variable" column
    df.drop(columns=["Variable"], inplace=True)

    # Adding the new "Variable" column with the new data
    df = assign(df, 'variable')

    return df
