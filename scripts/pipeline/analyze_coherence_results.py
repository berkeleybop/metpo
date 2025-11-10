"""
Analyze coherence results to find METPO classes with strong external alignment.

Looks for cases where:
1. High coherence (>0.5): Most METPO siblings match external siblings
2. Low distance (<0.5): Good semantic similarity
3. Multiple siblings: Enough structure to be meaningful
"""
import pandas as pd
import click


@click.command()
@click.option('--results-csv', default='../data/coherence/sibling_coherence_analysis_output.csv', help='Coherence results CSV')
@click.option('--matches-csv', default='../data/mappings/metpo_mappings_combined_relaxed.sssom.tsv', help='SSSOM TSV mappings file')
def main(results_csv: str, matches_csv: str):
    """Analyze coherence results to find strong alignments."""

    print("Loading data...")
    coherence_df = pd.read_csv(results_csv)

    # Load SSSOM TSV mappings
    matches_df = pd.read_csv(matches_csv, sep='\t', comment='#')
    # Map SSSOM columns to expected column names
    matches_df['distance'] = 1.0 - matches_df['similarity_score']
    matches_df['metpo_id'] = matches_df['subject_id']
    matches_df['metpo_label'] = matches_df['subject_label']
    matches_df['match_document'] = matches_df['object_label']
    matches_df['match_ontology'] = matches_df['object_source']

    # Filter for meaningful cases
    # - Has siblings (at least 3 for meaningful structure)
    # - Has external siblings retrieved
    # - Has coherence score
    meaningful = coherence_df[
        (coherence_df['metpo_sibling_count'] >= 3) &
        (coherence_df['external_sibling_count'] > 0) &
        (coherence_df['coherence_score'].notna())
    ].copy()

    print(f"\nFiltered to {len(meaningful)} terms with meaningful structure (≥3 siblings)")

    # === HIGH COHERENCE CASES ===
    print("\n" + "="*80)
    print("HIGH COHERENCE CASES (≥0.5): METPO structure aligns with external ontology")
    print("="*80)

    high_coherence = meaningful[meaningful['coherence_score'] >= 0.5].sort_values(
        'coherence_score', ascending=False
    )

    if len(high_coherence) > 0:
        print(f"\nFound {len(high_coherence)} high-coherence terms:\n")
        for idx, row in high_coherence.iterrows():
            print(f"{'='*80}")
            print(f"METPO: {row['metpo_label']} ({row['metpo_id']})")
            print(f"  → External: {row['match_ontology']} {row['match_iri']}")
            print(f"  Match quality: distance = {row['match_distance']:.3f}")
            print(f"  Coherence: {row['coherence_score']:.1%} ({row['coherent_sibling_count']}/{row['metpo_sibling_count']} siblings align)")
            print(f"  External has {row['external_sibling_count']} siblings")

            # Show which siblings matched
            metpo_id = row['metpo_id']
            all_matches = matches_df[matches_df['metpo_id'] == metpo_id].nsmallest(10, 'distance')
            if len(all_matches) > 1:
                print(f"\n  Top matches for this term:")
                for _, match in all_matches.head(5).iterrows():
                    print(f"    {match['match_document'][:50]:50} ({match['match_ontology']:8}) dist={match['distance']:.3f}")
    else:
        print("\n  No high-coherence cases found.")

    # === MODERATE COHERENCE ===
    print("\n" + "="*80)
    print("MODERATE COHERENCE CASES (0.3-0.5): Partial alignment")
    print("="*80)

    moderate = meaningful[
        (meaningful['coherence_score'] >= 0.3) &
        (meaningful['coherence_score'] < 0.5)
    ].sort_values('coherence_score', ascending=False)

    if len(moderate) > 0:
        print(f"\nFound {len(moderate)} moderate-coherence terms (showing top 10):\n")
        for idx, row in moderate.head(10).iterrows():
            print(f"{row['metpo_label']:30} → {row['match_ontology']:10} "
                  f"coherence={row['coherence_score']:.1%} "
                  f"({row['coherent_sibling_count']}/{row['metpo_sibling_count']}) "
                  f"dist={row['match_distance']:.3f}")
    else:
        print("\n  No moderate-coherence cases found.")

    # === ANALYSIS BY ONTOLOGY ===
    print("\n" + "="*80)
    print("COHERENCE BY ONTOLOGY: Which ontologies align best with METPO?")
    print("="*80)

    ontology_stats = meaningful.groupby('match_ontology').agg({
        'coherence_score': ['mean', 'median', 'count'],
        'match_distance': ['mean', 'median']
    }).round(3)
    ontology_stats.columns = ['_'.join(col).strip() for col in ontology_stats.columns]
    ontology_stats = ontology_stats.sort_values('coherence_score_mean', ascending=False)

    print("\n", ontology_stats.to_string())

    # === BEST CANDIDATES FOR ALIGNMENT ===
    print("\n" + "="*80)
    print("BEST ALIGNMENT CANDIDATES: High coherence + Low distance")
    print("="*80)

    # Score = coherence * (1 - distance) to balance both factors
    meaningful['alignment_score'] = meaningful['coherence_score'] * (1 - meaningful['match_distance'])
    best_candidates = meaningful.nlargest(20, 'alignment_score')

    print(f"\nTop 20 candidates for importing/aligning with external ontologies:\n")
    print(f"{'Rank':<5} {'METPO Term':<35} {'Ontology':<10} {'Coherence':<12} {'Distance':<10} {'Score':<8}")
    print("-" * 90)

    for rank, (idx, row) in enumerate(best_candidates.iterrows(), 1):
        print(f"{rank:<5} {row['metpo_label'][:33]:<35} {row['match_ontology']:<10} "
              f"{row['coherence_score']:>6.1%} ({row['coherent_sibling_count']:>2}/{row['metpo_sibling_count']:<2}) "
              f"{row['match_distance']:>8.3f} {row['alignment_score']:>8.3f}")

    # Save candidates
    candidates_file = 'alignment_candidates.csv'
    best_candidates.to_csv(candidates_file, index=False)
    print(f"\n✓ Saved top candidates to: {candidates_file}")


if __name__ == "__main__":
    main()
