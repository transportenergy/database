from json import JSONDecodeError
import logging
import sys

import pandas as pd
import requests
import requests_cache


from .common import config, paths


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


class Dataset:
    def __init__(self, data):
        self.data = data

    @property
    def id(self):
        return self.data['dataset']['dataset_id']

    @property
    def uid(self):
        return self.data['dataset']['dataset_uid']

    def __str__(self):
        return f"<Dataset {self.uid}: '{self.id}'>"


class OpenKAPSARC:
    """Wrapper for the OpenKAPSARC data API.

    See https://datasource.kapsarc.org/api/v2/console

    Parameters
    ----------
    server : str, optional
        Address of the server, e.g. `http://example.com:8888`.

    """
    ALL = sys.maxsize
    max = {'rows': 100}
    server = 'https://datasource.kapsarc.org/api/v2'

    # Alternate values include 'opendatasoft', which includes all public data
    # sets hosted by the software provider used by KAPSARC
    source = 'catalog'

    def __init__(self, server=None):
        if server:
            self.server = server

    def _modify_params(self, params):
        params.setdefault('apikey', config['api_key'])

    def endpoint(self, name, *args, params={}, **kwargs):
        """Call the API endpoint *name* with any additional *args*."""
        # Construct the URL
        self._modify_params(params)
        args = list(filter(None, args))
        url_parts = [self.server, self.source, name] + args

        # Make the request
        r = requests.get('/'.join(url_parts), params=params, **kwargs)
        log.debug(r.url)

        r.raise_for_status()

        if 'application/json' in r.headers['content-type']:
            # Response in JSON
            try:
                return r.json()
            except JSONDecodeErrors:
                log.error(r.content)
                raise
        else:
            log.debug(r.headers['content-type'])
            return r

    # _auto_endpoint = [
    #     'datasets'
    # ]
    #
    # def __getattr__(self, name):
    #     if name in self._auto_endpoint:
    #         return partial(self.endpoint, name)
    #     else:
    #         raise AttributeError(name)

    def datasets(self, dataset_id=None, *args, params={}, kw=None, **kwargs):
        if kw:
            if 'where' in params:
                raise ValueError("either give kw= or params={'where': …}")
            params['where'] = f"keyword LIKE '{kw}'"

        params.setdefault('rows', self.max['rows'])

        result = self.endpoint('datasets', dataset_id, *args, params=params,
                               **kwargs)

        if dataset_id:
            return Dataset(result)
        else:
            total_count = result['total_count']
            log.info('{} results; retrieved {}'
                     .format(total_count, len(result['datasets'])))

            return [Dataset(ds_json) for ds_json in result['datasets']]

    def table(self, dataset_id, cache=True, **kwargs):
        """Return data from dataset *name*.

        Currently only the latest data on the master branch is returned.

        Returns
        -------
        :class:`pandas.DataFrame`

        """
        # Make another request to get dataset information
        ds = self.datasets(dataset_id)

        cache_path = (paths['historical'] / ds.uid).with_suffix('.csv')
        log.info(f'Caching in {cache_path}')

        # Stream data
        kwargs['stream'] = True
        args = ['datasets', dataset_id, 'exports', 'csv']
        with self.endpoint(*args, **kwargs) as response:
            # Write content to file
            with open(cache_path, 'wb') as cache:
                for chunk in response.iter_content():
                    cache.write(chunk)

        # Parse and return
        return pd.read_csv(cache_path, sep=';')
