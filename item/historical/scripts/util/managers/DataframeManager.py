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
        return "PF File saved at: {}".format(cwd)

    def create_user_friendly_file(self, df):
        pass
        # Exporting the final dataframe
        # filename = "{}_cleaned_PF.csv".format(self.dataset_id)
        # cwd = os.getcwd()
        # path = "{}/{}".format(cwd, filename)
        # df_with_all_countries_data.to_csv(path, index=False)
        # return " UF File saved at: {}".format(cwd)
