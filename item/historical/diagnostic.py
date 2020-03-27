"""Diagnostics for historical data sets."""


COV_TEXT = """{N_area} areas: {areas}"""


def coverage(df, area='COUNTRY'):
    """Return information about the coverage of a data set."""
    areas = sorted(df[area].unique())
    return COV_TEXT.format(N_area=len(areas), areas=areas)
