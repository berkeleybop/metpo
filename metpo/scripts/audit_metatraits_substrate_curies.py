"""Audit MetaTraits substrate CURIEs against authoritative CHEBI labels via OAK.

Cross-references MetaTraits' own CHEBI assignments with KG-Microbe compound
mappings and flags label mismatches, missing CURIEs, and disagreements between
sources.

Outputs a substrate-level audit TSV and a markdown summary report.
"""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import click
from oaklib import get_adapter


@dataclass
class SubstrateRecord:
    """Aggregated record for one unique substrate label."""

    substrate_label: str
    card_ids: list[str] = field(default_factory=list)
    metatraits_chebi_ids: set[str] = field(default_factory=set)


@dataclass
class AuditRow:
    """One row of the audit output TSV."""

    substrate_label: str
    card_count: int
    example_cards: str
    metatraits_chebi_id: str
    chebi_label_from_oak: str
    label_match: str
    kgm_chebi_id: str
    kgm_chebi_label: str
    kgm_label_match: str
    kgm_matches_metatraits: str
    audit_status: str


AUDIT_FIELDNAMES = [
    "substrate_label",
    "card_count",
    "example_cards",
    "metatraits_chebi_id",
    "chebi_label_from_oak",
    "label_match",
    "kgm_chebi_id",
    "kgm_chebi_label",
    "kgm_label_match",
    "kgm_matches_metatraits",
    "audit_status",
]


def normalize_text(value: str) -> str:
    """Normalize free-text to lower-case stripped canonical form."""
    return value.strip().lower()


def parse_cards_to_substrates(cards_path: Path) -> dict[str, SubstrateRecord]:
    """Parse metatraits_cards.tsv and aggregate by unique substrate label.

    Uses the same split logic as resolve_metatraits_in_sheets.py: composed
    cards have ": " separating base_category from substrate_label, and CHEBI:
    prefixed CURIEs in ontology_curies are substrate CURIEs.
    """
    substrates: dict[str, SubstrateRecord] = {}

    with cards_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        for row in reader:
            raw_name = (row.get("name") or "").strip()
            if not raw_name or ": " not in raw_name:
                continue

            _base_category, substrate_label = [part.strip() for part in raw_name.split(": ", 1)]
            if not substrate_label:
                continue

            card_id = (row.get("card_id") or "").strip()
            raw_curies = row.get("ontology_curies") or ""
            chebi_curies = {
                c.strip() for c in raw_curies.split(";") if c.strip().startswith("CHEBI:")
            }

            norm = normalize_text(substrate_label)
            if norm not in substrates:
                substrates[norm] = SubstrateRecord(substrate_label=substrate_label)
            rec = substrates[norm]
            rec.card_ids.append(card_id)
            rec.metatraits_chebi_ids.update(chebi_curies)

    return substrates


def load_kgm_mappings(kgm_path: Path) -> dict[str, tuple[str, str]]:
    """Load KG-Microbe compound mappings into {normalized_original: (chebi_id, chebi_label)}.

    Uses the ``mapped`` column for the CHEBI CURIE and ``chebi_label`` for the
    label.  Only rows where ``mapped`` starts with ``CHEBI:`` are included.
    When multiple rows exist for the same normalized original, the first is kept.
    """
    mappings: dict[str, tuple[str, str]] = {}

    with kgm_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        for row in reader:
            original = (row.get("original") or "").strip()
            mapped = (row.get("mapped") or "").strip()
            chebi_label = (row.get("chebi_label") or "").strip()

            if not original or not mapped.startswith("CHEBI:"):
                continue

            norm = normalize_text(original)
            if norm not in mappings:
                mappings[norm] = (mapped, chebi_label)

    return mappings


def verify_chebi_labels_via_oak(
    chebi_ids: set[str],
) -> dict[str, str | None]:
    """Look up authoritative CHEBI labels for a set of CURIEs using OAK.

    Returns {curie: label_or_None}.
    """
    adapter = get_adapter("sqlite:obo:chebi")
    labels: dict[str, str | None] = {}

    for curie, label in adapter.labels(chebi_ids):
        labels[curie] = label

    # Ensure every requested CURIE has an entry (None if not found)
    for curie in chebi_ids:
        if curie not in labels:
            labels[curie] = None

    return labels


def compare_labels(substrate_label: str, chebi_label: str | None) -> str:
    """Compare substrate label against CHEBI label. Returns match status."""
    if chebi_label is None:
        return "no_oak_label"
    norm_sub = normalize_text(substrate_label)
    norm_chebi = normalize_text(chebi_label)
    if norm_sub == norm_chebi:
        return "exact"
    # Case-insensitive is the same as exact here since both are lowered,
    # but check original casing
    if substrate_label.strip().lower() == chebi_label.strip().lower():
        return "exact"
    if substrate_label.strip() != chebi_label.strip() and norm_sub == norm_chebi:
        return "case_insensitive"
    return "mismatch"


def build_audit_rows(
    substrates: dict[str, SubstrateRecord],
    chebi_labels: dict[str, str | None],
    kgm_mappings: dict[str, tuple[str, str]],
) -> list[AuditRow]:
    """Combine all data sources into audit rows."""
    rows: list[AuditRow] = []

    for norm_label in sorted(substrates):
        rec = substrates[norm_label]
        card_count = len(rec.card_ids)
        example_cards = "; ".join(rec.card_ids[:3])

        # MetaTraits CHEBI -- take first if multiple (rare)
        mt_chebi_id = sorted(rec.metatraits_chebi_ids)[0] if rec.metatraits_chebi_ids else ""
        oak_label = chebi_labels.get(mt_chebi_id) if mt_chebi_id else None

        label_match = compare_labels(rec.substrate_label, oak_label) if mt_chebi_id else "no_curie"

        # KG-Microbe lookup
        kgm_entry = kgm_mappings.get(norm_label)
        kgm_chebi_id = kgm_entry[0] if kgm_entry else ""
        kgm_chebi_label = kgm_entry[1] if kgm_entry else ""

        if kgm_chebi_id:
            kgm_label_match = compare_labels(rec.substrate_label, kgm_chebi_label)
        else:
            kgm_label_match = "not_found"

        # Compare sources
        if mt_chebi_id and kgm_chebi_id:
            kgm_matches_mt = "yes" if mt_chebi_id == kgm_chebi_id else "no"
        else:
            kgm_matches_mt = "n/a"

        # Determine audit status
        if mt_chebi_id and label_match in ("exact", "case_insensitive"):
            audit_status = "verified"
        elif mt_chebi_id and label_match in ("mismatch", "no_oak_label"):
            audit_status = "mismatch"
        elif not mt_chebi_id and kgm_chebi_id:
            audit_status = "no_curie_kgm_available"
        elif not mt_chebi_id:
            audit_status = "no_curie"
        else:
            audit_status = "unknown"

        rows.append(
            AuditRow(
                substrate_label=rec.substrate_label,
                card_count=card_count,
                example_cards=example_cards,
                metatraits_chebi_id=mt_chebi_id,
                chebi_label_from_oak=oak_label or "",
                label_match=label_match,
                kgm_chebi_id=kgm_chebi_id,
                kgm_chebi_label=kgm_chebi_label,
                kgm_label_match=kgm_label_match,
                kgm_matches_metatraits=kgm_matches_mt,
                audit_status=audit_status,
            )
        )

    return rows


def write_audit_tsv(rows: list[AuditRow], output_path: Path) -> None:
    """Write the audit TSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=AUDIT_FIELDNAMES, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "substrate_label": row.substrate_label,
                    "card_count": row.card_count,
                    "example_cards": row.example_cards,
                    "metatraits_chebi_id": row.metatraits_chebi_id,
                    "chebi_label_from_oak": row.chebi_label_from_oak,
                    "label_match": row.label_match,
                    "kgm_chebi_id": row.kgm_chebi_id,
                    "kgm_chebi_label": row.kgm_chebi_label,
                    "kgm_label_match": row.kgm_label_match,
                    "kgm_matches_metatraits": row.kgm_matches_metatraits,
                    "audit_status": row.audit_status,
                }
            )


def _report_sections(rows: list[AuditRow]) -> list[str]:
    """Build markdown sections for the audit report."""
    status_counts = Counter(row.audit_status for row in rows)
    total = len(rows)
    total_cards = sum(row.card_count for row in rows)

    mismatches = [r for r in rows if r.audit_status == "mismatch"]
    disagreements = [r for r in rows if r.kgm_matches_metatraits == "no"]
    unmapped = sorted(
        [r for r in rows if r.audit_status in ("no_curie", "no_curie_kgm_available")],
        key=lambda r: r.card_count,
        reverse=True,
    )

    lines: list[str] = [
        "# MetaTraits Substrate CURIE Audit Report\n",
        "\n",
        "## Summary\n",
        "\n",
        f"- **Unique substrates:** {total}\n",
        f"- **Total composed cards:** {total_cards}\n",
        "\n",
        "### Audit Status Counts\n",
        "\n",
        "| Status | Count |\n",
        "|--------|-------|\n",
    ]
    for status, count in status_counts.most_common():
        lines.append(f"| `{status}` | {count} |\n")
    lines.append("\n")

    # Mismatches section
    lines.append("## Label Mismatches (MetaTraits CHEBI vs OAK)\n")
    lines.append("\n")
    if mismatches:
        lines.append("| Substrate | MetaTraits CHEBI | OAK Label |\n")
        lines.append("|-----------|-----------------|----------|\n")
        for r in sorted(mismatches, key=lambda x: x.substrate_label):
            lines.append(
                f"| {r.substrate_label} | {r.metatraits_chebi_id} | {r.chebi_label_from_oak} |\n"
            )
    else:
        lines.append("No mismatches found.\n")
    lines.append("\n")

    # KGM disagreements
    lines.append("## KG-Microbe vs MetaTraits CHEBI Disagreements\n")
    lines.append("\n")
    if disagreements:
        lines.append("| Substrate | MetaTraits CHEBI | KGM CHEBI | KGM Label |\n")
        lines.append("|-----------|-----------------|-----------|----------|\n")
        for r in sorted(disagreements, key=lambda x: x.substrate_label):
            lines.append(
                f"| {r.substrate_label} | {r.metatraits_chebi_id} "
                f"| {r.kgm_chebi_id} | {r.kgm_chebi_label} |\n"
            )
    else:
        lines.append("No disagreements found.\n")
    lines.append("\n")

    # Top unmapped substrates
    lines.append("## Top 30 Unmapped Substrates by Card Count\n")
    lines.append("\n")
    if unmapped:
        lines.append("| Substrate | Cards | KGM Available |\n")
        lines.append("|-----------|-------|---------------|\n")
        for r in unmapped[:30]:
            kgm_avail = "yes" if r.kgm_chebi_id else "no"
            lines.append(f"| {r.substrate_label} | {r.card_count} | {kgm_avail} |\n")
    else:
        lines.append("All substrates have CURIEs.\n")
    lines.append("\n")

    # Cross-references
    lines.extend(
        [
            "## Related Files\n",
            "\n",
            "- [`docs/casamino_acids_curie_mapping_case_study.md`]"
            "(../../docs/casamino_acids_curie_mapping_case_study.md) "
            "-- CHEBI:78020 error case study\n",
            "- [`docs/linkml_embedding_and_validation_tools.md`]"
            "(../../docs/linkml_embedding_and_validation_tools.md) "
            "-- OAK/linkml-store tooling research\n",
            "- [`data/mappings/metatraits_in_sheet_resolution.tsv`]"
            "(metatraits_in_sheet_resolution.tsv) "
            "-- in-sheet resolution table\n",
            "- [`data/mappings/metatraits_external_curie_coverage.tsv`]"
            "(metatraits_external_curie_coverage.tsv) "
            "-- external CURIE coverage\n",
        ]
    )

    return lines


def write_audit_report(rows: list[AuditRow], report_path: Path) -> None:
    """Write a markdown summary report alongside the TSV."""
    lines = _report_sections(rows)
    report_path.parent.mkdir(parents=True, exist_ok=True)
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
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=Path("data/mappings/metatraits_substrate_curie_audit.tsv"),
    show_default=True,
    help="Output audit TSV path",
)
@click.option(
    "--report",
    "-r",
    type=click.Path(path_type=Path),
    default=None,
    help="Output markdown report path (default: <output>.md sibling)",
)
@click.option(
    "--kgm-mappings",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="KG-Microbe compound_mappings_strict_hydrate.tsv (optional)",
)
def main(
    metatraits_cards: Path,
    output: Path,
    report: Path | None,
    kgm_mappings: Path | None,
) -> None:
    """Audit MetaTraits substrate CURIEs against CHEBI via OAK."""
    if report is None:
        report = output.with_suffix("").with_name(output.stem + "_report.md")

    click.echo(f"Parsing cards from {metatraits_cards}")
    substrates = parse_cards_to_substrates(metatraits_cards)
    click.echo(f"Found {len(substrates)} unique substrates")

    # Collect all CHEBI CURIEs that need OAK lookup
    all_chebi_ids: set[str] = set()
    for rec in substrates.values():
        all_chebi_ids.update(rec.metatraits_chebi_ids)
    click.echo(f"Looking up {len(all_chebi_ids)} unique CHEBI CURIEs via OAK")

    chebi_labels = verify_chebi_labels_via_oak(all_chebi_ids) if all_chebi_ids else {}
    click.echo(f"Retrieved {sum(1 for v in chebi_labels.values() if v)} labels")

    # Load KG-Microbe mappings
    kgm: dict[str, tuple[str, str]] = {}
    if kgm_mappings:
        click.echo(f"Loading KG-Microbe mappings from {kgm_mappings}")
        kgm = load_kgm_mappings(kgm_mappings)
        click.echo(f"Loaded {len(kgm)} unique compound mappings")

    # Build and write audit
    rows = build_audit_rows(substrates, chebi_labels, kgm)
    write_audit_tsv(rows, output)
    click.echo(f"Wrote {output} ({len(rows)} rows)")

    write_audit_report(rows, report)
    click.echo(f"Wrote {report}")

    # Summary
    status_counts = Counter(r.audit_status for r in rows)
    for status, count in status_counts.most_common():
        click.echo(f"  {status}: {count}")


if __name__ == "__main__":
    main()
