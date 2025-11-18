#!/usr/bin/env python3
"""
Comprehensive definition finder combining multiple sources.

Searches for the best definition for each METPO term by combining:
1. SSSOM embedding-based mappings (ChromaDB)
2. OLS/BioPortal API search results
3. Quality assessment and ranking

For each METPO term, ranks all candidate definitions by:
- Definition quality (length, structure, clarity)
- Source ontology reputation (PATO, GO, OMP > MPO, etc.)
- Match confidence/similarity
- Genus compatibility with parent classes
"""

import csv
import click
import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from difflib import SequenceMatcher
import pandas as pd


# Ontology quality tiers for prioritization
ONTOLOGY_TIERS = {
    "tier1": ["pato", "go", "omp", "bfo", "chebi", "obi"],  # Excellent definitions
    "tier2": ["ecocore", "d3o", "flopo", "micro", "envo", "obo", "upheno"],  # Good definitions
    "tier3": ["cl", "fypo", "apo", "oba", "exo", "ecto"],  # Adequate definitions
    "tier4": ["mpo", "ncit", "snomed", "mesh"],  # Often poor/missing definitions
}


def get_ontology_tier(ontology: str) -> int:
    """Get ontology quality tier (1=best, 5=worst)."""
    ontology_lower = ontology.lower()
    for tier_num, tier_list in enumerate(ONTOLOGY_TIERS.values(), 1):
        if ontology_lower in tier_list:
            return tier_num
    return 5  # Unknown ontologies


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
    if definition_clean.startswith(label_clean):
        extra = definition_clean[len(label_clean):].strip(" ;,.-")
        if len(extra) < min_length:
            return False

    # Check similarity ratio (labels very similar to definitions are suspect)
    similarity = SequenceMatcher(None, label_clean, definition_clean).ratio()
    if similarity > 0.85:
        return False

    return True


def has_genus_term(definition: str) -> bool:
    """Check if definition appears to have genus-differentia structure."""
    definition_lower = definition.lower()

    # Check for typical genus indicators
    genus_indicators = [
        definition_lower.startswith("a "),
        definition_lower.startswith("an "),
        definition_lower.startswith("the "),
        " is a " in definition_lower,
        " is an " in definition_lower,
    ]

    return any(genus_indicators)


def assess_definition_quality(definition: str, ontology: str) -> Tuple[str, int]:
    """
    Assess definition quality.

    Returns:
        (quality_label, quality_score) where higher score is better
    """
    if not definition or len(definition) < 30:
        return "poor", 0

    score = 0

    # Length score
    if len(definition) >= 150:
        score += 3
    elif len(definition) >= 100:
        score += 2
    elif len(definition) >= 50:
        score += 1

    # Structure score
    if has_genus_term(definition):
        score += 2

    # Ontology tier score
    tier = get_ontology_tier(ontology)
    score += (6 - tier)  # tier1=5pts, tier2=4pts, ..., tier5/unknown=1pt

    # Quality label
    if score >= 8:
        quality = "excellent"
    elif score >= 5:
        quality = "good"
    elif score >= 3:
        quality = "adequate"
    else:
        quality = "poor"

    return quality, score


def extract_definition_from_document(document: str) -> Tuple[str, str]:
    """Extract label and definition from ChromaDB document field."""
    if not document:
        return "", ""

    parts = document.split(";", 1)
    label = parts[0].strip()
    definition = parts[1].strip() if len(parts) > 1 else ""

    return label, definition


def load_sssom_candidates(sssom_path: Path, metpo_label: str) -> List[Dict]:
    """Load candidate definitions from SSSOM mappings."""
    candidates = []

    with open(sssom_path, "r", encoding="utf-8") as f:
        lines = [line for line in f if not line.startswith("#")]
        reader = csv.DictReader(lines, delimiter="\t")

        for row in reader:
            subject_label = row.get("subject_label", "").strip()
            if subject_label.lower() != metpo_label.lower():
                continue

            _, definition = extract_definition_from_document(row.get("object_label", ""))

            candidates.append({
                "source": "sssom",
                "definition": definition,
                "source_iri": row.get("object_id", "").strip(),
                "source_ontology": row.get("object_source", "").strip(),
                "source_label": row.get("object_label", "").split(";")[0].strip(),
                "match_type": row.get("predicate_id", "").split(":")[-1],
                "confidence": float(row.get("similarity_score", 0)),
            })

    return candidates


def load_api_candidates(api_results_path: Path, metpo_id: str) -> List[Dict]:
    """Load candidate definitions from OLS/BioPortal API search results."""
    candidates = []

    try:
        df = pd.read_csv(api_results_path, sep="\t")
        matches = df[df["metpo_id"] == metpo_id]

        for _, row in matches.iterrows():
            definition = row.get("match_definition", "")

            candidates.append({
                "source": "api_search",
                "definition": str(definition) if pd.notna(definition) else "",
                "source_iri": str(row.get("match_iri", "")),
                "source_ontology": str(row.get("match_ontology", "")),
                "source_label": str(row.get("match_label", "")),
                "match_type": "exactMatch" if row.get("similarity_ratio", 0) == 1.0 else "closeMatch",
                "confidence": float(row.get("similarity_ratio", 0)),
            })
    except Exception as e:
        # API results file may not exist
        pass

    return candidates


def rank_candidates(
    candidates: List[Dict],
    metpo_label: str,
    min_length: int = 30
) -> List[Dict]:
    """
    Rank and score all candidate definitions.

    Returns candidates sorted by quality score (best first).
    """
    scored = []

    for cand in candidates:
        definition = cand["definition"]
        ontology = cand["source_ontology"]

        # Skip non-real definitions
        if not is_real_definition(metpo_label, definition, min_length):
            continue

        # Assess quality
        quality_label, quality_score = assess_definition_quality(definition, ontology)

        # Calculate total score
        # Components: quality_score (0-10) + confidence boost (0-2)
        confidence = cand.get("confidence", 0)
        confidence_boost = min(2.0, confidence * 2)  # Max 2 points

        total_score = quality_score + confidence_boost

        scored.append({
            **cand,
            "quality_label": quality_label,
            "quality_score": quality_score,
            "total_score": total_score,
            "definition_length": len(definition),
        })

    # Sort by total score (descending)
    scored.sort(key=lambda x: x["total_score"], reverse=True)

    return scored


@click.command()
@click.option(
    "--mappings",
    "-m",
    type=click.Path(exists=True, path_type=Path),
    default="data/mappings/metpo_mappings_combined_relaxed.sssom.tsv",
    help="Path to SSSOM mappings file"
)
@click.option(
    "--api-results",
    "-a",
    type=click.Path(path_type=Path),
    default="data/ontology_assessments/phase1_high_quality_matches.tsv",
    help="Path to OLS/BioPortal API search results"
)
@click.option(
    "--metpo-terms",
    "-t",
    type=click.Path(exists=True, path_type=Path),
    default="src/templates/metpo_sheet.tsv",
    help="Path to METPO terms template"
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default="reports/comprehensive_definition_candidates.tsv",
    help="Output TSV file with all ranked candidates"
)
@click.option(
    "--best-output",
    "-b",
    type=click.Path(path_type=Path),
    default="reports/best_definition_per_term_final.tsv",
    help="Output TSV file with only best definition per term"
)
@click.option(
    "--min-length",
    type=int,
    default=30,
    help="Minimum definition length to consider"
)
@click.option(
    "--top-n",
    type=int,
    default=5,
    help="Number of top candidates to include in comprehensive output"
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed progress"
)
def main(
    mappings: Path,
    api_results: Path,
    metpo_terms: Path,
    output: Path,
    best_output: Path,
    min_length: int,
    top_n: int,
    verbose: bool
):
    """
    Find the best definition for each METPO term from multiple sources.

    Combines SSSOM embeddings, API search results, and quality assessment.
    """

    # Load METPO terms
    click.echo(f"Loading METPO terms from {metpo_terms}...")
    terms = []
    with open(metpo_terms, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)  # Skip ROBOT header row 1
        next(reader)  # Skip ROBOT header row 2

        for row in reader:
            if len(row) < 2:
                continue
            metpo_id = row[0].strip()
            metpo_label = row[1].strip()
            if metpo_id and metpo_label:
                terms.append({"id": metpo_id, "label": metpo_label})

    click.echo(f"Loaded {len(terms)} METPO terms")

    # Process each term
    all_candidates = []
    best_per_term = []
    found_count = 0

    for term in terms:
        metpo_id = term["id"]
        metpo_label = term["label"]

        if verbose:
            click.echo(f"\n{metpo_id} ({metpo_label})")

        # Collect candidates from all sources
        candidates = []

        # Source 1: SSSOM mappings
        sssom_cands = load_sssom_candidates(mappings, metpo_label)
        candidates.extend(sssom_cands)
        if verbose:
            click.echo(f"  SSSOM: {len(sssom_cands)} candidates")

        # Source 2: API search results
        api_cands = load_api_candidates(api_results, metpo_id)
        candidates.extend(api_cands)
        if verbose:
            click.echo(f"  API: {len(api_cands)} candidates")

        # Rank all candidates
        ranked = rank_candidates(candidates, metpo_label, min_length)

        if ranked:
            found_count += 1
            best = ranked[0]

            if verbose:
                click.echo(f"  ✓ Found {len(ranked)} valid definitions")
                click.echo(f"    Best: {best['source_ontology']} (score={best['total_score']:.1f}, {best['quality_label']})")
                click.echo(f"    {best['definition'][:100]}...")
            else:
                click.echo(f"✓ {metpo_id:20s} {len(ranked)} candidates, best: {best['source_ontology']} ({best['quality_label']})")

            # Save best
            best_per_term.append({
                "metpo_id": metpo_id,
                "metpo_label": metpo_label,
                **best
            })

            # Save top N for comprehensive report
            for rank, cand in enumerate(ranked[:top_n], 1):
                all_candidates.append({
                    "metpo_id": metpo_id,
                    "metpo_label": metpo_label,
                    "rank": rank,
                    **cand
                })
        else:
            if not verbose:
                click.echo(f"✗ {metpo_id:20s} no valid definitions found")

    # Write comprehensive output
    click.echo(f"\nWriting comprehensive results to {output}...")
    output.parent.mkdir(parents=True, exist_ok=True)

    if all_candidates:
        fieldnames = [
            "metpo_id", "metpo_label", "rank", "source", "definition",
            "definition_length", "source_iri", "source_ontology", "source_label",
            "match_type", "confidence", "quality_label", "quality_score", "total_score"
        ]
        with open(output, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()
            writer.writerows(all_candidates)

    # Write best per term
    click.echo(f"Writing best definitions to {best_output}...")

    if best_per_term:
        fieldnames = [
            "metpo_id", "metpo_label", "source", "definition", "definition_length",
            "source_iri", "source_ontology", "source_label", "match_type",
            "confidence", "quality_label", "quality_score", "total_score"
        ]
        with open(best_output, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()
            writer.writerows(best_per_term)

    # Summary
    click.echo("\n" + "="*70)
    click.echo("SUMMARY")
    click.echo("="*70)
    click.echo(f"Total METPO terms: {len(terms)}")
    click.echo(f"Terms with definitions: {found_count} ({found_count/len(terms)*100:.1f}%)")
    click.echo(f"Terms without definitions: {len(terms) - found_count}")

    if best_per_term:
        # Quality breakdown
        quality_counts = defaultdict(int)
        for item in best_per_term:
            quality_counts[item["quality_label"]] += 1

        click.echo(f"\nBest definition quality:")
        for quality in ["excellent", "good", "adequate", "poor"]:
            count = quality_counts.get(quality, 0)
            if count > 0:
                click.echo(f"  {quality:12s}: {count:4d} ({count/len(best_per_term)*100:5.1f}%)")

        # Source breakdown
        source_counts = defaultdict(int)
        for item in best_per_term:
            source_counts[item["source"]] += 1

        click.echo(f"\nBest definition source:")
        for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
            click.echo(f"  {source:12s}: {count:4d} ({count/len(best_per_term)*100:5.1f}%)")

        # Ontology breakdown
        onto_counts = defaultdict(int)
        for item in best_per_term:
            onto_counts[item["source_ontology"]] += 1

        click.echo(f"\nBest definition ontology (top 10):")
        for onto, count in sorted(onto_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            click.echo(f"  {onto:15s}: {count:4d} ({count/len(best_per_term)*100:5.1f}%)")

        avg_score = sum(item["total_score"] for item in best_per_term) / len(best_per_term)
        avg_length = sum(item["definition_length"] for item in best_per_term) / len(best_per_term)
        click.echo(f"\nAverage quality score: {avg_score:.1f}")
        click.echo(f"Average definition length: {avg_length:.0f} chars")


if __name__ == "__main__":
    main()
