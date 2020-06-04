import pytest

from item.common import paths
from item.model.dimensions import check, generate, list_pairs


@pytest.mark.skip("Requires synthetic model data.")
def test_list_pairs(item_tmp_dir):
    list_pairs(
        paths["data"] / "model" / "dimensions" / "quantities.tsv",
        paths["model"] / "pairs.txt",
    )


def test_generate():
    generate()


@pytest.mark.skip("Requires synthetic model data.")
def test_check(item_tmp_dir):
    dims = generate()
    check(dims, item_tmp_dir / "check.tsv")
