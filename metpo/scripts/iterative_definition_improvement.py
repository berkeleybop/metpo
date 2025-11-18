#!/usr/bin/env python3
"""
Iteratively improve METPO definitions using multiple sources.

Strategy:
1. Load READY file improvements (undergraduate curator work)
2. For each term:
   - If in READY → use improved definition + sources
   - Else: fix genus, search ChromaDB, compare candidates
3. Pick best definition based on OBO guidelines
4. Extract source attribution from best match

This combines all improvement sources in one pass.
"""
import click
import csv
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from tqdm import tqdm
import chromadb
from openai import OpenAI


def load_ready_improvements(ready_path: str) -> Dict[str, Dict]:
    """Load undergraduate curator improvements."""
    improvements = {}
    with open(ready_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            improvements[row["METPO_ID"]] = {
                "definition": row["Definition"],
                "sources": row.get("Foreign_Sources", ""),
                "curator": row.get("Curator", ""),
                "reasoning": row.get("Comment_Reasoning", "")
            }
    return improvements


def fix_genus_for_parent(definition: str, parent: str, label: str) -> Optional[str]:
    """Fix definition genus to match parent class."""
    if not definition or not parent:
        return None

    # Handle multi-parent (take first)
    parent = parent.split("|")[0].strip()

    # Skip if already has correct genus
    def_lower = definition.lower()
    parent_lower = parent.lower()
    if def_lower.startswith(f"a {parent_lower}") or def_lower.startswith(f"an {parent_lower}"):
        return None  # Already correct

    # Common patterns to fix
    patterns = {
        # Missing genus entirely
        r"^A (difference|range|concentration|temperature|pH|value|span)": f"A {parent}",
        r"^An (observation|organism)": f"An {parent}",

        # Wrong genus
        r"^A quality": f"A {parent}",
        r"^A process": f"A {parent}",
        r"^An entity": f"A {parent}",
    }

    for pattern, replacement in patterns.items():
        if re.match(pattern, definition):
            # Replace just the beginning
            fixed = re.sub(pattern, replacement, definition)
            if fixed != definition:
                return fixed

    # If definition doesn't start with "A/An", try to add genus
    if not re.match(r"^A(n)?\s", definition):
        article = "An" if parent[0].lower() in "aeiou" else "A"
        return f"{article} {parent} {definition.lower()}"

    return None


def check_definition_quality(definition: str, parent: str, label: str) -> Tuple[int, List[str]]:
    """
    Score definition quality (0-100) and return issues.

    Checks:
    - Genus matches parent (40 points)
    - Genus-differentia form (30 points)
    - No examples (10 points)
    - No generalizing (10 points)
    - Reasonable length (10 points)
    """
    score = 0
    issues = []

    if not definition:
        return 0, ["No definition"]

    def_lower = definition.lower()
    parent_lower = parent.split("|")[0].strip().lower() if parent else ""

    # Check genus matches parent (40 points)
    if parent_lower and (def_lower.startswith(f"a {parent_lower}") or def_lower.startswith(f"an {parent_lower}")):
        score += 40
    else:
        issues.append(f"Genus mismatch (parent: {parent})")

    # Check genus-differentia form (30 points)
    if re.match(r"^A(n)?\s+\w+.*?\s+(that|which|where|characterized by|defined by)", definition):
        score += 30
    elif re.match(r"^A(n)?\s+\w+", definition):
        score += 15  # Has genus but weak differentia
        issues.append("Weak differentia")
    else:
        issues.append("Not genus-differentia form")

    # Check for examples (lose 10 points)
    if re.search(r"\b(such as|e\.g\.|for example|including)\b", def_lower):
        issues.append("Contains examples")
    else:
        score += 10

    # Check for generalizing (lose 10 points)
    if re.search(r"\b(usually|generally|typically|often|sometimes|may)\b", def_lower):
        issues.append("Contains generalizing terms")
    else:
        score += 10

    # Check length (10 points)
    if 50 <= len(definition) <= 300:
        score += 10
    elif len(definition) < 50:
        issues.append("Too short")
    else:
        issues.append("Too long")

    return score, issues


def query_chromadb_for_definition(
    term_id: str,
    label: str,
    definition: str,
    collection,
    openai_client,
    n_results: int = 10
) -> List[Dict]:
    """Query ChromaDB to find similar terms with definitions."""
    # Create query text (use current definition or just label)
    query_text = f"{label}; {definition}" if definition else label

    try:
        # Get embedding
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query_text
        )
        query_embedding = response.data[0].embedding

        # Query ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["metadatas", "distances"]
        )

        # Extract matches
        matches = []
        if results["ids"] and results["ids"][0]:
            for i, match_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                similarity = 1.0 - (distance / 2.0)

                # Extract definition from metadata
                foreign_def = metadata.get("definition", "")

                # Skip if no definition or it's just a label repetition
                if not foreign_def or len(foreign_def) < 20:
                    continue

                matches.append({
                    "iri": match_id,
                    "label": metadata.get("label", ""),
                    "definition": foreign_def,
                    "ontology": metadata.get("ontology_prefix", ""),
                    "similarity": similarity,
                    "distance": distance
                })

        return matches

    except Exception as e:
        click.echo(f"  ⚠ Error querying ChromaDB for {term_id}: {e}", err=True)
        return []


def choose_best_definition(
    candidates: Dict[str, Dict],
    parent: str,
    label: str
) -> Tuple[str, str, str, int]:
    """
    Choose best definition from candidates.

    Returns: (definition, source, reason, score)
    """
    scored = []

    for source_type, candidate in candidates.items():
        if not candidate or not candidate.get("definition"):
            continue

        definition = candidate["definition"]
        score, issues = check_definition_quality(definition, parent, label)

        # Bonus for READY file (undergraduate work)
        if source_type == "READY":
            score += 10

        # Bonus for high similarity foreign matches
        if source_type == "foreign" and candidate.get("similarity", 0) >= 0.90:
            score += 5

        scored.append({
            "definition": definition,
            "source": candidate.get("source", source_type),
            "source_type": source_type,
            "score": score,
            "issues": issues,
            "curator": candidate.get("curator", ""),
            "iri": candidate.get("iri", "")
        })

    # Sort by score (highest first)
    scored.sort(key=lambda x: x["score"], reverse=True)

    if scored:
        best = scored[0]
        reason = f"{best['source_type']} (score={best['score']})"
        if best["issues"]:
            reason += f" [issues: {', '.join(best['issues'])}]"

        return best["definition"], best["source"], reason, best["score"]

    return None, None, "No candidates", 0


@click.command()
@click.option(
    "--metpo-tsv",
    type=click.Path(exists=True),
    default="src/templates/metpo_sheet_improved.tsv",
    help="Input METPO template TSV"
)
@click.option(
    "--ready-file",
    type=click.Path(exists=True),
    default="data/undergraduate_definitions/READY_FOR_GOOGLE_SHEETS.tsv",
    help="Undergraduate improvements file"
)
@click.option(
    "--chroma-path",
    type=click.Path(exists=True),
    default="data/chromadb/chroma_ols20_nonols4",
    help="ChromaDB directory"
)
@click.option(
    "--collection-name",
    default="combined_embeddings",
    help="ChromaDB collection name"
)
@click.option(
    "--output",
    type=click.Path(),
    default="src/templates/metpo_sheet_improved_v2.tsv",
    help="Output TSV file"
)
@click.option(
    "--report",
    type=click.Path(),
    default="data/definitions/improvement_report.tsv",
    help="Improvement report file"
)
@click.option(
    "--min-similarity",
    type=float,
    default=0.80,
    help="Minimum similarity for foreign definitions (default: 0.80)"
)
def main(metpo_tsv: str, ready_file: str, chroma_path: str, collection_name: str,
         output: str, report: str, min_similarity: float):
    """
    Iteratively improve METPO definitions.

    Combines:
    - READY file (undergraduate improvements)
    - Genus fixes (automatic parent alignment)
    - ChromaDB foreign definitions (OMP, PATO, GO, etc.)

    Chooses best definition based on OBO guideline compliance.
    """
    click.echo("🔧 Iterative Definition Improvement")
    click.echo("=" * 80)

    # Load READY file improvements
    click.echo(f"\n📥 Loading READY file from {ready_file}...")
    ready_improvements = load_ready_improvements(ready_file)
    click.echo(f"  Found {len(ready_improvements)} undergraduate improvements")

    # Initialize ChromaDB
    click.echo(f"\n📥 Loading ChromaDB from {chroma_path}...")
    chroma_client = chromadb.PersistentClient(path=chroma_path)
    collection = chroma_client.get_collection(collection_name)
    click.echo(f"  Collection '{collection_name}' loaded ({collection.count()} embeddings)")

    # Initialize OpenAI
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Load current METPO terms
    click.echo(f"\n📥 Loading METPO terms from {metpo_tsv}...")
    terms = []
    with open(metpo_tsv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        fieldnames = reader.fieldnames
        for row in reader:
            terms.append(row)
    click.echo(f"  Loaded {len(terms)} terms")

    # Process each term
    click.echo(f"\n🔄 Processing terms...")
    improvements = []
    report_data = []

    for term in tqdm(terms, desc="Improving definitions"):
        term_id = term["ID"]
        label = term["label"]
        current_def = term.get("description", "").strip()
        current_source = term.get("definition source", "").strip()
        current_editor = term.get("term editor", "").strip()
        parent = term.get("parent classes (one strongly preferred)", "").strip()

        # Skip if no parent (root classes)
        if not parent:
            continue

        # Collect candidates
        candidates = {
            "current": {
                "definition": current_def,
                "source": current_source,
            }
        }

        # Add READY improvement if available
        if term_id in ready_improvements:
            ready = ready_improvements[term_id]
            candidates["READY"] = {
                "definition": ready["definition"],
                "source": ready["sources"],
                "curator": ready["curator"]
            }

        # Try to fix genus
        fixed_def = fix_genus_for_parent(current_def, parent, label)
        if fixed_def:
            candidates["genus_fixed"] = {
                "definition": fixed_def,
                "source": current_source or "METPO (genus corrected)"
            }

        # Query ChromaDB for foreign definitions
        foreign_matches = query_chromadb_for_definition(
            term_id, label, current_def, collection, openai_client, n_results=5
        )

        # Add top foreign match if good enough
        if foreign_matches and foreign_matches[0]["similarity"] >= min_similarity:
            best_foreign = foreign_matches[0]
            candidates["foreign"] = {
                "definition": best_foreign["definition"],
                "source": best_foreign["iri"],
                "similarity": best_foreign["similarity"],
                "iri": best_foreign["iri"]
            }

        # Choose best definition
        best_def, best_source, reason, score = choose_best_definition(candidates, parent, label)

        # Update term if improved
        improved = False
        if best_def and best_def != current_def:
            term["description"] = best_def
            improved = True

        if best_source and best_source != current_source:
            # Add source if missing or better
            if not current_source or best_source.startswith("http"):
                term["definition source"] = best_source
                improved = True

        # Add curator to term editor if from READY
        if term_id in ready_improvements and not current_editor:
            curator = ready_improvements[term_id]["curator"]
            term["term editor"] = curator
            improved = True

        if improved:
            improvements.append(term_id)

        # Add to report
        report_data.append({
            "term_id": term_id,
            "label": label,
            "parent": parent,
            "current_definition": current_def[:100] + "..." if len(current_def) > 100 else current_def,
            "new_definition": best_def[:100] + "..." if best_def and len(best_def) > 100 else best_def,
            "current_source": current_source,
            "new_source": best_source,
            "improved": "Yes" if improved else "No",
            "reason": reason,
            "score": score
        })

    # Write output
    click.echo(f"\n💾 Writing output to {output}...")
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(terms)

    # Write report
    click.echo(f"💾 Writing report to {report}...")
    Path(report).parent.mkdir(parents=True, exist_ok=True)
    with open(report, "w", encoding="utf-8", newline="") as f:
        if report_data:
            writer = csv.DictWriter(f, fieldnames=report_data[0].keys(), delimiter="\t")
            writer.writeheader()
            writer.writerows(report_data)

    # Summary
    click.echo(f"\n✅ Complete!")
    click.echo(f"  Total terms processed: {len(terms)}")
    click.echo(f"  Terms improved: {len(improvements)} ({len(improvements)/len(terms)*100:.1f}%)")
    click.echo(f"  READY improvements used: {len([t for t in terms if t['ID'] in ready_improvements])}")
    click.echo(f"\n📄 Files:")
    click.echo(f"  Output: {output}")
    click.echo(f"  Report: {report}")


if __name__ == "__main__":
    main()
