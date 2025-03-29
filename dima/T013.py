import pandas as pd
import os
import os.path
import yaml
from yaml.loader import SafeLoader
import pycountry
import math

class AtoWorkbook:
            
    # Function that loads rule book
    def load_rule_book(self, file_name: str):
        with open(file_name) as f:
            SOURCES = yaml.load(f, Loader=SafeLoader)
        return SOURCES

    # Function that loads yaml file containing mapping of ISO_Code with Regions
    def populate_regions(self, file_name: str):
        REGION = {}
        # Populate the map from the regions.yaml file
        with open(file_name, 'r', encoding='utf-8') as file:
            for region_name, info in yaml.load(file, Loader=SafeLoader).items():
                REGION.update({c: region_name for c in info["countries"]})
        return REGION
    
     #Function that extracts Country and Region using ISO_Code
    
    # Function that mapps ISO_Code to Country and Region
    def country_region_mapping(self, economy_code, regions):
        COUNTRY = dict()
        region_country_list = []

        country = pycountry.countries.get(alpha_3=economy_code)    
        country_name = country.name
        region_country_list = [country_name, regions[economy_code]]
        COUNTRY.update({economy_code: region_country_list})                       
        
        return COUNTRY
    
    # Function that returns ruleID, indicator_name and dictionary
    def get_rule_id(self, rule_book:dict):
        rule_id = "Txxx"
        valid_id_found = False

        for key, value in rule_book.items():        
            for new_key, new_val in value.items():
                if new_key == "name":
                    indicator_name = new_val                
                    dataset_name_split = new_val.split('-')
                    list_length = len(dataset_name_split)
                    for index in range(list_length):
                        if "Roads" in dataset_name_split[index]:
                            valid_id_found = True
                            rule_id = key
                            break    
                        else:
                            valid_id_found = False

            if valid_id_found:            
               break

        return rule_id, value, indicator_name
    
    # Function that returns Vehicle Type
    def get_vehicle_type(self, mode:str, item_value: dict , dataset_name: str):
        """Determine 'Vehicle type' from 'mode' and 'indicator'"""

        splited_indicator_name = dataset_name.split('-')
        first_indicator_word = splited_indicator_name[0]
        mode_indicator = mode + " " +  first_indicator_word
        mode_indicator = mode_indicator.rstrip()            
        VehicleType = "All"
        vehicle_type_found = False
        
        for new_key, new_val in item_value.items():
            if new_key == "VehicleType":
                # Check if new_val is a dictionary
                if isinstance(new_val, dict):
                    for key1, value1 in new_val.items():
                        if mode_indicator in key1:                                                            
                            VehicleType = value1              
                            vehicle_type_found= True
                            break 
                            
        return VehicleType

    # Function that returns Variable Type
    def get_variable_type(self, service_name: str, indicator_name: str):
        """Determine 'variable' using Service name.

        The rules implemented are:
        ============================================= ===== ============
        Variable types                                 
        ============================================= ===== ============
            Variable
            The variable is set to Passenger Activity.
        ============================================= ===== ============
        """
        variable = None  # Initialize variable to None

        if service_name == "Passenger" and "Passengers Kilometer Travel - Roads" in indicator_name:
            variable = "Passenger Activity"

        return variable
    
   # Function that returns unit and unit_factor
    def get_unit_and_unit_factor(self, item_value: dict, unit_name: str):
        """Determine 'expected unit' and 'unit factor' from 'Unit'.

        The rules implemented are:

        ============================================= ===== ============
        Unit                                    
        ============================================= ===== ============
        The unit is changed from Passenger Activity to 10^9 passenger-km / yr.
        # Unit: "Million passenger kilometers to 10^9 passenger-km / yr"
        ============================================= ===== ============
        """
        unit = "NA"
        unit_factor = 1     
        unit_found = False    
            
        for new_key, new_val in item_value.items():            
            if new_key == "Unit":
                for key1, value1 in new_val.items():
                    if unit_name in value1:
                        unit = "10^9 passenger-km / yr"
                        unit_factor = 1000                        
                        unit_found= True
                        break
            if unit_found:
               break
            
        return unit, unit_factor
    
    #Function that extracts upper part of the dataframe
    #And returns [mode_value, source_value, service_value, unit_value, indicator_value, sheet_name]
    def extract_upper_part_one(self, df_upper: pd.DataFrame):
        column_names= list(df_upper.columns.values)

        upper_part_attributes = []

        # Accessing the "Mode" attribute
        mode_value = df_upper.loc[4, column_names[1]]
        upper_part_attributes.append(mode_value)

        source_long_name = "Asian Transport Outlook National Database"
        if column_names[1] == source_long_name:
           source_short_name = "ATO"

        # Accessing the "Source:" attribute
        source_value = source_short_name + "2023 " + df_upper.loc[1, column_names[1]]
        upper_part_attributes.append(source_value)    
        
        # Accessing the "Sector or Service" attribute
        service_value = df_upper.loc[5, column_names[1]]
        upper_part_attributes.append(service_value)

        # Accessing the "Unit" attribute
        unit_value = df_upper.loc[6, column_names[1]]
        upper_part_attributes.append(unit_value)

        # Accessing the "Indicator" attribute
        indicator_value = df_upper.loc[0, column_names[1]]
        upper_part_attributes.append(indicator_value)

        # Accessing the "Indicator ATO Code:" attribute
        sheet_name = df_upper.loc[1, column_names[1]]
        upper_part_attributes.append(sheet_name)

        return upper_part_attributes 
      
    # Function that extracts remaing upper part of the dataframe
    # And returns [vehicle_type, variable_type, unit, unit_factor, rule_id]
    def extract_upper_part_two(self, upper_part_attributes: list, rule_book: dict):
        #[mode_value, source_value, service_value, unit_value, indicator_value, sheet_name]
        remaining_part_attributes = []

        rule_id, item_value, indicator_name = self.get_rule_id(rule_book)

        vehicleType = self.get_vehicle_type(upper_part_attributes[0], item_value, indicator_name)
        
        unit, unit_factor = self.get_unit_and_unit_factor(item_value, upper_part_attributes[3])

        variable_type = self.get_variable_type(upper_part_attributes[2], upper_part_attributes[4])

        remaining_part_attributes.append(vehicleType)    
        remaining_part_attributes.append(variable_type)
        remaining_part_attributes.append(unit)
        remaining_part_attributes.append(unit_factor)
        remaining_part_attributes.append(rule_id)

        return remaining_part_attributes

    #Function that updates correct coulumns to the lower dataframe
    def process_lower_part(self, df: pd.DataFrame):
        column_names_lower= list(df.columns.values)
        columun_length = len(column_names_lower)
        valid_column_length = 0
        updated_column_names= []

        for index in range(columun_length):
            #remove extra white space from the end of a string
            column_names_lower[index].rstrip()

            #For columns Economy Code and Economy Name
            if index < 2: 
                expected_column = df.loc[13, column_names_lower[index]]

                # Replace columun names of the dataframe with the correct column name
                df.rename(columns = {column_names_lower[index]:expected_column}, inplace = True)
                updated_column_names.append(expected_column)

            #For columns from 1990 upto 2022
            else:
                expected_column = df.loc[13, column_names_lower[index]]
                same_type = isinstance(expected_column, str)

                #Incase the column value is different from string
                if not same_type:
                    expected_column = math.trunc(expected_column) #remove decimal numbers  
                    expected_column = str(expected_column) #int into string casting
                
                try:
                    valid_columun = int(expected_column) #string into int casting
                    int_type = isinstance(valid_columun, int)
                    if int_type:
                        # Replace columun names of the dataframe with the correct column name
                        df.rename(columns = {column_names_lower[index]:expected_column}, inplace = True)
                        updated_column_names.append(expected_column) 
                except ValueError:
                    print("Invalid columun name for : " + expected_column)

        df_lower_updated = df[updated_column_names].copy()
        df_lower_new = df_lower_updated.drop([13])

        return df_lower_new, updated_column_names

    # Function that updates the output dataframe
    def update_master_data(self, df_out_put: pd.DataFrame, df: pd.DataFrame, column_list_names,
                        upper_attributes, remaining_attributes, regions):
        #[mode_value, source_value, service_value, unit_value, indicator_value, sheet_name]
        #[vehicle_type, variable_type, unit, unit_factor, rule_id, Data quality flag]

        # Iterate over columns and reorder them
        column_order = ['Country', 'ISO Code', 'Region', 'Variable', 'Unit', 'Vehicle Type', 
                    'Technology', 'Fuel', 'ID', 'Mode', 'Source', 'Service'] + column_list_names[2:] + ['Data quality flag']
        
        for index, row in df.iterrows():
            country_new = self.country_region_mapping(row['Economy Code'], regions)
            num_of_country =  len(country_new[row['Economy Code']])

            if num_of_country == 1:
                single_name = country_new[row['Economy Code']]
                for common_name in single_name:
                    region_name = common_name
                    country_name = common_name          
            else:
                country_name, region_name = country_new[row['Economy Code']]
            
            df_out_put.loc[index, ['Country']] = country_name
            df_out_put.loc[index, ['ISO Code']] = row['Economy Code']
            df_out_put.loc[index, ['Region']] = region_name

            df_out_put.loc[index, ['Variable']] = remaining_attributes[1]
            df_out_put.loc[index, ['Unit']] = remaining_attributes[2]
            df_out_put.loc[index, ['Vehicle Type']] = remaining_attributes[0]
            df_out_put.loc[index, ['Technology']] = "All"
            df_out_put.loc[index, ['Fuel']] = "All"
            df_out_put.loc[index, ['ID']] = remaining_attributes[4]

            df_out_put.loc[index, ['Mode']] = upper_attributes[0]
            df_out_put.loc[index, ['Source']] = upper_attributes[1]
            df_out_put.loc[index, ['Service']] = upper_attributes[2]

            col_length = len(df.columns)
    
            for idx in range(col_length):        
                if idx > 1:          
                    if not math.isnan(df.loc[index,column_list_names[idx]]):                 
                        unit_value = df.loc[index,column_list_names[idx]]
                        final_unit = unit_value / remaining_attributes[3]       
                        df_out_put.loc[index, column_list_names[idx]] = final_unit

            # Add the "Data quality flag" column with a desired value (e.g., "!" or "!!")
            df_out_put.loc[index, ['Data quality flag']] = '!'

        # Reorder the columns
        df_out_put = df_out_put[column_order]
        
        return df_out_put
        
    # Function that extract and process the input files and save the final data  
    def process_input_data(self, workbook_file: str, master_file: str, regions_file: str, source_file: str):
        # Steps followed for extracting and cleaning the dataset
        #Step 1) Load both ATO workbook excel sheet and master dataset csv files into Dataframes
        df = pd.read_excel(open(workbook_excel_file, 'rb'),sheet_name='TAS-PAG-005(2)')
        #df = pd.read_excel(open(r"workbook_excel_file", 'rb'),sheet_name='TAS-FRA-005(3)')
        #df = pd.read_excel(io=os.path.abspath('workbook_excel_file'),sheet_name='TAS-FRA-005(3)') 

        # Load the master data CSV file
        master_df = pd.read_csv(master_csv_file)
        master_column_names= list(master_df.columns.values)

        #Step 2) Create a new dataframe using master dataset column names
        df_out_put = pd.DataFrame(columns=master_column_names)

        #Step 3) Separate the ATO workbook dataframe into two parts
        #a) Upper part of the data frame containg 8 rows 
        df_upper = df.head(8)

        #The function returns a list of 
        #[mode_value, source_value, service_value, unit_value, indicator_value, sheet_name]
        upper_part_attributes = self.extract_upper_part_one(df_upper)

        regions = self.populate_regions(regions_file)

        rule_book = self.load_rule_book(source_file)

        remaining_part_attributes = self.extract_upper_part_two(upper_part_attributes, rule_book)

        # b) Lower part of the dataframe containing the remaining rows 
        # extract lower part of the dataframe
        df_lower = df.iloc[13:65]

        df_lower_new, updated_column_names = self.process_lower_part(df_lower)

        master_df_output = self.update_master_data(df_out_put, df_lower_new, updated_column_names,
                                        upper_part_attributes, remaining_part_attributes, regions)    

        master_df_output.to_csv("Output_data_"+ upper_part_attributes[5] + ".csv", index=False)

           
# Name and path of input files
workbook_excel_file = r"ATO Workbook (TRANSPORT ACTIVITY & SERVICES (TAS))2023.xlsx"
master_csv_file = r"master dataset.csv"
regions_file = r"regions.yaml"
source_file = r"sources.yaml"

# Check if the Excel file exists
if os.path.isfile(workbook_excel_file):
    
    # Process the input files and save output as csv file
    atoWorkBook = AtoWorkbook()
    atoWorkBook.process_input_data(workbook_excel_file, master_csv_file, regions_file, source_file)
    print("File is found.")
else:
    print("File is not found on the specified path!!")

##<<<<<<<<<<<<<<<<<<<<< //////////////////////// >>>>>>>>>>>>>>>>>>>>>>>>##
##<<<<<<<<<<<<<<<<<<<<< Programe ends here >>>>>>>>>>>>>>>>>>>>>>>>##
##<<<<<<<<<<<<<<<<<<<<< //////////////////////// >>>>>>>>>>>>>>>>>>>>>>>>##        
