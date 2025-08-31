from collections.abc import Sequence
from functools import cache
from itertools import chain
from os.path import join
from typing import TYPE_CHECKING, Dict

import pandas as pd

from item.common import paths

if TYPE_CHECKING:
    from sdmx.model.common import Code

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
PAX: frozenset[str] = frozenset()
FREIGHT: frozenset[str] = frozenset()


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
    from . import structure

    global PAX, FREIGHT

    # Retrieve codelists for each data dimension
    INFO["fuel"] = structure.get_cl_fuel()
    mode = INFO["mode"] = structure.get_cl_mode()
    INFO["technology"] = structure.get_cl_technology()
    INFO["variable"] = structure.get_cl_measure()

    # Sets of modes, for convenience
    all_modes, pax_modes, freight_modes = set(), set(), set()
    for m in mode:
        try:
            service = str(m.get_annotation(id="SERVICE").text)
        except KeyError:
            pass
        else:
            if service == "passenger":
                pax_modes.add(m.id)
            elif service == "freight":
                freight_modes.add(m.id)
        all_modes.add(m.id)

    PAX = frozenset(pax_modes)
    FREIGHT = frozenset(freight_modes)
    INFO.update(modes_all=frozenset(all_modes))


#: Exclusions for :func:`generate`.
EXCLUDE_MODE = {
    "ef_bc": {"Freight Rail and Air and Ship"},
    "intensity_service": {"Freight Rail and Air and Ship"},
    "tkm": {"Freight Rail and Air and Ship"},
    "ttw_bc": {"Freight Rail and Air and Ship"},
    "ttw_ch4": {"Freight Rail and Air and Ship"},
    "ttw_co2e": {"Freight Rail and Air and Ship"},
    "ttw_n2o": {"Freight Rail and Air and Ship"},
    "ttw_pm2.5": {"Freight Rail and Air and Ship", "International Shipping"},
    "vkt": {"Freight Rail and Air and Ship"},
    "wtt_co2e": {
        "Domestic Shipping",
        "Freight Rail and Air and Ship",
        "International Shipping",
    },
    "wtw_co2e": {
        "Domestic Shipping",
        "Freight Rail and Air and Ship",
        "International Shipping",
    },
}


def generate():
    """Attempt to generate the reporting quantities from simple rules."""
    # Generate the list of quantities
    index = []

    @cache
    def _tf(technology: "Code") -> Sequence[tuple[str, str]]:
        """Return a sequence of valid (t, f) indices for `technology`."""
        result = []

        for f in technology.eval_annotation(id="FUEL") or INFO["fuel"]:
            result.append((technology.id, f))
        return tuple(result)

    @cache
    def _mtf(mode: "Code") -> Sequence[tuple[str, str, str]]:
        """Return a sequence of valid (m, t, f) indices for `mode`."""
        result: list[tuple[str, str, str]] = []

        for t in mode.eval_annotation(id="TECHNOLOGY") or INFO["technology"]:
            t_code = INFO["technology"][t]
            result.extend((mode.id, t, f) for (t, f) in _tf(t_code))

        return tuple(result)

    # Iterate through each measure concept, in order
    for measure in INFO["variable"]:
        # Retrieve information from annotations
        global_ = measure.eval_annotation(id="is-global")
        u = str(measure.get_annotation(id="UNIT_MEASURE").text)

        # Determine which modes are relevant for this measures
        modes = {m.id for m in INFO["mode"]}
        if not global_:
            # Some measures are relevant only for either passenger or freight modes
            try:
                service = str(measure.get_annotation(id="SERVICE").text)
            except KeyError:
                service = None

            if service == "passenger":
                modes = set(PAX)
            elif service == "freight":
                modes = set(FREIGHT)
            elif measure.id == "intensity_new":
                # A specific subset is used for this measure
                modes = {"2W", "Aviation", "Bus", "HDT", "LDV", "Passenger Rail"}

            # Further exclude
            modes -= EXCLUDE_MODE.get(measure.id, set())

        # Convert set of mode IDs to a list of codes
        m_codes = [INFO["mode"][m] for m in modes]

        # Add one entry to quantities for each allowable combination of dimensions
        index.extend(
            [measure.id, m, t, f, u] for (m, t, f) in chain(*map(_mtf, m_codes))
        )

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
