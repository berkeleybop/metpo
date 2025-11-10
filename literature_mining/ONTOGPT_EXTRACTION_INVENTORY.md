# OntoGPT Extraction Inventory - Complete Search Results

**Date:** 2025-11-06
**Purpose:** Comprehensive inventory of ALL OntoGPT extraction outputs across both computers
**Key Finding:** METPO terms use full URIs `<https://w3id.org/metpo/XXXXXXX>` NOT CURIEs `METPO:XXXXXXX`

---

## Search Methodology

### Initial Problem
- Searched for CURIE pattern: `METPO:`
- Found: 0 results
- This was INCORRECT - missed METPO terms entirely!

### Corrected Search
- Searched for URI pattern: `w3id.org/metpo/`
- Found: **83 METPO URIs on Ubuntu, 89 on Mac**
- This is the CORRECT count!

### Why the Confusion?
OntoGPT can output entity IDs in two formats:
1. **CURIE format**: `METPO:1000681` (namespace:id)
2. **URI format**: `<https://w3id.org/metpo/1000681>` (full URL)

The METPO terms in these extractions used URI format, while other ontologies (CHEBI, NCBITaxon) used CURIE format.

---

## Directory Structure

### Ubuntu: `/home/mark/gitrepos/metpo/literature_mining/`

**Main output directory:**
```
literature_mining/outputs/
├── *.yaml (17 files)
└── archive/
    ├── experiments/ (6 files)
    └── superseded/ (5 files)
```

**Other directories with YAML files:**
```
bacdive_chemical_utilization/
├── pmid.21602360.enhanced.output.yaml
├── bacdive_utilization_template.yaml
└── bacdive_utilizations_template_legacy.yaml

literature_mining/assessments/
├── extraction_analysis_20250818_155642.yaml
├── extraction_analysis_20250818_155959.yaml
├── extraction_analysis_20250818_161301.yaml
├── extraction_analysis_20250818_161411.yaml
└── extraction_analysis_yaml.yaml
```

### Mac: `/Users/MAM/Documents/gitrepos/metpo/literature_mining/`

**Additional file on Mac only:**
```
outputs/growth_conditions_20251101_132923.yaml
```

---

## METPO Term Counts by File (Ubuntu)

### Files with METPO URIs

**Note:** Searching for `w3id.org/metpo/`

```bash
# Command used:
find literature_mining/outputs -name "*.yaml" -exec sh -c 'count=$(grep -c "w3id.org/metpo/" "{}"); if [ "$count" -gt 0 ]; then echo "{}: $count"; fi' \;
```

**Results:**

```
Total METPO URIs found: 83
Distribution to be documented below...
```

### Files WITHOUT METPO URIs (AUTO: terms only)

**Production corpus (Oct 31, fullcorpus):**
- biochemical_base_fullcorpus_gpt4o_t00_20251031_231715.yaml: 0 METPO
- biochemical_hybrid_fullcorpus_gpt4o_t00_20251031_232234.yaml: 0 METPO
- chemical_utilization_hybrid_fullcorpus_gpt4o_t00_20251031_221515.yaml: 0 METPO
- cmm_fullcorpus_gpt4o_t00_20251031_193935.yaml: 0 METPO
- growth_conditions_hybrid_fullcorpus_gpt4o_t00_20251031_215409.yaml: 0 METPO
- morphology_fullcorpus_gpt4o_t00_20251031.yaml: 0 METPO

**Why no METPO?** These extractions returned empty `extracted_object: {}` for most documents.

---

## Term Format Examples

### METPO Terms (URI format)
```yaml
named_entities:
  - id: <https://w3id.org/metpo/1000681>
    label: rod-shaped
  - id: <https://w3id.org/metpo/1000702>
    label: Gram-negative
  - id: <https://w3id.org/metpo/1000703>
    label: motile
```

### CHEBI Terms (CURIE format)
```yaml
named_entities:
  - id: CHEBI:17439
    label: cysteine
  - id: CHEBI:15841
    label: polypeptide
```

### NCBITaxon Terms (CURIE format)
```yaml
named_entities:
  - id: NCBITaxon:1355477
    label: Bradyrhizobium diazoefficiens
```

### AUTO Terms (CURIE-like format)
```yaml
named_entities:
  - id: AUTO:USDA110
    label: USDA110
  - id: AUTO:methylotrophic%20bacteria
    label: methylotrophic bacteria
```

---

## Files with METPO Grounding - Detailed Inventory

### morphology_gpt-4o_20251030_180642.yaml

**METPO Classes Found:**
```yaml
- METPO:1000681 - rod-shaped (cell shape)
- METPO:1000702 - Gram-negative (gram stain)
- METPO:1000703 - motile (motility)
```

**Example extraction:**
```yaml
cell_shapes:
  - <https://w3id.org/metpo/1000681>
gram_stains:
  - <https://w3id.org/metpo/1000702>
motility_types:
  - <https://w3id.org/metpo/1000703>
```

**Template used:** morphology_template_base.yaml or morphology experiments

---

## Comparison: CURIE vs URI Format

### Search Patterns

**Incorrect search (misses URI format):**
```bash
grep "METPO:" file.yaml  # Found: 0
```

**Correct search (finds URI format):**
```bash
grep "w3id.org/metpo/" file.yaml  # Found: 83
```

**Comprehensive search (both formats):**
```bash
grep -E "(METPO:|w3id\.org/metpo/)" file.yaml
```

---

## Raw Data: All YAML Files Found

### Ubuntu - literature_mining/outputs/

```
biochemical_base_fullcorpus_gpt4o_t00_20251031_231715.yaml
biochemical_hybrid_fullcorpus_gpt4o_t00_20251031_232234.yaml
chemical_utilization_anthropic_claude-sonnet_20251031_190413.yaml
chemical_utilization_gpt-4o_20251030_162000.yaml
chemical_utilization_hybrid_fullcorpus_gpt4o_t00_20251031_221515.yaml
cmm_fullcorpus_gpt4o_t00_20251031_193935.yaml
fullpaper_hybrid_gpt4o_t00.yaml
fullpaper_hybrid_gpt4o_t03.yaml
fullpaper_prototype_chemical_hybrid_20251031_184029.yaml
growth_conditions_gpt-4o_20251030_142703.yaml
growth_conditions_hybrid_fullcorpus_gpt4o_t00_20251031_215409.yaml
growth_conditions_hybrid_gpt4o_t00_20251031_212526.yaml
growth_conditions_hybrid_gpt4o_t00_20251031_213345.yaml
morphology_fullcorpus_gpt4o_t00_20251031.yaml
morphology_gpt-4o_20251030_174301.yaml
morphology_gpt-4o_20251030_180642.yaml  ← HAS METPO!
morphology_test_gpt4o_t00_20251031_201811.yaml
```

### Ubuntu - literature_mining/outputs/archive/experiments/

```
morphology_gpt-4o_20251030_174301.yaml
morphology_gpt-4o_20251030_180642.yaml
morphology_hybrid_gpt4o_t00_20251031_202849.yaml
morphology_v2_gpt4o_t00_20251031.yaml
morphology_v3_gpt4o_t00_20251031.yaml
morphology_v4_gpt4o_t00_20251031.yaml
```

### Ubuntu - literature_mining/outputs/archive/superseded/

```
fullpaper_prototype_chemical_20251031_151234.yaml
fullpaper_prototype_chemical_ctd_20251031_182359.yaml
fullpaper_prototype_chemical_enhanced_20251031_180125.yaml
fullpaper_prototype_chemical_v2_20251031_160738.yaml
fullpaper_prototype_chemical_v3_20251031_163102.yaml
```

---

## Next Steps for Analysis

1. **Count METPO terms by file** - which files have the most METPO grounding?
2. **Extract METPO class distribution** - which METPO classes appear most?
3. **Compare with AUTO: terms** - same files or different?
4. **Template correlation** - which templates produce METPO URIs vs CURIEs?
5. **Update grounding analysis scripts** - search for both patterns

---

## Lessons Learned

### Critical Mistake
**Assumed:** OntoGPT outputs use consistent ID format (CURIEs)
**Reality:** OntoGPT can output URIs or CURIEs depending on configuration

### Why This Matters for ICBO
- Original analysis claimed 0% METPO grounding
- Actual METPO grounding is >0% (83 URIs found)
- Need to reanalyze with correct search pattern
- This shows importance of checking assumptions!

### Search Best Practices
```bash
# DON'T assume format
grep "METPO:" file.yaml

# DO search for both patterns
grep -E "(METPO:|w3id\.org/metpo/)" file.yaml

# BETTER: extract and normalize all IDs
python extract_all_entity_ids.py file.yaml
```

---

## Files for Reference

**This inventory:** `ONTOGPT_EXTRACTION_INVENTORY.md`
**Previous (incorrect) analysis:** `metpo_grounding_production_fullcorpus_strict.txt`
**Analysis scripts:** `analyze_metpo_grounding_filtered.py` (needs updating!)

---

**Status:** Inventory in progress - need to count METPO by file
**Next:** Detailed analysis of files containing METPO URIs
