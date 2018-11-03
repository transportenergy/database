#' Apply corrections to BP submitted data
#'
#' @param x data table with BP model data
#' @details Applies model-specific corrections to reporting categories
#' @importFrom assertthat assert_that
#' @importFrom dplyr mutate if_else
#' @importFrom magrittr "%>%"
correct_bp <- function( x ){
  #BP's GDP is in 2010 dollar year and in millions. Convert to billion 2005 USD and rename the unit
  x <- mutate(x, value = if_else(variable == 'PPP-GDP' & unit == "billion US$2010/yr",
                                 value * CONV_GDP_MIL10USD_BIL05USD, value)) %>%
    mutate(unit = if_else(unit == "billion US$2010/yr", "billion US$2005/yr", unit)) %>%
    # Some asymmetrical reporting exists here; technology- and fuel-level details are available in some cases but not others
    # If these are reported as "All", they will not be included in subsequent aggregations.
    mutate(technology = if_else(technology == "All", "All (no detail)", technology),
           fuel = if_else(fuel == "All", "All (no detail)", fuel))
  return(x)
}
