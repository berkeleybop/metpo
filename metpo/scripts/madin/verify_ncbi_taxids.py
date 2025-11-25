"""Verify that madin tax_ids are valid NCBI Taxonomy IDs by checking a sample."""

import csv
import time
from pathlib import Path

import click
import requests
from pymongo import MongoClient
from rich.console import Console
from rich.table import Table

console = Console()


def check_ncbi_taxid(tax_id: int) -> tuple[bool, str]:
    """Check if a tax_id exists in NCBI Taxonomy.

    Args:
        tax_id: NCBI Taxonomy ID to verify

    Returns:
        Tuple of (is_valid, scientific_name)
    """
    try:
        # Use NCBI E-utilities API
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {"db": "taxonomy", "id": tax_id, "retmode": "xml"}

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200 and "<ScientificName>" in response.text:
            # Extract scientific name
            start = response.text.find("<ScientificName>") + len("<ScientificName>")
            end = response.text.find("</ScientificName>", start)
            sci_name = response.text[start:end]
            return True, sci_name
        else:
            return False, "NOT FOUND"

    except Exception as e:
        return False, f"ERROR: {e}"


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
    "--sample-size",
    default=20,
    help="Number of random tax_ids to verify",
)
@click.option(
    "--output-tsv",
    type=click.Path(),
    help="Optional: Save results to TSV file",
)
def cli(
    mongo_uri: str,
    database: str,
    collection: str,
    sample_size: int,
    output_tsv: str | None,
) -> None:
    """Verify random sample of tax_ids against NCBI Taxonomy API."""
    client = MongoClient(mongo_uri)
    db = client[database]
    coll = db[collection]

    console.print(
        f"[bold]Verifying {sample_size} random tax_ids against NCBI Taxonomy API[/bold]\n"
    )
    console.print(
        "[yellow]Note: This will make API calls to NCBI (rate-limited)[/yellow]\n"
    )

    # Get random sample of documents with diverse tax_ids
    pipeline = [
        {"$match": {"tax_id": {"$exists": True, "$ne": None}}},
        {"$sample": {"size": sample_size}},
    ]

    samples = list(coll.aggregate(pipeline))

    table = Table(title="NCBI Taxonomy Validation")
    table.add_column("Madin tax_id", style="cyan")
    table.add_column("Madin org_name", style="green", no_wrap=False)
    table.add_column("NCBI Valid?", style="yellow")
    table.add_column("NCBI ScientificName", style="magenta", no_wrap=False)
    table.add_column("Match?", style="white")

    valid_count = 0
    name_match_count = 0

    for i, doc in enumerate(samples):
        tax_id = doc.get("tax_id")
        org_name = doc.get("org_name", "")

        # Check against NCBI
        is_valid, ncbi_name = check_ncbi_taxid(tax_id)

        if is_valid:
            valid_count += 1

        # Check if names match (loosely)
        names_match = "?"
        if is_valid and ncbi_name != "NOT FOUND":
            # Normalize for comparison
            madin_norm = org_name.lower().strip()
            ncbi_norm = ncbi_name.lower().strip()

            if madin_norm == ncbi_norm:
                names_match = "✓"
                name_match_count += 1
            elif madin_norm in ncbi_norm or ncbi_norm in madin_norm:
                names_match = "~"
                name_match_count += 0.5
            else:
                names_match = "✗"

        table.add_row(
            str(tax_id),
            org_name[:40],
            "✓" if is_valid else "✗",
            ncbi_name[:40] if ncbi_name else "N/A",
            names_match,
        )

        # Rate limiting - NCBI allows 3 requests/second without API key
        if i < len(samples) - 1:
            time.sleep(0.4)

    console.print(table)

    console.print("\n[bold]Summary:[/bold]")
    console.print(f"  Samples checked: {len(samples)}")
    console.print(
        f"  Valid NCBI tax_ids: {valid_count}/{len(samples)} ({valid_count / len(samples) * 100:.1f}%)"
    )
    console.print(
        f"  Name matches: {name_match_count}/{len(samples)} ({name_match_count / len(samples) * 100:.1f}%)"
    )

    if valid_count == len(samples):
        console.print(
            "\n[green]✓ All sampled tax_ids are valid NCBI Taxonomy IDs![/green]"
        )
    else:
        console.print(
            f"\n[red]✗ {len(samples) - valid_count} tax_ids not found in NCBI[/red]"
        )

    # Save to TSV if requested
    if output_tsv:
        output_path = Path(output_tsv)
        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(
                [
                    "madin_tax_id",
                    "madin_org_name",
                    "ncbi_valid",
                    "ncbi_scientific_name",
                    "names_match",
                ]
            )

            # Re-process samples for TSV output
            for doc in samples:
                tax_id = doc.get("tax_id")
                org_name = doc.get("org_name", "")

                is_valid, ncbi_name = check_ncbi_taxid(tax_id)

                names_match = "unknown"
                if is_valid and ncbi_name != "NOT FOUND":
                    madin_norm = org_name.lower().strip()
                    ncbi_norm = ncbi_name.lower().strip()

                    if madin_norm == ncbi_norm:
                        names_match = "exact"
                    elif madin_norm in ncbi_norm or ncbi_norm in madin_norm:
                        names_match = "partial"
                    else:
                        names_match = "no"

                writer.writerow(
                    [
                        tax_id,
                        org_name,
                        "yes" if is_valid else "no",
                        ncbi_name,
                        names_match,
                    ]
                )

                time.sleep(0.4)  # Rate limiting

        console.print(f"\n[green]Results saved to {output_path}[/green]")

    client.close()


if __name__ == "__main__":
    cli()
