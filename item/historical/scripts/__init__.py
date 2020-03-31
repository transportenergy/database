import pandas as pd

from item.common import paths
from item.historical import source_str
from . import T001
from .util.managers.dataframe import DataframeManager


SCRIPTS = {
    1: T001.process
}


def process(id):
    """Process a data set given its *id*."""
    # Creating the dataframe and viewing the data

    # Creating a dataframe from the csv data
    id_str = source_str(id)
    path = paths['data'] / 'historical' / 'input' / f'{id_str}_input.csv'
    df = pd.read_csv(path)

    # Call the dataset-specific processing
    script = SCRIPTS[1]
    df = script(df)

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
