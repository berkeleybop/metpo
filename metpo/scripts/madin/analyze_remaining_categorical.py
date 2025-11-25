"""Analyze remaining categorical fields: metabolism, range_salinity, range_tmp, motility, gram_stain, sporulation."""

from collections import Counter

import click
from pymongo import MongoClient
from rich.console import Console
from rich.table import Table

console = Console()


def analyze_field(coll, field_name: str, _total_docs: int) -> tuple[Counter, int]:
    """Analyze a single categorical field.

    Returns:
        Tuple of (value_counter, docs_with_data)
    """
    # Count documents with field
    has_field = coll.count_documents(
        {field_name: {"$exists": True, "$nin": [None, "NA"]}}
    )

    # Count occurrences
    value_counter = Counter()

    cursor = coll.find(
        {field_name: {"$exists": True, "$nin": [None, "NA"]}},
        {field_name: 1},
    )

    for doc in cursor:
        value = doc.get(field_name, "")
        if value and value != "NA":
            value_counter[value] += 1

    return value_counter, has_field


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
    "--output-dir",
    help="Optional: Directory to save TSV files",
    type=click.Path(),
)
def cli(mongo_uri: str, database: str, collection: str, output_dir: str | None) -> None:
    """Analyze remaining categorical fields."""
    client = MongoClient(mongo_uri)
    db = client[database]
    coll = db[collection]

    total_docs = coll.count_documents({})
    console.print(f"[bold]Total documents:[/bold] {total_docs:,}\n")

    fields_to_analyze = [
        "metabolism",
        "range_salinity",
        "range_tmp",
        "motility",
        "gram_stain",
        "sporulation",
    ]

    results = {}

    for field_name in fields_to_analyze:
        console.print(f"[bold cyan]{'=' * 60}[/bold cyan]")
        console.print(f"[bold]Analyzing: {field_name}[/bold]")
        console.print(f"[bold cyan]{'=' * 60}[/bold cyan]\n")

        value_counter, has_field = analyze_field(coll, field_name, total_docs)
        results[field_name] = (value_counter, has_field)

        console.print(
            f"  Documents with {field_name} (non-NA): {has_field:,} "
            f"({has_field / total_docs * 100:.2f}%)"
        )
        console.print(f"  Unique values: {len(value_counter)}")

        # Check for commas (lists)
        comma_count = coll.count_documents({field_name: {"$regex": ","}})
        if comma_count > 0:
            console.print(
                f"  [yellow]Contains commas (potential lists): {comma_count}[/yellow]"
            )

        # Show all values
        console.print(f"\n  All values for '{field_name}':")

        table = Table()
        table.add_column("Rank", style="cyan")
        table.add_column("Value", style="green", no_wrap=False)
        table.add_column("Count", style="yellow")
        table.add_column("% of Total", style="magenta")

        for i, (value, count) in enumerate(value_counter.most_common(), 1):
            percentage = (count / has_field * 100) if has_field > 0 else 0
            table.add_row(str(i), value, f"{count:,}", f"{percentage:.2f}%")

        console.print(table)
        console.print()

    # Summary table
    console.print(f"[bold cyan]{'=' * 60}[/bold cyan]")
    console.print("[bold]SUMMARY[/bold]")
    console.print(f"[bold cyan]{'=' * 60}[/bold cyan]\n")

    summary_table = Table(title="Categorical Fields Summary")
    summary_table.add_column("Field", style="cyan")
    summary_table.add_column("Unique Values", style="green")
    summary_table.add_column("Documents", style="yellow")
    summary_table.add_column("Coverage %", style="magenta")

    for field_name in fields_to_analyze:
        value_counter, has_field = results[field_name]
        coverage = (has_field / total_docs * 100) if total_docs > 0 else 0
        summary_table.add_row(
            field_name, str(len(value_counter)), f"{has_field:,}", f"{coverage:.2f}%"
        )

    console.print(summary_table)

    # Save TSVs if requested
    if output_dir:
        import csv
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for field_name in fields_to_analyze:
            value_counter, has_field = results[field_name]

            tsv_file = output_path / f"madin_{field_name}.tsv"

            with open(tsv_file, "w", newline="") as f:
                writer = csv.writer(f, delimiter="\t")
                writer.writerow([field_name, "count", "percentage"])

                for value, count in value_counter.most_common():
                    percentage = (count / has_field * 100) if has_field > 0 else 0
                    writer.writerow([value, count, f"{percentage:.2f}"])

        console.print(f"\n[green]All TSV files saved to {output_dir}/[/green]")

    client.close()


if __name__ == "__main__":
    cli()
