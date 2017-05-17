from os.path import join

from item.common import log


def test_log(item_tmp_dir):
    log('Hello')
    with open(join(item_tmp_dir, 'item.log')) as f:
        assert f.read() == 'Hello\n'
