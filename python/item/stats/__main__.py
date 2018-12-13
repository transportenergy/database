import click
from click import Group

from . import OpenKAPSARC

stats = Group('stats', help="Manipulate the stats database.")


@stats.command
@click.argument('server')
def demo(server):
    """Access the KAPSARC APIs at the given SERVER."""
    ok = OpenKAPSARC(server)

    print('List of all repositories:')
    for repo in ok.datarepo():
        print(repo['name'], ':', repo['id'])

    # very verbose
    print('\n\nInformation on one repository:')
    print(ok.datarepo('ik2_open_data'))

    print('\n\nData from one table in a branch in a repository:')
    print(ok.table('ik2_open_data', 'modal_split_of_freight_transport'))
    print(ok.table('ik2_open_data', 'modal_split_of_freight_transport', 10))
    print(ok.table('ik2_open_data', 'modal_split_of_freight_transport', 30))
