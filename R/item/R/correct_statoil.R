#' Apply corrections to Statoil submitted data
#'
#' @param x data table with Statoil model data
#' @details Applies model-specific corrections to reporting categories
#' @importFrom assertthat assert_that
#' @importFrom dplyr mutate if_else
#' @importFrom magrittr "%>%"
correct_statoil <- function( x ){
  # Reporting of PHEV "fuel" where not applicable (stock, sales) with the string "All" causes this to get dropped from
  # subsequent aggregations. Reset it to "Electricity/Liquids"
  x <- mutate(x, fuel = if_else(technology == "PHEV" & fuel == "All", "Electricity/Liquids", fuel))
  return(x)
}
