# METPO Ontology Alignment Pipeline

This directory contains tools for aligning METPO terms with external ontologies using semantic embeddings and structural coherence analysis.

## Overview

The pipeline evaluates METPO alignment with external ontologies through:
1. **Ontology selection** - Categorize ontologies by relevance to microbial phenotypes
2. **Semantic matching** - Find similar terms using OpenAI embeddings + ChromaDB
3. **Coherence validation** - Verify structural alignment using OAKLib
4. **Candidate generation** - Identify high-quality alignment candidates

## Prerequisites

### Required
- Python 3.11+
- OpenAI API key (set in `.env` or `OPENAI_API_KEY` environment variable)
- ChromaDB with OLS ontology embeddings
- OAKLib and dependencies

### Install Dependencies
```bash
cd /path/to/metpo
pip install -e ".[alignment]"  # or install individually: click, chromadb, openai, oaklib, pandas, requests
```

## Using the Pipeline

### Via Makefile (Recommended)

All pipeline steps are available as Makefile targets:

```bash
# Show all available targets and help
make help-alignment

# Run complete pipeline
make alignment-run-all

# Or run individual steps
make alignment-fetch-ontology-names    # Fetch ontology metadata from OLS4
make alignment-categorize-ontologies   # Categorize by relevance
make alignment-query-metpo-terms       # Query METPO against ChromaDB (requires OPENAI_API_KEY)
make alignment-analyze-matches         # Analyze match quality
make alignment-analyze-coherence       # Compute structural coherence
make alignment-identify-candidates     # Find high-quality candidates

# Cleanup
make clean-alignment-results   # Clean results only
make clean-alignment-all       # Clean all including catalog
```

### Via Individual Scripts

All scripts support `--help` for detailed options:

### 1. Ontology Preparation

#### fetch_ontology_names.py
Fetches ontology metadata from EBI OLS4 API and merges with size data.

```bash
python fetch_ontology_names.py \
  --sizes-csv ontology_sizes.csv \
  --output-csv ontology_catalog.csv \
  --api-delay 0.5
```

**Inputs**: `ontology_sizes.csv` (ontology size counts)  
**Outputs**: `ontology_catalog.csv` (sizes + titles + descriptions)

#### categorize_ontologies.py
Categorizes ontologies by relevance using keyword-based scoring.

```bash
python categorize_ontologies.py \
  --input-csv ontology_catalog.csv \
  --output-prefix ontologies
```

**Inputs**: `ontology_catalog.csv`  
**Outputs**:
- `ontologies_very_appealing.csv` - High relevance (OMP, APO, PATO, etc.)
- `ontologies_in_between.csv` - Medium relevance
- `ontologies_not_appealing.csv` - Low relevance (NCBItaxon, SwissLipids, etc.)

**Scoring criteria**:
- Bacterial/microbial focus: +15 points
- Phenotype/trait terms: +12 points
- Antimicrobial resistance: +14 points
- Large size (>500K): -10 points (unless highly relevant)

### 2. Data Migration

#### migrate_to_chromadb_resilient.py
Migrates embeddings from SQLite databases to ChromaDB.

```bash
python migrate_to_chromadb_resilient.py \
  --db-path ./embeddings.db \
  --chroma-path ./embeddings_chroma \
  --collection-name ols_embeddings \
  --batch-size 1000
```

**Use case**: Convert OLS ontology embeddings from SQLite to ChromaDB for vector search.

### 3. Semantic Matching

#### query_metpo_terms.py
Queries METPO terms against ChromaDB to find similar external terms.

```bash
python query_metpo_terms.py \
  --metpo-tsv ../src/templates/metpo_sheet.tsv \
  --chroma-path ./metpo_relevant_chroma \
  --collection-name metpo_relevant_embeddings \
  --output metpo_relevant_matches.csv \
  --top-n 5
```

**Inputs**:
- METPO template TSV with term definitions
- ChromaDB collection with OLS embeddings
- OpenAI API for query embeddings

**Outputs**: `metpo_relevant_matches.csv`

**Columns**: `metpo_id`, `metpo_label`, `metpo_parents`, `query_text`, `match_id`, `match_document`, `match_ontology`, `match_iri`, `distance`, `rank`

### 4. Match Analysis

#### analyze_matches.py
Analyzes match quality and coverage statistics.

```bash
python analyze_matches.py \
  --input-csv metpo_relevant_matches.csv \
  --good-match-threshold 0.9
```

**Outputs**: Statistics on match quality, ontology coverage, distance distributions

#### analyze_sibling_coherence.py
Advanced structural coherence analysis using OAKLib.

```bash
python analyze_sibling_coherence.py \
  --matches-csv metpo_relevant_matches.csv \
  --metpo-tsv ../src/templates/metpo_sheet.tsv \
  --output sibling_coherence_results.csv \
  --max-terms 100 \
  --debug
```

**Process**:
1. For each METPO-external match pair
2. Fetch siblings from both METPO and external ontology (via OAKLib)
3. Check how many METPO siblings also match external siblings
4. Calculate coherence score: `coherent_siblings / metpo_siblings`

**Outputs**: `sibling_coherence_results.csv` or `full_coherence_results.csv`

**Columns**: `metpo_id`, `metpo_label`, `match_iri`, `match_ontology`, `match_distance`, `metpo_sibling_count`, `external_sibling_count`, `coherent_sibling_count`, `coherence_score`

#### analyze_coherence_results.py
Summarizes coherence findings and identifies alignment candidates.

```bash
python analyze_coherence_results.py \
  --results-csv full_coherence_results.csv \
  --matches-csv metpo_relevant_matches.csv
```

**Identifies**:
- High coherence cases (≥0.5): METPO structure aligns with external ontology
- Low coherence cases (<0.2): Structural mismatch despite semantic similarity
- Alignment candidates: coherence ≥0.5, distance <0.5, ≥3 siblings

**Outputs**: `alignment_candidates.csv` - Terms ready for formal alignment

## Data Files

### Input Data
- `ontology_sizes.csv` - Size counts for ontologies from OLS
- `metpo-report.tsv` - METPO term definitions (from main repo)
- `*.db` - SQLite databases with ontology embeddings (fao, mco, mpo, n4l, omp, MicrO)
- `metpo_relevant_chroma/` - ChromaDB with filtered ontology embeddings

### Intermediate Results
- `ontology_catalog.csv` - Ontology metadata (sizes + titles + descriptions)
- `ontologies_*.csv` - Categorized ontologies
- `metpo_chromadb_matches.csv` - Raw embedding matches
- `metpo_relevant_matches.csv` - Filtered matches from relevant ontologies
- `oba_matches.csv` - OBA-specific matches (historical)

### Analysis Outputs
- `sibling_coherence_results.csv` - Coherence scores for sample
- `full_coherence_results.csv` - Complete coherence analysis
- `alignment_candidates.csv` - High-confidence candidates for alignment

## Interactive Notebooks

- `explore_embeddings.ipynb` - Explore embedding space, visualize clusters
- `query_chromadb.ipynb` - Interactive queries and experiments

## Typical Workflow

### Using Make (Recommended)
```bash
# Run the entire pipeline
make alignment-run-all

# Or run steps individually as needed
make alignment-fetch-ontology-names      # 1. Prepare catalog (one-time)
make alignment-categorize-ontologies     # 2. Categorize (one-time)
make alignment-query-metpo-terms         # 3. Query with embeddings
make alignment-analyze-coherence         # 4. Compute coherence
make alignment-identify-candidates       # 5. Find candidates
```

### Using Scripts Directly
```bash
# 1. Prepare ontology catalog (one-time)
cd notebooks
python fetch_ontology_names.py
python categorize_ontologies.py

# 2. Migrate embeddings to ChromaDB (if needed)
python migrate_to_chromadb_resilient.py \
  --db-path ./oba_chroma.db \
  --chroma-path ./metpo_relevant_chroma

# 3. Query METPO terms
python query_metpo_terms.py \
  --output metpo_relevant_matches.csv

# 4. Analyze matches
python analyze_matches.py --input-csv metpo_relevant_matches.csv

# 5. Compute coherence
python analyze_sibling_coherence.py \
  --matches-csv metpo_relevant_matches.csv \
  --output full_coherence_results.csv

# 6. Identify alignment candidates
python analyze_coherence_results.py \
  --results-csv full_coherence_results.csv
```

## Key Concepts

### Semantic Similarity
- Uses OpenAI `text-embedding-3-small` model
- Combines term label + parent labels for context
- Distance < 0.5 typically indicates good semantic match
- Distance < 0.3 indicates very strong match

### Structural Coherence
- Measures whether hierarchical relationships align
- High coherence (≥0.5): METPO siblings match external siblings
- Validates that ontologies agree on domain structure, not just labels
- Coherence = 1.0 means perfect structural agreement

### Ontology Selection Criteria
- **Very Appealing**: Bacterial phenotypes, traits, resistance (score ≥ 10)
- **In-Between**: Potentially useful, unclear relevance (score -4 to 9)
- **Not Appealing**: Unrelated domains, too large (score ≤ -5)

## Environment Variables

```bash
# Required
export OPENAI_API_KEY="sk-..."

# Optional
export CHROMADB_HOST="localhost"
export CHROMADB_PORT="8000"
```

## Troubleshooting

**ChromaDB connection issues**: Ensure collection exists, path is correct
**OAKLib adapter failures**: Some ontologies may not be available via OAKLib
**OpenAI rate limits**: Add delays between queries or use batch processing
**Memory issues**: Process large datasets in batches using `--max-terms`

## See Also

- `/docs/metpo_alignment_handoff.md` - Detailed pipeline documentation
- `/docs/METPO_JUSTIFICATION.md` - Rationale for METPO development
- `/analysis/` - BiPortal submission analysis tools
