"""Analyze isolation_source field format and values."""

from pathlib import Path

import click
from pymongo import MongoClient
from rich.table import Table

from metpo.scripts.madin.utils import (
    console,
    count_field_values,
    get_sample_values,
    print_field_stats,
    print_sample_analysis,
    save_counter_to_tsv,
)


def display_all_values(unique_sources: list[str], source_counter: dict) -> None:
    """Display all unique values with counts."""
    console.print("\n[bold]All unique isolation_source values:[/bold]")
    for source in sorted(unique_sources):
        count = source_counter.get(source, 0)
        console.print(f"  {source}: {count:,}")


def display_top_sources(source_counter: dict, total: int, top_n: int = 30) -> None:
    """Display top N most common sources in a table."""
    console.print("\n[bold]Most common isolation sources:[/bold]")
    table = Table()
    table.add_column("Rank", style="cyan")
    table.add_column("Isolation Source", style="green", no_wrap=False)
    table.add_column("Count", style="yellow")
    table.add_column("% of Total", style="magenta")

    for i, (source, count) in enumerate(source_counter.most_common(top_n), 1):
        percentage = (count / total * 100) if total > 0 else 0
        table.add_row(str(i), source, f"{count:,}", f"{percentage:.2f}%")

    console.print(table)


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

    field = "isolation_source"
    total_docs = coll.count_documents({})
    console.print(f"[bold]Total documents:[/bold] {total_docs:,}\n")

    # Basic field stats
    has_field = print_field_stats(coll, field, total_docs)

    # Sample values
    single_examples, comma_examples = get_sample_values(coll, field)
    print_sample_analysis(single_examples, comma_examples, field)

    # Check for comma-separated values
    console.print("\n[bold]Checking entire collection:[/bold]")
    comma_count = coll.count_documents({field: {"$regex": ","}})
    console.print(
        f"  Documents with comma-separated {field}: {comma_count:,} "
        f"({comma_count / has_field * 100:.2f}% of non-NA)"
    )

    # Get unique values
    unique_sources = coll.distinct(field, {field: {"$nin": [None, "NA"]}})
    console.print(f"\n[bold]Unique {field} values:[/bold]")
    console.print(f"  Total unique values: {len(unique_sources):,}")

    # Count occurrences
    source_counter = count_field_values(coll, field)

    # Display top sources
    display_top_sources(source_counter, has_field)

    # Analyze naming patterns
    console.print("\n[bold]Analyzing naming patterns:[/bold]")
    underscore_count = sum(1 for source in unique_sources if "_" in source)
    console.print(f"  Values with underscores: {underscore_count}/{len(unique_sources)}")

    # Show all unique values
    display_all_values(unique_sources, source_counter)

    # Save to TSV if requested
    if output_tsv:
        save_counter_to_tsv(
            source_counter,
            has_field,
            Path(output_tsv),
            columns=("isolation_source", "count", "percentage"),
        )

    client.close()


if __name__ == "__main__":
    cli()
