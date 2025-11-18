"""
Generate embeddings from ROBOT query TSV output and insert into ChromaDB.

Takes TSV from: robot query --input <owl> --query sparql/extract_for_embeddings.rq <output.tsv>

Follows the methodology from https://cthoyt.com/2025/08/04/ontology-text-embeddings.html
- Concatenates labels, synonyms, and definitions as: "label; synonym1; synonym2; definition"
- Generates embeddings using OpenAI text-embedding-3-small
- Stores in ChromaDB with metadata (ontologyId, entityType, iri)
"""

import csv
import os
from pathlib import Path

import chromadb
import click
import openai
from chromadb.config import Settings
from dotenv import load_dotenv
from tqdm import tqdm


def parse_robot_output(tsv_path: str, ontology_id: str) -> list[dict]:
    """
    Parse ROBOT query TSV output into term dictionaries.

    Returns list of dicts with: iri, label, synonyms, definition, document
    """
    terms = []

    with Path(tsv_path).open( encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            # Handle SPARQL variable names (with or without ? prefix)
            iri = row.get("?class") or row.get("class")

            # Normalize IRI: strip angle brackets if present (standardize format)
            if iri and iri.startswith("<") and iri.endswith(">"):
                iri = iri[1:-1]

            # Parse labels (take first as primary)
            labels_str = row.get("?labels") or row.get("labels", "")
            if not labels_str:
                continue  # Skip if no label

            labels = [lbl.strip() for lbl in labels_str.split("|") if lbl.strip()]
            label = labels[0]

            # Parse synonyms
            synonyms_str = row.get("?synonyms") or row.get("synonyms", "")
            synonyms = [s.strip() for s in synonyms_str.split("|") if s.strip()] if synonyms_str else []

            # Parse definitions (take first)
            definitions_str = row.get("?definitions") or row.get("definitions", "")
            definitions = [d.strip() for d in definitions_str.split("|") if d.strip()] if definitions_str else []
            definition = definitions[0] if definitions else ""

            # Create document text: "label; synonym1; synonym2; definition"
            parts = [label]
            parts.extend(synonyms)
            if definition:
                parts.append(definition)
            document = "; ".join(parts)

            terms.append({
                "iri": iri,
                "label": label,
                "synonyms": synonyms,
                "definition": definition,
                "document": document,
                "ontologyId": ontology_id,
                "entityType": "class"
            })

    return terms


def generate_embedding(text: str, api_key: str, model: str = "text-embedding-3-small") -> list[float]:
    """Generate OpenAI embedding for text."""
    client = openai.OpenAI(api_key=api_key)
    response = client.embeddings.create(
        model=model,
        input=text
    )
    return response.data[0].embedding


def insert_into_chromadb(
    terms: list[dict],
    chroma_path: str,
    collection_name: str,
    api_key: str,
    batch_size: int = 100,
    skip_existing: bool = True
):
    """
    Insert terms with embeddings into ChromaDB.

    Args:
        terms: List of term dicts from parse_robot_output
        chroma_path: Path to ChromaDB storage
        collection_name: Name of collection
        api_key: OpenAI API key
        batch_size: Number of terms to process per batch
        skip_existing: Skip terms that already exist in collection
    """
    # Initialize ChromaDB
    client = chromadb.PersistentClient(
        path=chroma_path,
        settings=Settings(anonymized_telemetry=False)
    )

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"description": "OLS + custom ontology embeddings"}
    )

    # Get existing IRIs if skip_existing is True
    existing_iris = set()
    if skip_existing and terms:
        try:
            # Get all existing entries for this ontology
            ontology_id = terms[0]["ontologyId"]
            results = collection.get(
                where={"ontologyId": ontology_id},
                include=["metadatas"]
            )
            existing_iris = {meta["iri"] for meta in results["metadatas"]}
            if existing_iris:
                print(f"Found {len(existing_iris)} existing terms for {ontology_id}")
        except Exception as e:
            print(f"Warning: Could not check existing terms: {e}")

    # Process in batches
    added = 0
    skipped = 0
    errors = 0

    for i in tqdm(range(0, len(terms), batch_size), desc="Generating embeddings"):
        batch = terms[i:i + batch_size]

        batch_ids = []
        batch_embeddings = []
        batch_documents = []
        batch_metadatas = []

        for term in batch:
            # Skip if already exists
            if term["iri"] in existing_iris:
                skipped += 1
                continue

            try:
                # Generate embedding
                embedding = generate_embedding(term["document"], api_key)

                # Create unique ID (ontologyId:entityType:iri)
                term_id = f"{term['ontologyId']}:{term['entityType']}:{term['iri']}"

                batch_ids.append(term_id)
                batch_embeddings.append(embedding)
                batch_documents.append(term["document"])
                batch_metadatas.append({
                    "ontologyId": term["ontologyId"],
                    "entityType": term["entityType"],
                    "iri": term["iri"]
                })

            except Exception as e:
                errors += 1
                tqdm.write(f"Error processing {term['iri']}: {e}")
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
                added += len(batch_ids)
            except Exception as e:
                errors += len(batch_ids)
                tqdm.write(f"Error adding batch to ChromaDB: {e}")

    print("\n✓ Complete!")
    print(f"  Added: {added}")
    print(f"  Skipped (existing): {skipped}")
    print(f"  Errors: {errors}")
    print(f"  Total terms in collection: {collection.count():,}")


@click.command()
@click.option(
    "--tsv-file",
    type=click.Path(exists=True, dir_okay=False),
    multiple=True,
    required=True,
    help="Path(s) to ROBOT query TSV output"
)

@click.option(
    "--chroma-path",
    type=click.Path(),
    default="./embeddings_chroma",
    help="Path to ChromaDB storage directory"
)
@click.option(
    "--collection-name",
    type=str,
    default="ols_embeddings",
    help="Name of ChromaDB collection"
)
@click.option(
    "--batch-size",
    type=int,
    default=100,
    help="Batch size for embedding generation"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show terms without generating embeddings"
)
@click.option(
    "--no-skip-existing",
    is_flag=True,
    help="Don't skip existing terms (will error on duplicates)"
)
def main(tsv_file: tuple[str], chroma_path: str, collection_name: str,
         batch_size: int, dry_run: bool, no_skip_existing: bool):
    """
    Generate embeddings from ROBOT query TSV and insert into ChromaDB.

    Workflow:
        # 1. Run ROBOT query to extract terms
        robot query \\
            --input ../external/ontologies/bioportal/D3O.owl \\
            --query ../sparql/extract_for_embeddings.rq \\
            d3o_terms.tsv

        # 2. Generate embeddings and insert to ChromaDB
        python embed_ontology_to_chromadb.py \\
            --tsv-file d3o_terms.tsv \\
            --ontology-id d3o \\
            --chroma-path ./chroma_ols_27

        # Or dry run to preview:
        python embed_ontology_to_chromadb.py \\
            --tsv-file d3o_terms.tsv \\
            --ontology-id d3o \\
            --dry-run
    """
    # Load environment (override=True to use .env file even if var already set)
    load_dotenv(dotenv_path="../.env", override=True)
    api_key = os.getenv("OPENAI_API_KEY")

    if not dry_run and not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")

    all_terms = []
    total_api_calls = 0

    for single_tsv_file in tsv_file:
        # Extract ontology_id from filename (e.g., "D3O.tsv" -> "d3o")
        ontology_id = os.path.basename(single_tsv_file).split(".")[0].lower()
        print(f"Parsing ROBOT query output: {single_tsv_file} for ontology ID: {ontology_id}")
        terms = parse_robot_output(single_tsv_file, ontology_id)
        print(f"✓ Extracted {len(terms)} terms from {ontology_id}")
        all_terms.extend(terms)
        total_api_calls += len(terms)

    if not all_terms:
        print("No terms found in any TSV files. Check if ROBOT query extracted any classes.")
        return

    # Show sample from the first term in the aggregated list
    print("\nSample term:")
    sample = all_terms[0]
    print(f"  IRI: {sample['iri']}")
    print(f"  Label: {sample['label']}")
    print(f"  Synonyms: {len(sample['synonyms'])}")
    def_preview = sample["definition"][:100] if sample["definition"] else "(none)"
    print(f"  Definition: {def_preview}")
    print(f"  Document: {sample['document'][:150]}...")

    if dry_run:
        print("\n✓ Dry run complete (no embeddings generated)")
        print("\nFirst 5 terms (from all aggregated):")
        for term in all_terms[:5]:
            print(f"\n{term['label']} (Ontology: {term['ontologyId']})")
            print(f"  IRI: {term['iri']}")
            if term["synonyms"]:
                print(f"  Synonyms: {', '.join(term['synonyms'][:3])}")
            doc_preview = term["document"][:200] + "..." if len(term["document"]) > 200 else term["document"]
            print(f"  Doc: {doc_preview}")
        return

    print("\nGenerating embeddings and inserting into ChromaDB...")
    print(f"  This will make {total_api_calls} OpenAI API calls")
    print(f"  Estimated cost: ~${total_api_calls * 0.00002:.4f}")

    insert_into_chromadb(
        all_terms,
        chroma_path,
        collection_name,
        api_key,
        batch_size,
        skip_existing=not no_skip_existing
    )


if __name__ == "__main__":
    main()
