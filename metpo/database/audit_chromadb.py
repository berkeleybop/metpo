"""Audit ChromaDB collections for ontology distribution and vector dimensions."""

from collections import Counter

import chromadb
import click
from chromadb.config import Settings


def audit_collection(chroma_path: str, collection_name: str):
    """Audit a ChromaDB collection."""

    print(f"\n{'=' * 80}")
    print(f"Auditing: {chroma_path} / {collection_name}")
    print(f"{'=' * 80}")

    try:
        client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(anonymized_telemetry=False)
        )

        collection = client.get_collection(name=collection_name)
        total = collection.count()

        print(f"\nTotal embeddings: {total:,}")

        if total == 0:
            print("⚠️  Empty collection!")
            return None

        # Scan all embeddings to get ontology distribution and vector dimensions
        print("Scanning all embeddings...")

        batch_size = 10000
        all_ontologies = []
        vector_dims = set()

        for offset in range(0, total, batch_size):
            results = collection.get(
                limit=min(batch_size, total - offset),
                offset=offset,
                include=["metadatas", "embeddings"]
            )

            for metadata in results["metadatas"]:
                if "ontologyId" in metadata:
                    all_ontologies.append(metadata["ontologyId"])

            # Check vector dimensions
            for embedding in results["embeddings"]:
                if embedding is not None and len(embedding) > 0:
                    vector_dims.add(len(embedding))

        # Vector dimension check
        print("\n--- Vector Dimensions ---")
        if len(vector_dims) == 1:
            print(f"✓ All vectors same dimension: {next(iter(vector_dims))}")
        else:
            print("⚠️  WARNING: Multiple vector dimensions found!")
            for dim in sorted(vector_dims):
                print(f"   Dimension {dim}")

        # Ontology distribution
        ont_counts = Counter(all_ontologies)

        print(f"\n--- Ontology Distribution ({len(all_ontologies):,} embeddings) ---")
        print(f"{'Ontology':<20} {'Count':<12} {'% of Total':<12}")
        print("-" * 70)

        for ont, count in sorted(ont_counts.items(), key=lambda x: x[1], reverse=True):
            pct = 100 * count / len(all_ontologies)
            print(f"{ont:<20} {count:<12,} {pct:>6.2f}%")

        print(f"\nTotal unique ontologies: {len(ont_counts)}")

        # Low-count ontologies
        low_count = [(ont, count) for ont, count in ont_counts.items() if count < 100]
        if low_count:
            print("\nOntologies with < 100 embeddings:")
            for ont, count in sorted(low_count, key=lambda x: x[1]):
                pct = 100 * count / len(all_ontologies)
                print(f"  {ont:<20} {count:>5,} ({pct:>5.2f}%)")

        return {
            "total": total,
            "ontologies": set(ont_counts.keys()),
            "vector_dims": vector_dims,
            "ont_counts": ont_counts,
            "sampled": len(all_ontologies)
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


@click.command()
def main():
    """Audit all ChromaDB collections."""

    collections = [
        ("./chroma_ols_27", "ols_embeddings"),
        ("../embeddings_chroma", "non_ols_embeddings"),
        ("./chroma_combined", "combined_embeddings"),
    ]

    results = {}

    for path, name in collections:
        label = f"{path}/{name}"
        results[label] = audit_collection(path, name)

    # Comparison analysis
    print(f"\n\n{'=' * 80}")
    print("CROSS-DATABASE COMPARISON")
    print(f"{'=' * 80}")

    ols_result = results.get("./chroma_ols_27/ols_embeddings")
    non_ols_result = results.get("../embeddings_chroma/non_ols_embeddings")
    combined_result = results.get("./chroma_combined/combined_embeddings")

    if ols_result and non_ols_result and combined_result:
        print("\nTotal Counts:")
        print(f"  OLS:       {ols_result['total']:>10,}")
        print(f"  Non-OLS:   {non_ols_result['total']:>10,}")
        print(f"  Combined:  {combined_result['total']:>10,}")
        print(f"  Expected:  {ols_result['total'] + non_ols_result['total']:>10,}")

        if combined_result["total"] == ols_result["total"] + non_ols_result["total"]:
            print("  ✓ Combined count matches OLS + Non-OLS")
        else:
            diff = combined_result["total"] - (ols_result["total"] + non_ols_result["total"])
            print(f"  ⚠️  Combined count off by {diff:,}")

        print("\nVector Dimensions:")
        all_dims = ols_result["vector_dims"] | non_ols_result["vector_dims"] | combined_result["vector_dims"]
        if len(all_dims) == 1:
            print(f"  ✓ All databases use same dimension: {next(iter(all_dims))}")
        else:
            print("  ⚠️  Inconsistent dimensions across databases:")
            print(f"     OLS: {ols_result['vector_dims']}")
            print(f"     Non-OLS: {non_ols_result['vector_dims']}")
            print(f"     Combined: {combined_result['vector_dims']}")

        print("\nOntology Coverage:")
        print(f"  OLS ontologies: {len(ols_result['ontologies'])}")
        print(f"  Non-OLS ontologies: {len(non_ols_result['ontologies'])}")
        print(f"  Combined ontologies: {len(combined_result['ontologies'])}")
        print(f"  Expected: {len(ols_result['ontologies'] | non_ols_result['ontologies'])}")

        # Check for missing ontologies
        expected_ontologies = ols_result["ontologies"] | non_ols_result["ontologies"]
        missing = expected_ontologies - combined_result["ontologies"]
        if missing:
            print("\n  ⚠️  Ontologies missing from combined:")
            for ont in sorted(missing):
                print(f"     - {ont}")
        else:
            print("  ✓ All ontologies present in combined")

        # Check for unexpected ontologies in combined
        unexpected = combined_result["ontologies"] - expected_ontologies
        if unexpected:
            print("\n  ⚠️  Unexpected ontologies in combined:")
            for ont in sorted(unexpected):
                print(f"     - {ont}")

        # List OLS-only and Non-OLS-only
        print(f"\nOLS-only ontologies ({len(ols_result['ontologies'] - non_ols_result['ontologies'])}):")
        for ont in sorted(ols_result["ontologies"] - non_ols_result["ontologies"]):
            count = ols_result["ont_counts"].get(ont, 0)
            print(f"  - {ont:<20} {count:,}")

        print(f"\nNon-OLS-only ontologies ({len(non_ols_result['ontologies'] - ols_result['ontologies'])}):")
        for ont in sorted(non_ols_result["ontologies"] - ols_result["ontologies"]):
            count = non_ols_result["ont_counts"].get(ont, 0)
            print(f"  - {ont:<20} {count:,}")

    print(f"\n{'=' * 80}")


if __name__ == "__main__":
    main()
