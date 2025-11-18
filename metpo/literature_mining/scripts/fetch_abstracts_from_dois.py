"""
Fetch abstracts from DOIs using artl-mcp's Europe PMC integration.

This script uses artl-mcp directly to retrieve abstracts for papers
that have DOIs but not PMIDs.
"""

import json
from pathlib import Path

import click
from artl_mcp.tools import get_europepmc_paper_by_id


def get_abstract_from_doi(doi: str) -> dict | None:
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

    with Path(input_file).open() as f_in:
        reader = csv.DictReader(f_in, delimiter="\t")
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
            print("  ✗ Not found")
            results.append(row)

    # Write results
    if results:
        fieldnames = list(results[0].keys())
        with Path(output_file).open("w", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()
            writer.writerows(results)

        print(f"\nWrote {len(results)} results to {output_file}")


@click.command()
@click.option("--doi", help="Single DOI to fetch and print to stdout")
@click.option(
    "--input-file",
    type=click.Path(exists=True, path_type=Path),
    help="TSV file containing DOIs (batch mode)",
)
@click.option(
    "--output-file",
    type=click.Path(path_type=Path),
    help="Output TSV file (required with --input-file)",
)
@click.option(
    "--doi-column", default="doi", show_default=True, help="Name of the DOI column in input file"
)
def main(doi, input_file, output_file, doi_column):
    """Fetch abstracts from DOIs using Europe PMC API via artl-mcp.

    Two modes of operation:

    1. Single DOI mode: --doi DOI_STRING (prints JSON to stdout)

    2. Batch mode: --input-file FILE --output-file FILE
    """
    if doi:
        # Single DOI mode
        result = get_abstract_from_doi(doi)
        if result:
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo("No abstract found", err=True)
            raise click.Abort

    elif input_file:
        # Batch mode
        if not output_file:
            click.echo("Error: --output-file required with --input-file", err=True)
            raise click.Abort

        fetch_abstracts_from_file(input_file, output_file, doi_column)

    else:
        click.echo("Error: Must provide either --doi or --input-file", err=True)
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        raise click.Abort


if __name__ == "__main__":
    main()
