After finishing each data set cleaning, you need to write instructions on the steps you took to clean the dataset
------------------------------------------------------------------------------------------------------------------
The pseudocode for the provided Python code:
------------------------------------------------------------------------------------------------------------------
class AtoWorkbook:

    function load_rule_book(file_name: str) -> dict:
        # Load and return the rule book from the specified YAML file
        open file_name
        parse YAML content using SafeLoader
        return YAML content as dictionary

    function populate_regions(file_name: str) -> dict:
        # Populate and return the map of ISO_Code with Regions from the specified YAML file
        open file_name
        parse YAML content using SafeLoader
        iterate over items in YAML content
            for each region_name, info in items
                update REGION with ISO_Code mapping
        return REGION

    function country_region_mapping(economy_code, regions) -> dict:
        # Map ISO_Code to Country and Region using the provided economy_code and regions
        get country using pycountry for given economy_code
        get country_name from country
        create region_country_list with country_name and region from regions
        create COUNTRY dictionary with economy_code as key and region_country_list as value
        return COUNTRY

    function get_rule_id(rule_book: dict) -> tuple:
        # Return ruleID, indicator_name, and dictionary from the rule book
        initialize rule_id as "Txxx"
        initialize valid_id_found as False
        iterate over key, value in rule_book
            iterate over new_key, new_val in value
                if new_key is "name"
                    set indicator_name as new_val
                    split dataset_name using '-'
                    iterate over index in range(length of dataset_name_split)
                        if "Railways" in dataset_name_split[index]
                            set valid_id_found as True
                            set rule_id as key
                            break
                        else
                            set valid_id_found as False
        return rule_id, value, indicator_name

    function get_vehicle_type(mode: str, item_value: dict, dataset_name: str) -> str:
        # Determine Vehicle type based on mode, item_value, and dataset_name
        split dataset_name
        get first_indicator_word from splited_indicator_name
        create mode_indicator by concatenating mode and first_indicator_word
        iterate over new_key, new_val in item_value
            if new_key is "VehicleType"
                iterate over key1, value1 in new_val
                    if mode_indicator in key1
                        set VehicleType as value1
                        break
        return VehicleType

    function get_variable_type(service_name: str, indicator_name: str) -> str:
        # Determine Variable type based on service_name and indicator_name
        if service_name is "Freight"
            if "Freight Transport" in indicator_name
                set variable as "Freight Activity"
            elif "Freight (TEU)" in indicator_name
                set variable as "Freight (TEU)"
            elif "Freight (Weight)" in indicator_name
                set variable as "Freight (Weight)"
            elif "Stock" in indicator_name
                set variable as "Stock"
            elif "Sales (New Vehicles)" in indicator_name
                set variable as "Sales (New Vehicles)"
            else
                set variable as "Not Available"
        return variable

    function get_unit_and_unit_factor(item_value: dict, unit_name: str) -> tuple:
        # Determine expected unit and unit_factor based on item_value and unit_name
        initialize unit as "NA"
        initialize unit_factor as 1
        initialize unit_found as False
        iterate over new_key, new_val in item_value
            if new_key is "Unit"
                iterate over key1, value1 in new_val
                    if unit_name in value1
                        set unit as "10^9 tonne-km / yr"
                        set unit_factor as 1000
                        set unit_found as True
                        break
            if unit_found
                break
        return unit, unit_factor

    function extract_upper_part_one(df_upper: DataFrame) -> list:
        # Extract and return upper part attributes from the DataFrame
        get column_names as list of column names of df_upper
        initialize upper_part_attributes as empty list
        set mode_value as df_upper[4, column_names[1]]
        append mode_value to upper_part_attributes
        set source_long_name as "Asian Transport Outlook National Database"
        if column_names[1] is source_long_name
            set source_short_name as "ATO"
        set source_value as source_short_name + "2023 " + df_upper[1, column_names[1]]
        append source_value to upper_part_attributes
        set service_value as df_upper[5, column_names[1]]
        append service_value to upper_part_attributes
        set unit_value as df_upper[6, column_names[1]]
        append unit_value to upper_part_attributes
        set indicator_value as df_upper[0, column_names[1]]
        append indicator_value to upper_part_attributes
        set sheet_name as df_upper[1, column_names[1]]
        append sheet_name to upper_part_attributes
        return upper_part_attributes

    function extract_upper_part_two(upper_part_attributes: list, rule_book: dict) -> list:
        # Extract and return remaining upper part attributes using upper_part_attributes and rule_book
        initialize remaining_part_attributes as empty list
        call get_rule_id with rule_book and assign result to rule_id, item_value, indicator_name
        set vehicleType as get_vehicle_type using upper_part_attributes[0], item_value, indicator_name
        set unit, unit_factor as get_unit_and_unit_factor using item_value, upper_part_attributes[3]
        set variable_type as get_variable_type using upper_part_attributes[2], upper_part_attributes[4]
        append vehicleType, variable_type, unit, unit_factor, rule_id to remaining_part_attributes
        return remaining_part_attributes

    function process_lower_part(df: DataFrame) -> tuple:
        # Process lower part of the DataFrame and return updated DataFrame and column names
        get column_names_lower as list of column names of df
        set columun_length as length of column_names_lower
        initialize valid_column_length as 0
        initialize updated_column_names as empty list
        iterate over index in range(columun_length)
            remove extra white space from end of column_names_lower[index]
            if index < 2
                set expected_column as df[13, column_names_lower[index]]
                copy df to df (to avoid SettingWithCopyWarning)
                rename column_names_lower[index] to expected_column in df
                append expected_column to updated_column_names
            else
                set expected_column as df[13, column_names_lower[index]]
                set same_type as isinstance(expected_column, str)
                if not same_type
                    set expected_column as convert expected_column to int (truncate decimal)
                    set expected_column as convert expected_column to string
                try
                    set valid_columun as convert expected_column to int
                    set int_type as isinstance(valid_columun, int)
                    if int_type
                        copy df to df (to avoid SettingWithCopyWarning)
                        rename column_names_lower[index] to expected_column in df
                        append expected_column to updated_column_names
                except ValueError
                    print "Invalid columun name for : " + expected_column
        set df_lower_updated as copy of columns from df using updated_column_names
        set df_lower_new as df_lower_updated with row at index 13 dropped
        return df_lower_new, updated_column_names

    function update_master_data(df_out_put: DataFrame, df: DataFrame, column_list_names: list,
                                upper_attributes: list, remaining_attributes: list, regions: dict) -> DataFrame:
        # Update df_out_put DataFrame with values from df, upper_attributes, and remaining_attributes
        iterate over index, row in df
            set country_new as country_region_mapping using row['Economy Code'], regions
            set num_of_country as length of country_new[row['Economy Code']]
            if num_of_country is 1
                set single_name as country_new[row['Economy Code']]
                iterate over common_name in single_name
                    set region_name as common_name
                    set country_name as common_name
            else
                set country_name, region_name as country_new[row['Economy Code']]
            set df_out_put[index, ['Country']] as country_name
            set df_out_put[index, ['ISO Code']] as row['Economy Code']
            set df_out_put[index, ['Region']] as region_name
            set df_out_put[index, ['Variable']] as remaining_attributes[1]
            set df_out_put[index, ['Unit']] as remaining_attributes[2]
            set df_out_put[index, ['Vehicle Type']] as remaining_attributes[0]
            set df_out_put[index, ['Technology']] as "All"
            set df_out_put[index, ['Fuel']] as "All"
            set df_out_put[index, ['ID']] as remaining_attributes[4]
            set df_out_put[index, ['Mode']] as upper_attributes[0]
            set df_out_put[index, ['Source']] as upper_attributes[1]
            set df_out_put[index, ['Service']] as upper_attributes[2]
            set col_length as length of df.columns
            iterate over idx in range(col_length)
                if idx > 1
                    if not math.isnan(df[index, column_list_names[idx]])
                        set unit_value as df[index, column_list_names[idx]]
                        set final_unit as unit_value / remaining_attributes[3]
                        set df_out_put[index, column_list_names[idx]] as final_unit
        return df_out_put

    function process_input_data(workbook_file: str, master_file: str, regions_file: str, source_file: str):
        # Process input data files and save the final data
        set df as read_excel from workbook_file with sheet_name 'TAS-FRA-005(2)'
        set master_df as read_csv from master_file
        set master_column_names as list of column names of master_df
        set df_out_put as DataFrame with columns master_column_names
        set df_upper as first 8 rows of df
        set upper_part_attributes as extract_upper_part_one using df_upper
        set regions as populate_regions using regions_file
        set rule_book as load_rule_book using source_file
        set remaining_part_attributes as extract_upper_part_two using upper_part_attributes, rule_book
        set df_lower as rows 13 to 65 of df
        set df_lower_new, updated_column_names as process_lower_part using df_lower
        set master_df_output as update_master_data using df_out_put, df_lower_new, updated_column_names,
                                    upper_part_attributes, remaining_part_attributes, regions
        save master_df_output to CSV file with name "Output_data_" + upper_part_attributes[5] + ".csv"

# Name and path of input files
set workbook_excel_file as "ATO Workbook (TRANSPORT ACTIVITY & SERVICES (TAS))2023.xlsx"
set master_csv_file as "master dataset.csv"
set regions_file as "regions.yaml"
set source_file as "sources.yaml"

# Check if the Excel file exists
if workbook_excel_file exists
    # Process the input files and save output as csv file
    set atoWorkBook as new instance of AtoWorkbook
    call process_input_data using atoWorkBook, workbook_excel_file, master_csv_file, regions_file, source_file
    print "File is found."
else
    print "File is not found on the specified path!!"
