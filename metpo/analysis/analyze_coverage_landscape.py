#!/usr/bin/env python3
"""
Create comprehensive coverage landscape summary for METPO branches.
Shows best coverage, fragmentation score, and coverage distribution for each branch.
"""

from collections import defaultdict

import pandas as pd

print("="*80)
print("METPO COVERAGE LANDSCAPE SUMMARY")
print("="*80)

# Load data
print("\nLoading METPO template...")
df = pd.read_csv("../src/templates/metpo_sheet.tsv", sep="\t", header=0, skiprows=[1])

# Build mappings and hierarchy
label_to_id = {}
id_to_label = {}
for _, row in df.iterrows():
    if isinstance(row["ID"], str) and row["ID"].startswith("METPO:"):
        label_to_id[row["label"]] = row["ID"]
        id_to_label[row["ID"]] = row["label"]

children_map = defaultdict(list)
for _, row in df.iterrows():
    if not isinstance(row["ID"], str) or not row["ID"].startswith("METPO:"):
        continue
    parent_str = row["parent classes (one strongly preferred)"]
    if pd.notna(parent_str) and isinstance(parent_str, str):
        parents = [p.strip() for p in parent_str.split("|")]
        for parent_label in parents:
            if parent_label in label_to_id:
                parent_id = label_to_id[parent_label]
                children_map[parent_id].append(row["ID"])

def get_descendants(node_id):
    desc = set()
    for child in children_map.get(node_id, []):
        desc.add(child)
        desc.update(get_descendants(child))
    return desc

# Find branches
all_nodes = set(id_to_label.keys())
parent_nodes = set(children_map.keys())
leaf_nodes = all_nodes - parent_nodes

branches = []
for parent_id in sorted(parent_nodes):
    descendants = get_descendants(parent_id)
    leaf_desc = descendants & leaf_nodes
    if len(leaf_desc) >= 5:
        branches.append({
            "id": parent_id,
            "label": id_to_label[parent_id],
            "total_desc": len(descendants),
            "leaf_desc": len(leaf_desc),
            "leaves": leaf_desc
        })

branches.sort(key=lambda x: x["leaf_desc"], reverse=True)

# Load search results
search_df = pd.read_csv("phase1_raw_results.tsv", sep="\t")
hq_df = search_df[search_df["similarity_ratio"] >= 0.5]

print(f"Analyzing {len(branches)} branches...")

# Analyze each branch
landscape = []

for branch in branches:
    leaves = branch["leaves"]
    branch_hq = hq_df[hq_df["metpo_id"].isin(leaves)]

    if len(branch_hq) == 0:
        landscape.append({
            "branch": branch["label"],
            "leaf_count": len(leaves),
            "best_ontology": "none",
            "best_coverage_pct": 0.0,
            "onts_for_50pct": 0,
            "onts_for_90pct": 0,
            "total_onts_with_matches": 0,
            "fragmentation_score": "UNCOVERED"
        })
        continue

    # Coverage by ontology
    ont_cov = defaultdict(lambda: {"leaves": set(), "sims": []})
    for _, row in branch_hq.iterrows():
        ont = row["match_ontology"]
        ont_cov[ont]["leaves"].add(row["metpo_id"])
        ont_cov[ont]["sims"].append(row["similarity_ratio"])

    # Sort by coverage
    ont_sorted = sorted(
        [(ont, data) for ont, data in ont_cov.items()],
        key=lambda x: len(x[1]["leaves"]),
        reverse=True
    )

    # Best single ontology (excluding METPO)
    best_ont = None
    best_cov_pct = 0.0
    for ont, data in ont_sorted:
        if ont != "METPO":
            pct = (len(data["leaves"]) / len(leaves)) * 100
            if pct > best_cov_pct:
                best_ont = ont
                best_cov_pct = pct

    # Count ontologies needed for 50% and 90%
    covered = set()
    onts_50 = 0
    onts_90 = 0
    reached_50 = False
    reached_90 = False

    for ont, data in ont_sorted:
        if ont == "METPO":
            continue
        covered.update(data["leaves"])

        if not reached_50:
            onts_50 += 1
            if len(covered) >= 0.5 * len(leaves):
                reached_50 = True

        if not reached_90:
            onts_90 += 1
            if len(covered) >= 0.9 * len(leaves):
                reached_90 = True

    if not reached_50:
        onts_50 = len([o for o, _ in ont_sorted if o != "METPO"])
    if not reached_90:
        onts_90 = len([o for o, _ in ont_sorted if o != "METPO"])

    # Fragmentation score
    total_onts = len([o for o, _ in ont_sorted if o != "METPO"])
    if best_cov_pct >= 90:
        frag = "CONSOLIDATED"
    elif onts_90 <= 3:
        frag = "LOW"
    elif onts_90 <= 10:
        frag = "MODERATE"
    elif onts_90 <= 50:
        frag = "HIGH"
    else:
        frag = "EXTREME"

    landscape.append({
        "branch": branch["label"],
        "leaf_count": len(leaves),
        "best_ontology": best_ont or "none",
        "best_coverage_pct": best_cov_pct,
        "onts_for_50pct": onts_50,
        "onts_for_90pct": onts_90,
        "total_onts_with_matches": total_onts,
        "fragmentation_score": frag
    })

# Create DataFrame and save
landscape_df = pd.DataFrame(landscape)
landscape_df = landscape_df.sort_values("onts_for_90pct", ascending=False)
landscape_df.to_csv("../../data/ontology_assessments/coverage/metpo_coverage_landscape.tsv", sep="\t", index=False)

# Display summary
print("\n" + "="*80)
print("COVERAGE LANDSCAPE BY FRAGMENTATION")
print("="*80)

for frag_level in ["EXTREME", "HIGH", "MODERATE", "LOW", "CONSOLIDATED", "UNCOVERED"]:
    subset = landscape_df[landscape_df["fragmentation_score"] == frag_level]
    if len(subset) == 0:
        continue

    print(f"\n{frag_level} FRAGMENTATION ({len(subset)} branches):")
    print(f"{'Branch':<35} {'Leaves':<7} {'Best Ont':<12} {'Best%':<7} {'For90%'}")
    print("-" * 80)

    for _, row in subset.iterrows():
        print(f"{row['branch']:<35} {row['leaf_count']:<7} "
              f"{row['best_ontology']:<12} {row['best_coverage_pct']:>5.1f}% "
              f"{row['onts_for_90pct']}")

print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)

print("\nFragmentation distribution:")
for frag_level in ["CONSOLIDATED", "LOW", "MODERATE", "HIGH", "EXTREME", "UNCOVERED"]:
    count = len(landscape_df[landscape_df["fragmentation_score"] == frag_level])
    print(f"  {frag_level:<15} {count:>3} branches")

print("\nBest single-ontology coverage:")
best_overall = landscape_df.nlargest(5, "best_coverage_pct")
for _, row in best_overall.iterrows():
    print(f"  {row['branch']:<35} {row['best_ontology']:<12} {row['best_coverage_pct']:>5.1f}%")

print("\nMost fragmented (require most ontologies for 90%):")
worst = landscape_df.nlargest(5, "onts_for_90pct")
for _, row in worst.iterrows():
    print(f"  {row['branch']:<35} {row['onts_for_90pct']:>3} ontologies")

print("\n✓ Saved to ../../data/ontology_assessments/coverage/metpo_coverage_landscape.tsv")
print("="*80)
