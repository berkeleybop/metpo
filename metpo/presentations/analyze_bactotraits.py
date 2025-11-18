"""
Analyze BactoTraits data and METPO usage - 100% TRACEABLE
Primary sources:
- /home/mark/gitrepos/kg-microbe/data/raw/BactoTraits_databaseV2_Jun2022.csv
- /home/mark/gitrepos/kg-microbe/data/transformed/bactotraits/edges.tsv
- /home/mark/gitrepos/kg-microbe/data/transformed/bactotraits/nodes.tsv
"""
import csv
from collections import Counter, defaultdict
from pathlib import Path

# Primary source files
RAW_FILE = Path("/home/mark/gitrepos/kg-microbe/data/raw/BactoTraits_databaseV2_Jun2022.csv")
TRANSFORMED_EDGES = Path("/home/mark/gitrepos/kg-microbe/data/transformed/bactotraits/edges.tsv")
TRANSFORMED_NODES = Path("/home/mark/gitrepos/kg-microbe/data/transformed/bactotraits/nodes.tsv")

def analyze_raw_bactotraits():
    """Analyze the raw BactoTraits CSV file"""
    if not RAW_FILE.exists():
        print(f"ERROR: Raw file not found: {RAW_FILE}")
        return None

    print("\n=== BactoTraits Raw Data Analysis ===")
    print(f"Source: {RAW_FILE}")

    with Path(RAW_FILE).open( encoding="utf-8", errors="ignore") as f:
        # Skip first two header rows (units and descriptions)
        f.readline()
        f.readline()

        reader = csv.DictReader(f, delimiter=";")

        total_strains = 0
        trait_coverage = defaultdict(int)

        for row in reader:
            total_strains += 1

            # Check which traits are present (non-empty)
            for key, value in row.items():
                if value and value.strip():
                    trait_coverage[key] += 1

        print(f"\nTotal strains: {total_strains:,}")
        print("\nTop 20 traits by coverage:")
        for trait, count in sorted(trait_coverage.items(), key=lambda x: x[1], reverse=True)[:20]:
            pct = (count / total_strains) * 100
            print(f"  {trait:40s}: {count:6,} ({pct:5.1f}%)")

        return {
            "total_strains": total_strains,
            "trait_coverage": trait_coverage
        }

def analyze_transformed_bactotraits():
    """Analyze METPO usage in transformed BactoTraits data"""
    if not TRANSFORMED_EDGES.exists():
        print(f"ERROR: Transformed edges not found: {TRANSFORMED_EDGES}")
        return None

    print("\n=== BactoTraits Transformed Data (METPO Usage) ===")
    print(f"Source: {TRANSFORMED_EDGES}")

    metpo_objects = []
    total_edges = 0
    metpo_edges = 0

    with Path(TRANSFORMED_EDGES).open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            total_edges += 1
            obj = row.get("object", "")
            if obj.startswith("METPO:"):
                metpo_edges += 1
                metpo_objects.append(obj)

    print(f"\nTotal edges: {total_edges:,}")
    print(f"Edges using METPO: {metpo_edges:,}")
    print(f"Percentage: {(metpo_edges/total_edges)*100:.1f}%")

    # Count unique METPO terms
    metpo_counter = Counter(metpo_objects)
    unique_metpo_terms = len(metpo_counter)

    print(f"\nUnique METPO terms used: {unique_metpo_terms}")
    print("\nTop 20 most frequently used METPO terms:")
    for term, count in metpo_counter.most_common(20):
        print(f"  {term}: {count:,}")

    return {
        "total_edges": total_edges,
        "metpo_edges": metpo_edges,
        "unique_metpo_terms": unique_metpo_terms,
        "metpo_distribution": metpo_counter
    }

def analyze_transformed_nodes():
    """Analyze nodes in transformed BactoTraits data"""
    if not TRANSFORMED_NODES.exists():
        print(f"ERROR: Transformed nodes not found: {TRANSFORMED_NODES}")
        return None

    print("\n=== BactoTraits Transformed Nodes ===")
    print(f"Source: {TRANSFORMED_NODES}")

    node_types = Counter()
    total_nodes = 0

    with Path(TRANSFORMED_NODES).open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            total_nodes += 1
            node_id = row.get("id", "")
            # Extract prefix
            if ":" in node_id:
                prefix = node_id.split(":")[0]
                node_types[prefix] += 1

    print(f"\nTotal nodes: {total_nodes:,}")
    print("\nNode types (by prefix):")
    for prefix, count in node_types.most_common():
        pct = (count / total_nodes) * 100
        print(f"  {prefix:20s}: {count:8,} ({pct:5.1f}%)")

    return {
        "total_nodes": total_nodes,
        "node_types": node_types
    }

def main():
    print("=" * 70)
    print("BactoTraits Analysis - 100% TRACEABLE TO PRIMARY SOURCES")
    print("=" * 70)

    raw_stats = analyze_raw_bactotraits()
    transformed_stats = analyze_transformed_bactotraits()
    node_stats = analyze_transformed_nodes()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    if raw_stats:
        print(f"Raw BactoTraits strains: {raw_stats['total_strains']:,}")
    if transformed_stats:
        print(f"Transformed edges: {transformed_stats['total_edges']:,}")
        print(f"METPO edges: {transformed_stats['metpo_edges']:,}")
        print(f"Unique METPO terms: {transformed_stats['unique_metpo_terms']}")
    if node_stats:
        print(f"Total nodes: {node_stats['total_nodes']:,}")

if __name__ == "__main__":
    main()
