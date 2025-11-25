#!/usr/bin/env python3
"""
Analyze columns in TSV files to identify CURIE usage patterns.

Checks each column for values matching CURIE pattern: prefix:identifier
where both parts contain no whitespace or colons.
"""

import csv
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# CURIE pattern: non-whitespace/non-colon + colon + non-whitespace/non-colon
CURIE_PATTERN = re.compile(r'^[^\s:]+:[^\s:]+$')


def is_curie(value: str) -> bool:
    """Check if a value matches CURIE pattern."""
    if not value or value == '':
        return False
    return bool(CURIE_PATTERN.match(value))


def analyze_tsv_file(filepath: Path, source: str) -> List[Tuple[str, str, str, float, int, int, int]]:
    """
    Analyze a TSV file for CURIE patterns in each column.

    Returns list of tuples: (source, filename, column_name, curie_percentage, curie_count, non_null_count, total_rows)
    """
    results = []

    with open(filepath, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames

        # Initialize counters for each column
        column_counts = {col: {'non_null': 0, 'curies': 0} for col in headers}
        total_rows = 0

        # Process each data row
        for row in reader:
            total_rows += 1

            for col in headers:
                value = row.get(col, '').strip()
                if value:  # Only count non-empty values
                    column_counts[col]['non_null'] += 1
                    if is_curie(value):
                        column_counts[col]['curies'] += 1

    # Calculate percentages
    filename = filepath.name
    for col_name, counts in column_counts.items():
        non_null = counts['non_null']
        curies = counts['curies']
        percentage = (curies / non_null * 100) if non_null > 0 else 0.0
        results.append((source, filename, col_name, percentage, curies, non_null, total_rows))

    return results


def main():
    """Main function to analyze files and output results."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_curie_columns.py <directory_or_file> [file2.tsv ...]", file=sys.stderr)
        sys.exit(1)

    all_results = []
    files_to_process = []

    for filepath_str in sys.argv[1:]:
        filepath = Path(filepath_str)
        if not filepath.exists():
            print(f"Warning: Path not found: {filepath}", file=sys.stderr)
            continue

        if filepath.is_dir():
            # Find all nodes.tsv and edges.tsv files recursively
            files_to_process.extend(filepath.rglob('nodes.tsv'))
            files_to_process.extend(filepath.rglob('edges.tsv'))
        else:
            files_to_process.append(filepath)

    for filepath in files_to_process:
        # Extract source from path (e.g., "bacdive" from "../kg-microbe/data/transformed/bacdive/nodes.tsv")
        parts = filepath.parts
        if 'transformed' in parts:
            source_idx = parts.index('transformed') + 1
            source = parts[source_idx] if source_idx < len(parts) else 'unknown'
        else:
            source = 'unknown'

        results = analyze_tsv_file(filepath, source)
        all_results.extend(results)

    # Output using csv.writer for clean TSV
    writer = csv.writer(sys.stdout, delimiter='\t')
    writer.writerow(['source', 'file', 'column', 'curie_percentage', 'curie_count', 'non_null_count', 'total_rows'])

    # Output results sorted by source, percentage (descending), file, column
    for source, filename, col_name, percentage, curie_count, non_null, total_rows in sorted(all_results, key=lambda x: (x[0], -x[3], x[1], x[2])):
        writer.writerow([source, filename, col_name, f"{percentage:.2f}", curie_count, non_null, total_rows])


if __name__ == '__main__':
    main()
