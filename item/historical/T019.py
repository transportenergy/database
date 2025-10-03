import os

import pandas as pd
import yaml

EXCEL_SHEET_NAME = "ATO Workbook (TRANSPORT ACTIVITY & SERVICES (TAS))2023.xlsx"
REGION_YAML_FILE_NAME = "regions_roadmap.yaml"
RULEBOOK_YAML_FILE_NAME = "sources.yaml"
OUTPUT_FILE_NAME = "output_data_TAS-FRA-007(3).csv"


class ItemTransformer:

    def __init__(self, sheetname, file_name):
        self.sheetname = sheetname
        self.file_name = file_name

    def execute(self):
        excel_file = pd.ExcelFile(EXCEL_SHEET_NAME)
        region_yaml_data = self.load_yaml_to_cache(REGION_YAML_FILE_NAME)
        rule_book_yaml_data = self.load_yaml_to_cache(RULEBOOK_YAML_FILE_NAME)
        for sheet_name in excel_file.sheet_names:
            if sheet_name in [self.sheetname]:
                df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None, index_col=None)
                df = self.drop_empty_data(df)
                df_metadata_columns = self.load_metadata(df)
                df_data = self.load_data(df)
                df_data.to_csv('internal_df_data.csv', index=False, header=False)
                meta_data, applicable_rule = self.transform_metatdata(df_metadata_columns, rule_book_yaml_data)
                df_metadata_transformed = pd.DataFrame(meta_data)
                df_data_csv = pd.read_csv('internal_df_data.csv')
                os.remove("internal_df_data.csv")
                self.create_dummy_merge_column(df_metadata_transformed, df_data_csv)
                merged_df = pd.merge(df_metadata_transformed, df_data_csv, on='merge_column', how='right')
                merged_df.drop('merge_column', axis=1, inplace=True)
                self.transformation_data(region_yaml_data, merged_df, applicable_rule)
                merged_df.to_csv(self.file_name, index=False)
        print("Execution completed for sheet : "+ self.sheetname)
        """ ---------------------------------------------- """

    def load_metadata(self, df):
        df_metadata_rows = df.iloc[:8, :]
        df_metadata_columns = df_metadata_rows.iloc[:, [0, 1]]
        return df_metadata_columns

    def load_data(self, df):
        df_data_rows = df.iloc[12:64, :]
        df_data = df_data_rows.iloc[:, 0:35]
        return df_data

    def transform_metatdata(self, df_metadata_columns, rule_book_yaml_data):

        meta_data = {}
        source_value = None
        id_value = None
        applicable_rule = None
        indicator = ""
        for row in df_metadata_columns._values:
            if row[0] == "Indicator ATO Code:":
                source_value = [row[1]]
            elif row[0] == "Mode:":
                mode_value = [row[1]]
            elif row[0] == "Indicator:":
                key, value = self.find_matching_rule_by_indicator(row[1], rule_book_yaml_data)
                id_value = key
                indicator = row[1]
                applicable_rule = value
        meta_data["Source"] = [applicable_rule["Source Prefix"] + " " + source_value[0]]
        meta_data["Variable"] = applicable_rule["Variable"]
        meta_data["Unit"] = applicable_rule["Unit"]
        meta_data["Service"] = applicable_rule["Service"]
        meta_data["Mode"] = applicable_rule["Mode"]
        meta_data["Vehicle Type"] = self.get_vehicle_type(meta_data["Mode"], indicator, applicable_rule)
        meta_data["Technology"] = ["All"]
        meta_data["Fuel"] = ["All"]
        meta_data["ID"] = id_value
        return meta_data, applicable_rule

    def transformation_data(self, yaml_data, merged_df, applicable_rule):
        self.rename_and_reorder_columns(merged_df)
        unit = applicable_rule["Unit Factor"]
        for column_name in merged_df.columns:
            no_spaces = column_name.replace(" ", "")
            try:
                if not no_spaces.isalpha():
                    integer_number = int(column_name.split('.')[0])
                    if 1900 <= integer_number <= 2022:
                        merged_df[column_name] = merged_df[column_name] / unit
                        merged_df.rename(columns={column_name: integer_number}, inplace=True)
            except Exception as e:
                print(f"There is a exception transforming column : {column_name}")
            self.add_region_from_iso_code(column_name, merged_df, yaml_data)
        self.fill_years(merged_df, applicable_rule)


    def rename_and_reorder_columns(self, merged_df):
        merged_df.rename(columns={'Economy Code': 'ISO Code'}, inplace=True)
        merged_df.rename(columns={'Economy Name': 'Country'}, inplace=True)
        # Specify the column to be shifted
        country_to_shift = 'Country'
        ISO_code_to_shift = 'ISO Code'
        country_position = 1  # Specify the desired position (index) where the column should be moved
        ISO_position = 2  # Specify the desired position (index) where the column should be moved
        # Shift the column to the desired position
        merged_df.insert(country_position, country_to_shift, merged_df.pop(country_to_shift))
        merged_df.insert(ISO_position, ISO_code_to_shift, merged_df.pop(ISO_code_to_shift))
        if "Remarks" in merged_df.columns:
            merged_df.pop("Remarks")

    def add_region_from_iso_code(self, column_name, merged_df, yaml_data):
        if column_name == "ISO Code":
            region_list = []
            economy_code = merged_df[column_name]
            for code in economy_code:
                if code == "nan":
                    region_list.append("Not Found")
                match_found = False
                for key, value in yaml_data.items():
                    countries_economy_code = value["countries"]
                    if code in countries_economy_code:
                        match_found = True
                        region_list.append(key)
                        break
                if not match_found:
                    region_list.append("Not Found")
            merged_df.insert(3, "Region", region_list)

    def fill_years(self, merged_df, applicable_rule):
        fill_until_year = 0000
        fill_year_from_index = 0
        for index, column_name in enumerate(merged_df.columns):
            try:
                if isinstance(column_name, int):
                    fill_until_year = column_name
                    fill_year_from_index = index
                    break
            except Exception as e:
                print(f"There is a exception transforming column : {column_name}")
        fill_years_from = applicable_rule["Fill years from"]

        i = 0
        number_of_years_to_fill = fill_until_year - fill_years_from
        while i < number_of_years_to_fill:
            merged_df.insert(fill_year_from_index, fill_years_from, None)
            fill_years_from += 1
            i += 1
            fill_year_from_index += 1


    def create_dummy_merge_column(self, df_metadata_tranformed, df_data_csv):
        df_metadata_tranformed['merge_column'] = 1
        df_data_csv["merge_column"] = 1

    def drop_empty_data(self, df):
        # Drop empty columns and unnecessary rows
        return df.dropna(axis=1, how='all').dropna(axis=0, how='all')

    def load_yaml_to_cache(self, filename):
        yaml_file_path = f"config/{filename}"
        with open(yaml_file_path, 'r') as file:
            yaml_data_cache = yaml.safe_load(file)
        return yaml_data_cache

    def find_matching_rule_by_indicator(self, indicator, rule_book_yaml_data):
        match_found = False
        for key, inner_dict in rule_book_yaml_data.items():
            if inner_dict["Name"] in indicator:
                match_found = True
                return key, inner_dict
        if not match_found:
            print("Matching rule not found for the indicator present in your sheet")

    def get_vehicle_type(self, mode, indicator, applicable_rule):
        generated_vehicle_type = mode[0] + " " + indicator.split(' -')[0].lower()
        try:
            rule_vehicle_type_value = applicable_rule["Vehicle Type"][generated_vehicle_type]
            return rule_vehicle_type_value
        except KeyError as e:
            rule_vehicle_type_value = applicable_rule["Vehicle Type"]["Default"]
            return rule_vehicle_type_value



# Execute transformation for sheet 'TAS-FRA-007(3)'
SHEET_NAME = 'TAS-FRA-007(3)'
OUTPUT_FILE_NAME = "output_data_TAS-FRA-007(3).csv"
item_transformer = ItemTransformer(SHEET_NAME, OUTPUT_FILE_NAME)
""" ---------------------------------------------- """
print("Starting execution for sheet : "+ item_transformer.sheetname)
item_transformer.execute()



