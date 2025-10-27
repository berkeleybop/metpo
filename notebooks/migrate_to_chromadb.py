#!/usr/bin/env python
"""
Migrate embeddings from SQLite to ChromaDB for fast vector similarity search.

This script reads embeddings from embeddings.db and loads them into ChromaDB,
which provides efficient vector similarity search using HNSW indexing.
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
        # Try common keys
        return (data.get('embedding') or
                data.get('values') or
                data.get('data') or
                list(data.values())[0])
    else:
        raise ValueError(f"Unexpected embedding format: {type(data)}")


def migrate_embeddings(
    db_path: str,
    chroma_path: str,
    batch_size: int = 1000,
    limit: int | None = None
):
    """Migrate embeddings from SQLite to ChromaDB."""

    print(f"Connecting to SQLite database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Count total embeddings
    count_query = "SELECT COUNT(*) FROM embeddings"
    if limit:
        count_query += f" LIMIT {limit}"
    total = cursor.execute(count_query).fetchone()[0]

    if limit:
        total = min(total, limit)

    print(f"Total embeddings to migrate: {total:,}")

    # Initialize ChromaDB
    print(f"Initializing ChromaDB at: {chroma_path}")
    client = chromadb.PersistentClient(
        path=chroma_path,
        settings=Settings(anonymized_telemetry=False)
    )

    # Create or get collection
    # Note: ChromaDB will auto-create HNSW index for fast similarity search
    collection = client.get_or_create_collection(
        name="ols_embeddings",
        metadata={"description": "OLS ontology term embeddings from text-embedding-3-small"}
    )

    print(f"Collection '{collection.name}' ready (current count: {collection.count()})")

    # Migrate in batches
    query = "SELECT ontologyId, iri, document, embeddings FROM embeddings"
    if limit:
        query += f" LIMIT {limit}"

    cursor.execute(query)

    batch_ids = []
    batch_embeddings = []
    batch_documents = []
    batch_metadatas = []

    processed = 0

    with tqdm(total=total, desc="Migrating embeddings") as pbar:
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break

            for ontology_id, iri, document, embedding_json in rows:
                try:
                    embedding_vector = extract_embedding_vector(embedding_json)

                    # Use ontologyId:IRI as unique ID (handles duplicates across ontologies)
                    unique_id = f"{ontology_id}:{iri}"
                    batch_ids.append(unique_id)
                    batch_embeddings.append(embedding_vector)
                    batch_documents.append(document)
                    batch_metadatas.append({
                        "ontologyId": ontology_id,
                        "iri": iri
                    })

                    processed += 1
                    pbar.update(1)

                except Exception as e:
                    print(f"\nError processing {iri}: {e}")
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
                    print(f"\nError adding batch to ChromaDB: {e}")
                    # Try adding one by one to identify problematic entries
                    for i in range(len(batch_ids)):
                        try:
                            collection.add(
                                ids=[batch_ids[i]],
                                embeddings=[batch_embeddings[i]],
                                documents=[batch_documents[i]],
                                metadatas=[batch_metadatas[i]]
                            )
                        except Exception as e2:
                            print(f"Failed to add {batch_ids[i]}: {e2}")

                # Clear batch
                batch_ids = []
                batch_embeddings = []
                batch_documents = []
                batch_metadatas = []

    conn.close()

    print(f"\n✓ Migration complete!")
    print(f"  Processed: {processed:,} embeddings")
    print(f"  ChromaDB collection size: {collection.count():,}")
    print(f"\nCollection stored at: {chroma_path}")


@click.command()
@click.option(
    '--db-path',
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    required=True,
    help="Path to SQLite embeddings database"
)
@click.option(
    '--chroma-path',
    type=click.Path(path_type=str),
    default="./chroma_db",
    help="Path to ChromaDB storage directory"
)
@click.option(
    '--batch-size',
    type=int,
    default=1000,
    help="Batch size for migration"
)
@click.option(
    '--limit',
    type=int,
    default=None,
    help="Limit migration to first N embeddings (for testing)"
)
def main(db_path: str, chroma_path: str, batch_size: int, limit: int | None):
    """Migrate embeddings from SQLite to ChromaDB for fast vector similarity search."""
    migrate_embeddings(
        db_path=db_path,
        chroma_path=chroma_path,
        batch_size=batch_size,
        limit=limit
    )


if __name__ == "__main__":
    main()
