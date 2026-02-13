"""
Analyze PRIMARY SOURCES ONLY - NO MARKDOWN DOCUMENTATION

Primary sources:
1. ChromaDB SQLite databases (actual embeddings)
2. SSSOM mapping files (.sssom.tsv)
3. KG-Microbe transformed TSV files
"""

import csv
import sqlite3
from collections import Counter
from pathlib import Path

from metpo.utils.sssom_utils import extract_prefix, parse_sssom_curie_map

# PRIMARY SOURCE 1: ChromaDB databases
CHROMA_COMBINED = Path("/home/mark/gitrepos/metpo/notebooks/chroma_combined/chroma.sqlite3")
CHROMA_OLS_20 = Path("/home/mark/gitrepos/metpo/notebooks/chroma_ols_20/chroma.sqlite3")
CHROMA_NONOLS_4 = Path("/home/mark/gitrepos/metpo/notebooks/chroma_nonols_4/chroma.sqlite3")

# PRIMARY SOURCE 2: SSSOM mappings
SSSOM_RELAXED = Path(
    "/home/mark/gitrepos/metpo/data/mappings/metpo_mappings_combined_relaxed.sssom.tsv"
)
SSSOM_OPTIMIZED = Path("/home/mark/gitrepos/metpo/data/mappings/metpo_mappings_optimized.sssom.tsv")


def query_chromadb(db_path, description):
    """Query a ChromaDB SQLite database for ontology statistics"""
    print(f"\n=== {description} ===")
    print(f"Source: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Total embeddings
    cursor.execute("SELECT COUNT(*) FROM embeddings")
    total = cursor.fetchone()[0]
    print(f"Total embeddings: {total:,}")

    # Ontologies
    cursor.execute("""
        SELECT string_value as ontology, COUNT(*) as count
        FROM embedding_metadata
        WHERE key = 'ontologyId'
        GROUP BY string_value
        ORDER BY count DESC
    """)

    ontologies = cursor.fetchall()
    print(f"Unique ontologies: {len(ontologies)}")
    print("\nTop 20 by embedding count:")
    for ont, count in ontologies[:20]:
        pct = (count / total * 100) if total > 0 else 0
        print(f"  {ont:<15} {count:>8,} ({pct:5.1f}%)")

    conn.close()
    return ontologies, total


def analyze_sssom(sssom_path):
    """Analyze SSSOM mapping file PRIMARY SOURCE"""
    print("\n=== SSSOM Mappings ===")
    print(f"Source: {sssom_path}")

    target_prefixes = Counter()
    predicates = Counter()
    total_mappings = 0
    curie_map = parse_sssom_curie_map(sssom_path)

    with Path(sssom_path).open() as f:
        data_lines = [line for line in f if not line.startswith("#")]
        reader = csv.DictReader(data_lines, delimiter="\t")
        for row in reader:
            total_mappings += 1

            # Extract prefix from object_id
            prefix = extract_prefix(row.get("object_id", ""), curie_map)
            if prefix:
                target_prefixes[prefix.upper()] += 1

            pred = row.get("predicate_id", "")
            predicates[pred] += 1

    print(f"Total mappings: {total_mappings:,}")
    print("\nTop 20 target ontologies:")
    for prefix, count in target_prefixes.most_common(20):
        print(f"  {prefix:<15} {count:>6}")

    print("\nMapping types:")
    for pred, count in predicates.most_common():
        pred_name = pred.split("/")[-1] if "/" in pred else pred
        print(f"  {pred_name:<30} {count:>6}")

    return target_prefixes, predicates, total_mappings


def main():
    print("=" * 80)
    print("PRIMARY SOURCE ANALYSIS - ChromaDB + SSSOM")
    print("NO MARKDOWN DOCUMENTATION - ONLY RAW DATA")
    print("=" * 80)

    # Analyze ChromaDB databases
    print("\n" + "=" * 80)
    print("PRIMARY SOURCE 1: ChromaDB SQLite Databases")
    print("=" * 80)

    combined_onts, combined_total = query_chromadb(
        CHROMA_COMBINED, "Combined ChromaDB (All 39 ontologies tested)"
    )
    ols20_onts, ols20_total = query_chromadb(CHROMA_OLS_20, "Filtered OLS-20 ChromaDB")
    nonols_onts, nonols_total = query_chromadb(CHROMA_NONOLS_4, "Non-OLS 4 ChromaDB")

    # Analyze SSSOM mappings
    print("\n" + "=" * 80)
    print("PRIMARY SOURCE 2: SSSOM Mapping Files")
    print("=" * 80)

    print("\n--- Relaxed Mappings (distance < 0.80) ---")
    relaxed_targets, _relaxed_preds, relaxed_total = analyze_sssom(SSSOM_RELAXED)

    print("\n--- Optimized Mappings (tighter thresholds) ---")
    _opt_targets, _opt_preds, opt_total = analyze_sssom(SSSOM_OPTIMIZED)

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY FROM PRIMARY SOURCES")
    print("=" * 80)

    print("\nChromaDB Ontology Counts (from SQLite queries):")
    print(f"  Combined (tested): {len(combined_onts)} ontologies, {combined_total:,} embeddings")
    print(f"  OLS-20 (filtered): {len(ols20_onts)} ontologies, {ols20_total:,} embeddings")
    print(f"  Non-OLS-4: {len(nonols_onts)} ontologies, {nonols_total:,} embeddings")

    print("\nSSOM Mappings (from TSV files):")
    print(f"  Relaxed: {relaxed_total:,} mappings")
    print(f"  Optimized: {opt_total:,} mappings")

    print(f"\nUnique target ontologies in SSSOM (relaxed): {len(relaxed_targets)}")

    # Which ontologies in ChromaDB OLS-20?
    ols20_names = [ont[0] for ont in ols20_onts]
    print("\nOLS-20 ontologies (from ChromaDB query):")
    print(f"  {', '.join(ols20_names)}")

    # Which in non-OLS?
    nonols_names = [ont[0] for ont in nonols_onts]
    print("\nNon-OLS-4 ontologies (from ChromaDB query):")
    print(f"  {', '.join(nonols_names)}")

    print("\n" + "=" * 80)
    print("ALL DATA EXTRACTED FROM PRIMARY SOURCES:")
    print("  - ChromaDB SQLite databases (direct SQL queries)")
    print("  - SSSOM .tsv files (direct parsing)")
    print("  - NO markdown documentation used")
    print("=" * 80)


if __name__ == "__main__":
    main()
