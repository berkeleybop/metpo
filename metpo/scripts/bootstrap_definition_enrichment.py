"""
Bootstrap METPO definition enrichment by fetching real definitions from source
ontologies and assessing their quality and reuse.

This script:
1. Finds high-confidence SSSOM mappings for METPO terms
2. Fetches actual definitions from source ontologies (via local OWL or APIs)
3. Measures term "importance" via reuse across ontologies (PageRank proxy)
4. Assesses definition quality against Seppälä-Ruttenberg-Smith guidelines
5. Generates prioritized recommendations
"""

import csv
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

import click
import requests


def read_sssom_mappings(sssom_path: Path, min_confidence: float) -> dict[str, list[dict]]:
    """Read SSSOM mappings and organize by METPO term, filtering by confidence."""
    mappings = defaultdict(list)

    with Path(sssom_path).open(encoding="utf-8") as f:
        lines = [line for line in f if not line.startswith("#")]
        reader = csv.DictReader(lines, delimiter="\t")

        for row in reader:
            subject_id = row.get("subject_id", "").strip()
            if not subject_id.startswith("METPO:"):
                continue

            confidence = float(row.get("confidence", 0))
            if confidence < min_confidence:
                continue

            mapping_info = {
                "subject_id": subject_id,
                "subject_label": row.get("subject_label", "").strip(),
                "predicate_id": row.get("predicate_id", "").strip(),
                "object_id": row.get("object_id", "").strip(),
                "object_label": row.get("object_label", "").strip(),
                "confidence": confidence,
                "similarity_score": float(row.get("similarity_score", 0)),
                "object_source": row.get("object_source", "").strip(),
            }

            mappings[subject_id].append(mapping_info)

    return mappings


def extract_definition_from_label(object_label: str) -> str | None:
    """Extract definition from object_label if it contains one (label; definition format)."""
    if ";" not in object_label:
        return None

    parts = object_label.split(";", 1)
    definition = parts[1].strip()

    # Filter out obvious non-definitions (just synonyms, short phrases)
    if len(definition) < 20:  # Too short to be a real definition
        return None
    if definition[0].islower() and not definition.startswith("the "):  # Likely just a synonym
        return None

    return definition


def fetch_term_from_ols(term_iri: str, max_retries: int = 3) -> dict | None:
    """Fetch term information from OLS4 API."""
    encoded_iri = quote(term_iri, safe="")
    url = f"https://www.ebi.ac.uk/ols4/api/terms/{encoded_iri}"

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "_embedded" in data and "terms" in data["_embedded"]:
                    terms = data["_embedded"]["terms"]
                    if terms:
                        return terms[0]
            elif response.status_code == 404:
                return None
            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            if attempt == max_retries - 1:
                click.echo(f"Warning: Failed to fetch {term_iri}: {e}", err=True)
            time.sleep(1)

    return None


def count_ontology_usage_ols(term_iri: str) -> int:
    """Count how many ontologies in OLS use this term (PageRank proxy)."""
    try:
        # Use OLS search with exact IRI match
        encoded_iri = quote(term_iri, safe="")
        url = f"https://www.ebi.ac.uk/ols4/api/search?q={encoded_iri}&exact=true&groupField=iri&rows=100"

        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "response" in data:
                num_found = data["response"].get("numFound", 0)
                return num_found
        time.sleep(0.5)  # Rate limiting
    except Exception as e:
        click.echo(f"Warning: Failed to count usage for {term_iri}: {e}", err=True)

    return 0


def assess_definition_quality_detailed(definition: str) -> dict[str, any]:
    """
    Assess definition quality against Seppälä-Ruttenberg-Smith guidelines.
    Returns dict with quality metrics.
    """
    if not definition:
        return {
            "overall": "missing",
            "length": 0,
            "has_genus": False,
            "issues": ["No definition"],
        }

    issues = []

    # Check length
    length = len(definition)
    if length < 30:
        issues.append("Too short (< 30 chars)")

    # Check for genus-differentia structure (heuristic)
    has_genus = False
    genus_indicators = ["a ", "an ", "the "]
    if any(definition.lower().startswith(ind) for ind in genus_indicators):
        has_genus = True

    # Check for circular definition (starts with defined term)
    # Note: We don't have the definiendum here, so can't check this

    # Check for problematic patterns
    if "usually" in definition.lower() or "generally" in definition.lower():
        issues.append("Contains generalizing expression (usually/generally)")

    if (
        "such as" in definition.lower()
        or "e.g." in definition.lower()
        or "for example" in definition.lower()
    ):
        issues.append("Contains examples (such as/e.g./for example)")

    if definition.count(";") > 1:
        issues.append("Multiple semicolons (may be multiple definitions)")

    # Determine overall quality
    if length == 0:
        overall = "missing"
    elif length < 30 or len(issues) >= 3:
        overall = "poor"
    elif length < 100 or len(issues) >= 2:
        overall = "adequate"
    elif len(issues) == 0 and has_genus:
        overall = "excellent"
    else:
        overall = "good"

    return {
        "overall": overall,
        "length": length,
        "has_genus": has_genus,
        "issues": issues,
    }


@click.command()
@click.option(
    "--mappings",
    "-m",
    type=click.Path(exists=True, path_type=Path),
    default="data/mappings/metpo_mappings_combined_relaxed.sssom.tsv",
    help="Path to SSSOM mappings file",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default="reports/definition_enrichment_bootstrap.tsv",
    help="Output TSV file for recommendations",
)
@click.option(
    "--min-confidence",
    type=float,
    default=0.85,
    help="Minimum confidence threshold for considering mappings",
)
@click.option(
    "--fetch-from-ols/--no-fetch", default=True, help="Fetch additional metadata from OLS API"
)
@click.option("--top-n", type=int, default=20, help="Number of top mappings to analyze in detail")
def main(mappings: Path, output: Path, min_confidence: float, fetch_from_ols: bool, top_n: int):
    """
    Bootstrap METPO definition enrichment by fetching real definitions
    and assessing quality with PageRank-like term importance.
    """
    click.echo(f"Reading SSSOM mappings from {mappings}...")
    click.echo(f"Minimum confidence: {min_confidence}")

    sssom_mappings = read_sssom_mappings(mappings, min_confidence)
    click.echo(f"Found {len(sssom_mappings)} METPO terms with high-confidence mappings")

    # Collect all candidate definitions
    candidates = []

    for metpo_id, term_mappings in sorted(sssom_mappings.items()):
        metpo_label = term_mappings[0]["subject_label"] if term_mappings else ""

        for mapping in term_mappings[:3]:  # Top 3 matches per term
            # Extract definition from SSSOM object_label
            sssom_def = extract_definition_from_label(mapping["object_label"])

            if sssom_def:
                candidates.append(
                    {
                        "metpo_id": metpo_id,
                        "metpo_label": metpo_label,
                        "source_iri": mapping["object_id"],
                        "source_ontology": mapping["object_source"],
                        "match_type": mapping["predicate_id"].split("#")[-1].split(":")[-1],
                        "confidence": mapping["confidence"],
                        "definition_source": "sssom",
                        "definition": sssom_def,
                    }
                )

    click.echo(f"\nFound {len(candidates)} candidate definitions from SSSOM file")

    # Fetch additional data from OLS for top candidates
    if fetch_from_ols and candidates:
        click.echo(f"\nFetching additional metadata from OLS for top {top_n} candidates...")

        # Sort by confidence and take top N
        top_candidates = sorted(candidates, key=lambda x: x["confidence"], reverse=True)[:top_n]

        for i, candidate in enumerate(top_candidates, 1):
            click.echo(
                f"  [{i}/{len(top_candidates)}] Fetching {candidate['source_iri']}...", nl=False
            )

            # Fetch term from OLS
            ols_data = fetch_term_from_ols(candidate["source_iri"])

            if ols_data:
                # Get definition from OLS (more authoritative)
                ols_def = None
                if ols_data.get("description"):
                    ols_def = " ".join(ols_data["description"])

                if ols_def and len(ols_def) > len(candidate["definition"]):
                    candidate["definition"] = ols_def
                    candidate["definition_source"] = "ols"

                # Count usage across ontologies
                usage_count = count_ontology_usage_ols(candidate["source_iri"])
                candidate["ontology_usage_count"] = usage_count

                click.echo(f" ✓ (used in {usage_count} ontologies)")
            else:
                candidate["ontology_usage_count"] = 0
                click.echo(" ✗ (not found in OLS)")

    # Assess quality of all definitions
    click.echo("\nAssessing definition quality...")
    for candidate in candidates:
        quality = assess_definition_quality_detailed(candidate["definition"])
        candidate["quality_overall"] = quality["overall"]
        candidate["quality_length"] = quality["length"]
        candidate["quality_has_genus"] = quality["has_genus"]
        candidate["quality_issues"] = "; ".join(quality["issues"]) if quality["issues"] else ""

    # Sort by multiple factors: confidence, quality, usage
    def sort_key(c):
        quality_score = {"excellent": 4, "good": 3, "adequate": 2, "poor": 1, "missing": 0}
        return (
            quality_score.get(c["quality_overall"], 0),
            c.get("ontology_usage_count", 0),
            c["confidence"],
        )

    candidates.sort(key=sort_key, reverse=True)

    # Write output
    output.parent.mkdir(parents=True, exist_ok=True)

    if candidates:
        fieldnames = [
            "metpo_id",
            "metpo_label",
            "source_iri",
            "source_ontology",
            "match_type",
            "confidence",
            "ontology_usage_count",
            "quality_overall",
            "quality_length",
            "quality_has_genus",
            "quality_issues",
            "definition_source",
            "definition",
        ]

        with Path(output).open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()

            for candidate in candidates:
                # Ensure all fields exist
                row = {field: candidate.get(field, "") for field in fieldnames}
                writer.writerow(row)

        click.echo(f"\n✓ Generated {len(candidates)} recommendations")
        click.echo(f"✓ Output written to {output}")

        # Summary statistics
        by_quality = defaultdict(int)
        for c in candidates:
            by_quality[c["quality_overall"]] += 1

        click.echo("\nQuality distribution:")
        for quality in ["excellent", "good", "adequate", "poor", "missing"]:
            if quality in by_quality:
                click.echo(f"  {quality}: {by_quality[quality]}")

        # Show top 5
        click.echo("\nTop 5 recommendations:")
        for i, candidate in enumerate(candidates[:5], 1):
            click.echo(f"\n  {i}. {candidate['metpo_id']} ({candidate['metpo_label']})")
            click.echo(
                f"     Quality: {candidate['quality_overall']} | "
                f"Used in {candidate.get('ontology_usage_count', '?')} ontologies | "
                f"Confidence: {candidate['confidence']:.3f}"
            )
            click.echo(f"     Definition: {candidate['definition'][:100]}...")
    else:
        click.echo("\n✗ No candidate definitions found")


if __name__ == "__main__":
    main()
