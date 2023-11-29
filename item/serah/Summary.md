Steps to load and transform iTEM data.

These instructions are for TAS-FRA-004(2),T019_TAS-FRA-007(3) and T020_TAS-VEP-018

1. Load data using Pandas
2. Read metadata (Upper part in excel) and Actual data (down part in excel)
3. Apply rule book to transform metadata based on sheets 
4. Apply transformation on data
   1. Divide the kms driven from millions to billions
   2. Use the ISO Code to find the Region and add a new column
   3. Fetch necessary data from the rule book applicable to rule id
5. Merge the transformed data into single master csv





