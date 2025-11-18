#!/usr/bin/env python
"""Combine OLS and non-OLS ChromaDB databases into a single unified database."""

import os
import click
import chromadb
from chromadb.config import Settings
from tqdm import tqdm


@click.command()
@click.option(
    "--ols-path",
    type=click.Path(exists=True),
    default="notebooks/chroma_ols_27",
    help="Path to OLS ChromaDB"
)
@click.option(
    "--non-ols-path",
    type=click.Path(exists=True),
    default="embeddings_chroma",
    help="Path to non-OLS ChromaDB"
)
@click.option(
    "--output-path",
    type=click.Path(),
    default="notebooks/chroma_combined",
    help="Path for combined ChromaDB output"
)
@click.option(
    "--output-collection",
    type=str,
    default="combined_embeddings",
    help="Name of combined collection"
)
@click.option(
    "--batch-size",
    type=int,
    default=1000,
    help="Batch size for copying embeddings"
)
def main(ols_path, non_ols_path, output_path, output_collection, batch_size):
    """
    Combine OLS and non-OLS ChromaDB databases into a unified database.

    This creates a new ChromaDB at the output path containing all embeddings
    from both source databases.
    """
    print("=" * 80)
    print("COMBINING CHROMADB DATABASES")
    print("=" * 80)

    # Check if output already exists
    if os.path.exists(output_path):
        click.confirm(
            f"\nWarning: Output path '{output_path}' already exists. Overwrite?",
            abort=True
        )
        import shutil
        shutil.rmtree(output_path)

    # Connect to source databases
    print(f"\n1. Connecting to source databases...")

    ols_client = chromadb.PersistentClient(
        path=ols_path,
        settings=Settings(anonymized_telemetry=False)
    )
    ols_collection = ols_client.get_collection(name="ols_embeddings")
    ols_count = ols_collection.count()
    print(f"   OLS database: {ols_count:,} embeddings")

    non_ols_client = chromadb.PersistentClient(
        path=non_ols_path,
        settings=Settings(anonymized_telemetry=False)
    )
    non_ols_collection = non_ols_client.get_collection(name="non_ols_embeddings")
    non_ols_count = non_ols_collection.count()
    print(f"   Non-OLS database: {non_ols_count:,} embeddings")

    total_count = ols_count + non_ols_count
    print(f"   Total to combine: {total_count:,} embeddings")

    # Create output database
    print(f"\n2. Creating combined database at: {output_path}")
    output_client = chromadb.PersistentClient(
        path=output_path,
        settings=Settings(anonymized_telemetry=False)
    )

    output_collection = output_client.get_or_create_collection(
        name=output_collection,
        metadata={"description": "Combined OLS and non-OLS ontology embeddings"}
    )

    # Copy OLS embeddings
    print(f"\n3. Copying OLS embeddings ({ols_count:,} terms)...")
    copy_collection(ols_collection, output_collection, batch_size)

    # Copy non-OLS embeddings
    print(f"\n4. Copying non-OLS embeddings ({non_ols_count:,} terms)...")
    copy_collection(non_ols_collection, output_collection, batch_size)

    # Verify
    final_count = output_collection.count()
    print(f"\n5. Verification:")
    print(f"   Expected: {total_count:,}")
    print(f"   Actual:   {final_count:,}")

    if final_count == total_count:
        print("   ✓ Count matches!")
    else:
        print(f"   ⚠ Count mismatch! Difference: {abs(final_count - total_count)}")

    print("\n" + "=" * 80)
    print("✓ COMBINATION COMPLETE")
    print("=" * 80)
    print(f"\nCombined database location: {output_path}")
    print(f"Collection name: {output_collection.name}")
    print(f"Total embeddings: {final_count:,}")


def copy_collection(source_collection, dest_collection, batch_size):
    """Copy all embeddings from source to destination collection in batches.

    Uses chunked processing to avoid loading entire collection into memory.
    """
    total = source_collection.count()
    print(f"   Processing {total:,} embeddings in chunks of {batch_size}...")

    copied = 0
    offset = 0

    with tqdm(total=total, desc="   Copying") as pbar:
        while offset < total:
            # Fetch a chunk
            chunk_data = source_collection.get(
                limit=batch_size,
                offset=offset,
                include=["embeddings", "documents", "metadatas"]
            )

            # Check if we got data
            if not chunk_data["ids"]:
                break

            # Add to destination
            dest_collection.add(
                ids=chunk_data["ids"],
                embeddings=chunk_data["embeddings"],
                documents=chunk_data["documents"],
                metadatas=chunk_data["metadatas"]
            )

            chunk_size = len(chunk_data["ids"])
            copied += chunk_size
            offset += chunk_size
            pbar.update(chunk_size)

    print(f"   ✓ Copied {copied:,} embeddings")


if __name__ == "__main__":
    main()
