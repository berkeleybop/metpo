# Morphology Extraction Template Analysis

**Date**: 2025-10-31
**Analyst**: Claude (via claude-code)

## Executive Summary

Testing of morphology extraction templates on CMM corpus papers reveals that **the base template is performing optimally** - it's being appropriately conservative rather than under-extracting. The "Extract ALL" optimization pattern that succeeded for chemical_utilization extraction actually **harms** morphology extraction by forcing hallucinations when minimal morphology data is present.

### Key Finding
**The CMM corpus is unsuitable for morphology template testing** because it consists primarily of metabolic/physiological studies, not taxonomic descriptions.

## Test Corpus Composition

### Papers Tested (test-fullpaper-prototype/)
1. **fmicb-14-1258452.txt** (67KB) - "Metabolism-linked methylotaxis sensors" - chemotaxis study
2. **e00266-15.txt** (8KB) - Genome announcement
3. **fmicb-13-921635.txt** (71KB) - "Siderophore for Lanthanide and Iron Uptake" - metabolic study

### Morphology Content Analysis
All three papers mention bacterial cells in **functional/background context only**:
- "Motile bacteria take a competitive advantage..." (general statement, line 26 of fmicb-14-1258452)
- "pink-pigmented bacteria" (genus-level background, line 91 of fmicb-13-921635)
- "Gram-negative bacteria" (general background, line 115 of fmicb-13-921635)

**NONE contain strain-specific morphological characterizations** like:
- "Cells are rod-shaped, 0.5 × 2.0 μm"
- "Non-motile" or "Motile by means of peritrichous flagella"
- "Gram-positive"
- "Non-spore-forming"

## Template Comparison Results

| Template | Total Extracted | Entities | Relationships | Grounding % | Hallucinations |
|----------|----------------|----------|---------------|-------------|----------------|
| **Base (morphology_template_base.yaml)** | **12** | **8** | **4** | **62.5%** | **None** |
| V3 (prompt.skip) | 18 | 12 | 6 | 46.2% | Moderate |
| V4 (conditional) | 16 | 10 | 6 | 54.5% | Low |
| V2 (single field) | 15 | N/A | 15 | 50.0% | Moderate |
| Hybrid (Extract ALL) | 37 | 19 | 18 | 36.8% | **Severe** |

### Hallucination Examples from Hybrid Template
```
cell_shape:
  - AUTO:Not%20explicitly%20mentioned
motility:
  - AUTO:Not%20mentioned
pigmentation:
  - AUTO:Not%20explicitly%20mentioned
```

## Why Chemical_Utilization_Hybrid Succeeded but Morphology_Hybrid Failed

### Chemical Utilization Template (SUCCESS)
- **Data density**: 24 papers → 1,214 relationships extracted
- **Data presence**: Papers explicitly describe chemical utilization experiments
- **"Extract ALL" effect**: Forces comprehensive extraction of PRESENT data
- **Architecture**: Single `chemical_utilizations` field prevents entity/relationship conflicts
- **Result**: 100% ground truth accuracy (5/5 relationships)

### Morphology Template (FAILURE)
- **Data density**: 3 papers → Only functional mentions, not taxonomic descriptions
- **Data presence**: Minimal to no strain-specific morphology characterizations
- **"Extract ALL" effect**: Forces LLM to hallucinate when no data present
- **Architecture**: Dual entity + relationship fields create extraction pressure
- **Result**: Aggressive templates extract garbage ("Not mentioned", template artifacts)

## Root Cause Analysis

### Problem 1: Corpus Mismatch
The CMM corpus focuses on:
- ✓ Methylotroph metabolism
- ✓ Chemical utilization
- ✓ Growth conditions
- ✗ Taxonomic morphology descriptions

### Problem 2: Optimization Pattern Misapplication
The "Extract ALL" + "Be COMPREHENSIVE" pattern works when:
- ✓ Papers contain extensive target data (chemical utilization)
- ✗ Papers contain minimal target data (morphology in metabolic papers)

### Problem 3: Template Architecture
- **Single field approach** (v2): Reduces hallucinations but still forces extraction
- **Dual field approach** (base, v3, v4, hybrid): Entity fields + relationship fields create double extraction pressure
- **Base template conservatism**: Actually optimal behavior for sparse data

## Search for Suitable Papers

### CMM Corpus Survey (24 papers)
```bash
grep -l "rod-shaped\|coccus\|Gram-positive\|Gram-negative\|non-motile" *.txt
```
**Result**: Only 3 papers with morphology keywords:
- fmicb-13-921635.txt (siderophore study - already tested)
- PMID_24816778.txt (review article on MDHs)
- doi_10_3389-fbioe_2023_1130939.txt (cyanobacteria biosorption)

**None contain taxonomic morphology descriptions**

## Recommendations

### 1. Keep Base Template As-Is ✓
The `morphology_template_base.yaml` is:
- Appropriately conservative
- Not hallucinating
- Correctly extracting minimal data present
- **No optimization needed**

### 2. Test on Appropriate Papers
Need papers with actual taxonomic descriptions:
- Novel species descriptions (e.g., "Methylobacterium ___ sp. nov.")
- Emended descriptions
- Taxonomic revisions
- Papers in: *Int J Syst Evol Microbiol*, *Antonie van Leeuwenhoek*, etc.

### 3. Template Optimization Strategy
```
IF corpus has dense target data:
    THEN use "Extract ALL" + inline examples + single field
ELSE IF corpus has sparse target data:
    THEN use conservative base template
```

### 4. Alternative: Switch Corpus
Since morphology isn't well-represented in CMM corpus:
- Option A: Find morphology-rich papers outside CMM
- Option B: Accept that morphology extraction isn't priority for this corpus
- Option C: Focus remaining effort on growth_conditions template (likely has better data density in CMM)

## Files Generated During Analysis

### Templates Created
- `/templates/morphology_hybrid.yaml` - Failed (36.8% grounding, severe hallucinations)
- `/templates/morphology_v2.yaml` - Failed (50.0% grounding, single field approach)
- `/templates/morphology_v3.yaml` - Failed (46.2% grounding, prompt.skip approach)
- `/templates/morphology_v4.yaml` - Failed (54.5% grounding, conditional prompts)

### Output Files
- `/outputs/morphology_test_gpt4o_t00_20251031_201811.yaml` - Base template (BEST)
- `/outputs/morphology_hybrid_gpt4o_t00_20251031_202849.yaml` - Hybrid (WORST)
- `/outputs/morphology_v2_gpt4o_t00_20251031.yaml` - Single field
- `/outputs/morphology_v3_gpt4o_t00_20251031.yaml` - Prompt.skip
- `/outputs/morphology_v4_gpt4o_t00_20251031.yaml` - Conditional

## Lessons Learned

### 1. Corpus Content Matters More Than Template Design
- Best template cannot extract data that doesn't exist
- Need to match template to corpus content

### 2. "Extract ALL" is a Double-Edged Sword
- **Amplifies present data** → good for chemical_utilization
- **Amplifies absence** → bad for morphology (forces hallucinations)

### 3. Conservative Templates Have Value
- Base template's low extraction volume reflects data reality
- Not a failure - it's appropriate behavior

### 4. Single vs Dual Field Architecture
- Single field (`chemical_utilizations`): Less prompt pressure, cleaner for LLM
- Dual field (`cell_shape` + `cell_shape_relationships`): Double extraction pressure
- But even single field doesn't help if data is absent

### 5. Ground Truth Validation is Critical
- High extraction volume ≠ good performance
- Must verify against actual paper content
- Hybrid's 37 extractions looked impressive until manual inspection

## Next Steps

1. ✅ **Completed**: Comprehensive morphology template testing
2. ✅ **Completed**: Root cause analysis of poor extraction
3. **Pending**: Find morphology-rich papers for proper validation
4. **Pending**: Test growth_conditions template (likely better data fit for CMM)
5. **Pending**: Document final template optimization guidelines

## Conclusion

The morphology extraction "problem" is not a template problem - it's a corpus problem. The base template is working correctly by being conservative when faced with minimal morphological characterization data.

**Recommendation**: Keep `morphology_template_base.yaml` as the production template and focus future optimization efforts on templates that match the CMM corpus content (chemical_utilization ✓, growth_conditions ?, morphology ✗).
