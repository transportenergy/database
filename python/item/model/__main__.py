from click import Argument, Command, Group

from item.model import process_raw
from item.model.dimensions import (
    list_pairs,
    make_regions_csv,
    make_regions_yaml,
    )
from item.model.plot import plot_all_item1


model = Group('model', help="Manipulate the model database.")


def add(fn, *params):
    """Wrap *fn* and add it to the click.Group."""
    model.add_command(Command(
        fn.__name__,
        callback=fn,
        help=fn.__doc__,
        params=params))


add(process_raw,
    Argument(['models'], nargs=-1),
    )

add(list_pairs,
    Argument(['in_file'], default='quantities.tsv'),
    Argument(['out_file'], default='pairs.txt'),
    )

add(make_regions_csv,
    Argument(['models'], help='List of models to output'),
    Argument(['out_file']),
    )

add(make_regions_yaml,
    Argument(['in_file']),
    Argument(['country'], help='IN_FILE column with country codes'),
    Argument(['region'], help='IN_FILE column with region names'),
    Argument(['out_file']),
    )

add(plot_all_item1)
