#!/bin/bash
# Cleanup superseded/throwaway files from ontology analysis
# Run this after reviewing ONTOLOGY_SELECTION_SUMMARY.md

set -e

echo "This will remove superseded documentation, throwaway scripts, and old data files."
echo "Files to be removed:"
echo ""
echo "Superseded Documentation:"
echo "  - ontology_source_value_analysis.md"
echo "  - ontology_value_analysis_combined.txt"
echo ""
echo "Throwaway Scripts:"
echo "  - test_gc_query.py"
echo "  - check_chromadb_ontologies.py"
echo "  - create_optimized_chromadb.py"
echo "  - sanity_check_non_ols.py"
echo "  - analyze_iri_duplicates.py"
echo ""
echo "Superseded Data Files:"
echo "  - metpo_mappings_combined.sssom.tsv (strict cutoff version)"
echo "  - metpo_mappings.sssom.tsv (earlier version)"
echo ""

read -p "Proceed with deletion? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Aborted."
    exit 1
fi

echo "Removing files..."

# Superseded documentation
rm -f ontology_source_value_analysis.md
rm -f ontology_value_analysis_combined.txt

# Throwaway scripts
rm -f test_gc_query.py
rm -f check_chromadb_ontologies.py
rm -f create_optimized_chromadb.py
rm -f sanity_check_non_ols.py
rm -f analyze_iri_duplicates.py

# Superseded data files
rm -f metpo_mappings_combined.sssom.tsv
rm -f metpo_mappings.sssom.tsv

echo "✓ Cleanup complete!"
echo ""
echo "Kept files:"
echo "  Documentation:"
echo "    - ONTOLOGY_SELECTION_SUMMARY.md (master reference)"
echo "    - ontology_removal_recommendation.md (detailed ROI analysis)"
echo "    - chromadb_audit_report.md (database verification)"
echo "    - vector_search_analysis.md (threshold analysis)"
echo "  Scripts:"
echo "    - chromadb_semantic_mapper.py (core tool)"
echo "    - audit_chromadb.py, analyze_ontology_value.py, analyze_match_quality.py"
echo "    - analyze_sibling_coherence.py, analyze_matches.py, analyze_coherence_results.py"
echo "    - combine_chromadb.py, filter_ols_chromadb.py"
echo "  Data:"
echo "    - metpo_mappings_combined_relaxed.sssom.tsv (used for final decisions)"
echo "    - chromadb_audit_results.txt, ontology_value_analysis_relaxed.txt"
