"""Analyze carbon substrates after unpacking comma-separated lists.

This script splits the carbon_substrates field on commas and counts
individual substrate occurrences.
"""

import csv
import logging
from collections import Counter
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


def analyze_unpacked_substrates(
    connection_string: str,
    database_name: str,
    collection_name: str,
) -> tuple[Counter, int, int]:
    """Analyze individual carbon substrates after unpacking lists.

    Args:
        connection_string: MongoDB connection URI
        database_name: Name of the database
        collection_name: Name of the collection

    Returns:
        Tuple of (substrate_counts, total_docs, docs_with_substrates)
    """
    logger.info(f"Connecting to MongoDB: {database_name}.{collection_name}")

    client = MongoClient(connection_string)
    db = client[database_name]
    collection = db[collection_name]

    # Count documents
    total_docs = collection.count_documents({})
    docs_with_field = collection.count_documents(
        {"carbon_substrates": {"$exists": True, "$nin": [None, "NA"]}}
    )

    logger.info(f"Total documents: {total_docs:,}")
    logger.info(f"Documents with carbon_substrates (non-NA): {docs_with_field:,}")

    # Fetch all carbon_substrates values
    cursor = collection.find(
        {"carbon_substrates": {"$exists": True, "$nin": [None, "NA"]}},
        {"carbon_substrates": 1},
    )

    # Unpack and count individual substrates
    substrate_counter = Counter()

    for doc in cursor:
        substrates_str = doc.get("carbon_substrates", "")
        if substrates_str and substrates_str != "NA":
            # Split on ", " (comma-space) to preserve internal commas like "2,3-butanediol"
            individual_substrates = [s.strip() for s in substrates_str.split(", ")]
            substrate_counter.update(individual_substrates)

    logger.info(f"Found {len(substrate_counter)} unique individual substrates")

    client.close()
    return substrate_counter, total_docs, docs_with_field


def display_results(
    substrate_counts: Counter,
    _total_docs: int,
    docs_with_substrates: int,
    top_n: int = 50,
) -> None:
    """Display results in a formatted table.

    Args:
        substrate_counts: Counter of substrate occurrences
        total_docs: Total number of documents in collection
        docs_with_substrates: Number of documents with substrate data
        top_n: Number of top results to show
    """
    # Most common substrates
    table = Table(title="Individual Carbon Substrates (Unpacked from Lists)")
    table.add_column("Rank", justify="right", style="cyan")
    table.add_column("Substrate", style="green")
    table.add_column("Count", justify="right", style="yellow")
    table.add_column("% of Docs w/ Data", justify="right", style="magenta")

    for i, (substrate, count) in enumerate(substrate_counts.most_common(top_n), 1):
        percentage = (
            (count / docs_with_substrates * 100) if docs_with_substrates > 0 else 0
        )
        # Truncate long values
        display_value = substrate if len(substrate) <= 50 else substrate[:47] + "..."
        table.add_row(
            str(i),
            display_value,
            f"{count:,}",
            f"{percentage:.1f}%",
        )

    console.print(table)

    # Show distribution summary
    console.print("\n[bold]Distribution Summary:[/bold]")

    # Count substrates by frequency
    freq_buckets = {
        "1 occurrence": 0,
        "2-5 occurrences": 0,
        "6-10 occurrences": 0,
        "11-50 occurrences": 0,
        "51-100 occurrences": 0,
        "100+ occurrences": 0,
    }

    for count in substrate_counts.values():
        if count == 1:
            freq_buckets["1 occurrence"] += 1
        elif count <= 5:
            freq_buckets["2-5 occurrences"] += 1
        elif count <= 10:
            freq_buckets["6-10 occurrences"] += 1
        elif count <= 50:
            freq_buckets["11-50 occurrences"] += 1
        elif count <= 100:
            freq_buckets["51-100 occurrences"] += 1
        else:
            freq_buckets["100+ occurrences"] += 1

    for bucket, count in freq_buckets.items():
        if count > 0:
            console.print(f"  {bucket}: {count} substrates")


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
    "--top-n",
    default=50,
    help="Number of most common substrates to show",
    show_default=True,
)
@click.option(
    "--output-tsv",
    help="Optional: Save full results to TSV file",
    type=click.Path(),
)
def cli(
    mongo_uri: str,
    database: str,
    collection: str,
    top_n: int,
    output_tsv: str | None,
) -> None:
    """Analyze individual carbon substrates after unpacking comma-separated lists."""
    try:
        # Analyze substrates
        substrate_counts, total_docs, docs_with_substrates = (
            analyze_unpacked_substrates(mongo_uri, database, collection)
        )

        # Display results
        display_results(substrate_counts, total_docs, docs_with_substrates, top_n)

        # Print summary
        console.print("\n[bold]Summary:[/bold]")
        console.print(f"Total documents: {total_docs:,}")
        console.print(f"Documents with substrate data: {docs_with_substrates:,}")
        console.print(f"Unique individual substrates: {len(substrate_counts):,}")
        console.print(f"Total substrate mentions: {sum(substrate_counts.values()):,}")

        # Optionally save to TSV
        if output_tsv:
            with Path(output_tsv).open("w", newline="") as f:
                writer = csv.writer(f, delimiter="\t")
                writer.writerow(["substrate", "count", "percent_of_docs_with_data"])

                for substrate, count in substrate_counts.most_common():
                    percentage = (
                        (count / docs_with_substrates * 100)
                        if docs_with_substrates > 0
                        else 0
                    )
                    writer.writerow([substrate, count, f"{percentage:.2f}"])

            logger.info(f"Full results saved to {output_tsv}")
            console.print(f"\n[green]Full results saved to {output_tsv}[/green]")

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
