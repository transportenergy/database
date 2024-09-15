import logging
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Mapping, Optional

import numpy as np
import pandas as pd
import sdmx
import sdmx.model.common as m

from item.common import paths
from item.structure.sdmx import _get_anno, generate, merge_dsd

if TYPE_CHECKING:
    import sdmx.model.common

log = logging.getLogger(__name__)


def add_unit(key: Dict, concept: m.Concept) -> None:
    """Add units to a key."""
    # Retrieve the unit information, stored by read_items()
    unit = _get_anno(concept, "preferred_unit")

    if isinstance(unit, str):
        key["unit"] = unit
    else:
        # Conditional units
        for condition, unit in unit.items():
            dim, value = condition.split(" == ")
            if dim in key and key[dim] == value:
                key["unit"] = unit
                return


def collapse(row: pd.Series) -> pd.Series:
    """Collapse multiple concepts into fewer columns.

    - VARIABLE label is formatted using the labels for LCA_SCOPE, POLLUTANT, and/or
      FLEET.
    - MODE label is formatted using the labels for SERVICE, VEHICLE, AUTOMATION and/or
      OPERATOR.
    """
    data = row.to_dict()

    # Combine 3 concepts with the measure name ("VARIABLE")
    fleet = data.pop("FLEET")
    lca_scope = data.pop("LCA_SCOPE")
    pollutant = data.pop("POLLUTANT")

    data["VARIABLE"] = (
        f"{pollutant} {data['VARIABLE']}"
        + (f" ({lca_scope})" if len(lca_scope) else "")
        + (f" ({fleet.lower()} vehicles)" if fleet not in ("Total", "") else "")
    ).strip()

    # Combine 4 concepts with "MODE"
    service = data.pop("SERVICE")
    vehicle = data.pop("VEHICLE")
    operator = data.pop("OPERATOR")
    automation = data.pop("AUTOMATION")

    if len(operator) and len(automation) and data["MODE"] == "Light-duty vehicle":
        automation = "" if automation == "Human" else " AV"
        oa = " ({}{})".format(operator.lower(), automation)
    else:
        oa = ""

    data["MODE"] = (
        (f"{service} " if service != "Total" else "")
        + data["MODE"]
        + (f" {vehicle}" if vehicle != "Total" else "")
        + oa
    ).strip()

    return pd.Series(data)


def name_for_id(
    dsd: "sdmx.model.common.BaseDataStructureDefinition", ids: List[str]
) -> Mapping[str, Dict[str, str]]:
    """Return a nested dict for use with :meth:`pandas.DataFrame.replace`.

    For the concept schemes `ids` (e.g. 'mode'), the
    :attr:`~.IdentifiableArtefact.id` attribute of a particulate
    :class:`.Concept` (e.g. 'air') is replaced with its
    :attr:`~.NameableArtefact.name` (e.g. 'Aviation').
    """
    result: Mapping[str, Dict[str, str]] = defaultdict(dict)
    for id in ids:
        codelist = dsd.dimensions.get(id).local_representation.enumerated  # type: ignore [union-attr]
        assert codelist is not None

        for code in codelist:
            if code.id == "_Z":
                name = ""
            else:
                name = code.name.localized_default()
                if not len(name):
                    name = code.id.title()

            result[id][code.id] = name

    return result


def make_template(output_path: Optional[Path] = None, verbose: bool = True):
    """Generate a data template.

    Outputs files containing all keys specified for the iTEM ``HISTORICAL`` data
    structure definition. The file is produced in two formats:

    - :file:`*.csv`: comma-separated values
    - :file:`*.xlsx`: Microsoft Excel.

    …and in three variants:

    - :file:`full.*`: with full dimensionality for every concept.
    - :file:`condensed.*`: with a reduced number of dimensions, with labels for some
      dimensions combining labels for others in shorter, conventional, human-readable
      form.
    - :file:`index.*`: an index or map between the two above versions.

    See also
    --------
    .collapse
    """
    # TODO Use SDMX constraints to filter on concepts that are parents of other concepts

    sm = generate()

    ds = merge_dsd(
        sm,
        "HISTORICAL",
        [
            "GDP",
            "POPULATION",
            "PRICE_FUEL",
            "PRICE_POLLUTANT",
            "ACTIVITY_VEHICLE",
            "ACTIVITY",
            "ENERGY",
            "EMISSIONS",
            "ENERGY_INTENSITY",
            "SALES",
            "STOCK",
            "LOAD_FACTOR",
        ],
    )

    # Convert to pd.DataFrame
    df0 = sdmx.to_pandas(ds).reset_index()

    # Save in multiple formats
    output_path = output_path or paths["output"]
    log.info(f"Output to {output_path}/{{index,template}}.{{csv,xlsx}}")

    # "Index" format: only simple replacements, full dimensionality
    df1 = df0.replace({"_Z": "", np.nan: "", "(REF_AREA)": "…", "(TIME_PERIOD)": "…"})

    df1.to_csv(output_path / "full.csv")
    df1.to_excel(output_path / "full.xlsx")

    # "Template" format: more human-readable

    # Use names instead of IDs for labels in these dimensions
    replacements = name_for_id(
        sm.structure["HISTORICAL"],
        (
            "AUTOMATION FLEET FUEL MODE OPERATOR POLLUTANT SERVICE TECHNOLOGY VARIABLE "
            "VEHICLE"
        ).split(),
    )
    # Rename all columns except "Value" using data structure info
    columns = dict()
    for dim_id in df1.columns:
        try:
            name = (
                sm.structure["HISTORICAL"]
                .dimensions.get(dim_id)
                .concept_identity.name.localized_default()  # type: ignore [union-attr]
            )
        except (KeyError, AttributeError):
            # Use the dimension ID in title case for VARIABLE and VALUE, which do not
            # have a .concept_identity
            name = dim_id.title()
        finally:
            columns[dim_id] = name

    # Apply replacements; use collapse() above to reduce number of columns
    df2 = df1.replace(replacements).apply(collapse, axis=1).rename(columns=columns)

    df2.to_csv(output_path / "condensed.csv", index=False)
    df2.to_excel(output_path / "condensed.xlsx", index=False)

    # Output the index
    df3 = pd.concat({"FULL": df0, "CONDENSED": df1}, axis=1)
    df3.to_csv(output_path / "index.csv")
    df3.to_excel(output_path / "index.xlsx")
