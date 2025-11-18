# METPO Attribution Columns and Predicates Reference

## ROBOT Template Columns in metpo_sheet.tsv

### Row 1: Human-readable column names
### Row 2: ROBOT template directives with predicates

---

## Core Metadata Columns

| Column # | Human Name | ROBOT Directive | Predicate CURIE | Full IRI | Purpose |
|----------|------------|-----------------|-----------------|----------|---------|
| 1 | ID | ID | - | - | Term identifier (e.g., METPO:1000059) |
| 2 | label | LABEL | rdfs:label | http://www.w3.org/2000/01/rdf-schema#label | Human-readable term name |
| 3 | TYPE | TYPE | - | - | owl:Class, owl:ObjectProperty, etc. |
| 4 | parent classes | SC % SPLIT=\| | rdfs:subClassOf | http://www.w3.org/2000/01/rdf-schema#subClassOf | Parent class(es), pipe-separated |

---

## Definition and Attribution Columns

| Column # | Human Name | ROBOT Directive | Predicate CURIE | Full IRI | Purpose | In OWL |
|----------|------------|-----------------|-----------------|----------|---------|--------|
| 5 | description | A IAO:0000115 | IAO:0000115 | http://purl.obolibrary.org/obo/IAO_0000115 | **Textual definition** | ✅ As annotation |
| 6 | definition source | >A IAO:0000119 | IAO:0000119 | http://purl.obolibrary.org/obo/IAO_0000119 | **Definition source URI** | ✅ As axiom annotation on definition |
| 7 | comment | A rdfs:comment | rdfs:comment | http://www.w3.org/2000/01/rdf-schema#comment | **Curator notes, rationale** | ✅ As annotation |

**Note:** The `>A` directive means "annotation on annotation" - so IAO:0000119 becomes an axiom annotation on the IAO:0000115 assertion.

---

## Additional Attribution Predicates Used in `/tmp/metpo_attributed_definitions.tsv`

These were prepared but only some made it into the final template (via the comment field):

| Predicate CURIE | Full IRI | Purpose | Usage |
|-----------------|----------|---------|-------|
| IAO:0000117 | http://purl.obolibrary.org/obo/IAO_0000117 | **Term editor** - person who added/edited the term | "METPO Editorial Team", curator names |
| IAO:0000232 | http://purl.obolibrary.org/obo/IAO_0000232 | **Curator note** - internal notes for ontology editors | Rationale, adaptation notes |
| dcterms:contributor | http://purl.org/dc/terms/contributor | **Contributor** - additional contributors | Undergraduate curator names |
| dc:creator | http://purl.org/dc/elements/1.1/creator | **Creator** - original author | Undergraduate curator who wrote original definition |
| rdfs:seeAlso | http://www.w3.org/2000/01/rdf-schema#seeAlso | **See also** - related resources | Additional reference URLs |
| oboInOwl:created_by | http://www.geneontology.org/formats/oboInOwl#created_by | **Created by** - creator identifier | Short form (AG, JDK, LW, METPO) |
| oboInOwl:hasDbXref | http://www.geneontology.org/formats/oboInOwl#hasDbXref | **Database cross-reference** | Foreign ontology CURIEs |

---

## Synonym Columns (existing in template)

| Column # | Human Name | ROBOT Directive | Predicate CURIE | Full IRI | Purpose |
|----------|------------|-----------------|-----------------|----------|---------|
| 8 | biolink equivalent | AI skos:closeMatch | skos:closeMatch | http://www.w3.org/2004/02/skos/core#closeMatch | Biolink model mapping |
| 9 | confirmed exact synonym | A oboInOwl:hasExactSynonym SPLIT=\| | oboInOwl:hasExactSynonym | http://www.geneontology.org/formats/oboInOwl#hasExactSynonym | Exact synonyms |
| 10 | literature mining synonyms | A oboInOwl:hasRelatedSynonym SPLIT=\| | oboInOwl:hasRelatedSynonym | http://www.geneontology.org/formats/oboInOwl#hasRelatedSynonym | Synonyms from OntoGPT |
| 11 | madin synonym or field | A oboInOwl:hasRelatedSynonym SPLIT=\| | oboInOwl:hasRelatedSynonym | http://www.geneontology.org/formats/oboInOwl#hasRelatedSynonym | MADIN database synonyms |
| 12 | synonym source | >AI IAO:0000119 | IAO:0000119 | http://purl.obolibrary.org/obo/IAO_0000119 | Source for MADIN synonyms |
| 13 | bacdive keyword synonym | A oboInOwl:hasRelatedSynonym SPLIT=\| | oboInOwl:hasRelatedSynonym | http://www.geneontology.org/formats/oboInOwl#hasRelatedSynonym | BacDive keywords |
| 14 | synonym source | >AI IAO:0000119 | IAO:0000119 | http://purl.obolibrary.org/obo/IAO_0000119 | Source for BacDive synonyms |
| 15 | bactotraits synonym | A oboInOwl:hasRelatedSynonym SPLIT=\| | oboInOwl:hasRelatedSynonym | http://www.geneontology.org/formats/oboInOwl#hasRelatedSynonym | BactoTraits synonyms |
| 16 | synonym source | >AI IAO:0000119 | IAO:0000119 | http://purl.obolibrary.org/obo/IAO_0000119 | Source for BactoTraits synonyms |

---

## Other Annotation Columns

| Column # | Human Name | ROBOT Directive | Predicate CURIE | Full IRI | Purpose |
|----------|------------|-----------------|-----------------|----------|---------|
| 17 | measurement_unit_ucum | A qudt:ucumCode | qudt:ucumCode | http://qudt.org/schema/qudt/ucumCode | UCUM unit code |
| 18 | range_min | A METPO:range_min | METPO:2000072 | http://purl.obolibrary.org/obo/METPO_2000072 | Minimum value |
| 19 | range_max | A METPO:range_max | METPO:2000071 | http://purl.obolibrary.org/obo/METPO_2000071 | Maximum value |
| 20 | equivalent_class_formula | EC % | - | - | OWL equivalent class expression |

---

## Attribution Patterns Used

### 1. Foreign Ontology Definition Source
```
Column 5 (description): "A quality that inheres in a bearer by virtue of..."
Column 6 (definition source): http://purl.obolibrary.org/obo/PATO_0000001
Column 7 (comment): "Based on PATO:quality (SSSOM similarity: 0.999999)"
```

### 2. Undergraduate Curator Attribution
```
Column 5 (description): "A biological process comprising the chemical reactions..."
Column 6 (definition source): (empty or METPO:curation)
Column 7 (comment): "Undergraduate curator: Anthea Guo"
```

### 3. Public Domain Source Attribution
```
Column 5 (description): "A halophily preference in which an organism requires..."
Column 6 (definition source): https://en.wikipedia.org
Column 7 (comment): "Based on Wikipedia, MicrobeWiki"
```

### 4. METPO Curation
```
Column 5 (description): "A phenotype characterized by specific pH values..."
Column 6 (definition source): METPO:curation
Column 7 (comment): "METPO editorial curation"
```

---

## ROBOT Template Directive Legend

| Directive | Meaning |
|-----------|---------|
| `A` | Annotation - creates an OWL annotation on the term |
| `>A` | Annotation on annotation - creates an axiom annotation (metadata about an annotation) |
| `AI` | Annotation with IRI value |
| `SC` | SubClass of |
| `EC` | Equivalent Class |
| `%` | Split on % character (allows multiple values) |
| `SPLIT=\|` | Split on pipe character (allows multiple values) |

---

## Current Coverage in `/tmp/metpo_sheet_updated.tsv`

- **256 terms total**
- **256 with IAO:0000115** (textual definition) - 100%
- **118 with IAO:0000119** (definition source) - 46%
- **145 with rdfs:comment** (curator notes) - 57%

### Terms still needing IAO:0000119 (definition source):
138 terms have definitions but no URI source - these are primarily:
- Undergraduate curator definitions without foreign ontology mappings
- METPO-specific terms without external equivalents
- Terms that need attribution to "METPO:curation" or similar

---

## Recommended Next Steps

To achieve full attribution for all 256 terms:

1. **Add METPO:curation as default source** for internally curated definitions
2. **Add ISBN references** for textbook-based definitions (e.g., ISBN:978-0321897398 for Brock Biology)
3. **Add ORCID or structured curator references** for undergraduate contributions
4. **Consider adding IAO:0000117 (term editor) column** to template for explicit editor attribution
