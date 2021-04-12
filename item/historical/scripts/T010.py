"""Data cleaning code and configuration for T010."""
from typing import Any, Dict

from item.historical.util import dropna_logged
from item.structure import column_name
from item.utils import convert_units

#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    source="International Organization of Motor Vehicle Manufacturers",
    variable="Stock",
    service="Freight",
    fuel="All",
    technology="All",
    vehicle_type="All",
    unit="10^6 vehicle",
    mode="Road",
)

#: Columns to drop from the raw data.
COLUMNS: Dict[str, Any] = dict(
    drop=[],
    # Column containing country name for determining ISO 3166 alpha-3 codes and
    # iTEM regions. Commented, because this is the default value.
    # country_name="Country",
)


def process(df):
    """Process data set T010."""

    def clean(df):
        return df.assign(
            Country=df["Country"].str.title(),
            Value=df["Value"].str.replace(",", "").astype(float),
        )

    # - Melt
    # - Remove the ',' from the values in the 'Value' column; convert to float
    # - Drop null values.
    # - Convert to the preferred iTEM units.
    df = (
        df.rename(columns={"REGIONS/COUNTRIES": "Country"})
        .melt(id_vars=["Country"], var_name=column_name("YEAR"), value_name="Value")
        .pipe(clean)
        .pipe(dropna_logged, "Value", ["Country"])
        .pipe(convert_units, "Mvehicle", "Gvehicle")
    )

    return df
