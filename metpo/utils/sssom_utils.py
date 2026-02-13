"""Helpers for parsing SSSOM metadata and identifiers."""

import re
from pathlib import Path

CURIE_MAP_LINE = re.compile(r"^#\s{0,4}([A-Za-z][\w.-]*):\s*(\S+)\s*$")


def strip_angle_brackets(identifier: str) -> str:
    """Return identifier without surrounding angle brackets."""
    text = str(identifier).strip()
    if text.startswith("<") and text.endswith(">"):
        return text[1:-1].strip()
    return text


def parse_sssom_curie_map(sssom_path: str | Path) -> dict[str, str]:
    """Parse ``# curie_map`` prefixes from an SSSOM TSV header."""
    curie_map: dict[str, str] = {}
    in_curie_map = False

    with Path(sssom_path).open(encoding="utf-8") as handle:
        for line in handle:
            if not line.startswith("#"):
                break

            text = line.rstrip("\n")
            if text.strip() == "# curie_map:":
                in_curie_map = True
                continue

            if in_curie_map:
                match = CURIE_MAP_LINE.match(text)
                if match:
                    prefix, expansion = match.groups()
                    curie_map[prefix] = expansion
                    continue

                # End curie_map block at the first non-entry comment line.
                if text.startswith("# ") and ":" in text:
                    in_curie_map = False

    return curie_map


def extract_prefix(identifier: str, curie_map: dict[str, str] | None = None) -> str | None:
    """
    Extract prefix from CURIE/IRI identifier.

    Preference order:
    1. CURIE prefix when object is already CURIE-like.
    2. curie_map expansion match when object is an IRI.
    3. conservative structural fallbacks (OBO IRIs).
    """
    text = strip_angle_brackets(identifier)
    if not text:
        return None

    lowered = text.lower()
    is_iri = lowered.startswith(("http://", "https://"))
    if ":" in text and not is_iri:
        return text.split(":", 1)[0]

    if curie_map:
        best_prefix: str | None = None
        best_len = -1
        for prefix, expansion in curie_map.items():
            if text.startswith(expansion) and len(expansion) > best_len:
                best_prefix = prefix
                best_len = len(expansion)
        if best_prefix is not None:
            return best_prefix

    if "/obo/" in text and "_" in text:
        return text.split("/obo/")[1].split("_")[0]

    return None
