from itertools import product

import sdmx

from item.structure import generate, make_template


def test_make_template(tmp_path):
    make_template(output_path=tmp_path)

    # Produces 4 files
    for base, suffix in product(["full", "condensed", "index"], [".csv", ".xlsx"]):
        assert (tmp_path / base).with_suffix(suffix).exists()

    # Files have the expected length
    expected_keys = 20763
    assert expected_keys + 1 == sum(1 for _ in open(tmp_path / "condensed.csv"))
    assert expected_keys + 1 == sum(1 for _ in open(tmp_path / "full.csv"))
    assert expected_keys + 2 == sum(1 for _ in open(tmp_path / "index.csv"))


def test_sdmx_roundtrip(tmp_path):
    path = tmp_path / "structure.xml"

    # Structure can be written
    with open(path, "wb") as f:
        f.write(sdmx.to_xml(generate(), pretty_print=True))

    # Structure can be read
    sm = sdmx.read_sdmx(path)

    # One CubeRegion
    assert 1 == len(sm.constraint["PRICE_FUEL"].data_content_region)

    # One dimension with a MemberSelection
    cr = sm.constraint["PRICE_FUEL"].data_content_region[0]
    assert {"FUEL"} == set(d.id for d in cr.member.keys())

    # 3 values in the MemberSelection
    assert 3 == len(cr.member["FUEL"].values)
