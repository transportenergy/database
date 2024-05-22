"""Command-line interface for the iTEM databases."""

from pathlib import Path
from textwrap import indent

import click

from item.historical.cli import historical
from item.model.cli import model
from item.remote.cli import remote


@click.group(help=__doc__)
@click.option(
    "--path",
    "paths",
    type=(str, click.Path()),
    multiple=True,
    metavar="<KEY> <PATH>",
    help="Override data paths (multiple allowed).",
)
def main(paths):
    from item.common import init_paths

    paths = {k.replace("_", " "): v for (k, v) in paths}

    init_paths(**paths)


@main.command()
def help():
    """Show extended help for the command-line tool."""
    print(__doc__, end="\n\n")
    print(
        """This tool takes configuration options in one of two ways:

1. From a file named item_config.yaml in the current directory. For
   instance, to override the path to the raw model data, put the
   following in item_config.yaml:

   path:
     'model raw': ../custom/data/location

2. From command-line options. For instance, give the following:

   $ ./run --path model_raw ../custom/data/location COMMAND

Underscores are converted to spaces automatically.

In a Python script, the following is equivalent:

    import item
    item.init_paths(model_raw='../custom/data/location')
    …
"""
    )


@main.command()
def debug():
    """Show debugging information, including paths."""
    import yaml

    from item.common import config, paths

    dump_args = dict(indent=2, default_flow_style=False)

    def _dump(data):
        print(indent(yaml.dump(data, **dump_args), "  "))

    print("Configuration file: %s" % config.get("_filename", "none"))
    _dump(config.get("_from_file", {}))

    print("Command-line overrides:")
    _dump(config.get("_cli", {}))

    print("Paths:")
    _dump(paths)


@main.command()
@click.option("--dry-run", "-n", is_flag=True, help="Only show what would be done.")
@click.argument("path", type=click.Path())
def mkdirs(path, dry_run):
    """Create a directory tree for the database."""
    from item.common import make_database_dirs

    make_database_dirs(path, dry_run)


@main.command()
def template():
    """Generate the MIP submission template."""
    from item.structure import make_template

    make_template()


@main.command("update-dsd")
def update_dsd():
    """Generate the iTEM SDMX data structures.

    The file item/data/structure.xml is updated.
    """
    import sdmx

    from item.structure import generate

    with open(Path(__file__).parent / "data" / "structure.xml", "wb") as f:
        f.write(sdmx.to_xml(generate(), pretty_print=True))


main.add_command(model)
main.add_command(historical)
main.add_command(remote)
