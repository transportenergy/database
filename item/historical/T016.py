import pandas as pd
import os
import sys
import os.path
import yaml
from yaml.loader import SafeLoader
import pycountry
import math
from pathlib import Path  # Using pathlib for path manipulation

class AtoWorkbook:
            
    def __init__(self, workbook_file, master_file, regions_file, source_file, sheet_name, submodule_path):
        self.workbook_file = workbook_file
        self.master_file = master_file
        self.regions_file = regions_file
        self.source_file = source_file
        self.sheet_name = sheet_name
        self.submodule_path = submodule_path  

    # Function that loads yaml file containing mapping of ISO_Code with Regions
    def populate_regions(self): 
        regions = {}        

        try:
            with open(self.regions_file, 'r', encoding='utf-8') as file:            
                data = yaml.load(file, Loader=SafeLoader)
                for region_name, info in data.items():
                    regions.update({c: region_name for c in info.get("countries", [])})                    
        except FileNotFoundError:
            print(f"Error: File not found - {self.regions_file}")
        except yaml.YAMLError as e:
            print(f"Error loading YAML from {self.regions_file}: {e}")
        return regions
    
     #Function that extracts Country and Region using ISO_Code
    
     # Function that loads rule book
    def load_rule_book(self):
        with open(self.source_file) as f:
            SOURCES = yaml.load(f, Loader=SafeLoader)
        return SOURCES
    
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
                        if "LDV Sales" in dataset_name_split[index]:
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
        """Determine 'Vehicle type' from 'indicator'

        The rules implemented are:

        ============================================= ===== ============
        Vehicle type                                      
        ============================================= ===== ============
        The Vehicle Type for New Vehicle is: "LDV"
        ============================================= ===== ============
        """
        # Dataset name: LDV Sales
        splited_indicator_name = dataset_name.split(' ')
        first_indicator_word = splited_indicator_name[0]
            
        VehicleType = "NA"
        vehicle_type_found = False
        

        for new_key, new_val in item_value.items():
            if new_key == "name" and first_indicator_word in new_val:                                                            
               VehicleType = first_indicator_word              
               vehicle_type_found= True
               break 
                        
            if vehicle_type_found:
               break 
        
        return VehicleType

    # Function that returns Variable Type
    def get_variable_type(self, service_name: str, indicator_name: str):
        """Determine 'variable' using Service name and Indicator name.

        The rules implemented are:
        ============================================= ===== ============
        Variable types                                 
        ============================================= ===== ============
        Freight Activity
        Freight (TEU)
        Freight (Weight)
        Stock
        Sales (New Vehicles)
        ============================================= ===== ============
        """
        if service_name ==  "Freight":
            if "Freight Transport" in indicator_name:
                variable = "Freight Activity"
            elif "Freight (TEU)" in indicator_name:
                variable = "Freight (TEU)"
            elif "Freight (Weight)" in indicator_name:
                variable = "Freight (Weight)"
            elif "Stock" in indicator_name:
                variable = "Stock"
            elif "Sales (New Vehicles)" in indicator_name:
                variable = "Sales (New Vehicles)"
            else:
                variable = "Not Available" 
        elif service_name ==  "Passenger":
            if "Vehicle registration (LDV)" in indicator_name:
                variable = "Stock"
            elif "Vehicle registration (Bus)" in indicator_name:
                variable = "Stock"          
            elif "Stock" in indicator_name:
                variable = "Stock"
            elif "LDV Sales" in indicator_name:
                variable = "Sales (New Vehicles)"
            else:
                variable = "Not Available"
        else:
                variable = "Not Available"   

        return variable
    
    # Function that returns unit and unit_factor
    def get_unit_and_unit_factor(self, item_value: dict, unit_name: str):
        """Determine 'expected unit' and 'unit factor' from 'Unit'.

        The rules implemented are:

        ============================================= ===== ============
        Unit                                    
        ============================================= ===== ============
        The unit is changed from Number to 10^6 vehicle / yr.
        # Unit: "Number to 10^6 vehicle / y"
        ============================================= ===== ============
        """
        unit = "NA"
        unit_factor = 1     
        unit_found = False    
            
        for new_key, new_val in item_value.items():            
            if new_key == "Unit":
                for key1, value1 in new_val.items():
                    if unit_name in value1:
                        unit = "10^6 vehicle / y"
                        unit_factor = 1000000                       
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
                # Ensure you are working with the original DataFrame and to avoid SettingWithCopyWarning
                df = df.copy()
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
                        # Ensure you are working with the original DataFrame and to avoid SettingWithCopyWarning
                        df = df.copy()
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
        #[vehicle_type, variable_type, unit, unit_factor, rule_id]
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
        
        return df_out_put
        
    # Function that extract and process the input files and save the final data  
    def process_input_data(self):
        # Steps followed for extracting and cleaning the dataset
        #Step 1) Load both ATO workbook excel sheet and master dataset csv files into Dataframes
        df = pd.read_excel(open(self.workbook_file, 'rb'), self.sheet_name)
        
        # Load the master data CSV file
        master_df = pd.read_csv(self.master_file)
        master_column_names= list(master_df.columns.values)

        #Step 2) Create a new dataframe using master dataset column names
        df_out_put = pd.DataFrame(columns=master_column_names)

        #Step 3) Separate the ATO workbook dataframe into two parts
        #a) Upper part of the data frame containg 8 rows 
        df_upper = df.head(8)

        #The function returns a list of 
        #[mode_value, source_value, service_value, unit_value, indicator_value, sheet_name]
        upper_part_attributes = self.extract_upper_part_one(df_upper)

        regions = self.populate_regions()

        rule_book = self.load_rule_book()

        remaining_part_attributes = self.extract_upper_part_two(upper_part_attributes, rule_book)

        # b) Lower part of the dataframe containing the remaining rows 
        # extract lower part of the dataframe
        df_lower = df.iloc[13:65]

        df_lower_new, updated_column_names = self.process_lower_part(df_lower)

        master_df_output = self.update_master_data(df_out_put, df_lower_new, updated_column_names,
                                        upper_part_attributes, remaining_part_attributes, regions)

        # Specify the saving path for the CSV file
        out_put_name = "T016_output.csv"
        saving_path = os.path.abspath(os.path.join(self.submodule_path, 'data', 'historical', 'output', out_put_name))   

        master_df_output.to_csv(saving_path, index=False)

           
def get_input_files():
    # Get the current script's path
    script_path = Path(__file__).resolve()
    # Assuming the submodule is one level up from the script
    submodule_path = script_path.parent.parent
    # Add the submodule path to the system path           
    sys.path.append(str(submodule_path))
    submodule_path = script_path.parent.parent

    input_files = []

    # Specify the path to the input files
    excel_file_path = os.path.abspath(os.path.join(submodule_path, 'data', 'historical', 'input', 'T016_input.xlsx'))
    input_files.append(excel_file_path)

    master_file_path = os.path.abspath(os.path.join(submodule_path, 'data', 'historical', 'input', 'master dataset.csv'))
    input_files.append(master_file_path)    

    regions_file_path = os.path.abspath(os.path.join(submodule_path, 'data', 'historical', 'regions.yaml'))
    input_files.append(regions_file_path)

    source_file_path = os.path.abspath(os.path.join(submodule_path, 'data', 'historical', 'sources_for_T015_T016_T017.yaml'))
    input_files.append(source_file_path)

    sheet_name = r"TAS-VEP-005(1)"
    input_files.append(sheet_name)

    input_files.append(submodule_path)

    return input_files

input_files = get_input_files()

# Check if the file exists
if os.path.isfile(input_files[0]):
    
    # Process the input files and save output as csv file
    atoWorkBook = AtoWorkbook(input_files[0], input_files[1], input_files[2], input_files[3], input_files[4], input_files[5])
    atoWorkBook.process_input_data()
    print("File is found.")
else:
    print("File is not found on the specified path:", input_files[0])

##<<<<<<<<<<<<<<<<<<<<< //////////////////////// >>>>>>>>>>>>>>>>>>>>>>>>##
##<<<<<<<<<<<<<<<<<<<<< Programe ends here >>>>>>>>>>>>>>>>>>>>>>>>##
##<<<<<<<<<<<<<<<<<<<<< //////////////////////// >>>>>>>>>>>>>>>>>>>>>>>>##        
