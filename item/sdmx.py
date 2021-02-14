from datetime import datetime

import sdmx.model as m
import sdmx.message as msg
from sdmx.model import Code, Concept

#: Current version of all data structures.
#:
#: .. todo: Allow a different version for each particular structure, e.g. code list.
VERSION = "0.1"


def generate() -> msg.StructureMessage:
    """Return the SDMX data structures for iTEM data."""
    sm = msg.StructureMessage(prepared=datetime.now())

    item = m.Agency(
        id="iTEM",
        name="International Transport Energy Modeling",
        contact=[
            m.Contact(
                name="iTEM organizing group",
                email=["mail@transportenergy.org"],
                uri=["https://transportenergy.org"],
            )
        ],
    )

    ma_args = dict(
        maintainer=item,
        version=VERSION,
        is_external_reference=False,
    )

    as_ = m.AgencyScheme(id="iTEM", **ma_args)
    as_.append(item)
    sm.organisation_scheme[as_.id] = as_
    sm.header = msg.Header(sender=item)

    cs0 = m.ConceptScheme(
        id="TRANSPORT",
        **ma_args,
        description="Concepts used as dimensions or attributes for transport data.",
    )
    cs0.extend(CS_TRANSPORT)
    sm.concept_scheme[cs0.id] = cs0

    cs1 = m.ConceptScheme(
        id="TRANSPORT_MEASURES",
        **ma_args,
        description="Concepts used as measures in transport data.",
    )
    cs1.extend(CS_TRANSPORT_MEASURES)
    sm.concept_scheme[cs1.id] = cs1

    for id, codes in CODELISTS.items():
        cl = m.Codelist(id=f"CL_{id}", **ma_args)
        cl.extend(codes)
        sm.codelist[cl.id] = cl

    dsd0 = m.DataStructureDefinition(
        id="HISTORICAL",
        **ma_args,
        description=(
            "Structure of the 'unified' iTEM historical transport data. This DSD has "
            "all possible dimensions, regardless of whether a particular measure "
            "(represented in the 'VARIABLE' dimension) is relevant for that measure. "
            "In the future, the historical data will be provided via multiple data "
            "flows, each with a distinct structure that reflects the dimensions that "
            "are valid for the relevant measure(s)."
        ),
    )
    for order, concept_id in enumerate(
        (
            "TYPE MODE VEHICLE FUEL TECHNOLOGY AUTOMATION OPERATOR POLLUTANT LCA_SCOPE "
            "FLEET"
        ).split()
    ):
        d = m.Dimension(
            id=concept_id,
            name=cs0[concept_id].name,
            concept_identity=cs0[concept_id],
            order=order,
        )
        try:
            d.local_representation = m.Representation(
                enumerated=sm.codelist[f"CL_{concept_id}"]
            )
        except KeyError:
            # No codelist for this concept
            pass
        dsd0.dimensions.append(d)

    # Also add the measure dimension
    dsd0.dimensions.append(
        m.MeasureDimension(
            id="VARIABLE",
            name="Measure",
            description="Reference to a concept from CL_TRANSPORT_MEASURES.",
        )
    )

    sm.structure[dsd0.id] = dsd0

    return sm


#: Concepts for the ``iTEM:TRANSPORT`` concept scheme.
CS_TRANSPORT = (
    # Used as dimensions
    Concept(id="TYPE", name="Objects being transported, e.g. passengers or freight"),
    Concept(id="MODE", name="Mode or medium of transport"),
    Concept(id="VEHICLE", name="Type of transport vehicle"),
    Concept(id="FUEL", name="Fuel or energy carrier for transport"),
    Concept(
        id="TECHNOLOGY",
        name="Powertrain technology",
        description="Energy conversion technology used to power a motorized vehicle",
    ),
    Concept(
        id="AUTOMATION", name="Degree of automation in operation of transport vehicles"
    ),
    Concept(id="OPERATOR", name="Entity operating a transport vehicle"),
    Concept(id="POLLUTANT", name="Species of environmental pollutant"),
    Concept(
        id="LCA_SCOPE",
        name="LCA scope",
        description="Scope of analysis covered by a transport life-cycle measure",
    ),
    Concept(
        id="FLEET",
        description="Part of a fleet of transport vehicles, e.g. new versus used.",
    ),
)

#: Concepts for the ``iTEM:TRANSPORT_MEASURES`` concept scheme.
CS_TRANSPORT_MEASURES = (
    Concept(
        id="ACTIVITY",
        name="Transport activity",
        description=(
            "Amount of travel or transport by a person, vehicle, or collection of "
            "these."
        ),
    ),
    Concept(id="ENERGY", name="Energy"),
    Concept(id="ENERGY_INTENSITY", name="Energy intensity of activity"),
    Concept(id="EMISSION", name="Emission", description="Mass of a pollutant emitted."),
    Concept(id="GDP", name="Gross Domestic Product"),
    Concept(
        id="LOAD_FACTOR",
        name="Load factor",
        description="Amount of activity provided per vehicle",
    ),
    Concept(id="POPULATION", name="Population", description="i.e. of people."),
    Concept(
        id="PRICE", name="Price", description="Market or fixed price for commodity."
    ),
    Concept(id="SALES", name="Sales", description="New sales of vehicles in a period."),
    Concept(id="STOCK", name="Stock", description="Quantity of transport vehicles."),
)

CL_LCA_SCOPE = (
    Code(id="TTW", name="Tank-to-wheels"),
    Code(id="WTT", name="Well-to-tank"),
    Code(id="WTW", name="Well-to-wheels"),
)

CL_MODE = (
    Code(id="ALL", name="All", description="All transport modes."),
    Code(id="AIR", name="Aviation"),
    Code(id="LAND", name="Land transport"),
    Code(id="ROAD", name="Road"),
    Code(id="RAIL", name="Rail"),
    Code(id="WATER", name="Water"),
)

CL_OPERATOR = (
    Code(
        id="OWN",
        name="Own-supplied",
        description=(
            "Transport by a vehicle owned and operated for private use by a household "
            "or individual."
        ),
    ),
    Code(
        id="HIRE",
        name="Hired",
        description=(
            "Transport by a vehicle (and driver) hired through a firm or commercial "
            "service."
        ),
    ),
)

CL_TYPE = (
    Code(id="P", name="Passenger"),
    Code(id="F", name="Freight"),
)

#: Codes for various code lists.
CODELISTS = {
    "LCA_SCOPE": CL_LCA_SCOPE,
    "MODE": CL_MODE,
    "OPERATOR": CL_OPERATOR,
    "TYPE": CL_TYPE,
}
