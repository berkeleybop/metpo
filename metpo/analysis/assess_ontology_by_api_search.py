"""
Phase 1 Batch Search: METPO Label Discovery

Searches METPO class labels through OLS4 and BioPortal APIs to discover
which ontologies have the best label alignment with METPO. This is a bootstrap
discovery phase - no filtering applied, let the data reveal patterns.

Output files:
- phase1_raw_results.tsv: All search results with similarity scores
- phase1_high_quality_matches.tsv: Results with similarity >= 0.5
- phase1_summary_stats.json: Summary statistics
- phase1_ontology_rankings.tsv: Ontologies ranked by high-quality match count
"""

import json
import os
import sys
import time
from pathlib import Path

import click
import Levenshtein
import pandas as pd
import requests
from dotenv import load_dotenv


def search_ols(label, rows=75):
    """Search OLS4 for a label"""
    url = "https://www.ebi.ac.uk/ols4/api/search"
    params = {"q": label, "type": "class", "rows": rows}

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            docs = data.get("response", {}).get("docs", [])
            return [
                {
                    "label": d.get("label"),
                    "iri": d.get("iri"),
                    "ontology": d.get("ontology_name"),
                    "definition": d.get("description", [""])[0] if d.get("description") else "",
                }
                for d in docs
            ]
        return []
    except Exception as e:
        print(f"  ⚠️  OLS error for '{label}': {e}")
        return []


def search_bioportal(label, api_key, pagesize=75):
    """Search BioPortal for a label"""
    url = "https://data.bioontology.org/search"
    params = {"q": label, "pagesize": pagesize}
    headers = {}

    if api_key:
        headers["Authorization"] = f"apikey token={api_key}"

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            collection = data.get("collection", [])
            results = []
            for item in collection:
                ontology_url = item.get("links", {}).get("ontology", "")
                ontology = ontology_url.split("/")[-1] if ontology_url else "unknown"

                results.append(
                    {
                        "label": item.get("prefLabel"),
                        "iri": item.get("@id"),
                        "ontology": ontology,
                        "definition": item.get("definition", [""])[0]
                        if isinstance(item.get("definition"), list)
                        else item.get("definition", ""),
                    }
                )
            return results
        return []
    except Exception as e:
        print(f"  ⚠️  BioPortal error for '{label}': {e}")
        return []


def calculate_similarity(metpo_label, match_label):
    """Calculate Levenshtein distance and similarity ratio"""
    if pd.isna(match_label):
        return None, None

    str1 = str(metpo_label).lower()
    str2 = str(match_label).lower()

    distance = Levenshtein.distance(str1, str2)
    ratio = Levenshtein.ratio(str1, str2)

    return distance, ratio


@click.command()
@click.option(
    "--input-file",
    "-i",
    type=click.Path(exists=True, path_type=Path),
    default="data/metpo_terms/metpo_all_labels.tsv",
    help="Input TSV file with METPO IDs and labels (2 columns: metpo_id, metpo_label)",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    default="data/ontology_assessments",
    help="Output directory for results",
)
@click.option(
    "--ols-rows",
    type=int,
    default=75,
    help="Number of results to request from OLS API per query",
)
@click.option(
    "--bioportal-pagesize",
    type=int,
    default=75,
    help="Number of results to request from BioPortal API per query",
)
@click.option(
    "--rate-limit",
    type=float,
    default=1.0,
    help="Rate limiting delay in seconds between API calls",
)
@click.option(
    "--similarity-threshold",
    type=float,
    default=0.5,
    help="Minimum similarity ratio for high-quality matches (0.0-1.0)",
)
def main(
    input_file: Path,
    output_dir: Path,
    ols_rows: int,
    bioportal_pagesize: int,
    rate_limit: float,
    similarity_threshold: float,
):
    """
    Search METPO class labels through OLS4 and BioPortal APIs to discover
    which ontologies have the best label alignment with METPO.

    Outputs:
    - phase1_raw_results.tsv: All search results with similarity scores
    - phase1_high_quality_matches.tsv: Results with similarity >= threshold
    - phase1_summary_stats.json: Summary statistics
    - phase1_ontology_rankings.tsv: Ontologies ranked by high-quality match count
    """
    # Load environment variables
    load_dotenv()
    bioportal_api_key = os.getenv("BIOPORTAL_API_KEY")

    if not bioportal_api_key:
        click.echo("⚠️  Warning: BIOPORTAL_API_KEY not set in environment")
        click.echo("   BioPortal searches may fail")
    else:
        click.echo("✓ BioPortal API key loaded")

    print("\n" + "=" * 70)
    print("Phase 1 Batch Search: METPO Label Discovery")
    print("=" * 70 + "\n")

    # Load METPO labels
    if not input_file.exists():
        click.echo(f"❌ Error: Input file not found at {input_file}", err=True)
        sys.exit(1)

    metpo_df = pd.read_csv(input_file, sep="\t", names=["metpo_id", "metpo_label"])
    print(f"✓ Loaded {len(metpo_df)} METPO labels\n")
    print(f"Estimated runtime: ~{len(metpo_df) * 2 * rate_limit / 60:.1f} minutes")
    print(f"  - {ols_rows} results from OLS per query")
    print(f"  - {bioportal_pagesize} results from BioPortal per query")
    print(f"  - {rate_limit}s rate limiting between API calls\n")

    # Run batch search
    all_results = []
    start_time = time.time()

    for idx, row in metpo_df.iterrows():
        metpo_id = row["metpo_id"]
        metpo_label = row["metpo_label"]

        print(f"[{idx + 1}/{len(metpo_df)}] {metpo_label}")

        # Search OLS
        ols_results = search_ols(metpo_label, rows=ols_rows)
        print(f"  OLS: {len(ols_results)} results")

        for result in ols_results:
            all_results.append(
                {
                    "metpo_id": metpo_id,
                    "metpo_label": metpo_label,
                    "source": "OLS",
                    "match_label": result["label"],
                    "match_iri": result["iri"],
                    "match_ontology": result["ontology"],
                    "match_definition": result["definition"],
                }
            )

        # Rate limiting between API calls
        time.sleep(rate_limit)

        # Search BioPortal
        bp_results = search_bioportal(metpo_label, bioportal_api_key, pagesize=bioportal_pagesize)
        print(f"  BioPortal: {len(bp_results)} results")

        for result in bp_results:
            all_results.append(
                {
                    "metpo_id": metpo_id,
                    "metpo_label": metpo_label,
                    "source": "BioPortal",
                    "match_label": result["label"],
                    "match_iri": result["iri"],
                    "match_ontology": result["ontology"],
                    "match_definition": result["definition"],
                }
            )

        # Rate limiting between METPO terms
        time.sleep(rate_limit)

    elapsed = time.time() - start_time
    print(f"\n✓ Search complete: {len(all_results)} total results in {elapsed / 60:.1f} minutes\n")

    # Convert to DataFrame and calculate string distances
    print("Calculating string similarity scores...")
    results_df = pd.DataFrame(all_results)

    results_df["levenshtein_distance"] = results_df.apply(
        lambda row: calculate_similarity(row["metpo_label"], row["match_label"])[0], axis=1
    )

    results_df["similarity_ratio"] = results_df.apply(
        lambda row: calculate_similarity(row["metpo_label"], row["match_label"])[1], axis=1
    )

    print("✓ Calculated similarity scores\n")
    print("Similarity statistics:")
    print(results_df["similarity_ratio"].describe())
    print()

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save raw results
    raw_output = output_dir / "phase1_raw_results.tsv"
    results_df.to_csv(raw_output, sep="\t", index=False)
    print(f"✓ Saved raw results to {raw_output}")

    # Save high-quality matches
    high_quality = results_df[results_df["similarity_ratio"] >= similarity_threshold]
    hq_output = output_dir / "phase1_high_quality_matches.tsv"
    high_quality.to_csv(hq_output, sep="\t", index=False)
    print(f"✓ Saved high-quality matches (similarity ≥ {similarity_threshold}) to {hq_output}")

    # Analyze ontology rankings by high-quality matches
    hq_ontology_counts = high_quality["match_ontology"].value_counts()
    ontology_rankings = pd.DataFrame(
        {"ontology": hq_ontology_counts.index, "high_quality_matches": hq_ontology_counts.values}
    )

    # Add average similarity by ontology
    avg_similarity = results_df.groupby("match_ontology")["similarity_ratio"].mean()
    ontology_rankings["avg_similarity"] = ontology_rankings["ontology"].map(avg_similarity)

    # Add total matches
    total_matches = results_df["match_ontology"].value_counts()
    ontology_rankings["total_matches"] = ontology_rankings["ontology"].map(total_matches)

    # Sort by high-quality matches
    ontology_rankings = ontology_rankings.sort_values("high_quality_matches", ascending=False)

    rankings_output = output_dir / "phase1_ontology_rankings.tsv"
    ontology_rankings.to_csv(rankings_output, sep="\t", index=False)
    print(f"✓ Saved ontology rankings to {rankings_output}")

    # Save summary statistics
    summary_stats = {
        "total_metpo_terms": len(metpo_df),
        "total_results": len(results_df),
        "high_quality_results": len(high_quality),
        "high_quality_threshold": similarity_threshold,
        "unique_ontologies": results_df["match_ontology"].nunique(),
        "avg_similarity": float(results_df["similarity_ratio"].mean()),
        "median_similarity": float(results_df["similarity_ratio"].median()),
        "top_10_ontologies": ontology_rankings.head(10).to_dict("records"),
        "runtime_minutes": elapsed / 60,
    }

    summary_output = output_dir / "phase1_summary_stats.json"
    with Path(summary_output).open("w") as f:
        json.dump(summary_stats, f, indent=2)
    print(f"✓ Saved summary statistics to {summary_output}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total METPO terms searched: {len(metpo_df)}")
    print(f"Total results found: {len(results_df)}")
    print(
        f"High-quality matches (≥{similarity_threshold}): {len(high_quality)} ({len(high_quality) / len(results_df) * 100:.1f}%)"
    )
    print(f"Unique ontologies found: {results_df['match_ontology'].nunique()}")
    print(f"Average similarity: {results_df['similarity_ratio'].mean():.3f}")
    print(f"Median similarity: {results_df['similarity_ratio'].median():.3f}")
    print("\nTop 10 ontologies by high-quality matches:")
    for _i, row in ontology_rankings.head(10).iterrows():
        print(
            f"  {row['ontology']:20s} {int(row['high_quality_matches']):4d} HQ matches, {row['avg_similarity']:.3f} avg similarity"
        )
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
