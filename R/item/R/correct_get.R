#' Apply corrections to GET submitted data
#'
#' @param x data table with GET model data
#' @details Applies model-specific corrections to reporting categories
#' @importFrom assertthat assert_that
#' @importFrom dplyr left_join
#' @importFrom magrittr "%>%"
correct_get <- function( x ){
  # GET reported some additional fuels that no other models reported.
  # The data associated with these extra fuels is dropped
  GET_fuels_to_drop <- c( "OIL-based Fossil Liquids", "CTL", "GTL", "PETRO_ICEV", "PETRO_HEV",
                          "CTL_ICEV", "CTL_HEV", "GTL_ICEV", "GTL_HEV", "PETRO" )
  x <- subset(x, !fuel %in% GET_fuels_to_drop)
  return(x)
}
