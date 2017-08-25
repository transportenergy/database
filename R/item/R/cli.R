description <- "Command-line interface for the iTEM databases.

This tool takes configuration options in one of two ways:

1. From a file named item_config.yaml in the current directory. For
instance, to override the path to the raw model data, put the
following in item_config.yaml:

    path:
      'model raw': ../custom/data/location

2. From command-line options. For instance, give the following:

       $ ./run --path model_raw ../custom/data/location COMMAND

Underscores are converted to spaces automatically."

cli_debug <- function () {
  print(ls(config))
  print(ls(paths))
}

list_commands <- function (commands) {
  cmdlist <- paste(labels(commands), collapse='\n  ')
  paste('Commands:', cmdlist, sep='\n  ')
}

cli <- function () {
  # Load configuration from 'item_config.yaml'
  load_config()

  # Available commands
  commands <- list(
    mkdirs = make_database_dirs,
    debug = cli_debug,
    load_model_data = load_model_data
    )

  # Parse command-line options (currently none)
  option_list <- list()
  parser <- optparse::OptionParser(
    usage='%prog [OPTIONS] COMMAND',
    option_list=option_list,
    description=description,
    epilog=list_commands(commands))
  arguments <- optparse::parse_args(parser, positional_arguments=TRUE)
  args <- arguments$args

  init_paths()

  if (length(args) == 0) {
    # No command given -> print help
    optparse::print_help(parser)
  } else {
    # First argument is name of the command
    cmd <- get(args[1], commands)
    result <- do.call(cmd, as.list(args[-1]))
  }
}
