import logging
from collections import ChainMap
from datetime import datetime
from functools import lru_cache
from typing import TYPE_CHECKING, List, cast
import sdmx
import pandas as pd
import io
import yaml
from item.common import paths
import openpyxl
import re

from transport_data import config as tdc_config
from transport_data import adb
import os

import numpy as np
import sdmx.message as msg
from sdmx import Client
from sdmx.model import common as m
from sdmx.model.v21 import (
    DataKey,
    DataKeySet,
    DataSet,
    MeasureDimension,
    MemberSelection,
    MemberValue,
    Observation,
    PrimaryMeasure,
)

from item.structure import base
from transport_data.config import user_data_path

from typing import Optional

def get_sdmx_from_file(fetch_info:dict) -> pd.DataFrame:
    """Retrieve data from a local SDMX XML file and convert it to a pandas DataFrame.

    Arguments
    ---------
    file_path : str
        Path to the local SDMX XML file.

    Returns
    -------
    pandas.DataFrame
    """
    source = fetch_info.get('source', '')
    resource_id = fetch_info.get('resource_id', '')
    print("resource_id", source)
    whole_path=""
    if source =="ADB":
        modified_ID=f"{"DataSet_ADB_"}{resource_id}{".xml"}"
        whole_path=os.path.join(user_data_path(), "transport-data", "transport-data", "local", "ADB", modified_ID)
    print(whole_path)
    # Read the XML file
    with open(whole_path, 'rb') as file:
        xml_content = file.read()

    # Create a file-like object from the bytes content
    xml_file_like = io.BytesIO(xml_content)

    # Parse the XML content
    msg = sdmx.read_sdmx(xml_file_like)

    # Convert to pd.DataFrame, preserving attributes
    df = sdmx.to_pandas(msg, attributes="dgso")
    index_cols = df.index.names

    # Reset index, use categoricals
    return df.reset_index().astype({c: "category" for c in index_cols})

def check_ADB_SDMX():
    with open(paths["data"] / "historical" / "sources.yaml") as f:
    #: The current version of the file is always accessible at
    #: https://github.com/transportenergy/metadata/blob/master/historical/sources.yaml
        SOURCES = yaml.safe_load(f)
    unique_wb_values = set()
    for source in SOURCES:
        if 'fetch' in SOURCES[source] and "file_path" in SOURCES[source]['fetch']:
            match=re.search(r'DataSet_ADB_(\w+)', SOURCES[source]['fetch']['file_path'])
            if match:
                unique_wb_values.add(match.group(1))
    print(unique_wb_values)
    file_path_ECONOMIES = os.path.join(tdc_config.user_data_path(), "transport-data","transport-data", "local", "ADB", "Codelist_ADB_ECONOMY.xml")
    if os.path.exists(file_path_ECONOMIES):
        return  # Do nothing if the file exists
    else:
    # If the file does not exist, execute the commands
        try:
            for wb in unique_wb_values:
                adb.fetch(wb)
                if wb == "TAS":
                    sheets_to_erase = ["TAS-FRA-026", "TAS-FRA-027", "TAS-FRA-028","TAS-FRA-029", "TAS-PAT-018"]
                    workbook_path = os.path.join(tdc_config.user_data_path(), "transport-data", "transport-data", "Cache", "adb", "ATO Workbook (TRANSPORT ACTIVITY & SERVICES (TAS)).xlsx")                    
                    workbook = openpyxl.load_workbook(workbook_path)
                    os.remove(workbook_path)
                    for sheet in sheets_to_erase:
                        if sheet in workbook.sheetnames:
                            workbook.remove(workbook[sheet])
                    workbook.save(workbook_path)
                adb.convert(wb)

        except:
            logging.error("ADB data fetch and conversion failed.")
            return