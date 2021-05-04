import click
from click import Group

from . import fetch_source
from .legacy import main as _phase1

historical = Group("historical", help="Manipulate the historical database.")


@historical.command()
@click.argument("output_path", type=click.Path(file_okay=False, writable=True))
def diagnostics(output_path):
    """Generate diagnostics on the historical input data sets."""
    from .diagnostic import run_all

    run_all(output_path)


@historical.command()
@click.argument("source", type=int)
def fetch(source):
    """Retrieve raw data for SOURCE."""
    path = fetch_source(source)
    print(f"Retrieved {path}")


@historical.command()
@click.argument(
    "output_file",
    type=click.Path(dir_okay=False, writable=True),
    default="IK2_Open_Data_conv_phase1.csv",
)
@click.option(
    "--use-cache/--no-cache",
    is_flag=True,
    default=True,
    help="Use cached files (no network traffic).",
)
def phase1(output_file, use_cache):
    """Convert raw data to have consistent columns and units.

    OUTPUT_FILE defaults to 'IK2_Open_Data_conv_phase1.csv'.
    """
    _phase1(output_file, use_cache)
