# notebooks/

## Purpose

This directory serves two distinct purposes:

### 1. Makefile Automation Scripts (Production)

Core scripts called by Makefile targets for METPO's ontology alignment workflow:

| Script | Makefile Target | Purpose |
|--------|----------------|---------|
| `fetch_ontology_names.py` | `alignment-fetch-ontology-names` | Fetch OLS4 ontology metadata |
| `categorize_ontologies.py` | `alignment-categorize-ontologies` | Categorize ontologies by relevance |
| `chromadb_semantic_mapper.py` | `alignment-query-metpo-terms` | Semantic mapping via ChromaDB |
| `analyze_matches.py` | `alignment-analyze-matches` | Analyze SSSOM mapping quality |
| `analyze_sibling_coherence.py` | `alignment-analyze-coherence` | Validate structural coherence |
| `analyze_coherence_results.py` | `alignment-identify-candidates` | Identify high-coherence candidates |
| `embed_ontology_to_chromadb.py` | `embeddings-non-ols-create` | Generate embeddings for non-OLS ontologies |

**Do not move these scripts** - they are tightly coupled to Makefile targets.

### 2. Exploration Notebooks (Documentation)

Educational/exploratory Jupyter notebooks:

- `ols_search_example.ipynb` - OLS4 and BioPortal API examples
- `explore_embeddings.ipynb` - SQLite embedding similarity search demo
- `query_chromadb.ipynb` - ChromaDB fast similarity search demo

### 3. Data Files

**Input Data** (external sources):
- Ontology metadata caches: `*_ontology_metadata.tsv`, `*_ontologies_complete.tsv/jsonl`
- METPO term lists: `metpo_all_labels.tsv`, `metpo_sample_labels.tsv`
- Ontology catalog: `ontology_sizes.csv`, `relevant_ontologies_for_metpo.tsv`

**Output Data** (analysis results):
- SSSOM mappings: `metpo_mappings_combined_relaxed.sssom.tsv`, `metpo_mappings_optimized.sssom.tsv`
- Coverage analysis: `metpo_branch_coverage_summary.tsv`, `metpo_coverage_landscape.tsv`
- Definition extraction: `definition_proposals.tsv`, `definition_sources_needed.tsv`, `high_confidence_definitions.tsv`
- Cross-references: `metpo_cross_references.tsv`
- Coherence results: `sibling_coherence_analysis_output.csv`

**Pipeline Intermediates**:
- `non-ols-terms/*.tsv` - Extracted terms from non-OLS ontologies for embedding

### 4. Archived Materials

- `archive/phase1/` - Superseded Phase 1 API-based discovery approach (see archive/phase1/README.md)

## Related Directories

- `scripts/analysis/` - Standalone analysis tools (not in Makefile workflow)
- `scripts/database/` - Database management utilities (ChromaDB operations)

## Workflow

See main Makefile for complete workflow:
```bash
make alignment-fetch-ontology-names
make alignment-categorize-ontologies
make alignment-create-embeddings
make alignment-query-metpo-terms
make alignment-analyze-matches
make alignment-analyze-coherence
make alignment-identify-candidates
```

## Design Philosophy

Per `CLAUDE.md`: "notebooks/ should have minimal .py files"

This directory maintains only scripts essential to Makefile automation, with standalone tools moved to `scripts/`. Jupyter notebooks are kept for exploration and education, not production workflows.
