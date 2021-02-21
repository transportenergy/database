from collections import ChainMap
from datetime import datetime
from functools import lru_cache

import sdmx.message as msg
import sdmx.model as m
from sdmx import Client
from sdmx.model import Annotation, Code, Concept, ConceptScheme, DataStructureDefinition

#: Current version of all data structures.
#:
#: .. todo:: Allow a different version for each particular structure, e.g. code list.
VERSION = "0.1"


def _dims(text):
    """Generate an annotation with dimensions."""
    return dict(annotations=[Annotation(id="_dimensions", text=text)])


def _units(mapping):
    """Generate an annotation with preferred units."""
    return dict(annotations=[Annotation(id="preferred_unit", text=repr(mapping))])


def update_object(obj, properties):
    for name, value in properties.items():
        setattr(obj, name, value)


@lru_cache()
def get_cdc():
    """Retrieve the ``CROSS_DOMAIN_CONCEPTS`` from the SDMX Global Registry."""
    id = "CROSS_DOMAIN_CONCEPTS"
    msg = Client("SGR").conceptscheme(id)
    return msg.concept_scheme[id]


@lru_cache()
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

    for cs in CONCEPT_SCHEMES:
        update_object(cs, ma_args)
        cs.extend(CONCEPTS[cs.id])
        sm.concept_scheme[cs.id] = cs

    for id, codes in CODELISTS.items():
        cl = m.Codelist(id=f"CL_{id}", **ma_args)
        # Add each code and any children
        # TODO Move this upstream
        for c in codes:
            cl.append(c)
            cl.extend(c.child)

        sm.codelist[cl.id] = cl

    # Retrieve the CROSS_DOMAIN_CONCEPTS scheme from the SDMX Global Registry
    cdc = get_cdc()

    # Concepts for each dimension of each DSD
    dsd_concepts = ChainMap(
        sm.concept_scheme["TRANSPORT"],
        sm.concept_scheme["MODELING"],
        cdc,
    )

    for dsd in DATA_STRUCTURES:
        # Set the maintainer etc.
        update_object(dsd, ma_args)

        # Pop an annotation and use it to produce a list of dimension IDs (see below)
        dims_annotation = dsd.annotations.pop(-1)
        assert "_dimensions" == dims_annotation.id
        dims = dims_annotation.text.localized_default().split()

        # Add dimensions to the data structure
        for order, concept_id in enumerate(dims):
            # Locate the corresponding concept in one of three concept schemes
            concept = dsd_concepts.get(concept_id)

            if concept_id == "VARIABLE":
                d = m.MeasureDimension(
                    id="VARIABLE",
                    name="Measure",
                    description="Reference to a concept from CL_TRANSPORT_MEASURES.",
                    local_representation=m.Representation(
                        enumerated=sm.concept_scheme["TRANSPORT_MEASURE"]
                    ),
                )
            elif concept is None:
                raise KeyError(concept_id)
            else:
                # Create the dimension, referring to the concept
                d = m.Dimension(
                    id=concept_id,
                    name=concept.name,
                    concept_identity=concept,
                    order=order,
                )

                try:
                    # The dimension is represented by the corresponding code list, if
                    # any
                    d.local_representation = m.Representation(
                        enumerated=sm.codelist[f"CL_{concept_id}"]
                    )
                except KeyError:
                    pass  # No iTEM codelist for this concept

            # Append this dimension
            dsd.dimensions.append(d)

        # Add the DSD to the StructureMessage
        sm.structure[dsd.id] = dsd

    return sm


CONCEPTS = {
    #: Concepts for the ``iTEM:TRANSPORT`` concept scheme.
    "TRANSPORT": (
        # Used as dimensions
        Concept(
            id="SERVICE",
            name="Service",
            description=(
                "Type of transport service e.g. transport of passengers or of freight."
            ),
        ),
        Concept(id="MODE", name="Mode or medium of transport"),
        Concept(
            id="VEHICLE", name="Vehicle type", description="Type of transport vehicle"
        ),
        Concept(id="FUEL", name="Fuel or energy carrier for transport"),
        Concept(
            id="TECHNOLOGY",
            name="Powertrain technology",
            description=(
                "Energy conversion technology used to power a motorized vehicle"
            ),
        ),
        Concept(
            id="AUTOMATION",
            name="Degree of automation in operation of transport vehicles",
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
    ),
    "MODELING": (
        Concept(
            id="MODEL",
            name="Model",
            description="Name or other identifier of a model used to generate data.",
        ),
        Concept(
            id="SCENARIO",
            name="Scenario",
            description=(
                "Name or other identifier of a specific configuration of a model."
            ),
        ),
    ),
    "TRANSPORT_MEASURE": (
        Concept(
            id="ACTIVITY",
            name="Transport activity",
            description=(
                "Amount of travel or transport by a person, vehicle, or collection of "
                "these."
            ),
            **_units(
                {
                    "SERVICE == passenger": "10⁹ passenger-km / yr",
                    "SERVICE == freight": "10⁹ tonne-km / yr",
                    # TODO distinguish "10⁹ vehicle-km / yr"
                }
            ),
        ),
        Concept(id="ENERGY", name="Energy", **_units("PJ / yr")),
        Concept(
            id="ENERGY_INTENSITY",
            name="Energy intensity of activity",
            **_units("MJ / vehicle-km"),
        ),
        Concept(
            id="EMISSION",
            name="Emission",
            description="Mass of a pollutant emitted.",
            **_units(
                {
                    "POLLUTANT == CO2": "10⁶ t CO₂ / yr",
                    "POLLUTANT == GHG": "10⁶ t CO₂e / yr",
                    "POLLUTANT == BC": "1O³ t BC / yr",
                    "POLLUTANT == PM25": "1O³ t PM2.5 / yr",
                }
            ),
        ),
        Concept(
            id="GDP", name="Gross Domestic Product", **_units("10⁹ USD(2005) / year")
        ),
        Concept(
            id="LOAD_FACTOR",
            name="Load factor",
            description="Amount of activity provided per vehicle",
            **_units(
                {
                    "SERVICE == PASSENGER": "passenger / vehicle",
                    "SERVICE == FREIGHT": "tonne / vehicle",
                }
            ),
        ),
        Concept(
            id="POPULATION",
            name="Population",
            description="i.e. of people.",
            **_units("10⁶ persons"),
        ),
        Concept(
            id="PRICE",
            name="Price",
            description="Market or fixed price for commodity.",
            **_units(
                {
                    "POLLUTANT == CO2": "USD(2005) / t CO₂",
                    "POLLUTANT == GHG": "USD(2005) / t CO₂e",
                    "FUEL == GASOLINE": "USD(2005) / litre",
                    "FUEL == DIESEL": "USD(2005) / litre",
                    "FUEL == NG": "USD(2005) / litre",
                    "FUEL == ELECTRICITY": "USD(2005) / kW-h",
                }
            ),
        ),
        Concept(
            id="SALES",
            name="Sales",
            description="New sales of vehicles in a period.",
            **_units("10⁶ vehicle / yr"),
        ),
        Concept(
            id="STOCK",
            name="Stock",
            description="Quantity of transport vehicles.",
            **_units("10⁶ vehicle"),
        ),
    ),
}

#: Concept schemes.
CONCEPT_SCHEMES = [
    ConceptScheme(
        id="TRANSPORT",
        description="Concepts used as dimensions or attributes for transport data.",
    ),
    ConceptScheme(
        id="MODELING",
        description="Concepts related to model-based research & assessment.",
    ),
    ConceptScheme(
        id="TRANSPORT_MEASURE",
        description="Concepts used as measures in transport data.",
    ),
]

CL_AUTOMATION = (
    Code(id="_Z", name="Not applicable"),
    Code(id="HUMAN", name="Human", description="Vehicle operated by a human driver."),
    Code(
        id="AV", name="Automated", description="Fully-automated (self-driving) vehicle."
    ),
)

CL_FLEET = (
    Code(id="_Z", name="Not applicable"),
    Code(id="ALL", description="All vehicles in use in the reporting period."),
    Code(id="NEW", description="Only newly-sold vehicles in the reporting period."),
    Code(
        id="USED",
        description=(
            "Only used vehicles that were not manufactured in the reporting period."
        ),
    ),
)

CL_FUEL = (
    Code(id="_Z", name="Not applicable"),
    Code(id="ALL", description="All fuels."),
    Code(
        id="LIQUID",
        name="All liquid",
        child=[
            Code(id="DIESEL"),
            Code(id="GASOLINE"),
            Code(id="BIOFUEL", name="Liquid biofuel"),
            Code(id="SYNTHETIC", description="a.k.a. synfuels, electrofuels."),
        ],
    ),
    Code(id="NG", name="Natural gas"),
    Code(id="HYDROGEN"),
    Code(id="ELECTRICITY"),
)

CL_LCA_SCOPE = (
    Code(id="_Z", name="Not applicable"),
    Code(id="TTW", name="Tank-to-wheels"),
    Code(id="WTT", name="Well-to-tank"),
    Code(id="WTW", name="Well-to-wheels"),
)

CL_MODE = (
    Code(id="_Z", name="Not applicable"),
    Code(id="ALL", name="All", description="All transport modes."),
    Code(id="AIR", name="Aviation"),
    Code(id="LAND", name="Land transport"),
    Code(id="ROAD", name="Road"),
    Code(id="RAIL", name="Rail"),
    Code(id="WATER", name="Water"),
)

CL_OPERATOR = (
    Code(id="_Z", name="Not applicable"),
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

CL_POLLUTANT = (
    Code(id="_Z", name="Not applicable"),
    Code(
        id="GHG",
        name="GHG",
        description=(
            "Greenhouse gases. Where used for totals, all GHGs are conveted to an "
            "equivalence basis."
        ),
        child=[
            Code(id="CO2", name="CO₂", description="Carbon dioxide."),
        ],
    ),
    Code(
        id="AQ",
        description="Air quality-related pollutant species.",
        child=[
            Code(id="BC", name="BC", description="Black carbon."),
            Code(
                id="NOX",
                name="NOx",
                description=(
                    "Air quality-related nitrogen oxides, i.e. NO, NO₂, and N₂O."
                ),
            ),
            Code(
                id="PM25",
                name="PM2.5",
                description="Particulate matter smaller than 2.5 μm.",
            ),
            Code(id="SO2", name="SO₂", description="Sulfur dioxide."),
        ],
    ),
)

CL_SERVICE = (
    Code(id="_Z", name="Not applicable"),
    Code(id="P", name="Passenger"),
    Code(id="F", name="Freight"),
)

CL_VEHICLE = (
    Code(id="_Z", name="Not applicable"),
    Code(id="ALL", description="All vehicle types."),
    Code(
        id="LDV",
        description="Light-duty road vehicle, including cars, SUVs, and light trucks.",
    ),
    Code(id="BUS"),
    Code(id="TRUCK"),
    Code(id="2W+3W", description="Two- and three-wheeled road vehicles."),
)


#: Codes for various code lists.
CODELISTS = {
    "AUTOMATION": CL_AUTOMATION,
    "FLEET": CL_FLEET,
    "FUEL": CL_FUEL,
    "LCA_SCOPE": CL_LCA_SCOPE,
    "MODE": CL_MODE,
    "OPERATOR": CL_OPERATOR,
    "POLLUTANT": CL_POLLUTANT,
    "SERVICE": CL_SERVICE,
    "VEHICLE": CL_VEHICLE,
}

#: Main iTEM data structures.
DATA_STRUCTURES = (
    DataStructureDefinition(
        id="HISTORICAL",
        description=(
            "Structure of the 'unified' iTEM historical transport data.\n\n"
            "This DSD has all possible dimensions, regardless of whether a particular "
            "measure (represented in the 'VARIABLE' dimension) is relevant for that "
            "measure. In the future, multiple data flows will be specified, each with a"
            "distinct structure that reflects the dimensions that are valid for the "
            "relevant measure(s)."
        ),
        **_dims(
            "VARIABLE SERVICE MODE VEHICLE FUEL TECHNOLOGY AUTOMATION OPERATOR "
            "POLLUTANT LCA_SCOPE FLEET REF_AREA TIME_PERIOD"
        ),
    ),
    DataStructureDefinition(
        id="MODEL",
        description=(
            "Structure of for iTEM model intercomparison data.\n\n"
            "This DSD has all possible dimensions, regardless of whether a particular "
            "measure (represented in the 'VARIABLE' dimension) is relevant for that "
            "measure. In the future, multiple data flows will be specified, each with a"
            "distinct structure that reflects the dimensions that are valid for the "
            "relevant measure(s)."
        ),
        **_dims(
            "MODEL SCENARIO VARIABLE SERVICE MODE VEHICLE FUEL TECHNOLOGY AUTOMATION "
            "OPERATOR POLLUTANT LCA_SCOPE FLEET REF_AREA TIME_PERIOD"
        ),
    ),
)
