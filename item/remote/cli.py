import click
from click import Group

from . import OpenKAPSARC

remote = Group("remote", help="Access remote data sources.")


@remote.command()
@click.argument("server", default=None, required=False)
def demo(server):
    """Access the KAPSARC APIs at the given SERVER."""
    ok = OpenKAPSARC(server)

    print("List of all datasets:")
    for ds in ok.datasets():
        print(ds)

    print("\n\nDatasets with the 'iTEM' keyword:")
    for ds in ok.datasets(kw="item"):
        print(ds)

    print("\n\nData from one table in a branch in a repository:")
    print(ok.table("modal-split-of-freight-transport"))
