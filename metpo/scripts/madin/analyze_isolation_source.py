"""Analyze isolation_source field format and values."""

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
    """Analyze isolation_source field."""
    client = MongoClient(mongo_uri)
    db = client[database]
    coll = db[collection]

    total_docs = coll.count_documents({})
    console.print(f"[bold]Total documents:[/bold] {total_docs:,}\n")

    # Check isolation_source field
    console.print("[bold]Analyzing isolation_source field:[/bold]")

    # Count documents with isolation_source
    has_isolation_source = coll.count_documents(
        {"isolation_source": {"$exists": True, "$nin": [None, "NA"]}}
    )
    console.print(
        f"  Documents with isolation_source (non-NA): {has_isolation_source:,} "
        f"({has_isolation_source / total_docs * 100:.2f}%)"
    )

    # Sample some values
    console.print("\n  Sample isolation_source values:")
    samples = list(
        coll.find(
            {"isolation_source": {"$exists": True, "$nin": [None, "NA"]}},
            {"isolation_source": 1, "org_name": 1},
        ).limit(20)
    )

    # Check if they contain commas (indicating lists)
    contains_comma = 0
    single_value = 0
    examples_with_comma = []
    examples_single = []

    for doc in samples:
        isolation_source = doc.get("isolation_source")
        org_name = doc.get("org_name", "")

        if isinstance(isolation_source, str):
            if "," in isolation_source:
                contains_comma += 1
                if len(examples_with_comma) < 5:
                    examples_with_comma.append((org_name, isolation_source))
            else:
                single_value += 1
                if len(examples_single) < 10:
                    examples_single.append((org_name, isolation_source))

    console.print("\n  Sample analysis (first 20):")
    console.print(f"    Single values: {single_value}/20")
    console.print(f"    Contains commas: {contains_comma}/20")

    if examples_single:
        console.print("\n  Examples of single values:")
        for org, source in examples_single[:10]:
            console.print(f"    {org[:40]}: {source}")

    if examples_with_comma:
        console.print("\n  Examples with commas (potential lists):")
        for org, source in examples_with_comma:
            console.print(f"    {org[:40]}: {source}")

    # Check entire collection for comma-containing isolation_source
    console.print("\n[bold]Checking entire collection:[/bold]")

    # Count docs with commas in isolation_source
    comma_sources = coll.count_documents({"isolation_source": {"$regex": ","}})
    console.print(
        f"  Documents with comma-separated isolation_source: {comma_sources:,} "
        f"({comma_sources / has_isolation_source * 100:.2f}% of non-NA)"
    )

    # Get unique values
    console.print("\n[bold]Unique isolation_source values:[/bold]")
    unique_sources = coll.distinct(
        "isolation_source", {"isolation_source": {"$nin": [None, "NA"]}}
    )
    console.print(f"  Total unique values: {len(unique_sources):,}")

    # Count occurrences
    source_counter = Counter()

    cursor = coll.find(
        {"isolation_source": {"$exists": True, "$nin": [None, "NA"]}},
        {"isolation_source": 1},
    )

    for doc in cursor:
        source = doc.get("isolation_source", "")
        if source and source != "NA":
            source_counter[source] += 1

    # Show most common sources
    console.print("\n[bold]Most common isolation sources:[/bold]")
    table = Table()
    table.add_column("Rank", style="cyan")
    table.add_column("Isolation Source", style="green", no_wrap=False)
    table.add_column("Count", style="yellow")
    table.add_column("% of Total", style="magenta")

    for i, (source, count) in enumerate(source_counter.most_common(30), 1):
        percentage = (
            (count / has_isolation_source * 100) if has_isolation_source > 0 else 0
        )
        table.add_row(str(i), source, f"{count:,}", f"{percentage:.2f}%")

    console.print(table)

    # Check for underscores to understand naming pattern
    console.print("\n[bold]Analyzing naming patterns:[/bold]")
    underscore_count = sum(1 for source in unique_sources if "_" in source)
    console.print(
        f"  Values with underscores: {underscore_count}/{len(unique_sources)}"
    )

    # Show all unique values grouped by pattern
    console.print("\n[bold]All unique isolation_source values:[/bold]")
    for source in sorted(unique_sources):
        count = source_counter[source]
        console.print(f"  {source}: {count:,}")

    # Save to TSV if requested
    if output_tsv:
        import csv

        with open(output_tsv, "w", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(["isolation_source", "count", "percentage"])

            for source, count in source_counter.most_common():
                percentage = (
                    (count / has_isolation_source * 100)
                    if has_isolation_source > 0
                    else 0
                )
                writer.writerow([source, count, f"{percentage:.2f}"])

        console.print(f"\n[green]Results saved to {output_tsv}[/green]")
        console.print(f"  Total unique sources: {len(source_counter)}")
        console.print(f"  Total mentions: {sum(source_counter.values()):,}")

    client.close()


if __name__ == "__main__":
    cli()
