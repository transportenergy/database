# Instructions that was followed during cleaning of the dataset.

## The following steps has been followed during importing and cleaning of the input dataset.

```
> Step 1) Load "ATO Workbook (TRANSPORT ACTIVITY & SERVICES (TAS))2023.xlsx" file and transform into DataFrame using Panda.

>> Step 2) Load "master dataset.csv" file and transform into DataFrame using Panda, and create a new output DataFrame using
        columuns extracted from the "master dataset.csv" file.

> Step 3) Extract the following attributes such as: Vehicle Type, Variable, Unit, Unit_factor, Rule_id, Mode, Source,     
        Service, Indicator and Sheet_name from the upper part of the DataFrame.

>> Step 4) Extract the Economy Code and the value under each years within the series from the lower part of the DataFrame, as  
        well as cleaning of unwanted columuns was done.

Step 5) The country_region_mapping() function is used to generate Country and Region of each Economy Codes.

Step 6) The values for each years has been transformed using a unit_factor that is obtained from the upper part of the 
        DataFrame.

Step 7) Finally, the above extracted datas from both upper and lower part of the DataFrame are updated into the output 
        DataFrame and save the output as csv file.
```
 