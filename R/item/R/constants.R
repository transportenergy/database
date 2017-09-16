# Some useful conversions, assumptions, and constants
COMMENT_CHAR <- "#"
YEAR_PATTERN <- "^(1|2)[0-9]{3}$"   # a 1 or 2 followed by three digits, and nothing else
ITEM_YEARS <- c(seq(2005, 2040, 5), seq( 2050, 2100, 10))
ITEM_DATA_COLUMNS <- c("model", "scenario", "region", "variable", "mode", "technology",
                       "fuel", "unit", "year", "value")
DS_DATA_COLUMNS <- ITEM_DATA_COLUMNS
   DS_DATA_COLUMNS[which(DS_DATA_COLUMNS == "region")] <- "iso"
CONV_ZJ_PJ <- 1e-6    #convert from zetajoules to petajoules
CONV_BIL_MIL <- 1000 # convert from billions to millions
CONV_TRIL_BIL <- 1000 # convert from trillions to billions
CONV_ONES_MIL <- 1e-6 # convert from ones to millions
CONV_BILLIONLITERSGASOLINE_PJ <- 34.2 # convert from billion liters of gasoline to petajoules
CONV_GDP_MIL10USD_BIL05USD <- 0.000909 # convert from million 2010 USD to billion 2005 USD
BASEYEAR <- 2010 # base year assumed for country-level datasets with a single base year
DS_OUTPUT_DIR <- "outputs/downscale"
DS_GDP_ELAST_CO2 <- 0.5  # assumed GDP elasticity of total CO2 emissions used for CO2 downscaling proxy
DS_DEFAULT_SCENARIO <- "SSP2" # default socioeconomic realization for downscaling from model regions to countries, for models that provided no socioeconomic data


