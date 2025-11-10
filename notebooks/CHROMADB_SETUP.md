# ChromaDB Setup for query_chromadb.ipynb

## Database: chroma_ols20_nonols4

**Location**: `notebooks/chroma_ols20_nonols4/`
**Collection**: `combined_embeddings`
**Size**: 3.4GB (gitignored)
**Embeddings**: 452,942 embeddings

## Contents

This ChromaDB contains embeddings from **24 curated ontologies**:
- **20 OLS ontologies** (filtered from full OLS catalog)
- **4 non-OLS ontologies** (from BioPortal)

This is the final curated ontology set used for METPO semantic mapping.

## Source

Derived from the 300GB OLS SQLite embedding file through the following pipeline:
1. Filter OLS embeddings to 20 most relevant ontologies
2. Generate embeddings for 4 non-OLS ontologies from BioPortal
3. Combine into single ChromaDB collection

## Regeneration

To recreate this database from scratch on the Ubuntu NUC:

```bash
# On Ubuntu NUC at ~/gitrepos/metpo
# This was created through the embedding generation pipeline
# See Makefile targets: embed-ols-terms, embed-non-ols-terms
```

## Copying from Ubuntu NUC

To copy this database to another machine:

```bash
# From metpo repository root
rsync -avz --progress ubuntu:~/gitrepos/metpo/notebooks/chroma_ols20_nonols4/ notebooks/chroma_ols20_nonols4/
```

Where `ubuntu` is an SSH host alias (see `~/.ssh/config`).

## Usage in Notebook

The `query_chromadb.ipynb` notebook queries this database to demonstrate:
- Fast semantic similarity search
- Filtering by ontology
- Multi-term queries

The notebook uses OpenAI text-embedding-3-small (1536 dimensions) for query embeddings.
