Command-line interface (:mod:`item.cli`)
****************************************

The command ``item`` is installed with the package.
The CLI provides help with the ``--help`` option::

    $ item --help
    Usage: item [OPTIONS] COMMAND [ARGS]...

      Command-line interface for the iTEM databases.

    Options:
      --path <KEY> <PATH>  Override data paths (multiple allowed).
      --help               Show this message and exit.

    Commands:
      debug       Show debugging information, including paths.
      help        Show extended help for the command-line tool.
      historical  Manipulate the historical database.
      mkdirs      Create a directory tree for the database.
      model       Manipulate the model database.
      remote      Access remote data sources.
      template    Generate the MIP submission template.
