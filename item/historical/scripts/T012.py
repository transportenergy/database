"""Data cleaning code and configuration for T012."""
import numpy as np

from item.historical.util import dropna_logged
from item.structure import column_name
from item.utils import convert_units

#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    source="United Nations",
    variable="Population",
    unit="10^6 people",
)

#: Columns to drop from the raw data.
COLUMNS = dict(
    drop=[
        "Index",
        "Variant",
        "Notes",
        "Country code",
        "Parent code",
    ],
    # Column containing country name for determining ISO 3166 alpha-3 codes and
    # iTEM regions. Commented, because this is the default value.
    # country_name='Country',
)


def process(df):
    """Process data set T012."""

    def clean(df):
        return df.assign(
            Value=df["Value"]
            .str.replace(" ", "")
            .replace("...", "NaN")
            .astype(np.float),
        )

    # - Select only rows with Type == "Country/Area".
    # - Rename the column with country names to to "Country".
    # - Remove spaces from strings in the "Value" column; convert to numeric.
    # - Drop null values.
    # - Convert to the preferred iTEM units.
    return (
        df.query("Type == 'Country/Area'")
        .drop("Type", axis=1)
        .rename(columns={"Region, subregion, country or area *": "Country"})
        .melt(id_vars=["Country"], var_name=column_name("YEAR"), value_name="Value")
        .pipe(clean)
        .pipe(dropna_logged, "Value", ["Country"])
        .pipe(convert_units, "Mpassenger", "Gpassenger")
    )
