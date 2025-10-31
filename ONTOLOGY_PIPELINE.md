# Ontology Embedding Pipeline

Robust pipeline for fetching non-OLS ontologies from BioPortal, extracting terms with ROBOT, and generating embeddings for ChromaDB.

## Overview

This pipeline handles:
- Downloading ontologies from BioPortal (with failure detection)
- Extracting terms using ROBOT SPARQL queries (with 0-byte detection)
- Tracking successes/failures in manifest
- Logging all errors for review
- Processing only successfully extracted ontologies

## Quick Start

```bash
# 1. Set up environment
export BIOPORTAL_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"

# 2. Download all non-OLS ontologies from BioPortal
make download-non-ols-bioportal-ontologies

# 3. Generate TSV files with ROBOT queries
make generate-non-ols-tsvs

# 4. Update manifest by scanning filesystem
make scan-manifest

# 5. View status
make view-manifest
make view-logs

# 6. Embed successful extractions to ChromaDB
make embed-non-ols-terms
```

## Design Philosophy

**Clean separation of concerns:**
- **Python scripts** = Single-purpose functions with clear exit codes (0=success, 1=failure)
- **Make** = Dependency management and orchestration (no shell conditionals)
- **Manifest** = Filesystem state tracking (updated by scan, not inline)

This means:
- No `subprocess.run()` or `os.system()` to call other Python scripts
- No complex `if/then/else` in Makefile targets
- Python does Python (error handling, validation, logging)
- Make does Make (dependencies, pattern rules)

## Non-OLS Ontologies Covered

The pipeline processes these BioPortal-only ontologies:

- **MPO** - MPO/RIKEN Microbial Phenotype Ontology
- **OMP** - Ontology of Microbial Phenotypes
- **BIPON** - Bacterial interlocked Process Ontology
- **D3O** - D3O/DSMZ Digital Diversity Ontology
- **FMPM** - Food Matrix for Predictive Microbiology
- **GMO** - Growth Medium Ontology
- **HMADO** - Human Microbiome and Disease Ontology
- **ID-AMR** - Infectious Diseases and Antimicrobial Resistance
- **MCCV** - Microbial Culture Collection Vocabulary
- **MEO** - Metagenome and Environment Ontology
- **miso** - Microbial Conditions Ontology
- **OFSMR** - Open Predictive Microbiology Ontology
- **TYPON** - Microbial Typing Ontology

## Property Coverage

The SPARQL query (`sparql/extract_for_embeddings.rq`) now covers diverse property patterns found across ontologies:

### Labels
- `rdfs:label` (all ontologies)
- `skos:prefLabel` (GMO)
- `dc:title` (D3O)
- `spin:labelTemplate` (N4L)

### Synonyms
- `oboInOwl:hasExactSynonym`, `hasBroadSynonym`, `hasNarrowSynonym`, `hasRelatedSynonym` (OMP, BIPON)
- `skos:altLabel` (GMO)
- `owl:altLabel` (FMPM)
- `obo#Synonym` (BIPON)

### Definitions
- `IAO:0000115` (OMP - standard OBO definition)
- `skos:definition` (GMO)
- `rdfs:comment` (D3O, all)
- `obo#Definition` (BIPON)

## Tracking System

### Manifest (`.ontology_manifest.json`)

Tracks state of each ontology:

```json
{
  "ontologies": {
    "D3O": {
      "status": "success",
      "fetched_at": "2025-10-31T14:23:45",
      "source": "bioportal",
      "file_path": "non-ols/D3O.owl",
      "file_size_bytes": 309000,
      "robot_query_status": "success",
      "tsv_path": "notebooks/non-ols-terms/D3O.tsv",
      "tsv_size_bytes": 45000,
      "term_count": 411
    },
    "HMADO": {
      "status": "empty",
      "fetched_at": "2025-10-31T14:24:12",
      "source": "bioportal",
      "file_path": "non-ols/HMADO.owl",
      "file_size_bytes": 75
    }
  }
}
```

### Logs

- **`.ontology_fetch.log`** - Failed downloads with timestamps
- **`.robot_query.log`** - Failed/empty ROBOT queries with details

### Commands

```bash
# Update manifest by scanning directories
make scan-manifest

# View manifest (formatted JSON)
make view-manifest

# View error logs
make view-logs

# Manual manifest updates
uv run update-manifest --ontology D3O --status success --file non-ols/D3O.owl
uv run update-manifest --ontology D3O --robot-status success --tsv notebooks/non-ols-terms/D3O.tsv --term-count 411
```

## Manual Ontology Addition

To add ontologies not in BioPortal (like N4L):

```bash
# 1. Place file in non-ols/
cp ~/Downloads/n4l_merged.owl non-ols/

# 2. Query with ROBOT
make notebooks/non-ols-terms/n4l_merged.tsv

# 3. Update manifest
make scan-manifest
```

The embedding script will automatically pick up all `*.tsv` files in `notebooks/non-ols-terms/`.

## Robustness Features

### Failure Detection
- **Empty downloads**: Files < 1KB removed and logged
- **0-byte TSVs**: Detected and logged (ROBOT query failed)
- **Empty TSVs**: Detected and logged (query succeeded but no results)

### Continuation
- Uses `-` prefix in Makefile to continue on errors
- Each ontology processed independently
- Manifest tracks partial progress

### Idempotency
- Manifest prevents re-downloading successful fetches
- TSV generation checks for existing OWL files
- Embedding script skips already-embedded terms

## Workflow Details

### 1. Download (`download-ontology` script)
**What it does:**
- Fetches from BioPortal API using `requests` library
- Validates file size (must be > 1KB)
- Logs failures to `.ontology_fetch.log`
- Exits with code 0 (success) or 1 (failure)

**What it does NOT do:**
- Update manifest (Make calls `scan-manifest` separately)
- Call other scripts
- Make decisions about what to do next

### 2. Query (`query-ontology` script)
**What it does:**
- Runs ROBOT via `subprocess` (external tool, not Python)
- Validates output (checks file exists and has content)
- Counts extracted terms
- Logs failures/empty results to `.robot_query.log`
- Exits with code 0 (success) or 1 (failure)

**What it does NOT do:**
- Update manifest (Make calls `scan-manifest` separately)
- Call other scripts
- Re-download files

### 3. Scan Manifest (`scan-manifest` script)
**What it does:**
- Scans `non-ols/` and `notebooks/non-ols-terms/` directories
- Checks file sizes and term counts
- Updates `.ontology_manifest.json` with current state
- Called manually after download/query phases

**Separation of concerns:**
- Download/query scripts focus on their single job
- Manifest tracking is a separate concern
- Make orchestrates the workflow

### 4. Embed (`embed_ontology_to_chromadb.py`)
**What it does:**
- Processes all TSVs in `notebooks/non-ols-terms/`
- Extracts ontology ID from filename
- Skips already-embedded terms
- Concatenates: `label; synonym1; synonym2; definition`
- Generates OpenAI embeddings
- Stores in ChromaDB collection

## Troubleshooting

### Download failures
```bash
# View which ontologies failed
make view-logs | grep FETCH_FAILED

# Retry specific ontology
make non-ols/HMADO.owl
```

### Query failures
```bash
# View which queries failed/empty
make view-logs | grep QUERY

# Retry specific query
make notebooks/non-ols-terms/D3O.tsv
```

### Check manifest status
```bash
# See summary counts
uv run scan-manifest --verbose

# Check specific ontology
make view-manifest | grep -A10 '"D3O"'
```

## Configuration

### Environment Variables
- `BIOPORTAL_API_KEY` - Required for downloads
- `OPENAI_API_KEY` - Required for embeddings

### Paths (configurable in Makefile)
- OWL files: `non-ols/*.owl` or `non-ols/*.ttl`
- TSV outputs: `notebooks/non-ols-terms/*.tsv`
- ChromaDB: `./embeddings_chroma` (default)

## Cost Estimation

OpenAI embedding costs (~$0.00002 per term):
- D3O (411 terms): ~$0.008
- OMP (2,728 terms): ~$0.055
- All 13 ontologies (~10,000 terms est.): ~$0.20

Check manifest for exact term counts before embedding.
