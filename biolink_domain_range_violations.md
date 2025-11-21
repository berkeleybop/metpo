# Biolink Model Domain/Range Violations in kg-microbe

**Analysis Date:** 2025-11-20
**Data Source:** kg-microbe transformed data (local build from 2025-11-11, commit 77c42d8)

## Summary

Found **293,080 edges** (15.9% of 1,862,932 total) with Biolink Model domain/range violations across all kg-microbe data sources.

## Violation Categories

### 1. Wrong Object Type for `capable_of` (186,197 edges - 10.0%)

**Issue:** Using `biolink:capable_of` with `PhenotypicQuality` as object instead of `Occurrent` (biological process)

**Biolink Constraint:**
- Domain: NamedThing
- Range: **Occurrent** (biological processes)

**Actual Usage:**
- `biolink:OrganismTaxon` → `biolink:capable_of` → `biolink:PhenotypicQuality` (with EC enzyme IDs)

**Impact:** 186,197 edges across bacdive and madin_etal

**Root Cause:** EC enzyme codes (e.g., `EC:3.1.1.1`) are being categorized as `biolink:PhenotypicQuality` but used as if they were `biolink:BiologicalProcess`. EC codes represent enzyme activities (processes), not qualities.

**Fix Options:**
1. **Recategorize EC nodes** as `biolink:BiologicalProcess` or `biolink:MolecularActivity`
2. **Use different predicate** like `biolink:has_phenotype` if EC codes should remain as qualities
3. **Add intermediate nodes** representing the actual biological processes

### 2. Missing Object Category for `has_phenotype` (44,081 edges - 2.4%)

**Issue:** Object nodes have empty/null `category` field

**Biolink Constraint:**
- Domain: BiologicalEntity
- Range: **PhenotypicFeature**

**Actual Usage:**
- `biolink:OrganismTaxon` → `biolink:has_phenotype` → `(empty category)` (METPO IDs)

**Impact:** 44,081 edges in madin_etal

**Root Cause:** METPO phenotype nodes in madin_etal dataset are missing category assignments

**Fix:** Assign `biolink:PhenotypicQuality` or `biolink:PhenotypicFeature` category to all METPO nodes

### 3. Missing Subject Category (23,258 edges - 1.3%)

**Issue:** Subject nodes have `(unknown)` or `(empty)` categories

**Patterns:**
- `(unknown)` ENVO nodes → `biolink:location_of` → organisms (14,888 edges)
- `(empty)` isolation_source nodes → `biolink:location_of` → organisms (6,775 edges)
- `(unknown)` NCBITaxon nodes in various predicates (1,595 edges)

**Fix:**
- Assign `biolink:EnvironmentalFeature` to ENVO and isolation_source nodes
- Assign `biolink:OrganismTaxon` to NCBITaxon nodes with missing categories

### 4. Missing Object Category for `subclass_of` (13,010 edges - 0.7%)

**Issue:** Object nodes have `(unknown)` category in taxonomic hierarchy

**Biolink Constraint:**
- Domain: OntologyClass
- Range: **OntologyClass**

**Actual Usage:**
- `biolink:OrganismTaxon` (strain) → `biolink:subclass_of` → `(unknown)` (NCBITaxon)

**Impact:** 13,010 edges in bacdive

**Fix:** Assign category to all NCBITaxon nodes (should be `biolink:OrganismTaxon`)

### 5. Non-Standard Predicates (23,289 edges - 1.3%)

**Predicates not found in Biolink Model:**

| Predicate | Count | Notes |
|-----------|-------|-------|
| `biolink:produces` | 12,523 | Should probably be `biolink:has_output` |
| `biolink:associated_with_resistance_to` | 10,297 | Complement of `associated_with_sensitivity_to` |
| `biolink:has_chemical_role` | 357 | May be valid but not in our constraint set |
| `biolink:is_assessed_by` | 112 | Inverse of `biolink:assesses` (which also isn't standard) |

**Fix:** Map to standard Biolink predicates or request addition to Biolink Model

### 6. Minor Issues (772 edges - 0.04%)

- Missing object categories for `occurs_in`, `location_of`, `consumes`
- Various `(unknown)` category issues

## Breakdown by Data Source

| Source | Violations | Total Edges | % Violations |
|--------|------------|-------------|--------------|
| bacdive | ~230,000 | 1,656,667 | ~13.9% |
| madin_etal | ~58,000 | 115,397 | ~50.3% |
| bactotraits | ~5,000 | 90,768 | ~5.5% |

## Recommendations

### Priority 1: Fix EC Node Categories
- Recategorize all EC enzyme codes as `biolink:BiologicalProcess` or `biolink:MolecularActivity`
- Impact: Fixes 186,197 edges (63% of all violations)

### Priority 2: Assign Missing Categories
- Add categories to all METPO phenotype nodes in madin_etal
- Add categories to ENVO environmental nodes
- Impact: Fixes 81,349 edges (28% of all violations)

### Priority 3: Standardize Predicates
- Map `biolink:produces` → `biolink:has_output`
- Map `biolink:assesses` → standard predicate (or keep as domain-specific)
- Add `biolink:associated_with_resistance_to` to Biolink Model
- Impact: Fixes 23,289 edges (8% of all violations)

## Files Generated

- `kg_microbe_edge_patterns.tsv` - All unique edge patterns with counts
- `biolink_violations.tsv` - Full violation report with status for each pattern
- `biolink_predicate_constraints.json` - Domain/range constraints used
- `extract_edge_patterns.py` - Script to extract patterns
- `check_biolink_violations.py` - Script to check violations

## Notes

- **NamedThing Policy:** We treat NamedThing as satisfied by any non-empty, non-unknown category, per Biolink's definition of NamedThing as the root of all entity types
- **ChemicalEntity Range:** The constraint checker may have issues with `ChemicalEntity` vs `biolink:ChemicalEntity` - needs review
- **Implicit Violations:** Some violations may be "implicit" (using parent classes where child classes are expected) - these are generally acceptable in OWL/RDF reasoning but flagged here for data quality

## Related Issues

- #30 - Broader KGX format compliance
- #432-434, #436 - BacDive CURIE format violations
