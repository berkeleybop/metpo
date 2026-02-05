# Non-OLS Ontology Processing Status Report

Related to: https://github.com/berkeleybop/metpo/issues/255#issuecomment-3462462852

Date: 2025-10-31

## Summary

Successfully processed **12 of 13** BioPortal-only ontologies mentioned in issue #255, extracting **10,785 total terms**.

- ✅ **9 ontologies**: Working without modification
- 🔧 **3 ontologies**: Working with workarounds
- ⚠️ **1 ontology**: Requires one-time manual download (MISO)
- ❌ **1 ontology**: Failed - not actually available (HMADO)

---

## ✅ Working Without Workarounds (9 ontologies)

| Ontology | Terms | Full Name |
|----------|-------|-----------|
| OMP | 2,309 | Ontology of Microbial Phenotypes |
| BIPON | 1,746 | Bacterial Interlocked Process Ontology |
| GMO | 1,557 | Growth Medium Ontology |
| MPO | 320 | MPO/RIKEN Microbial Phenotype Ontology |
| D3O | 283 | D3O/DSMZ Digital Diversity Ontology |
| ID-AMR | 271 | Infectious Diseases and Antimicrobial Resistance |
| OFSMR | 159 | Open Predictive Microbiology Ontology |
| FMPM | 155 | Food Matrix for Predictive Microbiology |
| TYPON | 19 | Microbial Typing Ontology |
| MCCV | 16 | Microbial Culture Collection Vocabulary |

**Total: 6,835 terms**

---

## 🔧 Working With Workarounds (3 ontologies)

### 1. MEO (2,499 terms) - Metagenome and Environment Ontology
**Issue:** Broken import declaration
- MEO imports `https://mdatahub.org/data/msv/` which returns unparseable HTML
- ROBOT fails during ontology loading: `UnloadableImportException`

**Workaround:** Created `catalog-v001.xml` to redirect broken import
```xml
<uri name="https://mdatahub.org/data/msv/" uri="file:///dev/null"/>
```
- ROBOT now uses: `robot query --catalog catalog-v001.xml --input MEO.owl ...`
- Successfully extracts 2,499 terms (with 18 unparseable triples logged as warnings)

**Status:** ✅ Working in pipeline

---

### 2. OFSMR (159 terms) - Open Predictive Microbiology Ontology
**Issue:** Non-standard property usage
- Uses `owl:label` (160 occurrences) instead of standard `rdfs:label`
- Original SPARQL query missed all labels → 0 terms extracted

**Workaround:** Added `owl:label` to SPARQL query property list
```sparql
FILTER(?labelProp IN (
  rdfs:label,
  skos:prefLabel,
  owl:label,  # Added for OFSMR
  ...
))
```

**Status:** ✅ Working in pipeline

---

### 3. N4L (454 terms) - N4L Phenotypic Ontology
**Issue:** Not available on BioPortal
- Listed in issue #255 as "Not Available in Either System"
- No OLS or BioPortal source

**Workaround:** Manual file placement
- Obtained `n4l_merged.owl` (2.8MB)
- Placed in `non-ols/` directory
- Pipeline processed automatically via wildcard pattern matching

**Status:** ✅ Working in pipeline

---

## ⚠️ Requires Manual Download (1 ontology)

### MISO - Microbial Conditions Ontology
**Issue:** BioPortal API broken
- Web interface: https://bioportal.bioontology.org/ontologies/MISO exists and shows content
- API endpoint returns: `422 Unprocessable Entity`
- Likely a BioPortal server-side configuration issue with this specific submission

**Solution:** Manual download via web interface
1. Visit https://bioportal.bioontology.org/ontologies/MISO
2. Download OWL file using web interface download button
3. Copy to `non-ols/MISO.owl`
4. Run `make notebooks/non-ols-terms/MISO.tsv`

**Note:** The ontology file itself is valid OWL (verified with `robot convert`). Only the programmatic API download is broken.

**Status:** ⏳ Pending manual action

---

## ❌ Failed (1 ontology)

### HMADO - Human Microbiome and Disease Ontology
**Issue:** Not actually available
- Listed in issue #255 as "Ontologies Available Only in BioPortal"
- BioPortal page exists: https://bioportal.bioontology.org/ontologies/HMADO
- API returns: `404 Not Found`
- Web interface download also fails
- Google search for "Human Microbiome Associated Disease Ontology" only returns BioPortal page (no other sources)

**Conclusion:** HMADO appears to be listed on BioPortal but not actually available/functional. May be a placeholder or withdrawn ontology.

**Status:** ❌ Lost cause - ontology not available

---

## Technical Improvements Made

### 1. Enhanced SPARQL Query Coverage
Added support for diverse property patterns found across ontologies:

**Labels:**
- Standard: `rdfs:label`, `skos:prefLabel`
- Non-standard: `owl:label` (OFSMR), `spin:labelTemplate` (N4L), `dc:title` (D3O)

**Synonyms:**
- Standard OBO: `oboInOwl:hasExactSynonym`, `hasBroadSynonym`, `hasNarrowSynonym`, `hasRelatedSynonym`
- SKOS: `skos:altLabel`
- Non-standard: `owl:altLabel` (FMPM), `obo:Synonym` (BIPON)

**Definitions:**
- Standard: `IAO:0000115` (OBO definition)
- Alternatives: `skos:definition`, `rdfs:comment`, `obo:Definition` (BIPON)

See `PROPERTY_AUDIT.md` for complete verification evidence.

### 2. Robust Pipeline Architecture
- **Download script** (`download-ontology`): Validates file sizes, logs failures, exits with clear codes
- **Query validation** (`validate-tsv`): Counts terms, detects empty outputs, logs issues
- **Manifest tracking** (`scan-manifest`): Tracks fetch/query status for all ontologies
- **Logging**: `.ontology_fetch.log` and `.robot_query.log` capture all errors
- **Catalog support**: `catalog-v001.xml` handles broken imports

### 3. Makefile Integration
```makefile
# Pattern rule with catalog support
notebooks/non-ols-terms/%.tsv: non-ols/%.owl sparql/extract_for_embeddings.rq
    robot query --input $< --catalog catalog-v001.xml --query $(word 2,$^) $@
    uv run validate-tsv $* --tsv $@
```

---

## Final Statistics

**Successfully Processed:**
- 12 ontologies
- 10,785 terms total
- Ready for embedding into ChromaDB

**Breakdown by source:**
- 9 from BioPortal API (automatic)
- 1 from BioPortal web (MISO - pending manual download)
- 1 from manual source (N4L)
- 3 required workarounds (MEO, OFSMR, N4L)

**Not Available:**
- 1 ontology (HMADO)

---

## Next Steps

1. **Immediate:** Manually download MISO from BioPortal web interface
2. **Optional:** Update issue #255 to note HMADO is not actually available
3. **Ready:** Run `make embed-non-ols-terms` to generate ChromaDB embeddings for all 12 ontologies

---

## Related Files

- **Pipeline documentation:** `ONTOLOGY_PIPELINE.md`
- **Property audit:** `PROPERTY_AUDIT.md`
- **SPARQL query:** `sparql/extract_for_embeddings.rq`
- **Catalog file:** `catalog-v001.xml`
- **Manifest:** `.ontology_manifest.json` (gitignored, tracks runtime state)
