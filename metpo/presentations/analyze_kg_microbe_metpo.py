"""
Comprehensive analysis of METPO usage across all KG-Microbe datasets - 100% TRACEABLE

Primary sources:
- /home/mark/gitrepos/kg-microbe/data/transformed/bactotraits/edges.tsv
- /home/mark/gitrepos/kg-microbe/data/transformed/madin_etal/edges.tsv
- /home/mark/gitrepos/kg-microbe/data/transformed/bacdive/edges.tsv
"""

import csv
from collections import Counter
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.use("Agg")

# Primary source directories
KG_MICROBE_ROOT = Path("/home/mark/gitrepos/kg-microbe/data/transformed")
DATASETS = ["bactotraits", "madin_etal", "bacdive"]


def analyze_dataset(dataset_name):
    """Analyze METPO usage in a single KG-Microbe dataset"""
    edges_file = KG_MICROBE_ROOT / dataset_name / "edges.tsv"

    if not edges_file.exists():
        print(f"WARNING: {edges_file} not found, skipping")
        return None

    metpo_objects = []
    total_edges = 0
    metpo_edges = 0
    predicates = Counter()

    with Path(edges_file).open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            total_edges += 1
            obj = row.get("object", "")
            pred = row.get("predicate", "")

            predicates[pred] += 1

            if obj.startswith("METPO:"):
                metpo_edges += 1
                metpo_objects.append(obj)

    metpo_counter = Counter(metpo_objects)
    unique_metpo_terms = len(metpo_counter)

    return {
        "dataset": dataset_name,
        "total_edges": total_edges,
        "metpo_edges": metpo_edges,
        "unique_metpo_terms": unique_metpo_terms,
        "metpo_distribution": metpo_counter,
        "predicates": predicates,
        "source_file": str(edges_file),
    }


def load_metpo_labels():
    """Load METPO ID to label mapping"""
    labels_file = Path("/tmp/metpo_labels.csv")
    if not labels_file.exists():
        print("WARNING: METPO labels file not found, using IDs")
        return {}

    labels = {}
    with Path(labels_file).open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            metpo_id = row["id"]
            label = row["label"]
            labels[f"METPO:{metpo_id}"] = label
    return labels


def main():
    print("=" * 80)
    print("KG-Microbe METPO Usage Analysis - 100% TRACEABLE TO PRIMARY SOURCES")
    print("=" * 80)
    print(f"\nSource directory: {KG_MICROBE_ROOT}")

    # Load METPO labels
    metpo_labels = load_metpo_labels()
    print(f"Loaded {len(metpo_labels)} METPO labels")

    all_results = []
    all_metpo_terms = set()

    # Analyze each dataset
    for dataset_name in DATASETS:
        print(f"\n{'=' * 80}")
        print(f"Dataset: {dataset_name.upper()}")
        print("=" * 80)

        result = analyze_dataset(dataset_name)
        if result:
            all_results.append(result)
            all_metpo_terms.update(result["metpo_distribution"].keys())

            print(f"\nSource: {result['source_file']}")
            print(f"Total edges: {result['total_edges']:,}")
            print(f"METPO edges: {result['metpo_edges']:,}")
            pct = (
                (result["metpo_edges"] / result["total_edges"]) * 100
                if result["total_edges"] > 0
                else 0
            )
            print(f"Percentage: {pct:.1f}%")
            print(f"Unique METPO terms: {result['unique_metpo_terms']}")

            print("\nTop 10 METPO terms:")
            for term, count in result["metpo_distribution"].most_common(10):
                print(f"  {term}: {count:,}")

    # Combined summary
    print(f"\n{'=' * 80}")
    print("COMBINED SUMMARY")
    print("=" * 80)

    total_edges_all = sum(r["total_edges"] for r in all_results)
    total_metpo_edges_all = sum(r["metpo_edges"] for r in all_results)

    print(f"\nTotal edges across all datasets: {total_edges_all:,}")
    print(f"Total METPO edges: {total_metpo_edges_all:,}")
    print(f"Overall percentage: {(total_metpo_edges_all / total_edges_all) * 100:.1f}%")
    print(f"Total unique METPO terms used: {len(all_metpo_terms)}")

    print("\nPer-dataset breakdown:")
    print(f"{'Dataset':<20} {'Total Edges':>15} {'METPO Edges':>15} {'%':>8} {'Unique Terms':>15}")
    print("-" * 80)
    for r in all_results:
        pct = (r["metpo_edges"] / r["total_edges"]) * 100 if r["total_edges"] > 0 else 0
        print(
            f"{r['dataset']:<20} {r['total_edges']:>15,} {r['metpo_edges']:>15,} {pct:>7.1f}% {r['unique_metpo_terms']:>15}"
        )

    # Combine all METPO term counts
    combined_metpo = Counter()
    for r in all_results:
        combined_metpo.update(r["metpo_distribution"])

    print(f"\n{'=' * 80}")
    print("TOP 30 MOST FREQUENTLY USED METPO TERMS (ACROSS ALL DATASETS)")
    print("=" * 80)
    for term, count in combined_metpo.most_common(30):
        print(f"{term}: {count:,}")

    # Generate visualization - only Top 15 METPO terms
    try:
        _fig, ax = plt.subplots(figsize=(10, 8))

        # Top 15 METPO terms (with labels)
        top_terms = combined_metpo.most_common(15)
        terms = [metpo_labels.get(t[0], t[0].replace("METPO:", "")) for t in top_terms]
        counts = [t[1] for t in top_terms]

        ax.barh(range(len(terms)), counts, color="#6A4C93")
        ax.set_yticks(range(len(terms)))
        ax.set_yticklabels(terms, fontsize=12)
        ax.set_xlabel("Frequency", fontsize=14)
        ax.set_title("Top 15 Most Frequent METPO Terms", fontsize=16, fontweight="bold")
        ax.invert_yaxis()

        # Add value labels on bars
        for i, v in enumerate(counts):
            ax.text(v + max(counts) * 0.01, i, f"{v:,}", va="center", fontsize=10)

        plt.tight_layout()

        output_file = Path(__file__).parent / "kg_microbe_metpo_usage.png"
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        print(f"\n\nVisualization saved to: {output_file}")

    except Exception as e:
        print(f"\nWarning: Could not generate visualization: {e}")

    print("\n" + "=" * 80)
    print("PRIMARY SOURCES USED:")
    for r in all_results:
        print(f"  - {r['source_file']}")
    print("=" * 80)


if __name__ == "__main__":
    main()
