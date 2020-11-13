import operator
from functools import reduce
from itertools import chain
from os.path import join
from textwrap import indent
from typing import Any, Dict, List

import plotnine

from item.common import paths
from item.model.common import INDEX, select
from item.model.dimensions import INFO

scale_linetype_scenario = plotnine.scale_linetype(limits=["reference", "policy"])


def min_max(data, dims):
    """Add 'min' and 'max' columns to *data*, grouped on *dims*."""
    grp = data.groupby(dims)["value"]
    data["min"] = grp.transform("min")
    data["max"] = grp.transform("max")
    data["mean"] = grp.transform("mean")
    data["std"] = grp.transform("std")
    return data


def plot_all_item1():
    """Produce all plots for the iTEM1 database."""
    from plotnine import aes, facet_grid, geom_bar, labs

    from item.model import load_model_data, squash_scenarios
    from item.model.dimensions import ALL, PAX

    class pass_energy_use_mode(Plot):
        """Passenger energy use by mode.

        This reproduces a figure from the (private) item2-scripts respository.
        """

        variable = "energy"
        selectors = dict(
            region="Global", mode=PAX, tech=ALL, fuel=ALL, year=[2015, 2030, 2050]
        )
        terms = [
            aes("year", "value / 1000", fill="mode"),
            geom_bar(stat="identity"),
            facet_grid(["scenario", "model"]),
            labs(x="Year", y="EJ/year"),
        ]

    df = load_model_data(1)
    df = squash_scenarios(df, 1)
    pass_energy_use_mode(df, 1).save()


class Plot:
    """Plot class.

    Subclass Plot, overriding the variables below and optionally
    the filter() method, to create plots.
    """

    # Selectors to subset the data
    select: Dict[str, Any] = {}

    # Aesthetic mapping for plotnine.aes
    aes: Dict[str, Any] = {}

    # Sequence of plotnine terms
    # TODO more specific typing
    terms: List[Any] = []

    def filter(self, data):
        """Override this method to filter or transform the selected data."""
        return data

    @classmethod
    def from_dict(cls, name, attrs={}):
        """Create a Plot subclass with given *name* and *attrs*."""
        import pandas

        # Environments for parsing
        term_globals = {
            "scale_linetype_scenario": scale_linetype_scenario,
        }
        term_globals.update(plotnine.__dict__)
        filter_globals = {
            "pd": pandas,
            "min_max": min_max,
        }

        # Attrs for the new class
        new_attrs = {
            "aes": cls.aes.copy(),
            "select": cls.select.copy(),
            "terms": cls.terms.copy(),
            "filter": cls.filter,
        }

        # Preprocess the info
        for key, value in attrs.items():
            if key in ("aes", "select"):
                new_attrs[key].update(value)
            elif key == "terms":
                # Evaluate the terms as if "from plotnine import *"
                new_attrs["terms"] = list(map(lambda s: eval(s, term_globals), value))
            elif key == "filter":
                # Construct a function
                source = "def filter(self, data):\n" + indent(value, "    ")
                tmp = {}
                exec(source, filter_globals, tmp)
                new_attrs.update(tmp)

        # Define and return the new class
        return type(name, (cls,), new_attrs)

    def __init__(self, data, *fn_extra):
        # Subset the data

        # Query
        selectors = self.select.copy()
        query = selectors.pop("query", None)
        if query:
            data = data.query(query)

        # Select
        data = select(data, **selectors)

        # Filter
        data = self.filter(data)

        # Produce labels from the aesthetic mapping
        labels = {}
        for k, v in self.aes.items():
            # Dimensions like 'fuel' → title case
            if v in INDEX:
                labels[k] = v.title()

            # Label the value using the variable information
            if v == "value":
                var = data["variable"].unique()
                assert len(var) == 1
                var_info = INFO["variable"][var[0]]
                labels[k] = "{} [{}]".format(var[0], var_info["unit"])

        # Chain together the terms to produce the figure
        figure = reduce(
            operator.add,
            chain(
                [
                    plotnine.ggplot(data),
                    plotnine.aes(**self.aes),
                    # Use the generated labels first, to allow the terms to override
                    plotnine.labs(**labels),
                ],
                self.terms,
            ),
        )

        # Compose the filename
        fn_extra = map(str, fn_extra)
        name = "_".join(chain([self.__class__.__name__], fn_extra))
        filename = join(paths["plot"], "%s.%s" % (name, "pdf"))

        # Save
        figure.save(filename, width=128, height=96, units="mm")
