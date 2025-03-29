"""Common code for data input."""

from logging import DEBUG
from os.path import join
from typing import Dict

import numpy as np
import pandas as pd
import xarray as xr
import yaml

from item.common import log, paths
from item.model.dimensions import INDEX

# Information about the models
MODELS: Dict[str, dict] = {}
SCENARIOS = None


def as_xarray(data, version, fmt):
    # Columns to preserve as a multi-index
    data.set_index(INDEX + ["year"], inplace=True)

    # variable name → xr.DataArray
    das = {}

    # Iterate over variables. Some variables (intensities) appear twice with
    # different units for freight, passenger
    for key, d in data.groupby(level=["variable", "unit"]):
        variable, unit = key

        log("Variable: {0[0]} [{0[1]}]\n  {1} values".format(key, len(d)), level=DEBUG)

        # Version-specific fixes
        # TODO move
        if version == 1:
            if variable == "intensity_new":
                log("  skipping", level=DEBUG)
                continue
            elif variable in ["ef_co2 (service)", "intensity_service"]:
                variable = variable.replace("service", unit[-3:])

        # *d* (the data for this variable) has all the MultiIndex levels of
        # *data*; drop the unused ones (requires pandas 0.20)
        d.index = d.index.remove_unused_levels()

        # Convert to xr.DataArray
        try:
            d = xr.DataArray.from_series(d["value"].astype(float))
        except Exception as e:
            if "non-unique multi-index" in str(e):
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
        d.attrs["unit"] = unit

        fill = float(100 * d.notnull().sum() / np.prod(list(d.sizes.values())))
        log(
            "  {:2.0f}% full\n  coords: {}\n  attrs: {}".format(
                fill, ", ".join(d.coords.keys()), d.attrs
            ),
            level=DEBUG,
        )

        das[variable] = d

    result = das

    # The resulting dataset is very sparse
    if fmt == xr.Dataset:
        log("Merging\n  sparseness:", level=DEBUG)

        result = xr.merge(das.values())

        for v in result:
            fill = float(
                100
                * result[v].notnull().sum()
                / np.prod(list(result[v].sizes.values()))
            )
            log("  {:3.0f}% full — {}".format(fill, v), level=DEBUG)

    return result


def concat_versions(dataframes={}):
    """Convert a dict of *dataframes* to a single pd.DataFrame.

    The keys of *dataframes* are saved in a new column 'version'.
    """
    dfs = []
    for version, df in dataframes.items():
        df["version"] = version
        dfs.append(df)
    return pd.concat(dfs)


def data_columns(df):
    """Return a sorted list of non-index columns in pandas.Dataframe *df*."""
    try:
        return sorted(set(df.columns) - set(INDEX))
    except TypeError:
        print(set(df.columns), set(INDEX), set(df.columns) - set(INDEX))
        raise


def drop_empty(df, columns=None):
    """Drop rows in *df* where the data columns are all empty.

    The number of dropped rows is logged. If *columns*, an iterable of column
    names, is given, drop on these columns instead.
    """
    rows = df.shape[0]
    if columns is None:
        columns = data_columns(df)
    df = df.dropna(how="all", subset=columns)
    log("  dropped %d empty rows" % (rows - df.shape[0]))
    return df


def load():
    """Load model & scenario data."""
    global SCENARIOS

    with open(join(paths["data"], "model", "models.yaml")) as f:
        MODELS = yaml.load(f, Loader=yaml.SafeLoader)

    # Load scenario information
    scenarios = []
    for model in MODELS:
        fn = join(paths["data"], "model", model, "scenarios.yaml")
        try:
            with open(fn) as f:
                m_s = yaml.load(f, Loader=yaml.SafeLoader)
        except FileNotFoundError:
            continue

        for version, m_s_v in m_s.items():
            for name, m_s_v_n in m_s_v.items():
                scenarios.append(
                    {
                        "model": model,
                        "version": version,
                        "scenario": name,
                        "category": m_s_v_n.get("category"),
                    }
                )

    SCENARIOS = pd.DataFrame(scenarios)


def tidy(df):
    # Rename data columns:
    # - remove 'X' preceding years
    # - convert years to integers
    # - lowercase
    def _rename(colname):
        try:
            if isinstance(colname, str):
                colname = colname.lstrip("X")
            return int(colname)
        except ValueError:
            if colname == "Tech":
                colname = "Technology"
            return colname.lower()

    df.rename(columns=_rename, inplace=True)
    return drop_empty(df.reindex_axis(INDEX + data_columns(df), axis=1))


def select(data, *args, **kwargs):
    """Select from *data*."""
    # Process arguments
    if len(args) > 1:
        raise ValueError(
            ("can't determine dimensions for >1 positional arguments: {}").format(
                " ".join(args)
            )
        )

    dims = {k: None for k in INDEX}

    for d, v in kwargs.items():
        d = "technology" if d == "tech" else d
        if isinstance(v, (int, str)):
            dims[d] = set([v])
        elif v is None:
            dims[d] = v
        else:
            dims[d] = set(v)

    if len(args) and dims["variable"] is None:
        dims["variable"] = set(args)

    # Code to this point is generic (doesn't depend on the format of *data*)

    if isinstance(data, xr.Dataset) or isinstance(data, dict):
        # TODO write methods for these other data types
        raise NotImplementedError

    # pandas.DataFrame
    # Construct a boolean mask
    keep = None
    for d, v in dims.items():
        if v is None:
            continue
        elif keep is None:
            keep = data[d].isin(v)
        else:
            keep &= data[d].isin(v)

    # Subset the data and return
    return data[keep].copy()


def to_wide(data, dimension="year"):
    """Convert *data* to wide format, one column per year."""
    return data.set_index(INDEX + ["year"])["value"].unstack(dimension)


load()
