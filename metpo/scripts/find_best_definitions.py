#!/usr/bin/env python3
"""
Find the best available definition for each METPO term from SSSOM mappings.

For each METPO term, iterate through mappings in descending similarity order
until finding a real definition (not just a label). Uses ChromaDB as the
authoritative source for definitions.

Quality criteria for a "real" definition:
- Not empty
- Not just the label repeated
- Length >= 30 characters
- Contains more than just the term name
"""

import csv
import click
import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
from difflib import SequenceMatcher


def is_real_definition(label: str, definition: str, min_length: int = 30) -> bool:
    """
    Check if a definition is real and not just a label repetition.

    Args:
        label: The term label
        definition: The candidate definition
        min_length: Minimum acceptable definition length

    Returns:
        True if this is a real, usable definition
    """
    if not definition or len(definition.strip()) < min_length:
        return False

    definition = definition.strip()
    label_clean = label.strip().lower()
    definition_clean = definition.lower()

    # Check if definition is just the label
    if definition_clean == label_clean:
        return False

    # Check if definition starts with label and has minimal additional content
    # e.g., "Thermophilic; Thermophilic" or "Coccus-shaped; Coccus"
    if definition_clean.startswith(label_clean):
        extra = definition_clean[len(label_clean):].strip(" ;,.-")
        if len(extra) < min_length:
            return False

    # Check similarity ratio (labels very similar to definitions are suspect)
    similarity = SequenceMatcher(None, label_clean, definition_clean).ratio()
    if similarity > 0.85:
        return False

    return True


def extract_definition_from_document(document: str) -> tuple[str, str]:
    """
    Extract label and definition from ChromaDB document field.

    ChromaDB documents use format: "label; definition" or just "label"

    Returns:
        (label, definition) tuple
    """
    if not document:
        return "", ""

    # Split on first semicolon
    parts = document.split(";", 1)
    label = parts[0].strip()
    definition = parts[1].strip() if len(parts) > 1 else ""

    return label, definition


def load_sssom_mappings(sssom_path: Path) -> Dict[str, List[Dict]]:
    """
    Load SSSOM mappings grouped by METPO subject_id, sorted by similarity.

    Returns:
        Dict mapping METPO ID -> list of mappings (highest similarity first)
    """
    mappings_by_subject = defaultdict(list)

    with open(sssom_path, "r", encoding="utf-8") as f:
        lines = [line for line in f if not line.startswith("#")]
        reader = csv.DictReader(lines, delimiter="\t")

        for row in reader:
            subject_id = row.get("subject_id", "").strip()
            if not subject_id.startswith("METPO:"):
                continue

            mappings_by_subject[subject_id].append({
                "subject_id": subject_id,
                "subject_label": row.get("subject_label", "").strip(),
                "object_id": row.get("object_id", "").strip(),
                "object_label": row.get("object_label", "").strip(),
                "object_source": row.get("object_source", "").strip(),
                "predicate_id": row.get("predicate_id", "").strip(),
                "confidence": float(row.get("confidence", 0)),
                "similarity_score": float(row.get("similarity_score", 0)),
                "comment": row.get("comment", "").strip(),
            })

    # Sort each term's mappings by similarity (highest first)
    for subject_id in mappings_by_subject:
        mappings_by_subject[subject_id].sort(
            key=lambda x: x["similarity_score"],
            reverse=True
        )

    return mappings_by_subject


def get_definition_from_chromadb(
    term_iri: str,
    collection,
    ontology_id: str
) -> Optional[str]:
    """
    Query ChromaDB to get the definition for a specific term IRI.

    Args:
        term_iri: Full IRI of the term
        collection: ChromaDB collection
        ontology_id: Ontology ID to filter by (e.g., "pato", "go")

    Returns:
        Definition text or None if not found
    """
    try:
        # Query by IRI metadata
        results = collection.get(
            where={"$and": [
                {"iri": term_iri},
                {"ontologyId": ontology_id.lower()}
            ]},
            include=["documents", "metadatas"]
        )

        if results and results["documents"]:
            document = results["documents"][0]
            label, definition = extract_definition_from_document(document)
            return definition if definition else None

        return None

    except Exception as e:
        click.echo(f"  Warning: Error querying ChromaDB for {term_iri}: {e}", err=True)
        return None


@click.command()
@click.option(
    "--mappings",
    "-m",
    type=click.Path(exists=True, path_type=Path),
    default="data/mappings/metpo_mappings_combined_relaxed.sssom.tsv",
    help="Path to SSSOM mappings file"
)
@click.option(
    "--chromadb-path",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    default="data/chromadb/chroma_ols20_nonols4",
    help="Path to ChromaDB directory"
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default="reports/best_definitions_per_term.tsv",
    help="Output TSV file"
)
@click.option(
    "--min-length",
    type=int,
    default=30,
    help="Minimum definition length to consider"
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed progress for each term"
)
def main(
    mappings: Path,
    chromadb_path: Path,
    output: Path,
    min_length: int,
    verbose: bool
):
    """
    Find the best available definition for each METPO term.

    For each METPO term, iterates through mappings in descending similarity
    order, checking ChromaDB for real definitions until one is found.
    """

    click.echo(f"Loading SSSOM mappings from {mappings}...")
    mappings_by_term = load_sssom_mappings(mappings)
    click.echo(f"Loaded mappings for {len(mappings_by_term)} METPO terms")

    click.echo(f"\nConnecting to ChromaDB at {chromadb_path}...")
    client = chromadb.PersistentClient(
        path=str(chromadb_path),
        settings=Settings(anonymized_telemetry=False)
    )
    collection = client.get_collection(name="combined_embeddings")
    click.echo(f"Connected to collection: {collection.count():,} embeddings")

    # Process each term
    click.echo(f"\nProcessing {len(mappings_by_term)} METPO terms...")
    results = []

    found_count = 0
    not_found_count = 0

    for subject_id in sorted(mappings_by_term.keys()):
        term_mappings = mappings_by_term[subject_id]
        subject_label = term_mappings[0]["subject_label"]

        if verbose:
            click.echo(f"\n{subject_id} ({subject_label})")
            click.echo(f"  Checking {len(term_mappings)} mappings...")

        best_definition = None
        best_mapping = None
        checked_count = 0

        # Try each mapping in order of similarity
        for mapping in term_mappings:
            checked_count += 1
            object_iri = mapping["object_id"]
            object_source = mapping["object_source"]
            similarity = mapping["similarity_score"]

            if verbose:
                click.echo(f"  [{checked_count}] {object_source} (sim={similarity:.3f}): {object_iri}")

            # First try the object_label from SSSOM (which may have semicolon format)
            sssom_label, sssom_def = extract_definition_from_document(mapping["object_label"])

            if is_real_definition(subject_label, sssom_def, min_length):
                best_definition = sssom_def
                best_mapping = mapping
                if verbose:
                    click.echo(f"    ✓ Found in SSSOM: {sssom_def[:80]}...")
                break

            # Try ChromaDB
            chromadb_def = get_definition_from_chromadb(object_iri, collection, object_source)

            if chromadb_def and is_real_definition(subject_label, chromadb_def, min_length):
                best_definition = chromadb_def
                best_mapping = mapping
                if verbose:
                    click.echo(f"    ✓ Found in ChromaDB: {chromadb_def[:80]}...")
                break

            if verbose and chromadb_def:
                click.echo(f"    ✗ ChromaDB def too short or label-like: {chromadb_def[:60]}")

        # Record result
        if best_definition:
            found_count += 1
            match_type = best_mapping["predicate_id"].split(":")[-1]
            results.append({
                "metpo_id": subject_id,
                "metpo_label": subject_label,
                "definition": best_definition,
                "definition_length": len(best_definition),
                "source_iri": best_mapping["object_id"],
                "source_ontology": best_mapping["object_source"],
                "source_label": sssom_label if best_definition == sssom_def else
                                extract_definition_from_document(best_mapping["object_label"])[0],
                "similarity_score": best_mapping["similarity_score"],
                "match_type": match_type,
                "rank": checked_count,
            })

            if not verbose:
                click.echo(f"✓ {subject_id:20s} found (sim={best_mapping['similarity_score']:.3f}, rank={checked_count})")
        else:
            not_found_count += 1
            if not verbose:
                click.echo(f"✗ {subject_id:20s} no definition found ({len(term_mappings)} checked)")

    # Write output
    click.echo(f"\nWriting results to {output}...")
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "metpo_id", "metpo_label", "definition", "definition_length",
            "source_iri", "source_ontology", "source_label",
            "similarity_score", "match_type", "rank"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(results)

    # Summary
    click.echo("\n" + "="*70)
    click.echo("SUMMARY")
    click.echo("="*70)
    click.echo(f"Total METPO terms: {len(mappings_by_term)}")
    click.echo(f"Found definitions: {found_count} ({found_count/len(mappings_by_term)*100:.1f}%)")
    click.echo(f"No definition found: {not_found_count} ({not_found_count/len(mappings_by_term)*100:.1f}%)")

    if results:
        avg_similarity = sum(r["similarity_score"] for r in results) / len(results)
        avg_length = sum(r["definition_length"] for r in results) / len(results)
        avg_rank = sum(r["rank"] for r in results) / len(results)

        click.echo(f"\nDefinition Quality:")
        click.echo(f"  Average similarity: {avg_similarity:.3f}")
        click.echo(f"  Average length: {avg_length:.0f} chars")
        click.echo(f"  Average rank: {avg_rank:.1f} (how many mappings checked)")

        # By ontology
        by_ontology = defaultdict(int)
        for r in results:
            by_ontology[r["source_ontology"]] += 1

        click.echo(f"\nDefinitions by source ontology:")
        for ont, count in sorted(by_ontology.items(), key=lambda x: x[1], reverse=True):
            pct = count / len(results) * 100
            click.echo(f"  {ont:15s}: {count:4d} ({pct:5.1f}%)")


if __name__ == "__main__":
    main()
