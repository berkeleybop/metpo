import click
import pandas as pd

from metpo.cli_common import distance_threshold_option, input_csv_option


@click.command()
@input_csv_option(
    required=False, help_text="Path to the SSSOM TSV file containing METPO term mappings"
)
@distance_threshold_option(
    default=0.9, help_text="Distance threshold below which a match is considered 'good'"
)
def main(input_file: str, distance_threshold: float):
    """Analyzes METPO term match quality from an SSSOM TSV file."""
    input_csv = input_file or "../metpo_relevant_mappings.sssom.tsv"
    good_match_threshold = distance_threshold

    print(f"Loading mappings from: {input_csv}")
    try:
        # Read SSSOM TSV (skip metadata lines starting with #)
        df = pd.read_csv(input_csv, sep="\t", comment="#")
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_csv}")
        return
    except Exception as e:
        print(f"Error loading SSSOM TSV: {e}")
        return

    # Map SSSOM columns to expected column names
    # Calculate distance from similarity_score: distance = 1.0 - similarity_score
    df["distance"] = 1.0 - df["similarity_score"]
    df["metpo_id"] = df["subject_id"]
    df["metpo_label"] = df["subject_label"]
    df["match_document"] = df["object_label"]
    df["match_ontology"] = df["object_source"]

    print(f"Loaded {len(df)} mapping records.")
    print(f"Using good match threshold: {good_match_threshold}")

    # --- Ontology Coverage Score ---
    unique_metpo_terms = df["metpo_id"].nunique()
    print(f"Total unique METPO terms queried: {unique_metpo_terms}")

    # Identify METPO terms with at least one 'good' match
    good_matches_per_term = (
        df[df["distance"] < good_match_threshold].groupby("metpo_id")["distance"].min()
    )
    metpo_terms_with_good_matches = good_matches_per_term.nunique()

    coverage_percentage = (
        (metpo_terms_with_good_matches / unique_metpo_terms) * 100 if unique_metpo_terms > 0 else 0
    )
    print(
        f"METPO terms with at least one 'good' match (distance < {good_match_threshold}): {metpo_terms_with_good_matches}"
    )
    print(f"Ontology Coverage Score: {coverage_percentage:.2f}%")

    # --- Distance Distribution by Ontology Type ---
    print("\n--- Distance Distribution Analysis ---")
    print(f"Overall Mean Distance: {df['distance'].mean():.3f}")
    print(f"Overall Median Distance: {df['distance'].median():.3f}")

    print("\nMean and Median Distance per Ontology:")
    distance_by_ontology = (
        df.groupby("match_ontology")["distance"].agg(["mean", "median"]).sort_values("mean")
    )
    print(distance_by_ontology.to_string())

    print("\n--- Top 5 METPO terms with best matches ---")
    # Get the best match for each METPO term
    best_matches = df.loc[df.groupby("metpo_id")["distance"].idxmin()]
    # Sort by distance and show top 5
    print(
        best_matches[["metpo_label", "match_document", "match_ontology", "distance"]]
        .head(5)
        .to_string(index=False)
    )

    print("\n--- Top 5 METPO terms with worst matches ---")
    # Sort by distance and show worst 5
    print(
        best_matches[["metpo_label", "match_document", "match_ontology", "distance"]]
        .tail(5)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
