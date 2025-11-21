# SPARQL Queries

This directory contains SPARQL queries for querying METPO and related knowledge graphs.

## Organization

All SPARQL queries use the `.rq` extension for consistency.

### Main Directory (`sparql/`)

Core METPO queries:

- **`definition_sources.rq`** - Extract definition source IRIs from METPO
- **`query_metpo_labels.rq`** - Extract METPO term labels  
- **`query_metpo_entities.rq`** - Extract METPO entities
- **`metpo_phenotype_classes.rq`** - Extract METPO phenotype classes
- **`extract_for_embeddings.rq`** - Extract data for embedding generation
- **`find_leaf_classes_without_attributed_synonyms.rq`** - QC query for missing synonyms
- **`bacdive_oxygen_phenotype_mappings.rq`** - BacDive oxygen phenotype mappings
- **`chem_interaction_props.rq`** - Chemical interaction properties

### N4L Queries (`sparql/n4l/`)

Queries for N4L (Numbers for Life) graphdb workflow:

- **`flatten_n4l_parsing_components.rq`** - Flatten N4L parsing components
- **`metpo_classes_temperature_limits.rq`** - METPO temperature limit classes
- **`temperature_query.rq`** - Temperature data queries

### Exploration Queries (`sparql/exploration/`)

Exploratory queries for knowledge graph analysis:

#### KG-Microbe (`sparql/exploration/kg-microbe/`)

- **`kg-microbe-Association-predicates.rq`** - Association predicates
- **`kg-microbe-direct-rdf-types.rq`** - Direct RDF types
- **`kg-microbe-most-associated-taxa.rq`** - Most associated taxa
- **`kg-microbe-OrganismTaxon-Association-predicates.rq`** - Organism taxon associations
- **`kg-microbe-OrganismTaxon-direct-predicates.rq`** - Direct predicates
- **`kg-microbe-OrganismTaxon-iri-styles.rq`** - IRI style analysis
- **`kg-microbe-types-bioloink-relations.rq`** - Biolink relation types

#### N4L Exploration (`sparql/exploration/n4l/`)

- **`n4l-organisms-with-most-statements.rq`** - Organisms with most statements

## Usage

### With ROBOT

Most queries are designed to be used with [ROBOT](http://robot.obolibrary.org/):

```bash
cd src/ontology
sh run.sh robot query \
    --input metpo.owl \
    --query ../../sparql/definition_sources.rq \
    ../../data/definitions/definition_sources.tsv
```

### With Makefile Targets

The Definition Work Pipeline provides make targets:

```bash
make data/definitions/definition_sources.tsv     # Extract definition sources
make definitions-workflow                         # Run full pipeline
```

See `make help-definitions` for complete list.

### With GraphDB or Triplestore

Exploration queries in `sparql/exploration/` can be executed directly in GraphDB or other SPARQL endpoints.

## Adding New Queries

1. Save query with `.rq` extension in appropriate directory
2. Add Makefile target if query is part of a workflow
3. Document query purpose in this README
4. Use descriptive filename (e.g., `extract_phenotype_mappings.rq`)

## SPARQL in src/

Note: `src/sparql/` contains ODK ontology development queries managed by the Ontology Development Kit. Those queries should not be moved to this directory.
