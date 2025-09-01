"""Structural metadata for iTEM model data flows.

These functions each return an SDMX codelist with an ID like ``CL_FOO`` corresponding to
the concept/dimension ``FOO``. The code lists were previously stored in/processed from
YAML files in a custom format, stored in the ``transportenergy/metadata`` repository.
"""

from functools import cache

from sdmx.model import common, v21


def get_cl_fuel() -> "common.Codelist":
    cl: "common.Codelist" = common.Codelist(id="CL_FUEL")

    cl.setdefault(id="All")
    cl.setdefault(id="Coal")
    cl.setdefault(id="Electricity")
    cl.setdefault(id="Hydrogen")
    cl.setdefault(id="Liquids")
    cl.setdefault(id="Liquids/Electricity")
    cl.setdefault(id="Natural gas")

    return cl


def get_cl_mode() -> "common.Codelist":
    cl: "common.Codelist" = common.Codelist(id="CL_MODE")

    F = v21.Annotation(id="SERVICE", text="freight")
    P = v21.Annotation(id="SERVICE", text="passenger")

    def _T(expr: str) -> "v21.Annotation":
        return v21.Annotation(
            id="TECHNOLOGY", text=repr(tuple(sorted(["All"] + expr.split("|"))))
        )

    cl.setdefault(id="All", name="All modes", description="All modes")
    cl.setdefault(
        id="2W",
        description="Two-wheeled vehicles (motorcycles, scooters, e-bikes, etc.)",
        annotations=[P, _T("BEV|CNG|FCEV|Liquids|Liquids PHEV")],
    )
    cl.setdefault(
        id="3W",
        description="Three-wheeled vehicles (rickshaws, etc.)",
        annotations=[P, _T("BEV|CNG|FCEV|Liquids|Liquids PHEV")],
    )
    cl.setdefault(id="Aviation", annotations=[P, _T("Hydrogen|Liquids")])
    cl.setdefault(id="Bus", annotations=[P, _T("BEV|CNG|FCEV|Liquids|Liquids PHEV")])
    cl.setdefault(id="Domestic Shipping", annotations=[F, _T("Liquids")])
    cl.setdefault(id="Freight Rail", annotations=[F, _T("Coal|Electric|Liquids")])
    cl.setdefault(
        id="Freight Rail and Air and Ship",
        description="Residual category for any models that do not represent these three modes explicitly",
        annotations=[F, _T("Coal|Electric|Hydrogen|Liquids|Natural gas")],
    )
    cl.setdefault(
        id="HDT",
        description="Heavy-duty freight trucks",
        annotations=[F, _T("BEV|CNG|Electric|FCEV|Liquids|Liquids PHEV")],
    )
    cl.setdefault(
        id="International Shipping",
        annotations=[F, _T("Hydrogen|Liquids|Natural gas")],
    )
    cl.setdefault(
        id="LDV",
        description="Light-duty passenger cars and trucks/SUVs/vans",
        annotations=[P, _T("BEV|CNG|FCEV|Liquids|Liquids PHEV")],
    )
    cl.setdefault(id="Passenger Rail", annotations=[P, _T("Coal|Electric|Liquids")])

    return cl


def get_cl_measure() -> "common.Codelist":
    cl: "common.Codelist" = common.Codelist(id="CL_MEASURE")

    # Shorthand
    g = v21.Annotation(id="is-global", text=repr(True))
    p = v21.Annotation(id="SERVICE", text="passenger")
    f = v21.Annotation(id="SERVICE", text="freight")

    def u(text: str) -> "v21.Annotation":
        return v21.Annotation(id="UNIT_MEASURE", text=text)

    cl.setdefault(
        id="Population",
        description="human population",
        annotations=[g, u("10⁶ persons")],
    )
    cl.setdefault(
        id="PPP-GDP",
        description="gross domestic product in terms of purchasing power parity (PPP)",
        annotations=[g, u("10⁹ 2005 USD / year")],
    )
    cl.setdefault(
        id="Carbon Price",
        description="for models that use a carbon price to incentivize carbon reductions across sectors",
        annotations=[g, u("2005 USD / t CO₂-eq")],
    )
    cl.setdefault(
        id="CO2 Emissions (all sectors)",
        description="variable that is only relevant for multi-sector models (i.e., the IAMs that represent transport and everything else)",
        annotations=[g, u("Mt CO₂ / year")],
    )
    cl.setdefault(
        id="GHG Emissions (all sectors)",
        description="variable that is only relevant for multi-sector models (i.e., the IAMs that represent transport and everything else)",
        annotations=[g, u("Mt CO₂-eq / year")],
    )
    cl.setdefault(
        id="CO2 Concentration",
        description="variable that is only relevant for multi-sector models that are coupled with a climate model (i.e., the IAMs)",
        annotations=[g, u("ppm")],
    )
    cl.setdefault(
        id="CO2eq Concentration (incl. all forcing agents)",
        description="variable that is only relevant for multi-sector models that are coupled with a climate model (i.e., the IAMs)",
        annotations=[g, u("ppm")],
    )
    cl.setdefault(
        id="Radiative Forcing",
        description="variable that is only relevant for multi-sector models that are coupled with a climate model (i.e., the IAMs)",
        annotations=[g, u("W / m²")],
    )
    cl.setdefault(
        id="ef_bc",
        description="emissions factor for black carbon (in terms of energy units)",
        annotations=[u("g / MJ")],
    )
    cl.setdefault(
        id="ef_co2 (service)",
        description="emissions factor for carbon dioxide (in terms of service demand units)",
        annotations=[p, u("g / passenger-km")],
    )
    cl.setdefault(
        id="ef_co2 (service)",
        description="emissions factor for carbon dioxide (in terms of service demand units)",
        annotations=[f, u("g / tonne-km")],
    )
    cl.setdefault(
        id="ef_co2",
        description="emissions factor for carbon dioxide (in terms of vehicle use units)",
        annotations=[u("g / vehicle-km")],
    )
    cl.setdefault(
        id="energy",
        description="energy use at the final energy (end-use transport sub-sector) level",
        annotations=[u("PJ / year")],
    )
    cl.setdefault(
        id="intensity_new",
        description="energy intensity (efficiency) of new vehicle technologies (in vehicle use units)",
        annotations=[u("MJ / vehicle-km")],
    )
    cl.setdefault(
        id="intensity_service",
        description="energy intensity (efficiency) of existing stock of vehicle technologies (in terms of service demand units)",
        annotations=[p, u("MJ / passenger-km")],
    )
    cl.setdefault(
        id="intensity_service",
        description="energy intensity (efficiency) of existing stock of vehicle technologies (in terms of service demand units)",
        annotations=[f, u("MJ / tonne-km")],
    )
    cl.setdefault(
        id="intensity",
        description="energy intensity (efficiency) of existing stock of vehicle technologies (in terms of vehicle use units)",
        annotations=[u("MJ / vehicle-km")],
    )
    cl.setdefault(
        id="pkm",
        description="passenger-kilometers traveled",
        annotations=[p, u("10⁹ passenger-km / year")],
    )
    cl.setdefault(
        id="sales",
        description="vehicle sales in a given year",
        annotations=[p, u("10⁶ vehicle / year")],
    )
    cl.setdefault(
        id="stock",
        description="existing vehicle stock (fleet) in a given year",
        annotations=[p, u("10⁶ vehicle")],
    )
    cl.setdefault(
        id="tkm",
        description="tonne-kilometers traveled",
        annotations=[f, u("10⁹ tonne-km / year")],
    )
    cl.setdefault(
        id="ttw_bc",
        description="tank-to-wheel (i.e., direct) emissions of black carbon",
        annotations=[u("kt BC / year")],
    )
    cl.setdefault(
        id="ttw_ch4",
        description="tank-to-wheel (i.e., direct) emissions of methane",
        annotations=[u("kt CH₄ / year")],
    )
    cl.setdefault(
        id="ttw_co2",
        description="tank-to-wheel (i.e., direct) emissions of carbon dioxide",
        annotations=[u("Mt CO₂ / year")],
    )
    cl.setdefault(
        id="ttw_co2e",
        description="tank-to-wheel (i.e., direct) emissions of all Kyoto GHGs (in terms of CO2-equivalent emissions)",
        annotations=[u("Mt CO₂-eq / year")],
    )
    cl.setdefault(
        id="ttw_n2o",
        description="tank-to-wheel (i.e., direct) emissions of nitrous oxide",
        annotations=[u("kt N₂O / year")],
    )
    cl.setdefault(
        id="ttw_pm2.5",
        description="tank-to-wheel (i.e., direct) emissions of fine particulate matter",
        annotations=[u("kt PM2.5 / year")],
    )
    cl.setdefault(
        id="vkt",
        description="vehicle-kilometers traveled",
        annotations=[u("10⁹ vehicle-km / year")],
    )
    cl.setdefault(
        id="wtt_co2e",
        description="well-to-tank (i.e., upstream) emissions of all Kyoto GHGs (in terms of CO2-equivalent emissions)",
        annotations=[u("Mt CO₂ / year")],
    )
    cl.setdefault(
        id="wtw_co2e",
        description="well-to-wheel (i.e., lifecycle) emissions of all Kyoto GHGs (in terms of CO2-equivalent emissions)",
        annotations=[u("Mt CO₂-eq / year")],
    )
    return cl


@cache
def get_cl_region() -> "common.Codelist":
    """Return a code list of model regions.

    This structural metadata was formerly in :file:`data/model/regions.yaml`.
    """
    cl: "common.Codelist" = common.Codelist(id="CL_REGION")

    def _add(id, children: str):
        parent = cl.setdefault(id=id)
        for child_id in children.split():
            parent.append_child(cl.setdefault(id=child_id))

    _add(
        "Africa",
        """AGO BDI BEN BFA BWA CAF CIV CMR COD COG COM CPV DJI DZA ERI ESH ETH GAB GHA
        GIN GMB GNB GNQ KEN LBR LBY LSO MAR MDG MLI MOZ MRT MUS MWI NAM NER NGA REU RWA
        SDN SEN SLE SOM STP SWZ TCD TGO TUN TZA UGA ZAF ZMB ZWE""",
    )
    _add("Australia", "AUS")
    _add("Brazil", "BRA")
    _add("Canada", "CAN")
    _add("China", "CHN HKG MAC TWN")
    _add(
        "EU-27",
        """AUT BEL BGR CYP CZE DEU DNK ESP EST FIN FRA GBR GRC GRL HRV HUN IRL ITA LTU
        LUX LVA MLT NLD POL PRT ROM ROU SVK SVN SWE""",
    )
    _add("India", "IND")
    _add("Japan", "JPN")
    _add("Mexico", "MEX")
    _add("Middle East", "ARE BHR EGY IRN IRQ ISR JOR KWT LBN OMN PSE QAT SAU SYR YEM")
    _add(
        "Non-EU Europe",
        """ALB AND ARM AZE BIH BLR CHE CHI FRO GEO GIB IMN ISL LIE MCO MDA MKD MNE NOR
        SCG SHN SJM SMR SPM SRB TCA TUR UKR VAT WLF YUG""",
    )
    _add(
        "Other Asia-Pacific",
        """AFG ASM BGD BRN BTN CCK COK CXR FJI FSM GUM IDN KAZ KGZ KHM KIR LAO LKA MDV
        MHL MMR MNG MNP MYS MYT NCL NFK NIU NPL NRU NZL PAK PCI PCN PHL PLW PNG PRK PYF
        SGP SLB SYC THA TJK TKL TKM TLS TON TUV UZB VNM VUT WSM""",
    )
    _add(
        "Other Latin America",
        """ABW AIA ANT ARG ATG BHS BLZ BMU BOL BRB CHL COL CRI CUB CYM DMA DOM ECU FLK
        GLP GRD GTM GUF GUY HND HTI JAM KNA LCA MSR MTQ NIC PAN PER PRY SLV SUR TTO URY
        VCT VEN VGB VIR""",
    )
    _add("Russia", "RUS")
    _add("South Korea", "KOR")
    _add("U.S.", "PRI USA")

    return cl


def get_cl_technology() -> "common.Codelist":
    cl: "common.Codelist" = common.Codelist(id="CL_TECHNOLOGY")

    def _F(expr: str) -> dict[str, list["v21.Annotation"]]:
        return dict(
            annotations=[
                v21.Annotation(
                    id="FUEL", text=repr(tuple(sorted(["All"] + expr.split("|"))))
                )
            ]
        )

    cl.setdefault(id="All")
    cl.setdefault(id="Liquids", **_F("Liquids"))
    cl.setdefault(
        id="Liquids PHEV",
        description="Plug-in hybrid electric vehicle",
        **_F("Electricity|Liquids|Liquids/Electricity"),
    )
    cl.setdefault(
        id="BEV",
        description="Plug-in battery-electric vehicle (pure electric)",
        **_F("Electricity"),
    )
    cl.setdefault(
        id="FCEV",
        description="Fuel cell electric vehicle",
        **_F("Hydrogen"),
    )
    cl.setdefault(
        id="CNG",
        description="Compressed natural gas vehicle",
        **_F("Natural gas"),
    )
    cl.setdefault(id="Natural gas", **_F("Natural gas"))
    cl.setdefault(id="Electric", **_F("Electricity"))
    cl.setdefault(id="Hydrogen", **_F("Hydrogen"))
    cl.setdefault(id="Coal", **_F("Coal"))

    return cl
