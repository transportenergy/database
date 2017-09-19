#' Apply corrections to EIA (WEPS+) submitted data
#'
#' @param x data table with EIA (WEPS+) model data
#' @details Applies model-specific corrections to reporting categories
#' @importFrom assertthat assert_that
#' @importFrom dplyr filter mutate if_else
#' @importFrom magrittr "%>%"
correct_eia <- function( x ){
  x <- x %>%
    # WEPS+ has an "LDT" category, whose output is tonne-km/yr. Because of the output unit,
    # this is re-classified as HDT for iTEM
    mutate(mode = if_else(mode == "LDT", "HDT", mode))
  return(x)
}
