# scripts/pipeline/

Makefile automation scripts for the METPO ontology alignment workflow.

## Scripts

These 7 scripts are called by Makefile targets and form the core of the METPO alignment pipeline:

### 1. fetch_ontology_names.py
**Makefile target**: `alignment-fetch-ontology-names`
**Purpose**: Fetch ontology metadata from OLS4 API and merge with size data
**Input**: `data/ontology_assessments/ontology_sizes.csv`
**Output**: `notebooks/ontology_catalog.csv`
**Usage**:
```bash
python scripts/pipeline/fetch_ontology_names.py \
  --sizes-csv data/ontology_assessments/ontology_sizes.csv \
  --output-csv notebooks/ontology_catalog.csv
```

### 2. categorize_ontologies.py
**Makefile target**: `alignment-categorize-ontologies`
**Purpose**: Categorize ontologies by relevance using keyword scoring
**Input**: `notebooks/ontology_catalog.csv`
**Output**: `notebooks/ontologies_*.csv` (very_appealing, appealing, somewhat_appealing, not_appealing)
**Usage**:
```bash
python scripts/pipeline/categorize_ontologies.py \
  --input-csv notebooks/ontology_catalog.csv \
  --output-prefix notebooks/ontologies
```

### 3. chromadb_semantic_mapper.py
**Makefile target**: `alignment-query-metpo-terms`
**Purpose**: Generate SSSOM mappings from METPO terms via ChromaDB semantic search
**Input**: `src/templates/metpo_sheet.tsv`, ChromaDB collection
**Output**: SSSOM TSV file (default: `data/mappings/metpo_mappings.sssom.tsv`)
**Usage**:
```bash
python scripts/pipeline/chromadb_semantic_mapper.py \
  --metpo-tsv src/templates/metpo_sheet.tsv \
  --chroma-path notebooks/metpo_relevant_chroma \
  --collection-name metpo_relevant_embeddings \
  --output notebooks/metpo_relevant_mappings.sssom.tsv \
  --top-n 10 \
  --label-only \
  --distance-cutoff 0.35
```

### 4. analyze_matches.py
**Makefile target**: `alignment-analyze-matches`
**Purpose**: Analyze SSSOM mapping quality and generate match statistics
**Input**: SSSOM TSV file
**Output**: Console output with match quality statistics
**Usage**:
```bash
python scripts/pipeline/analyze_matches.py \
  --input-csv notebooks/metpo_relevant_mappings.sssom.tsv \
  --good-match-threshold 0.9
```

### 5. analyze_sibling_coherence.py
**Makefile target**: `alignment-analyze-coherence`
**Purpose**: Compute structural coherence by checking if METPO siblings map to external siblings
**Input**: SSSOM TSV file, METPO OWL file
**Output**: Coherence results CSV (default: `data/coherence/sibling_coherence_analysis_output.csv`)
**Usage**:
```bash
python scripts/pipeline/analyze_sibling_coherence.py \
  --input-csv notebooks/metpo_relevant_mappings.sssom.tsv \
  --metpo-owl src/ontology/metpo.owl \
  --output-csv notebooks/full_coherence_results.csv
```

### 6. analyze_coherence_results.py
**Makefile target**: `alignment-identify-candidates`
**Purpose**: Identify high-coherence alignment candidates from coherence analysis
**Input**: Coherence results CSV, SSSOM TSV file
**Output**: Alignment candidates CSV
**Usage**:
```bash
python scripts/pipeline/analyze_coherence_results.py \
  --results-csv notebooks/full_coherence_results.csv \
  --matches-csv notebooks/metpo_relevant_mappings.sssom.tsv
```

### 7. embed_ontology_to_chromadb.py
**Makefile target**: `embed-non-ols-terms`
**Purpose**: Generate embeddings for non-OLS ontology terms and store in ChromaDB
**Input**: TSV files from `data/pipeline/non-ols-terms/`
**Output**: ChromaDB collection
**Usage**:
```bash
python scripts/pipeline/embed_ontology_to_chromadb.py \
  --tsv-file data/pipeline/non-ols-terms/D3O.tsv \
  --chroma-path ./embeddings_chroma \
  --collection-name non_ols_embeddings
```

## Complete Workflow

```bash
# Run the complete alignment pipeline
make alignment-run-all

# Or run steps individually
make alignment-fetch-ontology-names
make alignment-categorize-ontologies
make alignment-query-metpo-terms
make alignment-analyze-matches
make alignment-analyze-coherence
make alignment-identify-candidates
```

## Design Philosophy

These scripts:
- ✅ Are called by Makefile targets (tightly coupled to build system)
- ✅ Use Click for CLI interface
- ✅ Accept input/output paths as parameters
- ✅ Generate pipeline outputs (mappings, analysis results)
- ❌ Are not intended for standalone use (use via Makefile)

## Related Directories

- `scripts/analysis/` - Standalone analysis tools (not part of Makefile workflow)
- `scripts/database/` - Database management utilities
- `notebooks/` - Jupyter notebooks for exploration
- `data/` - All data files organized by purpose
