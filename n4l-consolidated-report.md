# N4L/KG-Microbe Data Harmonization - Consolidated Report
*Generated 2025-06-05*

---

## Executive Summary

This report consolidates the work completed on harmonizing Names for Life (N4L) protolog data with the KG-Microbe knowledge graph. The project focused on cleaning and wiring N4L data for smooth interoperability, including asserting RDF types, validating IRI patterns, and creating "aboutness" links between entities.

### Key Achievements
- **Type Assertions Added**: 59,770 total (23,533 References, 2,247 Protologs, 33,990 OrganismNames)
- **Aboutness Links Created**: 4,279 total (2,067 Reference→Protolog, 2,212 Protolog→OrganismNames)
- **IRI Pattern Validation**: Identified 22 malformed Protolog IRIs requiring curation
- **Predicate Analysis**: Found 32 unsafe predicate IRIs needing canonicalization

---

## 1. Project Context & Goals

### Background
Two Ontotext GraphDB repositories are maintained:
- **KG-Microbe**: A relatively tidy graph of microbial knowledge
- **Names for Life (N4L)**: Direct ingest of spreadsheets capturing Reference IDs (RID), Name IDs (NM), and richly annotated protolog phenotype tables

### Core Question
> Which bacterium appears in the most triples in both repositories and has a recent, un-emended IJSEM protolog?

### Prerequisites Addressed
1. Assert `rdf:type` triples for core entities
2. Validate the shapes of key IRIs  
3. Create lightweight "aboutness" edges
4. Produce reproducible SPARQL snippets & counts

---

## 2. Data Sources & Named Graphs

### Primary Data Sources

| Graph/File | Description | Subjects |
|------------|-------------|----------|
| `N4L_REF.ID_to_DOCID` | Map RID → paper metadata | ~23,534 |
| `protolog_normalization_*.xlsx/*` (7 sheets) | Protolog phenotype tables | 2,247 |
| `N4L_NM.ID_to_EX.ID` / `N4L_NM.ID_to_NCBI_TaxID` | Map NM/EX → taxon IDs | 33,990 |
| `reference_id_mapping.csv` | 23,534 rows × 6 columns (refid, year, pubmedid, etc.) | 23,534 |

### Graph Inventory with Subject Counts

| Graph | Count |
|-------|-------|
| `http://example.com/n4l/N4L_ID_to_NCBI_mappings.xlsx/N4L_REF.ID_to_DOCID` | 64,272 |
| `http://example.com/n4l/reference_id_mapping.csv` | 64,272 |
| `http://example.com/n4l/protolog_normalization_categories_with_1000_KMP.xlsx/All%28Sheet1%2C2%2C3%29` | 101 |
| `http://example.com/n4l/protolog_normalization_categories_with_1000_DB.xlsx/Sheet2` | 83 |
| `http://example.com/n4l/protolog_normalization_categories_with_1000_KMP.xlsx/EffectRIDProtos%28rid.2300_up%29` | 81 |
| `http://example.com/n4l/protolog_normalization_categories_with_1000_KMP.xlsx/Sheet2` | 20 |
| `http://example.com/n4l/protolog_normalization_categories_with_1000_DB.xlsx/Sheet3` | 20 |
| `http://example.com/n4l_temperatures_parsed` | 3 |

---

## 3. Type Assertions Implementation

### 3.1 Reference Types
- **Pattern**: `rid.<digits>`
- **SPARQL**: 
  ```sparql
  INSERT { GRAPH n4l:type_assertions { ?s a n4l:Reference } }
  WHERE {
    GRAPH <.../N4L_REF.ID_to_DOCID> { ?s ?p ?o }
    FILTER regex(str(?s),"rid\\.[0-9]+$")
  }
  ```
- **Result**: 23,533 triples added (rid.nvp absent due to empty row)

### 3.2 Protolog Types
- **Initial Issue**: Naïve query attempted to type all subjects (~2.5M)
- **Corrected Query**:
  ```sparql
  VALUES ?g { ...seven protolog sheet IRIs... }
  GRAPH ?g { SELECT DISTINCT ?s WHERE { ?s ?p ?o } }
  ```
- **Result**: 2,247 clean `n4l:Protolog` triples

### 3.3 OrganismNames Types
- **Pattern**: `nm.<digits>` or `ex.<digits>`
- **Result**: 33,990 `n4l:OrganismNames` triples

### Type Assertion Summary

| Class | Count |
|-------|-------|
| `n4l:Reference` | 23,533 |
| `n4l:Protolog` | 2,247 |
| `n4l:OrganismNames` | 33,990 |
| **Total** | **59,770** |

---

## 4. IRI Pattern Validation

### 4.1 Reference IRIs
- **Expected**: `http://example.com/n4l/rid.<digits>`
- **Validation Query**:
  ```sparql
  SELECT ?badRef WHERE {
    GRAPH n4l:type_assertions { 
      ?badRef a n4l:Reference .
      FILTER(!regex(str(?badRef),"^.*/rid\\.[0-9]+$"))
    }
  }
  ```
- **Result**: 0 mismatches - all clean

### 4.2 Protolog IRI Categories

| Category | Pattern | Count |
|----------|---------|-------|
| rid+nm | `rid.<d>_nm.<d>` | 2,033 |
| nm-only | `nm.<d>` | 177 |
| rid-only | `rid.<d>` | 15 |
| **other** | (malformed) | 22 |
| **Total** | | **2,247** |

#### Examples of Malformed Protolog IRIs
```
http://example.com/n4l/rid.3047-rid.3058          # RID range
http://example.com/n4l/rid.908_10.1601%2Fnm.570   # RID + encoded DOI + NM
http://example.com/n4l/rid.2345_only_emendations  # comment suffix
```

### 4.3 OrganismNames IRIs
- **Expected**: `nm.<digits>` or `ex.<digits>`
- **Result**: All 33,990 match `nm.<digits>` pattern; no `ex.*` found

---

## 5. Aboutness Links Implementation

### 5.1 Reference → Protolog Links
- **Method**: RID extraction using REPLACE function
- **Query Pattern**:
  ```sparql
  INSERT { GRAPH n4l:protolog_aboutness { ?ref n4l:is_about ?prot } }
  WHERE { ...RID extraction logic... }
  ```
- **Result**: 2,069 links

### 5.2 Protolog → OrganismNames Links
- **Two-pass approach**:
  - Pass 1 (nm-only): 177 triples
  - Pass 2 (rid+nm): 2,035 triples
- **Total**: 2,212 links

### Aboutness Summary (Non-reflexive)

| Subject Type | Object Type | Count |
|--------------|-------------|-------|
| Protolog | OrganismNames | 2,212 |
| Reference | Protolog | 2,067 |
| **Total** | | **4,279** |

### Complete Aboutness Matrix

| Subject Type | Object Type | Count |
|--------------|-------------|-------|
| (empty) | Protolog | 1 |
| OrganismNames | OrganismNames | 177 |
| OrganismNames | Protolog | 177 |
| Protolog | OrganismNames | 2,212 |
| Protolog | Protolog | 291 |
| Protolog | Reference | 14 |
| Reference | Protolog | 2,067 |
| Reference | Reference | 14 |

---

## 6. Predicate Analysis

### Top 20 Predicates by Usage

| Predicate | Count |
|-----------|-------|
| `name_id` | 5,921 |
| `name` | 5,839 |
| `ex_id_(or_tx_id)` | 5,454 |
| `culture_collection_numbers` | 4,516 |
| `rid` | 4,297 |
| `cellular_morphology_(shape)` | 4,179 |
| `type_strain_designation` | 4,092 |
| `isolation_source` | 3,778 |
| `motility` | 3,638 |
| `gram_positive_negative` | 3,535 |
| `cellular_morphology_(dimension_1)` | 3,461 |
| `oxygen,_h2_and_co2_requirements` | 3,242 |
| `positive_enzyme_activities` | 2,870 |
| `mol_g+c_content_(no_method)` | 2,817 |
| `cellular_morphology_(dimension_2)` | 2,809 |
| `temperature_optimum` | 2,696 |
| `colony_color` | 2,654 |
| `spore_forming?` | 2,583 |
| `negative_enzyme_activities` | 2,554 |
| `fatty_acids` | 2,486 |

*Note: 32 predicates contain unsafe characters (spaces, commas, parentheses)*

---

## 7. Quality Issues Identified

### 7.1 Malformed Protolog IRIs (22 total)
- RID ranges (e.g., `rid.3047-rid.3058`)
- Comment suffixes (e.g., `rid.2345_only_emendations`)
- DOI fragments (e.g., `rid.908_10.1601%2Fnm.570`)

### 7.2 Unsafe Predicate IRIs (32 total)
- Contain spaces, commas, parentheses
- Proposed canonicalization: `[^A-Za-z0-9_] → "_"`, lowercase, collapse `__*`

### 7.3 Mixed-role IRIs
- nm-only & rid-only rows create reflexive aboutness links
- Need dedicated `/protolog/` namespace

### 7.4 Missing Property Hierarchy
- Positive/negative trait predicates lack `rdfs:subPropertyOf` relationships

---

## 8. Recommended Next Steps

| Priority | Action | Impact |
|----------|--------|--------|
| ★★★ | Canonicalize 32 predicates via DELETE/INSERT | Prevents broken SHACL & SPARQL |
| ★★☆ | Curate 22 malformed IRIs or add `n4l:needsCuration` | Removes noise & future errors |
| ★★☆ | Create property hierarchy for traits | Enables roll-up queries |
| ★☆☆ | Mint dedicated `/protolog/` IRIs | Eliminates reflexive links |
| ★★★ | Write cross-repo SPARQL for original question | Answers business need |

---

## 9. Key SPARQL Queries

### 9.1 Type Assertion Verification
```sparql
PREFIX n4l: <http://example.com/n4l/>
SELECT ?o (COUNT(?s) AS ?count)
WHERE {
  GRAPH n4l:type_assertions { ?s ?p ?o }
}
GROUP BY ?o
```

### 9.2 Protolog Pattern Classification
```sparql
BIND(IF(regex(str(?s),"/rid\\.[0-9]+_nm\\.[0-9]+$"),"rid+nm",
     IF(regex(str(?s),"/rid\\.[0-9]+$"),"rid-only",
     IF(regex(str(?s),"/nm\\.[0-9]+$"),"nm-only","other"))) AS ?category)
```

### 9.3 Non-reflexive Aboutness Summary
```sparql
SELECT ?st ?ot (COUNT(DISTINCT CONCAT(STR(?s),STR(?o))) AS ?pairs)
WHERE {
  GRAPH n4l:protolog_aboutness { ?s n4l:is_about ?o FILTER(?s != ?o) }
  GRAPH n4l:type_assertions { ?s a ?st . ?o a ?ot }
}
GROUP BY ?st ?ot
```

---

## 10. Glossary

| Term | Definition |
|------|------------|
| **RID** | Reference (paper) identifier |
| **NM** | Taxon name identifier |
| **EX** | Exemplar identifier |
| **Protolog** | Curated phenotype record per taxon |
| **IJSEM** | International Journal of Systematic and Evolutionary Microbiology |
| **N4L** | Names for Life database |
| **KG-Microbe** | Knowledge Graph for Microbes |

---

## 11. Technical Notes

### IRI Patterns Summary
- **References**: `http://example.com/n4l/rid.<digits>`
- **Protologs**: `http://example.com/n4l/rid.<d>_nm.<d>` (or variants)
- **OrganismNames**: `http://example.com/n4l/nm.<digits>`

### Graph Names Used
- `n4l:type_assertions` - Store all rdf:type triples
- `n4l:protolog_aboutness` - Store all aboutness links
- Various source graphs from Excel/CSV imports

---

*End of Consolidated Report*