from itertools import product

import sdmx

from item.sdmx import generate
from item.structure import column_name, make_template


def test_column_name(caplog):
    # Correctly retrieves the name of a Concept from the data structures
    assert column_name("VEHICLE") == "Vehicle type"

    # Warning is logged for deprecated IDs
    assert column_name("YEAR") == "Year"
    assert "Deprecated dimension id: 'YEAR'" in caplog.messages


def test_make_template(tmp_path):
    make_template(output_path=tmp_path)

    # Produces 4 files
    for base, suffix in product(["full", "condensed", "index"], [".csv", ".xlsx"]):
        assert (tmp_path / base).with_suffix(suffix).exists()

    # Files have the expected length
    expected_keys = 6162
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

    assert 3 == len(sm.constraint["PRICE_FUEL"].data_content_keys)
