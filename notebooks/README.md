# notebooks/

This directory contains **only** Makefile automation scripts and Jupyter notebooks for exploration. All data files have been moved to `data/` directories organized by purpose.

## Contents

### Makefile Automation Scripts (7 files)

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

### Jupyter Notebooks (4 files)

Educational/exploratory notebooks for understanding the METPO workflow:

- `ols_search_example.ipynb` - OLS4 and BioPortal API examples
- `explore_embeddings.ipynb` - SQLite embedding similarity search demo
- `query_chromadb.ipynb` - ChromaDB fast similarity search demo
- `assess_ontology_by_api_search.ipynb` - Frequency-based ontology assessment (complementary to semantic embeddings)

### Pipeline Intermediates (1 directory)

- `non-ols-terms/` - Extracted terms from non-OLS ontologies for embedding generation (13 TSV files)
  - These are working files that need to stay accessible to the scripts that generated them

## Data Organization

All data files have been moved to organized directories in `data/`:

### Input Data
- `data/metpo_terms/` - METPO term lists (metpo_all_labels.tsv, metpo_sample_labels.tsv)
- `data/ontology_assessments/cache/` - Cached ontology metadata from OLS4/BioPortal APIs
- `data/ontology_assessments/` - Ontology assessment files (ontology_sizes.csv, relevant_ontologies_for_metpo.tsv)

### Output Data
- `data/mappings/` - SSSOM mapping files (metpo_mappings_*.sssom.tsv)
- `data/ontology_assessments/coverage/` - Coverage analysis results
- `data/definitions/` - Definition extraction outputs
- `data/coherence/` - Coherence analysis results

## Related Directories

- `scripts/analysis/` - Standalone analysis tools (not in Makefile workflow)
- `scripts/database/` - Database management utilities (ChromaDB operations)
- `data/` - All data files organized by purpose

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

This directory follows the principle: **"notebooks/ should contain only automation scripts and exploration notebooks, not data files"**

- ✅ 7 Makefile automation scripts (must stay here)
- ✅ 4 Jupyter notebooks for exploration
- ✅ 1 directory of pipeline intermediates (non-ols-terms/)
- ❌ No data files (all moved to data/ directories)
