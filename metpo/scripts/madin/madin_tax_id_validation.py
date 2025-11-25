"""Validate tax_id consistency with NCBI Taxonomy."""

import csv
from pathlib import Path

import click
from pymongo import MongoClient
from rich.console import Console
from rich.table import Table

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
    "--output-tsv",
    type=click.Path(),
    help="Optional: Save analysis summary to TSV file",
)
def cli(mongo_uri: str, database: str, collection: str, output_tsv: str | None) -> None:
    """Validate tax_id and species_tax_id field formats and consistency."""
    client = MongoClient(mongo_uri)
    db = client[database]
    coll = db[collection]

    total_docs = coll.count_documents({})
    console.print(f"[bold]Total documents:[/bold] {total_docs:,}\n")

    # Check tax_id field
    console.print("[bold]Analyzing tax_id field:[/bold]")

    # Count documents with tax_id
    has_tax_id = coll.count_documents({"tax_id": {"$exists": True, "$ne": None}})
    console.print(
        f"  Documents with tax_id: {has_tax_id:,} ({has_tax_id / total_docs * 100:.2f}%)"
    )

    # Check data types
    tax_id_types = coll.aggregate(
        [
            {"$match": {"tax_id": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": {"$type": "$tax_id"}, "count": {"$sum": 1}}},
        ]
    )

    console.print("\n  Data types found in tax_id:")
    for item in tax_id_types:
        console.print(f"    {item['_id']}: {item['count']:,}")

    # Get some sample values to check format
    console.print("\n  Sample tax_id values:")
    samples = list(
        coll.find(
            {"tax_id": {"$exists": True, "$ne": None}}, {"tax_id": 1, "org_name": 1}
        ).limit(50)
    )

    # Check for non-integer values
    non_integer = []
    negative = []
    zero = []
    very_large = []

    for doc in samples:
        tax_id = doc.get("tax_id")
        if tax_id is not None:
            if isinstance(tax_id, str):
                # Check if string represents an integer
                if not tax_id.isdigit():
                    non_integer.append((doc.get("org_name"), tax_id))
            elif isinstance(tax_id, int | float):
                if tax_id < 0:
                    negative.append((doc.get("org_name"), tax_id))
                elif tax_id == 0:
                    zero.append((doc.get("org_name"), tax_id))
                elif tax_id > 10000000:  # NCBI tax IDs are typically < 10M
                    very_large.append((doc.get("org_name"), tax_id))

    # Check entire collection for anomalies
    console.print("\n[bold]Checking for anomalies across entire collection:[/bold]")

    # String tax_ids
    string_tax_ids = coll.count_documents({"tax_id": {"$type": "string"}})
    console.print(f"  String tax_id values: {string_tax_ids:,}")

    # Negative tax_ids
    negative_tax_ids = coll.count_documents({"tax_id": {"$lt": 0}})
    console.print(f"  Negative tax_id values: {negative_tax_ids:,}")

    # Zero tax_ids
    zero_tax_ids = coll.count_documents({"tax_id": 0})
    console.print(f"  Zero tax_id values: {zero_tax_ids:,}")

    # Very large tax_ids (suspicious)
    large_tax_ids = coll.count_documents({"tax_id": {"$gt": 10000000}})
    console.print(f"  Tax_id > 10,000,000: {large_tax_ids:,}")

    # Check species_tax_id
    console.print("\n[bold]Analyzing species_tax_id field:[/bold]")

    has_species_tax_id = coll.count_documents(
        {"species_tax_id": {"$exists": True, "$ne": None}}
    )
    console.print(
        f"  Documents with species_tax_id: {has_species_tax_id:,} ({has_species_tax_id / total_docs * 100:.2f}%)"
    )

    # Check if tax_id and species_tax_id are always the same or different
    console.print("\n[bold]Comparing tax_id and species_tax_id:[/bold]")

    # Get documents with both fields
    both_fields = list(
        coll.find(
            {
                "tax_id": {"$exists": True, "$ne": None},
                "species_tax_id": {"$exists": True, "$ne": None},
            },
            {"tax_id": 1, "species_tax_id": 1, "org_name": 1, "species": 1},
        ).limit(100)
    )

    same_count = 0
    different_count = 0
    different_examples = []

    for doc in both_fields:
        if doc.get("tax_id") == doc.get("species_tax_id"):
            same_count += 1
        else:
            different_count += 1
            if len(different_examples) < 10:
                different_examples.append(doc)

    console.print(f"  Documents where tax_id == species_tax_id: {same_count}")
    console.print(f"  Documents where tax_id != species_tax_id: {different_count}")

    if different_examples:
        console.print("\n  Examples where they differ:")
        table = Table()
        table.add_column("Organism", style="cyan")
        table.add_column("Species", style="green")
        table.add_column("tax_id", style="yellow")
        table.add_column("species_tax_id", style="magenta")

        for doc in different_examples[:10]:
            table.add_row(
                str(doc.get("org_name", ""))[:40],
                str(doc.get("species", ""))[:40],
                str(doc.get("tax_id")),
                str(doc.get("species_tax_id")),
            )

        console.print(table)

    # Get min and max tax_id values
    console.print("\n[bold]Tax_id value ranges:[/bold]")

    min_tax = list(
        coll.find({"tax_id": {"$type": "number"}}, {"tax_id": 1})
        .sort("tax_id", 1)
        .limit(1)
    )

    max_tax = list(
        coll.find({"tax_id": {"$type": "number"}}, {"tax_id": 1})
        .sort("tax_id", -1)
        .limit(1)
    )

    if min_tax:
        console.print(f"  Minimum tax_id: {min_tax[0]['tax_id']}")
    if max_tax:
        console.print(f"  Maximum tax_id: {max_tax[0]['tax_id']}")

    # Check for "NA" or other string values
    console.print("\n[bold]Checking for non-numeric tax_id values:[/bold]")

    string_samples = list(
        coll.find({"tax_id": {"$type": "string"}}, {"tax_id": 1, "org_name": 1}).limit(
            10
        )
    )

    if string_samples:
        console.print(f"  Found {len(string_samples)} string tax_id examples:")
        for doc in string_samples:
            console.print(f"    {doc.get('org_name')}: '{doc.get('tax_id')}'")
    else:
        console.print("  No string tax_id values found")

    # Save to TSV if requested
    if output_tsv:
        output_path = Path(output_tsv)
        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(["metric", "value"])
            writer.writerow(["total_documents", total_docs])
            writer.writerow(["docs_with_tax_id", has_tax_id])
            writer.writerow(
                [
                    "tax_id_coverage_pct",
                    f"{has_tax_id / total_docs * 100:.2f}" if total_docs > 0 else "0",
                ]
            )
            writer.writerow(["string_tax_ids", string_tax_ids])
            writer.writerow(["negative_tax_ids", negative_tax_ids])
            writer.writerow(["zero_tax_ids", zero_tax_ids])
            writer.writerow(["large_tax_ids_over_10M", large_tax_ids])
            writer.writerow(["docs_with_species_tax_id", has_species_tax_id])
            writer.writerow(
                [
                    "species_tax_id_coverage_pct",
                    f"{has_species_tax_id / total_docs * 100:.2f}"
                    if total_docs > 0
                    else "0",
                ]
            )
            if min_tax:
                writer.writerow(["min_tax_id", min_tax[0]["tax_id"]])
            if max_tax:
                writer.writerow(["max_tax_id", max_tax[0]["tax_id"]])

        console.print(f"\n[green]Analysis summary saved to {output_path}[/green]")

    client.close()


if __name__ == "__main__":
    cli()
