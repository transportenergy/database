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
    drop=["IPCC-Annex", "World Region"],
)


def process(df):
    raise NotImplementedError
    # TODO column 'ISO-A3' already has ISO 3166 alpha-3 codes; use this instead of
    #      regenerating
    # TODO use the following
    # - Int. Aviation --> World
    # - Int. Shipping --> World
    # TODO discard rows where "IPCC" is anything other than r"1\.A\.3*"
    # TODO the Jupyter notebook assigned the units "10^6 tonne / year", but then
    #      divided the magnitudes by 1e3 *without* changing the units. The text says
    #      "For each value, convert them to billion"
    # TODO map "Mode". Per the Jupyter notebook: "There are five IPCC descriptions and
    #      this is how each one is mapped to our schema:
    # - 1. For countries:
    # -     IPCC --> Mode
    # -     Railways --> Rail
    # -     Road Transportation --> Road
    # -     Civil Aviation --> Air
    # -     Other Transportation --> Other
    # -     Water-borne Navigation --> Shipping
    # -
    # - 2. For Int. Aviation country:
    # -     IPCC --> Mode
    # -     Civil Aviation --> Domestic Aviation
    # -
    # - 3. For Int. Shipping country:
    # -     IPCC --> Mode
    # -     Water-Borne Navigation --> Domestic Shipping
