import pandas as pd

from item.common import paths
from item.historical import source_str
from . import T001
from .util.managers.dataframe import DataframeManager


MODULES = {
    1: T001
}


def process(id):
    """Process a data set given its *id*."""
    # Creating the dataframe and viewing the data

    # Creating a dataframe from the csv data
    id_str = source_str(id)
    path = paths['data'] / 'historical' / 'input' / f'{id_str}_input.csv'
    df = pd.read_csv(path)

    # Get the module for this data set
    dataset_module = MODULES[1]

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
    # TODO Assign ISO-3166 codes
    # TODO Assign iTEM regions based on ISO codes

    # Reordering the columns
    #
    # Rule: The columns should follow the order established in the latest
    # template
    dfm = DataframeManager(source_str(id))
    df = dfm.reorder_columns(df)

    # Exporting results

    # Programming Friendly View
    dfm.create_programming_friendly_file(df)

    # User Friendly View
    dfm.create_user_friendly_file(df)

    # Return the data for use by other code
    return df
