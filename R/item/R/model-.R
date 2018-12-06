# List of the index columns required to identify all data series
index = list(
    'model',
    'scenario',
    'region',
    'variable',
    'mode',
    'technology',
    'fuel',
    'unit'
    )

# Make these available as a character vector
index_names <- as.character(index)

#' Load the iTEM model database
#'
#' @param version Model database version to load (1 or 2)
#' @export
load_model_data <- function (version) {
  # Read data from file
  path <- paths[[paste0('models-', as.character(version))]]

  if (is.null(path)) {
    print(paste('invalid model database version:', version))
    return()
  }

  data <- tidy(read.csv(path, stringsAsFactors = FALSE))
  data <- reshape2::melt(data, id.vars=index, variable.name='year', na.rm=TRUE)
  data$year <- as.numeric(data$year)

  return(data)
}

tidy <- function (df) {
  rename <- function (colname) {
    colname <- sub('^X', '', colname)
    if (suppressWarnings(is.na(as.integer(colname)))) {
      if (colname == 'Tech') colname <- 'Technology'
      return(tolower(colname))
    } else {
      return(as.integer(colname))
    }
  }

  names(df) <- lapply(names(df), rename)
  return(df)
}
