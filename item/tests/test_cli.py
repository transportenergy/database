import pytest
from click.testing import CliRunner

import item.cli

COMMANDS = [
    # historical
    ("historical",),
    ("historical", "diagnostics"),
    ("historical", "phase1"),
    ("historical", "run-scripts"),
    # model
    ("model",),
    ("model", "process_raw"),
    ("model", "list_pairs"),
    # remote
    ("remote",),
    ("remote", "demo"),
    # Top-level
    ("debug",),
    ("mkdirs",),
    ("template",),
]


@pytest.mark.parametrize("cmd", COMMANDS)
def test_help(cmd):
    runner = CliRunner()
    result = runner.invoke(item.cli.main, list(cmd) + ["--help"])
    assert result.exit_code == 0


def test_debug():
    runner = CliRunner()
    result = runner.invoke(item.cli.main, ["debug"])
    assert not result.exception
