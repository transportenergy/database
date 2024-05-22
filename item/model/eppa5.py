from os.path import join

import pandas as pd
import pint
import yaml

from .common import log


def country_map(path):
    """Construct the countries-regions mapping for EPPA5.

    *path* points to the item2-data directory containing downscaling
    information files.

    *eppa5_map.tsv* maps from 'Countries' to EPPA5 regions. Some of these are
    ISO 3166 alpha-3 codes, but others (e.g. 'XAC') are special codes denoting
    aggregate regions in the Global Trade Analysis Project (GTAP) database that
    underlies EPPA.

    country_map():
    1. Reads a mapping of the GTAP regions to ISO codes/countries,
    2. Merges this with the mapping of GTAP countries/regions to EPPA5 regions.
    3. Writes the result to *eppa.tsv*.

    Requires:
    - eppa5_map.tsv
    - gtap.tsv (see header comment)

    """
    import pandas as pd
    import pycountry as pc

    def lookup_alpha3(name):
        """Look up the ISO 3166 alpha-3 code for the country *name*.

        If the country no longer exists (e.g. Netherlands Antilles), its
        historic code is returned.
        """
        try:
            return pc.countries.get(name=name).alpha3
        except KeyError:
            return pc.historic_countries.get(name=name).alpha3

    # Read the GTAP aggregate regions → country name mapping
    gtap = pd.read_table(join(path, "gtap.tsv"), comment="#")

    # Add alpha-3 codes
    gtap["Country"] = gtap["Country name"].apply(lookup_alpha3)

    # Read the GTAP region → EPPA5 region mapping
    eppa5 = pd.read_table(join(path, "eppa5_map.tsv"))

    # Merge the two tables. A single row in the EPPA5 mapping with Country ==
    # 'XAC' is replaced with multiple rows, one for each country in that GTAP
    # region. Common column names are suffixed '_x' (EPPA5) or '_y' (GTAP).
    df = pd.merge(
        eppa5, gtap, how="outer", left_on="Country", right_on="GTAP region", sort=True
    ).sort_index("columns")

    # Fill across columns, so that 'Country_y' and 'Country name_y' contain
    # values even if absent from the GTAP regions table
    df = df.fillna(axis="columns", method="ffill")

    # Select and rename columns, and output
    cols = {
        "Country_y": "ISO",
        "Country name_y": "name",
        "Region": "EPPA5",
    }
    df[list(cols.keys())].rename(columns=cols).set_index("ISO")[
        ["EPPA5", "name"]
    ].sort_index().drop_duplicates().to_csv(join(path, "eppa5.tsv"), sep="\t")


# FIXME Reduce complexity from 13 → ≤12
def import_data(data_path, metadata_path):  # noqa: C901
    # # Construct the countries-regions mapping
    # country_map(join(path, '..', 'downscale'))

    # Read the metadata
    with open(join(metadata_path, "variables.yaml")) as vars_f:
        vars = yaml.safe_load(vars_f)

    ureg = pint.UnitRegistry()
    for unit in vars["_units"]:
        ureg.define(unit)

    # Read the raw data
    try:
        import gdx

        if gdx.__version__ > "4":
            f = gdx.open_dataset(data_path)
        else:
            f = gdx.File(data_path)
    except ImportError:
        # py-gdx not installed
        return None, None

    data = []

    # Iterate over variables
    for var in sorted(vars.keys()):
        if var.startswith("_"):
            continue
        else:
            attrs = vars[var]
        log("  loading: %s" % var)

        # Attributes of the variable to import
        # Unit conversion
        convert = tuple(map(ureg, attrs.get("convert", [0, 0])))
        exponent = 1
        if not convert[0].dimensionless:
            log("    converting %s → %s" % convert)
            if convert[0].dimensionality ** -1 == convert[1].dimensionality:
                exponent = -1
                log("    values to be inverted")
        factor = (convert[0] ** exponent / convert[1]).to_base_units()
        log("    values to be multiplied by %f" % factor)

        # Sub-selection from a larger variable
        select = attrs.get("select", {})

        # Time and region dimensions
        time_dim = attrs.get("time", "T")
        region_dim = attrs.get("region", "R")
        if isinstance(region_dim, int):
            region_dim = "_%s_%d" % (var, region_dim)

        # Aggregation
        agg = attrs.get("agg", "sum")

        # Extract the variable from the GDX file as an xr.DataArray and change
        # units
        da = f[var] ** exponent * factor

        if len(select):
            # Select a subset of dimensions
            log("    selecting: " + ", ".join(["%s=%s" % kv for kv in select.items()]))
            da = da.sel(**select)

        # Determine one or more quantities to unpack from *da*
        qties = attrs["item"]["quantity"]
        try:
            dim = qties.pop("_dim")
            quantities = [({dim: k}, v) for k, v in qties.items()]
            agg = False
        except TypeError:
            quantities = [({}, qties)]

        # Retrieve quantities
        for sub, qty in quantities:
            log(
                "    %sto %s"
                % (["%s=%s " % kv for kv in sub.items()][0] if len(sub) else "", qty)
            )
            # Convert to pd.DataFrame, unstack the time dimension to columns,
            # convert the region dimension to a column named 'Region'
            df = (
                da.sel(**sub)
                .to_dataframe()[var]
                .unstack(time_dim)
                .reset_index()
                .rename(columns={region_dim: "region"})
            )

            if agg is not False:
                # Aggregate this set of rows, e.g. take a sum
                log("    aggregating using .%s()" % agg)
                aggregate = getattr(df, agg)()
                aggregate["region"] = "Global"
                df = df.append(aggregate, ignore_index=True)

            # Fill the other index columns
            df["variable"], df["mode"], df["technology"], df["fuel"] = qty
            df["unit"] = attrs["item"]["unit"]

            data.append(df)

    # Combine all data
    data = pd.concat(data)
    data["Model"] = "EPPA5"
    data["Scenario"] = "Outlook 2015"

    return data, None
