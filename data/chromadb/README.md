# ChromaDB Setup for query_chromadb.ipynb

## Database: chroma_ols20_nonols4

**Location**: `data/chromadb/chroma_ols20_nonols4/`
**Collection**: `combined_embeddings`
**Size**: 3.4GB (gitignored)
**Embeddings**: 452,942 embeddings from 24 curated ontologies
**Embedding Model**: OpenAI text-embedding-3-small (1536 dimensions)
**Cost**: ~$45-50 for embedding generation

## Contents

This ChromaDB contains embeddings from **24 curated ontologies**:
- **20 OLS ontologies** (filtered from ~500 available in OLS4)
- **4 non-OLS ontologies** (from BioPortal, not available in OLS)

### Complete Ontology List

| Ontology | Count | Description |
|----------|------:|-------------|
| upheno | 192,001 | Unified Phenotype Ontology - integrated cross-species phenotypes |
| go | 84,737 | Gene Ontology - biological processes, molecular functions, cellular components |
| oba | 73,148 | Ontology of Biological Attributes - traits and phenotypes |
| flopo | 35,359 | Flora Phenotype Ontology - plant phenotypes |
| micro | 17,645 | Ontology of Microbial Phenotypes - microbial traits |
| pato | 9,061 | Phenotype And Trait Ontology - qualities and attributes |
| envo | 7,365 | Environment Ontology - environmental conditions |
| fypo | 5,988 | Fission Yeast Phenotype Ontology |
| bco | 4,486 | Biological Collections Ontology |
| zfa | 3,576 | Zebrafish Anatomy Ontology |
| omp | 2,870 | Ontology of Microbial Phenotypes (BioPortal) |
| mco | 2,698 | Microbial Conditions Ontology |
| agro | 2,554 | Agronomy Ontology |
| xpo | 2,515 | Xenopus Phenotype Ontology |
| to | 1,974 | Plant Trait Ontology |
| wbphenotype | 1,798 | C. elegans Phenotype Ontology |
| mpo | 1,756 | Mammalian Phenotype Ontology |
| d3o | 1,478 | Diarrheal Disease Ontology (BioPortal) |
| bipon | 1,270 | Biofilm Phenotype Ontology (BioPortal) |
| apollo_sv | 831 | Apollo Structured Vocabulary |
| fmpm | 318 | Food Microbiology Phenotype Model (BioPortal) |
| miro | 214 | Mosquito Insecticide Resistance Ontology |
| gaz | 208 | Gazetteer - geographic locations |
| planp | 42 | Planarian Phenotype Ontology |

**Total**: 452,942 embeddings across 24 ontologies

### What This Database Does NOT Contain

This database **excludes** many ontologies from the full OLS catalog (~500 ontologies):

**Deliberately Excluded for Low Relevance**:
- **CHEBI** - Chemical Entities of Biological Interest (ROI: 0.009 matches per 1K embeddings)
- **NCIT** - NCI Thesaurus (too broad, clinical focus)
- **SNOMED CT** - Clinical terminology (not phenotypes)
- **Full NCBITaxon** - Taxonomy database (organisms not traits)
- **Anatomy ontologies** - UBERON, FMA, etc. (structures not phenotypes)
- **Clinical ontologies** - DOID, HP focused on human disease
- **Molecular ontologies** - SO, MI, etc. (sequences/interactions not phenotypes)

**Filtering Strategy**:
1. Started with OLS catalog of ~500 ontologies
2. Keyword-based relevance scoring (microbial, phenotype, trait, environment keywords)
3. Manual curation to select 20 most relevant OLS ontologies
4. Added 4 critical non-OLS ontologies from BioPortal (OMP, D3O, BIPON, FMPM)

**Result**: 24 ontologies covering microbial phenotypes, traits, and environmental conditions

## Source

### Generation Pipeline

This database was created from two sources:

**1. OLS Embeddings (20 ontologies)**
   - Started with 300GB OLS SQLite embedding file (all ~500 OLS ontologies pre-embedded)
   - Filtered to 20 most relevant ontologies for microbial phenotypes
   - Extracted and loaded into ChromaDB

**2. Non-OLS Embeddings (4 ontologies)**
   - Downloaded OWL files from BioPortal: OMP, D3O, BIPON, FMPM
   - Extracted terms with ROBOT: `make data/pipeline/non-ols-terms/%.tsv`
   - Generated embeddings via OpenAI API
   - Combined with OLS embeddings in ChromaDB

### Makefile Targets

```bash
# Regenerate non-OLS embeddings (requires OpenAI API key)
make embed-non-ols-terms

# Extract terms from BioPortal OWL files
make data/pipeline/non-ols-terms/OMP.tsv
make data/pipeline/non-ols-terms/D3O.tsv
make data/pipeline/non-ols-terms/BIPON.tsv
make data/pipeline/non-ols-terms/FMPM.tsv
```

**Note**: Regenerating the full database requires:
- 300GB OLS SQLite file (on Ubuntu NUC)
- OpenAI API key (~$45-50 cost for non-OLS embeddings)
- Significant compute time

## Copying from Ubuntu NUC

To copy this database to another machine:

```bash
# From metpo repository root
rsync -avz --progress ubuntu:~/gitrepos/metpo/data/chromadb/chroma_ols20_nonols4/ data/chromadb/chroma_ols20_nonols4/
```

Where `ubuntu` is an SSH host alias defined in `~/.ssh/config`:
```
Host ubuntu
    HostName 192.168.0.204
    User mark
    IdentityFile ~/.ssh/id_ed25519_to_ubuntu
```

## Usage

### Via CLI Tool (Recommended)

Use the `chromadb-semantic-mapper` CLI tool for production workflows:

```bash
uv run chromadb-semantic-mapper \
  --metpo-tsv src/templates/metpo_sheet.tsv \
  --chroma-path data/chromadb/chroma_ols20_nonols4 \
  --collection-name combined_embeddings \
  --output data/mappings/metpo_mappings.sssom.tsv \
  --max-rank 20 \
  --min-similarity 0.85
```

See `docs/cli-reference.md` for complete options.

### In Python Scripts

```python
import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(
    path="data/chromadb/chroma_ols20_nonols4",
    settings=Settings(anonymized_telemetry=False)
)

collection = client.get_collection(name="combined_embeddings")
print(f"Collection loaded: {collection.count():,} embeddings")

# Query with filtering
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=10,
    where={"ontologyId": "micro"},  # Filter to microbial phenotypes
    include=["documents", "metadatas", "distances"]
)
```

### In Makefile Pipeline

```bash
# Generate SSSOM mappings using this ChromaDB
make alignment-query-metpo-terms

# Uses scripts/pipeline/chromadb_semantic_mapper.py
# Output: data/mappings/metpo_mappings.sssom.tsv
```

## Collection Schema

Each embedding in the `combined_embeddings` collection has:

**Metadata**:
- `ontologyId`: Lowercase ontology prefix (e.g., "micro", "envo", "omp")
- `iri`: Full term IRI (e.g., "http://purl.obolibrary.org/obo/MICRO_0000001")
- `source`: "ols" or "bioportal"

**Document**: Combined label and definition text used for embedding

**Embedding**: 1536-dimension vector from OpenAI text-embedding-3-small

## Related Files

- **CLI Tools**:
  - `metpo/pipeline/chromadb_semantic_mapper.py` - Generate SSSOM mappings
  - `metpo/pipeline/embed_ontology_to_chromadb.py` - Create embeddings
  - `metpo/database/audit_chromadb.py` - Inspect/diagnose collections
  - `metpo/database/combine_chromadb.py` - Merge collections
  - `metpo/database/filter_ols_chromadb.py` - Subset by ontology
- **Data**: `data/mappings/metpo_mappings*.sssom.tsv` - Output mappings
- **Pipeline**: `data/pipeline/non-ols-terms/*.tsv` - Non-OLS term extractions
- **Docs**: `docs/cli-reference.md` - CLI tool documentation
