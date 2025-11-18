#!/usr/bin/env python3
"""Regenerate curator_proposed_definitions.tsv from undergraduate source files"""

import csv
import os
from pathlib import Path

# Curator info mapping
curator_info = {
    'curator4_all_terms.tsv': {'number': 4, 'name': 'Anthea Guo', 'github': 'crocodile27'},
    'curator5_all_terms_v3.tsv': {'number': 5, 'name': 'Jed Dongjin Kim-Ozaeta', 'github': 'jedkim-ozaeta'},
    'curator6_all_terms.tsv': {'number': 6, 'name': 'Luke Wang', 'github': 'lukewangCS121'},
}

# Get script directory and repo root
script_dir = Path(__file__).parent
repo_root = script_dir.parent.parent.parent

# Directory with curator files
curator_dir = repo_root / 'data' / 'undergraduate_definitions'

# Output file
output_file = repo_root / 'data' / 'undergraduate_definitions' / 'curator_proposed_definitions.tsv'

# Collect all rows
all_rows = []

for filename, info in curator_info.items():
    filepath = curator_dir / filename

    if not filepath.exists():
        print(f"Warning: {filepath} not found")
        continue

    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Skip header rows (both say "ID")
    # Data starts at line 3 (index 2)
    header = lines[0].strip().split('\t')

    reader = csv.DictReader(lines[2:], delimiter='\t', fieldnames=header)

    for row in reader:
        metpo_id = row.get('ID', '').strip()
        if not metpo_id or not metpo_id.startswith('METPO:'):
            continue

        # Create output row with original data exactly as provided
        # Handle None values from row.get()
        def safe_get(d, key, default=''):
            val = d.get(key, default)
            return val.strip() if val else default

        output_row = {
            'metpo_id': metpo_id,
            'label': safe_get(row, 'label'),
            'curator_number': info['number'],
            'curator_name': info['name'],
            'github_handle': info['github'],
            'proposed_definition': safe_get(row, 'description'),
            'definition_source': safe_get(row, 'definition source'),
            'has_definition_source': 'Yes' if safe_get(row, 'definition source') else 'No',
            'subclass_of_label': safe_get(row, 'parent class'),
            'subclass_of_id': safe_get(row, 'parent classes (one strongly preferred)'),
            'reasoning': safe_get(row, 'comment'),
            'quantitative_values': safe_get(row, 'quantitative_values'),
        }

        all_rows.append(output_row)

# Sort by metpo_id
all_rows.sort(key=lambda x: x['metpo_id'])

# Write to output file
fieldnames = [
    'metpo_id',
    'label',
    'curator_number',
    'curator_name',
    'github_handle',
    'proposed_definition',
    'definition_source',
    'has_definition_source',
    'subclass_of_label',
    'subclass_of_id',
    'reasoning',
    'quantitative_values'
]

with open(output_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()
    writer.writerows(all_rows)

print(f"✓ Regenerated {output_file}")
print(f"  Total rows: {len(all_rows)}")
print(f"  Unique terms: {len(set(r['metpo_id'] for r in all_rows))}")
