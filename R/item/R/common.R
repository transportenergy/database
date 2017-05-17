make_database_dirs <- function (path, dry_run = FALSE) {
  cat(paste('Creating database directories in:', path, '\n'))

  dirs <- c(
    file.path('model', 'database'),
    file.path('model', 'processed'),
    file.path('model', 'raw'),
    file.path('stats')
    )

  dirs <- c(path, file.path(path, dirs))

  if (as.logical(dry_run)) {
    noquote(dirs)
  } else {
    for (d in dirs) {
      dir.create(d, recursive=TRUE)
    }
  }
}

config <- new.env()
paths <- new.env()

load_config <- function () {
  config_file <- file.path(getOption('item wd'), 'item_config.yaml')
  if (file.exists(config_file)) {
    temp <- yaml::yaml.load_file(config_file)
    config <- list2env(temp, config)
  } else {
    config$path <- list()
  }
}

init <- function (libname, pkgname) {
  if (is.null(getOption('item wd'))) options(`item wd`=getwd())
  load_config()
  init_paths()
}

init_paths <- function (path_args=list()) {
  path_config <- config$path
  path_config <- utils::modifyList(path_config, path_args)

  init_path <- function(name, ...) {
    if (is.null(path_config[[name]])) {
      result <- do.call(file.path, list(...))
    } else {
      result <- path_config[[name]]
    }
    paths[[name]] <- normalizePath(result, mustWork=FALSE)
  }

  init_path('model', paths[['wd']])
  init_path('model raw', paths[['model']], 'raw')
  init_path('model processed', paths[['model']], 'processed')
  init_path('model database', paths[['model']], 'database')
  init_path('models-1', paths[['model database']], '1.csv')
  init_path('models-2', paths[['model database']], '2.csv')
}
