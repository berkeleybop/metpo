"""Analyze whether pathways field is single values or comma-separated lists."""

import csv
from collections import Counter
from pathlib import Path
from typing import Any

import click
from pymongo import MongoClient
from pymongo.collection import Collection
from rich.console import Console
from rich.table import Table

console = Console()


def analyze_samples(coll: Collection, field: str, limit: int = 20) -> dict[str, Any]:
    """Analyze sample values for comma presence.

    Returns dict with single_examples, comma_examples, and counts.
    """
    samples = list(
        coll.find(
            {field: {"$exists": True, "$nin": [None, "NA"]}},
            {field: 1, "org_name": 1},
        ).limit(limit)
    )

    result = {
        "single_count": 0,
        "comma_count": 0,
        "single_examples": [],
        "comma_examples": [],
    }

    for doc in samples:
        value = doc.get(field)
        org_name = doc.get("org_name", "")

        if isinstance(value, str):
            if "," in value:
                result["comma_count"] += 1
                if len(result["comma_examples"]) < 5:
                    result["comma_examples"].append((org_name, value))
            else:
                result["single_count"] += 1
                if len(result["single_examples"]) < 5:
                    result["single_examples"].append((org_name, value))

    return result


def print_sample_results(sample_data: dict[str, Any]) -> None:
    """Print sample analysis results."""
    console.print("\n  Sample analysis (first 20):")
    console.print(f"    Single values: {sample_data['single_count']}/20")
    console.print(f"    Contains commas: {sample_data['comma_count']}/20")

    if sample_data["single_examples"]:
        console.print("\n  Examples of single values:")
        for org, pathway in sample_data["single_examples"][:3]:
            console.print(f"    {org[:40]}: {pathway[:60]}")

    if sample_data["comma_examples"]:
        console.print("\n  Examples with commas (lists):")
        for org, pathway in sample_data["comma_examples"][:5]:
            display = pathway if len(pathway) <= 80 else pathway[:77] + "..."
            console.print(f"    {org[:40]}:")
            console.print(f"      {display}")


def get_length_distribution(coll: Collection) -> list[dict]:
    """Get pathway string length distribution."""
    pipeline = [
        {"$match": {"pathways": {"$type": "string", "$ne": "NA"}}},
        {"$project": {"pathways": 1, "length": {"$strLenCP": "$pathways"}}},
        {
            "$bucket": {
                "groupBy": "$length",
                "boundaries": [0, 20, 50, 100, 200, 500, 1000, 5000],
                "default": "5000+",
                "output": {"count": {"$sum": 1}},
            }
        },
    ]
    return list(coll.aggregate(pipeline))


def count_individual_pathways(coll: Collection) -> Counter:
    """Unpack comma-separated pathways and count individual ones."""
    pathway_counter: Counter = Counter()
    cursor = coll.find(
        {"pathways": {"$exists": True, "$nin": [None, "NA"]}}, {"pathways": 1}
    )

    for doc in cursor:
        pathways_str = doc.get("pathways", "")
        if pathways_str and pathways_str != "NA":
            individual_pathways = [p.strip() for p in pathways_str.split(", ")]
            pathway_counter.update(individual_pathways)

    return pathway_counter


def display_top_pathways(pathway_counter: Counter, top_n: int = 20) -> None:
    """Display top N pathways in a table."""
    table = Table()
    table.add_column("Rank", style="cyan")
    table.add_column("Pathway", style="green", no_wrap=False)
    table.add_column("Count", style="yellow")

    for i, (pathway, count) in enumerate(pathway_counter.most_common(top_n), 1):
        display = pathway if len(pathway) <= 60 else pathway[:57] + "..."
        table.add_row(str(i), display, f"{count:,}")

    console.print(table)


def save_results(pathway_counter: Counter, output_path: Path) -> None:
    """Save pathway counts to TSV."""
    total_mentions = sum(pathway_counter.values())

    with output_path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["pathway", "count", "percentage"])

        for pathway, count in pathway_counter.most_common():
            percentage = (count / total_mentions * 100) if total_mentions > 0 else 0
            writer.writerow([pathway, count, f"{percentage:.2f}"])

    console.print(f"\n[green]Results saved to {output_path}[/green]")
    console.print(f"  Total pathways: {len(pathway_counter)}")
    console.print(f"  Total mentions: {total_mentions:,}")


@click.command()
@click.option(
    "--mongo-uri",
    default="mongodb://localhost:27017",
    help="MongoDB connection URI",
    show_default=True,
)
@click.option("--database", default="madin", help="Database name", show_default=True)
@click.option("--collection", default="madin", help="Collection name", show_default=True)
@click.option("--output-tsv", help="Optional: Save results to TSV file", type=click.Path())
def cli(mongo_uri: str, database: str, collection: str, output_tsv: str | None) -> None:
    """Analyze pathways field format."""
    client = MongoClient(mongo_uri)
    db = client[database]
    coll = db[collection]

    total_docs = coll.count_documents({})
    console.print(f"[bold]Total documents:[/bold] {total_docs:,}\n")

    # Count documents with pathways
    has_pathways = coll.count_documents({"pathways": {"$exists": True, "$nin": [None, "NA"]}})
    console.print("[bold]Analyzing pathways field:[/bold]")
    console.print(
        f"  Documents with pathways (non-NA): {has_pathways:,} "
        f"({has_pathways / total_docs * 100:.2f}%)"
    )

    # Analyze samples
    console.print("\n  Sample pathways values:")
    sample_data = analyze_samples(coll, "pathways")
    print_sample_results(sample_data)

    # Check for comma-separated values
    console.print("\n[bold]Checking entire collection:[/bold]")
    comma_pathways = coll.count_documents({"pathways": {"$regex": ","}})
    console.print(
        f"  Documents with comma-separated pathways: {comma_pathways:,} "
        f"({comma_pathways / has_pathways * 100:.2f}% of non-NA)"
    )

    # Unique values
    unique_pathways = coll.distinct("pathways", {"pathways": {"$nin": [None, "NA"]}})
    console.print("\n[bold]Unique pathway combinations:[/bold]")
    console.print(f"  Total unique pathway strings: {len(unique_pathways):,}")

    # Length distribution
    console.print("\n[bold]Pathway string length distribution:[/bold]")
    for bucket in get_length_distribution(coll):
        console.print(f"    Length {bucket['_id']}: {bucket['count']:,} documents")

    # Count individual pathways
    console.print("\n[bold]Unpacking comma-separated pathways:[/bold]")
    pathway_counter = count_individual_pathways(coll)
    console.print(f"  Unique individual pathways after unpacking: {len(pathway_counter):,}")

    # Display top pathways
    console.print("\n[bold]Most common individual pathways:[/bold]")
    display_top_pathways(pathway_counter)

    # Save if requested
    if output_tsv:
        save_results(pathway_counter, Path(output_tsv))

    client.close()


if __name__ == "__main__":
    cli()
