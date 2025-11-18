"""
Extract definitions, definition sources, and cross-references from SSSOM mapping results.

This script analyzes semantic mapping results to:
1. Propose definitions for METPO terms without definitions
2. Assign definition sources (IAO:0000119) based on best matches
3. Generate database cross-references
4. Create skos:closeMatch annotations

Usage:
    uv run python extract_definitions_from_mappings.py
"""

import re
from pathlib import Path

import pandas as pd

# Configuration
SSSOM_FILE = "../../data/mappings/metpo_mappings_combined_relaxed.sssom.tsv"
METPO_SHEET = "../../src/templates/metpo_sheet.tsv"
OUTPUT_DIR = Path("../../data/definitions")

# Thresholds
HIGH_CONFIDENCE_DISTANCE = 0.35  # Distance < 0.35 for automatic proposals
GOOD_MATCH_DISTANCE = 0.60  # Distance < 0.60 for review queue
MIN_CONFIDENCE = 0.6  # Minimum confidence score


def extract_distance_from_comment(comment: str) -> float:
    """Extract cosine distance from SSSOM comment field."""
    match = re.search(r"distance:\s*([\d.]+)", comment)
    if match:
        return float(match.group(1))
    return 1.0  # Max distance if not found


def parse_object_label(label: str) -> tuple[str, str | None]:
    """
    Parse object_label field which may contain label; definition format.

    Returns:
        Tuple of (clean_label, definition_or_none)
    """
    if "; " in label:
        parts = label.split("; ", 1)
        return parts[0].strip(), parts[1].strip()
    return label.strip(), None


def extract_ontology_prefix(iri: str) -> str:
    """Extract ontology prefix from IRI."""
    # Handle obo format
    if "obo/" in iri:
        match = re.search(r"/obo/([A-Z]+)_", iri)
        if match:
            return match.group(1)

    # Handle DOI format
    if "doi.org" in iri:
        return "DOI"

    # Handle other formats
    if "biolink" in iri.lower():
        return "BIOLINK"
    if "dsmz" in iri.lower():
        return "D3O"
    if "mdatahub" in iri.lower():
        return "MEO"

    return "UNKNOWN"


def load_metpo_sheet() -> pd.DataFrame:
    """Load METPO template sheet."""
    df = pd.read_csv(METPO_SHEET, sep="\t", skiprows=1)
    # Column names from actual data
    df.columns = [
        "ID",
        "label",
        "TYPE",
        "parent",
        "description",
        "definition_source",
        "comment",
        "biolink_equivalent",
        "confirmed_exact_synonym",
        "literature_mining_synonyms",
        "madin_synonym",
        "synonym_source_1",
        "bacdive_keyword",
        "synonym_source_2",
        "bactotraits_synonym",
        "synonym_source_3",
        "measurement_unit",
        "range_min",
        "range_max",
        "equivalent_class",
    ]
    return df


def load_sssom_mappings() -> pd.DataFrame:
    """Load SSSOM mapping file, skipping header comments."""
    # Find where actual TSV data starts (after comment lines)
    with Path(SSSOM_FILE).open() as f:
        lines = f.readlines()

    data_start = 0
    for i, line in enumerate(lines):
        if not line.startswith("#"):
            data_start = i
            break

    # Read from data start
    df = pd.read_csv(SSSOM_FILE, sep="\t", skiprows=data_start)

    # Extract distance from comment
    df["distance"] = df["comment"].apply(extract_distance_from_comment)

    # Parse object labels
    df[["clean_object_label", "object_definition"]] = df["object_label"].apply(
        lambda x: pd.Series(parse_object_label(x))
    )

    # Extract ontology prefix
    df["ontology"] = df["object_id"].apply(extract_ontology_prefix)

    return df


def get_best_match_per_term(mappings_df: pd.DataFrame) -> pd.DataFrame:
    """Get the best match for each METPO term (lowest distance)."""
    # Filter to good matches only
    good_matches = mappings_df[mappings_df["distance"] < GOOD_MATCH_DISTANCE].copy()

    # Sort by distance and get first (best) per subject
    best_matches = good_matches.sort_values("distance").groupby("subject_id").first().reset_index()

    return best_matches


def propose_definitions(metpo_df: pd.DataFrame, mappings_df: pd.DataFrame) -> pd.DataFrame:
    """
    Propose definitions for METPO terms without definitions.

    Returns DataFrame with columns:
    - metpo_id
    - metpo_label
    - has_definition (bool)
    - has_def_source (bool)
    - best_match_distance
    - best_match_ontology
    - best_match_label
    - proposed_definition
    - proposed_def_source
    - confidence_level (high/medium/low/none)
    - action_needed
    """
    results = []

    for _, term in metpo_df.iterrows():
        metpo_id = term["ID"]
        metpo_label = term["label"]
        has_definition = pd.notna(term["description"]) and term["description"].strip() != ""
        has_def_source = (
            pd.notna(term["definition_source"]) and term["definition_source"].strip() != ""
        )

        # Get matches for this term
        term_matches = mappings_df[mappings_df["subject_id"] == metpo_id].copy()

        if len(term_matches) == 0:
            results.append(
                {
                    "metpo_id": metpo_id,
                    "metpo_label": metpo_label,
                    "has_definition": has_definition,
                    "has_def_source": has_def_source,
                    "best_match_distance": None,
                    "best_match_ontology": None,
                    "best_match_label": None,
                    "proposed_definition": None,
                    "proposed_def_source": None,
                    "confidence_level": "none",
                    "action_needed": "No matches found - manual definition required",
                }
            )
            continue

        # Sort by distance
        term_matches = term_matches.sort_values("distance")
        best_match = term_matches.iloc[0]

        distance = best_match["distance"]
        ontology = best_match["ontology"]
        match_label = best_match["clean_object_label"]
        match_def = best_match["object_definition"]

        # Determine confidence level
        if distance < HIGH_CONFIDENCE_DISTANCE:
            confidence = "high"
            action = "Auto-propose (distance < 0.35)"
        elif distance < GOOD_MATCH_DISTANCE:
            confidence = "medium"
            action = "Manual review recommended (distance 0.35-0.60)"
        else:
            confidence = "low"
            action = "Low confidence - manual definition preferred"

        # Propose definition source
        if match_def:
            proposed_def = match_def
            proposed_source = f"{ontology}:{best_match['object_id']}"
        else:
            proposed_def = None
            proposed_source = None
            action = f"{action} - but no definition available in match"

        results.append(
            {
                "metpo_id": metpo_id,
                "metpo_label": metpo_label,
                "has_definition": has_definition,
                "has_def_source": has_def_source,
                "best_match_distance": distance,
                "best_match_ontology": ontology,
                "best_match_label": match_label,
                "best_match_iri": best_match["object_id"],
                "proposed_definition": proposed_def,
                "proposed_def_source": proposed_source,
                "confidence_level": confidence,
                "action_needed": action,
            }
        )

    return pd.DataFrame(results)


def generate_cross_references(
    mappings_df: pd.DataFrame, distance_threshold: float = 0.60
) -> pd.DataFrame:
    """
    Generate database cross-references for all METPO terms with good matches.

    Returns DataFrame with columns:
    - metpo_id
    - metpo_label
    - xref_iris (list of IRIs)
    - xref_labels (list of labels)
    - mapping_types (list of skos predicates)
    - distances (list of distances)
    """
    good_matches = mappings_df[mappings_df["distance"] < distance_threshold].copy()

    grouped = (
        good_matches.groupby("subject_id")
        .agg(
            {
                "subject_label": "first",
                "object_id": list,
                "clean_object_label": list,
                "predicate_id": list,
                "distance": list,
                "ontology": list,
            }
        )
        .reset_index()
    )

    grouped.columns = [
        "metpo_id",
        "metpo_label",
        "xref_iris",
        "xref_labels",
        "mapping_types",
        "distances",
        "ontologies",
    ]

    return grouped


def main():
    print("Loading data...")
    metpo_df = load_metpo_sheet()
    mappings_df = load_sssom_mappings()

    print(f"Loaded {len(metpo_df)} METPO terms")
    print(f"Loaded {len(mappings_df)} semantic mappings")

    # Summary statistics
    terms_with_defs = metpo_df["description"].notna().sum()
    terms_without_defs = len(metpo_df) - terms_with_defs
    terms_with_def_source = metpo_df["definition_source"].notna().sum()

    print("\n=== Current Status ===")
    print(
        f"Terms with definitions: {terms_with_defs} ({terms_with_defs / len(metpo_df) * 100:.1f}%)"
    )
    print(
        f"Terms without definitions: {terms_without_defs} ({terms_without_defs / len(metpo_df) * 100:.1f}%)"
    )
    print(
        f"Terms with definition sources: {terms_with_def_source} ({terms_with_def_source / len(metpo_df) * 100:.1f}%)"
    )

    # Propose definitions
    print("\n=== Proposing Definitions ===")
    proposals = propose_definitions(metpo_df, mappings_df)

    # Save full proposal report
    output_file = OUTPUT_DIR / "definition_proposals.tsv"
    proposals.to_csv(output_file, sep="\t", index=False)
    print(f"Saved full proposal report to: {output_file}")

    # Summary by confidence level
    print("\n=== Proposal Summary ===")
    for level in ["high", "medium", "low", "none"]:
        count = len(proposals[proposals["confidence_level"] == level])
        print(f"{level.capitalize()} confidence: {count} terms")

    # High-confidence proposals (distance < 0.35) without definitions
    high_conf = proposals[
        (proposals["confidence_level"] == "high")
        & (~proposals["has_definition"])
        & (proposals["proposed_definition"].notna())
    ]
    print(f"\nHigh-confidence auto-proposals ready: {len(high_conf)}")

    if len(high_conf) > 0:
        high_conf_file = OUTPUT_DIR / "high_confidence_definitions.tsv"
        high_conf.to_csv(high_conf_file, sep="\t", index=False)
        print(f"Saved to: {high_conf_file}")

        # Show sample
        print("\nSample high-confidence proposals:")
        print(
            high_conf[
                [
                    "metpo_id",
                    "metpo_label",
                    "best_match_distance",
                    "best_match_ontology",
                    "proposed_definition",
                ]
            ]
            .head(10)
            .to_string()
        )

    # Generate cross-references
    print("\n=== Generating Cross-References ===")
    xrefs = generate_cross_references(mappings_df, distance_threshold=0.60)
    xref_file = OUTPUT_DIR / "metpo_cross_references.tsv"
    xrefs.to_csv(xref_file, sep="\t", index=False)
    print(f"Saved cross-references to: {xref_file}")
    print(f"Generated xrefs for {len(xrefs)} METPO terms")

    # Terms needing definition sources
    needs_def_source = proposals[
        (proposals["has_definition"])
        & (~proposals["has_def_source"])
        & (proposals["best_match_distance"].notna())
        & (proposals["best_match_distance"] < 0.60)
    ]
    print("\n=== Definition Sources Needed ===")
    print(f"Terms with definitions but no source: {len(needs_def_source)}")

    if len(needs_def_source) > 0:
        def_source_file = OUTPUT_DIR / "definition_sources_needed.tsv"
        needs_def_source.to_csv(def_source_file, sep="\t", index=False)
        print(f"Saved to: {def_source_file}")

    # Final summary
    print("\n=== Action Items ===")
    print(f"1. Review {len(high_conf)} high-confidence definition proposals (distance < 0.35)")
    print(
        f"2. Manually review {len(proposals[proposals['confidence_level'] == 'medium'])} medium-confidence proposals (distance 0.35-0.60)"
    )
    print(f"3. Add definition sources for {len(needs_def_source)} terms")
    print(
        f"4. Create {len(proposals[proposals['confidence_level'] == 'none'])} definitions from scratch (no good matches)"
    )

    print("\n=== Files Generated ===")
    print(f"- {output_file}: Full proposal report")
    if len(high_conf) > 0:
        print(f"- {high_conf_file}: High-confidence proposals")
    print(f"- {xref_file}: Database cross-references")
    if len(needs_def_source) > 0:
        print(f"- {def_source_file}: Terms needing definition sources")


if __name__ == "__main__":
    main()
