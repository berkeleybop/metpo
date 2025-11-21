#!/usr/bin/env python3
"""Query ChromaDB for semantic matches to a search phrase."""
import os
import chromadb
import click
import openai
from chromadb.config import Settings
from dotenv import load_dotenv


@click.command()
@click.option('--phrase', '-p', required=True, help='Search phrase to query')
@click.option('--chroma-path', default='data/chromadb/chroma_ols20_nonols4',
              help='Path to ChromaDB directory')
@click.option('--collection', default='combined_embeddings',
              help='ChromaDB collection name')
@click.option('--top-n', default=10, type=int,
              help='Number of results to return')
@click.option('--ontology', '-o', multiple=True,
              help='Filter to specific ontology (can specify multiple times)')
def main(phrase: str, chroma_path: str, collection: str, top_n: int, ontology: tuple):
    """Query ChromaDB for semantic matches to a search phrase."""

    # Load environment
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")

    # Connect to ChromaDB
    client = chromadb.PersistentClient(
        path=chroma_path,
        settings=Settings(anonymized_telemetry=False)
    )

    coll = client.get_collection(name=collection)
    print(f"✓ Collection '{collection}' loaded")

    # Try to get count, but don't wait if it's slow
    try:
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Count operation timed out")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(2)  # 2 second timeout
        try:
            count = coll.count()
            print(f"  Collection size: {count:,} embeddings")
        finally:
            signal.alarm(0)  # Cancel alarm
    except (TimeoutError, Exception):
        print("  Collection size: [skipped - counting takes too long]")

    # Generate embedding
    print(f"\nSearching for: '{phrase}'")
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=phrase
    )
    query_embedding = response.data[0].embedding

    # Build query kwargs
    query_kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": top_n,
        "include": ["documents", "metadatas", "distances"]
    }

    # Add ontology filter if specified
    if ontology:
        query_kwargs["where"] = {"ontologyId": {"$in": list(ontology)}}
        print(f"Filtering to ontologies: {', '.join(ontology)}")

    # Query
    results = coll.query(**query_kwargs)

    # Display results
    print(f"\nTop {len(results['ids'][0])} matches:\n")
    for i in range(len(results["ids"][0])):
        doc = results["documents"][0][i]
        ont = results["metadatas"][0][i].get("ontologyId", "unknown")
        iri = results["metadatas"][0][i].get("iri", "unknown")
        distance = results["distances"][0][i]
        similarity = 1.0 - (distance / 2.0)

        print(f"{i+1}. [{ont}] {doc}")
        print(f"   IRI: {iri}")
        print(f"   Similarity: {similarity:.4f}\n")


if __name__ == '__main__':
    main()
