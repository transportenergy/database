"""Tools to retrieve and push data."""
import pandasdmx as sdmx


def get_sdmx(source=None, **args):
    """Retrieve data from *source* using pandaSDMX.

    Arguments
    ---------
    source : str
        Name of a data source recognized by pandaSDMX, e.g. 'OECD'.
    args
        Other arguments to :meth:`sdmx.Request.get`.

    Returns
    -------
    pandas.DataFrame
    """
    # SDMX client for the data source
    req = sdmx.Request(source=source)

    # Retrieve the data
    msg = req.get(resource_type='data', tofile='debug.json', **args)

    # Convert to pd.DataFrame, preserving attributes
    df = sdmx.to_pandas(msg, attributes='dgso').dropna()
    index_cols = df.index.names

    # Reset index, use categoricals
    return df.reset_index().astype({c: 'category' for c in index_cols})
