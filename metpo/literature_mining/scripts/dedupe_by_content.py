#!/usr/bin/env python3
"""
Deduplicate abstracts by comparing content, not just filenames.

Uses PMID/DOI matching and text similarity to find duplicates.
"""

import re
import click
from pathlib import Path
from typing import Dict, Set, Tuple
from collections import defaultdict


def extract_identifiers(filepath: Path) -> Tuple[str, str, str]:
    """
    Extract PMID, DOI, and normalized abstract text.

    Returns:
        (pmid, doi, normalized_abstract_text)
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract PMID
    pmid_match = re.search(r"PMID:\s*(\d+)", content)
    pmid = pmid_match.group(1) if pmid_match else None

    # Extract DOI
    doi_match = re.search(r"DOI:\s*(10\.\S+)", content)
    doi = doi_match.group(1) if doi_match else None

    # Extract and normalize abstract text
    abstract_match = re.search(r"Abstract:\n(.+)", content, re.DOTALL)
    if abstract_match:
        abstract = abstract_match.group(1)
        # Normalize: lowercase, remove extra whitespace, remove HTML tags
        abstract = re.sub(r"<[^>]+>", "", abstract)  # Remove HTML
        abstract = re.sub(r"\s+", " ", abstract)  # Normalize whitespace
        abstract = abstract.lower().strip()
    else:
        abstract = None

    return pmid, doi, abstract


def find_duplicates(source_dirs):
    """
    Find duplicate abstracts across directories.

    Returns:
        Dictionary mapping canonical file to list of duplicates
    """
    # Group files by identifier
    by_pmid = defaultdict(list)
    by_doi = defaultdict(list)
    by_text_hash = defaultdict(list)

    all_files = []
    for source_dir in source_dirs:
        source_path = Path(source_dir)
        if not source_path.exists():
            continue
        all_files.extend(source_path.glob("*-abstract.txt"))

    print(f"Analyzing {len(all_files)} files...")

    for filepath in all_files:
        pmid, doi, abstract = extract_identifiers(filepath)

        # Group by PMID
        if pmid:
            by_pmid[pmid].append(filepath)

        # Group by DOI
        if doi:
            by_doi[doi].append(filepath)

        # Group by text hash (first 500 chars as proxy)
        if abstract:
            text_hash = abstract[:500]
            by_text_hash[text_hash].append(filepath)

    # Find duplicates
    duplicates = {}  # canonical -> [duplicates]

    # PMID-based duplicates
    for pmid, files in by_pmid.items():
        if len(files) > 1:
            # Keep the first one as canonical
            canonical = files[0]
            dupes = files[1:]
            if canonical not in duplicates:
                duplicates[canonical] = []
            duplicates[canonical].extend(dupes)

    # DOI-based duplicates (only for files not already caught by PMID)
    for doi, files in by_doi.items():
        if len(files) > 1:
            # Filter out already-found duplicates
            remaining = [f for f in files if f not in duplicates and
                        f not in [d for dlist in duplicates.values() for d in dlist]]

            if len(remaining) > 1:
                canonical = remaining[0]
                dupes = remaining[1:]
                if canonical not in duplicates:
                    duplicates[canonical] = []
                duplicates[canonical].extend(dupes)

    # Text-based duplicates (for remaining files)
    for text_hash, files in by_text_hash.items():
        if len(files) > 1:
            # Filter out already-found duplicates
            remaining = [f for f in files if f not in duplicates and
                        f not in [d for dlist in duplicates.values() for d in dlist]]

            if len(remaining) > 1:
                canonical = remaining[0]
                dupes = remaining[1:]
                if canonical not in duplicates:
                    duplicates[canonical] = []
                duplicates[canonical].extend(dupes)

    return duplicates, all_files


@click.command()
@click.option("--source-dirs", multiple=True,
              default=["literature_mining/abstracts", "literature_mining/cmm_pfas_abstracts"],
              help="Source directories to scan (can specify multiple)", show_default=True)
@click.option("--show-details", is_flag=True,
              help="Show details of each duplicate group")
def main(source_dirs, show_details):
    """Find duplicate abstracts by content comparison.

    Scans abstract files and identifies duplicates based on content similarity,
    even when filenames differ.
    """
    args = type("Args", (), {
        "source_dirs": source_dirs,
        "show_details": show_details
    })()

    duplicates, all_files = find_duplicates(args.source_dirs)

    print(f"\n{'='*70}")
    print("DEDUPLICATION RESULTS")
    print(f"{'='*70}")

    total_files = len(all_files)
    duplicate_files = sum(len(dupes) for dupes in duplicates.values())
    unique_files = total_files - duplicate_files

    print(f"\nTotal files scanned: {total_files}")
    print(f"Duplicate files found: {duplicate_files}")
    print(f"Unique files: {unique_files}")
    print(f"Duplicate groups: {len(duplicates)}")

    if args.show_details and duplicates:
        print(f"\n{'='*70}")
        print("DUPLICATE GROUPS")
        print(f"{'='*70}")

        for i, (canonical, dupes) in enumerate(duplicates.items(), 1):
            pmid, doi, _ = extract_identifiers(canonical)

            print(f"\nGroup {i}:")
            print(f"  Canonical: {canonical.name}")
            if pmid:
                print(f"  PMID: {pmid}")
            if doi:
                print(f"  DOI: {doi}")
            print(f"  Duplicates ({len(dupes)}):")
            for dupe in dupes:
                print(f"    - {dupe.name} (from {dupe.parent.name}/)")


if __name__ == "__main__":
    main()
