#!/usr/bin/env python
"""
Filter OLS ChromaDB to remove low-ROI ontologies.

Creates chroma_ols_20 from chroma_ols_27 by removing 7 low-value ontologies.
"""

import chromadb
from chromadb.config import Settings
import click


# OLS ontologies to REMOVE (7 total)
OLS_TO_REMOVE = {
    "chebi", "foodon", "cl", "fypo", "ecto", "aro", "ddpheno"
}


@click.command()
@click.option("--input-path", default="./chroma_ols_27", help="Path to input ChromaDB")
@click.option("--input-collection", default="ols_embeddings", help="Input collection name")
@click.option("--output-path", default="./chroma_ols_20", help="Path to output ChromaDB")
@click.option("--output-collection", default="ols_embeddings", help="Output collection name")
@click.option("--batch-size", default=10000, help="Batch size for processing")
def main(input_path, input_collection, output_path, output_collection, batch_size):
    """Filter OLS ChromaDB to remove low-ROI ontologies."""

    print(f"Creating filtered OLS ChromaDB")
    print(f"Input:  {input_path}/{input_collection}")
    print(f"Output: {output_path}/{output_collection}")
    print(f"\nRemoving {len(OLS_TO_REMOVE)} ontologies:")
    for ont in sorted(OLS_TO_REMOVE):
        print(f"  - {ont}")

    # Connect to input
    print(f"\nConnecting to input ChromaDB...")
    input_client = chromadb.PersistentClient(
        path=input_path,
        settings=Settings(anonymized_telemetry=False)
    )

    input_coll = input_client.get_collection(name=input_collection)
    total_input = input_coll.count()
    print(f"✓ Input collection: {total_input:,} embeddings")

    # Connect to output
    print(f"\nConnecting to output ChromaDB...")
    output_client = chromadb.PersistentClient(
        path=output_path,
        settings=Settings(anonymized_telemetry=False)
    )

    # Create output collection (delete if exists)
    try:
        output_client.delete_collection(name=output_collection)
        print(f"  Deleted existing collection: {output_collection}")
    except:
        pass

    output_coll = output_client.create_collection(
        name=output_collection,
        metadata={"description": "OLS embeddings - 20 high-ROI ontologies"}
    )
    print(f"✓ Output collection created: {output_collection}")

    # Process in batches
    print(f"\nProcessing embeddings in batches of {batch_size:,}...")

    offset = 0
    total_copied = 0
    total_skipped = 0
    ontology_counts = {}

    while offset < total_input:
        # Get batch
        batch = input_coll.get(
            limit=batch_size,
            offset=offset,
            include=["documents", "metadatas", "embeddings"]
        )

        if not batch["ids"]:
            break

        # Filter to keep only desired ontologies
        filtered_ids = []
        filtered_embeddings = []
        filtered_metadatas = []
        filtered_documents = []

        for i, metadata in enumerate(batch["metadatas"]):
            ont_id = metadata.get("ontologyId", "unknown")

            if ont_id not in OLS_TO_REMOVE:
                filtered_ids.append(batch["ids"][i])
                filtered_embeddings.append(batch["embeddings"][i])
                filtered_metadatas.append(metadata)
                filtered_documents.append(batch["documents"][i])

                # Track counts
                ontology_counts[ont_id] = ontology_counts.get(ont_id, 0) + 1
                total_copied += 1
            else:
                total_skipped += 1

        # Add filtered batch to output in smaller chunks (ChromaDB has max batch size)
        if filtered_ids:
            max_add_size = 5000
            for i in range(0, len(filtered_ids), max_add_size):
                end = min(i + max_add_size, len(filtered_ids))
                output_coll.add(
                    ids=filtered_ids[i:end],
                    embeddings=filtered_embeddings[i:end],
                    metadatas=filtered_metadatas[i:end],
                    documents=filtered_documents[i:end]
                )

        offset += len(batch["ids"])

        if offset % 50000 == 0 or offset >= total_input:
            print(f"  [{offset:,}/{total_input:,}] Copied: {total_copied:,}, Skipped: {total_skipped:,}")

    # Summary
    print(f"\n{'=' * 80}")
    print(f"FILTERING COMPLETE")
    print(f"{'=' * 80}")
    print(f"\nInput:   {total_input:,} embeddings (27 ontologies)")
    print(f"Copied:  {total_copied:,} embeddings ({100*total_copied/total_input:.1f}%)")
    print(f"Removed: {total_skipped:,} embeddings ({100*total_skipped/total_input:.1f}%)")

    print(f"\nOntology distribution in filtered database:")
    print(f"{'Ontology':<20} {'Count':<12}")
    print("-" * 35)
    for ont, count in sorted(ontology_counts.items(), key=lambda x: -x[1]):
        print(f"{ont:<20} {count:<12,}")

    print(f"\nTotal unique ontologies: {len(ontology_counts)}")

    # Verify
    final_count = output_coll.count()
    print(f"\n✓ Verification: Output collection has {final_count:,} embeddings")

    if final_count != total_copied:
        print(f"⚠️  WARNING: Count mismatch! Expected {total_copied:,}, got {final_count:,}")
    else:
        print(f"✓ Count verified!")

    print(f"\nFiltered OLS ChromaDB created at: {output_path}")


if __name__ == "__main__":
    main()
