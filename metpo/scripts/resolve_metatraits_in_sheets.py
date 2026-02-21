"""Resolve MetaTraits trait representations using METPO template-sheet mechanisms.

This script is intentionally non-SSSOM-first for operational use. It builds a
resolution table from:
- `src/templates/metpo-properties.tsv` synonym tuples + assay outcomes
- `src/templates/metpo_sheet.tsv` CURIE references in definition-source column

Output rows are designed as deterministic lookup artifacts for KG ingestion.

Coverage is reported at two levels:
- **METPO resolution**: card maps to specific METPO predicate pairs and class terms
- **Effective KGX coverage**: card carries usable external CURIEs (CHEBI, GO, EC)
  that can be used directly in KGX output, even without full METPO resolution
"""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import click

GENERIC_PROCESS_CURIES = {
    "GO:0008152",  # metabolism
    "GO:0009058",  # biosynthetic process
    "GO:0055114",  # oxidation-reduction process (often too broad/obsolete use)
    "GO:0040007",  # growth
    "GO:0009056",  # catabolic process
}

# MetaTraits base-category names that differ from METPO property synonym values.
# Maps normalized MetaTraits category -> normalized METPO synonym.
CATEGORY_ALIASES: dict[str, str] = {
    "enzyme activity": "physiology and metabolism.enzymes.[].activity",
}

RESOLVED_STATUSES = {
    "resolved",
    "resolved_with_notes",
    "resolved_nonchebi_with_notes",
}

# Prefixes whose CURIEs are directly usable in KGX without METPO mediation.
KGX_USABLE_PREFIXES = {"CHEBI", "GO", "EC"}

# Pattern for MetaTraits EC numbers like "EC3.2.1.52" (no colon after prefix).
_EC_NO_COLON_RE = re.compile(r"^EC\d+\.\d+")


def classify_external_curies(
    substrate_curies: tuple[str, ...],
    process_curies: tuple[str, ...],
) -> set[str]:
    """Return the set of KGX-usable prefix families present on a card.

    Recognises both standard CURIEs (``GO:0008152``) and MetaTraits-style
    EC numbers without a colon (``EC3.2.1.52``).
    """
    prefixes: set[str] = set()
    for curie in substrate_curies:
        pfx = curie.split(":")[0]
        if pfx in KGX_USABLE_PREFIXES:
            prefixes.add(pfx)
    for curie in process_curies:
        pfx = curie.split(":")[0]
        if pfx in KGX_USABLE_PREFIXES:
            prefixes.add(pfx)
        if _EC_NO_COLON_RE.match(curie):
            prefixes.add("EC")
    return prefixes


# Numeric unit strings from MetaTraits ``type`` field.
NUMERIC_TYPES = {"µm", "%", "ph", "% nacl (w/v)", "celsius", "genes", "bp", "score", "count"}


def classify_trait_format(
    is_composed: bool,
    trait_type: str,
) -> str:
    """Classify a MetaTraits card into one of four format categories.

    Returns one of:
    - ``composed_boolean``  -- base: substrate with true/false
    - ``uncomposed_boolean`` -- standalone boolean
    - ``uncomposed_factor``  -- standalone with categorical text value
    - ``uncomposed_numeric`` -- standalone with decimal + unit
    """
    if is_composed:
        return "composed_boolean"
    norm_type = trait_type.strip().lower()
    if norm_type == "factor":
        return "uncomposed_factor"
    if norm_type in NUMERIC_TYPES:
        return "uncomposed_numeric"
    # "boolean" and "binary" both map here
    return "uncomposed_boolean"


@dataclass(frozen=True)
class PropertyRef:
    """A METPO object property row used for MetaTraits predicate routing."""

    prop_id: str
    label: str


@dataclass(frozen=True)
class TraitCard:
    """MetaTraits card parsed from the scraper TSV."""

    card_id: str
    name: str
    trait_type: str
    description: str
    base_category: str
    substrate_label: str
    is_composed: bool
    process_curies: tuple[str, ...]
    substrate_curies: tuple[str, ...]
    trait_format: str = ""


def normalize_text(value: str) -> str:
    """Normalize free-text matching values to lower-case canonical form."""
    return value.strip().lower()


def parse_metatraits_cards(path: Path) -> list[TraitCard]:
    """Parse MetaTraits cards TSV produced by `fetch-metatraits`."""
    cards: list[TraitCard] = []

    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        for row in reader:
            raw_name = (row.get("name") or "").strip()
            if not raw_name:
                continue

            base_category = ""
            substrate_label = ""
            is_composed = False
            if ": " in raw_name:
                base_category, substrate_label = [part.strip() for part in raw_name.split(": ", 1)]
                is_composed = True

            raw_curies = row.get("ontology_curies") or ""
            all_curies = sorted({value.strip() for value in raw_curies.split(";") if value.strip()})
            process_curies = tuple(curie for curie in all_curies if not curie.startswith("CHEBI:"))
            substrate_curies = tuple(curie for curie in all_curies if curie.startswith("CHEBI:"))

            raw_type = (row.get("type") or "").strip()
            cards.append(
                TraitCard(
                    card_id=(row.get("card_id") or "").strip(),
                    name=raw_name,
                    trait_type=raw_type,
                    description=(row.get("description") or "").strip(),
                    base_category=base_category,
                    substrate_label=substrate_label,
                    is_composed=is_composed,
                    process_curies=process_curies,
                    substrate_curies=substrate_curies,
                    trait_format=classify_trait_format(is_composed, raw_type),
                )
            )

    return cards


def parse_metpo_curies(path: Path) -> dict[str, list[tuple[str, str]]]:
    """Parse metpo_sheet.tsv definition-source CURIEs into CURIE -> METPO targets."""
    curie_to_metpo: dict[str, list[tuple[str, str]]] = defaultdict(list)

    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.reader(stream, delimiter="\t")
        next(reader, None)
        next(reader, None)

        for row in reader:
            if len(row) <= 5:
                continue

            metpo_id = row[0].strip()
            label = row[1].strip()
            definition_sources = row[5].strip()
            if not metpo_id or not label or not definition_sources:
                continue

            for item in definition_sources.split("|"):
                source = item.strip()
                if not source:
                    continue
                if not re.match(r"^[A-Za-z][A-Za-z0-9_]+:\S+$", source):
                    continue
                if "://" in source:
                    continue
                curie_to_metpo[source].append((metpo_id, label))

    return curie_to_metpo


def parse_property_outcome_pairs(path: Path) -> dict[str, dict[str, PropertyRef | None]]:
    """Build base-category -> positive/negative METPO predicate pair map."""
    category_map: dict[str, dict[str, PropertyRef | None]] = defaultdict(
        lambda: {"positive": None, "negative": None}
    )

    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.reader(stream, delimiter="\t")
        next(reader, None)
        next(reader, None)

        for row in reader:
            if len(row) <= 11:
                continue
            if row[2].strip() != "owl:ObjectProperty":
                continue

            prop_id = row[0].strip()
            label = row[1].strip()
            synonym_tuple = row[9].strip() if len(row) > 9 else ""
            outcome = row[11].strip() if len(row) > 11 else ""
            if not prop_id or not synonym_tuple or outcome not in {"+", "-"}:
                continue

            synonyms = re.findall(r"oboInOwl:hasRelatedSynonym\s+'([^']+)'", synonym_tuple)
            if not synonyms:
                continue

            key = "positive" if outcome == "+" else "negative"
            ref = PropertyRef(prop_id=prop_id, label=label)
            for syn in synonyms:
                category_map[normalize_text(syn)][key] = ref

    return dict(category_map)


def parse_metpo_class_index(path: Path) -> dict[str, list[tuple[str, str]]]:
    """Build normalized name -> [(metpo_id, label)] from class labels and synonyms.

    Indexes rdfs:label (col 1), exact synonyms (col 9), and MetaTraits synonyms
    (col 17) for all ``owl:Class`` rows in the class template.
    """
    index: dict[str, list[tuple[str, str]]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.reader(stream, delimiter="\t")
        next(reader, None)
        next(reader, None)
        for row in reader:
            if len(row) < 3:
                continue
            metpo_id = row[0].strip()
            label = row[1].strip()
            if row[2].strip() != "owl:Class" or not metpo_id or not label:
                continue
            entry = (metpo_id, label)
            index[normalize_text(label)].append(entry)
            for col in (9, 17):
                if len(row) > col and row[col].strip():
                    for raw_syn in row[col].split("|"):
                        cleaned = raw_syn.strip()
                        if cleaned:
                            index[normalize_text(cleaned)].append(entry)
    return dict(index)


def parse_metpo_dataprop_index(path: Path) -> dict[str, list[tuple[str, str]]]:
    """Build normalized MetaTraits synonym -> [(metpo_id, label)] for owl:DataProperty rows."""
    index: dict[str, list[tuple[str, str]]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.reader(stream, delimiter="\t")
        next(reader, None)
        next(reader, None)
        for row in reader:
            if len(row) < 10:
                continue
            if row[2].strip() != "owl:DataProperty":
                continue
            prop_id = row[0].strip()
            label = row[1].strip()
            syn_tuple = row[9].strip()
            if not prop_id or not label or not syn_tuple:
                continue
            match = re.search(r"oboInOwl:hasRelatedSynonym\s+'([^']+)'", syn_tuple)
            if match:
                index[normalize_text(match.group(1))].append((prop_id, label))
    return dict(index)


def _resolve_composed_card(
    card: TraitCard,
    category_map: dict[str, dict[str, PropertyRef | None]],
    curie_to_metpo: dict[str, list[tuple[str, str]]],
    class_index: dict[str, list[tuple[str, str]]],
    curie_count: int,
    ext_curies_str: str,
) -> dict[str, str]:
    """Resolve a composed card (base: substrate) to an operational lookup row.

    Primary path: predicate pair + CHEBI/GO/EC object.
    Fallback: if the substrate label matches a METPO class, resolve via
    ``has_phenotype`` (e.g. ``cell color: yellow pigment`` →
    ``has_phenotype → METPO:1003030 yellow pigmented``).
    """
    category_key = normalize_text(card.base_category)
    category_key = CATEGORY_ALIASES.get(category_key, category_key)
    prop_pair = category_map.get(category_key, {"positive": None, "negative": None})
    positive = prop_pair.get("positive")
    negative = prop_pair.get("negative")

    matched_process_terms = sorted(
        {
            f"{metpo_id}|{label}"
            for curie in card.process_curies
            if curie not in GENERIC_PROCESS_CURIES
            for metpo_id, label in curie_to_metpo.get(curie, [])
        }
    )

    blocking_bits: list[str] = []
    note_bits: list[str] = []
    if positive is None:
        blocking_bits.append("missing_positive_predicate")
    if negative is None:
        blocking_bits.append("missing_negative_predicate")
    has_chebi = bool(card.substrate_curies)
    if not has_chebi and not matched_process_terms:
        blocking_bits.append("missing_chebi")
    if not matched_process_terms:
        note_bits.append("missing_process_term")
    if not has_chebi and matched_process_terms:
        note_bits.append("non_chebi_substrate")

    # Substrate-as-class fallback: when normal resolution fails, check if the
    # substrate label matches a METPO class (has_phenotype pattern).
    substrate_class_match = ""
    if blocking_bits:
        sub_key = normalize_text(card.substrate_label)
        cls_hits = class_index.get(sub_key, [])
        if cls_hits:
            substrate_class_match = "; ".join(sorted(f"{mid}|{ml}" for mid, ml in cls_hits))
            blocking_bits.clear()
            note_bits = ["has_phenotype_substrate"]

    if blocking_bits:
        status = "; ".join(blocking_bits + note_bits)
    elif "non_chebi_substrate" in note_bits:
        status = "resolved_nonchebi_with_notes"
    elif note_bits:
        status = "resolved_with_notes"
    else:
        status = "resolved"

    matched_col = substrate_class_match or "; ".join(matched_process_terms)

    return {
        "card_id": card.card_id,
        "trait_name": card.name,
        "mapping_kind": "composed",
        "base_category": card.base_category,
        "substrate_label": card.substrate_label,
        "predicate_positive_id": positive.prop_id if positive else "",
        "predicate_positive_label": positive.label if positive else "",
        "predicate_negative_id": negative.prop_id if negative else "",
        "predicate_negative_label": negative.label if negative else "",
        "substrate_chebi_ids": "; ".join(card.substrate_curies),
        "process_curies": "; ".join(card.process_curies),
        "matched_process_metpo": matched_col,
        "status": status,
        "trait_format": card.trait_format,
        "curie_count": str(curie_count),
        "usable_external_curies": ext_curies_str,
    }


def _resolve_base_card(
    card: TraitCard,
    curie_to_metpo: dict[str, list[tuple[str, str]]],
    class_index: dict[str, list[tuple[str, str]]],
    dataprop_index: dict[str, list[tuple[str, str]]],
    curie_count: int,
    ext_curies_str: str,
) -> dict[str, str]:
    """Resolve an uncomposed (base) card to an operational lookup row.

    Resolution cascade:
    1. CURIE match via definition-source column in metpo_sheet
    2. DatatypeProperty synonym match (numeric traits only)
    3. Class label / exact synonym / MetaTraits synonym match
    """
    matched_terms = sorted(
        {
            f"{metpo_id}|{label}"
            for curie in card.process_curies
            if curie not in GENERIC_PROCESS_CURIES
            for metpo_id, label in curie_to_metpo.get(curie, [])
        }
    )

    if not matched_terms:
        name_key = normalize_text(card.name)
        if card.trait_format == "uncomposed_numeric":
            dp_hits = dataprop_index.get(name_key, [])
            if dp_hits:
                matched_terms = sorted(f"{mid}|{ml}" for mid, ml in dp_hits)
        if not matched_terms:
            cls_hits = class_index.get(name_key, [])
            if cls_hits:
                matched_terms = sorted(f"{mid}|{ml}" for mid, ml in cls_hits)

    return {
        "card_id": card.card_id,
        "trait_name": card.name,
        "mapping_kind": "base",
        "base_category": "",
        "substrate_label": "",
        "predicate_positive_id": "",
        "predicate_positive_label": "",
        "predicate_negative_id": "",
        "predicate_negative_label": "",
        "substrate_chebi_ids": "",
        "process_curies": "; ".join(card.process_curies),
        "matched_process_metpo": "; ".join(matched_terms),
        "status": "resolved" if matched_terms else "missing_process_term",
        "trait_format": card.trait_format,
        "curie_count": str(curie_count),
        "usable_external_curies": ext_curies_str,
    }


def resolve_cards(
    cards: list[TraitCard],
    category_map: dict[str, dict[str, PropertyRef | None]],
    curie_to_metpo: dict[str, list[tuple[str, str]]],
    class_index: dict[str, list[tuple[str, str]]],
    dataprop_index: dict[str, list[tuple[str, str]]],
) -> list[dict[str, str]]:
    """Resolve each card to deterministic operational lookup rows."""
    resolved: list[dict[str, str]] = []

    for card in cards:
        ext_prefixes = classify_external_curies(card.substrate_curies, card.process_curies)
        ext_curies_str = "; ".join(sorted(ext_prefixes)) if ext_prefixes else ""
        curie_count = len(card.substrate_curies) + len(card.process_curies)

        if card.is_composed:
            resolved.append(
                _resolve_composed_card(
                    card, category_map, curie_to_metpo, class_index, curie_count, ext_curies_str
                )
            )
        else:
            resolved.append(
                _resolve_base_card(
                    card, curie_to_metpo, class_index, dataprop_index, curie_count, ext_curies_str
                )
            )

    return resolved


def write_resolution_table(rows: list[dict[str, str]], output_path: Path) -> None:
    """Write the deterministic operational lookup TSV."""
    fieldnames = [
        "card_id",
        "trait_name",
        "mapping_kind",
        "base_category",
        "substrate_label",
        "predicate_positive_id",
        "predicate_positive_label",
        "predicate_negative_id",
        "predicate_negative_label",
        "substrate_chebi_ids",
        "process_curies",
        "matched_process_metpo",
        "status",
        "trait_format",
        "curie_count",
        "usable_external_curies",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def _report_trait_format_section(rows: list[dict[str, str]]) -> list[str]:
    """Build the trait format breakdown table."""
    format_counts = Counter(row.get("trait_format", "") for row in rows)
    format_resolved = Counter(
        row.get("trait_format", "") for row in rows if row["status"] in RESOLVED_STATUSES
    )
    format_effective = Counter(
        row.get("trait_format", "")
        for row in rows
        if row["status"] in RESOLVED_STATUSES or row.get("usable_external_curies")
    )

    strategies = {
        "composed_boolean": "METPO predicate + CHEBI/GO/EC object",
        "uncomposed_boolean": "has_phenotype / capable_of + METPO class",
        "uncomposed_factor": "has_phenotype + METPO value class",
        "uncomposed_numeric": "METPO data property + xsd:decimal",
    }
    lines: list[str] = [
        "## Trait Format Breakdown\n",
        "\n",
        "| Format | Cards | METPO resolved | Effective KGX | KGX mapping strategy |\n",
        "|--------|-------|---------------|--------------|---------------------|\n",
    ]
    for fmt in [
        "composed_boolean",
        "uncomposed_boolean",
        "uncomposed_factor",
        "uncomposed_numeric",
    ]:
        n = format_counts.get(fmt, 0)
        lines.append(
            f"| `{fmt}` | {n} | {format_resolved.get(fmt, 0)}"
            f" | {format_effective.get(fmt, 0)} | {strategies.get(fmt, '')} |\n"
        )
    lines.append("\n")
    return lines


def _report_curie_section(rows: list[dict[str, str]]) -> list[str]:
    """Build the CURIE pattern distribution list."""
    buckets: Counter[str] = Counter()
    for row in rows:
        n = int(row.get("curie_count", "0"))
        if n == 0:
            buckets["0 CURIEs"] += 1
        elif n == 1:
            buckets["1 CURIE"] += 1
        elif n == 2:
            buckets["2 CURIEs"] += 1
        else:
            buckets["3+ CURIEs"] += 1
    lines: list[str] = ["## CURIE Pattern Distribution\n", "\n"]
    for bucket in ["0 CURIEs", "1 CURIE", "2 CURIEs", "3+ CURIEs"]:
        lines.append(f"- {bucket}: {buckets.get(bucket, 0)}\n")
    lines.append("\n")
    return lines


def _report_unresolved_categories(
    composed: list[dict[str, str]],
) -> list[str]:
    """Build the unresolved composed-categories table."""
    unresolved = [
        r for r in composed if r["status"] not in RESOLVED_STATUSES and r["base_category"]
    ]
    cat_total = Counter(r["base_category"] for r in unresolved)
    cat_ext = Counter(r["base_category"] for r in unresolved if r.get("usable_external_curies"))
    cat_preds = Counter(r["base_category"] for r in unresolved if r["predicate_positive_id"])
    cat_no_preds = Counter(r["base_category"] for r in unresolved if not r["predicate_positive_id"])

    lines: list[str] = [
        "## Unresolved Composed Categories\n",
        "\n",
        "| Category | Unresolved | Have predicates | Have ext CURIEs | Blocker |\n",
        "|----------|-----------|----------------|----------------|--------|\n",
    ]
    if not cat_total:
        lines.append("| (none) | 0 | — | — | — |\n")
    else:
        for cat, count in cat_total.most_common():
            ext = cat_ext.get(cat, 0)
            preds = cat_preds.get(cat, 0)
            no_preds = cat_no_preds.get(cat, 0)
            if no_preds == count:
                blocker = "need predicates"
            elif preds == count and ext == count:
                blocker = "missing CHEBI (ext CURIEs usable)"
            elif preds == count:
                blocker = "missing CHEBI"
            else:
                blocker = "mixed"
            lines.append(f"| `{cat}` | {count} | {preds} | {ext} | {blocker} |\n")
    lines.append("\n")
    return lines


def _report_truly_unmapped(truly_unmapped: list[dict[str, str]]) -> list[str]:
    """Build the truly-unmapped cards section."""
    lines: list[str] = ["## Truly Unmapped Cards\n", "\n"]
    if truly_unmapped:
        lines.append(
            f"{len(truly_unmapped)} cards have no METPO resolution and no usable"
            " external CURIEs (CHEBI, GO, EC):\n\n"
        )
        by_kind = Counter(row.get("base_category") or row["mapping_kind"] for row in truly_unmapped)
        for kind, count in by_kind.most_common():
            lines.append(f"- `{kind}`: {count}\n")
    else:
        lines.append("All cards have either METPO resolution or usable external CURIEs.\n")
    return lines


def write_report(rows: list[dict[str, str]], report_path: Path) -> None:
    """Write compact markdown coverage summary."""
    total = len(rows)
    composed = [row for row in rows if row["mapping_kind"] == "composed"]
    base = [row for row in rows if row["mapping_kind"] == "base"]
    resolved = [row for row in rows if row["status"] in RESOLVED_STATUSES]

    has_ext = [row for row in rows if row.get("usable_external_curies")]
    unresolved = [row for row in rows if row["status"] not in RESOLVED_STATUSES]
    unresolved_with_ext = [row for row in unresolved if row.get("usable_external_curies")]
    effective_count = len(resolved) + len(unresolved_with_ext)
    truly_unmapped = [row for row in unresolved if not row.get("usable_external_curies")]

    status_counts = Counter(row["status"] for row in rows)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "# MetaTraits In-Sheet Resolution Report\n",
        "\n",
        "## Summary\n",
        "\n",
        f"- Total cards: {total}\n",
        f"- Base cards: {len(base)}\n",
        f"- Composed cards: {len(composed)}\n",
        f"- Fully resolved (METPO): {len(resolved)}\n",
        f"- Cards with usable external CURIEs (CHEBI/GO/EC): {len(has_ext)}\n",
        f"- **Effective KGX coverage: {effective_count}/{total}"
        f" ({effective_count * 100 // total}%)**\n",
        f"- Truly unmapped (no METPO, no external CURIEs): {len(truly_unmapped)}\n",
        "\n",
    ]

    lines.extend(_report_trait_format_section(rows))
    lines.extend(_report_curie_section(rows))

    lines.extend(["## METPO Resolution Status Counts\n", "\n"])
    for status, count in status_counts.most_common():
        lines.append(f"- `{status}`: {count}\n")
    lines.append("\n")

    lines.extend(_report_unresolved_categories(composed))
    lines.extend(_report_truly_unmapped(truly_unmapped))

    report_path.write_text("".join(lines), encoding="utf-8")


@click.command()
@click.option(
    "--metatraits-cards",
    "-m",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="MetaTraits cards TSV from fetch-metatraits",
)
@click.option(
    "--metpo-sheet",
    "-t",
    type=click.Path(exists=True, path_type=Path),
    default=Path("src/templates/metpo_sheet.tsv"),
    show_default=True,
)
@click.option(
    "--properties-sheet",
    "-p",
    type=click.Path(exists=True, path_type=Path),
    default=Path("src/templates/metpo-properties.tsv"),
    show_default=True,
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=Path("data/mappings/metatraits_in_sheet_resolution.tsv"),
    show_default=True,
)
@click.option(
    "--report",
    "-r",
    type=click.Path(path_type=Path),
    default=Path("data/mappings/metatraits_in_sheet_resolution_report.md"),
    show_default=True,
)
def main(
    metatraits_cards: Path,
    metpo_sheet: Path,
    properties_sheet: Path,
    output: Path,
    report: Path,
) -> None:
    """Resolve MetaTraits catalog traits to in-sheet METPO operational mapping hints."""
    cards = parse_metatraits_cards(metatraits_cards)
    curie_to_metpo = parse_metpo_curies(metpo_sheet)
    category_map = parse_property_outcome_pairs(properties_sheet)
    class_index = parse_metpo_class_index(metpo_sheet)
    dataprop_index = parse_metpo_dataprop_index(properties_sheet)

    rows = resolve_cards(cards, category_map, curie_to_metpo, class_index, dataprop_index)
    write_resolution_table(rows, output)
    write_report(rows, report)

    resolved_count = sum(1 for row in rows if row["status"] in RESOLVED_STATUSES)
    ext_count = sum(
        1
        for row in rows
        if row["status"] not in RESOLVED_STATUSES and row.get("usable_external_curies")
    )
    effective = resolved_count + ext_count
    click.echo(f"Resolved (METPO): {resolved_count}/{len(rows)} traits")
    click.echo(f"Effective KGX coverage: {effective}/{len(rows)} ({effective * 100 // len(rows)}%)")
    click.echo(f"Wrote {output}")
    click.echo(f"Wrote {report}")


if __name__ == "__main__":
    main()
