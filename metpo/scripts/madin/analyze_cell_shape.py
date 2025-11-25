"""Analyze cell_shape field format and values."""

import csv
from collections import Counter
from pathlib import Path

import click
from pymongo import MongoClient
from pymongo.collection import Collection
from rich.console import Console
from rich.table import Table

console = Console()


def get_sample_values(
    coll: Collection, field: str, limit: int = 20
) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Get sample values and categorize by comma presence.

    Returns:
        Tuple of (single_value_examples, comma_examples)
    """
    samples = list(
        coll.find(
            {field: {"$exists": True, "$nin": [None, "NA"]}},
            {field: 1, "org_name": 1},
        ).limit(limit)
    )

    single_examples = []
    comma_examples = []

    for doc in samples:
        value = doc.get(field)
        org_name = doc.get("org_name", "")

        if isinstance(value, str):
            if "," in value:
                if len(comma_examples) < 5:
                    comma_examples.append((org_name, value))
            elif len(single_examples) < 10:
                single_examples.append((org_name, value))

    return single_examples, comma_examples


def count_field_values(coll: Collection, field: str) -> Counter:
    """Count occurrences of each field value."""
    counter: Counter = Counter()
    cursor = coll.find(
        {field: {"$exists": True, "$nin": [None, "NA"]}},
        {field: 1},
    )
    for doc in cursor:
        value = doc.get(field, "")
        if value and value != "NA":
            counter[value] += 1
    return counter


def unpack_comma_separated(coll: Collection, field: str) -> Counter:
    """Unpack comma-separated values and count individual items."""
    counter: Counter = Counter()
    cursor = coll.find(
        {field: {"$exists": True, "$nin": [None, "NA"]}},
        {field: 1},
    )
    for doc in cursor:
        value_str = doc.get(field, "")
        if value_str and value_str != "NA":
            # Split on ", " first, then try ","
            individual = [s.strip() for s in value_str.split(", ")]
            if len(individual) == 1 and "," in value_str:
                individual = [s.strip() for s in value_str.split(",")]
            counter.update(individual)
    return counter


def display_value_table(shape_counter: Counter, total: int) -> None:
    """Display a table of values sorted by frequency."""
    table = Table()
    table.add_column("Rank", style="cyan")
    table.add_column("Cell Shape", style="green", no_wrap=False)
    table.add_column("Count", style="yellow")
    table.add_column("% of Total", style="magenta")

    for i, (shape, count) in enumerate(shape_counter.most_common(), 1):
        percentage = (count / total * 100) if total > 0 else 0
        table.add_row(str(i), shape, f"{count:,}", f"{percentage:.2f}%")

    console.print(table)


def save_to_tsv(shape_counter: Counter, total: int, output_path: Path) -> None:
    """Save results to TSV file."""
    with output_path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["cell_shape", "count", "percentage"])
        for shape, count in shape_counter.most_common():
            percentage = (count / total * 100) if total > 0 else 0
            writer.writerow([shape, count, f"{percentage:.2f}"])

    console.print(f"\n[green]Results saved to {output_path}[/green]")
    console.print(f"  Total unique shapes: {len(shape_counter)}")
    console.print(f"  Total mentions: {sum(shape_counter.values()):,}")


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
    """Analyze cell_shape field."""
    client = MongoClient(mongo_uri)
    db = client[database]
    coll = db[collection]

    total_docs = coll.count_documents({})
    console.print(f"[bold]Total documents:[/bold] {total_docs:,}\n")

    # Count documents with cell_shape
    has_cell_shape = coll.count_documents(
        {"cell_shape": {"$exists": True, "$nin": [None, "NA"]}}
    )
    console.print("[bold]Analyzing cell_shape field:[/bold]")
    console.print(
        f"  Documents with cell_shape (non-NA): {has_cell_shape:,} "
        f"({has_cell_shape / total_docs * 100:.2f}%)"
    )

    # Sample values
    single_examples, comma_examples = get_sample_values(coll, "cell_shape")
    console.print("\n  Sample analysis (first 20):")
    console.print(f"    Single values: {len(single_examples)}")
    console.print(f"    Contains commas: {len(comma_examples)}")

    if single_examples:
        console.print("\n  Examples of single values:")
        for org, shape in single_examples[:10]:
            console.print(f"    {org[:40]}: {shape}")

    if comma_examples:
        console.print("\n  Examples with commas (potential lists):")
        for org, shape in comma_examples:
            console.print(f"    {org[:40]}: {shape}")

    # Check entire collection
    console.print("\n[bold]Checking entire collection:[/bold]")
    comma_shapes = coll.count_documents({"cell_shape": {"$regex": ","}})
    console.print(
        f"  Documents with comma-separated cell_shape: {comma_shapes:,} "
        f"({comma_shapes / has_cell_shape * 100:.2f}% of non-NA)"
    )

    # Get unique values
    unique_shapes = coll.distinct("cell_shape", {"cell_shape": {"$nin": [None, "NA"]}})
    console.print("\n[bold]Unique cell_shape values:[/bold]")
    console.print(f"  Total unique values: {len(unique_shapes):,}")

    # Count occurrences and display
    shape_counter = count_field_values(coll, "cell_shape")
    console.print("\n[bold]All cell_shape values (sorted by frequency):[/bold]")
    display_value_table(shape_counter, has_cell_shape)

    # Analyze naming patterns
    console.print("\n[bold]Analyzing naming patterns:[/bold]")
    underscore_count = sum(1 for shape in unique_shapes if "_" in shape)
    hyphen_count = sum(1 for shape in unique_shapes if "-" in shape)
    console.print(f"  Values with underscores: {underscore_count}/{len(unique_shapes)}")
    console.print(f"  Values with hyphens: {hyphen_count}/{len(unique_shapes)}")

    # Unpack comma-separated if present
    if comma_shapes > 0:
        console.print("\n[bold]Unpacking comma-separated cell_shapes:[/bold]")
        unpacked_counter = unpack_comma_separated(coll, "cell_shape")
        console.print(f"  Unique individual shapes after unpacking: {len(unpacked_counter):,}")

        if len(unpacked_counter) != len(unique_shapes):
            console.print("\n[bold]Individual shapes after unpacking:[/bold]")
            unpacked_table = Table()
            unpacked_table.add_column("Rank", style="cyan")
            unpacked_table.add_column("Shape", style="green")
            unpacked_table.add_column("Count", style="yellow")
            for i, (shape, count) in enumerate(unpacked_counter.most_common(), 1):
                unpacked_table.add_row(str(i), shape, f"{count:,}")
            console.print(unpacked_table)

    # Save to TSV if requested
    if output_tsv:
        save_to_tsv(shape_counter, has_cell_shape, Path(output_tsv))

    client.close()


if __name__ == "__main__":
    cli()
