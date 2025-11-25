"""Analyze cell_shape field format and values."""

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
    """Analyze cell_shape field."""
    client = MongoClient(mongo_uri)
    db = client[database]
    coll = db[collection]

    total_docs = coll.count_documents({})
    console.print(f"[bold]Total documents:[/bold] {total_docs:,}\n")

    # Check cell_shape field
    console.print("[bold]Analyzing cell_shape field:[/bold]")

    # Count documents with cell_shape
    has_cell_shape = coll.count_documents(
        {"cell_shape": {"$exists": True, "$nin": [None, "NA"]}}
    )
    console.print(
        f"  Documents with cell_shape (non-NA): {has_cell_shape:,} "
        f"({has_cell_shape / total_docs * 100:.2f}%)"
    )

    # Sample some values
    console.print("\n  Sample cell_shape values:")
    samples = list(
        coll.find(
            {"cell_shape": {"$exists": True, "$nin": [None, "NA"]}},
            {"cell_shape": 1, "org_name": 1},
        ).limit(20)
    )

    # Check if they contain commas (indicating lists)
    contains_comma = 0
    single_value = 0
    examples_with_comma = []
    examples_single = []

    for doc in samples:
        cell_shape = doc.get("cell_shape")
        org_name = doc.get("org_name", "")

        if isinstance(cell_shape, str):
            if "," in cell_shape:
                contains_comma += 1
                if len(examples_with_comma) < 5:
                    examples_with_comma.append((org_name, cell_shape))
            else:
                single_value += 1
                if len(examples_single) < 10:
                    examples_single.append((org_name, cell_shape))

    console.print("\n  Sample analysis (first 20):")
    console.print(f"    Single values: {single_value}/20")
    console.print(f"    Contains commas: {contains_comma}/20")

    if examples_single:
        console.print("\n  Examples of single values:")
        for org, shape in examples_single[:10]:
            console.print(f"    {org[:40]}: {shape}")

    if examples_with_comma:
        console.print("\n  Examples with commas (potential lists):")
        for org, shape in examples_with_comma:
            console.print(f"    {org[:40]}: {shape}")

    # Check entire collection for comma-containing cell_shape
    console.print("\n[bold]Checking entire collection:[/bold]")

    # Count docs with commas in cell_shape
    comma_shapes = coll.count_documents({"cell_shape": {"$regex": ","}})
    console.print(
        f"  Documents with comma-separated cell_shape: {comma_shapes:,} "
        f"({comma_shapes / has_cell_shape * 100:.2f}% of non-NA)"
    )

    # Get unique values
    console.print("\n[bold]Unique cell_shape values:[/bold]")
    unique_shapes = coll.distinct("cell_shape", {"cell_shape": {"$nin": [None, "NA"]}})
    console.print(f"  Total unique values: {len(unique_shapes):,}")

    # Count occurrences
    shape_counter = Counter()

    cursor = coll.find(
        {"cell_shape": {"$exists": True, "$nin": [None, "NA"]}},
        {"cell_shape": 1},
    )

    for doc in cursor:
        shape = doc.get("cell_shape", "")
        if shape and shape != "NA":
            shape_counter[shape] += 1

    # Show all values sorted by count
    console.print("\n[bold]All cell_shape values (sorted by frequency):[/bold]")
    table = Table()
    table.add_column("Rank", style="cyan")
    table.add_column("Cell Shape", style="green", no_wrap=False)
    table.add_column("Count", style="yellow")
    table.add_column("% of Total", style="magenta")

    for i, (shape, count) in enumerate(shape_counter.most_common(), 1):
        percentage = (count / has_cell_shape * 100) if has_cell_shape > 0 else 0
        table.add_row(str(i), shape, f"{count:,}", f"{percentage:.2f}%")

    console.print(table)

    # Check for underscores or hyphens
    console.print("\n[bold]Analyzing naming patterns:[/bold]")
    underscore_count = sum(1 for shape in unique_shapes if "_" in shape)
    hyphen_count = sum(1 for shape in unique_shapes if "-" in shape)
    console.print(f"  Values with underscores: {underscore_count}/{len(unique_shapes)}")
    console.print(f"  Values with hyphens: {hyphen_count}/{len(unique_shapes)}")

    # If commas exist, try unpacking
    if comma_shapes > 0:
        console.print("\n[bold]Unpacking comma-separated cell_shapes:[/bold]")

        unpacked_counter = Counter()

        cursor = coll.find(
            {"cell_shape": {"$exists": True, "$nin": [None, "NA"]}},
            {"cell_shape": 1},
        )

        for doc in cursor:
            shape_str = doc.get("cell_shape", "")
            if shape_str and shape_str != "NA":
                # Split on ", " first, then try ","
                individual_shapes = [s.strip() for s in shape_str.split(", ")]
                if len(individual_shapes) == 1 and "," in shape_str:
                    individual_shapes = [s.strip() for s in shape_str.split(",")]
                unpacked_counter.update(individual_shapes)

        console.print(
            f"  Unique individual shapes after unpacking: {len(unpacked_counter):,}"
        )

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
        import csv

        with open(output_tsv, "w", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(["cell_shape", "count", "percentage"])

            for shape, count in shape_counter.most_common():
                percentage = (count / has_cell_shape * 100) if has_cell_shape > 0 else 0
                writer.writerow([shape, count, f"{percentage:.2f}"])

        console.print(f"\n[green]Results saved to {output_tsv}[/green]")
        console.print(f"  Total unique shapes: {len(shape_counter)}")
        console.print(f"  Total mentions: {sum(shape_counter.values()):,}")

    client.close()


if __name__ == "__main__":
    cli()
