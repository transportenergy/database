# Some useful conversions, assumptions, and constants
COMMENT_CHAR <- "#"
YEAR_PATTERN <- "^(1|2)[0-9]{3}$"   # a 1 or 2 followed by three digits, and nothing else
ITEM_YEARS <- c(seq(2005, 2040, 5), seq( 2050, 2100, 10))
BASEYEAR <- 2010 # base year assumed for country-level datasets with a single base year
SIGNIFICANT_FIGURES <- 8 # number of significant figures to print output (default is writing all vars to 15 decimal places)

# iTEM columns
ITEM_ID_COLUMNS <- c("model", "scenario", "region", "variable", "mode", "technology", "fuel", "unit", "year")
ITEM_DATA_COLUMNS <- c(ITEM_ID_COLUMNS, "value") # ID columns plus the value column
ITEM_IDVARS_WITH_ALLS <- c("region", "mode", "technology", "fuel") # ID columns that collapse to "All" for reporting

# Downscaling-related columns - same as above but the region column is re-named to iso
DS_ID_COLUMNS <- sub( "region", "iso", ITEM_ID_COLUMNS)
DS_DATA_COLUMNS <- sub( "region", "iso", ITEM_DATA_COLUMNS)
DS_IDVARS_WITH_ALLS <- sub( "region", "iso", ITEM_IDVARS_WITH_ALLS)

# For global-only variables, don't include the region column
GLOBAL_IDVARS_WITH_ALLS <- ITEM_IDVARS_WITH_ALLS[ ITEM_IDVARS_WITH_ALLS != "region"]

# Unit conversions
CONV_ZJ_PJ <- 1e6    #convert from zetajoules to petajoules
CONV_BIL_MIL <- 1000 # convert from billions to millions
CONV_TRIL_BIL <- 1000 # convert from trillions to billions
CONV_ONES_MIL <- 1e-6 # convert from ones to millions
CONV_BILLIONLITERSGASOLINE_PJ <- 34.2 # convert from billion liters of gasoline to petajoules
CONV_GDP_MIL10USD_BIL05USD <- 0.000909 # convert from million 2010 USD to billion 2005 USD

DS_OUTPUT_DIR <- "outputs/downscale"
DS_GDP_ELAST_CO2 <- 0.5  # assumed GDP elasticity of total CO2 emissions used for CO2 downscaling proxy
DS_DEFAULT_SCENARIO <- "SSP2" # default socioeconomic realization for downscaling from model regions to countries, for models that provided no socioeconomic data
