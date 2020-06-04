import logging
import logging.config
import os
from os.path import abspath, join
from pathlib import Path
from warnings import filterwarnings

import yaml
from pkg_resources import resource_filename  # noqa: F401

# Occurs with pandas 0.20 and xarray 0.9.1
filterwarnings(
    "ignore",
    message=".*pandas.tslib module is deprecated.*",
    module="xarray.core.formatting",
)

# Various paths to data
paths = {
    # Package data
    "data": Path(resource_filename(__name__, "data")).resolve(),
}

if not paths["data"].exists():
    # Workaround for editable pip install
    paths["data"] = Path(__file__).parent / "data"


config = {}
_logger = None


def load_config(path=None):
    """Load configuration."""
    global config
    _path = abspath("." if path is None else path)
    try:
        with open(join(_path, "item_config.yaml")) as f:
            result = yaml.safe_load(f)
            config["_from_file"] = result
            config.update(result)
            config["_filename"] = "item_config.yaml"
    except FileNotFoundError:
        if path is not None:
            raise


def init(path=None):
    load_config(path)
    init_paths()


def init_log(verbose=True):
    with open(Path(__file__).with_name("logging.yaml")) as f:
        log_config = yaml.safe_load(f)

    # Set up the log file
    log_config["handlers"]["file_handler"]["filename"] = paths["log"] / "item.log"

    # Activate verbose output
    if verbose:
        log_config["handlers"]["console"]["level"] = "DEBUG"

    # Configure the loggers
    logging.config.dictConfig(log_config)

    global _logger
    _logger = logging.getLogger("item")


def init_paths(**kwargs):
    global config
    config["_cli"] = kwargs

    # Configure paths
    path_config = config.get("path", {})
    path_config.update(kwargs)

    def init_path(name, default, mkdir=False):
        full_path = Path(path_config.get(name, default)).resolve().expanduser()
        paths[name] = full_path

    init_path("cache", ".cache")

    init_path("log", ".")

    init_path("model", ".")
    init_path("model raw", paths["model"] / "raw")
    init_path("model processed", paths["model"] / "processed")
    init_path("model database", paths["model"] / "database")
    init_path("models-1", paths["model database"] / "1.csv")
    init_path("models-2", paths["model database"] / "2.csv")

    init_path("historical", Path(__file__).parent / "data" / "historical")
    init_path("historical input", paths["historical"] / "input")
    init_path("output", ".")

    init_path("plot", join(".", "plot"))


def log(*items, level=logging.INFO):
    """Write a collection of *items* to the log."""
    if _logger is None:
        init_log()
    if level == logging.INFO:
        _logger.info(*items)
    elif level == logging.DEBUG:
        _logger.debug(*items)


def make_database_dirs(path, dry_run):
    # Don't use log() here, as it prematurely causes the logfile to be opened
    print("Creating database directories in: {}".format(path))

    dirs = [
        ("model", "database"),
        ("model", "processed"),
        ("model", "raw"),
        ("historical",),
        ("historical", "input"),
        ("output",),
    ]
    dirs = [path] + [join(path, *d) for d in dirs]

    for name in dirs:
        if dry_run:
            log("  " + name)
        else:
            os.makedirs(name, exist_ok=True)
