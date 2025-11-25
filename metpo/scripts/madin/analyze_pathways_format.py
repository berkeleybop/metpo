"""Analyze whether pathways field is single values or comma-separated lists."""

from collections import Counter

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
    help="Optional: Save results to TSV file",
    type=click.Path(),
)
def cli(mongo_uri: str, database: str, collection: str, output_tsv: str | None) -> None:
    """Analyze pathways field format."""
    client = MongoClient(mongo_uri)
    db = client[database]
    coll = db[collection]

    total_docs = coll.count_documents({})
    console.print(f"[bold]Total documents:[/bold] {total_docs:,}\n")

    # Check pathways field
    console.print("[bold]Analyzing pathways field:[/bold]")

    # Count documents with pathways
    has_pathways = coll.count_documents(
        {"pathways": {"$exists": True, "$nin": [None, "NA"]}}
    )
    console.print(
        f"  Documents with pathways (non-NA): {has_pathways:,} ({has_pathways / total_docs * 100:.2f}%)"
    )

    # Sample some pathway values
    console.print("\n  Sample pathways values:")
    samples = list(
        coll.find(
            {"pathways": {"$exists": True, "$nin": [None, "NA"]}},
            {"pathways": 1, "org_name": 1},
        ).limit(20)
    )

    # Check if they contain commas (indicating lists)
    contains_comma = 0
    single_value = 0
    examples_with_comma = []
    examples_single = []

    for doc in samples:
        pathways = doc.get("pathways")
        org_name = doc.get("org_name", "")

        if isinstance(pathways, str):
            if "," in pathways:
                contains_comma += 1
                if len(examples_with_comma) < 5:
                    examples_with_comma.append((org_name, pathways))
            else:
                single_value += 1
                if len(examples_single) < 5:
                    examples_single.append((org_name, pathways))

    console.print("\n  Sample analysis (first 20):")
    console.print(f"    Single values: {single_value}/20")
    console.print(f"    Contains commas: {contains_comma}/20")

    if examples_single:
        console.print("\n  Examples of single values:")
        for org, pathway in examples_single[:3]:
            console.print(f"    {org[:40]}: {pathway[:60]}")

    if examples_with_comma:
        console.print("\n  Examples with commas (lists):")
        for org, pathway in examples_with_comma[:5]:
            display_pathway = pathway if len(pathway) <= 80 else pathway[:77] + "..."
            console.print(f"    {org[:40]}:")
            console.print(f"      {display_pathway}")

    # Check entire collection for comma-containing pathways
    console.print("\n[bold]Checking entire collection:[/bold]")

    # Count docs with commas in pathways
    comma_pathways = coll.count_documents({"pathways": {"$regex": ","}})
    console.print(
        f"  Documents with comma-separated pathways: {comma_pathways:,} ({comma_pathways / has_pathways * 100:.2f}% of non-NA)"
    )

    # Get unique pathway values
    console.print("\n[bold]Unique pathway combinations:[/bold]")
    unique_pathways = coll.distinct("pathways", {"pathways": {"$nin": [None, "NA"]}})
    console.print(f"  Total unique pathway strings: {len(unique_pathways):,}")

    # Show distribution of pathway string lengths
    console.print("\n[bold]Pathway string length distribution:[/bold]")

    length_pipeline = [
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

    length_dist = list(coll.aggregate(length_pipeline))
    for bucket in length_dist:
        console.print(f"    Length {bucket['_id']}: {bucket['count']:,} documents")

    # Unpack and count individual pathways
    console.print("\n[bold]Unpacking comma-separated pathways:[/bold]")

    pathway_counter = Counter()

    cursor = coll.find(
        {"pathways": {"$exists": True, "$nin": [None, "NA"]}}, {"pathways": 1}
    )

    for doc in cursor:
        pathways_str = doc.get("pathways", "")
        if pathways_str and pathways_str != "NA":
            # Split on ", " (comma-space) to preserve internal commas
            individual_pathways = [p.strip() for p in pathways_str.split(", ")]
            pathway_counter.update(individual_pathways)

    console.print(
        f"  Unique individual pathways after unpacking: {len(pathway_counter):,}"
    )

    # Show most common pathways
    console.print("\n[bold]Most common individual pathways:[/bold]")
    table = Table()
    table.add_column("Rank", style="cyan")
    table.add_column("Pathway", style="green", no_wrap=False)
    table.add_column("Count", style="yellow")

    for i, (pathway, count) in enumerate(pathway_counter.most_common(20), 1):
        display_pathway = pathway if len(pathway) <= 60 else pathway[:57] + "..."
        table.add_row(str(i), display_pathway, f"{count:,}")

    console.print(table)

    # Save to TSV if requested
    if output_tsv:
        import csv

        with open(output_tsv, "w", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(["pathway", "count", "percentage"])

            total_mentions = sum(pathway_counter.values())

            for pathway, count in pathway_counter.most_common():
                percentage = (count / total_mentions * 100) if total_mentions > 0 else 0
                writer.writerow([pathway, count, f"{percentage:.2f}"])

        console.print(f"\n[green]Results saved to {output_tsv}[/green]")
        console.print(f"  Total pathways: {len(pathway_counter)}")
        console.print(f"  Total mentions: {total_mentions:,}")

    client.close()


if __name__ == "__main__":
    cli()
