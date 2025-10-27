#!/usr/bin/env python
"""
Migrate filtered subset of embeddings to ChromaDB.

Supports filtering by:
- Include specific ontologies (--include)
- Exclude specific ontologies (--exclude)

Examples:
    # Migrate only OBA
    python migrate_filtered.py --include oba --chroma-path ./oba_chroma

    # Migrate METPO-relevant ontologies
    python migrate_filtered.py --include oba --include pato --include envo --chroma-path ./metpo_relevant_chroma

    # Migrate everything except large ontologies
    python migrate_filtered.py --exclude ncbitaxon --exclude slm --exclude dron
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


def build_where_clause(include_ontos: tuple[str, ...], exclude_ontos: tuple[str, ...]) -> str:
    """Build SQL WHERE clause for ontology filtering."""
    conditions = []

    if include_ontos:
        # If include list provided, only include those
        placeholders = ','.join('?' * len(include_ontos))
        conditions.append(f"ontologyId IN ({placeholders})")

    if exclude_ontos:
        # If exclude list provided, exclude those
        placeholders = ','.join('?' * len(exclude_ontos))
        conditions.append(f"ontologyId NOT IN ({placeholders})")

    if conditions:
        return "WHERE " + " AND ".join(conditions)
    return ""


def migrate_filtered(
    db_path: str,
    chroma_path: str,
    collection_name: str,
    include_ontos: tuple[str, ...],
    exclude_ontos: tuple[str, ...],
    batch_size: int = 1000
):
    """Migrate filtered embeddings to ChromaDB."""

    # Validate mutually exclusive options
    if include_ontos and exclude_ontos:
        raise click.UsageError("Cannot use both --include and --exclude. Choose one approach.")

    print(f"Connecting to SQLite database: {db_path}")

    # Initialize ChromaDB
    print(f"Initializing ChromaDB at: {chroma_path}")
    client = chromadb.PersistentClient(
        path=chroma_path,
        settings=Settings(anonymized_telemetry=False)
    )

    # Build collection description
    if include_ontos:
        onto_list = ', '.join(include_ontos)
        description = f"Embeddings from ontologies: {onto_list}"
    elif exclude_ontos:
        onto_list = ', '.join(exclude_ontos)
        description = f"All embeddings except: {onto_list}"
    else:
        description = "All embeddings"

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"description": description}
    )

    existing_count = collection.count()
    print(f"Collection '{collection.name}' ready (current count: {existing_count:,})")

    # Open connection
    conn = sqlite3.connect(db_path, isolation_level=None, timeout=30.0)
    cursor = conn.cursor()

    # Build query
    where_clause = build_where_clause(include_ontos, exclude_ontos)
    params = list(include_ontos) + list(exclude_ontos)

    # Count filtered records
    count_query = f"SELECT COUNT(*) FROM embeddings {where_clause}"
    total = cursor.execute(count_query, params).fetchone()[0]

    if include_ontos:
        print(f"Total embeddings for ontologies {include_ontos}: {total:,}")
    elif exclude_ontos:
        print(f"Total embeddings excluding {exclude_ontos}: {total:,}")
    else:
        print(f"Total embeddings: {total:,}")

    # Main query
    query = f"""
    SELECT ontologyId, entityType, iri, document, embeddings
    FROM embeddings
    {where_clause}
    """

    batch_ids = []
    batch_embeddings = []
    batch_documents = []
    batch_metadatas = []

    processed = 0
    errors = 0
    error_log_path = Path(chroma_path).parent / f"{Path(chroma_path).name}_migration_errors.log"
    error_log = open(error_log_path, "w")

    print(f"\nMigrating embeddings...")

    with tqdm(total=total, desc="Migrating") as pbar:
        try:
            cursor.execute(query, params)

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
        print(f"  See {error_log_path} for details")
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
    default="./filtered_chroma",
    help="Path to ChromaDB storage directory"
)
@click.option(
    '--collection-name',
    type=str,
    default="ols_embeddings",
    help="Name for the ChromaDB collection"
)
@click.option(
    '--include',
    'include_ontos',
    multiple=True,
    help="Include only these ontologies (can be specified multiple times)"
)
@click.option(
    '--exclude',
    'exclude_ontos',
    multiple=True,
    help="Exclude these ontologies (can be specified multiple times)"
)
@click.option(
    '--batch-size',
    type=int,
    default=1000,
    help="Batch size for migration"
)
def main(
    db_path: str,
    chroma_path: str,
    collection_name: str,
    include_ontos: tuple[str, ...],
    exclude_ontos: tuple[str, ...],
    batch_size: int
):
    """
    Migrate filtered subset of embeddings to ChromaDB.

    Use --include to specify ontologies to include (whitelist).
    Use --exclude to specify ontologies to exclude (blacklist).
    Cannot use both --include and --exclude together.

    Examples:

        Migrate only OBA:

            python migrate_filtered.py --include oba --chroma-path ./oba_chroma

        Migrate multiple ontologies:

            python migrate_filtered.py --include oba --include pato --include envo

        Migrate everything except large ontologies:

            python migrate_filtered.py --exclude ncbitaxon --exclude slm --exclude dron
    """
    migrate_filtered(
        db_path=db_path,
        chroma_path=chroma_path,
        collection_name=collection_name,
        include_ontos=include_ontos,
        exclude_ontos=exclude_ontos,
        batch_size=batch_size
    )


if __name__ == "__main__":
    main()
