"""Deterministic SOA file matcher for financial reconciliation."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CARRIER_DELIMITER = "-"
FILE_DELIMITER = "&"
_MAX_SPACES = 1
_XLSX_SUFFIX = ".xlsx"


def _truncate_at_spaces(value: str, max_spaces: int = _MAX_SPACES) -> str:
    """Keep text up to *max_spaces* blank spaces; consecutive spaces count as one."""
    space_count = 0
    chars: list[str] = []
    in_space_run = False

    for char in value:
        if char == " ":
            if not in_space_run:
                space_count += 1
                if space_count > max_spaces:
                    break
            chars.append(char)
            in_space_run = True
        else:
            chars.append(char)
            in_space_run = False

    return "".join(chars).strip()


def _match_key(value: str, delimiter: str) -> str:
    """Normalize a carrier or filename value into a deterministic match key."""
    head = value.split(delimiter, maxsplit=1)[0]
    return _truncate_at_spaces(head)


def find_soa_file(carrier_name: str, soa_directory: str | Path) -> Path | None:
    """Locate an SOA ``.xlsx`` file for *carrier_name* under *soa_directory*.

    Keys are built deterministically:

    1. Read up to the first ``-`` (carrier) or ``&`` (filename stem).
    2. Within that segment, keep text until at most two blank spaces are
       seen; runs of consecutive spaces count as a single space.
    3. Compare keys with strict equality.

    Example::

        Comoretel Holdings - NA0419              → Comoretel Holdings
        Comoretel Holdings & Aiwo SOA.xlsx       → Comoretel Holdings
    """
    directory = Path(soa_directory)

    if not directory.is_dir():
        logger.warning("SOA directory not found or is not a directory: %s", directory)
        return None

    carrier_key = _match_key(carrier_name, CARRIER_DELIMITER)
    matches: list[Path] = []

    for path in directory.iterdir():
        if not path.is_file() or path.suffix.casefold() != _XLSX_SUFFIX:
            continue
        if _match_key(path.stem, FILE_DELIMITER) == carrier_key:
            matches.append(path)

    if not matches:
        logger.warning(
            "No .xlsx file found matching carrier key '%s' (from '%s') in %s",
            carrier_key,
            carrier_name,
            directory,
        )
        return None

    matches.sort()

    if len(matches) > 1:
        logger.warning(
            "Multiple .xlsx files match carrier key '%s' in %s; returning %s",
            carrier_key,
            directory,
            matches[0],
        )

    return matches[0]
