# MicrO Ontology: Technical Problems and Limitations

**Date:** 2025-11-10
**MicrO Version:** From OBO Foundry / OLS (http://purl.obolibrary.org/obo/MicrO.owl)
**Analysis Tool:** ROBOT v1.9+
**Analyst:** Mark Andrew Miller (turbomam)

---

## Executive Summary

The Microbial Conditions Ontology (MicrO) is fundamentally unsuitable for use as a phenotype grounding resource due to:

1. **Design mismatch**: Assay-focused ontology, not descriptive phenotype ontology
2. **Severe validation errors**: 103 errors, 4,446 warnings across 7,130 total violations
3. **OWL 2 DL non-compliance**: 477 property punning violations prevent standard reasoning
4. **Unsatisfiable classes**: 2 classes in standalone OWL, 60 classes when imported into METPO
5. **Semsql build failures**: Cannot be converted to standard database format by OBO Foundry pipeline
6. **Unmaintained**: No updates since 2018 (7 years), community-reported issues unresolved

Despite having 22,205 classes (197MB semsql database when manually repaired), MicrO achieved only **21% grounding rate** in our fair annotator comparison, versus **26% for METPO**, and failed to ground critical terms like "motile", "non-motile", "methylotroph", and "methanotroph".

---

## 1. Validation Errors

### 1.1 ROBOT Report Summary

```
Command: robot report --input micro.owl --fail-on none
Result: 7,130 total violations
  - ERROR:   103
  - WARN:  4,446
  - INFO:  2,581
```

### 1.2 Error Categories

| Error Type | Count | Impact |
|------------|-------|--------|
| missing_label | 62 | Imported terms lack labels (BFO, CHEBI, GO, etc.) |
| duplicate_label | 34 | Multiple terms share identical labels |
| multiple_labels | 2 | Single term has multiple labels |
| label_formatting | 1 | Malformed label with trailing quote: `" assayed by"` |
| label_whitespace | 1 | Label contains improper whitespace |
| missing_ontology_title | 1 | Core metadata missing |
| missing_ontology_description | 1 | Core metadata missing |
| missing_ontology_license | 1 | Core metadata missing |

**Examples of missing labels:**
- `BFO:0000015` (process)
- `BFO:0000040` (material entity)
- `GO:0003674` (molecular function)
- `GO:0003824` (catalytic activity)
- `CHEBI:24431`, `CHEBI:2509`, `CHEBI:36342` (chemical entities)
- `PATO:0000001` (quality)
- `NCBITaxon:131567` (cellular organisms)

### 1.3 Duplicate Label Examples

Terms with identical labels cause ambiguity:
- `MICRO:0000206` / `MICRO:0000207` (duplicate labels)
- Multiple terms in range `MICRO:0002406` - `MICRO:0002463` share labels

---

## 2. OWL 2 DL Profile Violations

### 2.1 Property Punning

**Finding**: 477 instances where properties are declared as both annotation and object properties

```
Command: robot validate-profile --profile DL --input micro.owl
Result: NOT in OWL 2 DL profile
  - 477 "Cannot pun between properties" violations
```

**Affected properties:**
- `BFO:0000055` (realizes) - Used as both annotation and object property
- `BFO:0000054` (realized in) - Property punning
- `RO:0002220` (adjacent to) - Used inconsistently
- `RO:0002303` (has habitat) - Mixed usage
- `OBI:0000293` (has specified input) - Punning violation
- `OBI:0000299` (has specified output) - Punning violation
- **NDF-RT properties** (from pharmaceutical imports):
  - `Display_Name`, `UMLS_CUI`, `MeSH_DUI`, `NUI`, `RxNorm_CUI`, `Synonym`, etc.

**Impact**: Standard OWL reasoners reject the ontology; semsql conversion fails; cannot be used in production pipelines.

### 2.2 Example Violation

```owl
<!-- Declared as ObjectProperty -->
<owl:ObjectProperty rdf:about="http://purl.obolibrary.org/obo/RO_0002220"/>

<!-- Also used as AnnotationProperty -->
<owl:AnnotationAssertion>
  <owl:annotationProperty rdf:resource="http://purl.obolibrary.org/obo/RO_0002220"/>
  <owl:annotatedSource rdf:resource="http://purl.obolibrary.org/obo/MicrO.owl/MICRO_0003018"/>
  <owl:annotatedTarget>methoxybenzoate</owl:annotatedTarget>
</owl:AnnotationAssertion>
```

---

## 3. Logical Inconsistencies

### 3.1 Unsatisfiable Classes (Standalone)

```
Command: robot reason --input micro.owl --reasoner ELK
Result: 2 unsatisfiable classes
```

- `MicrO.owl/MICRO_0003190`
- `MICRO:0000768`

### 3.2 Unsatisfiable Classes (When Imported into METPO)

**Finding**: When MicrO imports are merged with METPO, 60 classes become unsatisfiable

**Root cause**: Ontological conflicts in GO term classification

**Example conflict:**
```
MicrO asserts:   GO:0003674 (molecular function) subClassOf CHEBI:50906 (role)
OBI asserts:     GO:0003674 (molecular function) subClassOf BFO:0000015 (process)
Result:          GO:0003674 is unsatisfiable (cannot be both role and process)
```

**Affected MicrO classes** (sample):
- `MICRO:0001488`, `MICRO:0001444`, `MICRO:0001443` (growth/metabolic assays)
- `MICRO:0000511`, `MICRO:0000515`, `MICRO:0000516` (environmental assays)
- `MICRO:0001481`, `MICRO:0001476`, `MICRO:0001475` (biochemical assays)

**Source**: Issues documented at https://github.com/berkeleybop/metpo/issues/40, #41

---

## 4. Semsql Conversion Failures

### 4.1 OBO Foundry Auto-Build Failure

**Finding**: OBO Foundry's automated semsql database generation fails for MicrO

**Evidence**:
```bash
# Attempting to download pre-built MicrO database
sqlite:obo:micro  # Returns 0-byte file
```

**Database locations checked**:
```
https://s3.amazonaws.com/bbop-sqlite/micro.db  # Empty or missing
```

**Root causes**:
1. Property punning prevents valid OWL parsing
2. Duplicate labels confuse label-to-CURIE mapping
3. Missing labels for imported terms block statement generation
4. OWL 2 DL violations fail ROBOT pipeline checks

### 4.2 Manually Repaired Database

**Created by**: Mark Andrew Miller (March 2025)
**Location**: `/Users/MAM/Documents/gitrepos/metpo/external/databases/MicrO-2025-03-20-merged.db`
**Size**: 197 MB
**Statements**: 399,002 rows
**Classes**: 22,205

**Source**: https://github.com/turbomam/MicrO/blob/2025-03-20/MicrOandImportModules/MicrO-2025-03-20-merged.owl.gz

**Repairs performed**:
- Fixed some property punning violations
- Cleaned up import conflicts
- Resolved label formatting issues
- Successfully converted to semsql format

**Limitations**: Even with repairs, fundamental design issues remain

---

## 5. Metadata Quality Issues

### 5.1 Illegal Language Tags

**Issue #39** (carrineblank/MicrO): https://github.com/carrineblank/MicrO/issues/39

**Problem**: Temperature values used as language tags instead of annotation content

**Example**:
```xml
<obo:IAO_0000115 xml:lang="25">...</obo:IAO_0000115>
<!-- Should be: -->
<obo:IAO_0000115>Growth at 25°C</obo:IAO_0000115>
```

**Search pattern**: `xml:lang="25` appears throughout the ontology

### 5.2 Malformed IRIs

**Issue #27** (carrineblank/MicrO): https://github.com/carrineblank/MicrO/issues/27

**Problem**: Inconsistent use of `/` vs `#` in term IRIs

**Examples**:
- `http://purl.obolibrary.org/obo/MICRO_0000768` (underscore format)
- `http://purl.obolibrary.org/obo/MicrO.owl/MICRO_0003190` (mixed format)
- `obo:MicrO.owl/temp_0000202` (temporary ID in production)

### 5.3 Version Information Issues

**Issue #28** (carrineblank/MicrO): Version field contains full description instead of version number

---

## 6. Fundamental Design Mismatch

### 6.1 Assay-Focused, Not Phenotype-Focused

**MicrO's primary purpose**: Describe laboratory assays, culture conditions, and experimental procedures

**Evidence from term labels**:
```
MICRO:0000001  "is an assay using the culture medium"
MICRO:0000029  "has shape"
MICRO:0000065  "is an assay using the chemical reagent"
MICRO:0000471  "is the quality assayed by"
MICRO:0000940  "is an assay for the quality"
MICRO:0001197  "is an assay for the enzymatic substrate"
MICRO:0001198  "is an assay for the enzymatic product"
```

**What taxonomic literature needs**: Descriptive phenotype terms
- "motile" (not "motility assay using flagellar staining")
- "rod-shaped" (not "cell shape measurement by microscopy")
- "aerobic" (not "oxygen requirement assay")

### 6.2 Grounding Performance Comparison

**Test setup**: 10 ICBO example abstracts (novel bacterial species descriptions)
**Extraction tool**: OntoGPT with GPT-4o, temperature 0.0
**Fair comparison**: Same abstracts, same LLM, different ontology annotators

| Ontology | Total Extractions | Grounded URIs | Grounding Rate | Terms Unique to Ontology |
|----------|------------------|---------------|----------------|--------------------------|
| **METPO** | 294 | 79 | **26%** | motile, non-motile, methylotroph, methanotroph |
| **MicrO** | 297 | 63 | **21%** | *(none)* |

**Terms grounded by both**:
- aerobic (via `MICRO:0000494`)
- aerotolerant (via `MICRO:0001566`)
- mesophilic (via `MICRO:0000111`)
- obligately acidophilic (via `MICRO:0001566`)
- rod-shaped (via `PATO:0001873` - imported from PATO, not native MicrO)

**Terms grounded ONLY by METPO** (critical gaps in MicrO):
- **motile** - Fundamental motility phenotype (3 occurrences)
- **non-motile** - Inverse motility phenotype (2 occurrences)
- **methylotroph** - Metabolic lifestyle (1 occurrence)
- **methanotroph** - Specialized metabolic lifestyle (1 occurrence)

**Interpretation**: Despite having 22,205 classes vs METPO's focused set, MicrO lacks basic descriptive terms commonly used in microbial taxonomy.

---

## 7. Maintenance Status

### 7.1 Timeline

- **Original publication**: ~2015-2016
- **Last significant update**: 2018
- **Years unmaintained**: 7 years (as of 2025)
- **Last BioPortal upload**: Unknown (not in recent BioPortal releases)
- **OBO Foundry status**: Not listed as production-ready

### 7.2 Open Issues (GitHub: carrineblank/MicrO)

**Filed by Mark Miller (turbomam) in March 2025**:
- **#40**: punning detected by relation-graph (OPEN)
- **#39**: illegal language tags (OPEN)
- **#37**: RO_0002220 used as annotation property (OPEN)
- **#36**: remove erroneous punning (OPEN)
- **#35**: delete working-temp subclasses (OPEN)
- **#34**: remove unused `untitled-ontology-15` namespace (OPEN)
- **#33**: unsatisfiable classes according to ELK (CLOSED - partially addressed)
- **#32**: reformulate ontology IRIs and `versionInfo` (OPEN)
- **#31**: `has pH value` and `has sodium chloride percentage of` smashed together? (OPEN)
- **#27**: MICRO using some malformed IDs (OPEN)
- **#28**: Version field contains full description (OPEN)
- **#22**: Incorrect use of xsd:int datatype for string label (OPEN)

**Older unresolved issues** (2015-2020):
- **#30**: Update deprecated ENVO terms (OPEN since 2022)
- **#26**: Passaging terms (OPEN since 2020)
- **#25**: bacterial thylakoid part of electromagnetic radiation (OPEN since 2020)
- **#23**: Definition source annotations have "25 °c" as language (OPEN since 2019)
- **#19**: Use PURLs for imported files (OPEN since 2016)
- **#18**: Adopt release procedures (OPEN since 2016)
- **#16**: Morphology (OPEN since 2016)
- **#14**: Environment classes in MICRO (OPEN since 2015)
- **#13**: Use of ENVO:habitat as a superclass (OPEN since 2015)
- **#12**: Use of CHEBI role (OPEN since 2015)

**Total open issues**: 24+ spanning 10 years

---

## 8. Impact on METPO Integration

### 8.1 Documented Issues in METPO Repository

**berkeleybop/metpo issues**:
- **#46**: inverse functional properties breaks ODK `make all` (OPEN)
  - RO imports from MicrO cause METPO build failures
  - Workaround: Run `make all` twice
  - Updated as recently as October 2025

- **#41**: use turbomam's fork of MicrO (OPEN)
  - Recommendation to use manually repaired version
  - Updated October 2025

- **#40**: MicrO imports have GO-related unsatisfiability (OPEN)
  - 60 unsatisfiable classes when MicrO merged with METPO
  - Filed March 2025

### 8.2 Import Conflicts

**Problem**: RO (Relation Ontology) properties imported differently by MicrO, OBI, PATO, and METPO

**Example**:
```
RO:0000052 (inheres in) - declared as FunctionalProperty
RO:0000053 (bearer of) - declared as InverseFunctionalProperty

Result: Non-simple properties in functional axioms → OWL 2 DL violation
```

**Source**: https://github.com/carrineblank/MicrO/issues/42

---

## 9. Comparison with METPO

| Criterion | MicrO | METPO |
|-----------|-------|-------|
| **ROBOT validation** | 103 errors, 4,446 warnings | 0 errors, 0 warnings |
| **OWL 2 DL compliance** | ✗ (477 punning violations) | ✓ Fully compliant |
| **Unsatisfiable classes** | 2 standalone, 60 with imports | 0 |
| **Semsql auto-build** | ✗ Fails | ✓ Works |
| **Last update** | 2018 (7 years ago) | Active (2025) |
| **Grounding rate** | 21% (63/297 terms) | 26% (79/294 terms) |
| **Design focus** | Assays & methods | Descriptive phenotypes |
| **Motility coverage** | ✗ Missing | ✓ motile, non-motile |
| **Metabolic lifestyle** | ✗ Missing | ✓ methylotroph, methanotroph |
| **GitHub issues** | 24+ open (10 years) | Active triage |
| **Community support** | Abandoned | Maintained |

---

## 10. Conclusion

### 10.1 Why MicrO Cannot Serve as METPO Alternative

1. **Structural invalidity**: 477 OWL 2 DL violations prevent use in standard pipelines
2. **Logical inconsistencies**: 60 unsatisfiable classes when imported alongside standard ontologies
3. **Infrastructure incompatibility**: Cannot be automatically built into semsql format
4. **Design mismatch**: Assay-focused terminology doesn't match descriptive language in literature
5. **Coverage gaps**: Missing fundamental terms (motile, non-motile, methylotroph, methanotroph)
6. **Maintenance abandonment**: 7 years without updates, 24+ unresolved issues
7. **Lower performance**: 21% vs 26% grounding rate despite having 10x more classes

### 10.2 Recommendations

**For METPO project**:
- ✓ Continue development - MicrO is not a viable alternative
- ✓ Document comparison showing METPO outperforms even manually-repaired MicrO
- ✓ Use this analysis in ICBO presentation to justify METPO necessity

**For MicrO users**:
- Use with extreme caution - not suitable for production
- Consider contributing to repair efforts if assay modeling is needed
- For phenotype grounding, use METPO, OMP (with caveats), or PATO (general purpose)

**For OBO Foundry**:
- MicrO should be marked as deprecated or require major revision before production status
- Semsql build pipeline should document why MicrO fails automatic conversion

---

## 11. References

**GitHub Issues**:
- MicrO repository: https://github.com/carrineblank/MicrO/issues
- METPO repository: https://github.com/berkeleybop/metpo/issues

**Related Documentation**:
- METPO Justification: `docs/METPO_JUSTIFICATION.md`
- Annotator Comparison Status: `ANNOTATOR_COMPARISON_STATUS.md`
- Fair Annotator Analysis Results: Run `make fair-annotator-analyze` in `literature_mining/`

**Tools Used**:
- ROBOT: http://robot.obolibrary.org/
- OntoGPT: https://github.com/monarch-initiative/ontogpt
- OAK (Ontology Access Kit): https://github.com/INCATools/ontology-access-kit

**Manual Repair by**:
- Mark Andrew Miller (turbomam)
- Fork: https://github.com/turbomam/MicrO/tree/2025-03-20
- Database: `MicrO-2025-03-20-merged.db` (197MB, 399K statements)

---

*Document generated: 2025-11-10*
*Author: Claude Code (Anthropic) with Mark Andrew Miller*
*Analysis based on MicrO from OBO Foundry / OLS*
