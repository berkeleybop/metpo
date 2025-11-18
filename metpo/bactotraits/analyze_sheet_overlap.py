#!/usr/bin/env python3
"""
Analyze overlap between minimal_classes.tsv (canonical) and other class sheets.

This script identifies:
1. Which classes in bactotraits.tsv/more_classes/attic_classes exist in minimal_classes.tsv
2. Which classes have important metadata (RangeMins/RangeMaxes) that would be lost
3. Which classes can be safely removed from non-canonical sheets
"""

import csv
from pathlib import Path


def normalize_id(id_str: str) -> str:
    """Convert various ID formats to METPO:XXXXXXX format."""
    if not id_str:
        return ""

    # Handle URL format: https://w3id.org/metpo/1000335 -> METPO:1000335
    if id_str.startswith("https://w3id.org/metpo/"):
        return f"METPO:{id_str.split('/')[-1]}"

    # Already in CURIE format
    if id_str.startswith("METPO:"):
        return id_str

    # Just a number
    if id_str.isdigit():
        return f"METPO:{id_str}"

    return id_str


def load_minimal_classes(tsv_path: Path) -> tuple[set[str], dict[str, str]]:
    """Load canonical class IDs and labels from minimal_classes.tsv."""
    canonical_ids = set()
    id_to_label = {}

    with open(tsv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            class_id = row.get("ID", "").strip()
            label = row.get("label", "").strip()

            if class_id and class_id != "ID":  # Skip header row
                normalized_id = normalize_id(class_id)
                canonical_ids.add(normalized_id)
                id_to_label[normalized_id] = label

    return canonical_ids, id_to_label


def analyze_sheet(sheet_path: Path, sheet_name: str, canonical_ids: set[str], id_to_label: dict[str, str]) -> dict:
    """Analyze a single sheet for overlaps and important metadata."""

    results = {
        "sheet_name": sheet_name,
        "total_rows": 0,
        "in_canonical": [],
        "not_in_canonical": [],
        "has_range_metadata": [],
        "safe_to_delete": [],
        "metadata_at_risk": []
    }

    with open(sheet_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            # Get the ID from first column (varies by sheet)
            first_col = row.get("First column") or row.get("class") or ""
            class_id = first_col.strip()

            if not class_id or class_id in ["First column", "class", "ID"]:
                continue

            results["total_rows"] += 1

            normalized_id = normalize_id(class_id)
            label = row.get("Values", "") or row.get("labels", "")
            units = row.get("Units", "").strip()
            range_min = row.get("RangeMins", "").strip()
            range_max = row.get("RangeMaxes", "").strip()

            # Check for range metadata
            has_ranges = bool(units or range_min or range_max)

            row_info = {
                "id": normalized_id,
                "label": label,
                "units": units,
                "range_min": range_min,
                "range_max": range_max,
                "canonical_label": id_to_label.get(normalized_id, "")
            }

            if normalized_id in canonical_ids:
                results["in_canonical"].append(row_info)

                if has_ranges:
                    results["has_range_metadata"].append(row_info)
                    results["metadata_at_risk"].append(row_info)
                else:
                    results["safe_to_delete"].append(row_info)
            else:
                results["not_in_canonical"].append(row_info)

    return results


def print_summary(results: dict):
    """Print a summary of the analysis."""
    print(f"\n{'='*80}")
    print(f"Sheet: {results['sheet_name']}")
    print(f"{'='*80}")
    print(f"Total rows: {results['total_rows']}")
    print(f"  In canonical (minimal_classes.tsv): {len(results['in_canonical'])}")
    print(f"  NOT in canonical: {len(results['not_in_canonical'])}")
    print(f"  With range metadata (Units/RangeMins/RangeMaxes): {len(results['has_range_metadata'])}")
    print(f"  SAFE to delete (in canonical, no unique metadata): {len(results['safe_to_delete'])}")
    print(f"  METADATA AT RISK (in canonical, has ranges): {len(results['metadata_at_risk'])}")


def print_detailed_ranges(results: dict):
    """Print details of classes with range metadata."""
    if results["metadata_at_risk"]:
        print("\n⚠️  Classes with range metadata that would be LOST if deleted:")
        print(f"{'ID':<20} {'Label':<30} {'Units':<10} {'Min':<8} {'Max':<8}")
        print("-" * 80)
        for row in results["metadata_at_risk"]:
            print(f"{row['id']:<20} {row['label'][:28]:<30} {row['units']:<10} {row['range_min']:<8} {row['range_max']:<8}")


def main():
    base_path = Path("/Users/MAM/Documents/gitrepos/metpo/downloads/sheets")

    # Load canonical classes
    print("Loading canonical classes from minimal_classes.tsv...")
    canonical_ids, id_to_label = load_minimal_classes(base_path / "minimal_classes.tsv")
    print(f"Found {len(canonical_ids)} canonical classes")

    # Analyze each non-canonical sheet
    sheets_to_analyze = [
        ("bactotraits.tsv", "bactotraits"),
        ("more_classes___inconsistent.tsv", "more_classes___inconsistent"),
        ("attic_classes.tsv", "attic_classes")
    ]

    all_results = []

    for filename, sheet_name in sheets_to_analyze:
        sheet_path = base_path / filename
        if sheet_path.exists():
            print(f"\nAnalyzing {filename}...")
            results = analyze_sheet(sheet_path, sheet_name, canonical_ids, id_to_label)
            all_results.append(results)
            print_summary(results)
            print_detailed_ranges(results)

    # Overall summary
    print(f"\n\n{'='*80}")
    print("OVERALL SUMMARY")
    print(f"{'='*80}")

    total_metadata_at_risk = sum(len(r["metadata_at_risk"]) for r in all_results)
    total_safe_to_delete = sum(len(r["safe_to_delete"]) for r in all_results)

    print(f"\nTotal classes with range metadata at risk: {total_metadata_at_risk}")
    print(f"Total classes SAFE to delete: {total_safe_to_delete}")

    print("\n\n📋 RECOMMENDATION:")
    print("-" * 80)
    print("BEFORE deleting any rows from non-canonical sheets:")
    print()
    print("1. PRESERVE range metadata by implementing the OWL data property restriction")
    print("   pattern from GitHub issue #233:")
    print("   - Use 'has measurement value' (IAO:0000004)")
    print("   - Add EquivalentClass axioms like: 'has measurement value' some float[>= 5, <= 9]")
    print()
    print("2. MIGRATE the range metadata from bactotraits.tsv columns:")
    print("   - Units → IAO:0000039 (measurement unit label)")
    print("   - RangeMins/RangeMaxes → data property restrictions in EquivalentClass")
    print()
    print("3. THEN safely delete duplicate rows from non-canonical sheets")
    print()
    print(f"This workflow will preserve {total_metadata_at_risk} classes' critical metadata")
    print("while cleaning up duplicates across your Google Sheets.")


if __name__ == "__main__":
    main()
