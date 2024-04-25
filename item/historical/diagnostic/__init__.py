"""Diagnostics for historical data sets."""

from importlib import import_module
from pathlib import Path

import pandas as pd

from item.historical import fetch_source, source_str

# Quality checks
QUALITY = ["A001", "A002", "A003"]

# Jinja2 template for diagnostics index page
INDEX_TEMPLATE = """<html><body>
{% for group_name, paths in groups.items() %}
<h1>{{ group_name|title }}</h1>

<ul>
{% for path in paths %}
  <li><a href="./{{ path }}">{{ path }}</a></li>
{% endfor %}
</ul>
{% endfor %}
</body></html>
"""

# Template for coverage()
COV_TEXT = """{N_area} areas: {areas}
{N_measures} measures: {measures}
{N_periods} periods: {periods[0]}–{last_period}

Measure-by-area coverage:
"""


def coverage(df, area="COUNTRY", measure="VARIABLE", period="TIME_PERIOD"):
    """Return information about the coverage of a data set."""

    # String report
    areas = sorted(df[area].unique())
    measures = sorted(df[measure].unique())
    periods = sorted(df[period].unique())
    result = COV_TEXT.format(
        N_area=len(areas),
        areas=" ".join(areas),
        N_measures=len(measures),
        measures=measures,
        N_periods=len(periods),
        periods=periods,
        last_period=periods[-1],
    )

    counts = df.groupby([measure, area]).count()

    for m, df0 in df.groupby(measure):
        result += f"\n{m}\n"

        for a, df1 in df0.groupby(area):
            # Number of observations. Some observations have a status, but no
            # value
            obs = max(counts.xs((m, a))[["value", "OBS_STATUS"]])

            # Observation value
            values = counts.xs((m, a))["value"]

            # Periods appearing in this series
            gp = sorted(df1[period].unique())
            missing = (periods.index(gp[-1]) + 1 - periods.index(gp[0])) - obs

            # Assemble line
            result += (
                f"  {a}: {obs} obs {gp[0]}–{gp[-1]}"
                + (f" ({missing} gaps)" if missing else "")
                + f"; {values} values\n"
            )

    return result


def run_all(output_path):
    """Run all diagnostics."""
    from zipfile import ZIP_DEFLATED, ZipFile

    from jinja2 import Template

    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    data_files = []

    # Coverage
    groups = {"Coverage": [], "Quality": []}

    for source_id in [0, 1, 2, 3]:
        # Output filename
        filename = f"{source_str(source_id)}.txt"
        groups["Coverage"].append(filename)

        # Read source data
        data_files.append(fetch_source(source_id, use_cache=True))
        data = pd.read_csv(data_files[-1])

        # Generate coverage and write to file
        # TODO this doesn't allow for column names other than the defaults to
        #      coverage(), above; generalize
        (output_path / filename).write_text(coverage(data))

    # Quality checks
    from item.historical import process

    for check in QUALITY:
        # Import
        check_module = import_module(f"item.historical.diagnostic.{check}")

        # Output filename
        filename = f"{check}.csv"
        groups["Quality"].append(filename)
        data_files.append(output_path / filename)

        # Generate inputs
        inputs = [process(arg) for arg in check_module.ARGS]

        # Compute and save
        check_module.compute(*inputs).to_csv(data_files[-1])

    # Archive data files
    zf = ZipFile(
        output_path / "data.zip", mode="w", compression=ZIP_DEFLATED, compresslevel=9
    )
    for path in data_files:
        zf.write(filename=path, arcname=path.name)

    groups["Cached raw source data"] = ["data.zip"]

    # Generate index file
    t = Template(INDEX_TEMPLATE)
    (output_path / "index.html").write_text(t.render(groups=groups))
