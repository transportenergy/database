from click import Argument, Command, Group

from item.model import process_raw
from item.model.dimensions import list_pairs
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

add(plot_all_item1)
