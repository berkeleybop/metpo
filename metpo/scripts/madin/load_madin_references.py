"""Load madin references from bacteria-archaea-traits repo into MongoDB."""

import csv
from pathlib import Path

import click
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from rich.console import Console

import logging

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

logger = get_logger(__name__)
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
    default="references",
    help="Collection name for references",
    show_default=True,
)
@click.option(
    "--references-file",
    default="/Users/MAM/Documents/gitrepos/bacteria-archaea-traits/output/prepared_references/references.csv",
    help="Path to references.csv file",
    show_default=True,
    type=click.Path(exists=True),
)
@click.option(
    "--drop-existing",
    is_flag=True,
    help="Drop existing collection before loading",
)
def cli(
    mongo_uri: str,
    database: str,
    collection: str,
    references_file: str,
    drop_existing: bool,
) -> None:
    """Load madin references from CSV into MongoDB."""
    try:
        # Check if file exists
        ref_path = Path(references_file)
        if not ref_path.exists():
            console.print(f"[red]Error: File not found: {references_file}[/red]")
            return

        # Connect to MongoDB
        logger.info(f"Connecting to MongoDB: {database}.{collection}")
        client = MongoClient(mongo_uri)
        db = client[database]
        coll = db[collection]

        # Drop existing collection if requested
        if drop_existing:
            logger.info(f"Dropping existing collection: {collection}")
            coll.drop()
            console.print(f"[yellow]Dropped existing collection: {collection}[/yellow]")

        # Read CSV and prepare documents
        logger.info(f"Reading references from: {references_file}")
        documents = []

        # Try different encodings
        encodings = ["utf-8", "latin-1", "iso-8859-1", "cp1252"]
        success = False

        for encoding in encodings:
            try:
                with open(references_file, encoding=encoding) as f:
                    reader = csv.DictReader(f)

                    for row in reader:
                        # Convert ref_id to integer
                        doc = {
                            "ref_id": int(row["ref_id"]),
                            "ref_type": row["ref_type"],
                            "reference": row["reference"],
                        }
                        documents.append(doc)

                logger.info(f"Successfully read file with encoding: {encoding}")
                console.print(f"[green]File encoding detected: {encoding}[/green]")
                success = True
                break
            except UnicodeDecodeError:
                documents = []  # Reset for next attempt
                continue

        if not success:
            raise ValueError(
                f"Could not read file with any of these encodings: {encodings}"
            )

        logger.info(f"Parsed {len(documents)} references from CSV")
        console.print(f"[green]Parsed {len(documents):,} references from CSV[/green]")

        # Insert into MongoDB
        if documents:
            logger.info("Inserting documents into MongoDB...")
            result = coll.insert_many(documents, ordered=False)
            inserted_count = len(result.inserted_ids)

            logger.info(f"Inserted {inserted_count} documents")
            console.print(
                f"[green]Successfully inserted {inserted_count:,} documents[/green]"
            )

            # Create index on ref_id for fast lookups (non-unique since there may be duplicates)
            logger.info("Creating index on ref_id...")
            coll.create_index("ref_id", unique=False)
            console.print("[green]Created index on ref_id[/green]")

            # Check for duplicates
            duplicate_pipeline = [
                {"$group": {"_id": "$ref_id", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gt": 1}}},
                {"$count": "total_duplicates"},
            ]
            dup_result = list(coll.aggregate(duplicate_pipeline))
            if dup_result:
                console.print(
                    f"[yellow]Warning: Found {dup_result[0]['total_duplicates']} ref_ids with duplicates[/yellow]"
                )
            else:
                console.print("[green]No duplicate ref_ids found[/green]")

            # Verify insertion
            total_docs = coll.count_documents({})
            console.print("\n[bold]Verification:[/bold]")
            console.print(f"  Total documents in collection: {total_docs:,}")

            # Show sample references
            console.print("\n[bold]Sample references:[/bold]")
            samples = coll.find().limit(5)
            for doc in samples:
                ref_text = (
                    doc["reference"][:80] + "..."
                    if len(doc["reference"]) > 80
                    else doc["reference"]
                )
                console.print(f"  ref_id {doc['ref_id']}: {ref_text}")

        else:
            console.print("[yellow]No documents to insert[/yellow]")

        client.close()
        console.print("\n[green]✓ References loaded successfully![/green]")

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
