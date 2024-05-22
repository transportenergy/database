"""Data cleaning code and configuration for T010."""

from item.util import convert_units, dropna_logged

#: iTEM data flow matching the data from this source.
DATAFLOW = "STOCK"

#: Dimensions and attributes which do not vary across this data set.
#:
#: NB “_T” the code for “Total”, is used for the ‘TECHNOLOGY’ and ‘VEHICLE’ dimensions,
#: since this data set provides totals.
COMMON_DIMS = dict(
    source="International Organization of Motor Vehicle Manufacturers",
    variable="Stock",
    service="Freight",
    unit="10^6 vehicle",
    mode="Road",
    technology="_T",
    vehicle="_T",
)

#: Column name to map to ISO 3166 alpha-3 codes.
COLUMNS = dict(country_name="REGIONS/COUNTRIES")


def process(df):
    """Process data set T010.

    - Melt from wide to long format.
    - Remove the ‘,’ thousands separators from the values in the ‘VALUE’ column; convert
      to :class:`float`.
    - Drop null values.
    - Convert units from 10³ vehicles to 10⁴ vehicles.
    """
    return (
        df.melt(
            id_vars=[COLUMNS["country_name"]],
            var_name="TIME_PERIOD",
            value_name="VALUE",
        )
        .assign(VALUE=lambda df_: df_["VALUE"].str.replace(",", "").astype(float))
        .pipe(dropna_logged, "VALUE", [COLUMNS["country_name"]])
        .pipe(convert_units, "kvehicle", "Mvehicle")
    )
