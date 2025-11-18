#!/usr/bin/env python
"""
Resilient ChromaDB migration that handles database corruption.

This version:
- Skips corrupted rows instead of crashing
- Commits batches periodically (survives crashes)
- Can resume from last checkpoint
- Logs errors for investigation
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
        return (data.get("embedding") or
                data.get("values") or
                data.get("data") or
                list(data.values())[0])
    else:
        raise ValueError(f"Unexpected embedding format: {type(data)}")


def migrate_embeddings_resilient(
    db_path: str,
    chroma_path: str,
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

    # Initialize ChromaDB first
    print(f"Initializing ChromaDB at: {chroma_path}")
    client = chromadb.PersistentClient(
        path=chroma_path,
        settings=Settings(anonymized_telemetry=False)
    )

    collection = client.get_or_create_collection(
        name="ols_embeddings",
        metadata={"description": "OLS ontology term embeddings from text-embedding-3-small"}
    )

    existing_count = collection.count()
    print(f"Collection '{collection.name}' ready (current count: {existing_count:,})")

    # Open connection with isolation level for better error handling
    conn = sqlite3.connect(db_path, isolation_level=None, timeout=30.0)
    cursor = conn.cursor()
    
    # Build WHERE clause for ontology filtering
    where_clause = ""
    filter_params = []
    
    if include_ontos:
        placeholders = ",".join("?" * len(include_ontos))
        where_clause = f"WHERE ontologyId IN ({placeholders})"
        filter_params = list(include_ontos)
        print(f"Filtering to include ontologies: {', '.join(include_ontos)}")
    elif exclude_ontos:
        placeholders = ",".join("?" * len(exclude_ontos))
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
    if offset > 0:
        query += f" LIMIT -1 OFFSET {offset}"
    elif limit:
        query += f" LIMIT {limit}"

    batch_ids = []
    batch_embeddings = []
    batch_documents = []
    batch_metadatas = []

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

    final_count = collection.count()
    print(f"\n✓ Migration complete!")
    print(f"  Processed: {processed:,} rows")
    print(f"  ChromaDB collection size: {final_count:,}")
    print(f"  Errors encountered: {errors}")
    if errors > 0:
        print(f"  See migration_errors.log for details")
    print(f"\nCollection stored at: {chroma_path}")


@click.command()
@click.option(
    "--db-path",
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    required=True,
    help="Path to SQLite embeddings database"
)
@click.option(
    "--chroma-path",
    type=click.Path(path_type=str),
    default="./chroma_db",
    help="Path to ChromaDB storage directory"
)
@click.option(
    "--batch-size",
    type=int,
    default=1000,
    help="Batch size for migration"
)
@click.option(
    "--limit",
    type=int,
    default=None,
    help="Limit migration to first N embeddings (for testing)"
)
@click.option(
    "--no-resume",
    is_flag=True,
    help="Start from beginning instead of resuming"
)
@click.option(
    "--include",
    "include_ontos",
    multiple=True,
    help="Include only these ontologies (can specify multiple times)"
)
@click.option(
    "--exclude",
    "exclude_ontos",
    multiple=True,
    help="Exclude these ontologies (can specify multiple times)"
)
def main(db_path: str, chroma_path: str, batch_size: int, limit: int | None, no_resume: bool,
         include_ontos: tuple[str, ...], exclude_ontos: tuple[str, ...]):
    """
    Resilient migration from SQLite to ChromaDB with error recovery and ontology filtering.
    
    Examples:
        # Migrate everything
        python migrate_to_chromadb_resilient.py --db-path embeddings.db
        
        # Migrate only specific ontologies
        python migrate_to_chromadb_resilient.py --db-path embeddings.db \\
            --include oba --include pato --include omp
        
        # Migrate everything except large ontologies
        python migrate_to_chromadb_resilient.py --db-path embeddings.db \\
            --exclude ncbitaxon --exclude slm
    """
    migrate_embeddings_resilient(
        db_path=db_path,
        chroma_path=chroma_path,
        batch_size=batch_size,
        limit=limit,
        resume=not no_resume,
        include_ontos=include_ontos,
        exclude_ontos=exclude_ontos
    )


if __name__ == "__main__":
    main()
