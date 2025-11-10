# scripts/analysis/

Standalone analysis tools for METPO data analysis and quality assessment.

These scripts are **not** part of the main Makefile workflow (unlike notebooks/ scripts), but provide valuable analysis capabilities.

## Scripts

### Coverage & Quality Analysis

**analyze_branch_coverage_final.py**
- **Purpose**: Analyzes METPO branch coverage by external ontology
- **Threshold**: ≥50% coverage to identify well-covered branches
- **Output**: `notebooks/metpo_branch_coverage_summary.tsv`
- **Usage**: `python scripts/analysis/analyze_branch_coverage_final.py`
- **TODO**: Add Click CLI with configurable threshold

**analyze_coverage_landscape.py**
- **Purpose**: Creates comprehensive coverage landscape summary
- **Metrics**: Fragmentation scores, coverage patterns, ontology distribution
- **Output**: `notebooks/metpo_coverage_landscape.tsv`
- **Usage**: `python scripts/analysis/analyze_coverage_landscape.py`
- **TODO**: Add Click CLI with output path option

**analyze_match_quality.py**
- **Purpose**: Quick match quality analysis by distance threshold
- **Input**: SSSOM file (argv)
- **Usage**: `python scripts/analysis/analyze_match_quality.py <sssom_file>`
- **TODO**: Convert to Click CLI with threshold parameters

### Ontology Value Assessment

**analyze_ontology_value.py**
- **Purpose**: ROI analysis - native vs imported terms, identifies redundancy
- **CLI**: ✅ Click interface (`--input`)
- **Metrics**: Import necessity, term uniqueness, ontology contribution
- **Usage**: `python scripts/analysis/analyze_ontology_value.py --input mappings.tsv`
- **Use Case**: Evaluate ontology source cost/benefit

### ICBO 2025 Analysis

**extract_definitions_from_mappings.py**
- **Purpose**: Extracts definitions, sources, and cross-references from SSSOM mappings
- **Outputs**:
  - `definition_proposals.tsv` - Candidate definitions
  - `definition_sources_needed.tsv` - Terms needing definitions
  - `high_confidence_definitions.tsv` - High-quality definitions
  - `metpo_cross_references.tsv` - Cross-reference mappings
- **Referenced**: `docs/ICBO_PREP.md`, `docs/icbo_analysis_notes.md`
- **Usage**: `python scripts/analysis/extract_definitions_from_mappings.py`
- **TODO**: Add Click CLI with input/output path parameters
- **Status**: Used for ICBO 2025 presentation data

## Design Philosophy

Scripts in this directory:
- ✅ Standalone tools (not Makefile dependencies)
- ✅ Reusable across projects
- ✅ Clear single purpose
- ⚠️ Should use Click CLI (some need conversion)

## Best Practices

When adding new scripts:
1. Use Click for CLI interface
2. Accept input/output paths as parameters (no hardcoded paths)
3. Include docstrings and --help text
4. Follow naming convention: `{verb}_{object}.py`
5. Add entry to this README

## Related

- `scripts/database/` - Database management utilities
- `notebooks/` - Makefile automation scripts (production workflow)
