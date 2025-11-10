#!/usr/bin/env python
"""
Generate SSSOM mappings by querying ChromaDB with semantic embeddings.

For each input term, generates an embedding from its label (optionally with parent labels),
then queries a ChromaDB collection for the top matches from ontologies with OLS-style embeddings.
Results are written in SSSOM TSV format with confidence scores and similarity measures.

INPUT FORMAT:
Currently hardcoded to work with ROBOT template TSV format:
  - Column 0: CURIE (e.g., METPO:1000001)
  - Column 1: Label (e.g., "thermophilic")
  - Column 3: Parent classes (pipe-separated, optional)
  - First 2 rows are skipped (ROBOT template headers)

The CURIE prefix (currently "METPO") is hardcoded in the SSSOM output metadata.
For use with other ontologies, the prefix mappings and subject_source would need
to be parameterized.

OUTPUT FORMAT:
SSSOM TSV with:
  - Metadata block (YAML in comments)
  - Tab-separated mappings with required SSSOM fields
  - Distance-based predicate selection (exactMatch, closeMatch, relatedMatch)
    Note: broadMatch/narrowMatch are not used since embeddings only measure semantic
    similarity, not hierarchical relationships.
  - Confidence scores derived from cosine distance: confidence = 1.0 - (distance / 2.0)
"""

import csv
import os
from pathlib import Path
from typing import List, Dict
from datetime import date

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


def create_query_text(label: str, parents: List[str], label_only: bool = False) -> str:
    """Create query text from label and parent labels."""
    if label_only or not parents:
        return label
    return f"{label} {' '.join(parents)}"


def distance_to_predicate(distance: float) -> str:
    """
    Map distance to SKOS mapping predicate based on semantic similarity.

    Note: We use only similarity-based predicates (exactMatch, closeMatch, relatedMatch)
    since embedding distance cannot determine hierarchical relationships (broadMatch/narrowMatch).

    Thresholds:
    - exactMatch: < 0.10 (essentially identical semantically)
    - closeMatch: < 0.35 (high confidence, validated ~71% precision)
    - relatedMatch: >= 0.35 (moderate semantic similarity)
    """
    if distance < 0.10:
        return "skos:exactMatch"
    elif distance < 0.35:
        return "skos:closeMatch"
    else:
        return "skos:relatedMatch"


def distance_to_confidence(distance: float) -> float:
    """Convert cosine distance to confidence score (0.0-1.0)."""
    return max(0.0, 1.0 - (distance / 2.0))


def write_sssom_output(matches: List[Dict], output_path: str, distance_cutoff: float):
    """Write matches in SSSOM TSV format."""
    # Filter by distance cutoff
    filtered = [m for m in matches if m['distance'] < distance_cutoff]

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        # Write metadata block
        f.write("# curie_map:\n")
        f.write("#   METPO: http://purl.obolibrary.org/obo/METPO_\n")
        f.write("#   skos: http://www.w3.org/2004/02/skos/core#\n")
        f.write("#   semapv: https://w3id.org/semapv/vocab/\n")
        f.write(f"# mapping_set_id: metpo-ontology-mappings-{date.today().isoformat()}\n")
        f.write(f"# mapping_date: {date.today().isoformat()}\n")
        f.write("# mapping_tool: openai_text-embedding-3-small\n")
        f.write("# mapping_provider: https://github.com/berkeleybop/metpo\n")
        f.write("# license: https://creativecommons.org/publicdomain/zero/1.0/\n")
        f.write(f"# comment: Semantic mappings generated using OpenAI text-embedding-3-small with distance cutoff {distance_cutoff}\n")
        f.write("#\n")

        # Write TSV header and data
        writer = csv.writer(f, delimiter='\t')
        writer.writerow([
            'subject_id',
            'subject_label',
            'predicate_id',
            'object_id',
            'object_label',
            'mapping_justification',
            'confidence',
            'similarity_score',
            'similarity_measure',
            'mapping_tool',
            'subject_source',
            'object_source',
            'comment'
        ])

        for m in filtered:
            writer.writerow([
                m['metpo_id'],
                m['metpo_label'],
                distance_to_predicate(m['distance']),
                m['match_iri'],
                m['match_document'],
                'semapv:SemanticSimilarityThresholdMatching',
                f"{distance_to_confidence(m['distance']):.6f}",
                f"{1.0 - m['distance']:.6f}",
                'cosine_similarity',
                'openai_text-embedding-3-small',
                'METPO',
                m['match_ontology'],
                f"Embedding cosine distance: {m['distance']:.4f}, Rank: {m['rank']}"
            ])

    return len(filtered)


def query_chromadb_for_term(
    term: Dict[str, str],
    collection,
    openai_api_key: str,
    top_n: int = 5,
    label_only: bool = False
) -> List[Dict[str, any]]:
    """Generate embedding for a METPO term and query ChromaDB."""

    # Create query text
    query_text = create_query_text(term['label'], term['parents'], label_only)

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
    default='../data/mappings/metpo_mappings.sssom.tsv',
    help="Output SSSOM TSV file path"
)
@click.option(
    '--top-n',
    type=int,
    default=5,
    help="Number of top matches to retrieve per term"
)
@click.option(
    '--limit',
    type=int,
    default=None,
    help="Limit number of METPO terms to process (for testing)"
)
@click.option(
    '--label-only',
    is_flag=True,
    default=False,
    help="Use only label for embedding (exclude parent labels)"
)
@click.option(
    '--distance-cutoff',
    type=float,
    default=0.35,
    help="Maximum distance to include in SSSOM output (default: 0.35)"
)
def main(metpo_tsv: str, chroma_path: str, collection_name: str, output: str, top_n: int, limit: int, label_only: bool, distance_cutoff: float):
    """Query METPO terms against ChromaDB embeddings and generate SSSOM TSV mappings."""

    # Load environment variables (override shell env vars)
    load_dotenv(dotenv_path='../.env', override=True)
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file or environment variables.")

    print(f"Loading METPO terms from: {metpo_tsv}")
    terms = load_metpo_terms(metpo_tsv)
    if limit:
        terms = terms[:limit]
        print(f"Loaded {len(terms)} METPO terms (limited to first {limit})")
    else:
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
            matches = query_chromadb_for_term(term, collection, openai.api_key, top_n, label_only)
            all_matches.extend(matches)
        except Exception as e:
            errors += 1
            tqdm.write(f"\n⚠ Error processing {term['id']} ({term['label']}): {e}")
            continue

        # Progress checkpoint every 50 terms
        if i % 50 == 0:
            tqdm.write(f"  [{i}/{len(terms)}] Processed, {len(all_matches)} matches so far, {errors} errors")

    # Write results in SSSOM TSV format
    print(f"\nWriting results to: {output}")

    if not all_matches:
        print("⚠ Warning: No matches to write!")
        return

    written = write_sssom_output(all_matches, output, distance_cutoff)

    # Count by predicate for summary
    filtered = [m for m in all_matches if m['distance'] < distance_cutoff]
    by_predicate = {}
    for m in filtered:
        pred = distance_to_predicate(m['distance'])
        by_predicate[pred] = by_predicate.get(pred, 0) + 1

    print(f"\n✓ Complete!")
    print(f"  METPO terms processed: {len(terms)}")
    print(f"  Successful queries: {len(terms) - errors}")
    print(f"  Errors: {errors}")
    print(f"  Total matches retrieved: {len(all_matches)}")
    print(f"  Matches written (distance < {distance_cutoff}): {written}")
    print(f"\n  Mappings by predicate:")
    for pred, count in sorted(by_predicate.items()):
        print(f"    {pred}: {count}")
    print(f"\n  Output file: {output}")


if __name__ == "__main__":
    main()
