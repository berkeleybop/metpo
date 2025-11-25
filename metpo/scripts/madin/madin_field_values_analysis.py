"""Analyze value distribution for a specific field in the madin MongoDB collection.

This script shows common and rare values for a given field.
"""

import csv
import logging
from pathlib import Path

import click
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from rich.console import Console
from rich.table import Table


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

logger = get_logger(__name__)
console = Console()


def analyze_field_values(
    connection_string: str,
    database_name: str,
    collection_name: str,
    field_name: str,
    top_n: int = 20,
    bottom_n: int = 20,
) -> tuple[list[tuple[str, int]], list[tuple[str, int]]]:
    """Analyze value distribution for a specific field.

    Args:
        connection_string: MongoDB connection URI
        database_name: Name of the database
        collection_name: Name of the collection
        field_name: Field to analyze
        top_n: Number of most common values to return
        bottom_n: Number of rarest values to return

    Returns:
        Tuple of (most_common, rarest) as lists of (value, count) tuples
    """
    logger.info(f"Connecting to MongoDB: {database_name}.{collection_name}")

    client = MongoClient(connection_string)
    db = client[database_name]
    collection = db[collection_name]

    # Count documents with this field
    docs_with_field = collection.count_documents(
        {field_name: {"$exists": True, "$ne": None}}
    )
    total_docs = collection.count_documents({})

    logger.info(f"Total documents: {total_docs:,}")
    logger.info(f"Documents with {field_name}: {docs_with_field:,}")

    # Use aggregation to get value counts
    pipeline = [
        {"$match": {field_name: {"$exists": True, "$ne": None}}},
        {"$group": {"_id": f"${field_name}", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]

    results = list(collection.aggregate(pipeline))
    logger.info(f"Found {len(results)} unique values")

    # Get most common
    most_common = [(str(item["_id"]), item["count"]) for item in results[:top_n]]

    # Get rarest (reverse order and take last N)
    rarest = [(str(item["_id"]), item["count"]) for item in results[-bottom_n:]]

    client.close()
    return most_common, rarest


def display_results(
    field_name: str,
    most_common: list[tuple[str, int]],
    rarest: list[tuple[str, int]],
    total_docs: int,
) -> None:
    """Display results in formatted tables.

    Args:
        field_name: Name of the field being analyzed
        most_common: List of most common (value, count) tuples
        rarest: List of rarest (value, count) tuples
        total_docs: Total number of documents
    """
    # Most common values
    table_common = Table(title=f"Most Common Values for '{field_name}'")
    table_common.add_column("Rank", justify="right", style="cyan")
    table_common.add_column("Value", style="green")
    table_common.add_column("Count", justify="right", style="yellow")
    table_common.add_column("% of Total", justify="right", style="magenta")

    for i, (value, count) in enumerate(most_common, 1):
        percentage = (count / total_docs * 100) if total_docs > 0 else 0
        # Truncate long values
        display_value = value if len(value) <= 60 else value[:57] + "..."
        table_common.add_row(
            str(i),
            display_value,
            f"{count:,}",
            f"{percentage:.2f}%",
        )

    console.print(table_common)
    console.print()

    # Rarest values
    table_rare = Table(title=f"Rarest Values for '{field_name}'")
    table_rare.add_column("Value", style="green")
    table_rare.add_column("Count", justify="right", style="yellow")
    table_rare.add_column("% of Total", justify="right", style="magenta")

    for value, count in rarest:
        percentage = (count / total_docs * 100) if total_docs > 0 else 0
        # Truncate long values
        display_value = value if len(value) <= 60 else value[:57] + "..."
        table_rare.add_row(
            display_value,
            f"{count:,}",
            f"{percentage:.2f}%",
        )

    console.print(table_rare)


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
    "--field",
    required=True,
    help="Field name to analyze",
)
@click.option(
    "--top-n",
    default=20,
    help="Number of most common values to show",
    show_default=True,
)
@click.option(
    "--bottom-n",
    default=20,
    help="Number of rarest values to show",
    show_default=True,
)
@click.option(
    "--output-tsv",
    type=click.Path(),
    help="Optional: Save results to TSV file",
)
def cli(
    mongo_uri: str,
    database: str,
    collection: str,
    field: str,
    top_n: int,
    bottom_n: int,
    output_tsv: str | None,
) -> None:
    """Analyze value distribution for a specific field in MongoDB collection."""
    try:
        # Get total doc count
        client = MongoClient(mongo_uri)
        db = client[database]
        coll = db[collection]
        total_docs = coll.count_documents({})
        client.close()

        # Analyze field
        most_common, rarest = analyze_field_values(
            mongo_uri, database, collection, field, top_n, bottom_n
        )

        # Display results
        display_results(field, most_common, rarest, total_docs)

        # Save to TSV if requested
        if output_tsv:
            output_path = Path(output_tsv)
            with output_path.open("w", newline="") as f:
                writer = csv.writer(f, delimiter="\t")
                writer.writerow(
                    ["category", "rank", "value", "count", "percent_of_total"]
                )

                # Write most common
                for i, (value, count) in enumerate(most_common, 1):
                    percentage = (count / total_docs * 100) if total_docs > 0 else 0
                    writer.writerow(
                        ["most_common", i, value, count, f"{percentage:.2f}"]
                    )

                # Write rarest
                for i, (value, count) in enumerate(rarest, 1):
                    percentage = (count / total_docs * 100) if total_docs > 0 else 0
                    writer.writerow(["rarest", i, value, count, f"{percentage:.2f}"])

            console.print(f"\n[green]Results saved to {output_path}[/green]")

        # Print summary
        console.print("\n[bold]Summary:[/bold]")
        console.print(f"Total documents: {total_docs:,}")
        console.print(f"Unique values in '{field}': {len(most_common) + len(rarest):,}")

    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        console.print(f"[red]Connection failed: {e}[/red]")
    except OperationFailure as e:
        logger.error(f"MongoDB operation failed: {e}")
        console.print(f"[red]Operation failed: {e}[/red]")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        console.print(f"[red]Error: {e}[/red]")
        raise


if __name__ == "__main__":
    cli()
