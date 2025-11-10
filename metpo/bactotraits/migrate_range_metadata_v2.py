#!/usr/bin/env python3
"""
Migrate range metadata from bactotraits.tsv to minimal_classes.tsv.

Creates separate columns for:
- measurement_unit_ucum (UCUM unit codes)
- range_min (numeric)
- range_max (numeric)
- equivalent_class_formula (Google Sheets formula)
"""

import csv
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple


def normalize_id(id_str: str) -> str:
    """Convert various ID formats to METPO:XXXXXXX format."""
    if id_str.startswith("https://w3id.org/metpo/"):
        return f"METPO:{id_str.split('/')[-1]}"
    if id_str.startswith("METPO:"):
        return id_str
    if id_str.isdigit():
        return f"METPO:{id_str}"
    return id_str


def map_unit_to_ucum(bactotraits_unit: str, class_label: str = '') -> str:
    """
    Map BactoTraits unit notation to UCUM codes.

    pH and GC are unitless, return empty string.
    Uses class label as fallback for incorrect unit values.
    """
    unit = bactotraits_unit.strip()

    # Infer from class label if unit seems wrong
    label_lower = class_label.lower()

    if 'nacl' in label_lower or 'salt' in label_lower:
        # NaCl classes should be % (percent)
        return '%'

    if 'temperature' in label_lower or 'temp' in label_lower:
        # Temperature classes should be Cel (Celsius)
        return 'Cel'

    if 'ph ' in label_lower or label_lower.startswith('ph '):
        # pH is unitless
        return ''

    if 'gc ' in label_lower or label_lower.startswith('gc ') or 'gc content' in label_lower:
        # GC content is unitless
        return ''

    # Otherwise use the provided unit
    # Temperature
    if unit == 'C':
        return 'Cel'

    # NaCl concentration
    if unit == '% NaCl':
        return '%'

    # Unitless quantities
    if unit in ['pH', '% GC']:
        return ''

    # Unknown or empty
    return ''


def load_range_metadata(bactotraits_path: Path) -> Dict[str, Dict[str, str]]:
    """Load range metadata from bactotraits.tsv."""
    range_data = {}

    with open(bactotraits_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            first_col = row.get('First column', '').strip()
            if not first_col or first_col == 'First column':
                continue

            class_id = normalize_id(first_col)

            # Get raw values
            label = row.get('Values', '').strip()
            units_raw = row.get('Units', '').strip()
            range_min = row.get('RangeMins', '').strip()
            range_max = row.get('RangeMaxes', '').strip()

            # Map to UCUM (using label as fallback)
            ucum_unit = map_unit_to_ucum(units_raw, label)

            # Only include if there's range data
            if range_min or range_max:
                range_data[class_id] = {
                    'label': label,
                    'unit_raw': units_raw,
                    'unit_ucum': ucum_unit,
                    'range_min': range_min,
                    'range_max': range_max
                }

    return range_data


def generate_google_sheets_formula(row_number: int,
                                   min_col: str,
                                   max_col: str) -> str:
    """
    Generate Google Sheets formula for equivalent_class_formula column.

    Args:
        row_number: The row number in the sheet (e.g., 3 for first data row)
        min_col: Column letter for range_min (e.g., 'P')
        max_col: Column letter for range_max (e.g., 'Q')

    Returns:
        Formula string like: =IF(AND(...), ...)
    """
    # Using Google Sheets references
    min_ref = f"{min_col}{row_number}"
    max_ref = f"{max_col}{row_number}"

    formula = (
        f'=IF(AND(NOT(ISBLANK({min_ref})), NOT(ISBLANK({max_ref}))), '
        f'"\'has measurement value\' some float[>= " & {min_ref} & " , <= " & {max_ref} & "]", '
        f'IF(NOT(ISBLANK({max_ref})), '
        f'"\'has measurement value\' some float[<= " & {max_ref} & "]", '
        f'IF(NOT(ISBLANK({min_ref})), '
        f'"\'has measurement value\' some float[>= " & {min_ref} & "]", '
        f'"")))'
    )

    return formula


def enhance_minimal_classes(minimal_path: Path,
                            range_data: Dict[str, Dict[str, str]],
                            output_path: Path,
                            dry_run: bool = True):
    """
    Add range metadata columns to minimal_classes.tsv.
    """
    rows = []
    header = None
    stats = {'total': 0, 'enhanced': 0, 'skipped': 0}

    # Read existing data
    with open(minimal_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        header = list(reader.fieldnames)

        for idx, row in enumerate(reader):
            class_id = row.get('ID', '').strip()

            if class_id and class_id != 'ID':
                stats['total'] += 1
                normalized_id = normalize_id(class_id)

                # Add range metadata if available
                if normalized_id in range_data:
                    metadata = range_data[normalized_id]
                    row['measurement_unit_ucum'] = metadata['unit_ucum']
                    row['range_min'] = metadata['range_min']
                    row['range_max'] = metadata['range_max']

                    # For TSV export, we'll use the computed value instead of formula
                    # User will add formula in Google Sheets
                    if metadata['range_min'] and metadata['range_max']:
                        equiv = f"'has measurement value' some float[>= {metadata['range_min']} , <= {metadata['range_max']}]"
                    elif metadata['range_max']:
                        equiv = f"'has measurement value' some float[<= {metadata['range_max']}]"
                    elif metadata['range_min']:
                        equiv = f"'has measurement value' some float[>= {metadata['range_min']}]"
                    else:
                        equiv = ""

                    row['equivalent_class_formula'] = equiv
                    stats['enhanced'] += 1

                    if dry_run:
                        label = row.get('label', '')[:40]
                        print(f"✓ {class_id}: {label:<40}")
                        if metadata['unit_raw'] and metadata['unit_raw'] != metadata.get('label', ''):
                            print(f"  Unit: {metadata['unit_raw']:<10} → {metadata['unit_ucum']}")
                        else:
                            print(f"  Unit: {metadata['unit_ucum']}")
                        print(f"  Range: [{metadata['range_min']}, {metadata['range_max']}]")
                        print(f"  Axiom: {equiv}")
                        print()
                else:
                    row['measurement_unit_ucum'] = ''
                    row['range_min'] = ''
                    row['range_max'] = ''
                    row['equivalent_class_formula'] = ''
                    stats['skipped'] += 1

            rows.append(row)

    # Write enhanced data
    if not dry_run:
        # Add new columns to header
        new_columns = ['measurement_unit_ucum', 'range_min', 'range_max', 'equivalent_class_formula']
        new_header = list(header) + new_columns

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=new_header, delimiter='\t', extrasaction='ignore')
            writer.writeheader()

            # Write ROBOT template row
            robot_row = {col: '' for col in new_header}
            robot_row.update({
                'ID': 'ID',
                'label': 'LABEL',
                'TYPE': 'TYPE',
                'parent class': 'SC %',
                'description': 'A IAO:0000115',
                'measurement_unit_ucum': '',  # blank - not used in ROBOT
                'range_min': '',  # blank - not used in ROBOT
                'range_max': '',  # blank - not used in ROBOT
                'equivalent_class_formula': 'EC %'  # ROBOT directive
            })

            # Preserve existing ROBOT directives
            for col in header:
                if col in ['definition source', 'comment', 'biolink equivalent']:
                    robot_row[col] = rows[0].get(col, '') if rows else ''

            writer.writerow(robot_row)

            # Write data rows (skip original ROBOT template row)
            for row in rows:
                if row.get('ID') != 'ID':
                    writer.writerow(row)

        print(f"\n✓ Enhanced minimal_classes.tsv written to: {output_path}")

    return stats


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Migrate range metadata to minimal_classes.tsv')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Preview changes without writing (default: True)')
    parser.add_argument('--execute', action='store_true',
                        help='Actually write the enhanced file')
    parser.add_argument('--bactotraits', type=Path,
                        default=Path('/Users/MAM/Documents/gitrepos/metpo/downloads/sheets/bactotraits.tsv'),
                        help='Path to bactotraits.tsv')
    parser.add_argument('--minimal', type=Path,
                        default=Path('/Users/MAM/Documents/gitrepos/metpo/downloads/sheets/minimal_classes.tsv'),
                        help='Path to minimal_classes.tsv')
    parser.add_argument('--output', type=Path,
                        default=Path('/Users/MAM/Documents/gitrepos/metpo/downloads/sheets/minimal_classes_enhanced.tsv'),
                        help='Output path for enhanced file')

    args = parser.parse_args()

    dry_run = not args.execute

    print("="*80)
    print("Range Metadata Migration Tool v2")
    print("Column-based approach with Google Sheets formula support")
    print("="*80)
    print(f"Mode: {'DRY RUN (preview only)' if dry_run else 'EXECUTE (will write file)'}")
    print()

    # Load range metadata
    print("Loading range metadata from bactotraits.tsv...")
    range_data = load_range_metadata(args.bactotraits)
    print(f"Found {len(range_data)} classes with range metadata")
    print()

    # Enhance minimal_classes
    print("Processing minimal_classes.tsv...")
    if dry_run:
        print("\nPreview of changes (first 5 classes):")
        print("-" * 80)

    stats = enhance_minimal_classes(args.minimal, range_data, args.output, dry_run)

    print()
    print("="*80)
    print("Summary")
    print("="*80)
    print(f"Total classes in minimal_classes.tsv: {stats['total']}")
    print(f"Classes enhanced with ranges: {stats['enhanced']}")
    print(f"Classes without ranges: {stats['skipped']}")

    if dry_run:
        print()
        print("ℹ️  This was a DRY RUN. No files were modified.")
        print(f"To execute: python {Path(__file__).name} --execute")
    else:
        print()
        print(f"✓ Enhanced file written to: {args.output}")
        print()
        print("Next steps:")
        print("1. Review the enhanced TSV file")
        print("2. Import to Google Sheets:")
        print("   - Open minimal_classes sheet")
        print("   - Add 4 new columns: measurement_unit_ucum, range_min, range_max, equivalent_class_formula")
        print("   - Copy data from enhanced TSV")
        print("3. IMPORTANT: Add Google Sheets formula to equivalent_class_formula column:")
        print("   Formula: =IF(AND(NOT(ISBLANK(range_min)), NOT(ISBLANK(range_max))),")
        print('            "\'has measurement value\' some float[>= " & range_min & " , <= " & range_max & "]", "")')
        print("4. Test download: make download-all-sheets")
        print("5. Test build: cd src/ontology && make metpo.owl")


if __name__ == "__main__":
    main()
