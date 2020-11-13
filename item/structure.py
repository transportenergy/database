from itertools import product
from pathlib import Path
from typing import Dict, List

import pandas as pd
import yaml
from pandas.core.computation.ops import UndefinedVariableError
from sdmx.model import Annotation, Concept, ConceptScheme

from item.common import paths


def read_items(root: Dict, klass=Concept):
    """Recursively read items and children."""
    result = []

    # Iterate over keys and children
    for item_id, contents in root.items():
        if item_id.startswith("_"):
            # This child is an attribute value like _name
            continue

        # No children, _name, _description, etc.
        contents = contents or {}

        # Create an object
        item = klass(
            id=item_id,
            name=contents.get("_name", item_id.title()),
            description=contents.get("_description", {}),
        )

        unit = contents.get("_unit", None)
        if unit:
            item.annotations.append(
                Annotation(id="unit", type="py:dict", text=repr(unit))
            )

        # Append to the result
        result.append(item)

        # Parse children recursively
        for child in read_items(contents, klass):
            item.append_child(child)
            result.append(child)

    return result


def common_dim_dummies():
    """Yield ConceptSchemes for the common dimensions.

    Each of these has only 1 item. Submitted datasets will have multiple values
    along each of these dimensions.
    """

    c_all = Concept(id="[All]", name="[all model values]")
    c_all = {c_all.id: c_all}
    c_total = Concept(id="[All + World]", name="[Global total or average]")
    c_total = {c_total.id: c_total}

    yield ConceptScheme(id="model", name="Model", items=c_all)
    yield ConceptScheme(id="scenario", name="Scenario", items=c_all)
    yield ConceptScheme(id="region", name="Region", items=c_total)
    yield ConceptScheme(id="year", name="Year", items=c_all)


def add_unit(key: Dict, concept: Concept) -> None:
    """Add units to a key."""
    # Retrieve the unit information, stored by read_items()
    anno = list(filter(lambda a: a.id == "unit", concept.annotations))
    assert len(anno) == 1
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


def read_concepts_yaml(path: Path) -> Dict[str, ConceptScheme]:
    """Read concepts from file.

    See Also
    --------
    :ref:`concepts-yaml`
    read_items
    """
    data = yaml.safe_load(open(path))

    concept_schemes = []

    for id, cs_data in data.items():
        concept_schemes.append(ConceptScheme(id=id, items=read_items(cs_data, Concept)))

    # Add common dimensions
    concept_schemes.extend(common_dim_dummies())

    # Reorganize as a dict
    return {cs.id: cs for cs in concept_schemes}


def read_measures_yaml(path: Path) -> ConceptScheme:
    """Read measures from file.

    See Also
    --------
    :ref:`measures-yaml`
    read_items
    """
    data = yaml.safe_load(open(path))
    return ConceptScheme(id="measure", items=read_items(data))


def collapse(row: pd.Series) -> pd.Series:
    """Collapse multiple concepts into fewer columns.

    - 'measure' column gets 'lca_scope', 'pollutant', and/or 'fleet'.
    - 'mode' column gets 'type', 'vehicle', and/or 'operator'.
    """
    data = row.to_dict()

    # Combine 3 concepts with 'measure' ("Variable")
    lca_scope = data.pop("lca_scope", "")
    if len(lca_scope):
        data["measure"] += " (" + lca_scope + ")"

    pollutant = data.pop("pollutant", "")
    if len(pollutant):
        data["measure"] = pollutant + " " + data["measure"]

    fleet = data.pop("fleet", "")
    if len(fleet):
        if data["measure"] == "Energy intensity" and fleet == "all":
            fleet = ""
        else:
            fleet = " (" + fleet + " vehicles)"
        data["measure"] += fleet

    # Combine 4 concepts with 'mode'
    type = data.pop("type", "")
    if len(type):
        if data["mode"] in ["Road", "Rail"]:
            data["mode"] = type + " " + data["mode"]
        elif data["mode"] == "All":
            data["mode"] = data["mode"] + " " + type

    vehicle = data.pop("vehicle", "")
    if len(vehicle) and vehicle != "All":
        data["mode"] = vehicle

    operator = data.pop("operator", "")
    automation = data.pop("automation", "")
    if len(operator) and len(automation) and data["mode"] == "LDV":
        automation = "" if automation == "Human" else " AV"
        data["mode"] += " ({}{})".format(operator.lower(), automation)

    return pd.Series(data)


def name_for_id(concept_schemes: Dict, ids: List) -> Dict[str, Dict[str, str]]:
    """Return a nested dict for use with :meth:`pandas.DataFrame.replace`.

    For the concept schemes `ids` (e.g. 'mode'), the
    :attr:`~.IdentifiableArtefact.id` attribute of a particulate
    :class:`.Concept` (e.g. 'air') is replaced with its
    :attr:`~.NameableArtefact.name` (e.g. 'Aviation').
    """
    result = dict()
    for id in ids:
        cs = concept_schemes[id]
        result[id] = {c.id: c.name.localized_default() for c in cs.items.values()}

    # Where 'all' appears in the technology column, the template requests
    # totals
    result["technology"]["all"] = "Total"

    return result


def make_template(output_path: Path = None, verbose: bool = True):
    """Generate a data template.

    Outputs files containing all keys specified in the :ref:`spec-yaml`. The
    file is produced in two formats:

    - :file:`template.csv`: comma-separated values.
    - :file:`template.xlsx`: Microsoft Excel.

    An 'index' file is also created (:file:`index.csv`, :file:`index.xlsx`).
    This file maps between 'Full dimensionality' keys (i.e. with all conceptual
    dimensions), and the 'Template (reduced)' columns appearing in
    :file:`template.csv`.
    """
    # TODO Use SDMX constraints to filter on concepts that are parents of other
    #      concepts

    # Concepts (used as dimensions) and possible values
    cs = read_concepts_yaml(paths["data"] / "concepts.yaml")

    # Measures, annotated by their units
    cs["measure"] = read_measures_yaml(paths["data"] / "measures.yaml")

    # Common dimensions applied to all keys
    common_dims = ["model", "scenario", "region", "year"]

    # Read specification of the template
    specs = yaml.safe_load(open(paths["data"] / "spec.yaml"))

    # Filters to reduce the set of Keys; see below at 'Filter Keys'
    exclude_global = []

    # Processed dataframes
    dfs = []

    # Process each entry in the spec file
    for n_spec, spec in enumerate(specs):
        # List of Key objects representing data
        keys = []

        try:
            # Retrieve the measure to add to the key later
            measure_id = spec.pop("measure")
            measure_concept = cs["measure"][measure_id]
        except KeyError:
            # Entry without a 'measure:' key is a list of global filters
            exclude_global = spec.pop("exclude")
            continue

        # List of dimensions for these Keys
        key_dims = common_dims + spec.pop("dims", [])

        # A list of iterable objects containing the values along each dimension
        iters = [iter(cs[d]) for d in key_dims]

        # Iterate, adding keys by Cartesian product over the dimensions
        for values in product(*iters):
            # Create a 'key' with these values, the sort order, and the measure
            key = dict(
                zip(key_dims, map(lambda c: c.id, values)),
                sort_order=n_spec,
                measure=measure_concept.id,
            )

            # Add appropriate units
            add_unit(key, measure_concept)

            # Store the Key
            keys.append(key)

        if verbose:
            print(f"\nSpec for {repr(measure_concept.id)}: {len(keys)} keys")

        # Convert list → DataFrame for filtering
        df = pd.DataFrame(keys).fillna("")

        # Filter Keys by both global and spec-specific filters
        for filter in exclude_global + spec.pop("exclude", []):
            # 'not' operator (~) to exclude the matching rows
            query_str = "~({})".format(filter)

            try:
                df.query(query_str, inplace=True)
            except UndefinedVariableError:
                # Filter references a dimension that's not in this dataframe;
                # the filter isn't relevant
                continue

            if verbose:
                print(f"  {df.shape[0]:5d} after constraint {query_str}")

        # Store the filtered keys as a dataframe
        dfs.append(df)

    # Combine all dataframes
    specs = pd.concat(dfs, axis=0, sort=False).fillna("")

    # Convert to the traditional iTEM format

    # Use names instead of IDs for these columns
    use_name_cols = [
        "type",
        "mode",
        "vehicle",
        "technology",
        "fuel",
        "pollutant",
        "automation",
        "operator",
        "measure",
    ]

    # Order of output columns
    target_cols = common_dims[:-1] + [
        "measure",
        "unit",
        "mode",
        "technology",
        "fuel",
        "year",
    ]

    # Columns to sort content
    sort_cols = [
        "sort_order",
        "measure",
        "unit",
        "type",
        "mode",
        "vehicle",
        "technology",
        "fuel",
        "lca_scope",
        "pollutant",
    ]

    replacements = name_for_id(cs, use_name_cols)

    # Chain several operations for better performance
    # - Replace some IDs with names
    # - Sort
    # - Save the full-resolution version as *specs_full*
    # - Collapse multiple columns into fewer
    # - Set preferred column order, drop the integer index
    # - Rename columns to Title Case
    specs_full = (
        specs.replace(replacements).sort_values(by=sort_cols).reset_index(drop=True)
    )
    specs = (
        specs_full.apply(collapse, axis=1)
        .reindex(columns=target_cols)
        .rename(columns={"measure": "variable"})
        .rename(columns=lambda name: name.title())
    )

    if verbose:
        print("", f"Total keys: {specs.shape[0]}", specs.head(10), sep="\n\n")

    # Save in multiple formats
    output_path = output_path or paths["output"]

    specs.to_csv(output_path / "template.csv", index=False)
    specs.to_excel(output_path / "template.xlsx", index=False)

    # Construct the index:
    # - Horizontally concatenate the full-dimension and 'collapse' (with
    #   'variable' column) data frames.
    # - Drop the dummy dimensions.
    # - Use '---' in empty cells for clarity.
    index_data = {"Full dimensionality": specs_full, "Template (reduced)": specs}
    index = (
        pd.concat(index_data, axis=1)
        .drop(columns=common_dims + list(map(str.title, common_dims)), axis=1, level=1)
        .replace("", "---")
    )

    # Save the index
    index.to_csv(output_path / "index.csv")
    index.to_excel(output_path / "index.xlsx")
