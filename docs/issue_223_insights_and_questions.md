# Issue #223 Investigation: Insights and Open Questions

**Date:** 2025-10-03
**Task:** Round-trip assessment of METPO's coverage of structured source values
**Status:** Analysis complete, validation questions remain

---

## Executive Summary

Completed comprehensive analysis of METPO's synonym claims against three primary data sources (Madin, BacDive, BactoTraits). Found:
- **Madin**: 14.6% coverage (15/103 pathways), 88 values missing
- **BacDive**: 100% verified (16/16 synonyms correct)
- **BactoTraits**: Critical naming mismatch requiring investigation

---

## Key Insights

### 1. METPO's Role in KG-Microbe Architecture

**Understanding from context:**
- METPO codifies textual values from raw data sources into formal ontology terms
- These become nodes in KGX knowledge graph format
- Node category hierarchy (preference): Biolink Model → High-profile ontologies (ChEBI) → METPO → Legacy placeholders

**Historical context:**
- KG-Microbe previously used placeholder CURIEs (e.g., `oxygen:aerobic`) before METPO existed
- METPO was developed to replace/formalize these placeholders
- Some "very old practices" still in use for KGX generation (per PI's workflow)

**Critical question:** How does the transition from placeholder CURIEs to METPO CURIEs work?
- Are placeholders being replaced?
- Do they coexist with equivalence mappings?
- Does this explain some of the synonym format choices?

---

### 2. Data Source Characteristics (from microbial_trait_datasets_background.md)

| Source | Type | Update Cadence | Access |
|--------|------|----------------|--------|
| **Madin et al.** | Frozen 2020 synthesis of 26 sources | Static snapshot | GitHub CSV/TSV |
| **BacDive** | Continuously curated strain database | Live updates | REST API (JSON) + CSV export |
| **BactoTraits** | Derived largely from BacDive | Static v2 (Jun 2022) | Institutional repository CSV |

**Key insight:** BactoTraits is derived from BacDive, explaining potential overlap and why BacDive identifiers are useful for crosswalking.

---

### 3. The BactoTraits Transformation Mystery

**Problem discovered:**
METPO's claimed BactoTraits synonyms don't match MongoDB field names.

**Examples of mismatch:**

| METPO Claims | MongoDB Actual | Field Category |
|--------------|----------------|----------------|
| `GC_<42.65` | `lte_42dot65` | GC content |
| `GC_42.65_57.0` | `42dot65_to_57dot0` | GC content |
| `TO_<10` | `optimum` (nested) | Temperature optimum |
| `TR_<10` | `range` (nested) | Temperature range |
| `pHO_0_to_6` | `optimum` (nested) | pH optimum |
| `Ox_aerobic` | `aerobic` | Oxygen preference |
| `s_curved_spiral` | `curved_spiral` | Cell shape |
| `G_positive` | `positive` | Gram stain |
| `motile` | `motile` ✓ | Motility |
| `non-motile` | `non_motile` | Motility |

**MongoDB actual structure:**
```javascript
{
  gc_content: {
    lte_42dot65: 1,
    42dot65_to_57dot0: 0,
    57dot0_to_66dot3: 0,
    gt_66dot3: 0
  },
  oxygen: {
    aerobic: 1,
    anaerobic: 0,
    facultative_aerobe_anaerobe: 0,
    microerophile: 0
  },
  temperature: {
    optimum: 25.5,
    range: [15, 35],
    delta: 20
  },
  cell_shape: {
    curved_spiral: 0,
    filament: 0,
    ovoid: 0,
    rod: 1,
    sphere: 0,
    star_dumbbell_pleomorphic: 0
  }
  // etc.
}
```

**Hypotheses:**

1. **CSV → MongoDB transformation**: The original `BactoTraits_databaseV2_Jun2022.csv` was transformed/normalized before MongoDB loading
   - Original CSV might have had different column headers
   - Transformation process needs to be documented
   - METPO synonyms might be based on original CSV headers, not MongoDB representation

2. **Placeholder CURIE legacy**: The prefixes (GC_, TO_, TR_, Ox_, s_, G_) might represent:
   - Attempts to match some intermediate format
   - Legacy placeholder CURIE naming conventions
   - An older version of BactoTraits data

3. **Multiple data versions**: METPO synonyms might reference:
   - An older version of BactoTraits (pre-v2 Jun 2022)
   - The raw CSV before transformation
   - An export format different from what's in MongoDB

**Action needed:**
- [ ] Read original `BactoTraits_databaseV2_Jun2022.csv` from kg-microbe raw data
- [ ] Compare CSV column headers to MongoDB field names
- [ ] Document the transformation mapping
- [ ] Determine which representation METPO synonyms should match

---

### 4. Madin Pathway Coverage Gap

**Verified coverage:** 15/103 pathways (14.6%)

**What's covered (15 pathways):**
- acetogenesis
- aerobic_anoxygenic_phototrophy
- aerobic_chemo_heterotrophy
- aerobic_heterotrophy
- anoxygenic_photoautotrophy (+ 3 subtypes: hydrogen/iron/sulfur oxidation)
- autotrophy
- fermentation
- heterotrophic
- methanogenesis
- methylotrophy
- photoautotrophy
- photoheterotrophy

**Missing categories (88 pathways):**
- **27 degradation pathways**: cellulose, chitin, hydrocarbon, aromatic compounds, lignin, plastic, etc.
- **24 oxidation pathways**: sulfur, iron, methane, manganese, hydrogen, arsenite, minerals, etc.
- **16 reduction pathways**: nitrate, sulfate, iron, manganese, denitrification, etc.
- **2 disproportionation**: dithionite, thiosulfate
- **2 nitrogen cycle**: annamox, nitrogen_fixation
- **2 methanogenesis subtypes**: acetoclastic, H2CO2

**Questions:**
- Are these 88 missing pathways currently represented as placeholder CURIEs in KG-Microbe?
- Would adding them to METPO allow retiring those placeholders?
- Should they be added as new METPO classes or synonyms of existing classes?
- Is there a hierarchical organization planned for:
  - Degradation processes (parent class)
  - Oxidation processes (parent class)
  - Reduction processes (parent class)
  - Disproportionation processes (parent class)

---

### 5. BacDive Perfect Match

**100% verification success:**
- All 9 oxygen tolerance synonyms match BacDive API values exactly
- All 7 halophily synonyms match BacDive API values exactly
- No false claims found

**This validates:**
- BacDive synonyms were created carefully against actual API data
- The nested JSON structure was properly traversed
- Field paths like `'Physiology and metabolism'.'oxygen tolerance'.'oxygen tolerance'` are correct

**Recommendation:** Use BacDive synonym creation process as template for fixing BactoTraits.

---

## Open Questions

### Architecture & Design

1. **KGX node format transition:**
   - How are placeholder CURIEs (`oxygen:aerobic`) being migrated to METPO CURIEs?
   - Should I examine actual KGX files in kg-microbe to understand current node formats?
   - Are there any mapping/equivalence files between old placeholders and METPO terms?

2. **METPO synonym format requirements:**
   - Should synonyms match the MongoDB representation (as found in data)?
   - Or should they match the original source format (CSV headers)?
   - Or should they match the KGX placeholder format?
   - Are there multiple synonym types (exact, broad, related) for different representations?

3. **Hierarchical organization:**
   - Should missing Madin pathways be organized into parent classes?
   - What's the strategy for pathway hierarchy (degradation → substrate-specific)?
   - Are there Biolink Model categories that should be used for metabolic pathways?

### Data Source Reconciliation

4. **BactoTraits transformation:**
   - Where is the CSV → MongoDB transformation code?
   - Is it in kg-microbe ETL pipeline?
   - Should METPO synonyms be updated to match MongoDB or kept aligned with CSV?

5. **Source versioning:**
   - Which version of each source should METPO synonyms target?
   - Madin: 2020 snapshot (static) ✓
   - BacDive: Current API (continuous updates) - should synonyms track changes?
   - BactoTraits: v2 Jun 2022 - but which representation?

6. **Crosswalking between sources:**
   - Since BactoTraits is derived from BacDive, should there be explicit mappings?
   - Should METPO classes reference both sources if they contain the same concept?
   - Example: oxygen preference in both BacDive and BactoTraits

### Validation & Quality

7. **Automated validation:**
   - Should we create scripts to verify synonym claims against MongoDB?
   - How often should validation run (on METPO release? On source updates?)?
   - What's the process when sources update and synonyms become stale?

8. **Synonym scope:**
   - METPO synonym column contains mixed content:
     - Attribute paths (e.g., "pathways", "oxygen tolerance")
     - Actual values (e.g., "aerobic", "fermentation")
   - Is this intentional design?
   - Should attribute paths be in a separate annotation property?

### Priority & Next Steps

9. **Issue #223 next actions:**
   - Should I fix BactoTraits synonyms immediately?
   - Should I add missing Madin pathways immediately?
   - Or gather more requirements first?

10. **PI's "old practices" for KGX:**
    - What are the old practices?
    - Do they impose constraints on how METPO should be structured?
    - Is there a migration plan to newer practices?

---

## Recommendations for Discussion

### Immediate Actions (after clarification)

1. **Investigate BactoTraits CSV** to understand transformation
   - Read original CSV from kg-microbe raw data
   - Map CSV columns → MongoDB fields
   - Determine which representation METPO should target

2. **Examine KGX files** to understand current usage
   - Look at actual node formats in kg-microbe output
   - Identify placeholder CURIEs vs METPO CURIEs
   - Understand edge cases and usage patterns

3. **Document transformation processes**
   - CSV → MongoDB mappings for each source
   - Version/snapshot information
   - Field normalization rules

### Medium-term Improvements

4. **Fix BactoTraits synonyms** (after understanding target format)
   - Remove incorrect prefixes (GC_, TO_, TR_, Ox_, s_, G_)
   - Match actual MongoDB field names
   - Handle nested structures (temperature, pH, NaCl)

5. **Add missing Madin pathways** (88 values)
   - Prioritize by category: degradation → reduction → oxidation
   - Create parent classes for organization
   - Map to Biolink Model categories where applicable

6. **Create automated validation**
   - Scripts to verify synonyms against MongoDB
   - Regular testing on source updates
   - CI/CD integration for METPO releases

### Long-term Strategy

7. **Hierarchical organization**
   - Create parent classes for major process types
   - Align with GO biological processes where appropriate
   - Maintain flat synonym list for backward compatibility

8. **Source version tracking**
   - Document which source version each synonym targets
   - Plan for handling source updates
   - Consider deprecation workflow for outdated synonyms

9. **KGX modernization**
   - Understand current "old practices"
   - Plan migration to newer approaches
   - Ensure METPO structure supports modern workflows

---

## Files Generated During Investigation

### Analysis Reports
- `metpo_madin_pathway_coverage.md` - Detailed Madin pathway gap analysis
- `metpo_source_coverage_analysis.md` - Comprehensive three-source analysis
- `kg_microbe_datasets.md` - Complete inventory of kg-microbe data sources
- `issue_223_insights_and_questions.md` - This file

### Temporary Analysis Files (for reference)
- `/tmp/madin_pathways_mongo.txt` - 103 unique Madin pathway values
- `/tmp/metpo_madin_synonyms.txt` - 70 METPO synonyms claiming Madin
- `/tmp/missing_in_metpo_final.txt` - 88 missing pathway values
- `/tmp/bacdive_verification.txt` - BacDive synonym verification results

### MongoDB Queries Used
```javascript
// Madin pathways
db.madin.aggregate([
  { $match: { pathways: { $ne: 'NA' } } },
  { $project: { pathway_array: { $split: ['$pathways', ', '] } } },
  { $unwind: '$pathway_array' },
  { $group: { _id: '$pathway_array' } },
  { $sort: { _id: 1 } }
])

// BacDive oxygen tolerance
db.strains_api.distinct('Physiology and metabolism.oxygen tolerance.oxygen tolerance')

// BacDive halophily
db.strains_api.distinct('Physiology and metabolism.halophily.halophily level')

// BactoTraits structure sample
db.bactotraits.findOne({gc_content: {$exists: true}})
```

---

## Next Session Preparation

**Before proceeding with fixes, need clarification on:**
1. Target format for synonyms (MongoDB vs CSV vs KGX placeholders)
2. Strategy for missing Madin pathways (new classes vs synonyms)
3. KGX generation practices and constraints
4. Source version tracking requirements

**Ready to proceed with:**
- BactoTraits CSV investigation (once direction is clear)
- KGX file examination (if helpful)
- Automated validation script creation
- Synonym corrections (after format decision)
