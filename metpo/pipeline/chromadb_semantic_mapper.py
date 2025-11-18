"""
Generate SSSOM mappings by querying ChromaDB with semantic embeddings.

For each input term, generates an embedding from its label and definition,
then queries a ChromaDB collection for the top matches from ontologies with OLS-style embeddings.
Results are written in SSSOM TSV format with confidence scores and similarity measures.

INPUT FORMAT:
Flexible TSV format with configurable column mapping via CLI options:
  - Default (ROBOT template): skip_rows=2, columns: ID, label, parent class, description
  - Standard TSV: skip_rows=1, customize column names via --id-column, --label-column, etc.
  - Examples:
    * ROBOT template: --skip-rows 2 --id-column ID --definition-column description
    * Curator definitions: --skip-rows 1 --id-column metpo_id --definition-column proposed_definition

Column options:
  --skip-rows: Number of header rows to skip (default: 2 for ROBOT template)
  --id-column: Column name for term CURIE (default: 'ID')
  --label-column: Column name for term label (default: 'label')
  --definition-column: Column name for definition (default: 'description')
  --parent-column: Column name for parent classes (default: 'parent class')

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
from datetime import UTC, datetime
from pathlib import Path

import chromadb
import click
import openai
from chromadb.config import Settings
from dotenv import load_dotenv
from tqdm import tqdm


def load_metpo_terms(
    tsv_path: str,
    skip_rows: int = 2,
    id_column: str = "ID",
    label_column: str = "label",
    definition_column: str = "description",
    parent_column: str = "parent class"
) -> list[dict[str, str]]:
    """
    Load terms from TSV file with flexible column mapping.

    Args:
        tsv_path: Path to input TSV file
        skip_rows: Number of header rows to skip (ROBOT template=2, standard TSV=1)
        id_column: Column name for term CURIE/ID
        label_column: Column name for term label
        definition_column: Column name for definition text
        parent_column: Column name for parent classes (optional)

    Returns:
        List of term dictionaries with keys: id, label, parents, parent_str, definition
    """
    terms = []

    with Path(tsv_path).open( encoding="utf-8") as f:
        lines = f.readlines()

        # Read header from first non-skipped row
        header_line = lines[skip_rows - 1] if skip_rows > 0 else lines[0]
        reader = csv.DictReader(
            lines[skip_rows:],
            delimiter="\t",
            fieldnames=header_line.strip().split("\t")
        )

        for row in reader:
            # Get values using column names, with fallback to empty string
            metpo_id = row.get(id_column, "").strip()
            label = row.get(label_column, "").strip()
            parent_classes = row.get(parent_column, "").strip()
            definition = row.get(definition_column, "").strip()

            if not metpo_id or not label:
                continue

            # Parse parent classes (pipe-separated)
            parents = [p.strip() for p in parent_classes.split("|") if p.strip()] if parent_classes else []

            terms.append({
                "id": metpo_id,
                "label": label,
                "parents": parents,
                "parent_str": parent_classes,
                "definition": definition
            })

    return terms


def create_query_text(label: str, definition: str = "", parents: list[str] | None = None, label_only: bool = False) -> str:
    """
    Create query text from label, definition, and/or parent labels.

    Default: Use "label; definition" format (matches ChromaDB embedding format).
    If no definition: Use "label parent1 parent2..." format.
    If label_only=True: Use only label.
    """
    if label_only:
        return label

    # Default: use definition if available (matches ChromaDB format "label; definition")
    if definition:
        return f"{label}; {definition}"

    # Fallback: use parents if no definition
    if parents:
        return f"{label} {' '.join(parents)}"

    # Last resort: just label
    return label


def similarity_to_predicate(similarity: float) -> str:
    """
    Map similarity score to SKOS mapping predicate.

    Note: We use only similarity-based predicates (exactMatch, closeMatch, relatedMatch, mappingRelation)
    since embedding similarity cannot determine hierarchical relationships (broadMatch/narrowMatch).

    IMPORTANT: Manual review recommended!
    Embedding-based similarity is agnostic to ontological categories. High similarity may occur
    between semantically related but ontologically incompatible terms (e.g., "thermophile"
    [material entity] vs "thermophilic" [quality]). Review mappings for ontological compatibility
    before accepting exactMatch or closeMatch predicates.

    Thresholds based on data analysis of 5,080 mappings (254 METPO terms, ranks 1-20):
    - Input: src/templates/metpo_sheet_improved.tsv (METPO terms with definitions)
    - Reference database: data/chromadb/chroma_ols20_nonols4 (452,942 embeddings from OLS ontologies + custom ontologies)
    - Embedding model: OpenAI text-embedding-3-small (1536 dimensions, L2-normalized)
    - Query format: "label; definition" (or "label parent_labels" if no definition)

    Predicate thresholds:
    - exactMatch: >= 0.90 (rounded from 95th percentile: 0.886)
    - closeMatch: >= 0.85 (rounded from 75th percentile: 0.845)
    - relatedMatch: >= 0.80 (rounded from 25th percentile: 0.783)
    - mappingRelation: < 0.80 (below 25th percentile, weakest matches)
    """
    if similarity >= 0.90:
        return "skos:exactMatch"
    if similarity >= 0.85:
        return "skos:closeMatch"
    if similarity >= 0.80:
        return "skos:relatedMatch"
    return "skos:mappingRelation"


def write_sssom_output(matches: list[dict], output_path: str, min_similarity: float, always_include_best: bool = True):
    """Write matches in SSSOM TSV format."""
    # Filter by minimum similarity, optionally keeping rank=1 (best match) for each term
    # similarity = 1 - (distance / 2), so distance = 2 * (1 - similarity)
    max_distance = 2.0 * (1.0 - min_similarity)

    if always_include_best:
        filtered = [m for m in matches if m["rank"] == 1 or m["distance"] <= max_distance]
    else:
        filtered = [m for m in matches if m["distance"] <= max_distance]

    with Path(output_path).open( "w", encoding="utf-8", newline="") as f:
        # Write metadata block
        f.write("# curie_map:\n")
        f.write("#   METPO: http://purl.obolibrary.org/obo/METPO_\n")
        f.write("#   skos: http://www.w3.org/2004/02/skos/core#\n")
        f.write("#   semapv: https://w3id.org/semapv/vocab/\n")
        f.write(f"# mapping_set_id: metpo-ontology-mappings-{datetime.now(UTC).date().isoformat()}\n")
        f.write(f"# mapping_date: {datetime.now(UTC).date().isoformat()}\n")
        f.write("# mapping_tool: openai_text-embedding-3-small\n")
        f.write("# mapping_provider: https://github.com/berkeleybop/metpo\n")
        f.write("# license: https://creativecommons.org/publicdomain/zero/1.0/\n")
        f.write(f"# comment: Semantic mappings generated using OpenAI text-embedding-3-small with minimum similarity {min_similarity}.\n")
        if always_include_best:
            f.write("#   Note: Best match (rank 1) is always included for each term, even if below threshold.\n")
        f.write("#\n")
        f.write("# IMPORTANT - Manual review recommended:\n")
        f.write("#   Embedding-based similarity is agnostic to ontological categories. High similarity scores\n")
        f.write("#   may occur between semantically related terms of incompatible types (e.g., 'thermophile'\n")
        f.write("#   [material entity] vs 'thermophilic' [quality]). Review mappings to ensure ontological\n")
        f.write("#   compatibility before accepting exactMatch or closeMatch predicates.\n")
        f.write("#\n")
        f.write("# Similarity calculation method:\n")
        f.write("#   1. Query and candidate terms embedded using OpenAI text-embedding-3-small (1536 dimensions, L2-normalized)\n")
        f.write("#   2. Cosine similarity computed as dot product of normalized embeddings: cos_sim = dot(query, candidate)\n")
        f.write("#   3. Similarity score normalized to [0,1]: similarity = (1 + cos_sim) / 2\n")
        f.write("#\n")
        f.write("# Predicate assignment thresholds:\n")
        f.write("#   Data source for threshold calibration:\n")
        f.write("#   - Input terms: src/templates/metpo_sheet_improved.tsv (254 METPO terms)\n")
        f.write("#   - Reference database: data/chromadb/chroma_ols20_nonols4 (452,942 embeddings)\n")
        f.write("#   - Analysis: 5,080 mappings (254 terms × 20 ranks)\n")
        f.write("#   - Query format: 'label; definition' (or 'label parent_labels' as fallback)\n")
        f.write("#\n")
        f.write("#   Predicate thresholds:\n")
        f.write("#   - exactMatch: similarity >= 0.90 (rounded from 95th percentile: 0.886)\n")
        f.write("#   - closeMatch: similarity >= 0.85 (rounded from 75th percentile: 0.845)\n")
        f.write("#   - relatedMatch: similarity >= 0.80 (rounded from 25th percentile: 0.783)\n")
        f.write("#   - mappingRelation: similarity < 0.80 (below 25th percentile, weakest matches)\n")
        f.write("#\n")
        f.write("# Notes:\n")
        f.write("#   - ChromaDB used for efficient retrieval (uses L2 distance internally)\n")
        f.write("#   - True cosine similarity computed from retrieved embeddings\n")
        f.write("#   - similarity_measure field: 'cosine_similarity'\n")
        f.write("#   - Embeddings from 'label; definition' format when definition available, else 'label parent_labels'\n")
        f.write("#\n")

        # Write TSV header and data
        writer = csv.writer(f, delimiter="\t")
        writer.writerow([
            "subject_id",
            "subject_label",
            "predicate_id",
            "object_id",
            "object_label",
            "mapping_justification",
            "similarity_score",
            "similarity_measure",
            "mapping_tool",
            "subject_source",
            "object_source"
        ])

        for m in filtered:
            similarity = 1.0 - (m["distance"] / 2.0)
            writer.writerow([
                m["metpo_id"],
                m["metpo_label"],
                similarity_to_predicate(similarity),
                m["match_iri"],
                m["match_document"],
                "semapv:SemanticSimilarityThresholdMatching",
                f"{similarity:.6f}",
                "cosine_similarity",
                "openai_text-embedding-3-small",
                "METPO",
                m["match_ontology"]
            ])

    return len(filtered)


def query_chromadb_for_term(
    term: dict[str, str],
    collection,
    openai_api_key: str,
    top_n: int = 5,
    label_only: bool = False
) -> list[dict[str, any]]:
    """Generate embedding for a METPO term and query ChromaDB."""

    # Create query text (default: "label; definition", fallback: "label parents", or just label)
    query_text = create_query_text(
        label=term["label"],
        definition=term.get("definition", ""),
        parents=term.get("parents", []),
        label_only=label_only
    )

    # Generate embedding
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=query_text
    )
    query_embedding = response.data[0].embedding

    # Query ChromaDB (request embeddings to compute true cosine distance)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_n,
        include=["documents", "metadatas", "embeddings"]  # Get embeddings, not L2 distances
    )

    # Compute true cosine distances from embeddings
    # For L2-normalized vectors: cosine_sim = dot_product(v1, v2)
    # cosine_distance = 1 - cosine_sim
    import numpy as np

    # Format results
    matches = []
    for i in range(len(results["ids"][0])):
        result_embedding = results["embeddings"][0][i]

        # Compute true cosine similarity and distance
        cosine_sim = float(np.dot(query_embedding, result_embedding))
        cosine_dist = 1.0 - cosine_sim

        matches.append({
            "metpo_id": term["id"],
            "metpo_label": term["label"],
            "metpo_parents": term["parent_str"],
            "query_text": query_text,
            "match_id": results["ids"][0][i],
            "match_document": results["documents"][0][i],
            "match_ontology": results["metadatas"][0][i].get("ontologyId", "unknown"),
            "match_iri": results["metadatas"][0][i].get("iri", "unknown"),
            "distance": cosine_dist,  # True cosine distance, not L2!
            "rank": i + 1
        })

    return matches


@click.command()
@click.option(
    "--metpo-tsv",
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    default="../src/templates/metpo_sheet.tsv",
    help="Path to METPO template TSV file"
)
@click.option(
    "--chroma-path",
    type=click.Path(path_type=str),
    default="./embeddings_chroma",
    help="Path to ChromaDB storage directory"
)
@click.option(
    "--collection-name",
    type=str,
    default="ols_embeddings",
    help="Name of the ChromaDB collection to query"
)
@click.option(
    "--output",
    type=click.Path(path_type=str),
    default="../data/mappings/metpo_mappings.sssom.tsv",
    help="Output SSSOM TSV file path"
)
@click.option(
    "--max-rank",
    type=int,
    default=None,
    help="Maximum number of matches to retrieve per term (default: no limit, retrieve all above min-similarity)"
)
@click.option(
    "--limit",
    type=int,
    default=None,
    help="Limit number of METPO terms to process (for testing)"
)
@click.option(
    "--label-only",
    is_flag=True,
    default=False,
    help="Use only label for embedding (exclude parent labels)"
)
@click.option(
    "--min-similarity",
    type=float,
    default=0.85,
    help="Minimum similarity score to include in SSSOM output (default: 0.85, range: 0.0-1.0)"
)
@click.option(
    "--always-include-best/--no-always-include-best",
    default=True,
    help="Always include best match (rank 1) even if below min-similarity (default: True)"
)
@click.option(
    "--skip-rows",
    type=int,
    default=2,
    help="Number of header rows to skip (ROBOT template=2, standard TSV=1)"
)
@click.option(
    "--id-column",
    type=str,
    default="ID",
    help="Column name for term CURIE/ID (default: 'ID')"
)
@click.option(
    "--label-column",
    type=str,
    default="label",
    help="Column name for term label (default: 'label')"
)
@click.option(
    "--definition-column",
    type=str,
    default="description",
    help="Column name for definition text (default: 'description')"
)
@click.option(
    "--parent-column",
    type=str,
    default="parent class",
    help="Column name for parent classes (default: 'parent class')"
)
def main(
    metpo_tsv: str,
    chroma_path: str,
    collection_name: str,
    output: str,
    max_rank: int,
    limit: int,
    label_only: bool,
    min_similarity: float,
    always_include_best: bool,
    skip_rows: int,
    id_column: str,
    label_column: str,
    definition_column: str,
    parent_column: str
):
    """Query METPO terms against ChromaDB embeddings and generate SSSOM TSV mappings."""

    # Load environment variables (override shell env vars)
    load_dotenv(dotenv_path="../.env", override=True)
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file or environment variables.")

    print(f"Loading METPO terms from: {metpo_tsv}")
    print(f"  Column mapping: ID={id_column}, Label={label_column}, Definition={definition_column}, Parent={parent_column}")
    print(f"  Skipping {skip_rows} header row(s)")
    terms = load_metpo_terms(
        metpo_tsv,
        skip_rows=skip_rows,
        id_column=id_column,
        label_column=label_column,
        definition_column=definition_column,
        parent_column=parent_column
    )
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
    # Default to retrieving 100 candidates if no max_rank specified (will filter by similarity later)
    retrieval_limit = max_rank if max_rank is not None else 100

    if max_rank is not None:
        print(f"\nQuerying ChromaDB for top {max_rank} matches per term...")
    else:
        print(f"\nQuerying ChromaDB (retrieving up to {retrieval_limit} candidates, filtering by similarity)...")

    print(f"This will make {len(terms)} OpenAI API calls (~{len(terms) * 0.5:.0f} seconds)")
    all_matches = []
    errors = 0

    for term in tqdm(terms, desc="Processing METPO terms"):
        try:
            matches = query_chromadb_for_term(term, collection, openai.api_key, retrieval_limit, label_only)
            all_matches.extend(matches)
        except Exception as e:
            errors += 1
            tqdm.write(f"⚠ Error processing {term['id']} ({term['label']}): {e}")
            continue

    # Write results in SSSOM TSV format
    print(f"\nWriting results to: {output}")

    if not all_matches:
        print("⚠ Warning: No matches to write!")
        return

    written = write_sssom_output(all_matches, output, min_similarity, always_include_best)

    # Count by predicate for summary
    max_distance = 2.0 * (1.0 - min_similarity)
    if always_include_best:
        filtered = [m for m in all_matches if m["rank"] == 1 or m["distance"] <= max_distance]
    else:
        filtered = [m for m in all_matches if m["distance"] <= max_distance]
    by_predicate = {}
    for m in filtered:
        similarity = 1.0 - (m["distance"] / 2.0)
        pred = similarity_to_predicate(similarity)
        by_predicate[pred] = by_predicate.get(pred, 0) + 1

    print("\n✓ Complete!")
    print(f"  METPO terms processed: {len(terms)}")
    print(f"  Successful queries: {len(terms) - errors}")
    print(f"  Errors: {errors}")
    print(f"  Total matches retrieved: {len(all_matches)}")
    print(f"  Matches written (similarity >= {min_similarity}): {written}")
    print("\n  Mappings by predicate:")
    for pred, count in sorted(by_predicate.items()):
        print(f"    {pred}: {count}")
    print(f"\n  Output file: {output}")


if __name__ == "__main__":
    main()
