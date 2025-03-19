# METPO Ontology Development Guide

## Build Commands
- Update Google Sheet template: `make -C src/ontology ../templates/metpo_sheet.tsv`
- Regenerate specific component: `make -C src/ontology recreate-metpo_sheet`
- Regenerate all components: `make -C src/ontology recreate-components`
- Run all tests: `make -C src/ontology test`
- Run tests without imports: `make -C src/ontology test_fast`
- Run reasoning test only: `make -C src/ontology reason_test`
- Run SPARQL validation: `make -C src/ontology sparql_test`
- Prepare release: `make -C src/ontology prepare_release`
- Validate ID ranges: `make -C src/ontology validate_idranges`
- Clean: `make -C src/ontology clean`
- Clean including templates: `make -C src/ontology squeaky-clean`

## Style Guidelines
- IDs: 6-digit numeric IDs prefixed with METPO: (e.g., METPO:000001)
- URIs: Use https://w3id.org/metpo/ as base URI
- Term labels: Sentence case, concise and descriptive
- Definitions: Complete sentences with periods, following "A X is a Y that Z" pattern
- Parent terms: Use pipe character (|) for multiple parents in templates
- Synonyms: Include relevant synonyms using SPLIT=| for multiple values
- Template structure: Maintain column headers in Google Sheet as per current format
- Validation: Terms should validate against OWL2 DL profile
- Imports: Reference external ontologies with proper annotations

## Documentation
Work in src/ontology/ directory and use run.sh (Unix) or run.bat (Windows) scripts