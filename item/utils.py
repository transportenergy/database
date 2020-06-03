import pint


def convert_units(df, units_from, units_to, cols=('Value', 'Unit')):
    """Convert units of *df*.

    Uses a vector :class:`pint.Quantity` to convert an entire column of values
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
    ureg = pint.get_application_registry()

    # Create a vector pint.Quantity; convert units
    qty = ureg.Quantity(df[cols[0]].values, units_from).to(units_to)

    # Assign magnitude and unit columns in output DataFrame
    df[cols[0]] = qty.magnitude
    df[cols[1]] = f'{qty.units:~}'

    return df
