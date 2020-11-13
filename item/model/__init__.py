import errno
import os
import pickle
from importlib import import_module
from os import makedirs
from os.path import join
from typing import Dict

import pandas as pd
import pycountry
import xarray as xr
import yaml

from item.common import log, paths
from item.model.common import as_xarray, concat_versions, select, tidy, to_wide
from item.model.dimensions import INDEX, load_template

__all__ = [
    "concat_versions",
    "coverage",
    "get_model_info",
    "load_model_data",
    "load_model_scenarios",
    "make_regions_csv",
    "make_regions_yaml",
    "select",
    "squash_scenarios",
    "to_wide",
]


# Versions of the database
VERSIONS = [1, 2]

# Information about the models
MODELS: Dict[str, dict] = {}


def coverage(models):
    """Display some basic data coverage information."""

    log("Checking data coverage.\n")

    # Accumulate a list of xr.DataArrays to later concatenate@
    result = []

    # Load the list of requested quantities
    qty = load_template(paths["model data"])

    # Find True/not-null values and sum to get the number of requested
    # quantities for each variable
    req = qty.notnull().sum(["Mode", "Technology", "Fuel"]).to_array(name="Requested")
    log("Quantities requested in reporting template: %d\n", req.sum())
    result.append((req, "Requested"))

    # Iterate through models
    for name in sorted(models.keys()):
        if name == "itf" or name == "exxonmobil" or name == "roadmap":
            # Skip due to a data issue
            continue
        log("Loading data for %s" % name)

        # Load model data
        df = pd.read_csv(os.path.join(paths["model data"], "model", name, "data.csv"))
        log(df.head())

        # Convert to an xr.Dataset, then count non-null values. We consider a
        # series populated if it has a data value for *any* scenario, region
        # and year.
        counts = (
            as_xarray(df)
            .notnull()
            .any(["Scenario", "Region", "Year"])
            .sum(["Mode", "Technology", "Fuel"])
            .to_array()
        )
        result.append((counts, name))

    # Make two separate lists of the DataArrays and labels
    data, labels = zip(*result)

    # Combine to a single Dataset
    df = (
        xr.concat(data, pd.Index(labels, name="model"))
        .fillna(0)
        .to_dataframe()
        .unstack("model")
    )

    # Compute some totals
    df.columns = df.columns.droplevel(0)
    df["# of models"] = (df.loc[:, "bp":] > 0).sum(axis="columns")
    df.loc["Total", :] = df.sum(axis="rows")
    df = df.astype(int)
    log(df)
    df.to_csv(os.path.join(paths["model data"], "output", "coverage.csv"))


def get_model_info(name, version):
    load_models_info()

    try:
        model_info = MODELS[name]
        if version in model_info["versions"]:
            return model_info
        else:
            raise ValueError(
                "model '{}' not present in database version {}".format(name, version)
            )
    except KeyError:
        raise ValueError(f"Model {repr(name)} not among {MODELS.keys()}")


def get_model_names(version=VERSIONS[-1]):
    """Return the names of all models in *version*."""
    load_models_info()

    result = []
    for name, info in MODELS.items():
        if version in info["versions"]:
            result.append(name)
    return result


def process_raw(version, models):
    """Process raw data submissions.

    Data for MODELS are imported from the raw data directory.
    """
    # Process arguments
    models = models if len(models) else get_model_names(version)

    log("Processing raw data for: {}".format(" ".join(models)))

    class _csv_model:
        def import_data(self, data_path, metadata_path):
            return pd.read_csv(data_path), None

    for name in models:
        try:
            info = get_model_info(name, version)
        except KeyError:
            log("  unknown model '%s', skipping" % name)
            continue

        if info["format"] == "csv":
            model = _csv_model()
        elif info["format"] is None:
            log("  model '{}' needs no import".format(name))
            continue
        else:
            model = import_module("item.model.%s" % name)

        _process_raw(name, model, version, info)


def _process_raw(name, model, version, info):
    log("Processing raw data for {}".format(name))
    # Path to raw data: this hold the contents of the Dropbox folder
    # 'ITEM2/Scenario_data_for_comparison/Data_submission_1/Raw_data'
    raw_data = join(
        paths["model raw"], str(version), "{}.{}".format(name, info["format"])
    )
    metadata = join(paths["data"], "model", name)

    log("  raw data: {}\n  metadata: {}".format(raw_data, metadata))

    # Load the data
    data, notes = model.import_data(raw_data, metadata)

    # Put columns in a canonical order
    data = tidy(data)

    # Log some diagnostic information
    iy = list(set(data.columns) - set(INDEX))
    log("  %d non-zero values beginning %s", data.loc[:, iy].notnull().sum().sum(), iy)

    # Create a subdirectory under item2-data/model, if it does not already
    # exist
    model_dir = join(paths["model processed"], str(version), name)
    makedirs(model_dir, exist_ok=True)

    # TODO log the last-changed date of the file used for import, or a
    # checksum

    # Write data
    data.to_csv(
        join(paths["model processed"], str(version), "%s.csv" % name), index=False
    )

    # Write the region list for this model
    pd.Series(data["region"].unique(), name="region").to_csv(
        join(model_dir, "region.csv"), index=False
    )

    # Write the model comments
    try:
        notes.to_csv(join(model_dir, "note.csv"), index=False)
    except AttributeError:
        # notes == None; no comments provided for this data set
        pass


def load_model_data(
    version, skip_cache=False, cache=True, fmt=pd.DataFrame, options=[]
):
    """Load model database"""
    # Check arguments
    version = int(version)

    try:
        path = paths["models-%d" % version]
    except KeyError:
        raise ValueError("invalid model database version: %s" % version)

    if fmt not in [pd.DataFrame, xr.DataArray, xr.Dataset]:
        raise ValueError("unknown return format: %s" % fmt)

    # Path for cached data
    cache_path = os.path.join(paths["cache"], "model-%d.pkl" % version)

    data = None

    # Read data from cache
    if not skip_cache:
        try:
            with open(cache_path, "rb") as f:
                data = pickle.load(f)
        except OSError as e:
            if e.errno == errno.ENOENT:  # No such file or directory
                pass

    # Read data from file
    if data is None:
        data = tidy(pd.read_csv(path))

        # Convert to long format, drop empty rows
        data = pd.melt(data, id_vars=INDEX, var_name="year").dropna(subset=["value"])

        # Cache the result
        if cache:
            with open(cache_path, "wb") as f:
                pickle.dump(data, f)

    # Optional additional processing
    if "squash scenarios" in options:
        data = squash_scenarios(data, version)
        options.remove("squash scenarios")

    if len(options):
        raise ValueError

    if fmt in [xr.Dataset, xr.DataArray]:
        # Convert to an xarray format
        return as_xarray(data, version, fmt)
    else:
        # return as-is
        return data


def load_models_info():
    """Load the models metadata into the MODELS global."""
    global MODELS

    if len(MODELS) > 0:
        # Already loaded
        return

    with open(join(paths["data"], "model", "models.yaml")) as f:
        MODELS = yaml.safe_load(f)


def load_model_regions(name, version):
    """Load regions.yaml for model *name* in database *version*.

    Returns a dictionary where:
    - Keys are codes or names of model regions.
    - Values are dictionaries with the keys:
      - description (optional): a longer name or description of the region
      - countries: a list of ISO 3166 alpha-3 codes for countries in the
        region.
    """
    # IDEA load from either regions-1.yaml or regions-2.yaml
    try:
        get_model_info(name, version)
    except Exception:
        if name.lower() == "item":
            # Use an empty path in the join() call below; this causes the
            # overall regions.yaml to be loaded
            name = ""
        else:
            raise

    with open(join(paths["data"], "model", name, "regions.yaml")) as f:
        return yaml.safe_load(f)


def load_model_scenarios(name, version):
    """Load scenarios.yaml for model *name* in database *version*.

    Returns a dictionay where:

    - Keys are codes or names of scenarios.
    - Values are dictionaries with the key:

      - ``category``: either 'reference' or 'policy'.
    """
    # Don't do anything with the return value; just check arguments
    get_model_info(name, version)

    with open(join(paths["data"], "model", name, "scenarios.yaml")) as f:
        return yaml.safe_load(f)[version]


def make_regions_csv(out_file, models=None, compare=None):
    """Produce a CSV *out_file* with a country→region map for *models*.

    The table is created by parsing the regions.yaml files in the iTEM model
    database metadata. It is indexed by ISO 3166 (alpha-3) codes, and has one
    column for each model in *models* (if no models are specified, all models
    are included).

    If *compare* is given, the table has entries only where the generated
    value and
    """
    version = VERSIONS[-1]  # Version 2 only

    models = models or get_model_names(version)

    def _load(name):
        def _invert(data):
            result = {}
            for k, v in data.items():
                result.update({c: k for c in v["countries"]})
            return result

        return pd.Series(
            _invert(load_model_regions(name, version)),
            name=name if len(name) else "item",
        )

    result = pd.concat([_load(model) for model in ["item"] + models], axis=1)

    def _get_name(row):
        error = None
        try:
            name = pycountry.countries.get(alpha_3=row.name).name
        except AttributeError:
            try:
                name = pycountry.historic_countries.get(alpha_3=row.name).name
                error = "historical"
            except AttributeError:
                name = ""
                error = "nonexistent"
            finally:
                print(
                    "{} ISO 3166 code '{}' in models: {}".format(
                        error, row.name, ", ".join(row.dropna().index)
                    )
                )
        return name

    result["name"] = result.apply(_get_name, axis=1)

    if compare is not None:
        other = pd.read_csv(compare)
        other.columns = map(str.lower, other.columns)
        other.set_index("iso", inplace=True)
        other.index = map(str.upper, other.index)

        result = result.where(result.ne(other))

    with open(out_file, "w") as f:
        result.to_csv(f)


def make_regions_yaml(in_file, country, region, out_file):
    """Convert a country→region map from CSV *in_file* to YAML *out_file*.

    *country* and *region* are columns in *in_file* with country codes and
    region names, respectively.
    """
    data = pd.read_csv(in_file)[[region, country]].sort_values([region, country])
    data[country] = data[country].apply(str.upper)

    result = {}

    for region, group in data.groupby(region):
        result[region] = dict(description="", countries=list(group[country]))

    with open(out_file, "w") as f:
        yaml.dump(result, f, default_flow_style=False)


def squash_scenarios(data, version):
    """Replace the per-model scenario names with scenario categories.

    *data* is a pd.DataFrame. *version* is the version of the iTEM model
    database.
    """
    # Construct the map from model metadata
    scenarios_map = {}
    for model in get_model_names(version):
        for s, info in load_model_scenarios(model, version).items():
            scenarios_map[s] = info["category"]

    return data.replace({"scenario": scenarios_map})
