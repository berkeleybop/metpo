#!/usr/bin/env python3
"""
Extract all unique prefixes from CURIE columns in TSV files.

For columns with high CURIE percentage (>90%), extracts all unique prefixes.
"""

import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import Set

CURIE_PATTERN = re.compile(r'^([^\s:]+):([^\s:]+)$')


def extract_prefixes_from_file(filepath: Path, columns: list) -> dict:
    """
    Extract unique prefixes from specified columns in a TSV file.

    Returns dict: {column_name: set_of_prefixes}
    """
    column_prefixes = defaultdict(set)

    with open(filepath, 'r') as f:
        # Read header
        header_line = f.readline().strip()
        headers = header_line.split('\t')

        # Map column names to indices
        col_indices = {col: i for i, col in enumerate(headers) if col in columns}

        # Process each data row
        for line in f:
            values = line.strip().split('\t')

            for col_name, col_idx in col_indices.items():
                if col_idx < len(values):
                    value = values[col_idx].strip()
                    match = CURIE_PATTERN.match(value)
                    if match:
                        prefix = match.group(1)
                        column_prefixes[col_name].add(prefix)

    return column_prefixes


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python extract_prefixes.py <file.tsv> [file2.tsv ...]", file=sys.stderr)
        sys.exit(1)

    # Columns to check (those with high CURIE percentages)
    curie_columns = ['id', 'subject', 'predicate', 'object', 'relation', 'category', 'primary_knowledge_source']

    all_prefixes = defaultdict(set)

    for filepath_str in sys.argv[1:]:
        filepath = Path(filepath_str)
        if not filepath.exists():
            print(f"Warning: File not found: {filepath}", file=sys.stderr)
            continue

        print(f"Extracting prefixes from {filepath}...", file=sys.stderr)
        file_prefixes = extract_prefixes_from_file(filepath, curie_columns)

        # Merge with overall results
        for col, prefixes in file_prefixes.items():
            all_prefixes[col].update(prefixes)

    # Output results
    print("column\tprefix\tcount")

    # Sort by column, then by prefix
    for col in sorted(all_prefixes.keys()):
        prefixes = sorted(all_prefixes[col])
        for prefix in prefixes:
            print(f"{col}\t{prefix}\t1")

    # Also output summary
    print("\n# Summary by column:", file=sys.stderr)
    for col in sorted(all_prefixes.keys()):
        print(f"# {col}: {len(all_prefixes[col])} unique prefixes", file=sys.stderr)

    # Output all unique prefixes across all columns
    all_unique_prefixes = set()
    for prefixes in all_prefixes.values():
        all_unique_prefixes.update(prefixes)

    print(f"\n# TOTAL UNIQUE PREFIXES: {len(all_unique_prefixes)}", file=sys.stderr)
    print("# All unique prefixes:", file=sys.stderr)
    for prefix in sorted(all_unique_prefixes):
        print(f"# {prefix}", file=sys.stderr)


if __name__ == '__main__':
    main()
