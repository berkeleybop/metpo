# METPO Repository Capabilities

A guide for users with basic knowledge of microbial phenotype ontologies who want to understand what METPO can do.

---

## Overview

**METPO** (Microbial Ecophysiological Trait and Phenotype Ontology) is an ontology project that provides standardized terminology for describing microbial phenotypes. This repository is more than just an ontology—it's a comprehensive framework for:

1. Building and maintaining the ontology from Google Sheets
2. Extracting phenotype data from scientific literature using LLMs
3. Aligning METPO with external ontologies via embeddings
4. Analyzing and reconciling external phenotype databases
5. LLM-assisted definition authoring
6. Generating presentations and documentation
7. Quality control and coverage analysis
8. Ontology annotator comparison (METPO vs OMP vs PATO vs MICRO)
9. Historical version tracking from BioPortal
10. NCBI taxonomy integration
11. Cost/performance benchmarking for LLM extractions
12. Round-trip reconciliation of source data coverage
13. Names for Life (N4L) protolog data transformation *(parked)*
14. Stub generation for inter-template references
15. KG-Microbe integration analysis
16. Undergraduate engagement planning

---

## 1. Ontology Development

### Building from ROBOT Templates

METPO terms are defined in TSV templates maintained in Google Sheets. The build process automatically downloads the latest versions from Google Sheets, then compiles them into OWL using ROBOT.

**Workflow (from `src/ontology/`):**
```bash
# Clean build - removes cached templates to force fresh download from Google Sheets
./run.sh make squeaky-clean

# Build and test
./run.sh make all test

# Prepare release artifacts
./run.sh make prepare_release
```

**Key files:**
- `src/templates/metpo_sheet.tsv` - Main class definitions (auto-downloaded from Google Sheets)
- `src/templates/metpo-properties.tsv` - Property definitions (auto-downloaded)
- `src/templates/stubs.tsv` - Stub terms for rapid expansion (generated)

**Outputs:** `metpo.owl`, `metpo.obo`, `metpo.json`

---

## 2. Literature Mining with OntoGPT

Extract structured phenotype data from research paper abstracts using LLM-powered extraction.

### Templates Available

| Template | Extracts |
|----------|----------|
| `growth_conditions` | Temperature, pH, salinity ranges |
| `chemical_utilization` | Substrate usage (with METPO grounding) |
| `morphology` | Cell shape, size, motility |
| `biochemical` | Metabolic pathways |
| `taxa` | Taxonomic information |

### Running Extractions

```bash
cd literature_mining

# Fetch abstracts from a source (n4l, bacdive, ijsem)
make abstracts SOURCE=ijsem N_ABSTRACTS=100

# Run extraction with a template
make extract TEMPLATE=chemical_utilization

# Run with benchmarking (tracks cost/time)
make benchmark TEMPLATE=growth_conditions MODEL=gpt-4o
```

### What You Get

- YAML files with structured extractions
- Named entities grounded to ontology terms (METPO, CHEBI, NCBITaxon, etc.)
- Relationships between entities
- Benchmark metrics (cost per abstract, time, entity counts)

---

## 3. Source Data Analysis

### Madin et al. Dataset

A compilation of ~170,000 bacterial/archaeal trait records from 26 sources.

**Analysis tools (17 CLI scripts):**
```bash
# Field overview
uv run madin-field-summary --output-tsv reports/field_summary.tsv

# Analyze specific fields
uv run madin-analyze-pathways --output-tsv reports/pathways.tsv
uv run madin-analyze-isolation --output-tsv reports/isolation.tsv
uv run madin-carbon-substrates --output-tsv reports/substrates.tsv

# Validate taxonomy IDs against NCBI
uv run madin-verify-ncbi-taxids --sample-size 50
```

### BactoTraits Database

Integration with BactoTraits microbial phenotype database:

```bash
# Import to MongoDB
make import-bactotraits

# Generate reconciliation reports
uv run reconcile-bactotraits-coverage
uv run bactotraits-metpo-set-difference
```

---

## 4. Ontology Alignment via Embeddings

Semantic matching of METPO terms against external ontologies from OLS and BioPortal using ChromaDB vector embeddings.

### Supported Ontology Sources

- **OLS (Ontology Lookup Service)** - EBI's ontology repository
- **BioPortal** - NCBO's biomedical ontology repository

### Pipeline Steps

```bash
# 1. Fetch ontology metadata from OLS
make alignment-fetch-ontology-names

# 2. Categorize by relevance (very_appealing, appealing, moderate, low)
make alignment-categorize-ontologies

# 3. Embed METPO terms to ChromaDB
make alignment-query-metpo-terms

# 4. Generate SSSOM mappings via semantic search
# (finds similar terms across ontologies based on embedding distance)

# 5. Analyze match quality
make alignment-analyze-matches

# 6. Compute structural coherence
make alignment-analyze-coherence

# 7. Or run everything
make alignment-run-all
```

### How It Works

1. METPO terms and external ontology terms are converted to vector embeddings
2. ChromaDB stores and indexes these embeddings
3. Semantic search finds closest matches across ontologies
4. Results are output as SSSOM (Simple Standard for Sharing Ontological Mappings) files

**Output:** SSSOM mapping files identifying candidate alignments to OMP, PATO, CHEBI, ENVO, etc.

### Additional Alignment Tools

```bash
# Download specific ontologies from BioPortal
make download-external-bioportal-ontologies  # Gets MPO, OMP, D3O

# Embed external ontology terms
uv run embed-ontology-to-chromadb

# Analyze alignment candidates
uv run analyze-coherence-results
```

---

## 5. LLM-Assisted Definition Authoring

Improve ontology term definitions using LLMs guided by the Seppälä-Ruttenberg-Smith (SRS) methodology for high-quality ontology definitions.

### Definition Improvement Tools

```bash
# Propose new definitions using LLM (follows SRS guidelines)
uv run propose-definitions-with-llm

# Find terms needing better definitions
uv run analyze-definition-opportunities

# Find best existing definitions to use as templates
uv run find-best-definitions
uv run find-best-definitions-comprehensive

# Compare definitions with hierarchy context
uv run compare-definitions-with-hierarchy

# Analyze definition coverage by subtree
uv run analyze-definition-coverage-by-subtree

# Iterative definition improvement workflow
uv run iterative-definition-improvement
```

### Definition Quality Guidelines

The LLM-assisted definition tools follow ontology definition best practices:
- Definitions should be genus-differentia style where appropriate
- Definitions should distinguish the term from its siblings
- Definitions should be consistent with parent term definitions
- Avoid circular definitions

---

## 6. Presentation & Documentation Generation

### Marp-Based Slides

Generate PDF presentations from Markdown using Marp:

```bash
cd docs/presentations/icbo_2025
make slides.pdf
```

**Features:**
- Markdown-based slide authoring
- Automatic PDF generation
- Consistent styling via Marp themes
- Version-controlled presentations

---

## 7. Quality Control & Reporting

```bash
# ROBOT validation report
make metpo-report.tsv

# QC checks on Google Sheets content
uv run qc-metpo-sheets

# Definition quality analysis
uv run analyze-definition-opportunities
uv run find-best-definitions

# Coverage analysis
uv run analyze-branch-coverage-final
```

---

## 8. Ontology Annotator Comparison

Compare phenotype extraction performance across different ontology annotators to evaluate grounding quality.

### Supported Annotators

- **METPO** - Microbial Ecophysiological Trait and Phenotype Ontology
- **OMP** - Ontology of Microbial Phenotypes
- **PATO** - Phenotype and Trait Ontology
- **MICRO** - Ontology of Prokaryotic Phenotypic and Metabolic Characters

### Running Comparisons

```bash
cd literature_mining

# Run fair comparison across all annotators (10 ICBO example abstracts)
make fair-annotator-test

# Analyze results
make fair-annotator-analyze

# Detailed phenotype-only analysis
make fair-annotator-analyze-phenotypes
```

### What It Measures

- Ontology URI groundings vs AUTO (ungrounded) terms
- Unique phenotype terms extracted per ontology
- Grounding percentage across abstracts

---

## 9. Historical Version Tracking

Track METPO evolution across BioPortal submissions to monitor ID and label stability.

```bash
# List available BioPortal submissions
make list-bioportal-submissions

# Download all historical METPO versions
make download-all-bioportal-submissions

# Extract entities from each version for comparison
make extract-all-metpo-entities
```

**Outputs:** Entity extracts in `metadata/ontology/historical_submissions/entity_extracts/`

---

## 10. NCBI Taxonomy Integration

Extract and integrate NCBI taxonomy rank information:

```bash
# Download NCBI taxonomy dump
make downloads/taxdmp.zip

# Extract rank triples to Turtle format
make local/noderanks.ttl
```

**Output:** `local/noderanks.ttl` - RDF triples mapping taxon IDs to their ranks

---

## 11. Cost/Performance Benchmarking

Track LLM extraction costs and performance metrics using CBORG API:

```bash
cd literature_mining

# Run benchmarked extraction
make benchmark TEMPLATE=growth_conditions MODEL=gpt-4o INPUT_DIR=abstracts/test

# Results logged to extraction_benchmarks.tsv
```

### Metrics Tracked

- Cost per abstract and per 1K characters
- Time per abstract and per 1K input characters
- Entities and relationships extracted per 1K input
- API key usage and budget remaining

---

## 12. Round-Trip Reconciliation

Verify that METPO covers all values from source databases and vice versa:

```bash
# Generate synonym sources report
make reports/synonym-sources.tsv

# Reconcile METPO coverage of Madin dataset
make reports/madin-metpo-reconciliation.yaml

# Reconcile METPO coverage of BactoTraits
make reports/bactotraits-metpo-reconciliation.yaml

# Find BactoTraits values not in METPO
make reports/bactotraits-metpo-set-diff.yaml

# Find leaf classes without attributed synonyms
make reports/leaf_classes_without_attributed_synonyms.tsv
```

### What It Answers

- Does METPO have classes for all source field values?
- Are there METPO synonyms claiming coverage that don't match source data?
- Which METPO terms lack synonym attributions?

---

## 13. Names for Life (N4L) Integration (Parked)

> **Status: PARKED/INCOMPLETE** - This work was started but is not actively maintained. The transformation code exists but the full pipeline is not integrated into the main workflow.

Transform and harmonize Names for Life protolog phenotype data for integration with KG-Microbe.

### What N4L Provides

- ~23,500 References (RID → paper metadata)
- ~2,200 Protologs with phenotype annotations
- ~34,000 OrganismNames linked to NCBI TaxIDs

### Transformation Pipeline

Located in `docs/n4l/transformation_code/`:

```bash
# Transform N4L Excel/TSV tables to RDF N-Quads
# (Jupyter notebook: n4l_tables_to_quads.ipynb)

# Parse temperature values from free text
# (Python: regex_parse_n4l_temperatures.py)
```

### Configuration Files

- `docs/n4l/config/n4l-xlsx-parsing-config.tsv` - Sheet parsing configuration
- `docs/n4l/config/n4l_predicate_mapping_normalization.csv` - Predicate canonicalization

### Outputs

- `local/n4l-tables.nq` - RDF N-Quads for GraphDB import
- `external/ontologies/manual/n4l_merged.owl` - Merged N4L ontology for embeddings

### Documentation

- `docs/n4l/n4l-consolidated-report.md` - Full harmonization report
- `docs/n4l/README.md` - N4L integration overview

---

## 14. External Data Integrations

| Source | What METPO Does |
|--------|-----------------|
| **Google Sheets** | Term definitions and properties |
| **BactoTraits** | Microbial phenotype database for reconciliation (MongoDB) |
| **BacDive** | Strain metadata via MongoDB; abstract fetching via PMIDs |
| **Names for Life (N4L)** | Protolog phenotype tables transformed to RDF |
| **NCBI Taxonomy** | Taxonomy rank triples (`local/noderanks.ttl`) |
| **BioPortal** | Downloads MPO, D3O for comparison; embedding-based alignment |
| **OLS** | Fetches ontology metadata; embedding-based alignment |
| **EuropePMC** | Literature abstracts via IJSEM |

---

## 15. SPARQL Queries

Pre-built SPARQL queries organized by execution target. See `sparql/README.md` for full documentation.

### Queries for METPO OWL File

Executed against the local `src/ontology/metpo.owl` using ROBOT or rdflib:

| Query | Purpose |
|-------|---------|
| `find_leaf_classes_without_attributed_synonyms.sparql` | QC: Find leaf classes missing synonym attribution |
| `query_metpo_entities.sparql` | Export all entities with labels and synonyms |
| `query_metpo_labels.rq` | Look up labels for specific METPO term IDs |
| `metpo_phenotype_classes.rq` | Browse class hierarchy with parent relationships |
| `chem_interaction_props.rq` | List chemical interaction properties |
| `bacdive_oxygen_phenotype_mappings.rq` | Extract BacDive-to-METPO oxygen mappings |

### Queries for Multi-Ontology Embeddings

Designed for triplestores loaded with multiple ontologies (METPO, OMP, PATO, etc.):

| Query | Purpose |
|-------|---------|
| `extract_for_embeddings.rq` | Extract labels, synonyms, definitions across ontologies for ChromaDB |

### KG-Microbe Exploration Queries (Archived)

Located in `sparql/exploration/kg-microbe/` for analyzing KG-Microbe RDF dumps:

| Query | Purpose |
|-------|---------|
| `kg-microbe-Association-predicates.rq` | Find predicates on Association entities |
| `kg-microbe-direct-rdf-types.rq` | Find all rdf:type assertions |
| `kg-microbe-most-associated-taxa.rq` | Count organisms with most associations |
| `kg-microbe-OrganismTaxon-*.rq` | Various queries for taxa exploration |

### SPARQL Update Scripts (.ru)

Located in `docs/n4l/graphdb_workflow/sparql/` for GraphDB N4L workflow (parked):

| Script | Purpose |
|--------|---------|
| `delete_most_0_value_triples.ru` | Clean zero-value data from N4L |
| `direct_ncbitaxid_same_as.ru` | Create owl:sameAs links to NCBI Taxonomy |
| `property_hierarchy.ru` | Establish property relationships |

### Running SPARQL Queries

**Using ROBOT:**
```bash
robot query --input src/ontology/metpo.owl \
  --query sparql/find_leaf_classes_without_attributed_synonyms.sparql results.tsv
```

**Using rdflib (Python):**
```python
from rdflib import Graph
g = Graph()
g.parse("src/ontology/metpo.owl", format="xml")
results = g.query(open("sparql/query_metpo_entities.sparql").read())
```

---

## 16. Environment Management

Check and manage development environment:

```bash
# Check environment status (Python, uv, MongoDB, ROBOT, API keys)
make check-env

# Install dependencies
make install           # Core only
make install-dev       # Development tools
make install-literature # Literature mining
make install-databases  # MongoDB tools
make install-notebooks  # Jupyter + ChromaDB
make install-all       # Everything
```

---

## 17. Stub Generation

> **Note:** This is build infrastructure, not a scientific capability. It's documented here for completeness regarding the multi-template ROBOT ecosystem.

Generate ROBOT template stubs from existing templates for inter-template references:

```bash
# Create stubs file from multiple templates
uv run create-stubs --output src/templates/stubs.tsv \
    src/templates/metpo_sheet.tsv \
    src/templates/metpo-properties.tsv
```

Stubs contain only ID, LABEL, and TYPE columns, allowing templates to reference each other without circular dependencies.

---

## 18. KG-Microbe Integration Analysis

Scripts to analyze how METPO terms are used across the KG-Microbe knowledge graph datasets.

Located in `metpo/presentations/`:

| Script | Purpose |
|--------|---------|
| `analyze_kg_microbe_metpo.py` | METPO usage across all KG-Microbe datasets |
| `analyze_bactotraits.py` | BactoTraits-specific analysis |
| `analyze_madin_etal.py` | Madin et al. dataset analysis |
| `analyze_primary_sources.py` | Primary source comparison |
| `analyze_ontogpt_grounding.py` | OntoGPT grounding quality |
| `analyze_ontology_landscape.py` | Related ontology comparison |
| `calculate_minimum_import_set.py` | Compute minimal import closure |
| `generate_feedback_loop.py` | Generate feedback for improvements |

---

## 19. Undergraduate Engagement Planning

Documentation and workflows for engaging undergraduate students in METPO development.

**Key documents:**
- `docs/undergraduate_engagement_plan.md` - Full engagement plan
- `docs/undergraduate_engagement_quickstart.md` - Quick start guide

**Focus areas:**
- Creating OBO Foundry-compliant definitions
- SKOS mapping to related ontologies (OMP, PATO, MCO, ENVO)
- Role-based tasks for different skill sets
- Preparation for EBI OLS submission

**Context:** Undergraduate contributions serve as one source of draft definitions that feed into the iterative refinement workflow: propose definition → search OLS embeddings for similar terms → refine based on findings → repeat. The value is in having material to run through the pipeline, regardless of initial quality.

---

## 20. Key CLI Commands

```bash
# Ontology building (from src/ontology/)
./run.sh make squeaky-clean      # Clean and re-download from Google Sheets
./run.sh make all test           # Build and test
./run.sh make prepare_release    # Prepare release artifacts

# Literature mining
cd literature_mining && make extract TEMPLATE=chemical_utilization

# Data analysis
uv run madin-field-summary
uv run reconcile-bactotraits-coverage

# Alignment
make alignment-run-all

# Definition improvement
uv run propose-definitions-with-llm

# Annotator comparison
cd literature_mining && make fair-annotator-test

# Reconciliation
make all-reports
```

---

## Related Repositories

### Core Dependencies

| Repository | Purpose | URL |
|------------|---------|-----|
| **kg-microbe** | Knowledge graph integrating microbial data including METPO | [Knowledge-Graph-Hub/kg-microbe](https://github.com/Knowledge-Graph-Hub/kg-microbe) |
| **OntoGPT** | LLM-based ontology extraction (SPIRES method) | [monarch-initiative/ontogpt](https://github.com/monarch-initiative/ontogpt) |
| **LinkML** | Schema language for METPO templates | [linkml/linkml](https://github.com/linkml/linkml) |
| **OAK** | Ontology Access Kit for programmatic ontology operations | [INCATools/ontology-access-kit](https://github.com/INCATools/ontology-access-kit) |

### Data Sources

| Repository/Resource | What It Provides | URL |
|---------------------|------------------|-----|
| **bacteria-archaea-traits** | Madin et al. trait synthesis (~170K records) | [bacteria-archaea-traits/bacteria-archaea-traits](https://github.com/bacteria-archaea-traits/bacteria-archaea-traits) |
| **BactoTraits** | Microbial phenotype database | [bactotraits](https://github.com/microbial-phenotypes/bactotraits) |
| **BacDive** | DSMZ bacterial diversity metadatabase (99K+ strains) | [bacdive.dsmz.de](https://bacdive.dsmz.de/) |

### Related Ontologies

| Ontology | Description | URL |
|----------|-------------|-----|
| **OMP** | Ontology of Microbial Phenotypes | [obofoundry.org/ontology/omp](https://obofoundry.org/ontology/omp.html) |
| **MPO** | RIKEN Microbial Phenotype Ontology | [BioPortal](https://bioportal.bioontology.org/ontologies/MPO) |
| **D3O** | DSMZ Digital Diversity Ontology | [BioPortal](https://bioportal.bioontology.org/ontologies/D3O) |

### Infrastructure

| Repository | Purpose | URL |
|------------|---------|-----|
| **ODK** | Ontology Development Kit (Docker-based build system) | [INCATools/ontology-development-kit](https://github.com/INCATools/ontology-development-kit) |
| **ROBOT** | OWL ontology tool for templates, reasoning, validation | [ontodev/robot](https://github.com/ontodev/robot) |
| **Biolink Model** | Upper-level schema for knowledge graphs | [biolink/biolink-model](https://github.com/biolink/biolink-model) |

---

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/berkeleybop/metpo.git
cd metpo
make install-all

# 2. Build the ontology (from src/ontology/)
cd src/ontology
./run.sh make squeaky-clean
./run.sh make all test
./run.sh make prepare_release

# 3. Run some analysis
cd ../..
uv run madin-field-summary

# 4. Try literature extraction
cd literature_mining
make abstracts SOURCE=ijsem N_ABSTRACTS=10
make extract TEMPLATE=growth_conditions
```

---

## Architecture Summary

```
METPO Repository
├── Ontology Development (ODK/ROBOT)
│   └── Google Sheets → TSV templates → OWL
│
├── Literature Mining (OntoGPT)
│   ├── Abstracts → LLM extraction → Structured YAML
│   ├── Cost/performance benchmarking
│   └── Annotator comparison (METPO vs OMP vs PATO vs MICRO)
│
├── Data Integration
│   ├── Madin dataset (MongoDB) + reconciliation
│   ├── BactoTraits (MongoDB) + reconciliation
│   ├── BacDive (MongoDB)
│   ├── Names for Life (parked - Excel/TSV → RDF)
│   └── NCBI Taxonomy (rank triples)
│
├── KG-Microbe Analysis
│   └── METPO usage across BactoTraits, Madin, BacDive edges
│
├── Alignment Pipeline (ChromaDB embeddings)
│   ├── OLS ontologies → embeddings → SSSOM mappings
│   └── BioPortal ontologies → embeddings → SSSOM mappings
│
├── Definition Authoring (LLM-assisted)
│   └── SRS-guided definition improvement
│
├── Version Tracking
│   └── BioPortal historical submissions → entity extracts
│
├── Presentations (Marp)
│   └── Markdown → PDF slides
│
└── Quality Control
    ├── ROBOT validation
    ├── Round-trip reconciliation
    ├── Definition analysis
    └── Coverage reports
```

---

## Further Reading

- [CLAUDE.md](../CLAUDE.md) - Development guide
- [literature_mining/README.md](../literature_mining/README.md) - Literature mining details
- [src/ontology/README-editors.md](../src/ontology/README-editors.md) - Ontology editing guide
- [KG-Microbe documentation](http://kghub.org/kg-microbe/static/intro.html) - Knowledge graph context
