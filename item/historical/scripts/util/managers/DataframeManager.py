from enum import Enum
import os
import pandas as pd


class ColumnName(Enum):
    SOURCE = "Source"
    YEAR = "Year"
    ISO_CODE = "ISO Code"
    ITEM_REGION = "Region"
    VARIABLE = "Variable"
    UNIT = "Unit"
    VALUE = "Value"
    SERVICE = "Service"
    MODE = "Mode"
    VEHICLE_TYPE = "Vehicle Type"
    FUEL = "Fuel"
    TECHNOLOGY = "Technology"
    ID = "Id"
    COUNTRY = "Country"


class DataframeManager:

    def __init__(self, dataset_id):
        self.dataset_id = dataset_id
        self.column_order = [
                ColumnName.SOURCE.value,
                ColumnName.COUNTRY.value,
                ColumnName.ISO_CODE.value,
                ColumnName.ITEM_REGION.value,
                ColumnName.VARIABLE.value,
                ColumnName.UNIT.value,
                ColumnName.SERVICE.value,
                ColumnName.MODE.value,
                ColumnName.VEHICLE_TYPE.value,
                ColumnName.TECHNOLOGY.value,
                ColumnName.FUEL.value,
                ColumnName.VALUE.value,
                ColumnName.YEAR.value]

    def get_dataframe_from_csv_file(self, path_to_file, delimeter=","):
        if os.path.exists(path_to_file):
            return pd.read_csv(path_to_file, delimeter)
        else:
            return pd.DataFrame({'Empty': []})

    def simple_column_insert(
                            self, dataframe,
                            column_name, cell_value, position=0):
        column_content = [cell_value] * len(dataframe)
        dataframe.insert(position, column_name, column_content, True)

    def reorder_columns(self, dataframe):
        return dataframe.reindex(columns=self.column_order)

    def rename_column(self, df, current_name, new_name):
        df.rename(columns={current_name: new_name}, inplace=True)

    def create_programming_friendly_file(self, dataframe):
        dataframe[ColumnName.ID.value] = [self.dataset_id] * len(dataframe)
        filename = "{}_cleaned_PF.csv".format(self.dataset_id)
        cwd = os.getcwd()
        path = "{}/{}".format(cwd, filename)
        dataframe.to_csv(path, index=False)
        return "File saved at: {}".format(cwd)

    def create_user_friendly_file(self, df, path=None):
        # Get the columns to preserve
        columns_to_preserve = self.column_order.remove(ColumnName.YEAR.value)

        # Grouping by country
        group_by_country = df.groupby(df[ColumnName.COUNTRY.value])

        # Getting the list of countries
        list_of_countries = list(group_by_country.groups.keys())

        # Saving the dict of all the final dataframes of each country
        dict_of_final_dataframes_per_country = {}

        # For each country, perform the following algorithm
        for country in list_of_countries:

            # Get the df corresponding to the given country
            df_country_X = group_by_country.get_group(country)

            # Get the list of years available for the given year
            list_of_years_for_country_X = list(
                                   set(df_country_X[ColumnName.YEAR.value]))

            # Group the data of country X by year
            group_by_year_country_X = df_country_X.groupby(
                                        df_country_X[ColumnName.YEAR.value])

            # Create a structure that will hold the dataframes of each year
            df_per_year_for_country_X = {}

            # Obtain the dataframe for each year
            for name, group in group_by_year_country_X:
                df_per_year_for_country_X[name] = group

            # Do the necessary processing required in the DF of each year
            for year in list_of_years_for_country_X:

                # Obtain the dataframe for country X in year Y
                df_country_X_in_year_Y = df_per_year_for_country_X[year]

                # Renaming and droping columns
                df_country_X_in_year_Y.rename(
                        columns={ColumnName.VALUE.value: year}, inplace=True)
                df_country_X_in_year_Y.drop(
                        columns=[ColumnName.YEAR.value], inplace=True)

            # Concatenating all the dataframes of a given country into a df
            list_of_all_df_for_country_X = list(
                                            df_per_year_for_country_X.values())
            df_concat_all_df_for_country_x = pd.concat(
                                                  list_of_all_df_for_country_X,
                                                  sort=False,
                                                  verify_integrity=True,
                                                  join='outer')

            # Creating the final df for country X by eliminating all NAN and
            # combining rows
            step1 = df_concat_all_df_for_country_x.groupby(columns_to_preserve)
            step2 = step1[list_of_years_for_country_X]
            final_df_country_x = step2.first().reset_index()

            # Saving the final df of country X in the list of all countries df
            dict_of_final_dataframes_per_country[country] = final_df_country_x

        # Concatenate all the dataframes of the countries
        list_df_for_all_countries_final = list(
                                 dict_of_final_dataframes_per_country.values())
        df_with_all_countries_data = pd.concat(
                                     list_df_for_all_countries_final,
                                     sort=False, verify_integrity=True,
                                     join='outer', ignore_index=True)

        # Ensuring all columns are in the correct order
        all_column_names = set(df_with_all_countries_data.keys())
        list_of_none_year_columns = self.column_order.remove(
                                                         ColumnName.YEAR.value)
        none_year_columns = set(list_of_none_year_columns)
        numberic_columns = list(all_column_names - none_year_columns)
        numberic_columns.sort()
        df_with_all_countries_data = self.reorder_columns(
                                                    df_with_all_countries_data)

        # Setting the column id for the dataframe
        id_column = [self.dataset_id] * len(df_with_all_countries_data)
        df_with_all_countries_data[ColumnName.ID.value] = id_column

        # Exporting the final dataframe
        filename = "{}_cleaned_PF.csv".format(self.dataset_id)
        cwd = os.getcwd()
        path = "{}/{}".format(cwd, filename)
        df_with_all_countries_data.to_csv(path, index=False)
        return "File saved at: {}".format(cwd)
