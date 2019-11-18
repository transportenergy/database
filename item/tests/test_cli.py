from click.testing import CliRunner

import item.cli


def test_debug():
    runner = CliRunner()
    result = runner.invoke(item.cli.main, ['debug'])
    assert not result.exception
