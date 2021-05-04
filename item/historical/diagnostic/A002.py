import pandas as pd

from item.util import convert_units

#: Input arguments
ARGS = ["T000", "T008"]


def compute(activity: pd.DataFrame, stock: pd.DataFrame) -> pd.DataFrame:
    """Quality diagnostic for vehicle utilization.

    Parameters
    ----------
    activity : pandas.DataFrame
        From :mod:`.T000`.
    stock : pandas.DataFrame
        From :mod:`.T008`.
    """
    query = "SERVICE == 'P' and MODE == 'Road' and VEHICLE == 'LDV'"

    # Columns to remove for alignment
    # - ID, VARIABLE, UNIT—since these are different quantities.
    # - FUEL: _Z for activity, _T for stock.
    # - AUTOMATION, OPERATOR: _T for activity, _Z for stock.
    remove_cols = ["ID", "VARIABLE", "UNIT", "FUEL", "AUTOMATION", "OPERATOR"]

    # Remaining columns for index
    index_cols = list(
        filter(lambda c: c not in remove_cols + ["VALUE"], activity.columns)
    )

    # Select activity
    activity = activity.query(query).drop(columns=remove_cols).set_index(index_cols)
    # Select stock: this data contain both vehicles and vehicles per capita; use only
    # the former
    stock = (
        stock.query(query + "and UNIT == 'vehicle'")
        .drop(columns=remove_cols)
        .set_index(index_cols)
    )

    # - Compute ratio.
    # - Drop NA values.
    # - Convert units.
    # - Assign 'VARIABLE'.
    return (
        (activity / stock)
        .dropna()
        .reset_index()
        .pipe(
            convert_units,
            "Gpassenger km / vehicle / year",
            "kpassenger km / vehicle / year",
        )
        .assign(VARIABLE="Vehicle activity")
    )
