from item.utils import convert_units
from item.historical import OUTPUT_PATH


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
    # Select activity
    activity = activity.query("Mode == 'Road' and `Vehicle Type` == 'All'").set_index(
        ["ISO Code", "Year"]
    )

    # Select stock
    vehicle_types = [
        "Light goods road vehicles",
        "Lorries (vehicle wt over 3500 kg)",
        "Road tractors",
    ]
    mask = stock.Fuel.isin(["All"]) & stock["Vehicle Type"].isin(vehicle_types)
    stock = stock[mask].groupby(["ISO Code", "Year"]).sum(numeric_only=True)

    df = (
        # Compute ratio, drop nulls
        (activity["Value"] / stock["Value"])
        .dropna()
        # Restore column names, for convert_units()
        .rename("Value")
        .reset_index()
        .assign(Variable="Load factor", Service="Freight", Fuel="All", Mode="Road")
        # To preferred units
        .pipe(convert_units, "Gt km / year / kvehicle", "kt km / year / vehicle")
    )

    # Save output before returning
    df.to_csv(OUTPUT_PATH / "A003.csv")

    return df
