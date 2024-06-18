import logging
from collections import ChainMap
from datetime import datetime
from functools import lru_cache
from typing import TYPE_CHECKING, List, cast

import numpy as np
import sdmx.message as msg
from sdmx import Client
from sdmx.model import common as m
from sdmx.model.v21 import (
    DataKey,
    DataKeySet,
    DataSet,
    MeasureDimension,
    MemberSelection,
    MemberValue,
    Observation,
    PrimaryMeasure,
)

from item.structure import base

if TYPE_CHECKING:
    import sdmx.model.common
    import sdmx.model.v21

log = logging.getLogger(__name__)


def _get_anno(obj, id):
    """Wrapper around :meth:`AnnotableArtefact.get_annotation`.

    Like :func:`_pop_anno`, but doesn't remove the annotation.
    """
    try:
        return eval(obj.get_annotation(id=id).text.localized_default())
    except KeyError:
        return None


def _pop_anno(obj, id):
    """Wrapper around :meth:`AnnotableArtefact.pop_annotation`.

    Inverse of :func:`_annotate`.
    """
    try:
        return eval(obj.pop_annotation(id=id).text.localized_default())
    except KeyError:
        return None


@lru_cache()
def get_cdc():
    """Retrieve the ``CROSS_DOMAIN_CONCEPTS`` from the SDMX Global Registry."""
    id = "CROSS_DOMAIN_CONCEPTS"
    msg = Client("SGR").conceptscheme(id)
    return msg.concept_scheme[id]


@lru_cache()
def generate() -> msg.StructureMessage:
    """Return the SDMX data structures for iTEM data."""
    item_agency = base.AS_ITEM["iTEM"]

    sm = msg.StructureMessage(
        header=msg.Header(sender=item_agency, prepared=datetime.now())
    )

    # Add the AgencyScheme containing iTEM
    sm.organisation_scheme[base.AS_ITEM.id] = base.AS_ITEM

    # Add concept schemes
    for cs in base.CONCEPT_SCHEMES:
        sm.concept_scheme[cs.id] = cs
        # Ensure concepts are associated to their parent scheme
        for item in cs:
            item.parent = item.parent or cs

    # Process and add code lists
    for id, codes in base.CODELISTS.items():
        # Create a code list object
        cl: "sdmx.model.common.Codelist" = m.Codelist(id=f"CL_{id}")

        # Add each code and any children
        # TODO move this upstream to sdmx1
        for c in codes:
            cl.append(c)
            cl.extend(c.child)

        # Add to the message
        sm.codelist[cl.id] = cl

    # Process and add data structure definitions
    for dsd in base.DATA_STRUCTURES:
        prepare_dsd(dsd, sm)

        # Add to the message
        sm.structure[dsd.id] = dsd

    # Process and add content constraints
    for cc in base.CONSTRAINTS:
        # Add the constraint to the message
        sm.constraint[cc.id] = cc

        # Look up the object that is constrained
        try:
            dsd = sm.structure[cc.id]
        except KeyError:
            log.info(f"No constraint(s) for {repr(dsd)}")
            continue

        # Update the constraint with a reference to the DSD
        cc.content.add(dsd)

        # Convert annotations into DataKeySet and CubeRegion objects, associated with
        # the DSDs
        dks_from_anno(cc, dsd)
        cr_from_anno(cc, dsd)

        # Update the constraint using applicable CubeRegions from GENERAL0, GENERAL1,
        # etc.
        merge_general_constraints(cc, dsd, sm)

    # Add MaintainableArtefact properties to all objects
    for kind in (
        "codelist",
        "concept_scheme",
        "constraint",
        "organisation_scheme",
        "structure",
    ):
        for obj in getattr(sm, kind).values():
            obj.maintainer = item_agency
            obj.version = base.VERSION
            obj.is_external_reference = False

    return sm


def merge_dsd(
    sm: msg.StructureMessage,
    target: str,
    others: List[str],
    fill_value: str = "_Z",
) -> "sdmx.model.v21.DataSet":
    """‘Merge’ 2 or more data structure definitions."""
    dsd_target = sm.structure[target]

    # Create a temporary DataSet
    ds: "sdmx.model.v21.DataSet" = DataSet(structured_by=dsd_target)

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
        base_key = m.Key(VARIABLE=dsd_id, described_by=dsd_target.dimensions)

        # Add KeyValues for other dimensions included in the target but not in this DSD
        for dim in dsd_target.dimensions:
            if dim.id in base_key.values or dim.id in dsd.dimensions:
                continue
            base_key[dim.id] = dim.local_representation.enumerated[fill_value]

        # Iterate over the possible keys in `dsd`; add to `k`
        ds.add_obs(
            Observation(dimension=(base_key + key).order(), value=np.nan)
            for key in dsd.iter_keys(constraint=cc)
        )

        log.info(f"{repr(dsd)}: {len(ds.obs) - count} keys")
        count = len(ds.obs)

    log.info(
        f"Total keys: {len(ds.obs)}\n"
        + "\n".join(map(lambda o: repr(o.dimension), ds.obs[:5]))
    )

    return ds


def prepare_dsd(
    dsd: "sdmx.model.v21.DataStructureDefinition", sm: msg.StructureMessage
):
    """Populate data structures within `dsd`."""
    # Concepts for each dimension of each DSD
    dsd_concepts = ChainMap(
        sm.concept_scheme["TRANSPORT"].items,
        sm.concept_scheme["MODELING"].items,
        # Retrieve the CROSS_DOMAIN_CONCEPTS scheme from the SDMX Global Registry
        get_cdc(),
    )

    try:
        # Pop an annotation and use it to produce a list of dimension IDs
        dims = _pop_anno(dsd, "_dimensions").split()
    except AttributeError:
        # No dimensions
        dims = []

    # Add common dimensions
    dims = dims + ["REF_AREA", "TIME_PERIOD"]

    # Add dimensions to the data structure
    for order, concept_id in enumerate(dims):
        # Locate the corresponding concept in one of three concept schemes
        concept = dsd_concepts.get(concept_id)

        if concept_id == "VARIABLE":
            d: m.DimensionComponent = MeasureDimension(
                id="VARIABLE",
                # NB these are not attributes of Component; store as a Concept
                # name="Variable",
                # description="Reference to a concept from CL_TRANSPORT_MEASURES.",
                local_representation=m.Representation(
                    enumerated=sm.concept_scheme["TRANSPORT_MEASURE"]
                ),
            )
        elif concept is None:
            raise KeyError(concept_id)
        else:
            # Create the dimension, referring to the concept
            d = m.Dimension(id=concept_id, concept_identity=concept, order=order)

            try:
                # The dimension is represented by the corresponding code list, if any
                d.local_representation = m.Representation(
                    enumerated=sm.codelist[f"CL_{concept_id}"]
                )
            except KeyError:
                pass  # No iTEM codelist for this concept

        # Append this dimension
        dsd.dimensions.append(d)

    # Add a primary measure: either one with ID matching the DSD, or OBS_VALUE as backup
    concept = dsd_concepts.get(dsd.id) or dsd_concepts.get("OBS_VALUE")
    assert concept is not None

    dsd.measures.append(PrimaryMeasure(id=concept.id, concept_identity=concept))

    # Assign order to the dimensions
    dsd.dimensions.assign_order()


def cr_from(
    info: dict, dsd: "sdmx.model.common.BaseDataStructureDefinition"
) -> m.CubeRegion:
    """Create a :class:`.CubeRegion` from a simple :class:`dict` of `info`."""
    cr = m.CubeRegion(included=info.pop("included", True))
    for dim_id, values in info.items():
        dim = cast(m.Dimension, dsd.dimensions.get(dim_id))

        values = values.split()
        if values[0] == "!":
            included = False
            values.pop(0)
        else:
            included = True

        cr.member[dim] = MemberSelection(
            included=included,
            values_for=dim,
            values=[MemberValue(value=value) for value in values],
        )

    return cr


def cr_from_anno(
    obj: "sdmx.model.v21.ContentConstraint",
    dsd: "sdmx.model.common.BaseDataStructureDefinition",
) -> None:
    """Convert an annotation on `obj` into a :class:`.CubeRegion` constraint."""
    all_info = _pop_anno(obj, "_data_content_region")

    if all_info is None:
        return

    for info in all_info:
        obj.data_content_region.append(cr_from(info, dsd))


def dks_from_anno(
    obj: "sdmx.model.v21.ContentConstraint",
    dsd: "sdmx.model.common.BaseDataStructureDefinition",
) -> None:
    """Convert an annotation on `obj` into a :class:`.DataKeySet` constraint."""
    info = _pop_anno(obj, "_data_content_keys")
    if info is None:
        return

    dks = DataKeySet(included=True, keys=[])
    for dim_id, values in info.items():
        dim = dsd.dimensions.get(dim_id)

        for value in values:
            dks.keys.append(
                DataKey(
                    key_value={dim: m.ComponentValue(value_for=dim, value=value)},
                    included=True,
                )
            )

    obj.data_content_keys = dks


def merge_general_constraints(
    cc: "sdmx.model.v21.ContentConstraint",
    dsd: "sdmx.model.common.BaseDataStructureDefinition",
    sm: msg.StructureMessage,
) -> None:
    """Merge general constraints from `sm` into `cc` if relevant to `dsd`."""
    for other_cc in filter(
        lambda obj: obj.id.startswith("GENERAL"), sm.constraint.values()
    ):
        for i, info in enumerate(_get_anno(other_cc, "_data_content_region")):
            if not (set(info.keys()) - {"included"}) < set(
                dim.id for dim in dsd.dimensions
            ):
                continue

            # log.debug(
            #     f"Extend {repr(cc)} using {repr(other_cc)}.data_content_region[{i}]"
            # )
            cc.data_content_region.append(cr_from(info, dsd))
