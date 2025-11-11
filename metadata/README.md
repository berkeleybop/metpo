# METPO Metadata Directory

This directory contains metadata about databases, ontologies, and project workflows that support the METPO ontology development pipeline.

## Structure

```
metadata/
├── databases/          # MongoDB metadata collections for external databases
│   ├── bactotraits/    # BactoTraits database field mappings and file metadata
│   └── madin/          # Madin trait database file metadata
├── ontology/           # Ontology submission and historical analysis metadata
│   ├── historical_submissions/  # Entity extracts from historical METPO versions
│   └── ols-submission.csv      # OLS submission tracking
├── project/            # Project-level metadata (reserved for future use)
└── README.md           # This file
```

## Directory Contents

### databases/

MongoDB metadata collections that support data integration workflows.

- **bactotraits/**: Field mappings between BactoTraits database and METPO terms, plus file metadata
- **madin/**: File metadata for Madin trait database

**Import collections:**
```bash
make import-bactotraits-metadata
make import-madin-metadata
```

See [databases/README.md](databases/README.md) for detailed documentation.

### ontology/

Metadata about METPO ontology submissions and historical versions.

- **historical_submissions/**: Entity extraction analysis from historical BioPortal submissions
- **ols-submission.csv**: Tracking for Ontology Lookup Service submissions

**Extract entities from historical versions:**
```bash
make extract-all-metpo-entities
```

See [ontology/README.md](ontology/README.md) for detailed documentation.

### project/

Reserved for project-level metadata such as:
- Contributor information
- Publication tracking
- Funding acknowledgments
- Project milestones

Currently empty, will be populated as needed.

## Design Philosophy

### Commit Data, Not Just Code

Simple metadata collections are stored as JSON and version-controlled:
- **Transparency**: Changes are tracked in git history
- **Reproducibility**: No hidden database state
- **Portability**: Works with standard tools (mongoimport, csvkit)
- **Documentation**: JSON serves as self-documenting schema

### Generated + Committed

Complex collections (like field_mappings) are:
1. **Generated** by automated tools from source files
2. **Committed** to git for documentation and backup
3. **Regenerable** via Makefile targets

This provides both automation and transparency.

## Usage Patterns

### Import MongoDB Collections

Import all database metadata:
```bash
make import-bactotraits-metadata  # Imports field_mappings and files
make import-madin-metadata        # Imports files
```

### Ontology Analysis

Extract entities from historical METPO versions:
```bash
make extract-all-metpo-entities   # Extract from all historical OWL files
make clean-entity-extracts        # Remove generated extraction files
```

### Cleanup

Remove generated files:
```bash
make clean-entity-extracts        # Remove ontology/historical_submissions/entity_extracts/*
```

## Maintenance

- **databases/**: JSON files are either hand-maintained (files.json) or generated (field_mappings.json)
- **ontology/ols-submission.csv**: Updated manually when submitting to OLS
- **ontology/historical_submissions/entity_extracts/**: Generated files, excluded from git history but documented
- **project/**: Reserved for future use

## Related Documentation

- [databases/README.md](databases/README.md) - MongoDB collection details
- [ontology/README.md](ontology/README.md) - Ontology submission tracking
- [ontology/historical_submissions/README.md](ontology/historical_submissions/README.md) - Historical analysis workflows
