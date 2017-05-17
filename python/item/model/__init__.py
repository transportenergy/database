"""Update item2-data

The sub-modules in this directory read from the Excel reporting templates
(BP, ExxonMobil, IEA, ITF, and MESSAGE) or GAMS GDX file (EPPA5). This script
is run from the top item-scripts directory with:

    $ python3 -m model COMMAND

The actions depend on COMMAND:

- 'import': the item2-data/model directory and subdirectories are populated
   with CSV and other files containing the input data.
- 'check':
- 'variables':

"""
import errno
from importlib import import_module
import os
from os import makedirs
from os.path import join
import pickle

import pandas as pd
import xarray as xr
import yaml

from item.common import paths, log
from item.model.common import as_xarray, data_columns, INDEX, tidy
from item.model.dimensions import load_template


__all__ = ['load_model_data']


def order_columns(df):
    """Return a copy of *df* with columns in a canonical order."""
    df = df.reindex_axis(INDEX + data_columns(df), axis=1)
    df.columns = map(str, df.columns)
    return df


def coverage(models):
    """Display some basic data coverage information."""

    log('Checking data coverage.\n')

    # Accumulate a list of xr.DataArrays to later concatenate@
    result = []

    # Load the list of requested quantities
    qty = load_template(paths['model data'])

    # Find True/not-null values and sum to get the number of requested
    # quantities for each variable
    req = qty.notnull().sum(['Mode', 'Technology', 'Fuel']) \
             .to_array(name='Requested')
    log('Quantities requested in reporting template: %d\n', req.sum())
    result.append((req, 'Requested'))

    # Iterate through models
    for name in sorted(models.keys()):
        if name == 'itf' or name == 'exxonmobil' or name == 'roadmap':
            # Skip due to a data issue
            continue
        log('Loading data for %s' % name)

        # Load model data
        df = pd.read_csv(os.path.join(paths['model data'], 'model', name,
                         'data.csv'))
        log(df.head())

        # Convert to an xr.Dataset, then count non-null values. We consider a
        # series populated if it has a data value for *any* scenario, region
        # and year.
        counts = as_xarray(df).notnull().any(['Scenario', 'Region', 'Year']) \
                              .sum(['Mode', 'Technology', 'Fuel']).to_array()
        result.append((counts, name))

    # Make two separate lists of the DataArrays and labels
    data, labels = zip(*result)

    # Combine to a single Dataset
    df = xr.concat(data, pd.Index(labels, name='model')).fillna(0) \
           .to_dataframe().unstack('model')

    # Compute some totals
    df.columns = df.columns.droplevel(0)
    df['# of models'] = (df.loc[:, 'bp':] > 0).sum(axis='columns')
    df.loc['Total', :] = df.sum(axis='rows')
    df = df.astype(int)
    log(df)
    df.to_csv(os.path.join(paths['model data'], 'output', 'coverage.csv'))


def process_raw(models):
    """Process raw data submissions.

    Data for MODELS are imported from the raw data directory.
    """
    log('Processing raw data for: {}'.format(' '.join(models)))
    with open(join(paths['data'], 'model', 'models.yaml')) as f:
        model_info = yaml.load(f)

    for name in models:
        try:
            info = model_info[name]
        except KeyError:
            log("  unknown model '%s', skipping" % name)
            continue

        if info['format'] in [None, 'csv']:
            log("  model '%s' data needs no import" % name)
            continue

        model = import_module('item.model.%s' % name)
        _process_raw(name, model, info)


def _process_raw(name, model, info):
    log('Processing raw data for {}'.format(name))
    # Path to raw data: this hold the contents of the Dropbox folder
    # 'ITEM2/Scenario_data_for_comparison/Data_submission_1/Raw_data'
    raw_data = join(paths['model raw'], '%s.%s' % (name, info['format']))
    metadata = join(paths['data'], 'model', name)

    log('  raw data: {}\n  metadata: {}'.format(raw_data, metadata))

    # Load the data
    data, notes = model.import_data(raw_data, metadata)

    # Put columns in a canonical order
    data = order_columns(data)

    # Log some diagnostic information
    iy = sorted(set(data.columns) - set(INDEX))[0]
    log('  %d non-zero values beginning %s' % (
        data.loc[:, iy:].notnull().sum().sum(), iy))

    # Create a subdirectory under item2-data/model, if it does not already
    # exist
    model_dir = join(paths['model processed'], name)
    makedirs(model_dir, exist_ok=True)

    # TODO log the last-changed date of the file used for import, or a
    # checksum

    # Write data
    data.to_csv(join(paths['model processed'], '%s.csv' % name), index=False)

    # Write the region list for this model
    pd.Series(data['region'].unique(), name='region') \
      .to_csv(join(model_dir, 'region.csv'), index=False)

    # Write the model comments
    try:
        notes.to_csv(join(model_dir, 'note.csv'), index=False)
    except AttributeError:
        # notes == None; no comments provided for this data set
        pass


def load_model_data(version, skip_cache=False, cache=True, fmt=pd.DataFrame):
    """Load model database"""
    # Check arguments
    version = int(version)

    try:
        path = paths['models-%d' % version]
    except KeyError:
        raise ValueError('invalid model database version: %s' % version)

    if fmt not in [pd.DataFrame, xr.DataArray, xr.Dataset]:
        raise ValueError('unknown return format: %s' % fmt)

    # Path for cached data
    cache_path = os.path.join(paths['cache'], 'model-%d.pkl' % version)

    data = None

    # Read data from cache
    if not skip_cache:
        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
        except OSError as e:
            if e.errno == errno.ENOENT:  # No such file or directory
                pass

    # Read data from file
    if data is None:
        data = tidy(pd.read_csv(path))

        # Convert to long format, drop empty rows
        data = pd.melt(data, id_vars=INDEX, var_name='year') \
                 .dropna(subset=['value'])

        # Cache the result
        if cache:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)

    if fmt in [xr.Dataset, xr.DataArray]:
        # Convert to an xarray format
        return as_xarray(data, version, fmt)
    else:
        # return as-is
        return data
