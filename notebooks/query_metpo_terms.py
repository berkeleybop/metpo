#!/usr/bin/env python
"""
Query METPO terms against ChromaDB embeddings.

For each METPO term, generates an embedding from its label + parent labels,
then queries ChromaDB for the top matches from OLS ontologies.
"""

import csv
import os
from pathlib import Path
from typing import List, Dict

import chromadb
import openai
from chromadb.config import Settings
from dotenv import load_dotenv
from tqdm import tqdm
import click


def load_metpo_terms(tsv_path: str) -> List[Dict[str, str]]:
    """Load METPO terms from the template TSV file."""
    terms = []

    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')

        # Skip first 2 header rows
        next(reader)
        next(reader)

        for row in reader:
            if len(row) < 4:
                continue

            metpo_id = row[0].strip()
            label = row[1].strip()
            parent_classes = row[3].strip() if len(row) > 3 else ""

            if not metpo_id or not label:
                continue

            # Parse parent classes (pipe-separated)
            parents = [p.strip() for p in parent_classes.split('|') if p.strip()]

            terms.append({
                'id': metpo_id,
                'label': label,
                'parents': parents,
                'parent_str': parent_classes
            })

    return terms


def create_query_text(label: str, parents: List[str]) -> str:
    """Create query text from label and parent labels."""
    if parents:
        return f"{label} {' '.join(parents)}"
    return label


def query_chromadb_for_term(
    term: Dict[str, str],
    collection,
    openai_api_key: str,
    top_n: int = 5
) -> List[Dict[str, any]]:
    """Generate embedding for a METPO term and query ChromaDB."""

    # Create query text
    query_text = create_query_text(term['label'], term['parents'])

    # Generate embedding
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=query_text
    )
    query_embedding = response.data[0].embedding

    # Query ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_n,
        include=["documents", "metadatas", "distances"]
    )

    # Format results
    matches = []
    for i in range(len(results['ids'][0])):
        matches.append({
            'metpo_id': term['id'],
            'metpo_label': term['label'],
            'metpo_parents': term['parent_str'],
            'query_text': query_text,
            'match_id': results['ids'][0][i],
            'match_document': results['documents'][0][i],
            'match_ontology': results['metadatas'][0][i].get('ontologyId', 'unknown'),
            'match_iri': results['metadatas'][0][i].get('iri', 'unknown'),
            'distance': results['distances'][0][i],
            'rank': i + 1
        })

    return matches


@click.command()
@click.option(
    '--metpo-tsv',
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    default='../src/templates/metpo_sheet.tsv',
    help="Path to METPO template TSV file"
)
@click.option(
    '--chroma-path',
    type=click.Path(path_type=str),
    default='./embeddings_chroma',
    help="Path to ChromaDB storage directory"
)
@click.option(
    '--collection-name',
    type=str,
    default='ols_embeddings',
    help="Name of the ChromaDB collection to query"
)
@click.option(
    '--output',
    type=click.Path(path_type=str),
    default='./metpo_chromadb_matches.csv',
    help="Output CSV file path"
)
@click.option(
    '--top-n',
    type=int,
    default=5,
    help="Number of top matches to retrieve per term"
)
def main(metpo_tsv: str, chroma_path: str, collection_name: str, output: str, top_n: int):
    """Query METPO terms against ChromaDB embeddings."""

    # Load environment variables
    load_dotenv(dotenv_path='../.env')
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file or environment variables.")

    print(f"Loading METPO terms from: {metpo_tsv}")
    terms = load_metpo_terms(metpo_tsv)
    print(f"Loaded {len(terms)} METPO terms")

    # Connect to ChromaDB
    print(f"\nConnecting to ChromaDB at: {chroma_path}")
    client = chromadb.PersistentClient(
        path=chroma_path,
        settings=Settings(anonymized_telemetry=False)
    )
    print("✓ ChromaDB client initialized")

    print(f"Loading collection '{collection_name}'...")
    collection = client.get_collection(name=collection_name)
    print("✓ Collection loaded")

    # Try to get count, but don't fail if index is corrupted
    try:
        count = collection.count()
        print(f"✓ Collection size: {count:,} embeddings")
    except Exception as e:
        print(f"⚠ Warning: Could not get collection count ({e})")
        print("  Continuing anyway - queries should still work...")

    # Query each term
    print(f"\nQuerying ChromaDB for top {top_n} matches per term...")
    print(f"This will make {len(terms)} OpenAI API calls (~{len(terms) * 0.5:.0f} seconds)")
    all_matches = []
    errors = 0

    for i, term in enumerate(tqdm(terms, desc="Processing METPO terms"), 1):
        try:
            matches = query_chromadb_for_term(term, collection, openai.api_key, top_n)
            all_matches.extend(matches)
        except Exception as e:
            errors += 1
            tqdm.write(f"\n⚠ Error processing {term['id']} ({term['label']}): {e}")
            continue

        # Progress checkpoint every 50 terms
        if i % 50 == 0:
            tqdm.write(f"  [{i}/{len(terms)}] Processed, {len(all_matches)} matches so far, {errors} errors")

    # Write results to CSV
    print(f"\nWriting results to: {output}")
    with open(output, 'w', newline='', encoding='utf-8') as f:
        if all_matches:
            writer = csv.DictWriter(f, fieldnames=all_matches[0].keys())
            writer.writeheader()
            writer.writerows(all_matches)
        else:
            print("⚠ Warning: No matches to write!")

    print(f"\n✓ Complete!")
    print(f"  METPO terms processed: {len(terms)}")
    print(f"  Successful queries: {len(terms) - errors}")
    print(f"  Errors: {errors}")
    print(f"  Total matches written: {len(all_matches)}")
    print(f"  Output file: {output}")


if __name__ == "__main__":
    main()
