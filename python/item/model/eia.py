import os

import pandas as pd


def import_data(path):
    input_fn = os.path.join(path, 'iTEM2_reporting_ITEDD_20160920.xlsx')

    # Read data sheet
    data = pd.read_excel(input_fn, sheetname='data1')

    # Read comments sheet
    notes = pd.read_excel(input_fn, 'comments1').dropna(subset=['Comments']) \
              .drop(['Scenario', 'Region'], axis='columns')
    notes['Model'] = 'WEPS+'

    return data, notes
