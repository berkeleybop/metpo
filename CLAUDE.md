# METPO Development Guide

## Build Commands
- Build all: `cd src/ontology && sh run.sh make prepare_release`
- Fast build (no imports): `cd src/ontology && sh run.sh make IMP=false prepare_release`
- Test ontology: `cd src/ontology && sh run.sh make test`
- Fast test: `cd src/ontology && sh run.sh make test_fast`
- Clean: `cd src/ontology && sh run.sh make clean`
- Refresh imports: `cd src/ontology && sh run.sh make refresh-imports`
- Validate: `cd src/ontology && sh run.sh make reason_test sparql_test`

## Ontology Structure
- Edit file: `src/ontology/metpo-edit.owl`
- Templates: `src/templates/metpo_sheet.tsv`
- Imports: `src/ontology/imports/` (bfo, obi, omp, pato, so, micro, mpo)

## Assets Directory
- Contains ontology files (.owl): 
  - MicrO (Microbiology Ontology) - compressed .owl.gz format
  - MPO (Microbial Phenotype Ontology) - with English-only version
  - OMP (Ontology of Microbial Phenotypes)
  - METPO (as OBO format)
- Database files (.db): SQLite databases of ontologies for querying
- Mapping files (.tsv, .SSSOM.tsv): Term mappings between ontologies
- Visualization resources (.png): Ontology relationship visualizations
- Python code: Jupyter notebook for BioPortal API mapping extraction
- Utility scripts: Text files with repair commands for ontology issues

## Coding Guidelines
- Follow OBO Foundry ID formats and conventions
- Include labels for all entities
- Use standard OWL Manchester syntax
- Place imports in appropriate files in imports directory
- Document term definitions with IAO:0000115
- Follow existing term naming patterns in the ontology

----

## Typical local build
* cd src/ontology/
* sh run.sh make squeaky-clean
* sh run.sh make update_repo
* sh run.sh make update_repo
* sh run.sh make refresh-imports
* sh run.sh make prepare_release