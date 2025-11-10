#!/usr/bin/env python
"""Analyze match quality by distance for each ontology."""

import pandas as pd
import sys

if len(sys.argv) < 2:
    print("Usage: python analyze_match_quality.py <sssom_file>")
    sys.exit(1)

df = pd.read_csv(sys.argv[1], sep='\t', comment='#')

# Extract distance from comment field
df['distance'] = df['comment'].str.extract(r'distance: ([\d.]+)').astype(float)

# Focus on non-OLS ontologies
non_ols = ['d3o', 'meo', 'miso', 'gmo', 'id-amr', 'n4l_merged', 'omp', 'bipon',
            'mccv', 'typon', 'fmpm', 'ofsmr', 'mpo']

print(f"{'Ontology':<15} {'Matches':<10} {'Best':<10} {'Median':<10} {'Worst':<10} {'Avg':<10} {'<0.35':<8} {'Assessment'}")
print("-" * 110)

for ont in sorted(non_ols):
    ont_df = df[df['object_source'] == ont]

    if len(ont_df) == 0:
        print(f"{ont:<15} {'0':<10} {'-':<10} {'-':<10} {'-':<10} {'-':<10} {'0':<8} REMOVE - no matches")
        continue

    distances = ont_df['distance'].sort_values()
    best = distances.iloc[0]
    median = distances.median()
    worst = distances.iloc[-1]
    avg = distances.mean()
    high_quality = len(ont_df[ont_df['distance'] < 0.35])

    # Assessment
    if avg < 0.35:
        assessment = "EXCELLENT - keep"
    elif avg < 0.50 and high_quality >= 3:
        assessment = "GOOD - keep"
    elif avg < 0.60 and high_quality >= 1:
        assessment = "FAIR - review"
    else:
        assessment = "POOR - likely remove"

    print(f"{ont:<15} {len(ont_df):<10} {best:<10.4f} {median:<10.4f} {worst:<10.4f} {avg:<10.4f} {high_quality:<8} {assessment}")
