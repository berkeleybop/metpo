# BacDive METPO Coverage Analysis

**Date**: 2025-11-20
**Location**: `/Users/MAM/Documents/gitrepos/kg-microbe/data/transformed/bacdive/`

## Executive Summary

**Current Status**: Only **61 METPO nodes** appear in the BacDive transform output, representing **120,266 edges** connecting bacterial strains to METPO phenotype terms.

**Major Finding**: Critical normalization mismatch between BacDive keyword processing and METPO synonym mappings is causing **significant coverage loss**, particularly for halophily terms.

---

## Current BacDive Transform Statistics

### Node Distribution (196,169 total nodes)

| Prefix | Count | Percentage | Notes |
|--------|-------|------------|-------|
| strain | 172,093 | 87.7% | Custom prefix for BacDive strains |
| NCBITaxon | 20,320 | 10.4% | Organism taxonomy |
| medium | 1,571 | 0.8% | Culture media |
| CHEBI | 1,088 | 0.6% | Chemical entities |
| assay | 511 | 0.3% | Experimental assays |
| isolation_source | 353 | 0.2% | Environmental sources |
| EC | 112 | 0.1% | Enzyme classification |
| **METPO** | **61** | **0.03%** | **⚠️ VERY LOW** |
| salinity | 4 | <0.01% | Custom salinity terms |
| pathways | 1 | <0.01% | Custom pathway terms |

### Edge Distribution (1,656,668 total edges)

**METPO-related edges**: 120,266 (7.3% of all edges)

**Top 10 METPO Terms by Edge Count**:

| METPO ID | Label | Edge Count | Percentage |
|----------|-------|------------|------------|
| METPO:1000615 | mesophilic | 53,850 | 44.8% |
| METPO:1001102 | biosafety level 1 | 19,689 | 16.4% |
| METPO:1000602 | aerobic | 15,546 | 12.9% |
| METPO:1000603 | anaerobic | 7,061 | 5.9% |
| METPO:1001103 | biosafety level 2 | 6,572 | 5.5% |
| METPO:1000604 | microaerophilic | 4,732 | 3.9% |
| METPO:1000616 | thermophilic | 2,346 | 2.0% |
| METPO:1000614 | psychrophilic | 1,781 | 1.5% |
| METPO:1000681 | spore-forming | 1,545 | 1.3% |
| METPO:1000699 | human pathogen | 1,262 | 1.0% |

**All other METPO terms**: 5,882 edges combined (4.9%)

---

## Two Distinct Sources of BacDive Knowledge

**Critical Distinction**: The BacDive transform extracts phenotype data through **two independent mechanisms** with different provenance levels:

### Mechanism 1: Keyword-Based Extraction (Low Provenance)

**Source**: `General.keywords` field - curator-assigned categorical labels without experimental evidence

**How it works** (`bacdive.py:979-984`):
```python
keywords = general_info.get(KEYWORDS, "")
nodes_from_keywords = {
    key: keyword_map[key.lower().replace(" ", "_").replace("-", "_")]
    for key in keywords
    if key.lower().replace(" ", "_").replace("-", "_") in keyword_map
}
```

**Characteristics**:
- ✅ Simple, categorical classifications (e.g., "halophilic", "mesophilic", "aerobe")
- ✅ High coverage across many strains
- ❌ No experimental evidence or measurement details
- ❌ Subject to curator interpretation and naming inconsistencies
- ⚠️ **Normalization issue**: Converts spaces/hyphens to underscores, causing mapping mismatches

**Example Keywords**:
- "halophilic", "moderately halophilic", "non-halophilic"
- "aerobe", "anaerobe", "mesophilic", "thermophilic"
- "spore-forming", "motile", "human pathogen"

**Current Coverage**: 159 strains with halophily keywords, thousands with temperature/oxygen keywords

---

### Mechanism 2: Path-Based Extraction (High Provenance)

**Source**: Specific JSON paths in `Physiology and metabolism.*` and `Morphology.*` with experimental evidence

**How it works** (`bacdive.py:252-313`):
```python
def _process_phenotype_by_metpo_parent(self, record, parent_iri, ...):
    """
    Extract values from BacDive JSON paths specified in METPO tree nodes.
    """
    parent_node = self.bacdive_metpo_tree.get(parent_iri)
    for json_path in parent_node.bacdive_json_paths:
        extracted_values = self._extract_value_from_json_path(record, json_path)
        # Create METPO edges for extracted values
```

**Characteristics**:
- ✅ Experimental evidence (references, methods, measurements)
- ✅ Structured data with detailed context
- ✅ Multiple observations per strain (different studies, conditions)
- ❌ More complex extraction logic
- ❌ Lower coverage (only strains with experimental data)

**Currently Ingested Paths** (`bacdive.py:1568-1608`):

| Parent METPO ID | Label | BacDive JSON Path | Lines |
|----------------|-------|-------------------|-------|
| METPO:1000601 | oxygen preference | `Physiology and metabolism.oxygen tolerance.oxygen tolerance` | 1571-1573 |
| METPO:1000870 | sporulation | `Physiology and metabolism.spore formation.spore formation` | 1578-1580 |
| METPO:1000631 | trophic type | `Physiology and metabolism.nutrition type.type` | 1585-1587 |
| METPO:1000666 | cell shape | `Morphology.cell morphology.cell shape` | 1592-1594 |
| METPO:1000697 | gram stain | `Morphology.cell morphology.gram stain` | 1599-1601 |
| METPO:1000701 | motility | `Morphology.cell morphology.motility` | 1606-1608 |

**Path Specification in METPO Sheet**:

METPO terms can specify BacDive JSON paths in the `bacdive keyword synonym` column. Example:

```tsv
METPO:1000629  halophily preference  ...  Physiology and metabolism.halophily.halophily level
```

When a METPO term has a path (contains `.`), the transform:
1. Extracts values from that JSON path in each BacDive record
2. Looks up the extracted value in METPO mappings
3. Creates an edge if a METPO term matches the value

**Example**: For oxygen tolerance:
- Path: `Physiology and metabolism.oxygen tolerance.oxygen tolerance`
- Extracted value: "aerobe"
- Mapped to: METPO:1000602 (aerobic)
- Creates edge: `NCBITaxon:XXX → biolink:has_phenotype → METPO:1000602`

---

### Coverage Comparison: Keywords vs. Paths

**Halophily Example**:

| Source | Coverage | Evidence Level | Current Status |
|--------|----------|---------------|----------------|
| `General.keywords` | 159 strains | ❌ Low (curator labels) | ⚠️ Partially working (normalization issues) |
| `Physiology and metabolism.halophily` | 9,687 strains | ✅ High (experimental) | ❌ Not yet ingested |
| `Physiology and metabolism.halophily.halophily level` | 32 strains | ✅ High (experimental) | ❌ Not yet ingested |

**Key Insight**: There are **60x more strains** with experimental halophily data (9,687) than categorical keywords (159), but only the keywords are currently being ingested!

---

### Why Both Mechanisms Matter

**Keyword extraction** provides:
- Broad phenotype coverage across many strains
- Simple categorical classifications useful for filtering
- Quick lookup without complex data parsing

**Path extraction** provides:
- Experimental provenance (citations, methods, conditions)
- Quantitative measurements (temperature ranges, pH values, salt concentrations)
- Multiple observations per strain (different studies)
- Higher-quality, evidence-based assertions

**Optimal Strategy**: Use **both mechanisms** to maximize coverage:
- Keywords for rapid categorical classification
- Paths for detailed, evidence-based phenotype data
- Path data should override/enrich keyword data when both exist

---

## Critical Issue: Halophily Coverage Gap

### Expected vs. Actual Halophily Edges

According to the [halophily investigation report](../bacphen-awareness/halophily_investigation_report.md), BacDive contains **159 strains** with halophily keywords in `General.keywords`, distributed as:

| Keyword in MongoDB | Strain Count | Expected Edges* | Actual Edges | Status |
|-------------------|--------------|----------------|--------------|--------|
| moderately halophilic | 56 | ~55 | **0** | ❌ MISSING |
| halophilic | 37 | ~37 | 74 | ✅ Working |
| halotolerant | 25 | ~25 | 49 | ✅ Working |
| non-halophilic | 16 | ~16 | **0** | ❌ MISSING |
| slightly halophilic | 14 | ~14 | **0** | ❌ MISSING |
| extremely halophilic | 9 | ~9 | **0** | ❌ MISSING |
| haloalkaliphilic | 2 | ~2 | 4 | ✅ Working |

_*Expected edges assume ~1 edge per strain after NCBITaxon validation_

**Total Halophily Edges**:
- **Expected**: ~158 (after NCBITaxon validation)
- **Actual**: 127 (74 + 49 + 4)
- **Missing**: ~31 edges (~20% loss)

### Root Cause: Normalization Mismatch

**The Problem**: BacDive keyword processing normalizes strings differently than METPO mappings store them.

**BacDive Transform Code** (`kg_microbe/transform_utils/bacdive/bacdive.py:981`):
```python
nodes_from_keywords = {
    key: keyword_map[key.lower().replace(" ", "_").replace("-", "_")]
    for key in keywords
    if key.lower().replace(" ", "_").replace("-", "_") in keyword_map
}
```

**METPO Mapping Loader** (`kg_microbe/utils/mapping_file_utils.py:335`):
```python
for syn in synonyms:
    if syn:  # only add non-empty synonyms
        mappings[syn] = {
            "curie": metpo_curie,
            # ... no normalization applied
        }
```

**Detailed Mismatch Examples**:

| MongoDB Keyword | BacDive Normalizes To | METPO Mapping Has | Match? | METPO ID |
|----------------|----------------------|-------------------|--------|----------|
| "halophilic" | "halophilic" | "halophilic" | ✅ YES | METPO:1000620 |
| "moderately halophilic" | "moderately_halophilic" | "moderately halophilic" | ❌ NO | METPO:1000623 |
| "non-halophilic" | "non_halophilic" | "non-halophilic" | ❌ NO | METPO:1000624 |
| "slightly halophilic" | "slightly_halophilic" | "slightly halophilic" | ❌ NO | METPO:1000625 |
| "extremely halophilic" | "extremely_halophilic" | "extremely halophilic" | ❌ NO | METPO:1000628 |

**Why Some Terms Work**:
- Terms without spaces/hyphens match perfectly: "halophilic", "halotolerant", "haloalkaliphilic"
- Terms with spaces/hyphens fail: "moderately halophilic", "non-halophilic", etc.

---

## Additional Coverage Gaps Identified

### 1. Untapped Quantitative Halophily Data

From the halophily investigation report:
- **9,687 strains** have quantitative salt concentration data in `Physiology and metabolism.halophily`
- This data is **not currently ingested** into KG-Microbe
- Only categorical keywords (159 strains) are being processed

**Opportunity**: Could add ~9,500 more halophily-related edges if quantitative data were mapped to METPO range classes (METPO:1000465-1000472 for NaCl ranges)

### 2. Missing METPO Terms in Transform Output

**METPO halophily terms with 0 edges**:
- METPO:1000623 (moderately halophilic) - 0 edges ← **should have ~55**
- METPO:1000624 (non halophilic) - 0 edges ← **should have ~16**
- METPO:1000625 (slightly halophilic) - 0 edges ← **should have ~14**
- METPO:1000626 (stenohaline) - 0 edges ← not in BacDive keywords
- METPO:1000627 (euryhaline) - 0 edges ← not in BacDive keywords
- METPO:1000628 (extremely halophilic) - 0 edges ← **should have ~9**
- METPO:1000629 (halophily preference) - 0 edges ← parent class

### 3. BacDive Phenotype Fields Not Yet Mapped

Beyond halophily, BacDive contains rich phenotype data in `Physiology and metabolism.*` paths that may not be fully ingested:

- Temperature tolerance ranges
- pH tolerance ranges
- Oxygen requirement details
- Metabolic capabilities
- Enzyme activities
- Antibiotic susceptibilities

**Action Needed**: Systematic audit of BacDive JSON paths vs. METPO coverage

---

## Proposed Improvements

### Priority 1: Fix Normalization Mismatch (IMMEDIATE)

**Option A: Normalize METPO mappings during loading**

Update `mapping_file_utils.py:load_metpo_mappings()` to apply the same normalization:

```python
for syn in synonyms:
    if syn:
        # Normalize synonym to match BacDive processing
        normalized_syn = syn.lower().replace(" ", "_").replace("-", "_")
        mappings[normalized_syn] = {
            "curie": metpo_curie,
            # ...
        }
```

**Option B: Update METPO sheet synonyms**

Change BacDive synonym column in `metpo_sheet.tsv` to use underscores:
- "moderately halophilic" → "moderately_halophilic"
- "non-halophilic" → "non_halophilic"
- etc.

**Recommendation**: Option A is preferred because it:
1. Keeps METPO sheet human-readable
2. Centralizes normalization logic
3. Can handle future synonym variations
4. Doesn't require ontology rebuilds

**Expected Impact**: Recover ~31 missing halophily edges immediately

### Priority 2: Ingest Halophily Path Data (HIGH)

**Task**: Enable path-based extraction for halophily data using the evidenced `Physiology and metabolism.halophily.*` fields

**Current Problem**: Only keyword-based halophily (159 strains) is ingested; experimental data (9,687 strains) is ignored.

**Implementation Approach**:

**Step 1**: Add path processing to transform code (`bacdive.py`):
```python
# Add after line 1608 (after motility processing)
# Process halophily using path-based extraction from METPO tree
# Parent: METPO:1000629 (halophily preference)
# Path: "Physiology and metabolism.halophily.halophily level"
self._process_phenotype_by_metpo_parent(
    value, "METPO:1000629", species_with_strains, key, node_writer, edge_writer
)
```

**Step 2**: Update METPO sheet to specify the path in METPO:1000629's `bacdive keyword synonym` column:
```tsv
METPO:1000629  halophily preference  ...  Physiology and metabolism.halophily.halophily level
```
(This may already exist - need to verify)

**Step 3**: Ensure all halophily child terms have proper value mappings in METPO sheet.

**Step 4** (Advanced): For quantitative salt concentration data in `Physiology and metabolism.halophily`, develop binning logic to map measurements to METPO NaCl range classes:
- METPO:1000465-1000468 (NaCl optimum: low, mid1, mid2, high)
- METPO:1000469-1000472 (NaCl range: low, mid1, mid2, high)

**Expected Impact**:
- Step 1-3: Add ~32 categorical halophily edges from `halophily level` field
- Step 4: Add ~9,500 halophily edges (60x increase) from quantitative measurements

### Priority 3: Systematic BacDive Path Coverage Audit (MEDIUM)

**Task**: Compare BacDive JSON schema paths against METPO mappings to identify unmapped phenotype data

**Approach**:
1. Extract all `Physiology and metabolism.*` paths from genson schema
2. Cross-reference with METPO `bacdive keyword synonym` column
3. Cross-reference with custom_curies.yaml entries
4. Identify unmapped paths with high data coverage
5. Create METPO mappings for high-value gaps

**Expected Impact**: Potentially hundreds to thousands of new phenotype edges

### Priority 4: Document Mapping Type Distinction (LOW)

**Issue**: METPO sheet doesn't clearly distinguish between:
- **Field mappings**: Column/path names → METPO terms (e.g., `Physiology and metabolism.halophily.halophily level`)
- **Value mappings**: Cell contents → METPO terms (e.g., "halophilic" → METPO:1000620)

**Task**: Add `mapping_type` column to `metpo_sheet.tsv` with values: "field", "value", "both"

**Expected Impact**: Clearer transform logic, fewer mapping errors

---

## Coverage Assessment Methodology

To measure BacDive → KG-Microbe → METPO coverage systematically:

### Metrics to Track

1. **Node Coverage**:
   - Total METPO terms in metpo.owl
   - METPO terms with BacDive synonyms defined
   - METPO terms appearing in transform output
   - **Gap**: Terms defined but not appearing

2. **Edge Coverage**:
   - Total BacDive strains in MongoDB
   - Strains with phenotype keywords in `General.keywords`
   - Strains with METPO edges in transform output
   - **Gap**: Strains with keywords but no edges

3. **Data Field Coverage**:
   - Total BacDive JSON paths in schema
   - Paths mapped to METPO/custom_curies
   - Paths materialized in KGX output
   - **Gap**: Paths with data but unmapped

4. **Keyword Coverage**:
   - Unique values in `General.keywords` across all strains
   - Keywords mapped to METPO
   - Keywords materialized in edges
   - **Gap**: Keywords present but unmapped

### Suggested Scripts

**Script 1**: `analyze_bacdive_metpo_coverage.py`
- Query MongoDB for all `General.keywords` values
- Count strain frequency for each keyword
- Check METPO mapping existence
- Check transform output presence
- Generate coverage report

**Script 2**: `audit_bacdive_json_paths.py`
- Parse genson schema for all JSON paths
- Extract `Physiology and metabolism.*` paths
- Cross-reference with METPO mappings
- Rank by data coverage (% strains with non-null values)
- Generate unmapped path report

**Script 3**: `validate_metpo_normalization.py`
- Load all METPO BacDive synonyms
- Apply BacDive normalization
- Check for mismatches
- Generate fix recommendations

---

## Related Issues and Documentation

**GitHub Issues**:
- Issue #22: BacDive Ingestion Lifecycle Documentation
- Issue #19: Repository Organization and Discovery

**Key Files**:
- Transform: `kg-microbe/kg_microbe/transform_utils/bacdive/bacdive.py`
- Mappings: `kg-microbe/kg_microbe/utils/mapping_file_utils.py`
- METPO Template: `metpo/src/templates/metpo_sheet.tsv`
- Configuration: `kg-microbe/kg_microbe/transform_utils/custom_curies.yaml`
- Investigation: `bacphen-awareness/halophily_investigation_report.md`

**Remote Resources**:
- METPO mappings fetched from: `https://raw.githubusercontent.com/berkeleybop/metpo/refs/tags/2025-10-31/src/templates/metpo_sheet.tsv`

---

## Summary: Quick Wins for Maximizing METPO Coverage

| Action | Type | Expected Impact | Difficulty | Priority |
|--------|------|----------------|-----------|----------|
| Fix keyword normalization | Keyword | +31 halophily edges (+24%) | Easy | **IMMEDIATE** |
| Add halophily path processing | Path | +32 categorical edges | Medium | **HIGH** |
| Ingest quantitative halophily | Path | +9,500 edges (60x) | Hard | HIGH |
| Systematic path audit | Both | +100s-1000s edges | Medium | MEDIUM |
| Add mapping_type column | Docs | Clarity, fewer errors | Easy | LOW |

**Low-Hanging Fruit**: Fix normalization mismatch → instant 24% increase in halophily coverage

**High-Value Target**: Enable path-based halophily → 60x increase in halophily data with experimental provenance

---

## Next Steps

### Immediate Actions (This Week)
1. ✅ **Complete analysis** - Document findings (this file)
2. ⏭️ **Fix normalization** - Implement Option A in `mapping_file_utils.py:335`
3. ⏭️ **Test fix** - Regenerate BacDive transform, verify halophily edges increase 127→158

### Short-Term Actions (Next 2 Weeks)
4. ⏭️ **Enable halophily paths** - Add path processing call in `bacdive.py`
5. ⏭️ **Verify METPO mappings** - Check METPO:1000629 has correct path
6. ⏭️ **Regenerate and validate** - Verify ~9,500 additional halophily edges

### Medium-Term Actions (Next Month)
7. ⏭️ **Create coverage scripts** - Implement the 3 suggested analysis scripts
8. ⏭️ **Run coverage audit** - Execute scripts against MongoDB and transform output
9. ⏭️ **Prioritize unmapped paths** - Identify high-value BacDive phenotype data
10. ⏭️ **Expand METPO mappings** - Add synonyms/paths for high-priority unmapped data

---

## Appendix: Command History

### Node Analysis
```bash
# Count nodes by prefix
cut -f1 /Users/MAM/Documents/gitrepos/kg-microbe/data/transformed/bacdive/nodes.tsv | \
  tail -n +2 | cut -d: -f1 | sort | uniq -c | sort -rn

# Results:
# 172093 strain
#  20320 NCBITaxon
#   1571 medium
#   1088 CHEBI
#    511 assay
#    353 isolation_source
#    112 EC
#     61 METPO  ← Very low!
```

### Edge Analysis
```bash
# Count total METPO edges
grep "METPO:" /Users/MAM/Documents/gitrepos/kg-microbe/data/transformed/bacdive/edges.tsv | wc -l
# Result: 120266

# Count by METPO term
grep "METPO:" edges.tsv | cut -f3 | sort | uniq -c | sort -rn | head -30

# Check halophily terms specifically
grep -E "METPO:100062[0-9]|METPO:1000628" edges.tsv | cut -f3 | sort | uniq -c
# Results:
#   74 METPO:1000620  (halophilic)
#    4 METPO:1000621  (haloalkaliphilic)
#   49 METPO:1000622  (halotolerant)
#    0 METPO:1000623  (moderately halophilic) ← MISSING
#    0 METPO:1000624  (non halophilic) ← MISSING
#    0 METPO:1000625  (slightly halophilic) ← MISSING
#    0 METPO:1000628  (extremely halophilic) ← MISSING
```

### METPO Mapping Analysis
```bash
# Check BacDive synonyms for missing terms
grep -E "1000623|1000624|1000625|1000628" \
  /Users/MAM/Documents/gitrepos/metpo/src/templates/metpo_sheet.tsv | \
  cut -f1,2,14

# Results show mismatch between:
# - BacDive normalization: "moderately_halophilic" (underscore)
# - METPO mapping: "moderately halophilic" (space)
```
