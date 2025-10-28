#!/usr/bin/env python3
"""
Analyze which ontologies provide complete or substantial coverage of METPO branches.

For each high-level METPO class, find all leaf descendants and check how many
have high-quality matches in other ontologies.
"""

import pandas as pd
from collections import defaultdict
import sys

# Configuration
HIGH_QUALITY_THRESHOLD = 0.5
MIN_COVERAGE_PERCENT = 50.0  # Minimum % coverage to report

print("="*80)
print("METPO BRANCH COVERAGE ANALYSIS")
print("="*80)

# Load METPO template to get hierarchy
print("\nLoading METPO template...")
metpo_template = pd.read_csv('../src/templates/metpo_sheet.tsv', sep='\t', skiprows=1)
metpo_template.columns = metpo_template.columns.str.strip()

# Load search results with similarity scores
print("Loading search results...")
search_results = pd.read_csv('phase1_raw_results.tsv', sep='\t')

# Filter to high-quality matches only
hq_results = search_results[search_results['similarity_ratio'] >= HIGH_QUALITY_THRESHOLD].copy()

print(f"Total METPO classes: {len(metpo_template)}")
print(f"Total search results: {len(search_results)}")
print(f"High-quality matches (≥{HIGH_QUALITY_THRESHOLD}): {len(hq_results)}")

# Build parent-child relationships
print("\nBuilding METPO hierarchy...")
parent_col = 'SC % SPLIT=|'  # Parent class column in processed template
if parent_col not in metpo_template.columns:
    print(f"Error: Column '{parent_col}' not found")
    print(f"Available columns: {list(metpo_template.columns)}")
    sys.exit(1)

# Create mapping of parent -> children
children_map = defaultdict(list)
for idx, row in metpo_template.iterrows():
    child_id = row['ID']
    parent = row[parent_col]

    if pd.notna(parent) and isinstance(parent, str):
        # Handle multiple parents (split by comma or semicolon)
        parents = [p.strip() for p in parent.replace(';', ',').split(',')]
        for p in parents:
            if p.startswith('METPO:'):
                children_map[p].append(child_id)

# Find leaf nodes (nodes with no children)
all_nodes = set(metpo_template['ID'].dropna())
parent_nodes = set(children_map.keys())
leaf_nodes = all_nodes - parent_nodes

print(f"Parent nodes: {len(parent_nodes)}")
print(f"Leaf nodes: {len(leaf_nodes)}")

# Get all descendants recursively
def get_all_descendants(node_id, children_map):
    """Get all descendants of a node (recursive)"""
    descendants = set()
    direct_children = children_map.get(node_id, [])

    for child in direct_children:
        descendants.add(child)
        descendants.update(get_all_descendants(child, children_map))

    return descendants

# Identify high-level branches (nodes with many descendants)
print("\nIdentifying high-level branches...")
branch_info = []

for parent_id in parent_nodes:
    descendants = get_all_descendants(parent_id, children_map)
    leaf_descendants = descendants & leaf_nodes

    if len(leaf_descendants) >= 3:  # Only consider branches with 3+ leaf nodes
        parent_row = metpo_template[metpo_template['ID'] == parent_id]
        if not parent_row.empty:
            parent_label = parent_row['label'].iloc[0]
            branch_info.append({
                'id': parent_id,
                'label': parent_label,
                'total_descendants': len(descendants),
                'leaf_descendants': len(leaf_descendants),
                'leaves': leaf_descendants
            })

# Sort by number of leaf descendants
branch_info.sort(key=lambda x: x['leaf_descendants'], reverse=True)

print(f"Found {len(branch_info)} branches with 3+ leaf nodes\n")

# For each branch, analyze coverage by ontology
print("="*80)
print("BRANCH COVERAGE BY ONTOLOGY")
print("="*80)

coverage_summary = []

for branch in branch_info:
    branch_id = branch['id']
    branch_label = branch['label']
    leaves = branch['leaves']

    print(f"\n{'='*80}")
    print(f"Branch: {branch_label} ({branch_id})")
    print(f"  Total descendants: {branch['total_descendants']}")
    print(f"  Leaf nodes: {len(leaves)}")
    print(f"{'='*80}")

    # Get high-quality matches for this branch's leaves
    branch_matches = hq_results[hq_results['metpo_id'].isin(leaves)]

    if len(branch_matches) == 0:
        print("  ⚠️  No high-quality matches found for any leaf in this branch")
        continue

    # Count coverage by ontology
    ontology_coverage = defaultdict(lambda: {'matched_leaves': set(), 'total_matches': 0, 'avg_similarity': []})

    for idx, row in branch_matches.iterrows():
        ontology = row['match_ontology']
        metpo_id = row['metpo_id']
        similarity = row['similarity_ratio']

        ontology_coverage[ontology]['matched_leaves'].add(metpo_id)
        ontology_coverage[ontology]['total_matches'] += 1
        ontology_coverage[ontology]['avg_similarity'].append(similarity)

    # Calculate statistics and find high-coverage ontologies
    coverage_stats = []
    for ontology, stats in ontology_coverage.items():
        matched_count = len(stats['matched_leaves'])
        coverage_pct = (matched_count / len(leaves)) * 100
        avg_sim = sum(stats['avg_similarity']) / len(stats['avg_similarity'])

        coverage_stats.append({
            'ontology': ontology,
            'matched_leaves': matched_count,
            'total_leaves': len(leaves),
            'coverage_pct': coverage_pct,
            'total_matches': stats['total_matches'],
            'avg_similarity': avg_sim
        })

    # Sort by coverage percentage
    coverage_stats.sort(key=lambda x: x['coverage_pct'], reverse=True)

    # Show ontologies with significant coverage
    print(f"\n  Ontologies with ≥{MIN_COVERAGE_PERCENT}% coverage:")
    print(f"  {'Ontology':<15} {'Covered':<8} {'Total':<7} {'%':<7} {'Matches':<9} {'Avg Sim':<8}")
    print(f"  {'-'*70}")

    found_coverage = False
    for stat in coverage_stats:
        if stat['coverage_pct'] >= MIN_COVERAGE_PERCENT:
            found_coverage = True
            print(f"  {stat['ontology']:<15} {stat['matched_leaves']:<8} {stat['total_leaves']:<7} "
                  f"{stat['coverage_pct']:>6.1f}% {stat['total_matches']:<9} {stat['avg_similarity']:.3f}")

            # Add to summary
            coverage_summary.append({
                'branch_id': branch_id,
                'branch_label': branch_label,
                'ontology': stat['ontology'],
                'coverage_pct': stat['coverage_pct'],
                'matched_leaves': stat['matched_leaves'],
                'total_leaves': stat['total_leaves'],
                'avg_similarity': stat['avg_similarity']
            })

    if not found_coverage:
        print(f"  (No ontology provides ≥{MIN_COVERAGE_PERCENT}% coverage)")
        # Show top 5 anyway
        print(f"\n  Top 5 ontologies by coverage:")
        print(f"  {'Ontology':<15} {'Covered':<8} {'Total':<7} {'%':<7} {'Matches':<9} {'Avg Sim':<8}")
        print(f"  {'-'*70}")
        for stat in coverage_stats[:5]:
            print(f"  {stat['ontology']:<15} {stat['matched_leaves']:<8} {stat['total_leaves']:<7} "
                  f"{stat['coverage_pct']:>6.1f}% {stat['total_matches']:<9} {stat['avg_similarity']:.3f}")

# Save coverage summary
if coverage_summary:
    summary_df = pd.DataFrame(coverage_summary)
    summary_df.to_csv('metpo_branch_coverage_summary.tsv', sep='\t', index=False)
    print(f"\n\n✓ Saved detailed coverage summary to metpo_branch_coverage_summary.tsv")

# Final summary: ontologies covering multiple branches
print("\n" + "="*80)
print("ONTOLOGIES COVERING MULTIPLE BRANCHES")
print("="*80)

if coverage_summary:
    multi_branch = defaultdict(list)
    for item in coverage_summary:
        multi_branch[item['ontology']].append({
            'branch': item['branch_label'],
            'coverage': item['coverage_pct']
        })

    # Filter to ontologies covering 2+ branches
    multi_coverage = {ont: branches for ont, branches in multi_branch.items() if len(branches) >= 2}

    if multi_coverage:
        for ontology, branches in sorted(multi_coverage.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"\n{ontology} (covers {len(branches)} branches):")
            for branch in sorted(branches, key=lambda x: x['coverage'], reverse=True):
                print(f"  • {branch['branch']}: {branch['coverage']:.1f}% coverage")
    else:
        print("\nNo ontology provides ≥50% coverage for multiple branches")
else:
    print("\nNo ontologies found with ≥50% coverage for any branch")

print("\n" + "="*80)
