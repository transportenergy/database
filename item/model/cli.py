import click
from click import Argument, Option

from item.model import make_regions_csv, make_regions_yaml, process_raw
from item.model.dimensions import list_pairs
from item.model.plot import plot_all_item1

model = click.Group("model", help="Manipulate the model database.")


def add(fn, *params):
    """Wrap *fn* and add it to the click.Group."""
    model.add_command(
        click.Command(fn.__name__, callback=fn, help=fn.__doc__, params=list(params))
    )


add(process_raw, Argument(["version"], type=int), Argument(["models"], nargs=-1))

add(
    list_pairs,
    Argument(["in_file"], default="quantities.tsv"),
    Argument(["out_file"], default="pairs.txt"),
)

add(
    make_regions_csv,
    Argument(["out_file"]),
    Argument(["models"], default=[]),
    Option(["--compare"], type=click.Path()),
)

add(
    make_regions_yaml,
    Argument(["in_file"]),
    Argument(["country"]),
    Argument(["region"]),
    Argument(["out_file"]),
)

add(plot_all_item1)
