"""Analyze unique values per field in the madin MongoDB collection.

This script connects to the local madin database and generates a table
showing the number of unique values for each field.
"""

import click
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from rich.console import Console
from rich.table import Table

import logging

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

logger = get_logger(__name__)
console = Console()


def analyze_unique_values(
    connection_string: str,
    database_name: str,
    collection_name: str,
) -> dict[str, int]:
    """Analyze unique values per field in a MongoDB collection.

    Args:
        connection_string: MongoDB connection URI
        database_name: Name of the database
        collection_name: Name of the collection

    Returns:
        Dictionary mapping field names to unique value counts

    Raises:
        ConnectionFailure: If cannot connect to MongoDB
        OperationFailure: If database operation fails
    """
    logger.info(f"Connecting to MongoDB: {database_name}.{collection_name}")

    client = MongoClient(connection_string)
    db = client[database_name]
    collection = db[collection_name]

    # Get total document count
    total_docs = collection.count_documents({})
    logger.info(f"Total documents in collection: {total_docs:,}")

    # Get one sample document to extract field names
    sample_doc = collection.find_one()
    if not sample_doc:
        logger.error("Collection is empty")
        return {}

    # Get all field names (excluding _id)
    field_names = [key for key in sample_doc if key != "_id"]
    logger.info(f"Found {len(field_names)} fields")

    # Count unique values for each field
    unique_counts: dict[str, int] = {}

    for field in field_names:
        logger.info(f"Analyzing field: {field}")
        try:
            # Use distinct to get unique values
            unique_values = collection.distinct(field)
            unique_counts[field] = len(unique_values)
            logger.info(f"  {field}: {len(unique_values):,} unique values")
        except Exception as e:
            logger.error(f"  Error analyzing {field}: {e}")
            unique_counts[field] = -1  # Mark as error

    client.close()
    return unique_counts


def display_results_table(
    unique_counts: dict[str, int],
    total_docs: int,
) -> None:
    """Display results in a formatted table.

    Args:
        unique_counts: Dictionary mapping field names to unique value counts
        total_docs: Total number of documents in collection
    """
    table = Table(title="Unique Values Per Field in Madin Dataset")
    table.add_column("Field Name", style="cyan", no_wrap=True)
    table.add_column("Unique Values", justify="right", style="green")
    table.add_column("% of Total", justify="right", style="yellow")
    table.add_column("Cardinality", style="magenta")

    # Sort by field name
    for field in sorted(unique_counts.keys()):
        count = unique_counts[field]

        if count == -1:
            table.add_row(field, "ERROR", "-", "-")
            continue

        # Calculate percentage
        percentage = (count / total_docs * 100) if total_docs > 0 else 0

        # Determine cardinality category
        if count == 1:
            cardinality = "Single value"
        elif count == total_docs:
            cardinality = "Unique key"
        elif count < 10:
            cardinality = "Very low"
        elif count < 100:
            cardinality = "Low"
        elif count < 1000:
            cardinality = "Medium"
        elif percentage > 90:
            cardinality = "Very high"
        else:
            cardinality = "High"

        table.add_row(
            field,
            f"{count:,}",
            f"{percentage:.1f}%",
            cardinality,
        )

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
def cli(
    mongo_uri: str,
    database: str,
    collection: str,
    output_tsv: str | None,
) -> None:
    """Analyze unique values per field in the madin MongoDB collection."""
    try:
        # Connect and get total count first
        client = MongoClient(mongo_uri)
        db = client[database]
        coll = db[collection]
        total_docs = coll.count_documents({})
        client.close()

        # Analyze unique values
        unique_counts = analyze_unique_values(mongo_uri, database, collection)

        # Display results
        display_results_table(unique_counts, total_docs)

        # Optionally save to TSV
        if output_tsv:
            import csv

            with open(output_tsv, "w", newline="") as f:
                writer = csv.writer(f, delimiter="\t")
                writer.writerow(
                    ["field_name", "unique_values", "percent_of_total", "cardinality"]
                )

                for field in sorted(unique_counts.keys()):
                    count = unique_counts[field]
                    if count == -1:
                        writer.writerow([field, "ERROR", "-", "-"])
                        continue

                    percentage = (count / total_docs * 100) if total_docs > 0 else 0

                    if count == 1:
                        cardinality = "Single value"
                    elif count == total_docs:
                        cardinality = "Unique key"
                    elif count < 10:
                        cardinality = "Very low"
                    elif count < 100:
                        cardinality = "Low"
                    elif count < 1000:
                        cardinality = "Medium"
                    elif percentage > 90:
                        cardinality = "Very high"
                    else:
                        cardinality = "High"

                    writer.writerow([field, count, f"{percentage:.1f}", cardinality])

            logger.info(f"Results saved to {output_tsv}")
            console.print(f"\n[green]Results saved to {output_tsv}[/green]")

        # Print summary
        console.print("\n[bold]Summary:[/bold]")
        console.print(f"Total documents: {total_docs:,}")
        console.print(f"Total fields analyzed: {len(unique_counts)}")

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
