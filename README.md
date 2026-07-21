
![Build Status](https://github.com/berkeleybop/metpo/actions/workflows/qc.yml/badge.svg)
# METPO

Microbial ecophysiological trait and phenotype ontology

## Versions

### Stable release versions

METPO releases are available from multiple sources:

**BioPortal** (Recommended for browsing and search):
- https://bioportal.bioontology.org/ontologies/METPO
- Browse classes, search terms, and visualize the hierarchy
- API access available

**GitHub Releases**:
- See [Releases](https://github.com/berkeleybop/metpo/releases)
- Download OWL, OBO, and JSON formats

**Direct OWL file**:
- Latest release: `metpo.owl` in this repository

### Editors' version

Editors of this ontology should use the edit version, [src/ontology/metpo-edit.owl](src/ontology/metpo-edit.owl)

## Identifiers and resolution

The canonical IRI for every METPO term is under the `https://w3id.org/metpo/` namespace, with a bare 7-digit local identifier:

- Term IRI: `https://w3id.org/metpo/<id>` (e.g. `https://w3id.org/metpo/1000482`)
- The ontology prefix `METPO:` expands to `https://w3id.org/metpo/`
- Ontology document IRI: `https://w3id.org/metpo/metpo.owl` (it sits under the `https://w3id.org/metpo/` delegation, as do the version IRIs and release products, e.g. `https://w3id.org/metpo/releases/<date>/metpo.owl`; the bare `https://w3id.org/metpo.owl` is outside the delegation and does not resolve)

**Do not use `http://purl.obolibrary.org/obo/METPO_<id>`.** METPO is not registered in the OBO Foundry, so those PURLs do not resolve (HTTP 404) and are not METPO identifiers. The canonical METPO identifier namespace is `https://w3id.org/metpo/` (resolved through the `w3id.org` host); `purl.obolibrary.org` is not used by METPO. (Term-IRI resolution behavior is still being finalized; see issues #450 and #435.)

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
make install-databases     # BactoTraits/Madin workflows (pandas, pymongo)
make install-analysis      # Analysis/visualization scripts (matplotlib, numpy, levenshtein)

# Install everything
make install-all
```

## Acknowledgements

This ontology repository was created using the [Ontology Development Kit (ODK)](https://github.com/INCATools/ontology-development-kit).

**METPO research relies on numerous external data sources and ontologies. See [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md) for complete citations and attributions for:**
- BactoTraits, Madin et al., and BacDive microbial trait databases
- 24+ ontologies from OBO Foundry and BioPortal
- Semsql databases, embedding infrastructure, and software tools

----

## Input:
- https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/edit?gid=0#gid=0

## Development Notes
- Historical development discussion: [berkeleybop/group-meetings #155](https://github.com/berkeleybop/group-meetings/issues/155) *(Note: May require repository access)*

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

### 2. Literature mining and ICBO extractions (retired)

The OntoGPT-based literature-mining pipeline (formerly `literature_mining/`) and the `metpo.literature_mining` package, including the ICBO 2025 extraction examples, were retired from this repo during scope-narrowing and archived at [turbomam/metpo-attic](https://github.com/turbomam/metpo-attic).

**Presentation materials**: See `docs/presentations/icbo_2025/` for slides and analysis from ICBO 2025. The Python scripts that generated the figures for that talk (formerly in `metpo/presentations/`) were also retired and are archived at [turbomam/metpo-attic](https://github.com/turbomam/metpo-attic).

### 3. Database Reconciliation (`metpo/scripts/`)

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

### 4. ID Allocation and Deprecation

METPO has gone through three numbering eras. All IDs ever used — across current templates,
historical BioPortal submissions, and tagged releases — are tracked to prevent reuse.

```bash
# Regenerate the id allocation audit report
make audit-ids                   # writes reports/id-allocation-audit.md

# Regenerate the deprecated IDs template (TSV) used to build the OWL component
make -C src/ontology -f metpo.Makefile regenerate-deprecated
# or just let the normal build pick it up:
make -C src/ontology -f metpo.Makefile components/metpo_sheet.owl
```

`src/templates/deprecated.tsv` is a ROBOT template that marks every burned ID as
`owl:deprecated true` with an `"obsolete ..."` label. It is committed to the repo and
merged into `metpo.owl` during every release build. **Never reuse a burned ID** — consult
`reports/id-allocation-audit.md` for the full list and the next safe IDs to allocate.

### 5. Ontology Alignment Pipeline

Semantic matching between METPO and other microbial ontologies using ChromaDB embeddings.

For a lighter-weight, label-based alternative (OLS4 + BioPortal search, no embeddings), see `assess-ontology-by-api-search` in `docs/cli-reference.md`.

```bash
make install-analysis

# Run alignment pipeline
make alignment-run-all

# Or run individual steps
make alignment-fetch-ontology-names
make alignment-categorize-ontologies
make alignment-analyze-matches
```

Identifies high-quality alignment candidates from OLS4 and non-OLS ontologies.

### 6. External Ontology Integration

External ontology files are treated as build artifacts, not committed. The `external/` directory is git-ignored; download what you need on demand:

```bash
make install-dev

# Download microbial ontologies from BioPortal into external/ontologies/bioportal/
make download-external-bioportal-ontologies
```

Historical METPO BioPortal submissions were downloaded once and processed into `metadata/ontology/historical_submissions/entity_extracts/` (committed), which is what the ID-allocation audit reads. For semantic matching against external ontologies, see the embedding strategy in `docs/embedding-strategy.md`.

## Key Documentation

- **Ontology editing**: `src/ontology/README-editors.md`
- **CLI reference**: `docs/cli-reference.md` - Complete guide to all command-line tools
- **Deprecation workflow**: `docs/deprecation-workflow.md` — how to deprecate terms and allocate new IDs
- **ID allocation and deprecation**: `reports/id-allocation-audit.md` — auto-generated list of all active and burned IDs, next safe IDs to allocate
- **Historical analysis**: `metadata/ontology/historical_submissions/README.md`
- **Database metadata**: `metadata/databases/README.md`
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
