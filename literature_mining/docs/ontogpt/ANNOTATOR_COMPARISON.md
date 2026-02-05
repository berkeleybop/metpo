# Annotator Comparison Experiment

This experiment compares different phenotype ontology annotators for OntoGPT extraction quality.

## Purpose

Demonstrate how different ontologies perform when grounding microbial phenotype terms:
- **METPO** - Metagenomic Phenotype Ontology (our custom ontology)
- **OMP** - Ontology of Microbial Phenotypes (OBO Foundry community ontology)
- **PATO** - Phenotypic Quality Ontology (general phenotype ontology)

## Test Setup

### Test Abstracts
We use the 2 ICBO example abstracts with the best METPO grounding:
- **19622650** - *Methylovirgula ligni* (12 METPO terms)
- **19622668** - *Bavariicoccus seileri* (12 METPO terms)

These are novel species descriptions rich in phenotype mentions (Gram staining, cell shape, motility, oxygen requirements, pH preferences, etc.).

### Databases

Pre-downloaded from https://s3.amazonaws.com/bbop-sqlite/:
```
literature_mining/intermediates/db/annotator_test/
├── metpo.db (1.5 MB)   - METPO custom ontology
├── omp.db   (11 MB)    - Ontology of Microbial Phenotypes
└── pato.db  (141 MB)   - Phenotypic Quality Ontology
```

### Templates

Three variant templates, identical except for the Phenotype class annotator:

- `strain_phenotype_metpo.yaml` - uses `sqlite:intermediates/db/annotator_test/metpo.db`
- `strain_phenotype_omp.yaml` - uses `sqlite:intermediates/db/annotator_test/omp.db`
- `strain_phenotype_pato.yaml` - uses `sqlite:intermediates/db/annotator_test/pato.db`

## Running the Comparison

```bash
cd literature_mining

# Run all three annotators on test abstracts
make annotator-test

# Analyze and compare results
make annotator-analyze

# Clean up
make annotator-clean
```

## Expected Output Structure

```
outputs/annotator_comparison/
├── metpo/
│   ├── 19622650-metpo.yaml
│   ├── 19622650-metpo.log
│   ├── 19622668-metpo.yaml
│   └── 19622668-metpo.log
├── omp/
│   ├── 19622650-omp.yaml
│   ├── 19622650-omp.log
│   ├── 19622668-omp.yaml
│   └── 19622668-omp.log
└── pato/
    ├── 19622650-pato.yaml
    ├── 19622650-pato.log
    ├── 19622668-pato.yaml
    └── 19622668-pato.log
```

## Analysis Metrics

The `annotator-analyze` target counts:
- **Ontology URI groundings**: Terms matched to `http://purl.obolibrary.org/obo/` URIs
- **AUTO terms**: Terms OntoGPT couldn't ground to the ontology
- **Total groundings**: Sum of ontology URIs + AUTO terms

Example output:
```
=== Annotator Comparison Analysis ===

metpo Results:
  19622650       :  14 groundings ( 12 ontology URIs,   2 AUTO terms)
  19622668       :  16 groundings ( 12 ontology URIs,   4 AUTO terms)

omp Results:
  19622650       :  18 groundings ( 15 ontology URIs,   3 AUTO terms)
  19622668       :  20 groundings ( 18 ontology URIs,   2 AUTO terms)

pato Results:
  19622650       :  10 groundings (  5 ontology URIs,   5 AUTO terms)
  19622668       :  12 groundings (  6 ontology URIs,   6 AUTO terms)
```

## Interpretation

### Higher ontology URI count = better grounding
- The ontology has terms that match the phenotype language in the literature
- Less reliance on AUTO (ungrounded) terms

### Expected patterns:
- **OMP**: Should have highest microbial phenotype coverage (it's purpose-built for this)
- **METPO**: Should perform well on our target domain (metabolic/environmental phenotypes)
- **PATO**: General phenotype ontology, may miss microbial-specific terms

## Adding More Annotators

To test additional ontologies:

1. Download the database:
```bash
cd literature_mining/intermediates/db/annotator_test
curl -L -o ontology_name.db.gz https://s3.amazonaws.com/bbop-sqlite/ontology_name.db.gz
gunzip ontology_name.db.gz
```

2. Create a template variant:
```bash
sed 's|sqlite:intermediates/db/annotator_test/metpo.db|sqlite:intermediates/db/annotator_test/ontology_name.db|g' \
  literature_mining/templates/strain_phenotype_icbo.yaml > \
  literature_mining/templates/strain_phenotype_ontology_name.yaml
```

3. Add to `Makefile`:
- Add ontology name to `ANNOTATORS` variable
- Create `annotator-test-ontology_name` target
- Update `annotator-test` dependencies

## Notes

- All extractions use the same LLM (gpt-4o by default, temperature 0.0)
- The only difference is the ontology database used for grounding
- This isolates the effect of ontology coverage on grounding quality
