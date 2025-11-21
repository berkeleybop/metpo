# BacDive Relation/Predicate Combinations

Analysis of all unique combinations of `relation` and `predicate` fields in `../kg-microbe/data/transformed/bacdive/edges.tsv`.

**Total edges:** 1,656,667
**Unique combinations:** 14

## Combinations Table

| Relation | Predicate | Count |
|----------|-----------|-------|
| NCIT:C153110 | biolink:assesses | 522,416 |
| RO:0000057 | biolink:consumes | 393,461 |
| RO:0002215 | biolink:capable_of | 186,014 |
| rdfs:subClassOf | biolink:subclass_of | 172,761 |
| RO:0001015 | biolink:location_of | 169,130 |
| RO:0002200 | biolink:has_phenotype | 123,867 |
| BAO:0002924 | biolink:occurs_in | 52,995 |
| RO:0002215 | biolink:produces | 12,523 |
| (empty) | biolink:associated_with_sensitivity_to | 12,518 |
| (empty) | biolink:associated_with_resistance_to | 10,297 |
| RO:0000056 | biolink:occurs_in | 343 |
| RO:0002200 | biolink:capable_of | 183 |
| NCIT:C153110 | biolink:is_assessed_by | 112 |
| RO:0000056 | biolink:consumes | 47 |

## Key Observations

### 1. Empty Relations (22,815 edges, 1.4%)
- `biolink:associated_with_sensitivity_to` - 12,518 edges
- `biolink:associated_with_resistance_to` - 10,297 edges

These predicates don't have corresponding RO/OBO relations defined.

### 2. Multiple Relations per Predicate

Some Biolink predicates map to multiple RO relations:

**biolink:occurs_in** (53,338 edges total):
- `BAO:0002924` - 52,995 edges (99.4%)
- `RO:0000056` (participates in) - 343 edges (0.6%)

**biolink:capable_of** (186,197 edges total):
- `RO:0002215` (capable of) - 186,014 edges (99.9%)
- `RO:0002200` (has phenotype) - 183 edges (0.1%) ⚠️ Likely incorrect mapping

**biolink:consumes** (393,508 edges total):
- `RO:0000057` (has participant) - 393,461 edges (99.99%)
- `RO:0000056` (participates in) - 47 edges (0.01%)

### 3. Multiple Predicates per Relation

Some RO relations map to multiple Biolink predicates:

**RO:0002215** (capable of):
- `biolink:capable_of` - 186,014 edges
- `biolink:produces` - 12,523 edges

**NCIT:C153110** (assessment relation):
- `biolink:assesses` - 522,416 edges
- `biolink:is_assessed_by` - 112 edges

**RO:0000056** (participates in):
- `biolink:occurs_in` - 343 edges
- `biolink:consumes` - 47 edges

**RO:0002200** (has phenotype):
- `biolink:has_phenotype` - 123,867 edges
- `biolink:capable_of` - 183 edges ⚠️ Likely incorrect mapping

## Relation Definitions

| Relation | Label | Definition |
|----------|-------|------------|
| NCIT:C153110 | Assessment | An evaluation or appraisal of a condition |
| RO:0000057 | has participant | A relation between a process and a continuant |
| RO:0002215 | capable of | A relation between a material entity and a process |
| rdfs:subClassOf | subclass of | Standard RDF subclass relation |
| RO:0001015 | location of | Inverse of 'located in' |
| RO:0002200 | has phenotype | A relation between an organism and a phenotype |
| BAO:0002924 | occurs in | BioAssay Ontology relation for process location |
| RO:0000056 | participates in | A relation between a continuant and a process |

## Data Quality Issues

1. **Inconsistent mapping**: `biolink:capable_of` → `RO:0002200` (183 edges) appears incorrect
   - Should probably be `RO:0002215` like the other 186,014 edges

2. **Missing relations**: 22,815 edges (1.4%) have empty relation field
   - Need RO/OBO mappings for sensitivity/resistance associations

3. **Multiple relation options**: Three predicates have split mappings
   - May indicate data source variations or transformation inconsistencies
