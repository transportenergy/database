import json
import logging
import sys
from datetime import datetime

import pandas as pd
import requests

from item.common import config, paths

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler(sys.stdout))


class APIError(Exception):
    """Error message returned by OpenKAPSARC."""

    pass


class Dataset:
    def __init__(self, data):
        self.data = data

    @property
    def id(self):
        return self.data["dataset"]["dataset_id"]

    @property
    def uid(self):
        return self.data["dataset"]["dataset_uid"]

    @property
    def records_count(self):
        return self.data["dataset"]["metas"]["default"]["records_count"]

    @property
    def data_processed(self):
        return datetime.fromisoformat(
            self.data["dataset"]["metas"]["default"]["data_processed"]
        )

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
    max = {"rows": 1000}
    server = "https://datasource.kapsarc.org/api/v2"

    # Alternate values include 'opendatasoft', which includes all public data
    # sets hosted by the software provider used by KAPSARC
    source = "catalog"

    def __init__(self, server=None, api_key=None):
        self.server = server or self.server
        self.api_key = api_key or config.get("api_key", None)

    def _modify_params(self, params):
        params.setdefault("apikey", self.api_key)

    def endpoint(self, name, *args, params={}, **kwargs):
        """Call the API endpoint *name* with any additional *args*."""
        # Construct the URL
        self._modify_params(params)
        args = list(filter(None, args))
        url_parts = [self.server, self.source, name] + args

        # Make the request
        r = requests.get("/".join(url_parts), params=params, **kwargs)
        log.debug(r.url)

        r.raise_for_status()

        if "application/json" in r.headers["content-type"]:
            # Response in JSON
            try:
                return r.json()
            except json.JSONDecodeErrors:
                log.error(r.content)
                raise
        else:
            log.debug(r.headers["content-type"])
            return r

    def datasets(self, dataset_id=None, *args, params={}, kw=None, **kwargs):
        if kw:
            if "where" in params:
                raise ValueError("either give kw= or params={'where': …}")
            params["where"] = f"keyword LIKE '{kw}'"

        result = self.endpoint("datasets", dataset_id, *args, params=params, **kwargs)

        if dataset_id:
            return Dataset(result)
        else:
            total_count = result["total_count"]
            log.info(
                "{} results; retrieved {}".format(total_count, len(result["datasets"]))
            )

            return [Dataset(ds_json) for ds_json in result["datasets"]]

    def table(self, dataset_id, cache=True, **kwargs):
        """Return data from dataset *name*.

        Currently only the latest data on the master branch is returned.

        Returns
        -------
        :class:`pandas.DataFrame`

        """
        # Make another request to get dataset information
        ds = self.datasets(dataset_id)

        # Cache path
        cache_path = (paths["historical"] / ds.uid).with_suffix(".csv")
        cache_is_valid = False
        log.info(f"Cache path {cache_path}")

        if cache and cache_path.exists():
            cache_is_valid = True

            # Check cache time
            cache_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
            if cache_time < ds.data_processed.replace(tzinfo=None):
                cache_is_valid = False
                log.info("…is outdated → remove")

            if cache_is_valid:
                # Check cache length
                with open(cache_path) as f:
                    cache_records = sum(1 for _ in f)

                if cache_records < ds.records_count:
                    cache_is_valid = False
                    log.info(
                        f"...has fewer records ({cache_records}) than "
                        f"source ({ds.records_count}) -> remove"
                    )

            if not cache_is_valid:
                cache_path.unlink()
            else:
                log.info("…is current; reading from file")
                return pd.read_csv(cache_path, sep=";")

        # Stream data
        kwargs["stream"] = True
        args = ["datasets", dataset_id, "exports", "csv"]
        with self.endpoint(*args, **kwargs) as response:
            # Write content to file
            with open(cache_path, "wb") as cache:
                for chunk in response.iter_content():
                    cache.write(chunk)

        # Parse and return
        return pd.read_csv(cache_path, sep=";")
