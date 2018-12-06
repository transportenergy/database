import pandas as pd
import requests
import requests_cache


requests_cache.install_cache('item')


class OpenKAPSARC:
    """Wrapper for the OpenKAPSARC APIs.

    The constructor takes the address of the server.
    """

    def __init__(self, server):
        self.server = server

    def endpoint(self, name, *args):
        """Call the API endpoint *name* with any additional *args*."""
        # Construct the URL
        r = requests.get(self.server + '/'.join(['', name] + list(args)))
        print(r.url)

        # All responses are in JSON
        return r.json()

    def datarepo(self, name=None):
        """Information about one or all data repositories.

        If *name* is None (the default), information on all repos is returned.
        """
        return self.endpoint('datarepo' if name else 'datarepos',
                             *filter(None, [name]))

    def table(self, repo, name):
        """Return data from table *name* in *repo* as a pd.DataFrame.

        Currently only the latest data on the master branch is returned.
        """
        response = self.endpoint('dataset', repo, 'master', name)

        # Parse table schema
        schema = response.pop('tschema')

        # Store column information according to the 'colorder' key
        columns = {}
        for col_info in schema.pop('columns'):

            if col_info['name'] == 'uhash':
                # FIXME the tschema includes information about a 'uhash'
                # column, but the data include only a '_id' column for each
                # row.
                col_info['name'] = '_id'

            columns[col_info.pop('colorder')] = col_info

        # Prepare a pd.Index for the data using the 'name' key
        col_index = pd.Index(col_info['name'] for _, col_info in
                             sorted(columns.items()))

        # Convert data to a pandas DataFrame
        data = pd.DataFrame(response.pop('data')) \
                 .reindex(columns=col_index)

        assert len(response) == 0

        return(data)


def demo(server):
    """Access the KAPSARC APIs at the given SERVER."""
    ok = OpenKAPSARC(server)

    print('List of all repositories:')
    for repo in ok.datarepo():
        print(repo['name'], ':', repo['id'])

    # commented: very verbose
    # print('\n\nInformation on one repository:')
    # print(ok.datarepo('ik2_open_data'))

    print('\n\nData from one table in a branch in a repository:')
    print(ok.table('ik2_open_data', 'modal_split_of_freight_transport'))
