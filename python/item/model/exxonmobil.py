import os

import pandas as pd

from .common import drop_empty


def import_data(path):
    input_fn = os.path.join(path, 'iTEM2_reporting_ExxonMobil.xlsx')

    data = pd.read_excel(input_fn, sheetname='data')
    data = drop_empty(data)

    # Some of the cells in the 'Region' column contain excess white space;
    # remove it
    data['Region'] = data['Region'].apply(lambda s: s.strip())

    data['Model'] = 'ExxonMobil'
    data['Scenario'] = 'Base'

    # Read comments sheet
    notes = pd.read_excel(input_fn, 'comments').dropna(subset=['comments']) \
              .drop(['Scenario', 'Region'], axis='columns')
    notes['Model'] = 'ExxonMobil'

    return data, notes
