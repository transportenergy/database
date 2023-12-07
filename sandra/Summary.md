After finishing each data set cleaning, you need to write instructions on the steps you took to clean the dataset
Coding:
1.	Initialization:
•	Import necessary libraries: Pandas, os, yaml, pycountry, and math.
•	Define the class AtoWorkbook.
2.	Loading Rule Book and Region Information:
loading a rule book from a YAML file using the load_rule_book function.
Another YAML file containing the mapping of ISO codes with regions is loaded using the populate_regions function.
3.	Country and Region Mapping:
(extract_country_region and country_region_mapping) to map ISO codes to country and region names. These mappings are extracted from the loaded region information.
4.	Rule Identification:
The get_rule_id function is used to identify a rule based on specific criteria within the rule book. The identified rule ID, indicator name, and associated dictionary are returned.
5.	Vehicle Type,Variable Type, Unit and Unit Factor :
 determination based according to specified rule.
6.	Extraction of Upper Part of the DataFrame:
The extract_upper_part_one function extracts the upper part of the dataframe, including mode, source, service, unit, indicator, and sheet name.
7.	Extraction of Remaining Upper Part Attributes:
The extract_upper_part_two function further processes the upper part attributes, including vehicle type, variable type, unit, unit factor, and rule ID.
8.	Processing Lower Part of the DataFrame:
The process_lower_part function updates the columns in the lower part of the dataframe by renaming them based on expected values from row 13.
9.	Updating Master Data:
The update_master_data function updates the master data dataframe with information from the upper and lower parts of the ATO workbook, including mode, source, service, country, region, variable type, unit, vehicle type, technology, fuel, and ID.
10.	Processing Input Data:
The process_input_data function orchestrates the entire process, including loading the ATO workbook and master dataset, extracting upper and lower parts, updating master data, and saving the final data as a CSV file.
11.	File Path Check:
To check whether the specified Excel file exists before processing:
12.	Output File:
The final processed data is saved as a CSV.

Rules:
Created specific rules in PDF file for each data file.

Other files:
Download some Yaml files to benefit from them in the code(regions.yaml and sources.yamel)