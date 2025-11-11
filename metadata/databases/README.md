# Database Metadata

This directory contains JSON metadata files that are imported into MongoDB to support the METPO project's data integration workflows.

## Purpose

These metadata files define:
- Field mappings between external databases and METPO ontology terms
- File locations and structure information for data import pipelines
- Configuration for data transformation and validation

## Collections

### BactoTraits (`bactotraits/`)

**bactotraits_field_mappings.json**
- Maps BactoTraits database fields to METPO class IRIs
- Used during BactoTraits import to automatically annotate trait data with ontology terms
- Import: `make import-bactotraits-metadata`

**bactotraits_files.json**
- Metadata about BactoTraits data files (locations, formats, schemas)
- Import: `make import-bactotraits-metadata`

### Madin (`madin/`)

**madin_files.json**
- Metadata about Madin trait database files
- Import: `make import-madin-metadata`

## Usage

Import all metadata collections:
```bash
make import-bactotraits-metadata
make import-madin-metadata
```

Or import individually:
```bash
mongoimport --db metpo --collection bactotraits_field_mappings --file metadata/databases/bactotraits/bactotraits_field_mappings.json --jsonArray
mongoimport --db metpo --collection bactotraits_files --file metadata/databases/bactotraits/bactotraits_files.json --jsonArray
mongoimport --db metpo --collection madin_files --file metadata/databases/madin/madin_files.json --jsonArray
```

## Maintenance

These files are generated and maintained through the METPO project workflows. When updating:
1. Regenerate JSON files using appropriate scripts
2. Test import with `mongoimport --drop` to replace collection
3. Verify data integrity with queries against the imported collections
