#!/usr/bin/env python3
"""
BactoTraits ↔ METPO Set Difference Analysis

Compare kg-microbe BactoTraits field names with METPO synonyms attributed to BactoTraits.
Shows exact set differences and identifies close matches (minor variations).

Usage:
    uv run python src/scripts/bactotraits_metpo_set_difference.py
    uv run python src/scripts/bactotraits_metpo_set_difference.py --format yaml --output reports/bactotraits-metpo-set-diff.yaml
"""

import csv
import click
import yaml
from pathlib import Path
from typing import Set, List, Dict, Tuple

# File paths
BACTOTRAITS_SOURCE_URI = "https://ordar.otelo.univ-lorraine.fr/files/ORDAR-53/BactoTraits_databaseV2_Jun2022.csv"

def read_kg_microbe_headers(kg_microbe_file: Path) -> Set[str]:
    """Read field names from kg-microbe BactoTraits.tsv header."""
    if not kg_microbe_file.exists():
        raise FileNotFoundError(f"kg-microbe file not found: {kg_microbe_file}")

    with open(kg_microbe_file, "r", encoding="utf-8") as f:
        header = f.readline().strip().split("\t")

    return set(header)


def read_metpo_bactotraits_synonyms(synonym_sources_tsv: Path) -> Dict[str, Dict]:
    """Read synonyms attributed to BactoTraits from synonym-sources.tsv."""
    if not synonym_sources_tsv.exists():
        raise FileNotFoundError(f"Synonym sources file not found: {synonym_sources_tsv}")

    synonyms = {}

    with open(synonym_sources_tsv, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            src = row.get("?src", "").strip("<>")
            syn_value = row.get("?synValue", "").strip('"')
            entity = row.get("?entity", "").strip("<>")
            entity_type = row.get("?entityType", "").strip('"')

            if src == BACTOTRAITS_SOURCE_URI and syn_value:
                if syn_value not in synonyms:
                    synonyms[syn_value] = {
                        "entity": entity,
                        "entity_type": entity_type,
                        "source": src
                    }

    return synonyms


def normalize_variant(text: str) -> str:
    """Normalize text for fuzzy matching: lowercase, no spaces/hyphens/underscores."""
    return text.lower().replace(" ", "").replace("-", "").replace("_", "")


def find_close_matches(missing: Set[str], present: Set[str]) -> Dict[str, List[str]]:
    """
    Find close matches between missing and present sets.
    Returns dict mapping missing items to list of close matches.
    """
    matches = {}

    for missing_item in missing:
        norm_missing = normalize_variant(missing_item)
        candidates = []

        for present_item in present:
            norm_present = normalize_variant(present_item)

            # Exact match after normalization
            if norm_missing == norm_present:
                diff = describe_difference(missing_item, present_item)
                if diff and diff != "unknown variation":
                    candidates.append({
                        "match": present_item,
                        "type": "normalized_exact",
                        "difference": diff
                    })
            # Very close match (edit distance or substring)
            elif norm_missing in norm_present or norm_present in norm_missing:
                diff = describe_difference(missing_item, present_item)
                if diff and diff != "unknown variation":
                    candidates.append({
                        "match": present_item,
                        "type": "substring",
                        "difference": diff
                    })

        if candidates:
            matches[missing_item] = candidates

    return matches


def describe_difference(str1: str, str2: str) -> str:
    """Describe the difference between two strings."""
    differences = []

    # Strip for comparison
    str1_stripped = str1.strip()
    str2_stripped = str2.strip()

    # Check case (after stripping whitespace)
    if str1_stripped.lower() == str2_stripped.lower() and str1_stripped != str2_stripped:
        differences.append("case")

    # Check leading/trailing whitespace
    if str1_stripped == str2_stripped and str1 != str2:
        differences.append("leading/trailing whitespace")

    # Check if they're the same after removing all whitespace
    if str1.replace(" ", "") == str2.replace(" ", "") and str1 != str2:
        if "leading/trailing whitespace" not in differences:
            differences.append("whitespace")

    # Check hyphen vs underscore
    if str1.replace("-", "_") == str2.replace("-", "_"):
        differences.append("hyphen vs underscore")

    # Check comparison operators
    if "<=" in str1 and "<" in str2 and "<=" not in str2:
        differences.append("< vs <=")
    elif "<=" in str2 and "<" in str1 and "<=" not in str1:
        differences.append("<= vs <")

    if ">=" in str1 and ">" in str2 and ">=" not in str2:
        differences.append("> vs >=")
    elif ">=" in str2 and ">" in str1 and ">=" not in str1:
        differences.append(">= vs >")

    # Check periods vs underscores
    if str1.replace(".", "_") == str2.replace(".", "_"):
        differences.append("period vs underscore")

    return ", ".join(differences) if differences else "unknown variation"


def categorize_by_issue(items_with_matches: Dict[str, List[Dict]]) -> Dict[str, List[Tuple[str, str]]]:
    """Categorize items by the type of issue (case, whitespace, operators, etc.)."""
    categories = {
        "case_only": [],
        "whitespace_only": [],
        "comparison_operators": [],
        "hyphen_underscore": [],
        "period_underscore": [],
        "multiple_issues": [],
    }

    for item, matches in items_with_matches.items():
        if not matches:
            continue

        # Take the best match (first one)
        best_match = matches[0]
        diff = best_match["difference"]
        match_str = best_match["match"]

        diff_types = [d.strip() for d in diff.split(",")]

        if len(diff_types) == 1:
            if "case" in diff_types[0]:
                categories["case_only"].append((item, match_str))
            elif "whitespace" in diff_types[0]:
                categories["whitespace_only"].append((item, match_str))
            elif "<" in diff_types[0] or ">" in diff_types[0]:
                categories["comparison_operators"].append((item, match_str))
            elif "hyphen" in diff_types[0]:
                categories["hyphen_underscore"].append((item, match_str))
            elif "period" in diff_types[0]:
                categories["period_underscore"].append((item, match_str))
        else:
            categories["multiple_issues"].append((item, match_str))

    return categories


@click.command()
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "yaml"], case_sensitive=False),
    default="text",
    help="Output format"
)
@click.option(
    "--output",
    type=click.Path(),
    help="Output file path. If not specified, prints to stdout."
)
@click.option(
    "--bactotraits-file",
    type=click.Path(exists=True, path_type=Path),
    default=Path("local/BactoTraits.tsv"),
    help="Path to the BactoTraits.tsv file."
)
@click.option(
    "--synonyms-file",
    type=click.Path(exists=True, path_type=Path),
    default=Path("reports/synonym-sources.tsv"),
    help="Path to the synonym-sources.tsv file."
)
def main(output_format, output, bactotraits_file, synonyms_file):
    """
    Compare kg-microbe BactoTraits headers with METPO BactoTraits-attributed synonyms.
    Shows exact set differences and identifies close matches.
    """

    # Load data
    kg_microbe_fields = read_kg_microbe_headers(bactotraits_file)
    metpo_synonyms = read_metpo_bactotraits_synonyms(synonyms_file)
    metpo_synonym_set = set(metpo_synonyms.keys())

    # Compute set differences
    in_bactotraits_not_metpo = kg_microbe_fields - metpo_synonym_set
    in_metpo_not_bactotraits = metpo_synonym_set - kg_microbe_fields
    in_both = kg_microbe_fields & metpo_synonym_set

    # Find close matches
    bt_close_matches = find_close_matches(in_bactotraits_not_metpo, metpo_synonym_set)
    metpo_close_matches = find_close_matches(in_metpo_not_bactotraits, kg_microbe_fields)

    # Items with NO close matches (true missing)
    bt_truly_missing = in_bactotraits_not_metpo - set(bt_close_matches.keys())
    metpo_truly_orphaned = in_metpo_not_bactotraits - set(metpo_close_matches.keys())

    # Categorize by issue type
    bt_categories = categorize_by_issue(bt_close_matches)
    metpo_categories = categorize_by_issue(metpo_close_matches)

    if output_format == "yaml":
        result = {
            "summary": {
                "kg_microbe_total_fields": len(kg_microbe_fields),
                "metpo_bactotraits_synonyms": len(metpo_synonym_set),
                "exact_matches": len(in_both),
                "bactotraits_not_in_metpo": len(in_bactotraits_not_metpo),
                "bactotraits_with_close_matches": len(bt_close_matches),
                "bactotraits_truly_missing": len(bt_truly_missing),
                "metpo_not_in_bactotraits": len(in_metpo_not_bactotraits),
                "metpo_with_close_matches": len(metpo_close_matches),
                "metpo_truly_orphaned": len(metpo_truly_orphaned),
            },
            "bactotraits_fields_not_in_metpo": {
                "close_matches_by_issue": {
                    "case_differences": [{"bt": bt, "metpo": mp} for bt, mp in bt_categories["case_only"]],
                    "whitespace_differences": [{"bt": bt, "metpo": mp} for bt, mp in bt_categories["whitespace_only"]],
                    "comparison_operator_differences": [{"bt": bt, "metpo": mp} for bt, mp in bt_categories["comparison_operators"]],
                    "hyphen_underscore_differences": [{"bt": bt, "metpo": mp} for bt, mp in bt_categories["hyphen_underscore"]],
                    "period_underscore_differences": [{"bt": bt, "metpo": mp} for bt, mp in bt_categories["period_underscore"]],
                    "multiple_issues": [{"bt": bt, "metpo": mp} for bt, mp in bt_categories["multiple_issues"]],
                },
                "truly_missing": sorted(bt_truly_missing)
            },
            "metpo_synonyms_not_in_bactotraits": {
                "close_matches_by_issue": {
                    "case_differences": [{"metpo": mp, "bt": bt} for mp, bt in metpo_categories["case_only"]],
                    "whitespace_differences": [{"metpo": mp, "bt": bt} for mp, bt in metpo_categories["whitespace_only"]],
                    "comparison_operator_differences": [{"metpo": mp, "bt": bt} for mp, bt in metpo_categories["comparison_operators"]],
                    "hyphen_underscore_differences": [{"metpo": mp, "bt": bt} for mp, bt in metpo_categories["hyphen_underscore"]],
                    "period_underscore_differences": [{"metpo": mp, "bt": bt} for mp, bt in metpo_categories["period_underscore"]],
                    "multiple_issues": [{"metpo": mp, "bt": bt} for mp, bt in metpo_categories["multiple_issues"]],
                },
                "truly_orphaned": sorted(metpo_truly_orphaned)
            },
            "exact_matches": sorted(in_both)
        }

        output_str = yaml.dump(result, default_flow_style=False, sort_keys=False, allow_unicode=True)
    else:
        # Text format
        lines = []
        lines.append("=" * 80)
        lines.append("BactoTraits ↔ METPO Set Difference Analysis")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"kg-microbe BactoTraits.tsv:          {len(kg_microbe_fields)} field names")
        lines.append(f"METPO BactoTraits-attributed synonyms: {len(metpo_synonym_set)} synonyms")
        lines.append(f"Exact matches:                         {len(in_both)} fields")
        lines.append("")

        lines.append("=" * 80)
        lines.append(f"PART 1: BactoTraits fields NOT in METPO ({len(in_bactotraits_not_metpo)} total)")
        lines.append("=" * 80)
        lines.append("")

        if bt_close_matches:
            lines.append(f"Close Matches ({len(bt_close_matches)} fields - minor variations):")
            lines.append("-" * 80)

            if bt_categories["case_only"]:
                lines.append(f"\nCase differences ({len(bt_categories['case_only'])}):")
                for bt, mp in bt_categories["case_only"]:
                    lines.append(f"  '{bt}' ≈ '{mp}'")

            if bt_categories["whitespace_only"]:
                lines.append(f"\nWhitespace differences ({len(bt_categories['whitespace_only'])}):")
                for bt, mp in bt_categories["whitespace_only"]:
                    lines.append(f"  '{bt}' ≈ '{mp}'")

            if bt_categories["comparison_operators"]:
                lines.append(f"\nComparison operator differences ({len(bt_categories['comparison_operators'])}):")
                for bt, mp in bt_categories["comparison_operators"]:
                    lines.append(f"  '{bt}' ≈ '{mp}'")

            if bt_categories["hyphen_underscore"]:
                lines.append(f"\nHyphen vs underscore ({len(bt_categories['hyphen_underscore'])}):")
                for bt, mp in bt_categories["hyphen_underscore"]:
                    lines.append(f"  '{bt}' ≈ '{mp}'")

            if bt_categories["period_underscore"]:
                lines.append(f"\nPeriod vs underscore ({len(bt_categories['period_underscore'])}):")
                for bt, mp in bt_categories["period_underscore"]:
                    lines.append(f"  '{bt}' ≈ '{mp}'")

            if bt_categories["multiple_issues"]:
                lines.append(f"\nMultiple issues ({len(bt_categories['multiple_issues'])}):")
                for bt, mp in bt_categories["multiple_issues"]:
                    lines.append(f"  '{bt}' ≈ '{mp}'")

        if bt_truly_missing:
            lines.append("")
            lines.append(f"Truly Missing ({len(bt_truly_missing)} fields - no close matches in METPO):")
            lines.append("-" * 80)
            for field in sorted(bt_truly_missing):
                lines.append(f"  ✗ '{field}'")

        lines.append("")
        lines.append("=" * 80)
        lines.append(f"PART 2: METPO synonyms NOT in BactoTraits ({len(in_metpo_not_bactotraits)} total)")
        lines.append("=" * 80)
        lines.append("")

        if metpo_close_matches:
            lines.append(f"Close Matches ({len(metpo_close_matches)} synonyms - minor variations):")
            lines.append("-" * 80)

            if metpo_categories["case_only"]:
                lines.append(f"\nCase differences ({len(metpo_categories['case_only'])}):")
                for mp, bt in metpo_categories["case_only"]:
                    lines.append(f"  '{mp}' ≈ '{bt}'")

            if metpo_categories["whitespace_only"]:
                lines.append(f"\nWhitespace differences ({len(metpo_categories['whitespace_only'])}):")
                for mp, bt in metpo_categories["whitespace_only"]:
                    lines.append(f"  '{mp}' ≈ '{bt}'")

            if metpo_categories["comparison_operators"]:
                lines.append(f"\nComparison operator differences ({len(metpo_categories['comparison_operators'])}):")
                for mp, bt in metpo_categories["comparison_operators"]:
                    lines.append(f"  '{mp}' ≈ '{bt}' (METPO should use <=, not <)")

            if metpo_categories["hyphen_underscore"]:
                lines.append(f"\nHyphen vs underscore ({len(metpo_categories['hyphen_underscore'])}):")
                for mp, bt in metpo_categories["hyphen_underscore"]:
                    lines.append(f"  '{mp}' ≈ '{bt}'")

            if metpo_categories["period_underscore"]:
                lines.append(f"\nPeriod vs underscore ({len(metpo_categories['period_underscore'])}):")
                for mp, bt in metpo_categories["period_underscore"]:
                    lines.append(f"  '{mp}' ≈ '{bt}'")

            if metpo_categories["multiple_issues"]:
                lines.append(f"\nMultiple issues ({len(metpo_categories['multiple_issues'])}):")
                for mp, bt in metpo_categories["multiple_issues"]:
                    lines.append(f"  '{mp}' ≈ '{bt}'")

        if metpo_truly_orphaned:
            lines.append("")
            lines.append(f"Truly Orphaned ({len(metpo_truly_orphaned)} synonyms - no close matches in BactoTraits):")
            lines.append("-" * 80)
            for syn in sorted(metpo_truly_orphaned):
                lines.append(f"  ⚠ '{syn}'")

        lines.append("")
        lines.append("=" * 80)

        output_str = "\n".join(lines)

    if output:
        with open(output, "w") as f:
            f.write(output_str)
        print(f"Report written to {output}")
    else:
        print(output_str)


if __name__ == "__main__":
    main()