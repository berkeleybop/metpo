"""Helpers for parsing SSSOM metadata and identifiers."""

import re
from pathlib import Path

CURIE_MAP_LINE = re.compile(r"^#\s{2,}([A-Za-z][\w.-]*):\s*(\S+)\s*$")

KNOWN_IRI_PREFIXES = {
    "biolink": "https://w3id.org/biolink/vocab/",
    "d3o": "https://purl.dsmz.de/schema/",
    "doi": "http://doi.org/",
    "bipon": "http://www.semanticweb.org/BiPON/",
}


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
                # End curie_map block at first normal metadata line like:
                # "# mapping_set_id: ...".
                if text.startswith("# ") and not text.startswith("#  "):
                    in_curie_map = False
                    continue

                match = CURIE_MAP_LINE.match(text)
                if match:
                    prefix, expansion = match.groups()
                    curie_map[prefix] = expansion
                    continue

                # Any non-matching comment line ends the curie_map block.
                in_curie_map = False

    return curie_map


def iri_to_curie(iri: str, known_iri_prefixes: dict[str, str] | None = None) -> tuple[str, str] | None:
    """Convert common IRI forms to CURIEs when safely possible."""
    prefixes = known_iri_prefixes or KNOWN_IRI_PREFIXES

    # OBO-style compact form, e.g. http://purl.obolibrary.org/obo/GO_0008152 -> GO:0008152
    if iri.startswith("http://purl.obolibrary.org/obo/"):
        local = iri.removeprefix("http://purl.obolibrary.org/obo/")
        if "_" in local:
            prefix, suffix = local.split("_", 1)
            if prefix and suffix:
                return f"{prefix}:{suffix}", f"http://purl.obolibrary.org/obo/{prefix}_"
        return None

    for prefix, base in prefixes.items():
        if iri.startswith(base):
            local = iri.removeprefix(base)
            if local:
                return f"{prefix}:{local}", base

    # Accept https variant for doi
    if iri.startswith("https://doi.org/"):
        local = iri.removeprefix("https://doi.org/")
        doi_base = prefixes.get("doi", "http://doi.org/")
        if local:
            return f"doi:{local}", doi_base

    return None


def normalize_object_id(
    raw_identifier: str,
    known_iri_prefixes: dict[str, str] | None = None,
) -> tuple[str, dict[str, str]]:
    """Normalize mapping object id to CURIE where possible, else plain IRI (no <>)."""
    clean = strip_angle_brackets(raw_identifier)
    if not clean:
        return clean, {}

    converted = iri_to_curie(clean, known_iri_prefixes=known_iri_prefixes)
    if converted is not None:
        curie, expansion = converted
        prefix = curie.split(":", 1)[0]
        return curie, {prefix: expansion}

    # Keep plain IRI if no safe CURIE normalization is available.
    return clean, {}


def extract_prefix(identifier: str, curie_map: dict[str, str] | None = None) -> str | None:
    """
    Extract prefix from CURIE/IRI identifier.

    Preference order:
    1. CURIE prefix when object is already CURIE-like.
    2. curie_map expansion match when object is an IRI.
    3. conservative structural fallbacks (OBO IRIs).
    """
    text = strip_angle_brackets(identifier)
    detected: str | None = None
    if not text:
        return detected

    lowered = text.lower()
    is_iri = lowered.startswith(("http://", "https://"))
    if ":" in text and not is_iri:
        detected = text.split(":", 1)[0]
    elif curie_map:
        best_prefix: str | None = None
        best_len = -1
        for prefix, expansion in curie_map.items():
            if text.startswith(expansion) and len(expansion) > best_len:
                best_prefix = prefix
                best_len = len(expansion)
        detected = best_prefix

    if detected is None:
        if "/obo/" in text and "_" in text:
            detected = text.split("/obo/")[1].split("_")[0]
        elif "doi.org" in lowered:
            detected = "doi"
        elif "biolink" in lowered:
            detected = "biolink"
        elif "purl.dsmz.de" in lowered:
            detected = "d3o"
        elif "mdatahub.org" in lowered:
            detected = "meo"
        elif "semanticweb.org/bipon/" in lowered:
            detected = "bipon"

    return detected
