#' Apply corrections to Roadmap submitted data
#'
#' @param x data table with Roadmap model data
#' @details Applies model-specific corrections to reporting categories
#' @importFrom assertthat assert_that
#' @importFrom dplyr left_join
correct_roadmap <- function( x ){
  assert_that(is.data.frame(x))
  # First, go ahead and load the mapping file
  tech_mapping <- load_roadmap_tech_mapping()
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
    select(-roadmap_technology)

  # the next step of the processing is to copy the aviation and rail data that is common
  # to both scenarios, so that it is associated with each of the LDV scenarios
  # 8/25/2017 - STOPPED HERE

  # Finally, re-sort for the correct column order
  x <- x[c( as.character(index), "year", "value")]
    return(x)
}

#' Load Roadmap technology re-mapping CSV table
#'
#' @param roadmap_remapping_folder Folder where Roadmap remapping file is located
#' @param filename Name of Roadmap tech remapping file
load_roadmap_tech_mapping <- function(roadmap_remapping_folder = 'roadmap model processed',
                                      filename = "tech_mapping.csv"){
  domain <- paths[[roadmap_remapping_folder]]
  fqfn <- paste0(domain, "/",filename)
  tech_mapping <- read.csv(fqfn, comment.char = COMMENT_CHAR, stringsAsFactors=FALSE)
  return( tech_mapping)
}
