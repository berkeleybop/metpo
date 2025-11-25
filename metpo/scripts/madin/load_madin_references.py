"""Load madin references from bacteria-archaea-traits repo into MongoDB."""

import csv
import logging
from pathlib import Path

import click
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, OperationFailure
from rich.console import Console


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


logger = get_logger(__name__)
console = Console()

ENCODINGS = ["utf-8", "latin-1", "iso-8859-1", "cp1252"]


def read_references_csv(ref_path: Path) -> list[dict]:
    """Read references from CSV file, trying multiple encodings."""
    for encoding in ENCODINGS:
        try:
            documents = []
            with ref_path.open(encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    documents.append({
                        "ref_id": int(row["ref_id"]),
                        "ref_type": row["ref_type"],
                        "reference": row["reference"],
                    })

            logger.info(f"Successfully read file with encoding: {encoding}")
            console.print(f"[green]File encoding detected: {encoding}[/green]")
            return documents
        except UnicodeDecodeError:
            continue

    raise ValueError(f"Could not read file with any of these encodings: {ENCODINGS}")


def insert_documents(coll: Collection, documents: list[dict]) -> int:
    """Insert documents into MongoDB and create index."""
    logger.info("Inserting documents into MongoDB...")
    result = coll.insert_many(documents, ordered=False)
    inserted_count = len(result.inserted_ids)

    logger.info(f"Inserted {inserted_count} documents")
    console.print(f"[green]Successfully inserted {inserted_count:,} documents[/green]")

    logger.info("Creating index on ref_id...")
    coll.create_index("ref_id", unique=False)
    console.print("[green]Created index on ref_id[/green]")

    return inserted_count


def check_duplicates(coll: Collection) -> None:
    """Check for duplicate ref_ids in collection."""
    pipeline = [
        {"$group": {"_id": "$ref_id", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}},
        {"$count": "total_duplicates"},
    ]
    dup_result = list(coll.aggregate(pipeline))
    if dup_result:
        console.print(f"[yellow]Warning: Found {dup_result[0]['total_duplicates']} ref_ids with duplicates[/yellow]")
    else:
        console.print("[green]No duplicate ref_ids found[/green]")


def show_verification(coll: Collection) -> None:
    """Show verification info and sample references."""
    total_docs = coll.count_documents({})
    console.print("\n[bold]Verification:[/bold]")
    console.print(f"  Total documents in collection: {total_docs:,}")

    console.print("\n[bold]Sample references:[/bold]")
    for doc in coll.find().limit(5):
        ref_text = doc["reference"][:80] + "..." if len(doc["reference"]) > 80 else doc["reference"]
        console.print(f"  ref_id {doc['ref_id']}: {ref_text}")


@click.command()
@click.option("--mongo-uri", default="mongodb://localhost:27017", help="MongoDB connection URI", show_default=True)
@click.option("--database", default="madin", help="Database name", show_default=True)
@click.option("--collection", default="references", help="Collection name for references", show_default=True)
@click.option("--references-file", required=True, help="Path to references.csv file", type=click.Path(exists=True))
@click.option("--drop-existing", is_flag=True, help="Drop existing collection before loading")
def cli(mongo_uri: str, database: str, collection: str, references_file: str, drop_existing: bool) -> None:
    """Load madin references from CSV into MongoDB."""
    try:
        ref_path = Path(references_file)
        if not ref_path.exists():
            console.print(f"[red]Error: File not found: {references_file}[/red]")
            return

        logger.info(f"Connecting to MongoDB: {database}.{collection}")
        client = MongoClient(mongo_uri)
        coll = client[database][collection]

        if drop_existing:
            logger.info(f"Dropping existing collection: {collection}")
            coll.drop()
            console.print(f"[yellow]Dropped existing collection: {collection}[/yellow]")

        logger.info(f"Reading references from: {references_file}")
        documents = read_references_csv(ref_path)
        logger.info(f"Parsed {len(documents)} references from CSV")
        console.print(f"[green]Parsed {len(documents):,} references from CSV[/green]")

        if documents:
            insert_documents(coll, documents)
            check_duplicates(coll)
            show_verification(coll)
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
