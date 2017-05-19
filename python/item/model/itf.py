import os

import pandas as pd

from .common import drop_empty, log


def import_data(path):
    input_fn = os.path.join(path,
                            'iTEM2_reporting_ITF_UrbanPassenger_Fuel.xlsx')

    # Giving 'None' causes all five sheets to be loaded
    data = pd.read_excel(input_fn, None)

    log(*['Sheet %s: %d rows' % (k, v.shape[0]) for k, v in data.items()])

    data = pd.concat(data.values())

    # Clobber the sub-model names
    data['Model'] = 'ITF'

    # Combine the sheets. No comments supplied
    return drop_empty(data), None
