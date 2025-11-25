"""Analyze whether ref_id fields are single values or comma-separated lists."""

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
    show_default=True,
)
@click.option(
    "--database",
    default="madin",
    help="Database name",
    show_default=True,
)
@click.option(
    "--collection",
    default="madin",
    help="Collection name",
    show_default=True,
)
@click.option(
    "--output-tsv",
    type=click.Path(),
    help="Optional: Save longest ref_id analysis to TSV file",
)
def cli(mongo_uri: str, database: str, collection: str, output_tsv: str | None) -> None:
    """Analyze ref_id field format."""
    client = MongoClient(mongo_uri)
    db = client[database]
    coll = db[collection]

    total_docs = coll.count_documents({})
    console.print(f"[bold]Total documents:[/bold] {total_docs:,}\n")

    # Check ref_id field
    console.print("[bold]Analyzing ref_id field:[/bold]")

    # Count documents with ref_id
    has_ref_id = coll.count_documents(
        {"ref_id": {"$exists": True, "$nin": [None, "NA"]}}
    )
    console.print(
        f"  Documents with ref_id (non-NA): {has_ref_id:,} ({has_ref_id / total_docs * 100:.2f}%)"
    )

    # Check data types
    ref_id_types = list(
        coll.aggregate(
            [
                {"$match": {"ref_id": {"$exists": True, "$nin": [None, "NA"]}}},
                {"$group": {"_id": {"$type": "$ref_id"}, "count": {"$sum": 1}}},
            ]
        )
    )

    console.print("\n  Data types found in ref_id:")
    for item in ref_id_types:
        console.print(f"    {item['_id']}: {item['count']:,}")

    # Sample some ref_id values
    console.print("\n  Sample ref_id values:")
    samples = list(
        coll.find(
            {"ref_id": {"$exists": True, "$nin": [None, "NA"]}},
            {"ref_id": 1, "org_name": 1},
        ).limit(20)
    )

    # Check if they contain commas (indicating lists)
    contains_comma = 0
    single_value = 0
    examples_with_comma = []
    examples_single = []

    for doc in samples:
        ref_id = doc.get("ref_id")
        org_name = doc.get("org_name", "")

        if isinstance(ref_id, str):
            if "," in ref_id:
                contains_comma += 1
                if len(examples_with_comma) < 5:
                    examples_with_comma.append((org_name, ref_id))
            else:
                single_value += 1
                if len(examples_single) < 5:
                    examples_single.append((org_name, ref_id))
        elif isinstance(ref_id, int | float):
            single_value += 1
            if len(examples_single) < 5:
                examples_single.append((org_name, str(ref_id)))

    console.print("\n  Sample analysis:")
    console.print(f"    Single values: {single_value}/20")
    console.print(f"    Contains commas: {contains_comma}/20")

    if examples_single:
        console.print("\n  Examples of single values:")
        for org, ref in examples_single:
            console.print(f"    {org[:40]}: {ref}")

    if examples_with_comma:
        console.print("\n  Examples with commas (lists):")
        for org, ref in examples_with_comma:
            console.print(f"    {org[:40]}: {ref}")

    # Check across entire collection for comma-containing ref_ids
    console.print(
        "\n[bold]Checking entire collection for comma-separated ref_ids:[/bold]"
    )

    # Check string ref_ids for commas
    string_ref_ids = list(
        coll.find({"ref_id": {"$type": "string", "$ne": "NA"}}, {"ref_id": 1}).limit(
            100
        )
    )

    comma_count = 0
    for doc in string_ref_ids:
        if "," in doc.get("ref_id", ""):
            comma_count += 1

    console.print(f"  Checked 100 string ref_ids, {comma_count} contain commas")

    # Get examples of longest ref_id strings (likely to be lists)
    console.print("\n[bold]Longest ref_id values (likely lists if they exist):[/bold]")

    longest_refs = list(
        coll.aggregate(
            [
                {"$match": {"ref_id": {"$type": "string", "$ne": "NA"}}},
                {
                    "$project": {
                        "ref_id": 1,
                        "org_name": 1,
                        "length": {"$strLenCP": "$ref_id"},
                    }
                },
                {"$sort": {"length": -1}},
                {"$limit": 10},
            ]
        )
    )

    table = Table()
    table.add_column("Organism", style="cyan", no_wrap=False)
    table.add_column("ref_id", style="green")
    table.add_column("Length", style="yellow")
    table.add_column("Has comma?", style="magenta")

    for doc in longest_refs:
        ref_id = doc.get("ref_id", "")
        org_name = doc.get("org_name", "")[:40]
        length = doc.get("length", 0)
        has_comma = "Yes" if "," in ref_id else "No"

        # Truncate long ref_ids for display
        display_ref = ref_id if len(ref_id) <= 50 else ref_id[:47] + "..."

        table.add_row(org_name, display_ref, str(length), has_comma)

    console.print(table)

    # If we find comma-separated ones, count how many values they have
    if comma_count > 0:
        console.print("\n[bold]Analyzing comma-separated ref_ids:[/bold]")

        comma_ref_docs = list(
            coll.find({"ref_id": {"$regex": ","}}, {"ref_id": 1, "org_name": 1}).limit(
                10
            )
        )

        if comma_ref_docs:
            console.print(f"  Found {len(comma_ref_docs)} examples:")
            for doc in comma_ref_docs:
                ref_id = doc.get("ref_id", "")
                # Try splitting on ", " first, then ","
                values = [v.strip() for v in ref_id.split(", ")]
                if len(values) == 1:
                    values = [v.strip() for v in ref_id.split(",")]

                console.print(f"    {doc.get('org_name', '')[:40]}")
                console.print(f"      ref_id: {ref_id}")
                console.print(f"      Count: {len(values)} references")

    # Save TSV output if requested
    if output_tsv:
        output_path = Path(output_tsv)
        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(["organism", "ref_id", "length", "has_comma"])

            for doc in longest_refs:
                ref_id = doc.get("ref_id", "")
                org_name = doc.get("org_name", "")
                length = doc.get("length", 0)
                has_comma = "Yes" if "," in ref_id else "No"
                writer.writerow([org_name, ref_id, length, has_comma])

        console.print(f"\n[green]Results saved to {output_path}[/green]")

    client.close()


if __name__ == "__main__":
    cli()
