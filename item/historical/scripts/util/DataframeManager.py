from enum import Enum


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

    @classmethod
    def simple_column_insert(
                            cls, dataframe,
                            column_name, cell_value, position=0):
        column_content = [cell_value] * len(dataframe)
        dataframe.insert(position, column_name, column_content, True)

    @classmethod
    def reorder_columns(cls, dataframe):
        column_order = ['Source', 'Region', 'Variable',
                        'Unit', 'Service', 'Mode',
                        'Vehicle Type', 'Technology',
                        'Fuel', 'Value', 'Year']
        return dataframe.reindex(columns=column_order)

    @classmethod
    def rename_column(cls, df, current_name, new_name):
        df.rename(columns={current_name: new_name}, inplace=True)
