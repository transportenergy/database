import os
import pandas as pd


class DatasetManager:

    def __init__(self, dataset_id):
        self.dataset_id = dataset_id

    def get_dataframe_from_csv_file(self, path_to_file, delimeter=","):
        if os.path.exists(path_to_file):
            return pd.read_csv(path_to_file, delimeter)
        else:
            return pd.DataFrame({'Empty': []})

    def create_user_friendly_file(self, dataframe, path):
        pass

    def create_programming_friendly_file(self, dataframe):
        dataframe["ID"] = [self.dataset_id] * len(dataframe)
        cwd = os.getcwd()
        filename = "{}_cleaned_PF_.csv".format(self.dataset_id)
        path = "{}/{}".format(cwd, filename)
        dataframe.to_csv(path, index=False)
        return "File saved at: {}".format(cwd)

    def get_iso_code_for_country(country_name):
        pass

    def get_item_region_for_iso_code(iso_code):
        pass
