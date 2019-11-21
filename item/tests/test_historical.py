from item.common import paths
from item.historical import input_file


def test_input_file(item_tmp_dir):
    # Create some temporary files in any order
    files = [
        'T001_foo.csv',
        'T001_bar.csv',
    ]
    for name in files:
        (paths['historical input'] / name).write_text('(empty)')

    # input_file retrieves the last-sorted file:
    assert input_file(1) == paths['historical input'] / 'T001_foo.csv'