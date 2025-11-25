"""Sample tax_id and ref_id values from madin collection."""

import csv
from pathlib import Path

import click
from pymongo import MongoClient
from rich.console import Console

console = Console()


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
    default=10,
    help="Number of samples to show",
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
    """Sample tax_id and ref_id values to understand their format."""
    client = MongoClient(mongo_uri)
    db = client[database]
    coll = db[collection]

    # Get sample documents with tax_id and ref_id
    console.print("[bold]Sample tax_id values:[/bold]")
    samples = list(
        coll.find(
            {"tax_id": {"$exists": True, "$ne": None}},
            {"org_name": 1, "tax_id": 1, "species_tax_id": 1},
        ).limit(sample_size)
    )

    for doc in samples:
        console.print(
            f"  org_name: {doc.get('org_name', 'N/A')[:50]}\n"
            f"  tax_id: {doc.get('tax_id')}\n"
            f"  species_tax_id: {doc.get('species_tax_id')}\n"
        )

    console.print("\n[bold]Sample ref_id values:[/bold]")
    samples = list(
        coll.find(
            {"ref_id": {"$exists": True, "$nin": [None, "NA"]}},
            {"org_name": 1, "ref_id": 1},
        ).limit(sample_size)
    )

    for doc in samples:
        ref_id = doc.get("ref_id", "N/A")
        # Truncate long ref_ids
        display_ref = ref_id if len(str(ref_id)) <= 100 else str(ref_id)[:97] + "..."
        console.print(
            f"  org_name: {doc.get('org_name', 'N/A')[:50]}\n  ref_id: {display_ref}\n"
        )

    # Save to TSV if requested
    if output_tsv:
        output_path = Path(output_tsv)
        with output_path.open("w", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(
                ["sample_type", "org_name", "tax_id", "species_tax_id", "ref_id"]
            )

            # Re-query to get all samples for TSV
            tax_samples = list(
                coll.find(
                    {"tax_id": {"$exists": True, "$ne": None}},
                    {"org_name": 1, "tax_id": 1, "species_tax_id": 1},
                ).limit(sample_size)
            )
            for doc in tax_samples:
                writer.writerow(
                    [
                        "tax_id_sample",
                        doc.get("org_name", "N/A"),
                        doc.get("tax_id", "N/A"),
                        doc.get("species_tax_id", "N/A"),
                        "",
                    ]
                )

            ref_samples = list(
                coll.find(
                    {"ref_id": {"$exists": True, "$nin": [None, "NA"]}},
                    {"org_name": 1, "ref_id": 1},
                ).limit(sample_size)
            )
            for doc in ref_samples:
                writer.writerow(
                    [
                        "ref_id_sample",
                        doc.get("org_name", "N/A"),
                        "",
                        "",
                        str(doc.get("ref_id", "N/A")),
                    ]
                )

        console.print(f"\n[green]Results saved to {output_path}[/green]")

    client.close()


if __name__ == "__main__":
    cli()
