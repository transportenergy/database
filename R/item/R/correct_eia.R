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
    mutate(mode = if_else(mode == "LDT", "HDT", mode)) %>%
    # Remove the "Wor" (world) reporting. The "Wor" region reports "All" mode, "All" fuel types, whereas at the
    # individual region level, "All" fuel types are not reported. This asymmetry would cause subsequent double counting.
    # All of the necessary data to re-estimate the global totals are available at the region level
    dplyr::filter(region != "All")
  return(x)
}
