# METPO Development Guide

## Build Commands
- Build all: `cd src/ontology && sh run.sh make prepare_release`
- Fast build (no imports): `cd src/ontology && sh run.sh make IMP=false prepare_release`
- Test ontology: `cd src/ontology && sh run.sh make test`
- Single test: `cd src/ontology && sh run.sh make reason_test` or `sparql_test`
- Clean: `cd src/ontology && sh run.sh make clean`
- Deep clean: `cd src/ontology && sh run.sh make squeaky-clean`
- Refresh imports: `cd src/ontology && sh run.sh make refresh-imports`
- Update repo: `cd src/ontology && sh run.sh make update_repo`

## Python Environment
- Setup with Poetry: `poetry install`
- Run Jupyter: `poetry run jupyter notebook`
- Python requires 3.11+

## Ontology Structure
- Edit file: `src/ontology/metpo-edit.owl`
- Templates: `src/templates/metpo_sheet.tsv`
- Reports: `src/ontology/reports/`

## Coding Guidelines
- Follow OBO Foundry ID formats and conventions
- Include labels for all entities
- Use standard OWL Manchester syntax
- Document term definitions with IAO:0000115
- Follow existing term naming patterns
- Jupyter notebooks should use rdflib for RDF processing
- Python: PEP 8 style recommended
- When editing, maintain existing formatting patterns

## Typical Workflow
1. `cd src/ontology/`
2. `sh run.sh make squeaky-clean`
3. `sh run.sh make update_repo`
4. `sh run.sh make refresh-imports`
5. `sh run.sh make prepare_release`