"""Generate TSV reports of unique value usage for categorical and list fields.

This script reads the field summary table to identify categorical and list fields,
then generates detailed TSV reports showing value distributions and counts.
"""

import csv
from collections import Counter
from pathlib import Path

import click
from pymongo import MongoClient
from rich.console import Console


# Default output directory for madin analysis
def get_madin_output_dir() -> Path:
    """Get the default output directory for madin analysis."""
    return Path(__file__).parent.parent.parent.parent / "docs" / "madin_paths"

console = Console()


def load_field_summary(tsv_path: Path) -> dict[str, dict]:
    """Load field summary table and categorize fields.

    Returns:
        Dictionary mapping field names to their metadata
    """
    fields = {}

    with tsv_path.open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            field_name = row["Field Name"]
            fields[field_name] = {
                "data_type": row["Data Type"],
                "subtype": row["Subtype"],
                "unique_count": int(row["Unique Values"]),
                "unpacked_count": row["Unpacked Unique"],
            }

    return fields


def generate_categorical_report(
    coll,
    field_name: str,
    output_file: Path,
    total_docs: int,
) -> None:
    """Generate TSV report for a categorical field.

    Args:
        coll: MongoDB collection
        field_name: Name of the field to analyze
        output_file: Path to output TSV file
        total_docs: Total number of documents in collection
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

    # Write TSV
    with output_file.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow([field_name, "count", "percentage", "pct_of_total"])

        for value, count in value_counter.most_common():
            pct_of_has_field = (count / has_field * 100) if has_field > 0 else 0
            pct_of_total = (count / total_docs * 100) if total_docs > 0 else 0
            writer.writerow(
                [value, count, f"{pct_of_has_field:.2f}", f"{pct_of_total:.2f}"]
            )

    console.print(
        f"  [green]✓[/green] {field_name}: {len(value_counter)} unique values → {output_file.name}"
    )


def generate_list_report(
    coll,
    field_name: str,
    output_file: Path,
    _total_docs: int,
) -> None:
    """Generate TSV report for a list field (comma-separated).

    Args:
        coll: MongoDB collection
        field_name: Name of the field to analyze
        output_file: Path to output TSV file
        total_docs: Total number of documents in collection
    """
    # Count documents with field
    coll.count_documents({field_name: {"$exists": True, "$nin": [None, "NA"]}})

    # Unpack and count individual elements
    unpacked_counter = Counter()

    cursor = coll.find(
        {field_name: {"$exists": True, "$nin": [None, "NA"]}},
        {field_name: 1},
    )

    for doc in cursor:
        value_str = doc.get(field_name, "")
        if value_str and value_str != "NA":
            # Split on ", " (comma-space)
            individual_values = [v.strip() for v in value_str.split(", ")]
            unpacked_counter.update(individual_values)

    # Write TSV
    with output_file.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow([f"{field_name}_element", "count", "percentage"])

        total_mentions = sum(unpacked_counter.values())

        for value, count in unpacked_counter.most_common():
            percentage = (count / total_mentions * 100) if total_mentions > 0 else 0
            writer.writerow([value, count, f"{percentage:.2f}"])

    console.print(
        f"  [green]✓[/green] {field_name}: {len(unpacked_counter)} unique elements "
        f"({total_mentions:,} total mentions) → {output_file.name}"
    )


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
    "--field-summary",
    help="Path to field summary TSV (input)",
    type=click.Path(exists=True),
)
@click.option(
    "--output-dir",
    help="Directory to save TSV reports",
    type=click.Path(),
)
def cli(
    mongo_uri: str,
    database: str,
    collection: str,
    field_summary: str | None,
    output_dir: str | None,
) -> None:
    """Generate value distribution reports for categorical and list fields."""
    # Set defaults using project paths
    if field_summary is None:
        field_summary_path = get_madin_output_dir() / "madin_field_summary.tsv"
    else:
        field_summary_path = Path(field_summary)

    if output_dir is None:
        output_path = get_madin_output_dir() / "field_reports"
    else:
        output_path = Path(output_dir)

    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client[database]
    coll = db[collection]

    total_docs = coll.count_documents({})
    console.print(f"[bold]Total documents:[/bold] {total_docs:,}\n")

    # Load field summary
    console.print(f"[bold]Loading field summary from:[/bold] {field_summary_path}")
    fields = load_field_summary(field_summary_path)
    console.print(f"  Found {len(fields)} fields\n")

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    console.print(f"[bold]Output directory:[/bold] {output_path}\n")

    # Identify categorical and list fields
    categorical_fields = [
        name for name, meta in fields.items() if meta["data_type"] == "categorical"
    ]
    list_fields = [name for name, meta in fields.items() if meta["data_type"] == "list"]

    console.print(
        f"[bold cyan]Categorical fields:[/bold cyan] {len(categorical_fields)}"
    )
    console.print(f"[bold cyan]List fields:[/bold cyan] {len(list_fields)}\n")

    # Generate categorical reports
    if categorical_fields:
        console.print("[bold]Generating categorical field reports:[/bold]")
        for field_name in sorted(categorical_fields):
            output_file = output_path / f"madin_{field_name}.tsv"
            generate_categorical_report(coll, field_name, output_file, total_docs)
        console.print()

    # Generate list reports
    if list_fields:
        console.print("[bold]Generating list field reports:[/bold]")
        for field_name in sorted(list_fields):
            output_file = output_path / f"madin_{field_name}_unpacked.tsv"
            generate_list_report(coll, field_name, output_file, total_docs)
        console.print()

    console.print(
        f"[bold green]✓ Complete![/bold green] All reports saved to {output_path}/"
    )

    client.close()


if __name__ == "__main__":
    cli()
