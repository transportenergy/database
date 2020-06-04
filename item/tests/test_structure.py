from item.structure import make_template


def test_make_template(tmp_path):
    make_template(output_path=tmp_path)

    # Produces 4 files
    for name in ["index.csv", "index.xlsx", "template.csv", "template.xlsx"]:
        assert (tmp_path / name).exists()

    assert 2493 + 1 == sum(1 for _ in open(tmp_path / "template.csv"))
    assert 2493 + 2 == sum(1 for _ in open(tmp_path / "index.csv"))
