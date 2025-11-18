# notebooks/

This directory contains **only** Jupyter notebooks for exploration and education.

## Philosophy

Per user guidance: "the only code i want in @notebooks/ is modules that are imported into a notebook"

Since these notebooks only import standard libraries and external packages (no local modules), this directory contains only .ipynb files.

## Contents

### Jupyter Notebooks (3 files)

Educational/exploratory notebooks for understanding METPO workflows:

- `ols_search_example.ipynb` - OLS4 and BioPortal API examples
- `explore_embeddings.ipynb` - SQLite embedding similarity search demo
- `assess_ontology_by_api_search.ipynb` - Frequency-based ontology assessment (complementary to semantic embeddings)

**Note**: ChromaDB querying is now handled by the production CLI tool `chromadb-semantic-mapper` (see `docs/cli-reference.md`)

## Related Directories

### Pipeline Scripts
- `scripts/pipeline/` - Makefile automation scripts (7 files moved from notebooks/)
  - fetch_ontology_names.py
  - categorize_ontologies.py
  - chromadb_semantic_mapper.py
  - analyze_matches.py
  - analyze_sibling_coherence.py
  - analyze_coherence_results.py
  - embed_ontology_to_chromadb.py

### Analysis Tools
- `scripts/analysis/` - Standalone analysis tools (not in Makefile workflow)
- `scripts/database/` - Database management utilities (ChromaDB operations)

### Data Files
All data files have been moved to `data/` directories organized by purpose:

#### Input Data
- `data/metpo_terms/` - METPO term lists
- `data/ontology_assessments/cache/` - Cached ontology metadata from OLS4/BioPortal APIs
- `data/ontology_assessments/` - Ontology assessment files
- `data/pipeline/non-ols-terms/` - **Pipeline intermediates** (TSV files extracted from ontologies for embedding generation)

#### Output Data
- `data/mappings/` - SSSOM mapping files
- `data/ontology_assessments/coverage/` - Coverage analysis results
- `data/definitions/` - Definition extraction outputs
- `data/coherence/` - Coherence analysis results

## Makefile Workflow

The main METPO alignment workflow calls scripts from `scripts/pipeline/`:

```bash
make alignment-fetch-ontology-names    # Fetch OLS4 metadata
make alignment-categorize-ontologies   # Categorize by relevance
make alignment-query-metpo-terms       # Generate SSSOM mappings
make alignment-analyze-matches         # Analyze match quality
make alignment-analyze-coherence       # Compute structural coherence
make alignment-identify-candidates     # Identify alignment candidates
```

See `Makefile` for complete workflow and `scripts/pipeline/README.md` for script documentation.
