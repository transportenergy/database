import logging

log = logging.getLogger(__name__)


def dropna_logged(df, column, log_columns=[]):
    """Drop rows from `df` with NaN values in `column`.

    Counts and unique values for each of `log_columns` are logged.
    """
    # Rows to drop
    to_drop = df[column].isnull()

    log.info(f"{to_drop.sum()} rows with NaN in {repr(column)}")

    for col in log_columns:
        # Sorted unique values in column `col`
        values = sorted(df[to_drop][col].unique())
        log.info(f"… with {len(values)} unique values in {repr(col)}: {values}")

    return df[~to_drop]
