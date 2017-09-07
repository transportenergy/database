#' Apply corrections to ITF submitted data
#'
#' @param x data table with ITF model data
#' @details Applies model-specific corrections to reporting categories
#' @importFrom assertthat assert_that
#' @importFrom dplyr mutate if_else
#' @importFrom magrittr "%>%"
correct_itf <- function( x ){
  # First load the variable_unit mapping, and extract the energy unit
  variable_unit_mapping <- unique(load_data_file("iTEM2_template", quiet = TRUE)[c("variable", "unit")])
  energy_unit <- variable_unit_mapping$unit[ variable_unit_mapping$variable == "energy"]
  x <- x %>%
    # ITF reported the variable "energy" as "fuel"
    mutate(variable = if_else(variable == "fuel", "energy", variable)) %>%
    # energy is reported in billion liters of gasoline instead of PJ. Change both values and unit names
    mutate(value = if_else(unit == "bil litres gasoline equiv/yr", value * CONV_BILLIONLITERSGASOLINE_PJ,
                           value)) %>%
    mutate(unit = if_else(unit == "bil litres gasoline equiv/yr", energy_unit, unit)) %>%
    # ITF reported "rail" in place of "Passenger Rail" for energy consumption. Re-set this
    mutate(mode = if_else(mode == "rail", "Passenger Rail", mode))
  return(x)
}
