from os.path import join

from item.common import paths
from item.model.dimensions import check, generate, list_pairs


def test_list_pairs(item_tmp_dir):
    list_pairs(
        join(paths['data'], 'model', 'dimensions', 'quantities.tsv'),
        join(paths['model'], 'pairs.txt'))


def test_generate():
    generate()


def test_check(item_tmp_dir):
    dims = generate()
    check(dims, join(item_tmp_dir, 'check.tsv'))
