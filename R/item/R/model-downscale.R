# Functions used for downscaling reported data from model-reported regions to countries
#' Load the data submitted by the individual models, cleaned and placed into a common folder
#'
#' @param model_data_folder folder where the pre-processed model output data is located
#' @details Assumes that the model data are all in the same folder, named with the extension ".csv",
#' and that no other csv files are in the same folder
#' @importFrom tidyr gather
#' @export
load_preprocessed_data <- function(model_data_folder){
  # Indicate the directory where the pre-processed model output is available
  domain <- paths[[model_data_folder]]

  if (is.null(domain)) {
    print(paste('invalid model:', model))
    return()
  }
  # Put all of the data in a list, where each model is an element of the list
  data <- list()
  filenames <- list.files(domain)[endsWith(list.files(domain), "csv")]

  for(fnum in seq_along(filenames)){
    cat("Loading", filenames[fnum], "...\n")
    fqfn <- paste0(domain, "/",filenames[fnum])
    f <- sub(".csv", "", filenames[fnum])

    # Read in the data tables to the list
    data[[f]] <- read.csv(fqfn, comment.char = COMMENT_CHAR, stringsAsFactors=FALSE) %>%
      # apply tidy (internal item function) and gather (i.e., melt) the years
      tidy() %>%
      gather(year, value, matches(YEAR_PATTERN))
  }
  return(data)
}

#' Apply corrections to pre-processed data, where the submitted data requires further modifications
#'
#' @param data list of data frames with model data
#' @details Applies model-specific functions, matching the named element of the list to a
#' corresponding function containing the same string ("correct_" + model name)
#' @importFrom assertthat assert_that
correct_preprocessed_data <- function(data){
  assert_that(is.list(data))
  for(model in names(data)){
    if( exists(paste0("correct_", model), mode = "function")){
      print( paste0( "Applying corrections to data submitted by model: ", model ))
      correction_function <- get( paste0("correct_", model))
      data[[model]] <- correction_function(data[[model]])
    }
  }
  return(data)
}


