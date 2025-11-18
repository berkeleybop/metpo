#!/usr/bin/env python3
"""
Analyze METPO SSSOM mappings from PRIMARY SOURCE files.

Parses /home/mark/gitrepos/metpo/data/mappings/metpo_mappings_*.sssom.tsv directly.
100% traceable.
"""

import csv
from pathlib import Path
from collections import Counter

def analyze_sssom(sssom_file):
    """Parse SSSOM file and count mappings by target ontology."""
    with open(sssom_file) as f:
        # Skip comment lines
        lines = [line for line in f if not line.startswith("#")]

    reader = csv.DictReader(lines, delimiter="\t")

    target_ontologies = Counter()
    match_types = Counter()
    total_mappings = 0

    for row in reader:
        # Extract target ontology prefix from object_id
        object_id = row.get("object_id", "")
        if ":" in object_id:
            prefix = object_id.split(":")[0]
            target_ontologies[prefix] += 1

        # Count match type
        pred = row.get("predicate_id", "")
        match_types[pred] += 1

        total_mappings += 1

    return total_mappings, target_ontologies, match_types

def main():
    metpo_root = Path("/home/mark/gitrepos/metpo")
    sssom_dir = metpo_root / "data" / "mappings"

    print("=== METPO SSSOM Mappings Analysis (PRIMARY SOURCE) ===\n")

    # Try both SSSOM files
    for sssom_file in ["metpo_mappings_combined_relaxed.sssom.tsv",
                       "metpo_mappings_optimized.sssom.tsv"]:
        filepath = sssom_dir / sssom_file

        if not filepath.exists():
            print(f"⚠️  Not found: {filepath}")
            continue

        print(f"Source: {filepath}")
        total, targets, matches = analyze_sssom(filepath)

        print(f"Total mappings: {total}")
        print(f"\nTarget ontologies (top 10):")
        for onto, count in targets.most_common(10):
            print(f"  {onto:15s} {count:4d} mappings")

        print(f"\nMatch types:")
        for match_type, count in matches.most_common():
            short_type = match_type.split("/")[-1] if "/" in match_type else match_type
            print(f"  {short_type:30s} {count:4d}")

        print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
