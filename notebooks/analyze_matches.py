import pandas as pd
import click

@click.command()
@click.option(
    '--input-csv',
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    default='../metpo_relevant_matches.csv',
    help="Path to the input CSV file containing METPO term matches."
)
@click.option(
    '--good-match-threshold',
    type=float,
    default=0.9,
    help="Distance threshold below which a match is considered 'good'."
)
def main(input_csv: str, good_match_threshold: float):
    """
    Analyzes METPO term match quality from a CSV file.
    """
    print(f"Loading matches from: {input_csv}")
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: Input CSV file not found at {input_csv}")
        return
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    print(f"Loaded {len(df)} match records.")
    print(f"Using good match threshold: {good_match_threshold}")

    # --- Ontology Coverage Score ---
    unique_metpo_terms = df['metpo_id'].nunique()
    print(f"Total unique METPO terms queried: {unique_metpo_terms}")

    # Identify METPO terms with at least one 'good' match
    good_matches_per_term = df[df['distance'] < good_match_threshold].groupby('metpo_id')['distance'].min()
    metpo_terms_with_good_matches = good_matches_per_term.nunique()

    coverage_percentage = (metpo_terms_with_good_matches / unique_metpo_terms) * 100 if unique_metpo_terms > 0 else 0
    print(f"METPO terms with at least one 'good' match (distance < {good_match_threshold}): {metpo_terms_with_good_matches}")
    print(f"Ontology Coverage Score: {coverage_percentage:.2f}%")

    # --- Distance Distribution by Ontology Type ---
    print("\n--- Distance Distribution Analysis ---")
    print(f"Overall Mean Distance: {df['distance'].mean():.3f}")
    print(f"Overall Median Distance: {df['distance'].median():.3f}")

    print("\nMean and Median Distance per Ontology:")
    distance_by_ontology = df.groupby('match_ontology')['distance'].agg(['mean', 'median']).sort_values('mean')
    print(distance_by_ontology.to_string())

    print("\n--- Top 5 METPO terms with best matches ---")
    # Get the best match for each METPO term
    best_matches = df.loc[df.groupby('metpo_id')['distance'].idxmin()]
    # Sort by distance and show top 5
    print(best_matches[['metpo_label', 'match_document', 'match_ontology', 'distance']].head(5).to_string(index=False))

    print("\n--- Top 5 METPO terms with worst matches ---")
    # Sort by distance and show worst 5
    print(best_matches[['metpo_label', 'match_document', 'match_ontology', 'distance']].tail(5).to_string(index=False))


if __name__ == "__main__":
    main()
