# BacDive Data Path Issues Created

Created 7 comprehensive GitHub issues in turbomam/issues repository for BacDive data transformation improvements.

## Issues Created

| Issue # | Title | BacDive Path | Current Status | Priority |
|---------|-------|--------------|----------------|----------|
| [#31](https://github.com/turbomam/issues/issues/31) | BacDive Enzyme Activity | `Physiology and metabolism → enzymes` | Positive only, category violation | High |
| [#32](https://github.com/turbomam/issues/issues/32) | BacDive Metabolite Utilization | `Physiology and metabolism → metabolite utilization` | Positive only | High |
| [#33](https://github.com/turbomam/issues/issues/33) | BacDive Metabolite Production | `Physiology and metabolism → metabolite production` | Positive only, non-standard predicate | High |
| [#34](https://github.com/turbomam/issues/issues/34) | BacDive Metabolite Tests | `Physiology and metabolism → metabolite tests` | **NOT TRANSFORMED** | Critical |
| [#35](https://github.com/turbomam/issues/issues/35) | BacDive API Assays | `Physiology and metabolism → API *` (multiple types) | Positive only, pseudo-CURIEs | High |
| [#36](https://github.com/turbomam/issues/issues/36) | BacDive Antibiotic Resistance | `Physiology and metabolism → antibiotic resistance` | Resistant only | High |
| [#37](https://github.com/turbomam/issues/issues/37) | BacDive Antibiogram | `Physiology and metabolism → antibiogram` | Resistant only, quantitative data lost | High |

## Common Themes Across All Issues

### Problems Identified

1. **Negative/susceptible test results ignored**: All data types only transform positive/resistant results
2. **Quantitative data lost**: Zone diameters, MIC values, intensity scores not captured
3. **No METPO mapping**: None of these biochemical data types currently use METPO terms
4. **Non-standard predicates**: `biolink:produces`, `biolink:assesses`, `biolink:associated_with_resistance_to`
5. **Category violations**: EC codes as `biolink:PhenotypicQuality` instead of process/activity
6. **Incomplete transformation**: Metabolite tests extracted but never converted to graph

### Proposals Provided

For each issue, provided:

1. ✅ **Full BacDive JSON path** with data structure examples
2. ✅ **Current transformation behavior** with line numbers and code references
3. ✅ **METPO usage status** (currently none for all biochemical data)
4. ✅ **Negative test result handling proposals** with specific METPO term examples
5. ✅ **ROBOT template examples** for `src/templates/metpo_sheet.tsv`
6. ✅ **Annotation property recommendations** from IAO, SKOS, oboInOwl, biolink, RO
7. ✅ **Minimal METPO-specific properties** - emphasized standard vocabularies

### Standard Vocabularies Recommended

**Annotation properties used across issues**:
- `IAO:0000115` (definition)
- `oboInOwl:hasExactSynonym` (exact synonym)
- `oboInOwl:hasBroadSynonym` (broad synonym)
- `oboInOwl:hasDbXref` (database cross-reference)
- `skos:exactMatch` (exact match for EC codes)
- `skos:relatedMatch` (related match for CHEBI)
- `biolink:close_match` (close match to biolink categories)
- `RO:0000057` (has participant)
- `RO:0002234` (has output)
- `RO:0002558` (has evidence)
- `IAO:0000004` (has measurement value)
- `IAO:0000039` (has measurement unit specification)

**External ontologies for cross-referencing**:
- CHEBI (chemicals/metabolites)
- EC (enzymes)
- GO (biological processes)
- ARO (antibiotic resistance)
- PATO (qualities)
- UO (units)
- CLSI/EUCAST (testing standards)

## Implementation Priority

### Critical (Must Fix)

**Issue #34 - Metabolite Tests**: Currently NOT transformed at all despite being extracted. Includes fundamental diagnostic tests (catalase, oxidase, Voges-Proskauer).

### High Priority (Major Data Loss)

**All other issues**: All lose 40-60% of test result data by ignoring negative/susceptible outcomes.

Specific high-impact fixes:
- **Issue #31**: 186K edges with category violation (EC codes as qualities)
- **Issue #32**: Missing fermentative vs. assimilatory distinction
- **Issue #33**: Using non-standard `biolink:produces` predicate
- **Issue #35**: Complex pseudo-CURIE system needs proper ontology terms
- **Issue #36, #37**: Clinical antimicrobial resistance data incomplete

## Next Steps

1. **Review ROBOT template proposals** in each issue
2. **Add METPO terms** to `src/templates/metpo_sheet.tsv` for highest priority tests
3. **Update kg-microbe transformation** to use METPO terms and capture negative results
4. **Request Biolink additions**: 
   - Add `biolink:associated_with_resistance_to` to model
   - Standardize `biolink:assesses` or provide alternative
5. **Integrate ARO**: Cross-reference antibiotic resistance terms
6. **Build METPO hierarchy**: Organize terms by biological phenomenon, not test kit

## Files Referenced

- `kg-microbe/kg_microbe/transform_utils/bacdive/bacdive_transform.py` (transformation code)
- `kg-microbe/kg_microbe/transform_utils/bacdive/bacdive_mappings.tsv` (assay mappings)
- `src/templates/metpo_sheet.tsv` (ROBOT template)
- `edge_pattern_assessment.md` (semantic analysis)
- `biolink_domain_range_violations.md` (constraint violations)

## Related Work

These issues build on:
- **Issue #438**: EC code categorization violation
- **Issue #439**: Missing METPO categories
- **Issue #440**: organism-medium relationship
- **Issues #432-434, #436**: BacDive CURIE format violations
- **Issue #30**: Broader KGX format compliance

## Data Impact

Implementing these changes would:
- **Add ~150K edges** for negative enzyme activity results
- **Add ~100K edges** for metabolite utilization negative results
- **Add ~50K edges** for metabolite production negative results  
- **Add ~100K edges** for metabolite test results (currently missing entirely)
- **Add ~50K edges** for negative API assay results
- **Add ~20K edges** for antibiotic susceptibility/intermediate results
- **Add quantitative measurements** for antibiogram zone diameters

**Total**: ~470K new edges representing negative test results and quantitative measurements, nearly 25% increase in kg-microbe data completeness.
