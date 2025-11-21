# BacDive Prefix Analysis

## CURIE Column Analysis Results

### Columns with High CURIE Content (>90%)

| File | Column | CURIE % | CURIE Count | Total Values |
|------|--------|---------|-------------|--------------|
| edges.tsv | predicate | 100.00% | 1,656,667 | 1,656,667 |
| edges.tsv | relation | 100.00% | 1,633,852 | 1,633,852 |
| nodes.tsv | category | 100.00% | 196,168 | 196,168 |
| edges.tsv | object | 99.99% | 1,656,558 | 1,656,667 |
| nodes.tsv | id | 99.95% | 196,068 | 196,168 |
| edges.tsv | subject | 92.49% | 1,532,282 | 1,656,667 |
| edges.tsv | primary_knowledge_source | 89.76% | 1,487,035 | 1,656,667 |

### Columns with No CURIEs (0%)

All other columns in both files (name, description, xref, synonym, etc.) contain 0% CURIEs.

---

## All Unique Prefixes Found (19 total)

### ✅ Standard/Registered Prefixes (11)

These are in standard registries (OBO, Biolink, Identifiers.org):

1. **biolink** - Biolink Model vocabulary
   - Columns: category, predicate
   - Standard IRI: `https://w3id.org/biolink/vocab/`

2. **RO** - Relation Ontology
   - Columns: relation
   - Standard IRI: `http://purl.obolibrary.org/obo/RO_`

3. **NCBITaxon** - NCBI Taxonomy
   - Columns: id, subject, object
   - Standard IRI: `http://purl.obolibrary.org/obo/NCBITaxon_`

4. **CHEBI** - Chemical Entities of Biological Interest
   - Columns: id, subject, object
   - Standard IRI: `http://purl.obolibrary.org/obo/CHEBI_`

5. **EC** - Enzyme Commission
   - Columns: id, subject, object
   - Standard IRI: `https://identifiers.org/ec-code/`

6. **KEGG** - KEGG Database
   - Columns: id, subject
   - Standard IRI: `https://identifiers.org/kegg/`

7. **CAS-RN** - Chemical Abstracts Service Registry Number
   - Columns: id, subject, object
   - Standard IRI: `https://identifiers.org/cas/` or `http://identifiers.org/cas/`

8. **BAO** - BioAssay Ontology
   - Columns: relation
   - Standard IRI: `http://www.bioassayontology.org/bao#BAO_`

9. **NCIT** - National Cancer Institute Thesaurus
   - Columns: relation
   - Standard IRI: `http://purl.obolibrary.org/obo/NCIT_`

10. **rdfs** - RDF Schema
    - Columns: relation
    - Standard IRI: `http://www.w3.org/2000/01/rdf-schema#`

11. **METPO** - Microbial Environmental Trait and Phenotype Ontology
    - Columns: id, object
    - Standard IRI: `http://purl.obolibrary.org/obo/METPO_` (if registered)
    - **Note**: Should be registered but may need verification

### ❌ Non-Standard/Local Prefixes (8)

These are kg-microbe/BacDive-specific and need IRI mappings:

1. **strain** - Organism strain identifiers
   - Columns: id, subject, object
   - **Needs mapping**: `http://w3id.org/kg-microbe/strain/` or similar

2. **medium** - Growth media identifiers
   - Columns: id, object
   - **Needs mapping**: `http://w3id.org/kg-microbe/medium/`

3. **assay** - Assay method identifiers
   - Columns: id, subject, object
   - **Needs mapping**: `http://w3id.org/kg-microbe/assay/`

4. **isolation_source** - Isolation source identifiers
   - Columns: id, subject
   - **Needs mapping**: `http://w3id.org/kg-microbe/isolation_source/`

5. **pathways** - Biological pathway identifiers
   - Columns: id, object
   - **Needs mapping**: `http://w3id.org/kg-microbe/pathways/`

6. **pathogen** - Pathogen type identifiers
   - Columns: id, object
   - **Needs mapping**: `http://w3id.org/kg-microbe/pathogen/`

7. **salinity** - Salinity measurement identifiers
   - Columns: id, object
   - **Needs mapping**: `http://w3id.org/kg-microbe/salinity/`

8. **bacdive** - BacDive-specific identifiers
   - Columns: primary_knowledge_source
   - **Needs mapping**: `https://bacdive.dsmz.de/` or `http://identifiers.org/bacdive/`

---

## Prefix Distribution by Column

### Node ID Column (`nodes.tsv:id`)
**13 unique prefixes:**
- Standard: NCBITaxon, CHEBI, EC, KEGG, METPO, CAS-RN
- Non-standard: strain, medium, assay, isolation_source, pathways, pathogen, salinity

### Edge Subject Column (`edges.tsv:subject`)
**8 unique prefixes:**
- Standard: NCBITaxon, CHEBI, EC, KEGG, CAS-RN
- Non-standard: strain, assay, isolation_source

### Edge Object Column (`edges.tsv:object`)
**11 unique prefixes:**
- Standard: NCBITaxon, CHEBI, EC, METPO, CAS-RN
- Non-standard: strain, medium, assay, pathways, pathogen, salinity

### Edge Predicate Column (`edges.tsv:predicate`)
**1 prefix:**
- biolink (100%)

### Edge Relation Column (`edges.tsv:relation`)
**4 unique prefixes:**
- All standard: RO, BAO, NCIT, rdfs

### Node Category Column (`nodes.tsv:category`)
**1 prefix:**
- biolink (100%)

### Edge Primary Knowledge Source Column (`edges.tsv:primary_knowledge_source`)
**1 prefix:**
- bacdive (89.76% of values are CURIEs)

---

## Required Actions for RDF Export

### 1. Add Standard Prefix Mappings (verification)

These should already be in Biolink Model context, but verify:

```yaml
configuration:
  curie_map:
    # Verify these are correct in Biolink context
    CAS-RN: http://identifiers.org/cas/
    METPO: http://purl.obolibrary.org/obo/METPO_
    KEGG: https://identifiers.org/kegg/
```

### 2. Add Non-Standard Prefix Mappings (REQUIRED)

```yaml
configuration:
  curie_map:
    # BacDive-specific prefixes
    strain: http://w3id.org/kg-microbe/strain/
    medium: http://w3id.org/kg-microbe/medium/
    assay: http://w3id.org/kg-microbe/assay/
    isolation_source: http://w3id.org/kg-microbe/isolation_source/
    pathways: http://w3id.org/kg-microbe/pathways/
    pathogen: http://w3id.org/kg-microbe/pathogen/
    salinity: http://w3id.org/kg-microbe/salinity/
    bacdive: https://bacdive.dsmz.de/
```

### 3. Consider Refactoring

**High-priority candidates for using standard identifiers:**

- **strain** → Map to BioSamples, NCBI Taxonomy, or culture collection IDs (DSM, ATCC)
- **medium** → Map to existing media ontologies or create proper METPO terms
- **assay** → Map to OBI (Ontology for Biomedical Investigations) terms
- **isolation_source** → Map to ENVO (Environment Ontology) terms

---

## Statistics Summary

| Category | Count | Percentage |
|----------|-------|------------|
| **Total unique prefixes** | 19 | 100% |
| Standard/registered | 11 | 57.9% |
| Non-standard/local | 8 | 42.1% |

**Impact on RDF export:**
- Without mappings: ~42% of prefix types will generate invalid URIs
- By node count: Majority of nodes use non-standard prefixes (strain, medium, etc.)

---

## Next Steps

1. ✅ Identify all prefixes (COMPLETE)
2. ⬜ Check which are in Biolink Model context
3. ⬜ Add missing standard prefixes to merge.yaml
4. ⬜ Define persistent URIs for non-standard prefixes
5. ⬜ Add all non-standard prefixes to merge.yaml
6. ⬜ Test RDF export with proper mappings
7. ⬜ Consider long-term refactoring to use standard identifiers
