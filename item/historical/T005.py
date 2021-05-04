from item.util import convert_units

#: iTEM data flow matching the data from this source.
DATAFLOW = "EMISSIONS"

#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    source="JRC",
    variable="Emissions",
    pollutant="CO2",
    lca_scope="TTW",
    service="_T",
    vehicle="_T",
    fuel="_T",
    technology="_T",
)

#: Columns to drop from the raw data.
COLUMNS = dict(
    drop=["IPCC_description", "IPCC-Annex", "Name", "World Region"],
)

#: Map from IPCC emissions category codes to iTEM ``CL_MODE`` values. The actual
#: descriptions appear in the ``IPCC_description`` column, which is discarded.
#:
#: - 1.A.3.a: Civil Aviation
#: - 1.A.3.b: Road Transportation
#: - 1.A.3.c: Railways
#: - 1.A.3.d: Water-borne Navigation
#: - 1.A.3.e: Other Transportation
MAP_MODE = {
    "1.A.3.a": "Air",
    "1.A.3.b": "Road",
    "1.A.3.c": "Rail",
    "1.A.3.d": "Water",
    "1.A.3.e": "Other",
}


def process(df):
    """Process T005.

    1. Select only measures with IDs beginning "1.A.3".
    2. Map from the IPCC emissions category (e.g. "1.A.3.a") to mode (e.g. "Air"); see
       :func:`map_mode`.
    3. Melt from wide to long format.
    4. Drop NA values.
    5. Use “_X” (not allocated/unspecified) as the region for international shipping and
       aviation.
    6. Convert from Mt/a to Gt/a.
    """
    return (
        df[df["IPCC"].str.startswith("1.A.3")]
        .assign(MODE=lambda df_: df_["IPCC"].apply(MAP_MODE.get))
        .drop(columns=["IPCC"])
        .melt(id_vars=["ISO_A3", "MODE"], var_name="TIME_PERIOD", value_name="VALUE")
        .dropna(subset=["VALUE"])
        .rename(columns={"ISO_A3": "REF_AREA"})
        .replace({"REF_AREA": {"SEA": "_X", "AIR": "_X"}})
        .pipe(convert_units, "megatonne / year", "gigatonne / year")
    )
