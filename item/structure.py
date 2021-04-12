import logging
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import sdmx
from sdmx import model

from item.common import paths
from item.sdmx import generate

log = logging.getLogger(__name__)


@lru_cache()
def column_name(id: str) -> str:
    """Return a human-readable name for a dimension in the historical DSD."""
    try:
        value = dict(VARIABLE="Variable", YEAR="Year", ID="ID")[id]
        log.warning(f"Deprecated dimension id: {repr(id)}")
        return value
    except KeyError:
        return (
            generate()
            .structure["HISTORICAL"]
            .dimensions.get(id.upper())
            .concept_identity.name.localized_default()
        )


def add_unit(key: Dict, concept: model.Concept) -> None:
    """Add units to a key."""
    # Retrieve the unit information, stored by read_items()
    anno = list(filter(lambda a: a.id == "preferred_unit", concept.annotations))[0]
    unit = eval(anno[0].text.localized_default(None))

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
    dsd: model.DataStructureDefinition, ids: List
) -> Dict[str, Dict[str, str]]:
    """Return a nested dict for use with :meth:`pandas.DataFrame.replace`.

    For the concept schemes `ids` (e.g. 'mode'), the
    :attr:`~.IdentifiableArtefact.id` attribute of a particulate
    :class:`.Concept` (e.g. 'air') is replaced with its
    :attr:`~.NameableArtefact.name` (e.g. 'Aviation').
    """
    result = defaultdict(dict)
    for id in ids:
        codelist = dsd.dimensions.get(id).local_representation.enumerated
        for code in codelist:
            if code.id == "_Z":
                name = ""
            else:
                name = code.name.localized_default()
                if not len(name):
                    name = code.id.title()

            result[id][code.id] = name

    return result


def merge_dsd(
    sm: sdmx.message.StructureMessage,
    target: str,
    others: List[str],
    fill_value: str = "_Z",
) -> model.DataSet:
    """`Merge` 2 or more data structure definitions."""
    dsd_target = sm.structure[target]

    # Create a temporary DataSet
    ds = model.DataSet(structured_by=dsd_target)

    # Count of keys
    count = 0

    for dsd_id in others:
        # Retrieve the DSD
        dsd = sm.structure[dsd_id]

        # Retrieve a constraint that affects this DSD
        ccs = [cc for cc in sm.constraint.values() if dsd in cc.content]
        assert len(ccs) <= 1
        cc = ccs[0] if len(ccs) and len(ccs[0].data_content_region) else None

        # Key for the VARIABLE dimension
        base_key = model.Key(VARIABLE=dsd_id, described_by=dsd_target.dimensions)

        # Add KeyValues for other dimensions included in the target but not in this DSD
        for dim in dsd_target.dimensions:
            if dim.id in base_key.values or dim.id in dsd.dimensions:
                continue
            base_key[dim.id] = dim.local_representation.enumerated[fill_value]

        # Iterate over the possible keys in `dsd`; add to `k`
        ds.add_obs(
            model.Observation(dimension=(base_key + key).order(), value=np.NaN)
            for key in dsd.iter_keys(constraint=cc)
        )

        log.info(f"{repr(dsd)}: {len(ds.obs) - count} keys")
        count = len(ds.obs)

    log.info(
        f"Total keys: {len(ds.obs)}\n"
        + "\n".join(map(lambda o: repr(o.dimension), ds.obs[:5]))
    )

    return ds


def make_template(output_path: Path = None, verbose: bool = True):
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
    df1 = df0.replace({"_Z": "", np.NaN: "", "(REF_AREA)": "…", "(TIME_PERIOD)": "…"})

    df1.to_csv(output_path / "full.csv")
    df1.to_excel(output_path / "full.xlsx")

    # "Template" format: more human-readable

    # Use names instead of IDs for labels on these dimensions
    replacements = name_for_id(
        sm.structure["HISTORICAL"],
        (
            "AUTOMATION FLEET FUEL MODE OPERATOR POLLUTANT SERVICE TECHNOLOGY VARIABLE "
            "VEHICLE"
        ).split(),
    )
    # Rename all columns except "Value" using data structure info
    columns = {name: column_name(name) for name in df1.columns[:-1]}
    columns["VALUE"] = "Value"

    # Apply replacements; use collapse() above to reduce number of columns
    df2 = df1.replace(replacements).apply(collapse, axis=1).rename(columns=columns)

    df2.to_csv(output_path / "condensed.csv", index=False)
    df2.to_excel(output_path / "condensed.xlsx", index=False)

    # Output the index
    df3 = pd.concat({"FULL": df0, "CONDENSED": df1}, axis=1)
    df3.to_csv(output_path / "index.csv")
    df3.to_excel(output_path / "index.xlsx")
