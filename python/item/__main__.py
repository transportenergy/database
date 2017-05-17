"""Command-line interface for the iTEM databases.

This tool takes configuration options in one of two ways:

1. From a file named item_config.yaml in the current directory. For
instance, to override the path to the raw model data, put the
following in item_config.yaml:

\b
    path:
      'model raw': ../custom/data/location

2. From command-line options. For instance, give the following:

       $ ./run --path model_raw ../custom/data/location COMMAND

 Underscores are converted to spaced automatically.

In a Python script, the following is equivalent:

\b
    import item
    item.init_paths(model_raw='../custom/data/location')
    …

"""
from textwrap import indent

import click

from item.model.__main__ import model
from item.stats.__main__ import stats


@click.group(help=__doc__)
@click.option('--path', 'paths',
              type=(str, click.Path()),
              multiple=True,
              metavar='<KEY> <PATH>',
              help='Override data paths (multiple allowed).')
def main(paths):
    from item.common import init_paths

    paths = {k.replace('_', ' '): v for (k, v) in paths}

    init_paths(**paths)


@main.command()
def debug():
    """Show debugging information, including paths."""
    import yaml

    from item.common import config, paths

    dump_args = dict(indent=2, default_flow_style=False)

    def _dump(data):
        print(indent(yaml.dump(data, **dump_args), '  '))

    print('Configuration file: %s' % config.get('_filename', 'none'))
    _dump(config.get('_from_file', {}))

    print('Command-line overrides:')
    _dump(config.get('_cli', {}))

    print('Paths:')
    _dump(paths)


main.add_command(model)
main.add_command(stats)


if __name__ == '__main__':
    main()  # pragma: no cover
