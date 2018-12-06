#' Apply corrections to MoMo submitted data
#'
#' @param x data table with MoMo model data
#' @details Applies model-specific corrections to reporting categories
#' @importFrom assertthat assert_that
#' @importFrom dplyr left_join
#' @importFrom magrittr "%>%"
correct_momo <- function( x ){
  x <- x %>%
    # Energy is reported in zetajoules; convert to petajoules
    mutate(value = if_else(variable == "energy", value * CONV_ZJ_PJ, value)) %>%
    #Population is in billions and GDP is in trillions. Convert to millions and billions, respectively.
    mutate(value = if_else(variable == "Population", value * CONV_BIL_MIL, value)) %>%
    mutate(value = if_else(variable == "PPP-GDP", value * CONV_TRIL_BIL, value)) %>%
    #The 4DS scenario is reported as zero in all years.
    filter(!(variable == "PPP-GDP" & scenario == "4DS")) %>%
    filter(!(variable == "Population" & scenario == "4DS"))
  x_4ds_socio <- subset(x, variable %in% c( "PPP-GDP", "Population"))
  x_4ds_socio$scenario <- "4DS"
  x <- bind_rows(x, x_4ds_socio)
  return(x)
}
