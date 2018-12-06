from click import Argument, Command, Group

from . import demo

stats = Group('stats', help="Manipulate the stats database.")


def add(fn, *params):
    """Wrap *fn* and add it to the click.Group."""
    stats.add_command(Command(
        fn.__name__,
        callback=fn,
        help=fn.__doc__,
        params=list(params)))


add(demo, Argument(['server']))
