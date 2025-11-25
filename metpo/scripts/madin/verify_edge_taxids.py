"""Verify edge case tax_ids (min, max, and some specific values)."""

import csv
import time
from pathlib import Path

import click
import requests
from pymongo import MongoClient
from rich.console import Console
from rich.table import Table

console = Console()


def check_ncbi_taxid(tax_id: int) -> tuple[bool, str, str]:
    """Check if a tax_id exists in NCBI Taxonomy.

    Args:
        tax_id: NCBI Taxonomy ID to verify

    Returns:
        Tuple of (is_valid, scientific_name, rank)
    """
    try:
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {"db": "taxonomy", "id": tax_id, "retmode": "xml"}

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200 and "<ScientificName>" in response.text:
            # Extract scientific name
            start = response.text.find("<ScientificName>") + len("<ScientificName>")
            end = response.text.find("</ScientificName>", start)
            sci_name = response.text[start:end]

            # Extract rank
            rank = "unknown"
            if "<Rank>" in response.text:
                rank_start = response.text.find("<Rank>") + len("<Rank>")
                rank_end = response.text.find("</Rank>", rank_start)
                rank = response.text[rank_start:rank_end]

            return True, sci_name, rank
        else:
            return False, "NOT FOUND", "N/A"

    except Exception as e:
        return False, f"ERROR: {e}", "N/A"


@click.command()
@click.option(
    "--mongo-uri",
    default="mongodb://localhost:27017",
    help="MongoDB connection URI",
)
@click.option(
    "--database",
    default="madin",
    help="Database name",
)
@click.option(
    "--collection",
    default="madin",
    help="Collection name",
)
@click.option(
    "--output-tsv",
    type=click.Path(),
    help="Optional: Save results to TSV file",
)
def cli(mongo_uri: str, database: str, collection: str, output_tsv: str | None) -> None:
    """Verify edge case tax_ids."""
    client = MongoClient(mongo_uri)
    db = client[database]
    coll = db[collection]

    console.print("[bold]Verifying edge case tax_ids[/bold]\n")

    # Get min and max tax_ids
    min_doc = coll.find_one({"tax_id": {"$type": "number"}}, sort=[("tax_id", 1)])

    max_doc = coll.find_one({"tax_id": {"$type": "number"}}, sort=[("tax_id", -1)])

    # Get some common ones
    common_values = [1, 2, 7, 100, 287, 1280, 2714]  # Common bacteria/archaea tax_ids

    edge_cases = []

    if min_doc:
        edge_cases.append(("MIN", min_doc))

    if max_doc:
        edge_cases.append(("MAX", max_doc))

    # Add some documents with common values if they exist
    for val in common_values:
        doc = coll.find_one({"tax_id": val})
        if doc:
            edge_cases.append((f"tax_id={val}", doc))

    table = Table(title="Edge Case Tax_ID Validation")
    table.add_column("Case", style="cyan")
    table.add_column("tax_id", style="green")
    table.add_column("Madin org_name", style="yellow", no_wrap=False)
    table.add_column("Valid?", style="magenta")
    table.add_column("NCBI Name", style="white", no_wrap=False)
    table.add_column("NCBI Rank", style="blue")

    for case_type, doc in edge_cases:
        tax_id = doc.get("tax_id")
        org_name = doc.get("org_name", "")

        is_valid, ncbi_name, rank = check_ncbi_taxid(tax_id)

        table.add_row(
            case_type,
            str(tax_id),
            org_name[:30] if org_name else "N/A",
            "✓" if is_valid else "✗",
            ncbi_name[:40] if ncbi_name else "N/A",
            rank,
        )

        time.sleep(0.4)  # Rate limiting

    console.print(table)

    # Check if tax_id=7 is valid (should be Azorhizobium caulinodans)
    console.print("\n[bold]Special check for tax_id=7 (minimum value):[/bold]")
    is_valid, name, rank = check_ncbi_taxid(7)
    if is_valid:
        console.print(f"  ✓ tax_id=7 is valid: {name} (rank: {rank})")
        console.print(
            "  Note: Low tax_ids were assigned early in NCBI Taxonomy history"
        )
    else:
        console.print("  ✗ tax_id=7 not found in NCBI")

    # Save to TSV if requested
    if output_tsv:
        output_path = Path(output_tsv)
        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(
                [
                    "case_type",
                    "tax_id",
                    "madin_org_name",
                    "ncbi_valid",
                    "ncbi_name",
                    "ncbi_rank",
                ]
            )

            for case_type, doc in edge_cases:
                tax_id = doc.get("tax_id")
                org_name = doc.get("org_name", "")
                is_valid, ncbi_name, rank = check_ncbi_taxid(tax_id)

                writer.writerow(
                    [
                        case_type,
                        tax_id,
                        org_name,
                        "yes" if is_valid else "no",
                        ncbi_name,
                        rank,
                    ]
                )
                time.sleep(0.4)  # Rate limiting

        console.print(f"\n[green]Results saved to {output_path}[/green]")

    client.close()


if __name__ == "__main__":
    cli()
