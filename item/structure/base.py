from typing import Any, Dict, List

from sdmx.model.common import (
    Agency,
    AgencyScheme,
    Code,
    Concept,
    ConceptScheme,
    ConstraintRole,
    ConstraintRoleType,
    Contact,
)
from sdmx.model.v21 import Annotation, ContentConstraint, DataStructureDefinition

#: Current version of all data structures.
#:
#: .. todo:: Allow a different version for each particular structure, e.g. code list.
VERSION = "0.1"


def anno(**kwargs) -> Dict[Any, Any]:  # NB actually Dict[str, List[Annotation]]
    """Store `kwargs` as annotations on a :class:`AnnotableArtefact` for later use."""
    return dict(annotations=[Annotation(id=k, text=repr(v)) for k, v in kwargs.items()])


def exclude_z(dims: str) -> List[Dict]:
    """Return "_data_content_region" annotation content to exclude "_Z" codes.

    Parameters
    ----------
    dims :
        Space-separated list of dimensions on which to exclude "_Z" codes.
    """
    return [{"included": False, dim: "_Z"} for dim in dims.split()]


def exclude(**kwargs):
    """Return a "_data_content_region" annotation content to exclude multiple codes."""
    return [{"included": False, k: v} for k, v in kwargs.items()]


AS_ITEM = AgencyScheme(id="iTEM")
AS_ITEM.append(
    Agency(
        id="iTEM",
        name="International Transport Energy Modeling",
        contact=[
            Contact(
                name="iTEM organizing group",
                email=["mail@transportenergy.org"],
                uri=["https://transportenergy.org"],
            )
        ],
    )
)


CS_TRANSPORT = ConceptScheme(
    id="TRANSPORT",
    description="Concepts used as dimensions or attributes for transport data.",
)
CS_TRANSPORT.extend(
    [
        # Used as dimensions
        Concept(
            id="SERVICE",
            name="Service",
            description=(
                "Type of transport service e.g. transport of passengers or of freight."
            ),
        ),
        Concept(id="MODE", name="Mode", description="Mode or medium of transport."),
        Concept(
            id="VEHICLE", name="Vehicle type", description="Type of transport vehicle."
        ),
        Concept(
            id="FUEL", name="Fuel", description="Fuel or energy carrier for transport."
        ),
        Concept(
            id="TECHNOLOGY",
            name="Powertrain technology",
            description=(
                "Energy conversion technology used to power a motorized vehicle"
            ),
        ),
        Concept(
            id="AUTOMATION",
            name="Automation",
            description="Degree of automation in operation of transport vehicles.",
        ),
        Concept(
            id="OPERATOR",
            name="Operator",
            description="Entity operating a transport vehicle.",
        ),
        Concept(
            id="POLLUTANT",
            name="Species",
            description="Species of environmental pollutant.",
        ),
        Concept(
            id="LCA_SCOPE",
            name="LCA scope",
            description=(
                "Scope of analysis covered by a transport life-cycle (LC) measure."
            ),
        ),
        Concept(
            id="FLEET",
            name="Fleet",
            description=(
                "Portion of a fleet of transport vehicles, e.g. new versus used."
            ),
        ),
    ]
)

CS_MODELING = ConceptScheme(
    id="MODELING",
    description="Concepts related to model-based research & assessment.",
)
CS_MODELING.extend(
    [
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
    ]
)

CS_TRANSPORT_MEASURE = ConceptScheme(
    id="TRANSPORT_MEASURE",
    description="Concepts used as measures in transport data.",
)
CS_TRANSPORT_MEASURE.extend(
    [
        Concept(
            id="ACTIVITY",
            name="Transport activity",
            description=(
                "Amount of travel or transport by a person, vehicle, or collection of "
                "these."
            ),
            **anno(
                preferred_units={
                    "SERVICE == passenger": "10⁹ passenger-km / yr",
                    "SERVICE == freight": "10⁹ tonne-km / yr",
                    # TODO distinguish "10⁹ vehicle-km / yr"
                }
            ),
        ),
        Concept(id="ENERGY", name="Energy", **anno(preferred_units="PJ / yr")),
        Concept(
            id="ENERGY_INTENSITY",
            name="Energy intensity of activity",
            **anno(preferred_units="MJ / vehicle-km"),
        ),
        Concept(
            id="EMISSIONS",
            name="Emissions",
            description="Mass of a pollutant emitted.",
            **anno(
                preferred_units={
                    "POLLUTANT == CO2": "10⁶ t CO₂ / yr",
                    "POLLUTANT == GHG": "10⁶ t CO₂e / yr",
                    "POLLUTANT == BC": "10³ t BC / yr",
                    "POLLUTANT == PM25": "10³ t PM2.5 / yr",
                }
            ),
        ),
        Concept(
            id="GDP",
            name="Gross Domestic Product",
            **anno(preferred_units="10⁹ USD(2005) / year"),
        ),
        Concept(
            id="LOAD_FACTOR",
            name="Load factor",
            description="Amount of activity provided per vehicle",
            **anno(
                preferred_units={
                    "SERVICE == PASSENGER": "passenger / vehicle",
                    "SERVICE == FREIGHT": "tonne / vehicle",
                }
            ),
        ),
        Concept(
            id="POPULATION",
            name="Population",
            description="i.e. of people.",
            **anno(preferred_units="10⁶ persons"),
        ),
        Concept(
            id="PRICE",
            name="Price",
            description="Market or fixed price for commodity.",
            **anno(
                preferred_units={
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
            **anno(preferred_units="10⁶ vehicle / yr"),
        ),
        Concept(
            id="STOCK",
            name="Stock",
            description="Quantity of transport vehicles.",
            **anno(preferred_units="10⁶ vehicle"),
        ),
    ]
)

#: Concept schemes.
CONCEPT_SCHEMES = [CS_TRANSPORT, CS_MODELING, CS_TRANSPORT_MEASURE]

#: Codes for the REF_AREA dimension, from SDMX codelist ``ESTAT:CL_AREA(1.8)``.
CL_AREA = (
    Code(id="_X", name="Not allocated/unspecified"),
    Code(id="B0", name="European Union (current composition)"),
    Code(id="B4", name="European Union (27 countries)"),
    Code(id="B5", name="European Union (28 countries)"),
    Code(id="W0", name="World"),
)

CL_AUTOMATION = (
    Code(id="_T", name="Total"),
    Code(id="_Z", name="Not applicable"),
    Code(id="HUMAN", name="Human", description="Vehicle operated by a human driver."),
    Code(
        id="AV", name="Automated", description="Fully-automated (self-driving) vehicle."
    ),
)

CL_FLEET = (
    Code(
        id="_T",
        name="Total",
        description="All vehicles in use in the reporting period.",
    ),
    Code(id="_Z", name="Not applicable"),
    Code(id="NEW", description="Only newly-sold vehicles in the reporting period."),
    Code(
        id="USED",
        description=(
            "Only used vehicles that were not manufactured in the reporting period."
        ),
    ),
)

CL_FUEL = (
    Code(id="_T", name="Total", description="All fuels."),
    Code(id="_Z", name="Not applicable"),
    Code(
        id="LIQUID",
        name="All liquid",
        child=[
            Code(id="DIESEL"),
            Code(id="GASOLINE"),
            Code(
                id="BIOFUEL",
                name="Liquid biofuel",
                child=[
                    Code(id="BIODIESEL"),
                    Code(id="BIOETH", name="Bioethanol"),
                ],
            ),
            Code(id="SYNTHETIC", description="a.k.a. synfuels, electrofuels."),
        ],
    ),
    Code(
        id="GAS",
        name="Gas",
        description="All gaseous fuels",
        child=[
            Code(id="CNG", name="CNG", description="Compressed natural gas."),
            Code(id="LNG", name="LNG", description="Liquified natural gas."),
            Code(id="LPG", name="LPG", description="Liquified propane gas."),
        ],
    ),
    Code(id="H2", name="Hydrogen"),
    Code(id="ELEC", name="Electricity"),
)

CL_LCA_SCOPE = (
    Code(id="_Z", name="Not applicable"),
    Code(id="TTW", name="Tank-to-wheels"),
    Code(id="WTT", name="Well-to-tank"),
    Code(id="WTW", name="Well-to-wheels"),
)

CL_MODE = (
    Code(id="_T", name="Total", description="All transport modes."),
    Code(id="_Z", name="Not applicable"),
    Code(id="AIR", name="Aviation"),
    Code(
        id="LAND",
        name="All land transport modes.",
        child=[
            Code(id="RAIL", name="Rail"),
            Code(id="ROAD", name="Road", description="Motorized road transport."),
            Code(
                id="OFFROAD",
                name="Off-road",
                description="Motorized off-road transport.",
            ),
            Code(id="ACTIVE", name="Non-motorized"),
        ],
    ),
    Code(id="WATER", name="Water"),
    Code(id="PIPE", name="Pipeline"),
)

CL_OPERATOR = (
    Code(id="_T", name="Total"),
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
        child=[Code(id="CO2", name="CO₂", description="Carbon dioxide.")],
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
    Code(id="_T", name="Total"),
    Code(id="_Z", name="Not applicable"),
    Code(id="P", name="Passenger"),
    Code(id="F", name="Freight"),
)

CL_TECHNOLOGY = (
    Code(id="_T", name="Total", description="All technologies."),
    Code(id="_Z", name="Not applicable"),
    Code(
        id="IC",
        name="Combustion",
        description=(
            "Using only chemical fuels. Inclusive of powertrains that store energy as"
            "electricity, i.e. hybrids."
        ),
        child=[
            Code(id="HYBRID", description="Hybridized internal combustion."),
            Code(id="NONHYB", description="Non-hybridized internal combusion."),
        ],
    ),
    Code(
        id="ELEC",
        name="Electric",
        description="Powertrains that can be charged using electricity.",
        child=[
            Code(
                id="BEV",
                description="Battery-electric powertrain using no chemical fuels.",
            ),
            Code(
                id="PHEV",
                name="Plug-in hybrid-electric",
                description=(
                    "Powertrain that can use both chemical fuels and electricity."
                ),
                child=[
                    Code(
                        id="PHEV-D",
                        name="Diesel PHEV",
                        description="PHEV powertrain that uses diesel fuel.",
                    ),
                    Code(
                        id="PHEV-G",
                        name="Diesel PHEV",
                        description="PHEV powertrain that uses gasoline fuel.",
                    ),
                ],
            ),
        ],
    ),
    Code(
        id="FC",
        name="Fuel cell",
        description="Using electrochemical conversion of fuel to electricity.",
    ),
)

CL_VEHICLE = (
    Code(id="_T", name="Total", description="All vehicle types."),
    Code(id="_Z", name="Not applicable"),
    Code(
        id="LDV",
        name="Light-duty vehicle",
        description="Light-duty road vehicle, including cars, SUVs, and light trucks.",
    ),
    Code(id="BUS", name="Bus"),
    Code(id="TRUCK", name="Truck"),
    Code(id="2W+3W", description="Two- and three-wheeled road vehicles."),
)


#: Codes for various code lists.
CODELISTS = {
    "AUTOMATION": CL_AUTOMATION,
    "AREA": CL_AREA,
    "FLEET": CL_FLEET,
    "FUEL": CL_FUEL,
    "LCA_SCOPE": CL_LCA_SCOPE,
    "MODE": CL_MODE,
    "OPERATOR": CL_OPERATOR,
    "POLLUTANT": CL_POLLUTANT,
    "SERVICE": CL_SERVICE,
    "TECHNOLOGY": CL_TECHNOLOGY,
    "VEHICLE": CL_VEHICLE,
}


#: Main iTEM data structures.
DATA_STRUCTURES = (
    DataStructureDefinition(
        id="ACTIVITY",
        description="Activity in terms of quantity of service provided.",
        **anno(_dimensions="SERVICE MODE VEHICLE TECHNOLOGY AUTOMATION OPERATOR"),
    ),
    DataStructureDefinition(
        id="ACTIVITY_VEHICLE",
        description="Activity of transport vehicles.",
        **anno(_dimensions="SERVICE MODE VEHICLE TECHNOLOGY AUTOMATION OPERATOR"),
    ),
    DataStructureDefinition(
        id="EMISSIONS",
        **anno(_dimensions="SERVICE MODE VEHICLE TECHNOLOGY FUEL POLLUTANT LCA_SCOPE"),
    ),
    DataStructureDefinition(
        id="ENERGY",
        description=(
            "Observations measure the total energy consumed by the vehicles per year "
            "during the TIME_PERIOD."
        ),
        **anno(_dimensions="SERVICE MODE VEHICLE TECHNOLOGY FLEET"),
    ),
    DataStructureDefinition(
        id="ENERGY_INTENSITY",
        **anno(_dimensions="SERVICE MODE VEHICLE TECHNOLOGY FLEET"),
    ),
    DataStructureDefinition(id="GDP"),
    DataStructureDefinition(id="POPULATION"),
    DataStructureDefinition(id="PRICE_FUEL", **anno(_dimensions="FUEL")),
    DataStructureDefinition(id="PRICE_POLLUTANT", **anno(_dimensions="POLLUTANT")),
    DataStructureDefinition(
        id="LOAD_FACTOR",
        description=(
            "The current version of this structure does not distinguish by powertrain "
            "technology. Implicitly TECHNOLOGY is 'ALL', so the observations measure "
            "the average load factor across all powertrain technologies."
        ),
        **anno(_dimensions="SERVICE MODE VEHICLE"),
    ),
    DataStructureDefinition(
        id="SALES",
        **anno(_dimensions="SERVICE MODE VEHICLE TECHNOLOGY FLEET"),
    ),
    DataStructureDefinition(
        id="STOCK",
        description=(
            "The current version of this structure does not distinguish by FLEET. "
            "Implicitly FLEET is 'ALL', so the observations measure the total of new "
            "and used vehicles."
        ),
        **anno(_dimensions="SERVICE MODE VEHICLE TECHNOLOGY"),
    ),
    DataStructureDefinition(
        id="HISTORICAL",
        description=(
            """Structure of the 'unified' iTEM historical transport data.

This DSD has all possible dimensions, regardless of whether a particular measure
(represented in the 'VARIABLE' dimension) is relevant for that measure. In the future,
multiple data flows will be specified, each with a distinct structure that reflects the
dimensions that are valid for the relevant measure(s)."""
        ),
        **anno(
            _dimensions=(
                "VARIABLE SERVICE MODE VEHICLE FUEL TECHNOLOGY AUTOMATION OPERATOR "
                "POLLUTANT LCA_SCOPE FLEET"
            )
        ),
    ),
    DataStructureDefinition(
        id="MODEL",
        description=(
            """Structure for iTEM model intercomparison data.

This DSD has all possible dimensions, regardless of whether a particular measure
(represented in the 'VARIABLE' dimension) is relevant for that measure. In the future,
multiple data flows will be specified, each with a distinct structure that reflects the
dimensions that are valid for the relevant measure(s)."""
        ),
        **anno(
            _dimensions=(
                "MODEL SCENARIO VARIABLE SERVICE MODE VEHICLE FUEL TECHNOLOGY "
                "AUTOMATION OPERATOR POLLUTANT LCA_SCOPE FLEET"
            )
        ),
    ),
)

_allowable = ConstraintRole(role=ConstraintRoleType.allowable)


#: Constraints applying to DSDs.
CONSTRAINTS = (
    ContentConstraint(
        id="GENERAL0",
        description="Vehicle types are only relevant for road modes.",
        role=_allowable,
        **anno(
            _data_content_region=[dict(included=False, MODE="! ROAD", VEHICLE="! _T")],
        ),
    ),
    ContentConstraint(
        id="GENERAL1",
        description="Vehicle types for freight or passenger service only.",
        role=_allowable,
        **anno(
            _data_content_region=[
                dict(included=False, SERVICE="P", VEHICLE="TRUCK"),
                dict(included=False, SERVICE="F", VEHICLE="LDV BUS 2W+3W"),
            ]
        ),
    ),
    ContentConstraint(
        id="GENERAL2",
        description=(
            "Air freight is (largely) provided as a byproduct of passenger service; "
            "most iTEM models do not include it separately"
        ),
        role=_allowable,
        **anno(_data_content_region=[dict(included=False, SERVICE="F", MODE="AIR")]),
    ),
    ContentConstraint(
        id="GENERAL3",
        description=(
            "Assume hybrid-electric and fuel cell powertrain technologies not used for "
            "air, rail, water, or small road vehicles."
        ),
        role=_allowable,
        **anno(
            _data_content_region=[
                dict(included=False, MODE="AIR RAIL WATER", TECHNOLOGY="HYBRID FC"),
                dict(included=False, VEHICLE="2W+3W", TECHNOLOGY="HYBRID FC"),
            ]
        ),
    ),
    ContentConstraint(
        id="GENERAL4",
        name="Technology/fuel constraints",
        description=(
            """- Combustion powertrains do not take electricity as an input.
- Fuel cell powertrains take only hydrogen as an input.
- Hydrogen is only used in fuel cell powertrains.
- Electric powertrains take only electricity as an input.
"""
        ),
        role=_allowable,
        **anno(
            _data_content_region=[
                dict(included=False, TECHNOLOGY="COMBUSTION", FUEL="ELEC"),
                dict(included=False, TECHNOLOGY="FC", FUEL="! H2"),
                dict(included=False, TECHNOLOGY="! FC", FUEL="H2"),
                dict(included=False, TECHNOLOGY="ELECTRIC", FUEL="! ELEC"),
            ]
        ),
    ),
    ContentConstraint(
        id="GENERAL5",
        description="Shared and automated vehicles only relevant for LDVs.",
        role=_allowable,
        **anno(
            _data_content_region=[
                dict(included=False, VEHICLE="! LDV", AUTOMATION="AV"),
                dict(included=False, VEHICLE="2W+3W", OPERATOR="HIRE"),
                dict(included=False, VEHICLE="LDV 2W+3W", OPERATOR="OWN"),
            ]
        ),
    ),
    ContentConstraint(
        id="GENERAL6",
        description="Don't require reporting the sum of road + rail.",
        role=_allowable,
        **anno(_data_content_region=exclude(MODE="LAND OFFROAD ACTIVE")),
    ),
    ContentConstraint(
        id="ACTIVITY",
        description="Omit sums by technology across modes.",
        role=_allowable,
        **anno(
            _data_content_region=[dict(included=False, MODE="_T", TECHNOLOGY="! _T")]
            + exclude_z("AUTOMATION MODE OPERATOR SERVICE TECHNOLOGY VEHICLE")
        ),
    ),
    ContentConstraint(
        id="ACTIVITY_VEHICLE",
        description="Omit sums by technology across modes.",
        role=_allowable,
        **anno(
            _data_content_region=[dict(included=False, MODE="_T", TECHNOLOGY="! _T")]
            + exclude_z("AUTOMATION MODE OPERATOR SERVICE TECHNOLOGY VEHICLE")
        ),
    ),
    ContentConstraint(
        id="EMISSIONS",
        description=(
            """- No use-phase emissions from electricity.
- No total across air quality species; _Z invalid.
- No use-phase emissions from electricity.
- Not concerned with e.g. HFC emissions from refrigerants, or CH₄ emissions at service
  stations. These are typically assigned to non-transport sectors even in models that
  include them.
- Only use-phase emissions of air quality pollutants.
         """
        ),
        role=_allowable,
        **anno(
            _data_content_region=[
                dict(included=False, FUEL="ELEC", LCA_SCOPE="TTW"),
                dict(included=False, POLLUTANT="_Z AQ"),
                dict(included=False, LCA_SCOPE="TTW", FUEL="ELEC"),
                dict(included=False, LCA_SCOPE="WTW", TECHNOLOGY="! _T"),
                dict(included=False, POLLUTANT="BC NOX PM25 SO2", LCA_SCOPE="! TTW"),
            ]
            + exclude_z("FUEL MODE SERVICE TECHNOLOGY VEHICLE")
        ),
    ),
    ContentConstraint(
        id="ENERGY",
        role=_allowable,
        **anno(_data_content_region=exclude_z("MODE SERVICE TECHNOLOGY VEHICLE")),
    ),
    ContentConstraint(
        id="ENERGY_INTENSITY",
        description=(
            "The current item:ENERGY_INTENSITY data structure excludes the intensity of"
            " transport service provided with used vehicles. This quantity can be "
            "computed from the intensities for the entire FLEET and for new vehicles "
            "only."
        ),
        role=_allowable,
        **anno(
            _data_content_region=[dict(FLEET="_T NEW")]
            + exclude(SERVICE="_T _Z")
            + exclude_z("MODE TECHNOLOGY")
        ),
    ),
    ContentConstraint(
        id="LOAD_FACTOR",
        role=_allowable,
        **anno(_data_content_region=exclude_z("MODE SERVICE VEHICLE")),
    ),
    ContentConstraint(
        id="PRICE_FUEL",
        role=_allowable,
        **anno(_data_content_region=[dict(FUEL="GASOLINE DIESEL ELEC")]),
    ),
    ContentConstraint(
        id="PRICE_POLLUTANT",
        role=_allowable,
        **anno(_data_content_region=[dict(POLLUTANT="GHG")]),
    ),
    ContentConstraint(
        id="SALES",
        description=(
            "The current iTEM:SALES data structure is only specified for new road "
            " transport vehicles. It excludes e.g. sales of aircraft or ships; and "
            "(re)sale of used road vehicles."
        ),
        role=_allowable,
        **anno(
            _data_content_region=[dict(FLEET="NEW", MODE="ROAD")]
            + exclude(SERVICE="_T _Z")
            + exclude_z("TECHNOLOGY VEHICLE")
        ),
    ),
    ContentConstraint(
        id="STOCK",
        description=(
            "The current iTEM:STOCK data structure is only specified for road transport"
            " vehicles. It excludes e.g. stock of aircraft or ships."
        ),
        role=_allowable,
        **anno(
            _data_content_region=[dict(MODE="ROAD")]
            + exclude(SERVICE="_T _Z")
            + exclude_z("TECHNOLOGY VEHICLE")
        ),
    ),
)
