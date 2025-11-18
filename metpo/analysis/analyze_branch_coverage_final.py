"""
Analyze METPO branch coverage by other ontologies.

For each major METPO branch, determine which ontologies provide
substantial coverage of the leaf nodes.
"""

from collections import defaultdict

import pandas as pd

print("="*80)
print("METPO BRANCH COVERAGE ANALYSIS")
print("="*80)

# Load METPO template
print("\nLoading METPO template...")
df = pd.read_csv("../src/templates/metpo_sheet.tsv", sep="\t", header=0, skiprows=[1])

# Create label->ID mapping
label_to_id = {}
id_to_label = {}
for _, row in df.iterrows():
    if isinstance(row["ID"], str) and row["ID"].startswith("METPO:"):
        label_to_id[row["label"]] = row["ID"]
        id_to_label[row["ID"]] = row["label"]

# Build hierarchy using label-based parents
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

print(f"Classes: {len(id_to_label)}")
print(f"Parent nodes: {len(children_map)}")

# Get all descendants recursively
def get_descendants(node_id):
    desc = set()
    for child in children_map.get(node_id, []):
        desc.add(child)
        desc.update(get_descendants(child))
    return desc

# Find leaf nodes
all_nodes = set(id_to_label.keys())
parent_nodes = set(children_map.keys())
leaf_nodes = all_nodes - parent_nodes

print(f"Leaf nodes: {len(leaf_nodes)}")

# Identify major branches
branches = []
for parent_id in sorted(parent_nodes):
    descendants = get_descendants(parent_id)
    leaf_desc = descendants & leaf_nodes

    if len(leaf_desc) >= 5:  # At least 5 leaf descendants
        branches.append({
            "id": parent_id,
            "label": id_to_label[parent_id],
            "total_desc": len(descendants),
            "leaf_desc": len(leaf_desc),
            "leaves": leaf_desc
        })

branches.sort(key=lambda x: x["leaf_desc"], reverse=True)

print(f"Major branches (≥5 leaves): {len(branches)}")

# Load search results
print("\nLoading search results...")
search_df = pd.read_csv("phase1_raw_results.tsv", sep="\t")
hq_df = search_df[search_df["similarity_ratio"] >= 0.5]

print(f"Total results: {len(search_df)}")
print(f"High-quality matches (≥0.5): {len(hq_df)}")

# Analyze each branch
print("\n" + "="*80)
print("COVERAGE BY BRANCH")
print("="*80)

coverage_results = []

for branch in branches:
    print(f"\n{branch['label']} ({branch['id']})")
    print(f"  Leaves: {branch['leaf_desc']}, Total descendants: {branch['total_desc']}")

    leaves = branch["leaves"]
    branch_hq = hq_df[hq_df["metpo_id"].isin(leaves)]

    if len(branch_hq) == 0:
        print("  ⚠️  No high-quality matches")
        continue

    # Coverage by ontology
    ont_coverage = defaultdict(lambda: {"leaves": set(), "count": 0, "sims": []})

    for _, row in branch_hq.iterrows():
        ont = row["match_ontology"]
        ont_coverage[ont]["leaves"].add(row["metpo_id"])
        ont_coverage[ont]["count"] += 1
        ont_coverage[ont]["sims"].append(row["similarity_ratio"])

    # Calculate statistics
    stats = []
    for ont, data in ont_coverage.items():
        cov_pct = (len(data["leaves"]) / len(leaves)) * 100
        avg_sim = sum(data["sims"]) / len(data["sims"])

        stats.append({
            "ont": ont,
            "covered": len(data["leaves"]),
            "total": len(leaves),
            "pct": cov_pct,
            "matches": data["count"],
            "avg_sim": avg_sim
        })

    stats.sort(key=lambda x: x["pct"], reverse=True)

    # Show top ontologies
    print(f"\n  {'Ontology':<15} {'Coverage':<12} {'%':<7} {'Matches':<9} {'Avg Sim'}")
    print(f"  {'-'*65}")

    for s in stats[:10]:
        marker = "★" if s["pct"] >= 50 else " "
        print(f"  {marker}{s['ont']:<14} {s['covered']}/{s['total']:<9} {s['pct']:>5.1f}% {s['matches']:<9} {s['avg_sim']:.3f}")

        if s["pct"] >= 50:
            coverage_results.append({
                "branch": branch["label"],
                "branch_id": branch["id"],
                "ontology": s["ont"],
                "coverage_pct": s["pct"],
                "covered_leaves": s["covered"],
                "total_leaves": s["total"],
                "avg_similarity": s["avg_sim"]
            })

# Final summary
print("\n" + "="*80)
print("SUMMARY: ONTOLOGIES WITH ≥50% BRANCH COVERAGE")
print("="*80)

if coverage_results:
    df_cov = pd.DataFrame(coverage_results)
    df_cov.to_csv("../../data/ontology_assessments/coverage/metpo_branch_coverage_summary.tsv", sep="\t", index=False)

    # Group by ontology
    ont_branches = defaultdict(list)
    for r in coverage_results:
        ont_branches[r["ontology"]].append({
            "branch": r["branch"],
            "pct": r["coverage_pct"],
            "cov": r["covered_leaves"],
            "tot": r["total_leaves"]
        })

    # Sort by number of branches covered
    for ont, branches_list in sorted(ont_branches.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n{ont} ({len(branches_list)} branch{'es' if len(branches_list) > 1 else ''}):")
        for b in sorted(branches_list, key=lambda x: x["pct"], reverse=True):
            print(f"  • {b['branch']}: {b['cov']}/{b['tot']} leaves ({b['pct']:.1f}%)")

    print("\n✓ Saved detailed results to ../../data/ontology_assessments/coverage/metpo_branch_coverage_summary.tsv")
else:
    print("\nNo ontology provides ≥50% coverage for any major branch")
    print("\nShowing best partial coverage for largest branch:")
    if branches:
        largest = branches[0]
        leaves = largest["leaves"]
        branch_hq = hq_df[hq_df["metpo_id"].isin(leaves)]

        ont_cov = defaultdict(lambda: {"leaves": set(), "sims": []})
        for _, row in branch_hq.iterrows():
            ont_cov[row["match_ontology"]]["leaves"].add(row["metpo_id"])
            ont_cov[row["match_ontology"]]["sims"].append(row["similarity_ratio"])

        stats = [(ont, len(d["leaves"]), sum(d["sims"])/len(d["sims"]))
                 for ont, d in ont_cov.items()]
        stats.sort(key=lambda x: x[1], reverse=True)

        print(f"\n{largest['label']} ({len(leaves)} leaves):")
        for ont, cov, avg in stats[:5]:
            pct = (cov / len(leaves)) * 100
            print(f"  {ont:<15} {cov}/{len(leaves):<7} {pct:>5.1f}% avg_sim={avg:.3f}")

print("\n" + "="*80)
