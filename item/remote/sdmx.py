from typing import Optional

import pandas as pd
import sdmx


def get_sdmx(source: Optional[str] = None, **args) -> pd.DataFrame:
    """Retrieve data from *source* using :mod:`sdmx`.

    Arguments
    ---------
    source : str
        Name of a data source recognized by ``sdmx1``, e.g. 'OECD'.
    args
        Other arguments to :meth:`sdmx.Request.get`.

    Returns
    -------
    pandas.DataFrame
    """
    # SDMX client for the data source
    req = sdmx.Client(source=source)

    # commented: for debugging
    # args.setdefault('tofile', 'debug.json')

    # Retrieve the data
    msg = req.get(resource_type="data", **args)

    # Convert to pd.DataFrame, preserving attributes
    df = sdmx.to_pandas(msg, attributes="dgso")
    index_cols = df.index.names

    # Reset index, use categoricals
    return df.reset_index().astype({c: "category" for c in index_cols})
