# kg-microbe BacDive Implementation Analysis

**Date:** 2025-10-22
**Analyzed commit:** 8a32701 (Merge pull request #413)

## Executive Summary

The kg-microbe BacDive ingest code (`kg_microbe/transform_utils/bacdive/bacdive.py`) uses a **hybrid approach** that combines:
1. **Structured JSON path extraction** for most phenotypes (NEW approach - lines 1594-1634)
2. **General.keywords extraction** as fallback and for certain fields (lines 983-988, 1330-1380)
3. **METPO tree-based mapping** that dynamically extracts values from both sources

The implementation is **already fairly sophisticated** but there are opportunities for improvement based on my MongoDB analysis.

## Files Used by BacDive Ingest

### Primary Code Files
1. **`kg_microbe/transform_utils/bacdive/bacdive.py`** (1788 lines)
   - Main transform class `BacDiveTransform`
   - Processes BacDive JSON → KGX nodes/edges

2. **`kg_microbe/utils/mapping_file_utils.py`** (351 lines)
   - `load_metpo_mappings()` - Loads METPO synonym mappings
   - `_build_metpo_tree()` - Builds METPO class hierarchy
   - `MetpoTreeNode` class - Represents nodes in METPO tree

3. **`kg_microbe/transform_utils/constants.py`**
   - All constant definitions (paths, predicates, categories, etc.)

### Configuration/Mapping Files

4. **`kg_microbe/transform_utils/custom_curies.yaml`** (406 lines)
   - Non-METPO keyword mappings
   - Handles keywords NOT yet in METPO
   - Categories: salinity, production, pathogen, GC content, pigment, pH, NaCl, temperature, cell dimensions

5. **Remote METPO templates** (fetched at runtime):
   - `https://raw.githubusercontent.com/berkeleybop/metpo/refs/tags/2025-09-23/src/templates/metpo_sheet.tsv`
   - `https://raw.githubusercontent.com/berkeleybop/metpo/refs/tags/2025-09-23/src/templates/metpo-properties.tsv`

6. **`data/transformed/bacdive/bacdive_mappings.tsv`**
   - Maps BacDive test names → EC numbers, CHEBI IDs, KEGG IDs

7. **`data/transformed/bacdive/metabolite_mapping.json`** (generated at runtime)
   - Maps CHEBI IDs to antibiotic/metabolite names

### Input Data
8. **`data/raw/bacdive_strains.json`**
   - Downloaded BacDive strain data (99,393 strains in my MongoDB)

## Biological Aspects Prioritized

Based on code analysis (lines 1594-1634, 983-1380), kg-microbe extracts:

### 1. Core Phenotypes (from structured paths via METPO tree)
Lines 1594-1634 use `_process_phenotype_by_metpo_parent()`:

- **Oxygen preference** (METPO:1000601)
  - Path: `Physiology and metabolism.oxygen tolerance.oxygen tolerance`
  - Extracts: aerobic, anaerobic, facultative, etc.

- **Spore formation** (METPO:1000870)
  - Path: `Physiology and metabolism.spore formation.spore formation`
  - Extracts: yes/no

- **Trophic type** (METPO:1000631)
  - Path: `Physiology and metabolism.nutrition type.type`
  - Extracts: autotroph, heterotroph, chemotroph, etc.

- **Cell shape** (METPO:1000666)
  - Path: `Morphology.cell morphology.cell shape`
  - Extracts: rod-shaped, coccus-shaped, etc.

- **Gram stain** (METPO:1000697)
  - Path: `Morphology.cell morphology.gram stain`
  - Extracts: positive, negative, variable

- **Motility** (METPO:1000701)
  - Path: `Morphology.cell morphology.motility`
  - Extracts: yes/no

### 2. Keywords (General.keywords)
Lines 983-988, 1330-1380 process keywords:

- **Temperature preference** (mesophilic, thermophilic, psychrophilic, hyperthermophilic)
  - **NOTE:** This is the ONLY source for temperature preference - no structured path exists!

- **Halophily** (halophilic, halotolerant, etc.)
  - Available in both keywords AND structured path

- **Pathogen type** (human pathogen, animal pathogen, plant pathogen)
  - Only in keywords

- **Production capabilities** (antibiotic production, toxin production, metabolite production)
  - Only in keywords

- **Pigmentation** (pigmented)
  - Only in keywords (generic)

- **Antibiotic resistance** (keyword)
  - Only in keywords

### 3. Metabolic Data (from structured sections)
Lines 1408-1767:

- **Enzymes** (EC numbers)
  - Path: `Physiology and metabolism.enzymes`
  - Only extracts positive activity ('+' sign)

- **Metabolite utilization** (CHEBI IDs)
  - Path: `Physiology and metabolism.metabolite utilization`
  - Only extracts positive utilization ('+' sign)

- **Metabolite production** (CHEBI IDs)
  - Path: `Physiology and metabolism.metabolite production`
  - Only extracts positive production ('yes')

- **Antibiotic resistance/sensitivity** (CHEBI IDs with threshold logic)
  - Path: `Physiology and metabolism.antibiotic resistance`
  - Numeric threshold: <15 = resistance, >25 = sensitivity

- **Antibiogram** (API tests)
  - Path: `Physiology and metabolism.antibiogram`
  - Processes all API test results

- **API tests** (various assays)
  - Path: `Physiology and metabolism.API *` (any key starting with "API ")
  - Only extracts positive results ('+' sign)

### 4. Other Extracted Data
Lines 842-922, 1132-1160, 1164-1406:

- **Isolation sources** (environment categories)
- **Culture media** (growth conditions)
- **Biosafety level** (from risk assessment)
- **Taxonomy** (NCBI taxon IDs)
- **Strain designations**

## Current Implementation Strategy

### The METPO Tree Approach (NEW - Sophisticated!)

The code builds a tree structure from METPO classes with these features:

1. **Dual synonym handling:**
   - BacDive synonyms can be **literal values** ("aerobic") OR **JSON paths** ("Physiology and metabolism.oxygen tolerance.oxygen tolerance")
   - The code differentiates by checking for dots in the synonym

2. **Dynamic path traversal:**
   - For each METPO parent (e.g., oxygen preference METPO:1000601)
   - Extracts all JSON paths associated with that parent
   - Extracts values from those paths
   - Matches extracted values against child node synonyms
   - Creates edges with appropriate predicates

3. **Predicate inference:**
   - Traverses up the METPO tree to find the closest parent with `biolink equivalent`
   - Uses that parent's label to look up predicate in properties sheet
   - Example: "aerobic" → parent "oxygen preference" → predicate "has phenotype"

4. **Category inference:**
   - Uses parent's `biolink equivalent` as the category
   - Falls back to "biolink:PhenotypicQuality"

### Keyword Processing (OLDER - Simpler)

Lines 983-988, 1330-1380:
```python
keywords = general_info.get(KEYWORDS, "")
nodes_from_keywords = {
    key: keyword_map[key.lower().replace(" ", "_").replace("-", "_")]
    for key in keywords
    if key.lower().replace(" ", "_").replace("-", "_") in keyword_map
}
```

This processes General.keywords by:
1. Normalizing keyword names (lowercase, underscores)
2. Looking up in `keyword_map` (built from METPO + custom_curies.yaml)
3. Creating nodes and edges for matched keywords

**The keyword_map includes:**
- METPO mappings (from tree traversal)
- Custom CURIE mappings (from custom_curies.yaml)
- Dynamically extracted values from the record itself

## Comparison with My Analysis Recommendations

### ✅ Already Implemented Well

1. **✅ Structured path extraction is prioritized**
   - Lines 1594-1634 process all major phenotypes from specific JSON paths
   - Uses METPO tree for systematic extraction

2. **✅ Keywords used for temperature preference**
   - My analysis found this is the ONLY source
   - Code correctly uses keywords for this (no temperature path extraction)

3. **✅ Hybrid approach for halophily**
   - Code can extract from both keywords and structured paths
   - If METPO tree has path defined, it uses that; otherwise falls back to keywords

4. **✅ Smart predicate/category inference**
   - Uses parent traversal for predicate determination
   - Better than hardcoding predicates

### ⚠️ Potential Improvements Based on My Analysis

#### 1. Missing Gram stain keyword variants (4,425 strains affected)

**Issue:** My analysis found 4,425 strains have Gram stain ONLY in keywords as:
- "Gram-positive" (keyword)
- "Gram-negative" (keyword)
- "Gram-variable" (keyword)

But METPO has synonyms as:
- "positive" (structured path value)
- "negative" (structured path value)
- "variable" (structured path value)

**Current behavior:**
- Line 1622-1627 processes Gram stain from `Morphology.cell morphology.gram stain`
- This ONLY gets "positive"/"negative"/"variable" from the structured path
- Does NOT capture "Gram-positive"/"Gram-negative"/"Gram-variable" from keywords

**Recommendation:** Add to METPO template or custom_curies.yaml:
```yaml
gram_stain:
  gram_positive:
    curie: "METPO:1000698"  # or whatever the METPO ID is
    name: "gram positive"
    category: "biolink:PhenotypicQuality"
    predicate: "biolink:has_phenotype"
  gram_negative:
    curie: "METPO:1000699"
    name: "gram negative"
    category: "biolink:PhenotypicQuality"
    predicate: "biolink:has_phenotype"
  gram_variable:
    curie: "METPO:1000700"
    name: "gram variable"
    category: "biolink:PhenotypicQuality"
    predicate: "biolink:has_phenotype"
```

#### 2. Missing "motile" keyword (113 strains affected)

**Issue:** My analysis found 113 strains have "motile" in keywords but NOT in structured path.

**Current behavior:**
- Line 1629-1634 processes motility from `Morphology.cell morphology.motility`
- This gets "yes"/"no" from structured path
- Does NOT capture "motile" keyword

**Current METPO mapping (from template):**
- METPO has "yes" and "no" as synonyms for motility
- But NOT "motile"

**Recommendation:** Add to METPO template's motile class:
```tsv
METPO:1000702  motile  ...  motile  ...
```
(Add "motile" to the `bacdive keyword synonym` column)

#### 3. Missing "spore-forming" keyword (1,440 strains affected)

**Issue:** My analysis found 1,440 strains have "spore-forming" in keywords but NOT in structured path.

**Current behavior:**
- Line 1601-1606 processes spore formation from `Physiology and metabolism.spore formation.spore formation`
- This gets "yes"/"no" from structured path
- Does NOT capture "spore-forming" keyword

**Current METPO mapping:**
- METPO has "yes", "no", and "spore" as synonyms
- But NOT "spore-forming"

**Recommendation:** Add to METPO template's spore-forming class:
```tsv
METPO:1000871  spore forming  ...  spore-forming|yes  ...
```

#### 4. Consider adding missing high-value keywords

**Issue:** My analysis found several high-usage keywords NOT in METPO or custom_curies.yaml:

High priority (already in custom_curies.yaml but worth noting):
- ✅ antibiotic_compound_production (508 occurrences) - **ALREADY MAPPED**
- ✅ human_pathogen (1,607 occurrences) - **ALREADY MAPPED**
- ✅ animal_pathogen (700 occurrences) - **ALREADY MAPPED**
- ✅ plant_pathogen (376 occurrences) - **ALREADY MAPPED**
- ✅ pigmented (166 occurrences) - **ALREADY MAPPED**
- ✅ antibiotic_resistance (157 occurrences) - **ALREADY MAPPED**

Medium priority (NOT mapped):
- colony-forming (2,582 occurrences) - might be too generic?
- Bacteria (97,270 occurrences) - taxonomy, not phenotype
- Archaea (1,125 occurrences) - taxonomy, not phenotype
- 16S sequence (27,058 occurrences) - data availability, not phenotype
- genome sequence (17,617 occurrences) - data availability, not phenotype

**Recommendation:** Current coverage is actually pretty good! The main gaps are:
1. Gram-* variants (addressed above)
2. motile (addressed above)
3. spore-forming (addressed above)
4. colony-forming (debatable if needed - low information content)

### ✅ No Changes Needed

1. **Cell shape** - Already well-handled by structured path extraction
2. **Halophily** - Already well-handled (can use both sources)
3. **Trophic type** - Already well-handled by structured path extraction
4. **Oxygen preference** - Already well-handled by structured path extraction

## Data Flow Summary

```
BacDive JSON Record
        ↓
    ┌───┴───────────────────────────────────────┐
    │                                           │
    ↓                                           ↓
General.keywords                    Structured sections
    ↓                                           ↓
Normalized                          JSON path extraction
(lowercase, underscores)            (via METPO tree)
    ↓                                           ↓
Lookup in keyword_map                   Match against synonyms
    │                                   in child nodes
    │                                           ↓
    │                                   Find METPO mapping
    │                                           │
    └───────────────┬───────────────────────────┘
                    ↓
            Create KGX nodes/edges
            (with predicates from METPO properties)
```

## Key Insight: The Two-Phase Approach

The code uses a sophisticated two-phase approach:

### Phase 1: Build keyword_map for this record
Lines 318-414 in `_build_keyword_map_from_record()`:
1. Start with custom_curies.yaml mappings
2. Add all METPO synonym mappings
3. **Traverse METPO tree** and extract values from THIS specific record
4. For each extracted value, find matching child nodes
5. Add those matches to keyword_map

This means the keyword_map is **record-specific** and includes:
- Static mappings (METPO + custom curies)
- Dynamic mappings (extracted from this record via JSON paths)

### Phase 2: Process keywords and paths
1. Extract from structured paths via `_process_phenotype_by_metpo_parent()` (lines 1594-1634)
2. Process General.keywords via keyword_map (lines 983-988, 1330-1380)
3. The keyword_map already knows about values extracted from structured paths (Phase 1)

## Recommendations Summary

### Immediate Actions (Easy Fixes)

1. **Add Gram stain keyword variants to METPO or custom_curies.yaml**
   - Maps "Gram-positive" → METPO:1000698
   - Maps "Gram-negative" → METPO:1000699
   - Maps "Gram-variable" → METPO:1000700
   - Affects 4,425 strains

2. **Add "motile" to METPO motile class synonyms**
   - Add to `bacdive keyword synonym` column in metpo_sheet.tsv
   - Affects 113 strains

3. **Add "spore-forming" to METPO spore-forming class synonyms**
   - Add to `bacdive keyword synonym` column in metpo_sheet.tsv
   - Affects 1,440 strains

### Medium Priority

4. **Document the temperature preference data source**
   - Add comment in code noting temperature preference ONLY comes from keywords
   - This is by design (no structured path exists in BacDive)
   - My analysis confirms this is correct approach

5. **Consider adding missing specific pigment keywords**
   - My analysis found specific pigment colors in General.keywords
   - custom_curies.yaml already has some (pink, yellow, brown, red, etc.)
   - But BacDive keywords don't include the specific colors - just "pigmented"
   - No action needed unless BacDive changes their keywords

### Low Priority / Optional

6. **Consider handling "colony-forming" keyword**
   - 2,582 occurrences
   - But very low information content (most bacteria form colonies)
   - Probably not worth adding

7. **Validate the 4,425 Gram stain keyword-only cases**
   - Sample some records to confirm they truly lack Morphology.cell morphology.gram stain
   - Verify these aren't data quality issues in BacDive
   - If they're valid, the custom_curies.yaml fix is appropriate

## Files to Modify

To implement recommendations:

1. **For METPO synonyms:**
   - `/Users/MAM/Documents/gitrepos/metpo/src/templates/metpo_sheet.tsv`
   - Add "motile" and "spore-forming" to appropriate rows' `bacdive keyword synonym` column

2. **For non-METPO keywords:**
   - `/Users/MAM/Documents/gitrepos/kg-microbe/kg_microbe/transform_utils/custom_curies.yaml`
   - Add gram_stain section with Gram-positive/negative/variable mappings

3. **For documentation:**
   - `/Users/MAM/Documents/gitrepos/kg-microbe/kg_microbe/transform_utils/bacdive/bacdive.py`
   - Add comments around lines 983-988 explaining temperature preference data source

## Questions for Team Discussion

1. **Should Gram-* variants go in METPO or custom_curies.yaml?**
   - METPO is more formal/standardized
   - custom_curies.yaml is quicker to update
   - I lean towards custom_curies.yaml for now, then move to METPO in next release

2. **Should "motile" map to the same METPO class as "yes" (for motility)?**
   - They mean the same thing
   - But "motile" is an adjective, "yes" is an answer to "is it motile?"
   - I think same class is fine

3. **Should "spore-forming" map to the same METPO class as "yes" (for spore formation)?**
   - Similar question as motile
   - I think same class is fine

4. **Should we add a validation step that warns when keywords contradict structured paths?**
   - Example: keyword says "aerobic" but structured path says "anaerobic"
   - This would help catch data quality issues
   - Might be overkill for now

5. **The code uses METPO tag 2025-09-23 - should this be updated?**
   - Line 14 in mapping_file_utils.py
   - Currently points to old release
   - Might want to point to latest or main branch

## Conclusion

The kg-microbe BacDive ingest code is **well-architected** and already uses a sophisticated hybrid approach. The main gaps are:

1. **4,425 strains** missing Gram stain due to keyword format mismatch
2. **1,440 strains** missing spore formation due to keyword format mismatch
3. **113 strains** missing motility due to keyword format mismatch

All three can be fixed by adding synonym mappings (either in METPO or custom_curies.yaml).

The temperature preference reliance on keywords is **correct by design** - my MongoDB analysis confirms there is no structured temperature preference path in BacDive data.

Overall, the implementation aligns well with my recommendations from the earlier analysis. The METPO tree-based approach is elegant and provides good coverage of the BacDive data.
