import click
from click import Group

from . import OpenKAPSARC
from .utils import main as _phase1

historical = Group('historical', help="Manipulate the historical database.")


@historical.command()
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


@historical.command()
@click.argument('input_dir', type=click.Path(exists=True, file_okay=False),
                default='IK2_Open_Data')
@click.argument('output_file', type=click.Path(dir_okay=False, writable=True),
                default='IK2_Open_Data_conv_phase1.csv')
def phase1(input_dir, output_file):
    """Convert raw data to have consistent columns and units.

    INPUT_DIR defaults to 'IK2_Open_Data'.
    OUTPUT_FILE defaults to 'IK2_Open_Data_conv_phase1.csv'.
    """
    _phase1(input_dir, output_file)
