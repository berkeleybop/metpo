#!/usr/bin/env python3
"""
Fetch abstracts from DOIs using artl-mcp's Europe PMC integration.

This script uses artl-mcp directly to retrieve abstracts for papers 
that have DOIs but not PMIDs.
"""

import json
from pathlib import Path
from typing import Optional

from artl_mcp.tools import get_europepmc_paper_by_id


def get_abstract_from_doi(doi: str) -> Optional[dict]:
    """
    Fetch abstract from a DOI using artl-mcp.
    
    Args:
        doi: The DOI to fetch (with or without "doi:" prefix)
    
    Returns:
        Dictionary with title, abstract, and metadata, or None if not found
    """
    # Clean the DOI
    clean_doi = doi.replace("doi:", "").replace("DOI:", "").strip()
    
    try:
        # Get paper data from Europe PMC
        data = get_europepmc_paper_by_id(clean_doi)
        
        if not data:
            return None
        
        return {
            "doi": data.get("doi", clean_doi),
            "pmid": data.get("pmid"),
            "pmcid": data.get("pmcid"),
            "title": data.get("title"),
            "abstract": data.get("abstractText"),
            "authors": data.get("authorString"),
            "journal": data.get("journalTitle"),
            "year": data.get("pubYear"),
            "source": "Europe PMC",
        }
        
    except Exception as e:
        print(f"Error fetching DOI {clean_doi}: {e}")
        return None


def fetch_abstracts_from_file(input_file: Path, output_file: Path, doi_column: str = "doi"):
    """
    Read DOIs from a TSV file and fetch abstracts.
    
    Args:
        input_file: Path to TSV file containing DOIs
        output_file: Path to write results (TSV format)
        doi_column: Name of the column containing DOIs
    """
    import csv
    
    with open(input_file, 'r') as f_in:
        reader = csv.DictReader(f_in, delimiter='\t')
        rows = list(reader)
    
    results = []
    for row in rows:
        doi = row.get(doi_column)
        if not doi:
            continue
        
        print(f"Fetching abstract for DOI: {doi}")
        abstract_data = get_abstract_from_doi(doi)
        
        if abstract_data:
            # Merge with original row
            result_row = {**row, **abstract_data}
            results.append(result_row)
            print(f"  ✓ Found: {abstract_data['title'][:60]}...")
        else:
            print(f"  ✗ Not found")
            results.append(row)
    
    # Write results
    if results:
        fieldnames = list(results[0].keys())
        with open(output_file, 'w', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\nWrote {len(results)} results to {output_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fetch abstracts from DOIs using Europe PMC"
    )
    parser.add_argument(
        "--doi",
        help="Single DOI to fetch"
    )
    parser.add_argument(
        "--input-file",
        type=Path,
        help="TSV file containing DOIs"
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Output TSV file (required with --input-file)"
    )
    parser.add_argument(
        "--doi-column",
        default="doi",
        help="Name of the DOI column in input file (default: doi)"
    )
    
    args = parser.parse_args()
    
    if args.doi:
        # Single DOI mode
        result = get_abstract_from_doi(args.doi)
        if result:
            print(json.dumps(result, indent=2))
        else:
            print("No abstract found")
            return 1
    
    elif args.input_file:
        # Batch mode
        if not args.output_file:
            print("Error: --output-file required with --input-file")
            return 1
        
        fetch_abstracts_from_file(args.input_file, args.output_file, args.doi_column)
    
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
