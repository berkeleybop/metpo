# scripts/database/

Database management and migration utilities for METPO's ChromaDB and SQLite databases.

These scripts handle database operations outside the main Makefile workflow.

## Scripts

### Database Integrity & Auditing

**audit_chromadb.py**
- **Purpose**: Database integrity checks - vector dimensions, ontology distribution
- **CLI**: ✅ Click interface (no args currently)
- **Checks**:
  - Vector dimension consistency
  - Ontology distribution across collections
  - Missing or malformed metadata
- **Usage**: `python scripts/database/audit_chromadb.py`
- **TODO**: Parameterize database paths (currently hardcoded)

### Database Operations

**combine_chromadb.py**
- **Purpose**: Merges OLS and non-OLS ChromaDB collections
- **CLI**: ✅ Click interface
- **Parameters**:
  - `--ols-path` - Path to OLS ChromaDB
  - `--non-ols-path` - Path to non-OLS ChromaDB
  - `--output-path` - Path for merged database
  - `--batch-size` - Batch size for processing (default: 1000)
- **Usage**:
  ```bash
  python scripts/database/combine_chromadb.py \
    --ols-path notebooks/ols_chroma/ \
    --non-ols-path notebooks/non_ols_chroma/ \
    --output-path notebooks/combined_chroma/
  ```
- **Status**: Production-ready

**filter_ols_chromadb.py**
- **Purpose**: Filters OLS ChromaDB to remove low-ROI ontologies
- **CLI**: ✅ Click interface
- **Parameters**:
  - `--input-path` - Input ChromaDB path
  - `--output-path` - Filtered output path
  - `--batch-size` - Batch size (default: 1000)
- **Usage**:
  ```bash
  python scripts/database/filter_ols_chromadb.py \
    --input-path notebooks/ols_chroma/ \
    --output-path notebooks/ols_chroma_filtered/
  ```
- **Status**: Production-ready

### Migration Tools

**migrate_to_chromadb_resilient.py**
- **Purpose**: Resilient SQLite to ChromaDB migration with error recovery
- **CLI**: ✅ Click interface
- **Parameters**:
  - `--db-path` - SQLite database path
  - `--chroma-path` - ChromaDB output path
  - `--batch-size` - Batch size (default: 1000)
  - `--include` - Ontology IDs to include (optional)
  - `--exclude` - Ontology IDs to exclude (optional)
- **Features**:
  - Error recovery with partial progress saving
  - Selective ontology migration
  - Batch processing for memory efficiency
- **Usage**:
  ```bash
  python scripts/database/migrate_to_chromadb_resilient.py \
    --db-path data.db \
    --chroma-path notebooks/chroma_db/
  ```
- **Status**: Historical migration tool (kept for reproducibility)
- **Note**: One-time migration from legacy SQLite to ChromaDB

## Design Philosophy

Scripts in this directory:
- ✅ Focus on database operations (ChromaDB, SQLite)
- ✅ Use Click CLI with clear parameters
- ✅ Handle errors gracefully (especially migrations)
- ✅ Batch processing for large datasets
- ⚠️ Parameterize paths (audit_chromadb.py needs update)

## Database Architecture

METPO uses ChromaDB for semantic search:

**Collections**:
- `ols_ontologies` - Terms from OLS4-registered ontologies
- `non_ols_ontologies` - Terms from BioPortal-only ontologies
- `combined` - Merged collection (via combine_chromadb.py)

**Vector Dimensions**: 1536 (OpenAI text-embedding-3-small)

**Metadata Schema**:
- `ontology_id` - Ontology prefix (e.g., "GO", "CHEBI")
- `term_id` - Full URI
- `label` - Human-readable label
- `definition` - Term definition (optional)

## Best Practices

When adding new database scripts:
1. Use Click for CLI interface
2. Accept all paths as parameters (no hardcoded paths)
3. Implement batch processing for large datasets
4. Add error recovery for long-running operations
5. Include progress indicators (tqdm)
6. Document database schema requirements
7. Add entry to this README

## Related

- `scripts/analysis/` - Data analysis tools
- `notebooks/embed_ontology_to_chromadb.py` - Embedding generation (Makefile workflow)
- `notebooks/chromadb_semantic_mapper.py` - Semantic search (Makefile workflow)
