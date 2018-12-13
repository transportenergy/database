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
    """Error message returned by OpenKAPSARC."""
    pass


class OpenKAPSARC:
    """Wrapper for the OpenKAPSARC APIs.

    Parameters
    ----------
    server : str
        Address of the server, e.g. `http://example.com:8888`.

    """
    ALL = sys.maxsize

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
        """Return information about one or all data repositories.

        If *name* is None (the default), information on all repos is returned.
        """
        return self.endpoint('datarepo' if name else 'datarepos',
                             *filter(None, [name]))

    def table(self, repo, name, rows=None, offset=None):
        """Return data from table *name* in *repo*.

        Currently only the latest data on the master branch is returned.

        Parameters
        ----------
        rows : int, optional
            Number of rows to return. OpenKAPSARC returns 20 rows if this
            parameter is unspecified.
        offset : int, optional
            Number of rows to skip from the beginning of the table.

        Returns
        -------
        :class:`pandas.DataFrame`

        """
        params = {}
        if rows:
            params['_limit'] = int(rows)
        if offset:
            params['_offset'] = int(offset)

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
