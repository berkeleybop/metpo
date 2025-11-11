# CLI Reference

METPO provides 30+ command-line tools for ontology alignment, database reconciliation, and analysis workflows. All commands are installed via `uv` and use standardized option names.

## Installation

```bash
# Install core dependencies
make install

# Install for specific workflows
make install-dev           # Development tools
make install-literature    # Literature mining
make install-databases     # Database workflows
make install-notebooks     # Alignment pipeline

# Or install everything
make install-all
```

## Common Option Patterns

All CLI tools follow consistent naming conventions:

| Option | Short | Description |
|--------|-------|-------------|
| `--input-file` | `-i` | Input file path |
| `--output` | `-o` | Output file path |
| `--distance-threshold` | | Semantic distance threshold (0.0-1.0) |
| `--chroma-path` | | ChromaDB storage directory |
| `--debug` | | Enable verbose debug output |
| `--dry-run` / `--execute` | | Preview vs. execute mode |

## Tools by Category

### Pipeline Tools

Commands for the semantic alignment pipeline.

#### `categorize-ontologies`

Categorize ontologies by relevance to microbial phenotypes.

```bash
uv run categorize-ontologies \
  --input-file ontology_catalog.csv \
  --output-prefix ontologies
```

**Options:**
- `--input-file, -i`: Input ontology catalog CSV (default: `ontology_catalog.csv`)
- `--output-prefix`: Prefix for output files (creates `{prefix}_very_appealing.csv`, etc.)

**Outputs:**
- `ontologies_very_appealing.csv` - High relevance (score ≥10)
- `ontologies_in_between.csv` - Medium relevance (score -4 to 9)
- `ontologies_not_appealing.csv` - Low relevance (score ≤-5)

---

#### `fetch-ontology-names`

Fetch ontology metadata from OLS4 API and merge with size data.

```bash
uv run fetch-ontology-names \
  --input-file ontology_sizes.csv \
  --output ontology_catalog.csv \
  --api-delay 0.5
```

**Options:**
- `--input-file, -i`: Input CSV with ontology sizes
- `--output, -o`: Output merged catalog CSV (default: `ontology_catalog.csv`)
- `--api-delay`: Delay between API requests in seconds (default: 0.5)

**Outputs:** CSV with columns: `ontologyId`, `title`, `count`, `description`

---

#### `chromadb-semantic-mapper`

Query METPO terms against ChromaDB for semantic matches.

```bash
uv run chromadb-semantic-mapper \
  --input-file ../src/templates/metpo_sheet.tsv \
  --chroma-path ./metpo_relevant_chroma \
  --output metpo_matches.csv \
  --top-n 5
```

**Options:**
- `--input-file, -i`: METPO template TSV
- `--chroma-path`: ChromaDB storage directory (default: `./chroma_db`)
- `--output, -o`: Output matches CSV
- `--top-n`: Number of top matches per term (default: 5)
- `--collection-name`: ChromaDB collection name

**Requirements:** `OPENAI_API_KEY` environment variable

---

#### `analyze-matches`

Analyze semantic match quality and coverage statistics.

```bash
uv run analyze-matches \
  --input-file metpo_matches.csv \
  --distance-threshold 0.35
```

**Options:**
- `--input-file, -i`: Input matches CSV
- `--distance-threshold`: Threshold for good matches (default: 0.9)

**Outputs:** Statistics on match quality, ontology coverage, distance distributions

---

#### `analyze-sibling-coherence`

Compute structural coherence between METPO and external ontologies using OAKLib.

```bash
uv run analyze-sibling-coherence \
  --input-file metpo_matches.csv \
  --metpo-owl ../src/ontology/metpo.owl \
  --distance-threshold 0.35 \
  --output coherence_results.csv \
  --debug
```

**Options:**
- `--input-file, -i`: SSSOM TSV mappings file
- `--metpo-owl`: METPO OWL file path
- `--distance-threshold`: Distance threshold for matches (default: 0.9)
- `--output, -o`: Output coherence CSV
- `--debug`: Enable verbose output
- `--max-terms`: Limit analysis to first N terms

**Process:**
1. For each METPO-external match pair
2. Fetch siblings from both ontologies via OAKLib
3. Calculate coherence: `coherent_siblings / metpo_siblings`

**Outputs:** CSV with coherence scores and sibling counts

---

#### `analyze-coherence-results`

Summarize coherence findings and identify alignment candidates.

```bash
uv run analyze-coherence-results \
  --results-file coherence_results.csv \
  --mappings-file metpo_matches.sssom.tsv
```

**Options:**
- `--results-file, -r`: Coherence results CSV
- `--mappings-file, -m`: SSSOM TSV mappings file

**Identifies:**
- High coherence cases (≥0.5): Good structural alignment
- Moderate coherence (0.3-0.5): Partial alignment
- Best candidates: High coherence + low distance + ≥3 siblings

**Outputs:** `alignment_candidates.csv`

---

#### `embed-ontology-to-chromadb`

Embed ontology terms into ChromaDB collection.

```bash
uv run embed-ontology-to-chromadb \
  --input-file terms.tsv \
  --chroma-path ./chroma_db \
  --collection-name my_ontology
```

**Options:**
- `--input-file, -i`: TSV file with ontology terms
- `--chroma-path`: ChromaDB storage directory
- `--collection-name`: Name for ChromaDB collection

**Requirements:** `OPENAI_API_KEY` environment variable

---

### Database Tools

Commands for ChromaDB management and migration.

#### `migrate-to-chromadb`

Migrate embeddings from SQLite to ChromaDB with optional filtering.

```bash
# Migrate all embeddings
uv run migrate-to-chromadb \
  --db-path embeddings.db \
  --chroma-path ./chroma_db

# Migrate only relevant ontologies
uv run migrate-to-chromadb \
  --db-path embeddings.db \
  --include aro --include eco --include envo \
  --chroma-path ./filtered_chroma
```

**Options:**
- `--db-path`: SQLite database file path
- `--chroma-path`: ChromaDB storage directory (default: `./chroma_db`)
- `--include <ontology>`: Include only specific ontologies (repeatable)
- `--exclude <ontology>`: Exclude specific ontologies (repeatable)
- `--batch-size`: Embeddings per batch (default: 1000)
- `--limit`: Limit to first N embeddings (for testing)
- `--no-resume`: Start from beginning instead of resuming

---

#### `audit-chromadb`

Audit ChromaDB collection integrity and statistics.

```bash
uv run audit-chromadb \
  --chroma-path ./chroma_db \
  --collection-name my_collection
```

**Options:**
- `--chroma-path`: ChromaDB storage directory
- `--collection-name`: Collection to audit

**Outputs:** Count, metadata stats, sample documents

---

#### `combine-chromadb`

Combine multiple ChromaDB collections into one.

```bash
uv run combine-chromadb \
  --source-paths chroma1/ chroma2/ chroma3/ \
  --target-path combined_chroma/ \
  --collection-name merged
```

**Options:**
- `--source-paths`: List of source ChromaDB directories
- `--target-path`: Target ChromaDB directory
- `--collection-name`: Name for combined collection

---

#### `filter-ols-chromadb`

Filter ChromaDB collection by ontology source.

```bash
uv run filter-ols-chromadb \
  --input-chroma ./all_chroma \
  --output-chroma ./filtered_chroma \
  --include aro --include eco --include envo
```

**Options:**
- `--input-chroma`: Source ChromaDB directory
- `--output-chroma`: Target ChromaDB directory
- `--include <ontology>`: Include only these ontologies (repeatable)
- `--exclude <ontology>`: Exclude these ontologies (repeatable)

---

### Analysis Tools

Commands for ontology and match quality analysis.

#### `analyze-ontology-value`

Analyze ontology value for METPO alignment.

```bash
uv run analyze-ontology-value \
  --input-file matches.csv
```

**Options:**
- `--input-file, -i`: Input matches CSV

**Outputs:** Statistics on ontology coverage, match quality, value scores

---

#### `analyze-match-quality`

Analyze match quality by distance for each ontology.

```bash
uv run analyze-match-quality \
  mappings.sssom.tsv \
  --distance-threshold 0.35
```

**Arguments:**
- `sssom_file`: SSSOM TSV file path

**Options:**
- `--distance-threshold`: Threshold for high-quality matches (default: 0.35)

**Outputs:** Table showing match quality statistics per ontology

---

### BactoTraits Tools

Commands for BactoTraits database reconciliation.

#### `reconcile-bactotraits-coverage`

Reconcile BactoTraits fields with METPO coverage.

```bash
uv run reconcile-bactotraits-coverage
```

**Outputs:** Reports on field coverage and mapping quality

---

#### `reconcile-madin-coverage`

Reconcile Madin database fields with METPO coverage.

```bash
uv run reconcile-madin-coverage
```

**Outputs:** Reports on field coverage and mapping quality

---

#### `bactotraits-metpo-set-difference`

Analyze set difference between BactoTraits and METPO terms.

```bash
uv run bactotraits-metpo-set-difference
```

**Outputs:** Terms in BactoTraits not covered by METPO

---

#### `create-bactotraits-field-mappings`

Generate field mapping metadata for MongoDB import.

```bash
uv run create-bactotraits-field-mappings \
  --provider-file local/bactotraits/BactoTraits_databaseV2_Jun2022.csv \
  --kg-microbe-file local/bactotraits/BactoTraits.tsv \
  --output metadata/databases/bactotraits/bactotraits_field_mappings.json
```

**Options:**
- `--provider-file`: Original BactoTraits CSV
- `--kg-microbe-file`: KG-Microbe version TSV
- `--output, -o`: Output JSON file
- `--db-name`: MongoDB database name
- `--collection-name`: MongoDB collection name

---

#### `create-stubs`

Create ROBOT template stubs from multiple input files.

```bash
uv run create-stubs \
  --output stubs.tsv \
  file1.tsv file2.tsv file3.tsv
```

**Options:**
- `--output, -o`: Output stub file
- `input_files`: One or more input TSV files (as arguments)

---

#### `migrate-range-metadata`

Migrate range metadata to minimal_classes.tsv.

```bash
uv run migrate-range-metadata \
  --bactotraits bactotraits.tsv \
  --minimal minimal_classes.tsv \
  --output minimal_classes_enhanced.tsv \
  --execute
```

**Options:**
- `--dry-run` / `--execute`: Preview or execute changes (default: dry-run)
- `--bactotraits`: BactoTraits TSV file path
- `--minimal`: Minimal classes TSV file path
- `--output, -o`: Output enhanced TSV

---

#### `update-manifest`

Update ROBOT manifest with new template files.

```bash
uv run update-manifest
```

---

#### `scan-manifest`

Scan and validate ROBOT manifest entries.

```bash
uv run scan-manifest
```

---

#### `download-ontology`

Download ontology file from remote source.

```bash
uv run download-ontology \
  --url https://example.org/ontology.owl \
  --output external/ontologies/myonto.owl
```

**Options:**
- `--url`: Ontology URL
- `--output, -o`: Local output path

---

#### `query-ontology`

Query ontology using OAKLib adapters.

```bash
uv run query-ontology \
  --ontology-file ontology.owl \
  --query "search term"
```

**Options:**
- `--ontology-file`: Ontology file path
- `--query`: Search query string

---

### Utility Tools

General-purpose utility commands.

#### `extract-rank-triples`

Extract taxonomy rank triples from NCBI nodes.dmp.

```bash
uv run extract-rank-triples \
  --input-file nodes.dmp \
  --output ranks.ttl
```

**Options:**
- `--input-file, -i`: NCBI nodes.dmp file
- `--output, -o`: Output Turtle file

**Outputs:** RDF triples in Turtle format

---

#### `convert-chem-props`

Convert chemical property data formats.

```bash
uv run convert-chem-props \
  --input-file properties.csv \
  --output properties.ttl
```

**Options:**
- `--input-file, -i`: Input properties file
- `--output, -o`: Output file

---

#### `import-bactotraits`

Import BactoTraits data to MongoDB.

```bash
uv run import-bactotraits \
  --input-file BactoTraits.tsv \
  --db-name metpo \
  --collection bactotraits
```

**Options:**
- `--input-file, -i`: BactoTraits TSV file
- `--db-name`: MongoDB database name
- `--collection`: MongoDB collection name

**Requirements:** MongoDB running on `MONGO_HOST:MONGO_PORT`

---

## Environment Variables

All tools respect these environment variables (configure in `.env`):

```bash
# API Keys
OPENAI_API_KEY=sk-...           # Required for embedding tools
NCBI_API_KEY=...                # Optional, for PubMed fetching
BIOPORTAL_API_KEY=...           # Optional, for BioPortal downloads

# Database
MONGO_HOST=localhost            # MongoDB host
MONGO_PORT=27017                # MongoDB port
MONGO_DB=metpo                  # MongoDB database name
CHROMA_PATH=./chroma_db         # ChromaDB storage path

# Pipeline settings
DISTANCE_THRESHOLD=0.35         # Semantic match threshold
EMBEDDING_BATCH_SIZE=1000       # Batch size for embeddings
API_DELAY=0.5                   # Delay between API requests (seconds)

# Development
DEBUG=false                     # Enable debug output
DRY_RUN=true                    # Default to dry-run mode
LOG_LEVEL=INFO                  # Logging level
```

## Getting Help

All commands support `--help`:

```bash
uv run <command> --help
```

## See Also

- [Root README.md](../README.md) - Main repository documentation
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [Makefile](../Makefile) - Automation workflows
- [literature_mining/README.md](../literature_mining/README.md) - Literature mining pipeline
- [docs/README.md](README.md) - Documentation index
