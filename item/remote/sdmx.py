import pandasdmx as sdmx


def get_sdmx(source=None, **args):
    """Retrieve data from *source* using :mod:`pandasdxm`.

    Arguments
    ---------
    source : str
        Name of a data source recognized by pandaSDMX, e.g. 'OECD'.
    args
        Other arguments to :meth:`pandasdmx.Request.get`.

    Returns
    -------
    pandas.DataFrame
    """
    # SDMX client for the data source
    req = sdmx.Request(source=source)

    # commented: for debugging
    # args.setdefault('tofile', 'debug.json')

    # Retrieve the data
    msg = req.get(resource_type='data', **args)

    # Convert to pd.DataFrame, preserving attributes
    df = sdmx.to_pandas(msg, attributes='dgso')
    index_cols = df.index.names

    # Reset index, use categoricals
    return df.reset_index().astype({c: 'category' for c in index_cols})
