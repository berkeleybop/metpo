#!/usr/bin/env python
"""
Resilient Qdrant migration that handles database corruption.

Qdrant advantages over ChromaDB:
- Disk-backed storage with memory-mapped files
- More memory-efficient for large datasets (290GB embeddings)
- Better indexing performance on limited hardware
- No in-memory HNSW rebuild issues

This version:
- Skips corrupted rows instead of crashing
- Commits batches periodically (survives crashes)
- Can resume from last checkpoint
- Logs errors for investigation
- Uses Qdrant's efficient disk-based indexing
"""

import sqlite3
import json
import click
from pathlib import Path
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, HnswConfigDiff, OptimizersConfigDiff
import hashlib


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


def string_to_id(s: str) -> int:
    """Convert string to deterministic integer ID for Qdrant (uses first 8 bytes of SHA256)."""
    hash_bytes = hashlib.sha256(s.encode('utf-8')).digest()
    # Convert first 8 bytes to unsigned 64-bit integer
    return int.from_bytes(hash_bytes[:8], byteorder='big', signed=False)


def migrate_embeddings_resilient(
    db_path: str,
    qdrant_path: str,
    collection_name: str = "ols_embeddings",
    batch_size: int = 1000,
    limit: int | None = None,
    resume: bool = True,
    include_ontos: tuple[str, ...] = (),
    exclude_ontos: tuple[str, ...] = ()
):
    """Migrate embeddings with error recovery and optional ontology filtering."""

    # Validate mutually exclusive options
    if include_ontos and exclude_ontos:
        raise click.UsageError("Cannot use both --include and --exclude. Choose one approach.")

    print(f"Connecting to SQLite database: {db_path}")

    # Initialize Qdrant client (disk-backed storage)
    print(f"Initializing Qdrant at: {qdrant_path}")
    client = QdrantClient(path=qdrant_path)

    # Check if collection exists, create if not
    collections = client.get_collections().collections
    collection_exists = any(c.name == collection_name for c in collections)

    if not collection_exists:
        print(f"Creating collection '{collection_name}' with 1536-dim vectors (text-embedding-3-small)")
        print("  Using optimized HNSW config for large-scale queries...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1536,  # text-embedding-3-small dimension
                distance=Distance.COSINE,
                on_disk=True  # Keep vectors on disk for memory efficiency
            ),
            hnsw_config=HnswConfigDiff(
                m=16,  # Connections per layer (balance speed/memory)
                ef_construct=100,  # Build quality
                full_scan_threshold=10000,  # Use HNSW index above this count
                on_disk=True  # Keep HNSW graph on disk
            ),
            optimizers_config=OptimizersConfigDiff(
                indexing_threshold=20000,  # Trigger segmentation/indexing
                memmap_threshold=20000  # Use memory mapping for large segments
            )
        )
    else:
        print(f"Collection '{collection_name}' already exists")

    # Get existing count
    collection_info = client.get_collection(collection_name=collection_name)
    existing_count = collection_info.points_count
    print(f"Collection '{collection_name}' ready (current count: {existing_count:,})")

    # Open connection with isolation level for better error handling
    conn = sqlite3.connect(db_path, isolation_level=None, timeout=30.0)
    cursor = conn.cursor()

    # Build WHERE clause for ontology filtering
    where_clause = ""
    filter_params = []

    if include_ontos:
        placeholders = ','.join('?' * len(include_ontos))
        where_clause = f"WHERE ontologyId IN ({placeholders})"
        filter_params = list(include_ontos)
        print(f"Filtering to include ontologies: {', '.join(include_ontos)}")
    elif exclude_ontos:
        placeholders = ','.join('?' * len(exclude_ontos))
        where_clause = f"WHERE ontologyId NOT IN ({placeholders})"
        filter_params = list(exclude_ontos)
        print(f"Filtering to exclude ontologies: {', '.join(exclude_ontos)}")

    # Count total
    try:
        count_query = f"SELECT COUNT(*) FROM embeddings {where_clause}"
        if limit:
            total = min(cursor.execute(count_query, filter_params).fetchone()[0], limit)
        else:
            total = cursor.execute(count_query, filter_params).fetchone()[0]
        print(f"Total embeddings to migrate: {total:,}")
    except sqlite3.DatabaseError as e:
        print(f"Warning: Could not count total rows: {e}")
        total = limit if limit else 9570045  # Known total from earlier

    # Resume from where we left off
    offset = existing_count if resume else 0
    if offset > 0:
        print(f"Resuming from offset {offset:,}")

    # Query with filtering, offset and limit
    query = f"SELECT ontologyId, entityType, iri, document, embeddings FROM embeddings {where_clause}"
    if offset > 0 and limit:
        # Resume: only fetch remaining rows up to limit
        remaining = limit - offset
        query += f" LIMIT {remaining} OFFSET {offset}"
    elif offset > 0:
        # Resume without limit: fetch all remaining
        query += f" LIMIT -1 OFFSET {offset}"
    elif limit:
        # Fresh start with limit
        query += f" LIMIT {limit}"

    batch_points = []

    processed = offset
    errors = 0
    error_log = open("migration_errors.log", "a")

    print(f"\nStarting migration...")

    with tqdm(total=total, initial=offset, desc="Migrating embeddings") as pbar:
        try:
            cursor.execute(query, filter_params)

            while True:
                try:
                    rows = cursor.fetchmany(batch_size)
                    if not rows:
                        break

                    for ontology_id, entity_type, iri, document, embedding_json in rows:
                        try:
                            embedding_vector = extract_embedding_vector(embedding_json)

                            # Create unique string ID and convert to integer
                            unique_str_id = f"{ontology_id}:{entity_type}:{iri}"
                            point_id = string_to_id(unique_str_id)

                            # Create Qdrant point with payload (metadata)
                            point = PointStruct(
                                id=point_id,
                                vector=embedding_vector,
                                payload={
                                    "ontologyId": ontology_id,
                                    "entityType": entity_type,
                                    "iri": iri,
                                    "document": document,
                                    "unique_id": unique_str_id  # Store string ID for reference
                                }
                            )
                            batch_points.append(point)

                            processed += 1
                            pbar.update(1)

                        except Exception as e:
                            errors += 1
                            error_log.write(f"Error processing {ontology_id}:{entity_type}:{iri}: {e}\n")
                            error_log.flush()
                            continue

                    # Upsert batch to Qdrant
                    if batch_points:
                        try:
                            client.upsert(
                                collection_name=collection_name,
                                points=batch_points
                            )
                        except Exception as e:
                            # Try one by one if batch fails
                            for point in batch_points:
                                try:
                                    client.upsert(
                                        collection_name=collection_name,
                                        points=[point]
                                    )
                                except Exception as e2:
                                    errors += 1
                                    error_log.write(f"Failed to add point {point.payload.get('unique_id')}: {e2}\n")
                                    error_log.flush()

                        # Clear batch
                        batch_points = []

                except sqlite3.DatabaseError as e:
                    # Database corruption encountered - log and try to continue
                    error_msg = f"Database error at offset {processed}: {e}\n"
                    print(f"\n{error_msg}")
                    error_log.write(error_msg)
                    error_log.flush()
                    errors += 1

                    # Try to skip ahead
                    try:
                        cursor.close()
                        conn.close()
                        conn = sqlite3.connect(db_path, isolation_level=None, timeout=30.0)
                        cursor = conn.cursor()

                        # Skip corrupted section - jump ahead by batch_size
                        processed += batch_size
                        query_resume = f"SELECT ontologyId, entityType, iri, document, embeddings FROM embeddings {where_clause} LIMIT -1 OFFSET {processed}"
                        cursor.execute(query_resume, filter_params)
                        pbar.update(batch_size)
                        print(f"Reconnected and skipped to offset {processed:,}")
                    except Exception as e2:
                        print(f"Could not resume: {e2}")
                        break

        except KeyboardInterrupt:
            print("\n\nMigration interrupted by user")
        finally:
            error_log.close()
            conn.close()

    # Get final count
    collection_info = client.get_collection(collection_name=collection_name)
    final_count = collection_info.points_count

    print(f"\n✓ Migration complete!")
    print(f"  Processed: {processed:,} rows")
    print(f"  Qdrant collection size: {final_count:,}")
    print(f"  Errors encountered: {errors}")
    if errors > 0:
        print(f"  See migration_errors.log for details")
    print(f"\nCollection stored at: {qdrant_path}")


@click.command()
@click.option(
    '--db-path',
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    required=True,
    help="Path to SQLite embeddings database"
)
@click.option(
    '--qdrant-path',
    type=click.Path(path_type=str),
    default="./qdrant_db",
    help="Path to Qdrant storage directory"
)
@click.option(
    '--collection-name',
    type=str,
    default="ols_embeddings",
    help="Name of Qdrant collection"
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
@click.option(
    '--no-resume',
    is_flag=True,
    help="Start from beginning instead of resuming"
)
@click.option(
    '--include',
    'include_ontos',
    multiple=True,
    help="Include only these ontologies (can specify multiple times)"
)
@click.option(
    '--exclude',
    'exclude_ontos',
    multiple=True,
    help="Exclude these ontologies (can specify multiple times)"
)
def main(db_path: str, qdrant_path: str, collection_name: str, batch_size: int,
         limit: int | None, no_resume: bool,
         include_ontos: tuple[str, ...], exclude_ontos: tuple[str, ...]):
    """
    Resilient migration from SQLite to Qdrant with error recovery and ontology filtering.

    Qdrant is optimized for large-scale embeddings on limited hardware:
    - Disk-backed storage with memory-mapped files
    - No in-memory HNSW rebuild (unlike ChromaDB)
    - Better memory efficiency for 290GB+ datasets

    Examples:
        # Test with small subset
        python migrate_to_qdrant_resilient.py --db-path embeddings.db --limit 1000

        # Migrate everything
        python migrate_to_qdrant_resilient.py --db-path embeddings.db

        # Migrate only specific ontologies
        python migrate_to_qdrant_resilient.py --db-path embeddings.db \\
            --include oba --include pato --include omp

        # Migrate everything except large ontologies
        python migrate_to_qdrant_resilient.py --db-path embeddings.db \\
            --exclude ncbitaxon --exclude slm
    """
    migrate_embeddings_resilient(
        db_path=db_path,
        qdrant_path=qdrant_path,
        collection_name=collection_name,
        batch_size=batch_size,
        limit=limit,
        resume=not no_resume,
        include_ontos=include_ontos,
        exclude_ontos=exclude_ontos
    )


if __name__ == "__main__":
    main()
