# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

METPO (Microbial Ecophysiological Trait and Phenotype Ontology) is a dual-purpose repository:
1. **Ontology Development** (`src/ontology/`) - OWL ontology for microbial traits and phenotypes
2. **Literature Mining Pipeline** (`literature_mining/`) - OntoGPT-based knowledge extraction from scientific papers

These two components are **independent** and managed separately.

## Ontology Development (src/ontology/)

### Building the Ontology

The ontology is built using the Ontology Development Kit (ODK) with Docker. All commands must be run from `src/ontology/`:

```bash
cd src/ontology

# Full build (requires Docker)
./run.sh make all

# Clean and rebuild everything
make squeaky-clean
./run.sh make all

# Fast build (skip imports/components refresh)
./run.sh make IMP=false PAT=false COMP=false all
```

### Source Data

- **Primary source**: Google Sheets (fetched automatically during build)
  - URL: https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU
- **Templates**: `src/templates/*.tsv` (ROBOT templates)
  - `metpo_sheet.tsv` - main term definitions
  - `metpo-synonyms.tsv` - synonym mappings
  - `metpo-properties.tsv` - object/data properties

### Build Process

1. Fetches latest CSV from Google Sheets
2. Generates OWL components using ROBOT templates (`src/ontology/components/*.owl`)
3. Merges with `src/ontology/metpo-edit.owl`
4. Runs reasoning (ELK reasoner)
5. Produces release artifacts (`metpo-base.owl`, `metpo-full.owl`, `metpo.owl`)

### Creating a Release

```bash
cd src/ontology

# Prepare release files (copies to project root)
./run.sh make prepare_release

# After reviewing generated files:
git add metpo.owl metpo-base.owl metpo-full.owl metpo.obo metpo.json
git commit -m "YYYY-MM-DD release"
git push

# Create GitHub release
gh release create vYYYY-MM-DD --title "YYYY-MM-DD Release" --draft metpo.owl metpo-base.owl metpo-full.owl --generate-notes
```

**Important**: Monitor third-party systems (OBO Foundry, Bioportal) after releases.

### Testing and Validation

```bash
cd src/ontology

# Run all tests
./run.sh make test

# Fast test (skip import/component refresh)
./run.sh make test_fast

# Specific validations
./run.sh make reason_test          # ELK reasoning test
./run.sh make sparql_test          # SPARQL validation queries
./run.sh make robot_reports        # Generate QC reports
```

### ODK Configuration

- **Config file**: `src/ontology/metpo-odk.yaml`
- **Update repository setup**: `./run.sh make update_repo`
- **ODK version**: v1.5.4

### Ontology Architecture

- **Base IRI**: `https://w3id.org/metpo`
- **ID Prefix**: `METPO:`
- **Edit file**: `src/ontology/metpo-edit.owl` (manual edits, use Protégé)
- **Components**: Auto-generated from templates (don't edit directly)
- **No imports**: Currently all imports commented out in ODK config
- **Release artifacts**:
  - `metpo.owl` - main release (full)
  - `metpo-base.owl` - without imports
  - `metpo-full.owl` - with reasoning

## Literature Mining Pipeline (literature_mining/)

### Setup

```bash
cd literature_mining

# Install dependencies
uv sync --extra dev

# Create directory structure
make setup
```

### Quick Start

```bash
cd literature_mining

# Run quick test (10 abstracts)
make quick-test TEMPLATE=growth_conditions

# Full extraction with specific parameters
make extract SOURCE=ijsem TEMPLATE=growth_conditions N_ABSTRACTS=50

# Assessment
make assess
```

### Pipeline Workflow

1. **Get PMIDs**: `make pmids SOURCE={n4l|bacdive|ijsem}`
2. **Fetch abstracts**: `make abstracts` (uses artl-cli)
3. **Build intermediates**: `make intermediates` (METPO database + SPARQL-derived enums)
4. **Update templates**: `make templates TEMPLATE=<name>`
5. **Extract**: `make extract TEMPLATE=<name>` (runs OntoGPT)
6. **Assess**: `make assess` (quality analysis)

### Templates

Five specialized templates (in `literature_mining/templates/`):
- **taxa_template** - PMID + taxonomic information
- **growth_conditions_template** - Media, temperature, pH, oxygen, salt
- **chemical_utilization_template** - Substrate usage (METPO predicates injected via SPARQL)
- **morphology_template** - Cell shape, Gram stain, motility
- **biochemical_template** - Enzyme activities, fatty acid profiles

**Template Design Principle**: Small, focused templates outperform comprehensive ones.

### Key Parameters

```bash
SOURCE=ijsem          # PMID source: n4l, bacdive, ijsem
TEMPLATE=growth_conditions  # Template name
N_PMIDS=10            # Number of PMIDs to sample
N_ABSTRACTS=5         # Number of abstracts to fetch
```

### OntoGPT Configuration

```bash
# Environment variables
export ANTHROPIC_API_KEY="..."
export OPENAI_API_KEY="..."

# Model selection (in Makefile)
-m claude-3-5-sonnet-latest  # Use Claude
# (default is OpenAI GPT-4)
```

### Directory Structure

```
literature_mining/
├── inputs/           # PMID sources
├── intermediates/    # METPO DB, generated YAML/TSV
├── templates/        # Template definitions (*_base.yaml, *_populated.yaml)
├── abstracts/        # Fetched abstracts (preserved)
├── outputs/          # Extraction results (timestamped)
├── assessments/      # Quality reports
├── cache/           # LLM response cache
└── logs/            # Processing logs
```

### Assessment Tools

```bash
# Template quality (no extractions needed)
make assess-templates

# Extraction quality analysis
make assess-extractions

# Both
make assess
```

### Important: Chemical Utilization Template

The `chemical_utilization_template` is special - it **dynamically injects METPO predicates** via SPARQL:

```bash
# This builds intermediates/yaml/chem_interaction_props_enum.yaml from METPO
make intermediates

# This injects the predicates into the template
make templates TEMPLATE=chemical_utilization
```

Other templates are static copies from `*_base.yaml` to `*_populated.yaml`.

### Cleanup

```bash
make clean              # Clean intermediates and templates
make clean-workspace    # Also clean inputs/logs (preserve outputs/abstracts)
make clean-all          # Everything except abstracts/
```

## Python Package Structure

### Installation

```bash
# Development installation
uv sync --extra dev
```

### Package Scripts

- `extract-rank-triples` - Extract taxon rank triples from ontology
- `convert-chem-props` - Convert chemical properties TSV to YAML enum

### Dependencies

Core dependencies:
- `click>=8.0` - CLI framework
- `pyyaml>=6.0.2` - YAML processing

Dev dependencies:
- `ontogpt==1.0.16` - Knowledge extraction
- `pandas>=2.3.1` - Data processing
- `rdflib>=7.1.4` - RDF handling
- `semsql>=0.4.0` - SQL over ontologies
- `artl-mcp>=0.33.0` - Abstract fetching
- `litellm==1.75.8` - LLM interface
- `openai>=1.95,<1.100` - OpenAI API

## Key Design Principles

### Ontology

- **Pure class hierarchies**: Primary goal
- **Reuse OBO Foundry terms**: Secondary priority
- **Minimal imports**: Currently disabled
- **Data-driven**: Google Sheets → ROBOT templates → OWL
- **Automated builds**: Docker + ODK + GitHub Actions

### Literature Mining

- **Template specialization**: Focused > comprehensive
- **Ontology grounding**: Critical for integration
- **METPO predicates**: Dynamically updated from ontology
- **Preservation**: Never delete abstracts/ or outputs/ directories
- **Timestamped outputs**: All extractions are dated
- **Assessment-driven**: Quality metrics guide development

## Common Tasks

### Update ontology after Google Sheets changes

```bash
cd src/ontology
./run.sh make squeaky-clean
./run.sh make all
```

### Run literature extraction with new METPO version

```bash
cd literature_mining
make clean-intermediates  # Force rebuild of METPO database
make intermediates        # Rebuild with new metpo.owl
make templates TEMPLATE=chemical_utilization  # Refresh predicates
make extract TEMPLATE=chemical_utilization
```

### Debug failed extractions

```bash
cd literature_mining
make debug-extract TEMPLATE=<name>  # Max verbosity + debug cache
# Check logs/debug_<template>_<timestamp>.log
```

### Add new template

1. Create `templates/<name>_template_base.yaml` (LinkML schema)
2. Add validation rule to `validate-templates` target in Makefile
3. Add build rule to `templates` section (static copy or SPARQL injection)
4. Test: `make validate && make templates TEMPLATE=<name>`

## Important Notes

- **Separate pipelines**: Ontology build and literature mining are independent
- **Docker required**: For ontology builds (ODK)
- **Never edit components**: `src/ontology/components/*.owl` are auto-generated
- **Preserve abstracts**: Expensive to re-fetch from PubMed
- **METPO database**: Rebuilt from `metpo.owl` via semsql
- **Release workflow**: prepare_release → git commit → GitHub release → monitor integrations

## Git Workflow

Current branch: `main`

Typical workflow:
1. Make changes (ontology edits or template updates)
2. Run builds/tests locally
3. Commit and push
4. CI runs QC checks (GitHub Actions)
5. For releases: create GitHub release with artifacts

## Documentation Locations

- **Ontology editing**: `src/ontology/README-editors.md`
- **Literature mining**: `literature_mining/README.md`
- **Development notes**: `literature_mining/DEVELOPMENT_NOTES.md`
- **Template requirements**: `literature_mining/FUNDAMENTAL_REQUIREMENTS.md`
- **OBO Academy**: https://oboacademy.github.io/obook/
