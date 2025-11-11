# Semsql Databases for External Ontologies

This directory contains semsql database files (.db) generated from external ontology OWL files. These databases enable fast SQL queries via OAKLib without parsing large OWL files.

## Purpose

**Semsql databases** are SQLite files containing:
- Ontology terms (classes, properties, individuals)
- Hierarchical relationships (is_a, part_of, etc.)
- Labels, definitions, synonyms
- Logical axioms and restrictions

**Why both OWL and .db?**
- **OWL files** (`external/ontologies/`): Original source, human-readable, version-controlled
- **Semsql .db files** (`external/databases/`): Derived databases for fast querying, gitignored

**Workflow**: `ontology.owl` → (semsql conversion) → `ontology.db` → (OAKLib queries)

## Current Inventory

### **Currently on Ubuntu Server** (needs migration to this directory)

Located in `ubuntu:~/gitrepos/metpo/notebooks/` (will be moved here):

| Database | Size | Source OWL | Version | Last Modified | Purpose |
|----------|------|------------|---------|---------------|---------|
| **fao.db** | 696K | ❓ Unknown | Unknown | Jun 12, 2024 | Food Additive Ontology - chemical utilization analysis |
| **mco.db** | 64M | ❓ Unknown (OLS?) | Unknown | Jun 12, 2024 | Microbial Conditions Ontology - growth conditions |
| **MicrO-2025-03-20-merged.db** | 197M | ❓ Unknown | 2025-03-20 | Jun 12, 2024 | MicroPhenotypes Ontology - primary microbial traits |
| **mpo_v0.74.en_only.db** | 1.1M | ❓ Unknown | v0.74 | Jun 12, 2024 | MPO/RIKEN Microbial Phenotype Ontology (OLD VERSION) |
| **n4l_merged.db** | 8.6M | ✅ external/ontologies/manual/n4l_merged.owl | 2016 | Jun 12, 2024 | N4L phenotypic ontology - merged version |
| **omp.db** | 12M | ✅ external/ontologies/bioportal/OMP.owl | Current | Jun 12, 2024 | Ontology of Microbial Phenotypes |

### **Locally Available (in external/ontologies/) but NO .db yet**

These OWL files exist but have not been converted to semsql databases:

| Ontology | OWL Location | Size | .db Status | Priority |
|----------|-------------|------|------------|----------|
| BIPON | external/ontologies/bioportal/BIPON.owl | 3.5M | ❌ Missing | Medium |
| D3O | external/ontologies/bioportal/D3O.owl | 308K | ❌ Missing | Medium |
| FMPM | external/ontologies/bioportal/FMPM.owl | 324K | ❌ Missing | Medium |
| GMO | external/ontologies/bioportal/GMO.owl | 614K | ❌ Missing | Medium |
| ID-AMR | external/ontologies/bioportal/ID-AMR.owl | 52K | ❌ Missing | Low |
| MCCV | external/ontologies/bioportal/MCCV.owl | 28K | ❌ Missing | Low |
| MEO | external/ontologies/bioportal/MEO.owl | 487K | ❌ Missing | Medium |
| MISO | external/ontologies/bioportal/MISO.owl | 422K | ❌ Missing | Medium |
| MPO | external/ontologies/bioportal/MPO.owl | 67K | ❓ Have v0.74.db (old) | High - update! |
| OFSMR | external/ontologies/bioportal/OFSMR.owl | 344K | ❌ Missing | Low |
| TYPON | external/ontologies/bioportal/TYPON.owl | 46K | ❌ Missing | Low |

**Note**: We don't need .db files for every ontology - only those used for OAKLib querying (e.g., coherence analysis, sibling extraction). For simple embedding-based matching, OWL → TSV → ChromaDB is sufficient.

## Missing Source OWL Files

These .db files exist but we don't have the source OWL files:

| Database | Source Needed | Where to Get | Notes |
|----------|--------------|--------------|-------|
| fao.db | ❓ fao.owl | Unknown - possibly custom download | Food Additive Ontology |
| mco.db | ❓ mco.owl | OLS4 (https://www.ebi.ac.uk/ols4/ontologies/mco) | Microbial Conditions - in OLS |
| MicrO-2025-03-20-merged.db | ❓ MicrO-merged.owl | Custom merge? Check with team | MicroPhenotypes merged |

**Action needed**: Find original OWL sources or determine if these .db files are still needed.

## MPO Version Status

We have **two MPO versions**:

1. **mpo_v0.74.en_only.db** (1.1M, Jun 2024) - OLD version, English-only subset
   - Location: `ubuntu:notebooks/`
   - Source: Unknown (possibly filtered from full MPO)
   - **Status**: Likely obsolete

2. **MPO.owl** (67K, Nov 2024) - CURRENT version
   - Location: `external/ontologies/bioportal/MPO.owl`
   - Source: BioPortal (downloaded Nov 1, 2024)
   - **Status**: Current, should generate new MPO.db from this

**Recommendation**:
- Generate fresh `mpo.db` from current `MPO.owl`
- Archive or delete `mpo_v0.74.en_only.db`

## Migration Plan

### 1. Move existing .db files to this directory

On ubuntu server:
```bash
cd ~/gitrepos/metpo
git pull origin main  # Get external/databases/ directory
mkdir -p external/databases
mv notebooks/*.db external/databases/
```

On local machine:
```bash
rsync -avz ubuntu:~/gitrepos/metpo/external/databases/*.db external/databases/
```

### 2. Acquire missing OWL files

**High Priority (needed for analysis):**
```bash
# Download MCO from OLS4
curl -L "https://www.ebi.ac.uk/ols4/api/ontologies/mco/download" -o external/ontologies/ols/mco.owl

# Download MicrO (if available publicly)
# OR check if it's a custom merge - ask team
```

**Where to put them:**
- OLS ontologies → `external/ontologies/ols/` (create this directory)
- BioPortal ontologies → `external/ontologies/bioportal/` (already exists)
- Custom/merged → `external/ontologies/manual/` (already exists)

**Medium/Low Priority (only if needed for OAKLib analysis):**
- FAO: Search for Food Additive Ontology source

### 3. Generate missing .db files

When needed, generate semsql databases from OWL files:

```bash
# Using OAKLib/semsql
semsql make external/ontologies/bioportal/MPO.owl external/databases/mpo.db

# OR using Makefile (if we add targets):
make external/databases/mpo.db
make external/databases/d3o.db
# etc.
```

## Usage

### In Python Scripts (via OAKLib)

```python
from oaklib import get_adapter

# Load semsql database
adapter = get_adapter("sqlite:external/databases/omp.db")

# Query hierarchy
term_id = "OMP:0000001"
parents = list(adapter.hierarchical_parents(term_id))
siblings = list(adapter.siblings(term_id))

# Get labels and definitions
label = adapter.label(term_id)
definition = adapter.definition(term_id)
```

### In Makefile Workflows

```bash
# Coherence analysis uses semsql for fast hierarchical queries
uv run analyze-sibling-coherence \
  --input-file mappings.sssom.tsv \
  --metpo-owl src/ontology/metpo.owl
  # Internally uses metpo.db for OAKLib queries
```

## Gitignore Status

**All .db files in this directory are gitignored** via `.gitignore`:
```
external/databases/*.db
```

**Why gitignored?**
- Derived from OWL files (can be regenerated)
- Large files (64M-197M for some)
- Binary format (not diff-friendly)

**Exception**: `src/ontology/metpo.db` is tracked in git because it's needed for ODK builds.

## Maintenance

### Updating databases

When OWL files are updated:
```bash
# Re-download OWL from BioPortal
make download-external-bioportal-ontologies

# Regenerate semsql database
semsql make external/ontologies/bioportal/OMP.owl external/databases/omp.db

# Verify
sqlite3 external/databases/omp.db "SELECT COUNT(*) FROM statements;"
```

### Checking database contents

```bash
# List tables
sqlite3 external/databases/omp.db ".tables"

# Count terms
sqlite3 external/databases/omp.db "SELECT COUNT(DISTINCT subject) FROM statements WHERE predicate='rdf:type';"

# Sample terms
sqlite3 external/databases/omp.db "SELECT subject, value FROM statements WHERE predicate='rdfs:label' LIMIT 10;"
```

## Related Files

- **Source OWL files**: `external/ontologies/{bioportal,manual,ols}/`
- **Term extractions**: `data/pipeline/non-ols-terms/*.tsv` (for embeddings)
- **ChromaDB**: `data/chromadb/` (vector database for semantic search)
- **Documentation**: `external/README.md` (overall external/ directory structure)

## Questions?

**"Do we need .db for every OWL file?"**
- No - only for OAKLib hierarchical queries (coherence analysis, sibling extraction)
- For simple semantic matching, OWL → TSV → ChromaDB is sufficient

**"What's the difference between .owl and .db?"**
- .owl: Original ontology (RDF/XML format, large, slow to parse)
- .db: SQL database (fast queries, optimized for OAKLib)

**"Why are some .db files so large?"**
- MicrO (197M): Merged ontology with many terms
- mco (64M): Comprehensive conditions ontology
- Size reflects number of classes + axioms + annotations

**"Can I regenerate .db from .owl?"**
- Yes: `semsql make ontology.owl database.db`
- Requires: semsql package (`uv pip install semsql`)
