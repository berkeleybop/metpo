"""Resolve MetaTraits trait representations using METPO template-sheet mechanisms.

This script is intentionally non-SSSOM-first for operational use. It builds a
resolution table from:
- `src/templates/metpo-properties.tsv` synonym tuples + assay outcomes
- `src/templates/metpo_sheet.tsv` CURIE references in definition-source column

Output rows are designed as deterministic lookup artifacts for KG ingestion.
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

            cards.append(
                TraitCard(
                    card_id=(row.get("card_id") or "").strip(),
                    name=raw_name,
                    trait_type=(row.get("type") or "").strip(),
                    description=(row.get("description") or "").strip(),
                    base_category=base_category,
                    substrate_label=substrate_label,
                    is_composed=is_composed,
                    process_curies=process_curies,
                    substrate_curies=substrate_curies,
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

            synonym_match = re.search(r"oboInOwl:hasRelatedSynonym\s+'([^']+)'", synonym_tuple)
            if not synonym_match:
                continue

            category = normalize_text(synonym_match.group(1))
            key = "positive" if outcome == "+" else "negative"
            category_map[category][key] = PropertyRef(prop_id=prop_id, label=label)

    return dict(category_map)


def resolve_cards(
    cards: list[TraitCard],
    category_map: dict[str, dict[str, PropertyRef | None]],
    curie_to_metpo: dict[str, list[tuple[str, str]]],
) -> list[dict[str, str]]:
    """Resolve each card to deterministic operational lookup rows."""
    resolved: list[dict[str, str]] = []

    for card in cards:
        if card.is_composed:
            category_key = normalize_text(card.base_category)
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
            if not card.substrate_curies:
                blocking_bits.append("missing_chebi")
            if not matched_process_terms:
                note_bits.append("missing_process_term")

            if blocking_bits:
                status = "; ".join(blocking_bits + note_bits)
            elif note_bits:
                status = "resolved_with_notes"
            else:
                status = "resolved"

            resolved.append(
                {
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
                    "matched_process_metpo": "; ".join(matched_process_terms),
                    "status": status,
                }
            )
            continue

        matched_terms = sorted(
            {
                f"{metpo_id}|{label}"
                for curie in card.process_curies
                if curie not in GENERIC_PROCESS_CURIES
                for metpo_id, label in curie_to_metpo.get(curie, [])
            }
        )
        resolved.append(
            {
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
            }
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
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_report(rows: list[dict[str, str]], report_path: Path) -> None:
    """Write compact markdown coverage summary."""
    total = len(rows)
    composed = [row for row in rows if row["mapping_kind"] == "composed"]
    base = [row for row in rows if row["mapping_kind"] == "base"]
    resolved = [row for row in rows if row["status"] in {"resolved", "resolved_with_notes"}]

    status_counts = Counter(row["status"] for row in rows)
    unresolved_categories = Counter(
        row["base_category"]
        for row in composed
        if row["status"] not in {"resolved", "resolved_with_notes"} and row["base_category"]
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# MetaTraits In-Sheet Resolution Report\n",
        "\n",
        "## Summary\n",
        "\n",
        f"- Total cards: {total}\n",
        f"- Base cards: {len(base)}\n",
        f"- Composed cards: {len(composed)}\n",
        f"- Fully resolved cards: {len(resolved)}\n",
        "\n",
        "## Status Counts\n",
        "\n",
    ]

    for status, count in status_counts.most_common():
        lines.append(f"- `{status}`: {count}\n")

    lines.extend(["\n", "## Unresolved Composed Categories\n", "\n"])
    if not unresolved_categories:
        lines.append("- none\n")
    else:
        for category, count in unresolved_categories.most_common():
            lines.append(f"- `{category}`: {count}\n")

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

    rows = resolve_cards(cards, category_map, curie_to_metpo)
    write_resolution_table(rows, output)
    write_report(rows, report)

    resolved_count = sum(1 for row in rows if row["status"] in {"resolved", "resolved_with_notes"})
    click.echo(f"Resolved {resolved_count}/{len(rows)} traits")
    click.echo(f"Wrote {output}")
    click.echo(f"Wrote {report}")


if __name__ == "__main__":
    main()
