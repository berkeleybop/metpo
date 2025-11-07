#!/usr/bin/env python3
"""
Analyze Madin et al data and METPO usage - 100% TRACEABLE
Primary sources:
- /home/mark/gitrepos/kg-microbe/data/raw/madin_etal.csv
- /home/mark/gitrepos/kg-microbe/data/transformed/madin_etal/edges.tsv
- /home/mark/gitrepos/kg-microbe/data/transformed/madin_etal/nodes.tsv
"""
import csv
import sys
from pathlib import Path
from collections import Counter, defaultdict

# Primary source files
RAW_FILE = Path("/home/mark/gitrepos/kg-microbe/data/raw/madin_etal.csv")
TRANSFORMED_EDGES = Path("/home/mark/gitrepos/kg-microbe/data/transformed/madin_etal/edges.tsv")
TRANSFORMED_NODES = Path("/home/mark/gitrepos/kg-microbe/data/transformed/madin_etal/nodes.tsv")

def analyze_raw_madin():
    """Analyze the raw Madin et al CSV file"""
    if not RAW_FILE.exists():
        print(f"ERROR: Raw file not found: {RAW_FILE}")
        return None

    print(f"\n=== Madin et al Raw Data Analysis ===")
    print(f"Source: {RAW_FILE}")

    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        total_records = 0
        trait_coverage = defaultdict(int)
        data_sources = Counter()
        domains = Counter()

        for row in reader:
            total_records += 1

            # Count data sources
            source = row.get('data_source', '')
            if source:
                data_sources[source] += 1

            # Count domains (superkingdom)
            domain = row.get('superkingdom', '')
            if domain:
                domains[domain] += 1

            # Check which traits are present (non-empty, not NA)
            for key, value in row.items():
                if value and value.strip() and value.strip().upper() != 'NA':
                    trait_coverage[key] += 1

        print(f"\nTotal records: {total_records:,}")

        print(f"\nData sources:")
        for source, count in data_sources.most_common():
            pct = (count / total_records) * 100
            print(f"  {source:30s}: {count:8,} ({pct:5.1f}%)")

        print(f"\nDomains (superkingdom):")
        for domain, count in domains.most_common():
            pct = (count / total_records) * 100
            print(f"  {domain:30s}: {count:8,} ({pct:5.1f}%)")

        print(f"\nTop 25 traits by coverage:")
        for trait, count in sorted(trait_coverage.items(), key=lambda x: x[1], reverse=True)[:25]:
            pct = (count / total_records) * 100
            print(f"  {trait:30s}: {count:8,} ({pct:5.1f}%)")

        return {
            'total_records': total_records,
            'trait_coverage': trait_coverage,
            'data_sources': data_sources,
            'domains': domains
        }

def analyze_transformed_madin():
    """Analyze METPO usage in transformed Madin et al data"""
    if not TRANSFORMED_EDGES.exists():
        print(f"ERROR: Transformed edges not found: {TRANSFORMED_EDGES}")
        return None

    print(f"\n=== Madin et al Transformed Data (METPO Usage) ===")
    print(f"Source: {TRANSFORMED_EDGES}")

    metpo_objects = []
    total_edges = 0
    metpo_edges = 0
    predicate_counter = Counter()

    with open(TRANSFORMED_EDGES, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            total_edges += 1
            obj = row.get('object', '')
            pred = row.get('predicate', '')

            predicate_counter[pred] += 1

            if obj.startswith('METPO:'):
                metpo_edges += 1
                metpo_objects.append(obj)

    print(f"\nTotal edges: {total_edges:,}")
    print(f"Edges using METPO: {metpo_edges:,}")
    if total_edges > 0:
        print(f"Percentage: {(metpo_edges/total_edges)*100:.1f}%")

    # Count unique METPO terms
    metpo_counter = Counter(metpo_objects)
    unique_metpo_terms = len(metpo_counter)

    print(f"\nUnique METPO terms used: {unique_metpo_terms}")

    print(f"\nPredicate distribution:")
    for pred, count in predicate_counter.most_common():
        pct = (count / total_edges) * 100 if total_edges > 0 else 0
        print(f"  {pred:50s}: {count:8,} ({pct:5.1f}%)")

    print(f"\nTop 20 most frequently used METPO terms:")
    for term, count in metpo_counter.most_common(20):
        print(f"  {term}: {count:,}")

    return {
        'total_edges': total_edges,
        'metpo_edges': metpo_edges,
        'unique_metpo_terms': unique_metpo_terms,
        'metpo_distribution': metpo_counter,
        'predicates': predicate_counter
    }

def analyze_transformed_nodes():
    """Analyze nodes in transformed Madin et al data"""
    if not TRANSFORMED_NODES.exists():
        print(f"ERROR: Transformed nodes not found: {TRANSFORMED_NODES}")
        return None

    print(f"\n=== Madin et al Transformed Nodes ===")
    print(f"Source: {TRANSFORMED_NODES}")

    node_types = Counter()
    total_nodes = 0

    with open(TRANSFORMED_NODES, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            total_nodes += 1
            node_id = row.get('id', '')
            # Extract prefix
            if ':' in node_id:
                prefix = node_id.split(':')[0]
                node_types[prefix] += 1

    print(f"\nTotal nodes: {total_nodes:,}")
    print(f"\nNode types (by prefix):")
    for prefix, count in node_types.most_common():
        pct = (count / total_nodes) * 100
        print(f"  {prefix:20s}: {count:8,} ({pct:5.1f}%)")

    return {
        'total_nodes': total_nodes,
        'node_types': node_types
    }

def main():
    print("=" * 70)
    print("Madin et al Analysis - 100% TRACEABLE TO PRIMARY SOURCES")
    print("=" * 70)

    raw_stats = analyze_raw_madin()
    transformed_stats = analyze_transformed_madin()
    node_stats = analyze_transformed_nodes()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    if raw_stats:
        print(f"Raw Madin et al records: {raw_stats['total_records']:,}")
    if transformed_stats:
        print(f"Transformed edges: {transformed_stats['total_edges']:,}")
        print(f"METPO edges: {transformed_stats['metpo_edges']:,}")
        print(f"Unique METPO terms: {transformed_stats['unique_metpo_terms']}")
    if node_stats:
        print(f"Total nodes: {node_stats['total_nodes']:,}")

if __name__ == "__main__":
    main()
