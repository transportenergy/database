import logging
from pathlib import Path
from typing import Optional, Sequence

import pandas as pd
import pooch
from iam_units import registry
from platformdirs import user_cache_path

log = logging.getLogger(__name__)


# TODO Add an argument to control the format of the output units
def convert_units(
    df: pd.DataFrame, units_from, units_to, cols: Optional[Sequence[str]] = None
) -> pd.DataFrame:
    """Convert units of `df`.

    Uses a vector :class:`registry.Quantity` to convert an entire column of values
    efficiently.

    Parameters
    ----------
    units_from : str or pint.Unit
        Units to convert from.
    units_to : str or pint.Unit
        Units to convert to.
    cols : 2-tuple of str
        Names of the columns in `df` containing the magnitude and unit, respectively.
        Default for the mangnitude is whichever column of `df` matches “value”, case-
        insensitive; if multiple columns have different cases of this name, the first
        is used.

    Returns
    -------
    pandas.DataFrame
    """
    # Default values
    cols = cols or [
        next(filter(lambda name: name.lower() == "value", df.columns)),
        "UNIT",
    ]

    # Create a vector pint.Quantity; convert units
    qty = registry.Quantity(df[cols[0]].values, units_from).to(units_to)

    # Assign magnitude and unit columns in output DataFrame
    return df.assign(**{cols[0]: qty.magnitude, cols[1]: f"{qty.units:~}"})


def dropna_logged(df, column, log_columns=[]):
    """Drop rows from `df` with NaN values in `column`.

    Counts and unique values for each of `log_columns` are logged.
    """
    # Rows to drop
    to_drop = df[column].isnull()

    log.info(f"{to_drop.sum()} rows with NaN in {repr(column)}")

    for col in log_columns if to_drop.sum() else []:
        # Sorted unique values in column `col`
        values = sorted(df[to_drop][col].unique())
        log.info(f"… with {len(values)} unique values in {repr(col)}: {values}")

    return df[~to_drop]


POOCH = pooch.create(
    path=user_cache_path("item"),
    base_url="https://github.com/transportenergy/metadata/archive/refs/heads",
    registry={
        "main.zip": "sha256:30e9c1d2c3cac1ee4b482ec31af641865103feb061db2bbd400677b62b3c059a"
    },
)


def metadata_repo_file(*parts: str) -> Path:
    """Return the path to a file from the ``transportenergy/metadata`` repository.

    This function fetches and caches a local copy of the data, if necessary.
    """
    import zipfile

    from filelock import FileLock

    # Path to extract files
    path_extract = user_cache_path("item").joinpath("metadata")
    path_extract.mkdir(parents=True, exist_ok=True)

    # Extract files if target directory does not exist or path_archive is newer
    # Lock the directory to avoid conflicting operations in concurrent threads/processes
    with FileLock(path_extract.with_suffix(".lock")):
        # Use Pooch to fetch (if needed) the archive to the cache directory
        path_archive = Path(POOCH.fetch("main.zip"))

        if not (
            path_extract.exists()
            and list(path_extract.iterdir())
            and path_extract.stat().st_mtime > path_archive.stat().st_mtime
        ):
            log.info(f"Unpack {path_archive} → {path_extract}")
            with zipfile.ZipFile(path_archive) as archive:
                archive.extractall(path=path_extract)

    # Use the first subdirectory of path_extract
    subdir = next(path_extract.iterdir())
    # Construct the sub-path to `parts` within the extracted files
    path_result = path_extract.joinpath(subdir, *parts)

    if not path_result.exists():
        raise FileNotFoundError(
            f"{path_result.relative_to(path_extract)} within {path_extract}"
        )
    return path_result
