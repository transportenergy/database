from item.util import convert_units

#: Input arguments
ARGS = ["T003", "T009"]


def compute(activity, stock):
    """Quality diagnostic for freight load factor.

    Returns the ratio of road freight traffic from :mod:`.T003` and the total number
    of freight vehicles from :mod:`.T009`.

    Parameters
    ----------
    activity : pandas.DataFrame
        From :mod:`.T003`.
    stock : pandas.DataFrame
        From :mod:`.T009`.
    """
    spacetime = ["REF_AREA", "TIME_PERIOD"]

    # Select activity
    activity = activity.query("MODE == 'Road' and VEHICLE == '_T'").set_index(spacetime)

    # Select stock
    mask = stock.FUEL.isin(["_Z"]) & stock.VEHICLE.isin(
        [
            "Light goods road vehicles",
            "Lorries (vehicle wt over 3500 kg)",
            "Road tractors",
        ]
    )
    stock = stock[mask].groupby(spacetime).sum(numeric_only=True)

    return (
        # Compute ratio, drop nulls
        (activity["VALUE"] / stock["VALUE"])
        .dropna()
        # Restore column names, for convert_units()
        .rename("VALUE")
        .reset_index()
        .assign(VARIABLE="Load factor", SERVICE="F", MODE="Road")
        # To preferred units
        .pipe(convert_units, "Gt km / year / kvehicle", "kt km / year / vehicle")
    )
