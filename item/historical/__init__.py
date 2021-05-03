import logging
import os
from copy import deepcopy
from functools import lru_cache
from importlib import import_module
from typing import Dict, Optional

import pandas as pd
import pycountry
import yaml

from item.common import paths
from item.remote import OpenKAPSARC, get_sdmx
from item.structure import generate

log = logging.getLogger(__name__)


#: Path for output from :func:`process`.
OUTPUT_PATH = paths["data"] / "historical" / "output"

#: Non-ISO names appearing in 1 or more data sets. These are used in
#: :meth:`iso_and_region` to replace names before they are looked up using
#: :mod:`pycountry`.
COUNTRY_NAME = {
    "azerbaidjan": "AZE",
    "bolivia (plurinational state of)": "BOL",
    "bosnia-herzegovina": "BIH",
    "bosnia": "BIH",
    "brunei": "BRN",
    "cape verde": "CPV",
    "china, hong kong sar": "HKG",
    "china, macao sar": "MAC",
    "china, taiwan province of china": "TWN",
    "congo kinshasa ": "COD",
    "congo_the democratic republic of the": "COD",
    "cote d'ivoire": "CIV",
    "dem. people's republic of korea": "PRK",
    "democratic republic of the congo": "COD",
    "former yugoslav republic of macedonia, the": "MKD",
    "germany (until 1990 former territory of the frg)": "DEU",
    "holy see": "VAT",
    "hong-kong": "HKG",
    "iran (islamic republic of)": "IRN",
    "iran": "IRN",
    "ivory coast": "CIV",
    "korea": "KOR",
    "libyan arab jamahiriya": "LBY",
    "macedonia, the former yugoslav republic of": "MKD",
    "macedonia": "MKD",
    "micronesia (fed. states of)": "FSM",
    "moldavia": "MDA",
    "montenegro, republic of": "MNE",
    "palestine": "PSE",
    "republic of korea": "KOR",
    "reunion": "REU",
    "russia": "RUS",
    "saint helena": "SHN",
    "serbia and montenegro": "SCG",
    "serbia, republic of": "SRB",
    "south korea": "KOR",
    "state of palestine": "PSE",
    "swaziland": "SWZ",
    "syria": "SYR",
    "taiwan_province of china": "TWN",
    "tanzania_united republic of": "TZA",
    "the former yugoslav republic of macedonia": "MKD",
    "united states virgin islands": "VIR",
    "venezuela (bolivarian republic of)": "VEN",
    "virgin islands_british": "VGB",
    "wallis and futuna islands": "WLF",
}


# TODO don't do this every time this file is imported; add a utility function somewhere
# to generate it, like .structure.generate().
#: Map from ISO 3166 alpha-3 code to region name.
REGION = {}
# Populate the map from the regions.yaml file
with open(paths["data"] / "model" / "regions.yaml") as file:
    for region_name, info in yaml.safe_load(file).items():
        REGION.update({c: region_name for c in info["countries"]})


with open(paths["data"] / "historical" / "sources.yaml") as f:
    #: The current version of the file is always accessible at
    #: https://github.com/transportenergy/metadata/blob/master/historical/sources.yaml
    SOURCES = yaml.safe_load(f)


def cache_results(id_str, df):
    """Write *df* to :data:`.OUTPUT_PATH` in two file formats.

    The files written are:

    - :file:`{id_str}-clean.csv`, in long or 'programming-friendly' format, i.e. with a
      a 'Year' column.
    - :file:`{id_str}-clean-wide.csv`, in wide or 'user-friendly' format, with one
      column per year.
    """
    OUTPUT_PATH.mkdir(exist_ok=True)

    # Long format ('programming friendly view')
    path = OUTPUT_PATH / f"{id_str}-clean.csv"
    df.to_csv(path, index=False)
    log.info(f"Write {path}")

    # Pivot to wide format ('user friendly view')

    # Columns for wide format
    columns = list(c for c in df.columns if c != "VALUE")

    duplicates = df.duplicated(subset=columns, keep=False)
    if duplicates.any():
        log.warning("Processing produced non-unique keys; no -wide output")
        log.info("(Use log level DEBUG for details)")
        log.debug(df[duplicates])
        return

    # Write wide format
    path = OUTPUT_PATH / f"{id_str}-clean-wide.csv"

    # - Add the iTEM region and country name. NB this would be slightly faster after
    #   unstacking, but would require more complicated code to get the desired column
    #   order.
    # - Set all columns but 'Value' as the index → pd.Series with MultiIndex.
    # - Unstack the TIME_PERIOD dimension to columns, i.e. wide format.
    # - Return the index to columns in the dataframe.
    # - Write to file.
    columns.extend(["NAME", "ITEM_REGION"])
    df.assign(
        NAME=lambda df_: df_["REF_AREA"].apply(get_country_name),
        ITEM_REGION=lambda df_: df_["REF_AREA"].apply(get_item_region),
    ).set_index(columns)["VALUE"].unstack("TIME_PERIOD").reset_index().to_csv(
        path, index=False
    )
    log.info(f"Write {path}")


def fetch_source(id, use_cache=True):
    """Fetch data from source *id*.

    The remote data is fetched using the API for the particular source.
    A network connection is required.

    Parameters
    ----------
    use_cache : bool, optional
        If given, use a cached local file, if available. No check of cache
        validity is performed.
    """
    # Retrieve source information from sources.yaml
    id = source_str(id)
    source_info = deepcopy(SOURCES[id])

    # Path for cached data. NB OpenKAPSARC does its own caching
    cache_path = paths["historical input"] / f"{id}.csv"

    if use_cache and cache_path.exists():
        log.info(f"From cache at {cache_path}")
        return cache_path

    # Information for fetching the data
    fetch_info = source_info["fetch"]

    remote_type = fetch_info.pop("type")
    if remote_type.lower() == "sdmx":
        # Use SDMX to retrieve the data
        result = get_sdmx(**fetch_info)
    elif remote_type.lower() == "openkapsarc":
        # Retrieve data using the OpenKAPSARC API
        ok_api = OpenKAPSARC(api_key=os.environ.get("OK_API_KEY", None))
        result = ok_api.table(**fetch_info)
    else:
        raise ValueError(remote_type)

    # Cache the results
    result.to_csv(cache_path, index=False)

    return cache_path


def input_file(id: int):
    """Return the path to a cached, raw input data file for data source *id*.

    CSV files are located in the 'historical input' data path. If more than
    one file has a name beginning with “T{id}”, the last sorted file is
    returned.
    """
    # List of all matching files
    all_files = sorted(paths["historical input"].glob(f"{source_str(id)}*.csv"))

    # The last file has the most recent timestamp
    return all_files[-1]


def process(id):
    """Process a data set given its *id*.

    Performs the following common processing steps:

    1. Load the data from cache.
    2. Load a module defining dataset-specific processing steps. This module is in a
       file named e.g. :file:`T001.py`.
    3. Call the dataset's (optional) :meth:`check` method. This method receives the
       input data frame as an argument, and can make one or more assertions to ensure
       the data is in the expected format.
    4. Drop columns in the dataset's (optional) :data:`COLUMNS['drop']` :class:`list`.
    5. Call the dataset-specific (required) :meth:`process` method. This method receives
       the data frame from step (4), and performs any additional processing.
    6. Assign ISO 3166 alpha-3 codes and the iTEM region based on a column containing
       country names; either :data:`COLUMNS['country_name']` or the default, 'Country'.
       See :meth:`iso_and_region`.
    7. Assign common dimensions from the dataset's (optional) :data:`COMMON_DIMS`
       :class:`dict`.
    8. Order columns according to :class:`.ColumnName`.
    9. Output data to two files. See :meth:`cache_results`.

    Parameters
    ----------
    id : int
        Data source id, as listed in :data:`.MODULES`. E.g. ``0`` imports data from
        from file :file:`T000.csv`.

    Returns
    -------
    DataFrame : :class:`pandas.DataFrame`
        Apart from generating :meth:`cache_results`, returns dataset as a DataFrame.

    """
    id_str = source_str(id)

    # Get the module for this data set
    dataset_module = import_module(f"item.historical.{id_str}")

    if getattr(dataset_module, "FETCH", False):
        # Fetch directly from source
        path = fetch_source(id)
    else:
        # Load the data from version stored in the transportenergy/metadata repo
        # TODO remove this option; always fetch from source or cache
        path = paths["historical input"] / f"{id_str}_input.csv"

    # Read the data
    df = pd.read_csv(path, sep=getattr(dataset_module, "CSV_SEP", ","))

    try:
        # Check that the input data is of the form expected by process()
        dataset_module.check(df)
    except AttributeError:
        # Optional check() function does not exist
        log.info("No pre-processing checks to perform")
    except AssertionError as e:
        # An 'assert' statement in check() failed
        msg = "Input data is invalid"
        log.error(f"{msg}: {e}")
        raise RuntimeError(msg)

    # Information about columns. If not defined, use defaults.
    columns = dict(country_name="Country")
    columns.update(getattr(dataset_module, "COLUMNS", {}))

    try:
        # List of column names to drop
        drop_cols = columns["drop"]
    except KeyError:
        # No variable COLUMNS in dataset_module, or no key 'drop'
        log.info(f"No columns to drop for {id_str}")
    else:
        df.drop(columns=drop_cols, inplace=True)
        log.info(f"Drop {len(drop_cols)} extra column(s)")

    # Call the dataset-specific process() function; returns a modified df
    df = dataset_module.process(df)
    log.info(f"{len(df)} observations")

    # Assign ISO 3166 alpha-3 codes and iTEM regions from a country name column
    country_col = columns["country_name"]
    # Use pandas.Series.apply() to apply the same function to each entry in
    # the column. Join these to the existing data frame as additional columns.
    df = df.combine_first(df[country_col].apply(iso_and_region))

    # Values to assign across all observations: the dataset ID
    assign_values = {column_name("ID"): id_str}

    # Handle any COMMON_DIMS, if defined
    for dim, value in getattr(dataset_module, "COMMON_DIMS", {}).items():
        # Retrieve a dimension ID; copy the value to be assigned
        assign_values[column_name(dim.upper())] = value

    # - Assign the values.
    # - Order the columns in the standard order.
    df = df.assign(**assign_values).reindex(columns=[ev.value for ev in ColumnName])

    # Save the result to cache
    cache_results(id_str, df)

    # Return the data for use by other code
    return df


@lru_cache()
def fill_values_for_dataflow(dataflow_id: Optional[str]) -> Dict[str, str]:
    """Return a dictionary of fill values for the data flow `dataflow_id`."""
    result: Dict[str, str] = dict()

    if dataflow_id is None:
        return result

    # Retrieve the SDMX data structures
    sm = generate()

    # Data structure for this data set
    dsd = sm.structure[dataflow_id]

    # Iterate over dimensions in the full dimensionality structure
    for dim in sm.structure["HISTORICAL"].dimensions:
        try:
            # Try to retrieve a matching dimension from the structure of this data set
            dsd.dimensions.get(dim.id)
        except KeyError:
            # No match → this dimension is not applicable to this data set → fill
            result[dim.id] = "_Z"

    return result


@lru_cache()
def dim_id_for_column_name(name):
    """Return a dimension ID in the iTEM ‘HISTORICAL’ structure for a column `name`."""
    return {
        "COUNTRY": "_drop",
        "ISO CODE": "REF_AREA",
        "VEHICLE TYPE": "VEHICLE",
        "YEAR": "TIME_PERIOD",
    }.get(name.upper(), name.upper())


@lru_cache()
def get_area_name_map():
    sm = generate()
    return {
        code.name.localized_default().lower(): code.id
        for code in sm.codelist["CL_AREA"]
    }


@lru_cache()
def iso_alpha_3(name: str) -> str:
    """Return ISO 3166 alpha-3 code for a country `name`.

    Parameters
    ----------
    name : str
        Country name. This is looked up in the `pycountry
        <https://pypi.org/project/pycountry/#countries-iso-3166>`_ 'name',
        'official_name', or 'common_name' field. Replacements from
        :data:`COUNTRY_NAME` are applied.
    """
    # lru_cache() ensures this function call is as fast as a dictionary lookup after
    # the first time each country name is seen

    # Maybe map a known, non-standard value to a standard value
    name = COUNTRY_NAME.get(name.lower(), name)

    # Use pycountry's built-in, case-insensitive lookup on all fields including name,
    # official_name, and common_name
    for db in (pycountry.countries, pycountry.historic_countries):
        try:
            return db.lookup(name).alpha_3
        except LookupError:
            continue

    try:
        return get_area_name_map()[name.lower()]
    except KeyError:
        raise LookupError(name)


@lru_cache()
def get_item_region(code: str) -> str:
    """Return iTEM region for a country's ISO 3166 alpha-3 `code`, or “N/A”."""
    return REGION.get(code, "N/A")


@lru_cache()
def get_country_name(code: str) -> str:
    """Return the country name for a country's ISO 3166 alpha-3 `code`."""
    for db in (pycountry.countries, pycountry.historic_countries):
        try:
            return db.get(alpha_3=code).name
        except AttributeError:
            continue

    # Possibly an area code like "B0"
    sm = generate()
    return sm.codelist["CL_AREA"][code].name.localized_default()


def source_str(id):
    """Return the canonical string name (e.g. 'T001') for a data source.

    Parameters
    ----------
    id : int or str
        Integer ID of the data source.
    """
    return f"T{id:03}" if isinstance(id, int) else id
