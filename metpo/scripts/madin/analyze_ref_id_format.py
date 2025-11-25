"""Analyze whether ref_id fields are single values or comma-separated lists."""

import csv
from pathlib import Path
from typing import Any

import click
from pymongo import MongoClient
from pymongo.collection import Collection
from rich.console import Console
from rich.table import Table

console = Console()


def get_ref_id_type_counts(coll: Collection) -> list[dict]:
    """Get counts of different data types in ref_id field."""
    return list(
        coll.aggregate([
            {"$match": {"ref_id": {"$exists": True, "$nin": [None, "NA"]}}},
            {"$group": {"_id": {"$type": "$ref_id"}, "count": {"$sum": 1}}},
        ])
    )


def analyze_samples(coll: Collection) -> dict[str, Any]:
    """Analyze sample ref_id values for comma presence."""
    samples = list(
        coll.find(
            {"ref_id": {"$exists": True, "$nin": [None, "NA"]}},
            {"ref_id": 1, "org_name": 1},
        ).limit(20)
    )

    result = {"single": 0, "comma": 0, "single_examples": [], "comma_examples": []}

    for doc in samples:
        ref_id = doc.get("ref_id")
        org_name = doc.get("org_name", "")

        if isinstance(ref_id, str) and "," in ref_id:
            result["comma"] += 1
            if len(result["comma_examples"]) < 5:
                result["comma_examples"].append((org_name, ref_id))
        else:
            result["single"] += 1
            ref_str = str(ref_id) if isinstance(ref_id, int | float) else ref_id
            if len(result["single_examples"]) < 5:
                result["single_examples"].append((org_name, ref_str))

    return result


def print_sample_analysis(sample_data: dict[str, Any]) -> None:
    """Print sample analysis results."""
    console.print("\n  Sample analysis:")
    console.print(f"    Single values: {sample_data['single']}/20")
    console.print(f"    Contains commas: {sample_data['comma']}/20")

    if sample_data["single_examples"]:
        console.print("\n  Examples of single values:")
        for org, ref in sample_data["single_examples"]:
            console.print(f"    {org[:40]}: {ref}")

    if sample_data["comma_examples"]:
        console.print("\n  Examples with commas (lists):")
        for org, ref in sample_data["comma_examples"]:
            console.print(f"    {org[:40]}: {ref}")


def count_comma_ref_ids(coll: Collection) -> int:
    """Count string ref_ids that contain commas."""
    string_ref_ids = list(
        coll.find({"ref_id": {"$type": "string", "$ne": "NA"}}, {"ref_id": 1}).limit(100)
    )
    return sum(1 for doc in string_ref_ids if "," in doc.get("ref_id", ""))


def get_longest_ref_ids(coll: Collection) -> list[dict]:
    """Get the longest ref_id string values."""
    return list(
        coll.aggregate([
            {"$match": {"ref_id": {"$type": "string", "$ne": "NA"}}},
            {"$project": {"ref_id": 1, "org_name": 1, "length": {"$strLenCP": "$ref_id"}}},
            {"$sort": {"length": -1}},
            {"$limit": 10},
        ])
    )


def display_longest_refs_table(longest_refs: list[dict]) -> None:
    """Display table of longest ref_id values."""
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
        display_ref = ref_id if len(ref_id) <= 50 else ref_id[:47] + "..."
        table.add_row(org_name, display_ref, str(length), has_comma)

    console.print(table)


def analyze_comma_separated_refs(coll: Collection) -> None:
    """Analyze comma-separated ref_id values."""
    console.print("\n[bold]Analyzing comma-separated ref_ids:[/bold]")

    comma_ref_docs = list(
        coll.find({"ref_id": {"$regex": ","}}, {"ref_id": 1, "org_name": 1}).limit(10)
    )

    if comma_ref_docs:
        console.print(f"  Found {len(comma_ref_docs)} examples:")
        for doc in comma_ref_docs:
            ref_id = doc.get("ref_id", "")
            values = [v.strip() for v in ref_id.split(", ")]
            if len(values) == 1:
                values = [v.strip() for v in ref_id.split(",")]

            console.print(f"    {doc.get('org_name', '')[:40]}")
            console.print(f"      ref_id: {ref_id}")
            console.print(f"      Count: {len(values)} references")


def save_longest_refs_tsv(longest_refs: list[dict], output_path: Path) -> None:
    """Save longest ref_id analysis to TSV file."""
    with output_path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["organism", "ref_id", "length", "has_comma"])

        for doc in longest_refs:
            ref_id = doc.get("ref_id", "")
            org_name = doc.get("org_name", "")
            length = doc.get("length", 0)
            has_comma = "Yes" if "," in ref_id else "No"
            writer.writerow([org_name, ref_id, length, has_comma])

    console.print(f"\n[green]Results saved to {output_path}[/green]")


@click.command()
@click.option(
    "--mongo-uri",
    default="mongodb://localhost:27017",
    help="MongoDB connection URI",
    show_default=True,
)
@click.option("--database", default="madin", help="Database name", show_default=True)
@click.option("--collection", default="madin", help="Collection name", show_default=True)
@click.option("--output-tsv", type=click.Path(), help="Optional: Save longest ref_id analysis to TSV file")
def cli(mongo_uri: str, database: str, collection: str, output_tsv: str | None) -> None:
    """Analyze ref_id field format."""
    client = MongoClient(mongo_uri)
    db = client[database]
    coll = db[collection]

    total_docs = coll.count_documents({})
    console.print(f"[bold]Total documents:[/bold] {total_docs:,}\n")
    console.print("[bold]Analyzing ref_id field:[/bold]")

    has_ref_id = coll.count_documents({"ref_id": {"$exists": True, "$nin": [None, "NA"]}})
    console.print(f"  Documents with ref_id (non-NA): {has_ref_id:,} ({has_ref_id / total_docs * 100:.2f}%)")

    console.print("\n  Data types found in ref_id:")
    for item in get_ref_id_type_counts(coll):
        console.print(f"    {item['_id']}: {item['count']:,}")

    console.print("\n  Sample ref_id values:")
    sample_data = analyze_samples(coll)
    print_sample_analysis(sample_data)

    console.print("\n[bold]Checking entire collection for comma-separated ref_ids:[/bold]")
    comma_count = count_comma_ref_ids(coll)
    console.print(f"  Checked 100 string ref_ids, {comma_count} contain commas")

    console.print("\n[bold]Longest ref_id values (likely lists if they exist):[/bold]")
    longest_refs = get_longest_ref_ids(coll)
    display_longest_refs_table(longest_refs)

    if comma_count > 0:
        analyze_comma_separated_refs(coll)

    if output_tsv:
        save_longest_refs_tsv(longest_refs, Path(output_tsv))

    client.close()


if __name__ == "__main__":
    cli()
