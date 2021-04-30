from functools import lru_cache

from item.historical.util import dropna_logged
from item.structure import column_name
from item.utils import convert_units


#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    source="JRC",
    variable="CO₂ emission (ttw)",
    technology="All",
    fuel="All",
    vehicle_type="All",
    service="All",
)

#: Columns to drop from the raw data.
COLUMNS = dict(
    drop=["IPCC_description", "IPCC-Annex", "World Region"],
)


def process(df):
    """Process T005.

    1. Select only measures with IDs beginning "1.A.3".
    2. Melt from wide to long format.
    3. Drop NA values.
    4. Map from the IPCC emissions category (e.g. "1.A.3.a") to mode (e.g. "Air");
       see :func:`map_mode`.
    5. Convert from Mt/a to Gt/a.
    """
    # TODO use the following
    # - Int. Aviation --> World
    # - Int. Shipping --> World

    return (
        df[df["IPCC"].str.startswith("1.A.3")]
        .melt(
            id_vars=["ISO_A3", "Name", "IPCC"],
            var_name=column_name("YEAR"),
            value_name=column_name("VALUE"),
        )
        .dropna(subset=[column_name("VALUE")])
        .rename(
            columns={"ISO_A3": column_name("ISO_CODE"), "Name": column_name("COUNTRY")}
        )
        .assign(mode=lambda df: df["IPCC"].apply(map_mode))
        .pipe(convert_units, "megatonne / year", "gigatonne / year")
    )


@lru_cache
def map_mode(value):
    return {
        "1.A.3.a": "Air",  # "Civil Aviation"
        "1.A.3.b": "Road",  # "Road Transportation"
        "1.A.3.c": "Rail",  # "Railways"
        "1.A.3.d": "Water",  # "Water-borne Navigation"
        "1.A.3.e": "Other",  # "Other Transportation"
    }.get(value)
