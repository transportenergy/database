#' Apply corrections to Roadmap submitted data
#'
#' @param x data table with Roadmap model data
#' @details Applies model-specific corrections to reporting categories
#' @importFrom assertthat assert_that
#' @importFrom dplyr left_join bind_rows
#' @importFrom magrittr "%>%"
correct_roadmap <- function( x ){
  assert_that(is.data.frame(x))
  # First, go ahead and load some mapping files that will be used
  tech_mapping <- load_data_file("model/roadmap/tech_mapping", quiet = TRUE)
  variable_unit_mapping <- unique(load_data_file("iTEM2_template", quiet = TRUE)[c("variable", "unit")])
  x <- x %>%
    # Roadmap model name is appended with metadata that needs to be stripped off
    mutate(model = "Roadmap") %>%
    # EU-28 is re-set to EU-27 for consistency
    mutate(region = sub( "EU-28", "EU-27", region)) %>%
    # Different size classes of heavy duty trucks (HDTs) are aggregated
    mutate( mode = if_else(grepl("HDT", mode), "HDT", mode)) %>%
    # 2-wheelers (2W) and 3-wheelers (3W) are aggregated
    mutate( mode = if_else(mode == "2W", "2W and 3W", mode)) %>%
    mutate( mode = if_else(mode == "3W", "2W and 3W", mode)) %>%
    # Fuel + technology information in the existing "technology" column is split into separate columns, and set
    # according to an exogenous mapping.
    rename(roadmap_technology = technology) %>%
    left_join( y = tech_mapping, by = "roadmap_technology") %>%
    select(-roadmap_technology) %>%
    # Sales and stock are reported in individual units; we want millions
    mutate(value = if_else(variable %in% c("sales", "stock"), value * CONV_ONES_MIL, value)) %>%
    # Aviation service is indicated in rpkm; convert to pkm for consistency
    mutate(variable = if_else(variable == "rpkm", "pkm", variable)) %>%
    # Join in the units from the variable-unit mapping table
    select(-unit) %>%
    left_join( variable_unit_mapping, by = "variable" ) %>%
    # any missing values for units indicate variables not considered in item2
    filter(!is.na(unit))

  # The roadmap aviation and rail are common to all scenarios. Split data by mode...
  x_av_rail <- subset(x, mode %in% c("Aviation", "Passenger Rail", "Freight Rail"))
  x_road <- subset(x, !mode %in% c( "Aviation", "Passenger Rail", "Freight Rail"))
  x_list <- list()
  # for each scenario, bind the road data for that scenario with the aviation + rail data,
  # re-naming the scenario in the aviation and rail data
  for(scen in unique(x_road$scenario)){
    x_av_rail$scenario <- scen
    x_list[[scen]] <- bind_rows(subset( x_road, scenario == scen),
                                x_av_rail)
  }
  x_final <- do.call(bind_rows, x_list)
  # Finally, re-sort for the correct column order
  x_final <- x_final[ITEM_DATA_COLUMNS]
    return(x_final)
}
