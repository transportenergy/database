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
