import pandas as pd

from item.common import log


def import_data(data_path, metadata_path):
    input_fn = data_path

    # Giving 'None' causes all five sheets to be loaded
    data = pd.read_excel(input_fn, None)

    for k, v in data.items():
        log("Sheet {}: {} rows".format(k, v.shape[0]))

    data = pd.concat(data.values())

    # Clobber the sub-model names
    data["Model"] = "ITF"

    # Combine the sheets. No comments supplied
    return data, None
