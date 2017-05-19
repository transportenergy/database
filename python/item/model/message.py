import os

import pandas as pd


def import_data(path):
    input_fn = os.path.join(path, 'iTEM2_reporting_MESSAGE_2016-08-26.xlsx')

    data = pd.read_excel(input_fn, sheetname=['data_Base', 'data_2C'])

    # Read comments sheet
    notes = pd.read_excel(input_fn, 'comments').dropna(subset=['comments']) \
              .drop(['Scenario', 'Region'], axis='columns')
    notes['Model'] = 'MESSAGE'

    return pd.concat(data.values()), None
