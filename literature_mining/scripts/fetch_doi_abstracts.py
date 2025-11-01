#!/usr/bin/env python3
"""
Fetch abstracts for papers with DOIs but no PMIDs.

Reads publication_ids.tsv and fetches abstracts for papers where pmid='Not Found'.
Saves abstracts as individual text files in the abstracts/ directory.
"""

import csv
import re
from pathlib import Path
from typing import Optional, Dict

from artl_mcp.tools import get_europepmc_paper_by_id


def sanitize_doi_for_filename(doi: str) -> str:
    """
    Convert DOI to a safe filename.

    Examples:
        10.1038/nature16174 -> 10_1038_nature16174
        10.1016/j.jhazmat.2023.133217 -> 10_1016_j_jhazmat_2023_133217
    """
    return re.sub(r'[^a-zA-Z0-9_]', '_', doi)


def get_abstract_from_doi(doi: str) -> Optional[Dict]:
    """
    Fetch abstract from a DOI using artl-mcp's Europe PMC API.

    Args:
        doi: The DOI to fetch

    Returns:
        Dictionary with paper metadata including abstract, or None if not found
    """
    clean_doi = doi.strip()

    try:
        print(f"  Fetching: {clean_doi}...")
        data = get_europepmc_paper_by_id(clean_doi)

        if not data:
            print(f"    ✗ Not found in Europe PMC")
            return None

        # Check if we got an abstract
        abstract_text = data.get("abstractText", "")
        if not abstract_text:
            print(f"    ✗ No abstract available")
            return None

        title = data.get("title", "No title")
        pmid = data.get("pmid")

        print(f"    ✓ Found: {title[:60]}...")
        if pmid:
            print(f"    📌 PMID discovered: {pmid}")

        return {
            "doi": data.get("doi", clean_doi),
            "pmid": pmid,
            "pmcid": data.get("pmcid"),
            "title": title,
            "abstract": abstract_text,
            "authors": data.get("authorString", ""),
            "journal": data.get("journalTitle", ""),
            "year": data.get("pubYear", ""),
        }

    except Exception as e:
        print(f"    ✗ Error: {e}")
        return None


def fetch_doi_only_abstracts(
    publication_ids_file: Path,
    output_dir: Path,
    dry_run: bool = False
):
    """
    Fetch abstracts for papers with DOIs but no PMIDs.

    Args:
        publication_ids_file: Path to publication_ids.tsv
        output_dir: Directory to save abstract files
        dry_run: If True, don't write files (just report what would happen)
    """
    # Ensure output directory exists
    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Read publication IDs
    with open(publication_ids_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)

    # Filter for DOI-only papers
    doi_only_papers = [
        row for row in rows
        if row.get('pmid') == 'Not Found' and row.get('doi')
    ]

    print(f"Found {len(doi_only_papers)} papers with DOIs but no PMIDs\n")

    if not doi_only_papers:
        print("No papers to fetch!")
        return

    # Track results
    fetched = 0
    not_found = 0
    discovered_pmids = {}

    for i, row in enumerate(doi_only_papers, 1):
        doi = row['doi']
        print(f"[{i}/{len(doi_only_papers)}] DOI: {doi}")

        # Fetch abstract
        paper_data = get_abstract_from_doi(doi)

        if not paper_data:
            not_found += 1
            continue

        # Determine filename
        if paper_data.get('pmid'):
            # If we discovered a PMID, use it!
            filename = f"{paper_data['pmid']}-abstract.txt"
            discovered_pmids[doi] = paper_data['pmid']
        else:
            # Use sanitized DOI
            safe_doi = sanitize_doi_for_filename(doi)
            filename = f"doi_{safe_doi}-abstract.txt"

        output_path = output_dir / filename

        # Write abstract
        if not dry_run:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Title: {paper_data['title']}\n\n")
                f.write(f"Authors: {paper_data['authors']}\n\n")
                f.write(f"Journal: {paper_data['journal']} ({paper_data['year']})\n\n")
                f.write(f"DOI: {paper_data['doi']}\n")
                if paper_data.get('pmid'):
                    f.write(f"PMID: {paper_data['pmid']}\n")
                if paper_data.get('pmcid'):
                    f.write(f"PMCID: {paper_data['pmcid']}\n")
                f.write(f"\nAbstract:\n{paper_data['abstract']}\n")

            print(f"    💾 Saved to: {filename}")
        else:
            print(f"    [DRY RUN] Would save to: {filename}")

        fetched += 1
        print()

    # Summary
    print("=" * 60)
    print(f"Summary:")
    print(f"  ✓ Fetched: {fetched}")
    print(f"  ✗ Not found: {not_found}")

    if discovered_pmids:
        print(f"\n📌 Discovered {len(discovered_pmids)} PMIDs that were missing:")
        for doi, pmid in discovered_pmids.items():
            print(f"  {doi} -> PMID {pmid}")
        print("\nYou may want to update publication_ids.tsv with these PMIDs!")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch abstracts for papers with DOIs but no PMIDs"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("literature_mining/publication_ids.tsv"),
        help="Path to publication_ids.tsv (default: literature_mining/publication_ids.tsv)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("literature_mining/abstracts"),
        help="Directory to save abstracts (default: literature_mining/abstracts)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write files, just show what would happen"
    )

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        return 1

    fetch_doi_only_abstracts(args.input, args.output_dir, args.dry_run)
    return 0


if __name__ == "__main__":
    exit(main())
