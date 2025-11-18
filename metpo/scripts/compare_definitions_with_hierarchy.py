#!/usr/bin/env python3
"""
Compare best matched definitions with METPO's asserted definitions.

Analyzes whether matched definitions follow genus-differentia guidelines
within the context of METPO's class hierarchy, and suggests tweaks.
"""

import csv
from difflib import SequenceMatcher
from pathlib import Path

import click


def parse_parent_classes(parent_str: str) -> list[str]:
    """Parse pipe-separated parent classes."""
    if not parent_str:
        return []
    return [p.strip() for p in parent_str.split("|") if p.strip()]


def get_genus_from_definition(definition: str) -> str | None:
    """
    Extract the genus term from a definition (genus-differentia form).

    Looks for patterns like "A <genus> that..." or "An <genus> that..."
    """
    if not definition:
        return None

    definition = definition.strip()

    # Common patterns for genus
    patterns = [
        ("A ", " that "),
        ("An ", " that "),
        ("A ", " which "),
        ("An ", " which "),
        ("A ", " where "),
        ("An ", " where "),
        ("A ", " in which "),
        ("An ", " in which "),
    ]

    for start, sep in patterns:
        if definition.startswith(start) and sep in definition:
            genus_part = definition[len(start):definition.index(sep)]
            return genus_part.strip()

    return None


def check_genus_match(genus: str, parent_labels: list[str]) -> tuple[bool, str | None]:
    """
    Check if genus mentions any parent class.

    Returns (matches, matched_parent)
    """
    if not genus or not parent_labels:
        return False, None

    genus_lower = genus.lower()

    for parent in parent_labels:
        parent_lower = parent.lower()
        parent_words = parent_lower.split()

        # Check if any significant word from parent appears in genus
        for word in parent_words:
            if len(word) > 3 and word in genus_lower:  # Skip short words like "a", "of"
                return True, parent

    return False, None


def similarity(s1: str, s2: str) -> float:
    """Calculate similarity between two strings."""
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()


def suggest_tweak(
    matched_def: str,
    parent_labels: list[str],
    metpo_label: str
) -> str | None:
    """
    Suggest how to tweak the matched definition to better fit METPO hierarchy.
    """
    if not matched_def or not parent_labels:
        return None

    genus = get_genus_from_definition(matched_def)

    # If no genus found or genus doesn't match parents, suggest replacement
    if not genus:
        # Definition doesn't follow genus-differentia form
        parent = parent_labels[0]  # Use first (primary) parent
        return f"Rewrite as: A {parent} that {matched_def.lower()}"

    matches, _matched_parent = check_genus_match(genus, parent_labels)

    if not matches:
        # Genus doesn't mention parent - suggest replacement
        parent = parent_labels[0]

        # Try to preserve the differentia
        if " that " in matched_def:
            differentia = matched_def[matched_def.index(" that "):].strip()
            return f"Replace genus '{genus}' with '{parent}': A {parent} {differentia}"
        if " which " in matched_def:
            differentia = matched_def[matched_def.index(" which "):].strip()
            return f"Replace genus '{genus}' with '{parent}': A {parent} {differentia}"
        return f"Replace genus '{genus}' with '{parent}' to match METPO hierarchy"

    return None  # Definition is already compatible


@click.command()
@click.option(
    "--best-definitions",
    "-b",
    type=click.Path(exists=True, path_type=Path),
    default="reports/best_definition_per_term_final.tsv",
    help="Path to best definitions TSV"
)
@click.option(
    "--metpo-terms",
    "-t",
    type=click.Path(exists=True, path_type=Path),
    default="src/templates/metpo_sheet.tsv",
    help="Path to METPO terms template"
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default="reports/definition_comparison_with_hierarchy.tsv",
    help="Output comparison TSV"
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed analysis"
)
def main(
    best_definitions: Path,
    metpo_terms: Path,
    output: Path,
    verbose: bool
):
    """
    Compare best matched definitions with METPO's asserted definitions.

    Checks if matched definitions follow genus-differentia form and are
    compatible with METPO's class hierarchy.
    """

    # Load METPO terms with parents and current definitions
    click.echo(f"Loading METPO terms from {metpo_terms}...")
    metpo_data = {}

    with open(metpo_terms, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)  # Skip ROBOT header row 1
        next(reader)  # Skip ROBOT header row 2

        for row in reader:
            if len(row) < 5:
                continue

            metpo_id = row[0].strip()
            metpo_label = row[1].strip()
            parent_str = row[3].strip() if len(row) > 3 else ""
            current_def = row[4].strip() if len(row) > 4 else ""

            if metpo_id:
                parents = parse_parent_classes(parent_str)
                metpo_data[metpo_id] = {
                    "label": metpo_label,
                    "parents": parents,
                    "current_definition": current_def
                }

    click.echo(f"Loaded {len(metpo_data)} METPO terms")

    # Load best matched definitions
    click.echo(f"\nLoading best matched definitions from {best_definitions}...")
    best_defs = {}

    with open(best_definitions, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            metpo_id = row["metpo_id"]
            best_defs[metpo_id] = row

    click.echo(f"Loaded {len(best_defs)} best matched definitions")

    # Compare
    results = []
    stats = {
        "has_current": 0,
        "needs_current": 0,
        "genus_matches_parent": 0,
        "genus_missing_parent": 0,
        "no_genus": 0,
        "needs_tweak": 0,
        "compatible": 0,
    }

    for metpo_id in sorted(best_defs.keys()):
        if metpo_id not in metpo_data:
            continue

        metpo = metpo_data[metpo_id]
        matched = best_defs[metpo_id]

        metpo_label = metpo["label"]
        parents = metpo["parents"]
        current_def = metpo["current_definition"]
        matched_def = matched["definition"]

        # Check if METPO has a current definition
        has_current = bool(current_def)
        stats["has_current"] += has_current
        stats["needs_current"] += not has_current

        # Extract genus from matched definition
        genus = get_genus_from_definition(matched_def)

        if not genus:
            stats["no_genus"] += 1
            genus_status = "no_genus"
            genus_match = False
            matched_parent = None
        else:
            genus_match, matched_parent = check_genus_match(genus, parents)

            if genus_match:
                stats["genus_matches_parent"] += 1
                genus_status = "genus_matches_parent"
            else:
                stats["genus_missing_parent"] += 1
                genus_status = "genus_missing_parent"

        # Suggest tweak if needed
        tweak = suggest_tweak(matched_def, parents, metpo_label)

        if tweak:
            stats["needs_tweak"] += 1
        else:
            stats["compatible"] += 1

        # Calculate similarity with current definition
        def_similarity = similarity(matched_def, current_def) if current_def else 0.0

        result = {
            "metpo_id": metpo_id,
            "metpo_label": metpo_label,
            "parent_classes": "|".join(parents),
            "current_definition": current_def,
            "has_current_definition": "yes" if has_current else "no",
            "matched_definition": matched_def,
            "matched_source": matched["source_ontology"],
            "matched_quality": matched["quality_label"],
            "def_similarity": f"{def_similarity:.3f}",
            "extracted_genus": genus or "",
            "genus_status": genus_status,
            "matched_parent": matched_parent or "",
            "suggested_tweak": tweak or "",
            "needs_tweak": "yes" if tweak else "no",
        }

        results.append(result)

        if verbose and (tweak or not has_current or genus_status != "genus_matches_parent"):
            click.echo(f"\n{metpo_id} ({metpo_label})")
            click.echo(f"  Parents: {', '.join(parents)}")
            if current_def:
                click.echo(f"  Current: {current_def[:80]}...")
            else:
                click.echo("  Current: [NONE]")
            click.echo(f"  Matched: {matched_def[:80]}...")
            click.echo(f"  Genus: {genus or '[NONE]'}")
            click.echo(f"  Status: {genus_status}")
            if tweak:
                click.echo(f"  Tweak: {tweak[:100]}...")

    # Write output
    click.echo(f"\nWriting comparison to {output}...")
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "metpo_id", "metpo_label", "parent_classes",
            "current_definition", "has_current_definition",
            "matched_definition", "matched_source", "matched_quality",
            "def_similarity", "extracted_genus", "genus_status",
            "matched_parent", "suggested_tweak", "needs_tweak"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(results)

    # Summary
    click.echo("\n" + "="*70)
    click.echo("SUMMARY")
    click.echo("="*70)
    click.echo(f"Terms analyzed: {len(results)}")
    click.echo("\nCurrent definitions:")
    click.echo(f"  Has definition: {stats['has_current']} ({stats['has_current']/len(results)*100:.1f}%)")
    click.echo(f"  Needs definition: {stats['needs_current']} ({stats['needs_current']/len(results)*100:.1f}%)")

    click.echo("\nGenus-differentia analysis:")
    click.echo(f"  Genus matches parent: {stats['genus_matches_parent']} ({stats['genus_matches_parent']/len(results)*100:.1f}%)")
    click.echo(f"  Genus doesn't match parent: {stats['genus_missing_parent']} ({stats['genus_missing_parent']/len(results)*100:.1f}%)")
    click.echo(f"  No genus found: {stats['no_genus']} ({stats['no_genus']/len(results)*100:.1f}%)")

    click.echo("\nRecommendations:")
    click.echo(f"  Compatible (no tweak needed): {stats['compatible']} ({stats['compatible']/len(results)*100:.1f}%)")
    click.echo(f"  Needs tweak: {stats['needs_tweak']} ({stats['needs_tweak']/len(results)*100:.1f}%)")


if __name__ == "__main__":
    main()
