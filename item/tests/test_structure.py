import logging
import re
from collections.abc import Iterator
from itertools import product
from typing import TYPE_CHECKING

import pytest
import sdmx
from sdmx.message import StructureMessage

from item.structure import generate, make_template
from item.structure.sdmx import make_iamc_variable_cl

if TYPE_CHECKING:
    from pathlib import Path

log = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def item_sdmx_structures() -> Iterator[StructureMessage]:
    """The results of :func:`item.structure.generate` as a fixture."""
    yield generate()


@pytest.mark.parametrize(
    "target, exp_len",
    (
        ("ACTIVITY", 906),
        # ("ACTIVITY_VEHICLE", 0),
        ("EMISSIONS", 17760),
        ("ENERGY_INTENSITY", 248),
        ("ENERGY", 720),
        ("GDP", 1),
        ("LOAD_FACTOR", 25),
        ("POPULATION", 1),
        # ("PRICE_FUEL", 0),
        # ("PRICE_POLLUTANT", 0),
        ("SALES", 46),
        ("STOCK", 46),
    ),
)
def test_make_iamc_variable_cl(
    tmp_path: "Path", item_sdmx_structures: StructureMessage, target: str, exp_len: int
) -> None:
    def strip_t(value: str) -> str:
        return re.sub(r"\|_T", "", value)

    result = make_iamc_variable_cl(item_sdmx_structures, target, format_id=strip_t)

    assert exp_len == len(result)

    # Structure can be written
    path = tmp_path.joinpath("output.xml")
    with open(path, "wb") as f:
        f.write(sdmx.to_xml(item_sdmx_structures, pretty_print=True))
    log.info(f"Wrote {path}")


def test_make_template(tmp_path) -> None:
    make_template(output_path=tmp_path)

    # Produces 4 files
    for base, suffix in product(["full", "condensed", "index"], [".csv", ".xlsx"]):
        assert (tmp_path / base).with_suffix(suffix).exists()

    # Files have the expected length
    expected_keys = 20763
    assert expected_keys + 1 == sum(1 for _ in open(tmp_path / "condensed.csv"))
    assert expected_keys + 1 == sum(1 for _ in open(tmp_path / "full.csv"))
    assert expected_keys + 2 == sum(1 for _ in open(tmp_path / "index.csv"))


def test_sdmx_roundtrip(tmp_path, item_sdmx_structures: StructureMessage) -> None:
    path = tmp_path / "structure.xml"

    # Structure can be written
    with open(path, "wb") as f:
        f.write(sdmx.to_xml(item_sdmx_structures, pretty_print=True))

    # Structure can be read
    sm = sdmx.read_sdmx(path)
    assert isinstance(sm, StructureMessage)

    # One CubeRegion
    assert 1 == len(sm.constraint["PRICE_FUEL"].data_content_region)

    # One dimension with a MemberSelection
    cr = sm.constraint["PRICE_FUEL"].data_content_region[0]
    assert {"FUEL"} == set(d.id for d in cr.member.keys())

    # 3 values in the MemberSelection
    assert 3 == len(cr.member["FUEL"].values)
