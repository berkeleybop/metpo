#!/usr/bin/env python3
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

import requests
import json
import os
import pandas as pd
import time
from pathlib import Path
from dotenv import load_dotenv
import Levenshtein
from collections import Counter
import sys

# Configuration
SAMPLE_FILE = "../../data/metpo_terms/metpo_all_labels.tsv"
OUTPUT_DIR = Path(".")
OLS_ROWS = 75
BIOPORTAL_PAGESIZE = 75
RATE_LIMIT_SLEEP = 1.0  # seconds
HIGH_QUALITY_THRESHOLD = 0.5

# Load environment variables
env_path = Path("..") / ".env"
load_dotenv(dotenv_path=env_path)
BIOPORTAL_API_KEY = os.getenv("BIOPORTAL_API_KEY")

if not BIOPORTAL_API_KEY:
    print("⚠️  Warning: BIOPORTAL_API_KEY not set in .env file")
    print("   BioPortal searches may fail")
else:
    print("✓ BioPortal API key loaded")


def search_ols(label, rows=OLS_ROWS):
    """Search OLS4 for a label"""
    url = "https://www.ebi.ac.uk/ols4/api/search"
    params = {"q": label, "type": "class", "rows": rows}

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            docs = data.get("response", {}).get("docs", [])
            return [{
                "label": d.get("label"),
                "iri": d.get("iri"),
                "ontology": d.get("ontology_name"),
                "definition": d.get("description", [""])[0] if d.get("description") else ""
            } for d in docs]
        return []
    except Exception as e:
        print(f"  ⚠️  OLS error for '{label}': {e}")
        return []


def search_bioportal(label, api_key, pagesize=BIOPORTAL_PAGESIZE):
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

                results.append({
                    "label": item.get("prefLabel"),
                    "iri": item.get("@id"),
                    "ontology": ontology,
                    "definition": item.get("definition", [""])[0] if isinstance(item.get("definition"), list) else item.get("definition", "")
                })
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


def main():
    print("\n" + "="*70)
    print("Phase 1 Batch Search: METPO Label Discovery")
    print("="*70 + "\n")

    # Load METPO sample labels
    sample_path = OUTPUT_DIR / SAMPLE_FILE
    if not sample_path.exists():
        print(f"❌ Error: Sample file not found at {sample_path}")
        print(f"   Please create it first using:")
        print(f"   awk -F'\\t' 'NR>2 {{print $1 \"\\t\" $2}}' ../src/templates/metpo_sheet.tsv | grep \"^METPO:\" | shuf -n 50 > {SAMPLE_FILE}")
        sys.exit(1)

    metpo_df = pd.read_csv(sample_path, sep="\t", names=["metpo_id", "metpo_label"])
    print(f"✓ Loaded {len(metpo_df)} METPO labels (20% sample)\n")
    print(f"Estimated runtime: ~{len(metpo_df) * 2 * RATE_LIMIT_SLEEP / 60:.1f} minutes")
    print(f"  - {OLS_ROWS} results from OLS per query")
    print(f"  - {BIOPORTAL_PAGESIZE} results from BioPortal per query")
    print(f"  - {RATE_LIMIT_SLEEP}s rate limiting between API calls\n")

    # Run batch search
    all_results = []
    start_time = time.time()

    for idx, row in metpo_df.iterrows():
        metpo_id = row["metpo_id"]
        metpo_label = row["metpo_label"]

        print(f"[{idx+1}/{len(metpo_df)}] {metpo_label}")

        # Search OLS
        ols_results = search_ols(metpo_label)
        print(f"  OLS: {len(ols_results)} results")

        for result in ols_results:
            all_results.append({
                "metpo_id": metpo_id,
                "metpo_label": metpo_label,
                "source": "OLS",
                "match_label": result["label"],
                "match_iri": result["iri"],
                "match_ontology": result["ontology"],
                "match_definition": result["definition"]
            })

        # Rate limiting between API calls
        time.sleep(RATE_LIMIT_SLEEP)

        # Search BioPortal
        bp_results = search_bioportal(metpo_label, BIOPORTAL_API_KEY)
        print(f"  BioPortal: {len(bp_results)} results")

        for result in bp_results:
            all_results.append({
                "metpo_id": metpo_id,
                "metpo_label": metpo_label,
                "source": "BioPortal",
                "match_label": result["label"],
                "match_iri": result["iri"],
                "match_ontology": result["ontology"],
                "match_definition": result["definition"]
            })

        # Rate limiting between METPO terms
        time.sleep(RATE_LIMIT_SLEEP)

    elapsed = time.time() - start_time
    print(f"\n✓ Search complete: {len(all_results)} total results in {elapsed/60:.1f} minutes\n")

    # Convert to DataFrame and calculate string distances
    print("Calculating string similarity scores...")
    results_df = pd.DataFrame(all_results)

    results_df["levenshtein_distance"] = results_df.apply(
        lambda row: calculate_similarity(row["metpo_label"], row["match_label"])[0],
        axis=1
    )

    results_df["similarity_ratio"] = results_df.apply(
        lambda row: calculate_similarity(row["metpo_label"], row["match_label"])[1],
        axis=1
    )

    print(f"✓ Calculated similarity scores\n")
    print("Similarity statistics:")
    print(results_df["similarity_ratio"].describe())
    print()

    # Save raw results
    raw_output = OUTPUT_DIR / "phase1_raw_results.tsv"
    results_df.to_csv(raw_output, sep="\t", index=False)
    print(f"✓ Saved raw results to {raw_output}")

    # Save high-quality matches
    high_quality = results_df[results_df["similarity_ratio"] >= HIGH_QUALITY_THRESHOLD]
    hq_output = OUTPUT_DIR / "phase1_high_quality_matches.tsv"
    high_quality.to_csv(hq_output, sep="\t", index=False)
    print(f"✓ Saved high-quality matches (similarity ≥ {HIGH_QUALITY_THRESHOLD}) to {hq_output}")

    # Analyze ontology rankings by high-quality matches
    hq_ontology_counts = high_quality["match_ontology"].value_counts()
    ontology_rankings = pd.DataFrame({
        "ontology": hq_ontology_counts.index,
        "high_quality_matches": hq_ontology_counts.values
    })

    # Add average similarity by ontology
    avg_similarity = results_df.groupby("match_ontology")["similarity_ratio"].mean()
    ontology_rankings["avg_similarity"] = ontology_rankings["ontology"].map(avg_similarity)

    # Add total matches
    total_matches = results_df["match_ontology"].value_counts()
    ontology_rankings["total_matches"] = ontology_rankings["ontology"].map(total_matches)

    # Sort by high-quality matches
    ontology_rankings = ontology_rankings.sort_values("high_quality_matches", ascending=False)

    rankings_output = OUTPUT_DIR / "phase1_ontology_rankings.tsv"
    ontology_rankings.to_csv(rankings_output, sep="\t", index=False)
    print(f"✓ Saved ontology rankings to {rankings_output}")

    # Save summary statistics
    summary_stats = {
        "total_metpo_terms": len(metpo_df),
        "total_results": len(results_df),
        "high_quality_results": len(high_quality),
        "high_quality_threshold": HIGH_QUALITY_THRESHOLD,
        "unique_ontologies": results_df["match_ontology"].nunique(),
        "avg_similarity": float(results_df["similarity_ratio"].mean()),
        "median_similarity": float(results_df["similarity_ratio"].median()),
        "top_10_ontologies": ontology_rankings.head(10).to_dict('records'),
        "runtime_minutes": elapsed / 60
    }

    summary_output = OUTPUT_DIR / "phase1_summary_stats.json"
    with open(summary_output, "w") as f:
        json.dump(summary_stats, f, indent=2)
    print(f"✓ Saved summary statistics to {summary_output}")

    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total METPO terms searched: {len(metpo_df)}")
    print(f"Total results found: {len(results_df)}")
    print(f"High-quality matches (≥{HIGH_QUALITY_THRESHOLD}): {len(high_quality)} ({len(high_quality)/len(results_df)*100:.1f}%)")
    print(f"Unique ontologies found: {results_df['match_ontology'].nunique()}")
    print(f"Average similarity: {results_df['similarity_ratio'].mean():.3f}")
    print(f"Median similarity: {results_df['similarity_ratio'].median():.3f}")
    print(f"\nTop 10 ontologies by high-quality matches:")
    for i, row in ontology_rankings.head(10).iterrows():
        print(f"  {row['ontology']:20s} {int(row['high_quality_matches']):4d} HQ matches, {row['avg_similarity']:.3f} avg similarity")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
