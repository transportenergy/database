import pandas as pd

#: Input arguments
ARGS = ["T000"]


def compute(activity: pd.DataFrame) -> pd.DataFrame:
    """Quality diagnostic for road share of passenger activity.

    Parameters
    ----------
    activity : pandas.DataFrame
        From :mod:`.T000`.
    """
    # Index columns; all but value
    index_cols = list(filter(lambda c: c not in ("VALUE", "VEHICLE"), activity.columns))

    # Select the numerator and denominator
    num = (
        activity.query("SERVICE == 'P' and MODE == 'Road' and VEHICLE == 'LDV'")
        .drop(columns="VEHICLE")
        .set_index(index_cols)
    )
    denom = (
        activity.query("SERVICE == 'P' and MODE == 'Road' and VEHICLE == '_T'")
        .drop(columns="VEHICLE")
        .set_index(index_cols)
    )

    return (
        (num / denom)
        .dropna()
        .reset_index()
        .assign(VARIABLE="Activity, share of distance", VEHICLE="LDV", UNIT="percent")
    )
