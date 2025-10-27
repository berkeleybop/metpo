#!/usr/bin/env python
"""
Migrate ONLY OBA (Ontology of Biological Attributes) embeddings to ChromaDB.

This is an incremental test to verify semantic matching works correctly
before attempting to migrate larger ontology sets.
"""

import sqlite3
import json
import click
from pathlib import Path
from tqdm import tqdm
import chromadb
from chromadb.config import Settings


def extract_embedding_vector(embedding_json: str) -> list[float]:
    """Extract embedding vector from JSON, handling dict or list formats."""
    data = json.loads(embedding_json)

    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        return (data.get('embedding') or
                data.get('values') or
                data.get('data') or
                list(data.values())[0])
    else:
        raise ValueError(f"Unexpected embedding format: {type(data)}")


def migrate_oba_only(
    db_path: str,
    chroma_path: str,
    batch_size: int = 1000
):
    """Migrate OBA embeddings only."""

    print(f"Connecting to SQLite database: {db_path}")

    # Initialize ChromaDB
    print(f"Initializing ChromaDB at: {chroma_path}")
    client = chromadb.PersistentClient(
        path=chroma_path,
        settings=Settings(anonymized_telemetry=False)
    )

    collection = client.get_or_create_collection(
        name="oba_embeddings",
        metadata={"description": "OBA (Ontology of Biological Attributes) embeddings only"}
    )

    existing_count = collection.count()
    print(f"Collection '{collection.name}' ready (current count: {existing_count:,})")

    # Open connection
    conn = sqlite3.connect(db_path, isolation_level=None, timeout=30.0)
    cursor = conn.cursor()

    # Count OBA records only
    total = cursor.execute(
        "SELECT COUNT(*) FROM embeddings WHERE ontologyId = 'oba'"
    ).fetchone()[0]
    print(f"Total OBA embeddings in database: {total:,}")

    # Query ONLY OBA records
    query = """
    SELECT ontologyId, entityType, iri, document, embeddings
    FROM embeddings
    WHERE ontologyId = 'oba'
    """

    batch_ids = []
    batch_embeddings = []
    batch_documents = []
    batch_metadatas = []

    processed = 0
    errors = 0
    error_log = open("oba_migration_errors.log", "w")

    print(f"\nMigrating OBA embeddings...")

    with tqdm(total=total, desc="Migrating OBA") as pbar:
        try:
            cursor.execute(query)

            while True:
                try:
                    rows = cursor.fetchmany(batch_size)
                    if not rows:
                        break

                    for ontology_id, entity_type, iri, document, embedding_json in rows:
                        try:
                            embedding_vector = extract_embedding_vector(embedding_json)

                            unique_id = f"{ontology_id}:{entity_type}:{iri}"
                            batch_ids.append(unique_id)
                            batch_embeddings.append(embedding_vector)
                            batch_documents.append(document)
                            batch_metadatas.append({
                                "ontologyId": ontology_id,
                                "entityType": entity_type,
                                "iri": iri
                            })

                            processed += 1
                            pbar.update(1)

                        except Exception as e:
                            errors += 1
                            error_log.write(f"Error processing {ontology_id}:{entity_type}:{iri}: {e}\n")
                            error_log.flush()
                            continue

                    # Add batch to ChromaDB
                    if batch_ids:
                        try:
                            collection.add(
                                ids=batch_ids,
                                embeddings=batch_embeddings,
                                documents=batch_documents,
                                metadatas=batch_metadatas
                            )
                        except Exception as e:
                            # Try one by one if batch fails
                            for i in range(len(batch_ids)):
                                try:
                                    collection.add(
                                        ids=[batch_ids[i]],
                                        embeddings=[batch_embeddings[i]],
                                        documents=[batch_documents[i]],
                                        metadatas=[batch_metadatas[i]]
                                    )
                                except Exception as e2:
                                    errors += 1
                                    error_log.write(f"Failed to add {batch_ids[i]}: {e2}\n")
                                    error_log.flush()

                        # Clear batch
                        batch_ids = []
                        batch_embeddings = []
                        batch_documents = []
                        batch_metadatas = []

                except sqlite3.DatabaseError as e:
                    error_msg = f"Database error at record {processed}: {e}\n"
                    print(f"\n{error_msg}")
                    error_log.write(error_msg)
                    error_log.flush()
                    errors += 1
                    break

        except KeyboardInterrupt:
            print("\n\nMigration interrupted by user")
        finally:
            error_log.close()
            conn.close()

    final_count = collection.count()
    print(f"\n✓ Migration complete!")
    print(f"  Processed: {processed:,} rows")
    print(f"  ChromaDB collection size: {final_count:,}")
    print(f"  Errors encountered: {errors}")
    if errors > 0:
        print(f"  See oba_migration_errors.log for details")
    print(f"\nCollection stored at: {chroma_path}")


@click.command()
@click.option(
    '--db-path',
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    default=str(Path.home() / "embeddings.db"),
    help="Path to SQLite embeddings database"
)
@click.option(
    '--chroma-path',
    type=click.Path(path_type=str),
    default="./oba_chroma",
    help="Path to ChromaDB storage directory (default: ./oba_chroma)"
)
@click.option(
    '--batch-size',
    type=int,
    default=1000,
    help="Batch size for migration"
)
def main(db_path: str, chroma_path: str, batch_size: int):
    """Migrate ONLY OBA embeddings to ChromaDB for testing."""
    migrate_oba_only(
        db_path=db_path,
        chroma_path=chroma_path,
        batch_size=batch_size
    )


if __name__ == "__main__":
    main()
