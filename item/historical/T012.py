"""Data cleaning code and configuration for T012."""
import numpy as np

from item.util import convert_units, dropna_logged

#: iTEM data flow matching the data from this source.
DATAFLOW = "POPULATION"

#: Dimensions and attributes which do not vary across this data set.
COMMON_DIMS = dict(
    source="United Nations",
    variable="Population",
    unit="10^6 people",
)

#: Column names:
#:
#: - ``drop``: to drop from the raw data.
#: - ``country_name``: to map to ISO 3166 codes.
COLUMNS = dict(
    drop=[
        "Index",
        "Variant",
        "Notes",
        "Country code",
        "Parent code",
    ],
    #
    country_name="Region, subregion, country or area *",
)


def process(df):
    """Process data set T012.

    - Select only rows with ``Type == "Country/Area"``; then drop this column.
    - Rename "Channel Islands" (ISO 3166 numeric code 830) with 831 (Jersey), the larger
      (compared to 832/Guernsey) of the two Channel Islands. Code 830 does not exist.
    - Melt from wide to long format.
    - Remove spaces from strings in the "Value" column; convert to numeric.
    - Drop null values.
    - Convert units from 10³ persons to 10⁶ persons.
    """
    return (
        df.query("Type == 'Country/Area'")
        .drop("Type", axis=1)
        .replace("Channel Islands", "Jersey")
        .melt(
            id_vars=[COLUMNS["country_name"]],
            var_name="TIME_PERIOD",
            value_name="Value",
        )
        .assign(
            Value=lambda df_: df_["Value"]
            .str.replace(" ", "")
            .replace("...", "NaN")
            .astype(np.float)
        )
        .pipe(dropna_logged, "Value", [COLUMNS["country_name"]])
        .pipe(convert_units, "kpassenger", "Mpassenger")
    )
