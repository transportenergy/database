from iam_units import registry


# TODO Add an argument to control the format of the output units
def convert_units(df, units_from, units_to, cols=("Value", "Unit")):
    """Convert units of *df*.

    Uses a vector :class:`registry.Quantity` to convert an entire column of values
    efficiently.

    Parameters
    ----------
    units_from : str or pint.Unit
        Units to convert from.
    units_to : str or pint.Unit
        Units to convert to.
    cols : 2-tuple of str
        Names of the columns in *df* containing the magnitude and unit,
        respectively.

    Returns
    -------
    pandas.DataFrame
    """

    # Create a vector pint.Quantity; convert units
    qty = registry.Quantity(df[cols[0]].values, units_from).to(units_to)

    # Assign magnitude and unit columns in output DataFrame
    return df.assign(**{cols[0]: qty.magnitude, cols[1]: f"{qty.units:~}"})
