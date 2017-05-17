from click.testing import CliRunner

import item.__main__


def test_debug():
    runner = CliRunner()
    result = runner.invoke(item.__main__.main, ['debug'])
    assert not result.exception
