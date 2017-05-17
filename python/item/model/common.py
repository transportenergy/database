"""Common code for data input."""
from logging import DEBUG

import numpy as np
import xarray as xr

from item.common import log


# List of the index columns required to identify all data series
INDEX = [
    'model',
    'scenario',
    'region',
    'variable',
    'mode',
    'technology',
    'fuel',
    'unit',
    ]


def as_xarray(data, version, fmt):
    # Columns to preserve as a multi-index
    data.set_index(INDEX + ['year'], inplace=True)

    # variable name → xr.DataArray
    das = {}

    # Iterate over variables. Some variables (intensities) appear twice with
    # different units for freight, passenger
    for key, d in data.groupby(level=['variable', 'unit']):
        variable, unit = key

        log('Variable: {0[0]} [{0[1]}]\n  {1} values'.format(key, len(d)),
            level=DEBUG)

        # Version-specific fixes
        # TODO move
        if version == 1:
            if variable == 'intensity_new':
                log('  skipping', level=DEBUG)
                continue
            elif variable in ['ef_co2 (service)', 'intensity_service']:
                variable = variable.replace('service', unit[-3:])

        # *d* (the data for this variable) has all the MultiIndex levels of
        # *data*; drop the unused ones (requires pandas 0.20)
        d.index = d.index.remove_unused_levels()

        # Convert to xr.DataArray
        try:
            d = xr.DataArray.from_series(d['value'].astype(float))
        except Exception as e:
            if 'non-unique multi-index' in str(e):
                log(d.index[d.index.duplicated()].to_series(), level=DEBUG)
            raise

        # Convert unused dimensions for this variable to attributes
        squeeze_dims = []
        for c in d.coords:
            if d.sizes[c] == 1:
                # Dimension 'c' has only one value → convert
                d.attrs[c] = d[c].values[0]
                squeeze_dims.append(c)
        d = d.squeeze(squeeze_dims, drop=True)
        d.name = variable
        d.attrs['unit'] = unit

        fill = float(100 * d.notnull().sum() / np.prod(list(d.sizes.values())))
        log('  {:2.0f}% full\n  coords: {}\n  attrs: {}'
            .format(fill, ', '.join(d.coords.keys()), d.attrs),
            level=DEBUG)

        das[variable] = d

    result = das

    # The resulting dataset is very sparse
    if fmt == xr.Dataset:
        log('Merging\n  sparseness:', level=DEBUG)

        result = xr.merge(das.values())

        for v in result:
            fill = float(100 * result[v].notnull().sum() /
                         np.prod(list(result[v].sizes.values())))
            log('  {:3.0f}% full — {}'.format(fill, v), level=DEBUG)

    return result


def data_columns(df):
    """Return a sorted list of non-index columns in pandas.Dataframe *df*."""
    return sorted(set(df.columns) - set(INDEX))


def drop_empty(df, columns=None):
    """Drop rows in *df* where the data columns are all empty.

    The number of dropped rows is logged. If *columns*, an iterable of column
    names, is given, drop on these columns instead.
    """
    rows = df.shape[0]
    if columns is None:
        columns = data_columns(df)
    df = df.dropna(how='all', subset=columns)
    log('  dropped %d empty rows' % (rows - df.shape[0]))
    return df


def tidy(df):
    # Rename data columns:
    # - remove 'X' preceding years
    # - convert years to integers
    # - lowercase
    def _rename(colname):
        try:
            if isinstance(colname, str):
                colname = colname.lstrip('X')
            return int(colname)
        except ValueError:
            if colname == 'Tech':
                colname = 'Technology'
            return colname.lower()

    df.rename(columns=_rename, inplace=True)
    return drop_empty(df.reindex_axis(INDEX + data_columns(df), axis=1))
