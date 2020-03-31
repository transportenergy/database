from functools import lru_cache

import pandas as pd
import pycountry
import yaml

from item.common import paths
from item.historical import source_str
from . import T001
from .util.managers.dataframe import ColumnName


MODULES = {
    1: T001
}

OUTPUT_PATH = paths['data'] / 'historical' / 'output'

#: Non-ISO names appearing in 1 or more data sets; see :meth:`iso_and_region`.
COUNTRY_NAME = {
    "Montenegro, Republic of": "Montenegro",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Korea": "Korea, Republic of",
    "Serbia, Republic of": "Serbia",
}


# Map from ISO 3166 alpha-3 code to region name
REGION = {}
# Populate the map from the regions.yaml file
with open(paths['data'] / 'model' / 'regions.yaml') as file:
    for region_name, info in yaml.safe_load(file).items():
        REGION.update({c: region_name for c in info['countries']})


def process(id):
    """Process a data set given its *id*.

    Performs the following steps:

    1. Load the data from cache.
    2. Load a module defining dataset-specific processing steps. This module
       is in a file named e.g. :file:`T001.py`.
    3. Call the dataset's (optional) :meth:`check` method. This method receives
       the input data frame as an argument, and can make one or more assertions
       to ensure the data is in the expected format.
    4. Drop columns in the dataset's (optional) :data:`DROP_COLUMNS`
       :class:`list`.
    5. Call the dataset's (required) :meth:`process` method. This method
       receives the data frame from step (4), and performs any necessary
       processing.
    6. Assigns ISO 3166 alpha-3 codes and the iTEM region based on a column
       containing country names.
    7. Orders columns.
    8. Outputs data to two files.

    """
    # Creating the dataframe and viewing the data

    # Creating a dataframe from the csv data
    id_str = source_str(id)
    path = paths['data'] / 'historical' / 'input' / f'{id_str}_input.csv'
    df = pd.read_csv(path)

    # Get the module for this data set
    dataset_module = MODULES[1]

    try:
        # Check that the input data is of the form required by the script
        dataset_module.check(df)
    except AttributeError:
        print('No pre-processing checks to perform')
    except AssertionError as e:
        print(f'Input data is invalid: {e}')

    try:
        # Remove unnecessary columns
        df.drop(columns=dataset_module.DROP_COLUMNS, inplace=True)
        print('Drop {len(dataset_module.DROP_COLUMNS)} extra column(s)')
    except AttributeError:
        # No variable DROP_COLUMNS in dataset_module
        print(f'No columns to drop for {id_str}')

    # Call the dataset-specific processing
    df = dataset_module.process(df)
    print(f'{len(df)} observations')

    # Perform common cleaning tasks

    # Assign ISO 3166 alpha-3 codes and iTEM regions from a country name column
    column = 'Country'  # TODO read this name from dataset_module

    # Use pandas.Series.apply() to apply the same function to each entry in
    # the given column
    df = pd.concat([df, df[column].apply(iso_and_region)], axis=1)

    # Reordering the columns
    #
    # Rule: The columns should follow the order established in the latest
    # template
    df = df.assign(**{ColumnName.ID.value: id_str}) \
           .reindex(columns=[ev.value for ev in ColumnName])

    cache_results(id_str, df)

    # Return the data for use by other code
    return df


@lru_cache()
def iso_and_region(name):
    """Return (ISO 3166 alpha-3 code, iTEM region) for a country *name*."""
    # lru_cache() ensures this function call is as fast as a dictionary lookup
    # after the first time each country name is seen

    # Maybe map a known, non-standard value to a standard value
    name = COUNTRY_NAME.get(name, name)

    # Use pycountry's built-in, case-insensitive lookup on all fields including
    # name, official_name, and common_name
    alpha_3 = pycountry.countries.lookup(name).alpha_3

    # Look up the region, construct a Series, and return
    return pd.Series(
        [alpha_3, REGION.get(alpha_3, 'N/A')],
        index=[ColumnName.ISO_CODE.value, ColumnName.ITEM_REGION.value])


def cache_results(id_str, df):
    """Write *df* to cache in two file formats.

    The files written are:

    - :file:`{id_str}_cleaned_PF.csv`, in long or 'programming-friendly'
      format.
    - :file:`{id_str}_cleaned_UF.csv`, in wide or 'user-friendly' format.
    """
    OUTPUT_PATH.mkdir(exist_ok=True)

    # Long format ('programming friendly view')
    path = OUTPUT_PATH / f'{id_str}_cleaned_PF.csv'
    df.to_csv(path, index=False)
    print(f'Write {path}')

    # Pivot to wide format ('user friendly view') and write to CSV
    columns = [ev.value for ev in ColumnName if ev != ColumnName.VALUE]
    path = OUTPUT_PATH / f'{id_str}_cleaned_UF.csv'
    df.set_index(columns) \
      .unstack(ColumnName.YEAR.value) \
      .reset_index()\
      .to_csv(path, index=False)

    print(f'Write {path}')
