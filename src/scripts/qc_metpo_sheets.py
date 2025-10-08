#!/usr/bin/env python3
"""
Quality Control script for METPO Google Sheets templates.

Checks for:
1. ID clashes within and across sheets
2. Label clashes within and across sheets
3. Parent classes/properties referenced but not defined
4. Other structural issues

Usage:
    python qc_metpo_sheets.py metpo_sheet.tsv metpo-properties.tsv

    Or download directly from Google Sheets:
    python qc_metpo_sheets.py --download
"""

import sys
import csv
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import argparse
import urllib.request

GOOGLE_SHEET_ID = "1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU"
SHEET_GIDS = {
    "metpo_sheet": "355012485",
    "metpo-properties": "2094089867",
}

class QCIssue:
    def __init__(self, severity, category, message, location=""):
        self.severity = severity  # ERROR, WARNING, INFO
        self.category = category
        self.message = message
        self.location = location

    def __str__(self):
        loc = f" [{self.location}]" if self.location else ""
        return f"{self.severity}: {self.category}{loc}: {self.message}"


class SheetData:
    def __init__(self, filename):
        self.filename = filename
        self.rows = []
        self.ids = {}  # id -> (row_num, label, type, is_stub)
        self.labels = defaultdict(list)  # label -> [(row_num, id, type, is_stub)]
        self.parents = []  # [(row_num, id, parent_ref, type)]
        self.stubs = []  # [(row_num, id, label)] - stub definitions

    def load(self):
        """Load TSV file and extract key information."""
        with open(self.filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            for row_num, row in enumerate(reader, start=1):
                self.rows.append(row)

                # Skip header rows
                if row_num <= 2:
                    continue

                if len(row) < 3:
                    continue

                row_id = row[0].strip() if row[0] else ""
                label = row[1].strip() if len(row) > 1 and row[1] else ""
                row_type = row[2].strip() if len(row) > 2 and row[2] else ""
                comment = row[3].strip() if len(row) > 3 and row[3] else ""

                # Skip empty rows
                if not row_id and not label:
                    continue

                # Check if this is a stub definition
                is_stub = "stub" in comment.lower()
                if is_stub:
                    self.stubs.append((row_num, row_id, label))

                # Store ID mapping
                if row_id:
                    self.ids[row_id] = (row_num, label, row_type, is_stub)

                # Store label mapping
                if label and row_type in ['owl:Class', 'owl:ObjectProperty', 'owl:DataProperty', 'owl:AnnotationProperty']:
                    self.labels[label].append((row_num, row_id, row_type, is_stub))

                # Extract parent reference (column 3 for classes, column 6 for properties)
                parent_ref = ""
                if row_type == 'owl:Class' and len(row) > 3:
                    parent_ref = row[3].strip()
                elif row_type in ['owl:ObjectProperty', 'owl:DataProperty'] and len(row) > 6:
                    parent_ref = row[6].strip()

                if parent_ref and "stub" not in parent_ref.lower():  # Don't track stub as parent
                    self.parents.append((row_num, row_id, parent_ref, row_type))


def download_sheet(gid, output_file):
    """Download TSV from Google Sheets."""
    url = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?exportFormat=tsv&gid={gid}"
    print(f"Downloading {output_file} from Google Sheets...")
    urllib.request.urlretrieve(url, output_file)
    print(f"  ✓ Downloaded to {output_file}")


def check_id_clashes(sheets: List[SheetData]) -> List[QCIssue]:
    """Check for duplicate IDs within and across sheets."""
    issues = []
    all_ids = defaultdict(list)  # id -> [(sheet_name, row_num, label, type, is_stub)]

    for sheet in sheets:
        for id_val, (row_num, label, row_type, is_stub) in sheet.ids.items():
            all_ids[id_val].append((sheet.filename, row_num, label, row_type, is_stub))

    # Find duplicates
    for id_val, occurrences in all_ids.items():
        if len(occurrences) > 1:
            # Check if this is a legitimate stub + real definition pattern
            stub_count = sum(1 for _, _, _, _, is_stub in occurrences if is_stub)
            real_count = sum(1 for _, _, _, _, is_stub in occurrences if not is_stub)

            # If we have exactly one stub and one real definition across sheets, this is OK
            if stub_count > 0 and real_count > 0 and len(occurrences) == stub_count + real_count:
                # This is expected: stub in properties sheet, real definition in main sheet
                continue

            # Group by sheet
            by_sheet = defaultdict(list)
            for sheet_name, row_num, label, row_type, is_stub in occurrences:
                by_sheet[sheet_name].append((row_num, label, row_type, is_stub))

            if len(by_sheet) == 1:
                # Within same sheet
                sheet_name = list(by_sheet.keys())[0]
                locations = ", ".join([f"row {r}" for r, _, _, _ in by_sheet[sheet_name]])
                issues.append(QCIssue(
                    "ERROR",
                    "ID_CLASH_WITHIN_SHEET",
                    f"ID '{id_val}' appears {len(occurrences)} times in same sheet",
                    f"{sheet_name}: {locations}"
                ))
            else:
                # Across sheets - check if all are stubs or all are real
                all_stubs = all(is_stub for _, _, _, _, is_stub in occurrences)
                all_real = all(not is_stub for _, _, _, _, is_stub in occurrences)

                if all_stubs or all_real:
                    # Multiple stubs or multiple real definitions - this is an error
                    details = "; ".join([
                        f"{sheet}: rows {', '.join([f'{r} (' + ('stub' if s else 'real') + ')' for r, _, _, s in rows])}"
                        for sheet, rows in by_sheet.items()
                    ])
                    issues.append(QCIssue(
                        "ERROR",
                        "ID_CLASH_ACROSS_SHEETS",
                        f"ID '{id_val}' appears in multiple sheets (all {'stubs' if all_stubs else 'real definitions'})",
                        details
                    ))

    return issues


def check_label_clashes(sheets: List[SheetData]) -> List[QCIssue]:
    """Check for duplicate labels within and across sheets."""
    issues = []
    all_labels = defaultdict(list)  # label -> [(sheet_name, row_num, id, type, is_stub)]

    for sheet in sheets:
        for label, occurrences in sheet.labels.items():
            for row_num, id_val, row_type, is_stub in occurrences:
                all_labels[label].append((sheet.filename, row_num, id_val, row_type, is_stub))

    # Find duplicates
    for label, occurrences in all_labels.items():
        if len(occurrences) > 1:
            # Check if this is a legitimate stub + real definition pattern
            stub_count = sum(1 for _, _, _, _, is_stub in occurrences if is_stub)
            real_count = sum(1 for _, _, _, _, is_stub in occurrences if not is_stub)

            # If we have exactly one stub and one real definition across sheets, this is OK
            if stub_count > 0 and real_count > 0 and len(occurrences) == stub_count + real_count:
                # This is expected: stub in properties sheet, real definition in main sheet
                continue

            # Check if same type
            types = set(t for _, _, _, t, _ in occurrences)

            # Group by sheet
            by_sheet = defaultdict(list)
            for sheet_name, row_num, id_val, row_type, is_stub in occurrences:
                by_sheet[sheet_name].append((row_num, id_val, row_type, is_stub))

            severity = "ERROR" if len(types) > 1 else "WARNING"

            if len(by_sheet) == 1:
                # Within same sheet
                sheet_name = list(by_sheet.keys())[0]
                ids = [id_val for _, id_val, _, _ in by_sheet[sheet_name]]
                locations = ", ".join([f"row {r} ({id_val})" for r, id_val, _, _ in by_sheet[sheet_name]])

                issues.append(QCIssue(
                    severity,
                    "LABEL_CLASH_WITHIN_SHEET",
                    f"Label '{label}' appears {len(occurrences)} times in same sheet with IDs: {', '.join(ids)}",
                    f"{sheet_name}: {locations}"
                ))
            else:
                # Across sheets - check if all are stubs or all are real
                all_stubs = all(is_stub for _, _, _, _, is_stub in occurrences)
                all_real = all(not is_stub for _, _, _, _, is_stub in occurrences)

                if all_stubs or all_real:
                    # Multiple stubs or multiple real definitions - this is an error
                    details = "; ".join([
                        f"{sheet}: rows {', '.join([f'{r} ({id_val}, ' + ('stub' if s else 'real') + ')' for r, id_val, _, s in rows])}"
                        for sheet, rows in by_sheet.items()
                    ])
                    issues.append(QCIssue(
                        severity,
                        "LABEL_CLASH_ACROSS_SHEETS",
                        f"Label '{label}' appears in multiple sheets (all {'stubs' if all_stubs else 'real definitions'})",
                        details
                    ))

    return issues


def check_undefined_parents(sheets: List[SheetData]) -> List[QCIssue]:
    """Check for parent references that are not defined."""
    issues = []

    # Build combined ID and label index
    all_ids = set()
    all_labels = set()

    for sheet in sheets:
        all_ids.update(sheet.ids.keys())
        all_labels.update(sheet.labels.keys())

    # Check each parent reference
    for sheet in sheets:
        for row_num, id_val, parent_ref, row_type in sheet.parents:
            # Skip empty parents
            if not parent_ref:
                continue

            # Skip comment-only rows (stubs)
            if "stub" in parent_ref.lower():
                continue

            # Check if parent is defined (could be ID or label)
            is_id = parent_ref.startswith("METPO:") or ":" in parent_ref
            is_label = not is_id

            if is_id and parent_ref not in all_ids:
                issues.append(QCIssue(
                    "ERROR",
                    "UNDEFINED_PARENT_ID",
                    f"Parent ID '{parent_ref}' not defined anywhere",
                    f"{sheet.filename}: row {row_num}, ID {id_val}"
                ))
            elif is_label and parent_ref not in all_labels:
                issues.append(QCIssue(
                    "WARNING",
                    "UNDEFINED_PARENT_LABEL",
                    f"Parent label '{parent_ref}' not defined anywhere (using labels for parents may cause issues)",
                    f"{sheet.filename}: row {row_num}, ID {id_val}"
                ))

            # Check for self-referential parents
            # Get the label for this ID
            current_label = sheet.ids.get(id_val, (None, None, None))[1]
            if parent_ref == id_val:
                issues.append(QCIssue(
                    "ERROR",
                    "SELF_REFERENTIAL_PARENT_ID",
                    f"Parent references itself via ID",
                    f"{sheet.filename}: row {row_num}, ID {id_val}"
                ))
            elif parent_ref == current_label:
                issues.append(QCIssue(
                    "ERROR",
                    "SELF_REFERENTIAL_PARENT_LABEL",
                    f"Parent references itself via label '{parent_ref}'",
                    f"{sheet.filename}: row {row_num}, ID {id_val}"
                ))

    return issues


def check_structural_issues(sheets: List[SheetData]) -> List[QCIssue]:
    """Check for other structural issues."""
    issues = []

    for sheet in sheets:
        for row_num, row in enumerate(sheet.rows, start=1):
            if row_num <= 2:  # Skip headers
                continue

            if len(row) < 3:
                continue

            id_val = row[0].strip() if row[0] else ""
            label = row[1].strip() if len(row) > 1 and row[1] else ""
            row_type = row[2].strip() if len(row) > 2 and row[2] else ""

            # Skip empty rows
            if not id_val and not label:
                continue

            # Check for missing ID
            if not id_val and row_type in ['owl:Class', 'owl:ObjectProperty', 'owl:DataProperty']:
                issues.append(QCIssue(
                    "ERROR",
                    "MISSING_ID",
                    f"Row has label '{label}' but no ID",
                    f"{sheet.filename}: row {row_num}"
                ))

            # Check for missing label
            if id_val and not label and row_type in ['owl:Class', 'owl:ObjectProperty', 'owl:DataProperty']:
                issues.append(QCIssue(
                    "WARNING",
                    "MISSING_LABEL",
                    f"ID '{id_val}' has no label",
                    f"{sheet.filename}: row {row_num}"
                ))

            # Check ID format
            if id_val and not id_val.startswith("METPO:") and not id_val.startswith("IAO:") and row_type != "":
                issues.append(QCIssue(
                    "WARNING",
                    "NON_METPO_ID",
                    f"ID '{id_val}' doesn't start with METPO: or IAO:",
                    f"{sheet.filename}: row {row_num}"
                ))

    return issues


def main():
    parser = argparse.ArgumentParser(description="QC checks for METPO templates")
    parser.add_argument("--download", action="store_true", help="Download sheets from Google")
    parser.add_argument("files", nargs="*", help="TSV files to check (if not using --download)")

    args = parser.parse_args()

    if args.download:
        files = []
        for name, gid in SHEET_GIDS.items():
            filename = f"/tmp/{name}.tsv"
            download_sheet(gid, filename)
            files.append(filename)
    else:
        if len(args.files) < 2:
            print("Usage: python qc_metpo_sheets.py metpo_sheet.tsv metpo-properties.tsv")
            print("   or: python qc_metpo_sheets.py --download")
            sys.exit(1)
        files = args.files

    print("\n" + "="*80)
    print("METPO Sheet Quality Control")
    print("="*80 + "\n")

    # Load sheets
    sheets = []
    for filename in files:
        print(f"Loading {filename}...")
        sheet = SheetData(filename)
        sheet.load()
        sheets.append(sheet)
        print(f"  ✓ {len(sheet.ids)} entities ({len(sheet.stubs)} stubs), {len(sheet.parents)} parent references\n")

    # Run checks
    all_issues = []

    print("Checking for ID clashes...")
    all_issues.extend(check_id_clashes(sheets))

    print("Checking for label clashes...")
    all_issues.extend(check_label_clashes(sheets))

    print("Checking for undefined parents...")
    all_issues.extend(check_undefined_parents(sheets))

    print("Checking for structural issues...")
    all_issues.extend(check_structural_issues(sheets))

    # Report results
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80 + "\n")

    if not all_issues:
        print("✅ No issues found!\n")
        return 0

    # Group by severity
    errors = [i for i in all_issues if i.severity == "ERROR"]
    warnings = [i for i in all_issues if i.severity == "WARNING"]
    infos = [i for i in all_issues if i.severity == "INFO"]

    if errors:
        print(f"❌ {len(errors)} ERROR(S):")
        print("-" * 80)
        for issue in errors:
            print(f"  {issue}")
        print()

    if warnings:
        print(f"⚠️  {len(warnings)} WARNING(S):")
        print("-" * 80)
        for issue in warnings:
            print(f"  {issue}")
        print()

    if infos:
        print(f"ℹ️  {len(infos)} INFO:")
        print("-" * 80)
        for issue in infos:
            print(f"  {issue}")
        print()

    # Summary
    print("="*80)
    print(f"Summary: {len(errors)} errors, {len(warnings)} warnings, {len(infos)} info")
    print("="*80 + "\n")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
