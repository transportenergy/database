"""Diagnostics for historical data sets."""


COV_TEXT = """{N_area} areas: {areas}
{N_measures} measures: {measures}
{N_periods} periods: {periods[0]}–{last_period}

Measure-by-area coverage:
"""


def coverage(df, area='COUNTRY', measure='VARIABLE', period='TIME_PERIOD'):
    """Return information about the coverage of a data set."""

    # String report
    areas = sorted(df[area].unique())
    measures = sorted(df[measure].unique())
    periods = sorted(df[period].unique())
    result = COV_TEXT.format(
        N_area=len(areas),
        areas=' '.join(areas),
        N_measures=len(measures),
        measures=measures,
        N_periods=len(periods),
        periods=periods,
        last_period=periods[-1]
        )

    counts = df.groupby([measure, area]).count()

    for m, df0 in df.groupby(measure):
        result += f'\n{m}\n'

        for a, df1 in df0.groupby(area):
            # Number of observations. Some observations have a status, but no
            # value
            obs = max(counts.xs((m, a))[['value', 'OBS_STATUS']])

            # Observation value
            values = counts.xs((m, a))['value']

            # Periods appearing in this series
            gp = sorted(df1[period].unique())
            missing = (periods.index(gp[-1]) + 1 - periods.index(gp[0])) - obs

            # Assemble line
            result += (
                f'  {a}: {obs} obs {gp[0]}–{gp[-1]}'
                + (f' ({missing} gaps)' if missing else '')
                + f'; {values} values\n')

    return result
