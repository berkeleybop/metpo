# Extraction Results and Metrics

Consolidated production results and quality metrics from OntoGPT extractions.

## Production Extraction Results

### Chemical Utilization (Full Corpus)

**Run**: `cmm_fullcorpus_gpt4o_t00_20251031_193935.yaml`

| Metric | Value |
|--------|-------|
| Total relationships | 1,214 |
| Avg per paper | 50.6 |
| Papers with relationships | 12/24 (50%) |
| Ground truth accuracy | 5/5 (100%) |
| CHEBI grounding | 75 (48.1%) |
| NCBITaxon grounding | 19 (12.2%) |
| AUTO (ungrounded) | 62 (39.7%) |
| Overall grounding | 60.3% |

### Morphology (Full Corpus)

**Run**: `morphology_fullcorpus_gpt4o_t00_20251031.yaml`

Using base template (appropriate for sparse data):
- 24 papers processed
- Conservative extraction appropriate for CMM corpus

### Growth Conditions

**Run**: `growth_conditions_hybrid_gpt4o_t00_20251031_213345.yaml`

- 3-paper test: 453 extractions
- Full corpus run completed

## Template Specialization Scores

Assessment of how well templates focus on their intended domains:

| Template | Overall | Specificity | Exclusivity |
|----------|---------|-------------|-------------|
| Chemical Utilization | 99.0/100 | 100.0% | 98.0% |
| Growth Conditions | 97.0/100 | 100.0% | 93.9% |
| Biochemical | 96.6/100 | 100.0% | 93.1% |
| Morphology | 89.3/100 | 87.5% | 91.1% |
| Taxa | 83.9/100 | 75.0% | 92.8% |

**Cross-template overlap** (acceptable, primarily universal entities):
- Biochemical <-> Morphology: 13.1%
- Taxa <-> Growth Conditions: 9.6%
- Morphology <-> Chemical Utilization: 1.9%

## IJSEM Literature Knowledge Distribution

Analysis of 100 IJSEM abstracts showing information frequency:

**High frequency (80-100% of abstracts)**:
- Taxonomic classification & new species descriptions
- Isolation source & environmental context
- Basic cell morphology (shape, Gram staining, motility)
- Growth conditions (temperature, pH, salinity, oxygen)
- Phylogenetic relationships (16S rRNA analysis)

**Medium frequency (45-75%)**:
- Metabolic capabilities & substrate utilization
- Biochemical characteristics (enzyme activities, API tests)
- Fatty acid profiles & chemotaxonomy
- Ecological roles & environmental adaptations

**Lower frequency (~25%)**:
- Secondary metabolite production
- Specialized enzyme activities

**Implication**: Template optimization should match data density. Chemical utilization benefits from "Extract ALL"; morphology needs conservative approach for CMM corpus.

## Quality Metrics Definitions

### Coverage metrics

```
Abstract Footprint = (chars in original_spans) / (chars in Text.content)
Raw Completeness = (populated raw_completion_outputs) / (total template fields)
Entity Density = (semicolon-separated entities) / (populated raw fields)
```

### Conversion metrics

```
Named Entity Conversion = (named entities extracted) / (entities in raw outputs)
CompoundExpression Conversion = (CEs in extracted_objects) / (relationship strings)
```

### Grounding metrics

```
Ontology Grounding Rate = (non-AUTO entities) / (total named entities)
Template Specialization = (domain-specific ontology hits) / (total grounded)
```

## Quality Targets

**Minimum acceptable**:
- Coverage: >70%
- Raw completeness: >80%
- Entity conversion: >90%
- CE conversion: >80%
- Ontology grounding: >60%
- Template specialization: >80%

**Excellent**:
- Coverage: >85%
- Raw completeness: >95%
- Entity conversion: >95%
- CE conversion: >90%
- Ontology grounding: >80%
- Template specialization: >90%

## Output File Locations

### Production outputs

```
outputs/
├── cmm_fullcorpus_gpt4o_t00_20251031_193935.yaml     # Chemical (1,214 rels)
├── morphology_fullcorpus_gpt4o_t00_20251031.yaml     # Morphology (24 papers)
├── growth_conditions_hybrid_*.yaml                    # Growth conditions
└── annotator_comparison/                              # Fair comparison results
    ├── metpo/
    ├── omp/
    ├── pato/
    └── micro/
```

### Archived outputs

```
outputs/archive/
├── superseded/     # Chemical template iterations
└── experiments/    # Morphology template iterations
```

See: [../ARCHIVE_SUMMARY.md](../ARCHIVE_SUMMARY.md) for archive structure.

## Assessment Tools

```bash
# Template analysis
uv run metpo-assessor analyze-templates templates/

# Extraction analysis
uv run metpo-assessor analyze-extractions outputs/

# Via Makefile
make assess-templates
make assess-extractions
```

See also:
- [GROUNDING_ANALYSIS.md](GROUNDING_ANALYSIS.md) for grounding details
- [TEMPLATE_OPTIMIZATION.md](TEMPLATE_OPTIMIZATION.md) for template design

---

*Consolidated from: DEVELOPMENT_NOTES.md, SESSION_NOTES.md, FUNDAMENTAL_REQUIREMENTS.md*
