import os

import pandas as pd
import yaml


# Define the function used for converting a unit from raw to standard in iTEM3
# template
def unit_conversion(unitA, unitB):
    # Convert unitA to unitB
    if (unitA, unitB) == ("Gigawatt-hour", 'PJ / yr'):
        func = lambda x: x * 0.0036
    if (unitA, unitB) == ("Thousand TOE (tonnes of oil equivalent)",'PJ / yr'):
        func = lambda x: x * 0.0419
    if unitA == unitB:
        func = lambda x: x
    if ((unitA, unitB) == ('10⁶ tonne-km / yr', "10⁹ tonne-km / yr")) | ((unitA, unitB) == ('Million TKM (tonne-kilometre)',"10⁹ tonne-km / yr")) \
        | ((unitA, unitB) == ("10⁶ passenger-km / yr", "10⁹ passenger-km / yr")) | ((unitA, unitB) == ("Millions of passenger-kilometres","10⁹ passenger-km / yr")):
        func = lambda x: x / 1000
    if ((unitA, unitB) == ("10³ tonne / yr", "10⁹ tonne / yr")) | ((unitA, unitB) == ("Number", "10⁶ vehicle / yr"))  \
        | ((unitA, unitB) == ('Thousand tonnes', "10⁹ tonne / yr")) | ((unitA, unitB) == ("Number", "10⁶ vehicle")) \
        | ((unitA, unitB) == ("absolute value", "10⁶ vehicle")) | ((unitA, unitB) == ("per 1000 inhabitants","10⁶ vehicle / k inhabitants")):
        func = lambda x: x / 10**6
    return func


# For adding Unit column with defined one by the raw data set
def add_unit_conversion(row):
    info = top_dict["Added_columns_var_mapping"]["Unit"]
    if info["DEPEND"] == "None":
        value = info["MAPPING"]
    else:
        depended_field = info["DEPEND"]
        v = row[depended_field]
        value = info["MAPPING"][v]
    return value


# For converting Unit from raw to standard
def value_conversion(row):
    info = top_dict["Other_columns_var_mapping"]["Unit"]
    func = unit_conversion(row["Unit"], info["MAPPING"][row["Unit"]])
    return func(row["Value"])


# Function of conversion phase 1
def conversion_layer1(df, top_dict):
    # Input:
    #  df - raw data set loaded from IK2 Open Data
    #  top_dict - raw-data-set-dependent dictionary with mapping rules loaded
    #  from mapping_conv_phase1.yaml

    # Rename existing columns that to match the template
    col_dict = top_dict['Raw_columns_mapping']
    df = df.loc[:, [x for x in col_dict]]
    df.rename(columns=col_dict, inplace=True)

    # Add columns that are not included and mapping with pre-defined rules
    for col, value in top_dict['Added_columns_var_mapping'].items():
        if col == 'Unit':
            df[col] = df.apply(lambda row: add_unit_conversion(row), axis=1)
        else:
            df[col] = value

    # Unit conversion if necessary
    if "Unit" in top_dict["Other_columns_var_mapping"]:
        df["Value"] = df.apply(lambda row: value_conversion(row), axis=1)
    # Name conversion for some columns to keep as consistent as possible while
    # keeping the raw data set's taxonomy
    if "Other_columns_var_mapping" in top_dict:
        for field in top_dict["Other_columns_var_mapping"]:
            if field != "Unit":
                df[field] = df[field].apply(
                    lambda x: top_dict["Other_columns_var_mapping"][field][x])
            else:
                df[field] = df[field].apply(
                    lambda x:
                    top_dict["Other_columns_var_mapping"][field]["MAPPING"][x])
    return df


if __name__ == '__main__':
    datapath = "IK2_Open_Data/"
    dataList = os.listdir(datapath)
    dataList = [x for x in dataList if x[-4:] == ".csv"]
    top_most_dict_yaml = yaml.safe_load(open('mapping_conv_phase1.yaml'))
    list_of_df = []

    for file in top_most_dict_yaml:
        df = pd.read_csv(datapath + file, sep=";")
        top_dict = top_most_dict_yaml[file]  # Mapping rules for dataset
        df = conversion_layer1(df, top_dict)
        df["Source"] = file
        list_of_df.append(df)
    df_output = pd.concat(list_of_df, sort=False, ignore_index=True)
    df_output = df_output[["Model", "Scenario", "Region", "Variable", "Unit",
                           "Mode", "Technology", "Fuel", "Year", "Value",
                           "Source"]]
    df_output.to_csv("IK2_Open_Data_conv_phase1.csv", index=False)
