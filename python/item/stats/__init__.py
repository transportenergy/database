from json import JSONDecodeError
import logging
import sys

import pandas as pd
import requests
import requests_cache


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler(sys.stdout))

requests_cache.install_cache('item')

try:
    import simplejson
    JSONDecodeErrors = (JSONDecodeError, simplejson.JSONDecodeError)
except ImportError:
    JSONDecodeErrors = (JSONDecodeError,)


class APIError(Exception):
    pass


class OpenKAPSARC:
    """Wrapper for the OpenKAPSARC APIs.

    The constructor takes the address of the server.
    """

    def __init__(self, server):
        self.server = server

    def endpoint(self, name, *args, params={}):
        """Call the API endpoint *name* with any additional *args*."""
        # Construct the URL
        r = requests.get(self.server + '/'.join(['', name] + list(args)),
                         params=params)
        log.info(r.url)

        r.raise_for_status()

        # All responses are in JSON
        try:
            return r.json()
        except JSONDecodeErrors:
            log.error(r.content)
            raise

    def datarepo(self, name=None):
        """Information about one or all data repositories.

        If *name* is None (the default), information on all repos is returned.
        """
        return self.endpoint('datarepo' if name else 'datarepos',
                             *filter(None, [name]))

    def table(self, repo, name, rows=None):
        """Return data from table *name* in *repo* as a pd.DataFrame.

        Currently only the latest data on the master branch is returned.
        """
        params = {}
        if rows:
            params['_limit'] = rows

        response = self.endpoint('dataset', repo, 'master', name,
                                 params=params)

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
    print(ok.table('ik2_open_data', 'modal_split_of_freight_transport', 10))
    print(ok.table('ik2_open_data', 'modal_split_of_freight_transport', 30))
