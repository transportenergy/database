from collections import OrderedDict
from os.path import join
from typing import Dict

import pandas as pd
import yaml

from item.common import paths

# Metadata on database dimensions
INFO: Dict[str, dict] = {}

# List of the index columns required to identify all data series
INDEX = [
    "model",
    "scenario",
    "region",
    "variable",
    "mode",
    "technology",
    "fuel",
    "unit",
]

# Constants, for e.g. select()
ALL = "All"
PAX = None
FREIGHT = None


def check(A, out_file):
    """Compare a table of quantities, *A*, to the official list.

    The comparison is performed using a database 'outer' join; this preserves
    rows in either table that do not appear in the other.

    Results are written to *out_file*; the last two columns, 'unit_generated'
    and 'unit_official' are filled iff the quantity is present in the
    respective list.

    """
    fn = join(paths["data"], "model", "dimensions", "quantities.tsv")
    B = pd.read_table(fn, sep="\t", comment="#")
    cols = ["variable", "mode", "technology", "fuel"]
    merged = pd.merge(A, B, how="outer", on=cols, suffixes=("_generated", "_official"))
    N = merged.count().to_dict()
    print(
        "Excess generated quantities: {}\nMissing official quantities: {}".format(
            N["variable"] - N["unit_official"], N["variable"] - N["unit_generated"]
        )
    )
    merged.sort_values(by=cols).to_csv(out_file, sep="\t")


def load():
    global PAX, FREIGHT

    # Read the lists of allowable labels for each data dimension
    data = OrderedDict()
    path = paths["data"].joinpath("model", "dimensions")
    for k in ["variable", "mode", "technology", "fuel", "match"]:
        with open(path.joinpath(k).with_suffix(".yaml"), encoding="utf-8") as f:
            data[k] = yaml.safe_load(f)
    variable, mode, tech, fuel, match = data.values()

    # Sets of modes, for convenience
    all_modes = frozenset(mode.keys())
    pax_modes = frozenset(
        [m for m, info in mode.items() if info["type"] == "passenger"]
    )
    PAX = pax_modes
    freight_modes = all_modes - pax_modes
    FREIGHT = freight_modes

    # Read allowable combinations of data dimensions
    # *mode_tech* and *tech_fuel* are now dictionaries mapping from labels on
    # one dimension to allowable labels on the next dimension

    # mode → technology
    mode_tech = match["mode_technology"]
    for t in mode_tech.values():
        t = tuple(["All"] + list(t))
    mode_tech["All"] = ["All"]

    tech_fuel = match["technology_fuel"]
    for f in tech_fuel.items():
        f = tuple(["All"] + list(f))
    tech_fuel["All"] = ["All"]

    INFO.update(data)
    INFO.update(
        {"modes_all": all_modes, "mode_tech": mode_tech, "tech_fuel": tech_fuel}
    )


def generate():
    """Attempt to generate the reporting quantities from simple rules."""
    # Generate the list of quantities
    index = []

    # Iterate through each variable, in order
    for name, var_info in INFO["variable"].items():
        # Determine which modes are reported for this variable
        if var_info.get("global", False):
            # First eight are global quantities—only 'All' modes
            modes = {}
        else:
            # Some variables are only for either passenger or freight modes
            var_type = var_info.get("type", None)

            if var_type == "passenger":
                modes = set(PAX)
            elif var_type == "freight":
                modes = set(FREIGHT)
            elif name == "intensity_new":
                # A specific subset is used for this variable
                modes = {"2W", "Aviation", "Bus", "HDT", "LDV", "Passenger Rail"}
            else:
                # Other variables are reported for all modes, minus the
                # exclusions below
                modes = set(INFO["modes_all"])

            # Further exclusions from some variables
            if name in [
                "ef_bc",
                "intensity_service",
                "tkm",
                "ttw_bc",
                "ttw_ch4",
                "ttw_co2e",
                "ttw_n2o",
                "ttw_pm2.5",
                "vkt",
                "wtt_co2e",
                "wtw_co2e",
            ]:
                modes -= {"Freight Rail and Air and Ship"}

            if name in ["ttw_pm2.5", "wtt_co2e", "wtw_co2e"]:
                modes -= {"International Shipping"}

            if name in ["wtt_co2e", "wtw_co2e"]:
                modes -= {"Domestic Shipping"}

        # Add one entry to quantities for each allowable combination of
        # dimensions
        for m in ["All"] + sorted(modes):
            for t in INFO["mode_tech"][m]:
                for f in INFO["tech_fuel"][t]:
                    index.append([name, m, t, f, var_info["unit"]])

    # Combine into a single table and return
    index = pd.DataFrame(
        index, columns=["variable", "mode", "technology", "fuel", "unit"]
    )
    return index


def list_pairs(in_file, out_file):
    """Helper function for preparing the quantities list.

    Writes a file *out_file* with all unique combinations of variables between
    successive dimesions in *in_file*; that is, all combinations of:
    - variable & mode,
    - mode & technology, and
    - technology & fuel.

    """
    in_path = in_file
    qty = pd.read_table(in_path, sep="\t", comment="#")

    with open(out_file, "w") as f:
        for pair in [
            ["variable", "mode"],
            ["mode", "technology"],
            ["technology", "fuel"],
        ]:
            # Find unique combinations of values in the two columns; sort
            unique = sorted(qty.groupby(pair).groups.keys())
            # Write to file
            f.write(" → ".join(pair) + "\n\n" + "\n".join(map(str, unique)) + "\n\n")


def load_template(version):
    """Load a data submission template for *version*."""
    qty = pd.read_csv(join(dir, "iTEM{}_template.csv".format(version)))
    qty["model"] = ""
    qty["scenario"] = ""
    qty["region"] = ""
    qty["2005"] = True

    # result = as_xarray(qty).sel(Year='2005').squeeze().drop(['model'])
    result = qty
    return result


load()
