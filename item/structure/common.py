import logging
from functools import lru_cache

from item.structure.sdmx import generate

log = logging.getLogger(__name__)


@lru_cache()
def column_name(id: str) -> str:
    """Return a human-readable name for a dimension in the historical DSD."""
    try:
        value = dict(VARIABLE="Variable", YEAR="Year", ID="ID")[id]
        log.warning(f"Deprecated dimension id: {repr(id)}")
        return value
    except KeyError:
        return (
            generate()
            .structure["HISTORICAL"]
            .dimensions.get(id.upper())
            .concept_identity.name.localized_default()
        )
