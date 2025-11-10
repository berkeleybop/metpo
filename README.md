
![Build Status](https://github.com/berkeleybop/metpo/actions/workflows/qc.yml/badge.svg)
# METPO

Microbial ecophysiological trait and phenotype ontology

More information can be found at http://obofoundry.org/ontology/metpo

## Versions

### Stable release versions

The latest version of the ontology can always be found at:

http://purl.obolibrary.org/obo/metpo.owl

(note this will not show up until the request has been approved by obofoundry.org)

### Editors' version

Editors of this ontology should use the edit version, [src/ontology/metpo-edit.owl](src/ontology/metpo-edit.owl)

## Contact

Please use this GitHub repository's [Issue tracker](https://github.com/berkeleybop/metpo/issues) to request new terms/classes or report errors or specific concerns related to the ontology.

## Installation

### Requirements

- **Python**: 3.11 or higher
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (recommended)
- **ROBOT**: For ontology processing (see [ROBOT installation](http://robot.obolibrary.org/))
- **MongoDB**: For database workflows (optional)

### Environment Setup

```bash
# Check your environment
make check-env

# Install core dependencies only
make install

# Install for specific workflows
make install-dev           # Development tools (oaklib, rdflib, semsql)
make install-literature    # Literature mining (ontogpt, artl-mcp)
make install-databases     # BactoTraits/Madin workflows (pandas, pymongo)
make install-notebooks     # Jupyter notebooks (chromadb, matplotlib)

# Install everything
make install-all
```

## Acknowledgements

This ontology repository was created using the [Ontology Development Kit (ODK)](https://github.com/INCATools/ontology-development-kit).

----

## Input:
- https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/edit?gid=0#gid=0

## Notes
- https://github.com/berkeleybop/group-meetings/issues/155#issuecomment-2715444097

----

METPO is intended to drive mining knowledge out of papers from journals like IJSEM
and expressing the findings with classes and predicates from METPO or the Biolink model,
which would then become part of KG-Microbe.

We strive to keep our class hierarchies pure. Reuse of terms from OBO Foundry ontologies
and the use of logical axioms are high but secondary priorities.

## Repository Structure and Workflows

This repository supports multiple research workflows beyond ontology development:

### 1. Ontology Development (`src/ontology/`)

The core METPO ontology is built using the Ontology Development Kit (ODK). The root Python code and Makefiles are **not involved** in ontology releases.

**Building the ontology** (requires Docker):
```bash
cd src/ontology
make squeaky-clean          # Clean all generated files
./run.sh make all          # Full build with Docker wrapper
```

The build process fetches the latest CSV data from Google Sheets, generates ROBOT template output, and builds all ontology format files (OWL, OBO, JSON).

**Creating a release:**
```bash
cd src/ontology
./run.sh prepare_release   # Copies files to project root
```

See `src/ontology/README-editors.md` for detailed instructions.

### 2. Literature Mining Pipeline (`literature_mining/`)

Extract structured microbial trait data from research papers using OntoGPT with METPO grounding.

**Quick start:**
```bash
make install-literature

# Fetch abstracts and run extraction
make -C literature_mining pmids SOURCE=ijsem
make -C literature_mining abstracts SOURCE=ijsem N_ABSTRACTS=10
make -C literature_mining extract TEMPLATE=growth_conditions
```

**Key features:**
- OntoGPT-based extraction with custom templates
- METPO-grounded entity recognition
- Cost/performance benchmarking
- Multiple extraction templates (growth conditions, chemical utilization, morphology, etc.)

See `literature_mining/README.md` for full documentation.

### 3. ICBO Example Extractions (`literature_mining/`)

Example extractions demonstrating METPO's grounding strengths and weaknesses, used in ICBO 2025 presentation.

```bash
make install-literature

# Extract phenotypes and chemical utilizations from example abstracts
make -C literature_mining icbo-phenotypes
make -C literature_mining icbo-chemicals

# Analyze METPO grounding quality
make -C literature_mining icbo-analyze
```

Example inputs, templates, and outputs are in `literature_mining/abstracts/icbo_examples/` and `literature_mining/outputs/icbo_examples/`.

**Presentation materials**: See `docs/presentations/icbo_2025/` for slides and analysis from ICBO 2025.

### 4. Database Reconciliation (`metpo/scripts/`)

Import and reconcile microbial trait databases (BactoTraits, Madin et al.) with METPO terminology.

```bash
make install-databases

# Import datasets to MongoDB
make import-bactotraits
make import-madin

# Generate reconciliation reports
make all-reports
```

**Outputs:**
- `reports/bactotraits-metpo-reconciliation.yaml`
- `reports/madin-metpo-reconciliation.yaml`
- `reports/synonym-sources.tsv`

### 5. Historical ID Tracking (`metadata/historical_usage_analysis/`)

Track METPO entity stability and IRI evolution across BioPortal submissions.

```bash
# Download historical submissions
make download-all-bioportal-submissions

# Extract entities from each version
make extract-all-metpo-entities
```

Analyzes IRI numbering scheme changes, entity additions/removals, and ID reuse violations. See `metadata/historical_usage_analysis/README.md` for comprehensive findings.

### 6. Ontology Alignment Pipeline (`notebooks/`)

Semantic matching between METPO and other microbial ontologies using ChromaDB embeddings.

```bash
make install-notebooks

# Run alignment pipeline
make alignment-run-all

# Or run individual steps
make alignment-fetch-ontology-names
make alignment-categorize-ontologies
make alignment-analyze-matches
```

Identifies high-quality alignment candidates from OLS4 and non-OLS ontologies.

### 7. External Ontology Integration (`external/`)

Centralized storage for all external ontology files and derived databases.

```bash
make install-dev

# Download microbial ontologies from BioPortal
make download-external-bioportal-ontologies

# Extract terms for embeddings
make notebooks/non-ols-terms/MPO.tsv
make notebooks/non-ols-terms/D3O.tsv
```

**Structure:**
- `external/ontologies/bioportal/` - Downloaded from BioPortal (13+ ontologies: MPO, OMP, D3O, GMO, MISO, etc.)
- `external/ontologies/manual/` - Manually added files (e.g., n4l_merged.owl)
- `external/databases/` - Derived semsql databases
- `external/metpo_historical/` - Historical METPO BioPortal submissions

## Key Documentation

- **Ontology editing**: `src/ontology/README-editors.md`
- **Literature mining**: `literature_mining/README.md`
- **Historical analysis**: `metadata/historical_usage_analysis/README.md`
- **Development guide**: `CLAUDE.md`
- **Analysis reports**: `reports/`

## Common Tasks

```bash
# Check environment setup
make check-env

# Generate all analysis reports
make all-reports

# Test complete workflow reproducibility
make test-workflow

# Clean generated data
make clean-data
```

## License

METPO is released under the [Creative Commons Attribution 4.0 International License (CC-BY-4.0)](https://creativecommons.org/licenses/by/4.0/).

You are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made

See [LICENSE](https://creativecommons.org/licenses/by/4.0/legalcode) for full details. 
