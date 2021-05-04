import logging
from typing import Optional, Sequence

import pandas as pd
from iam_units import registry

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
