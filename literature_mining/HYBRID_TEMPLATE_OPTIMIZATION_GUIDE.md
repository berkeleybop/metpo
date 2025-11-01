# Hybrid Template Optimization Guide

## Overview

This document describes the optimizations discovered through chemical_utilization template testing that should be applied to growth_conditions and morphology templates to create "hybrid" versions.

## Key Optimizations Discovered

### 1. Inline Examples with `exclude` Annotation

**What worked:**
```yaml
annotations:
  prompt: >-
    Extract ALL relationships. Examples:
    22A uses_for_growth methanol; MG1655 synthesizes cobalamin
  exclude: 22A, MG1655, methanol, cobalamin
```

**What FAILED:**
- Using `prompt.examples` annotation (causes those entities to be excluded from extraction)
- Not using `exclude` (causes example entities to appear in output)

### 2. Explicit Comprehensiveness Instructions

**Add to ALL relationship extraction prompts:**
- "Extract ALL..." at the beginning
- "Be COMPREHENSIVE - do not omit relationships"
- "Extract BOTH positive AND negative information"
- "Be thorough and capture all relationships described in the text"

### 3. Diverse Examples by Category

**Show 2-3 examples per major category:**
- Cover different relationship types
- Include both positive and negative examples
- Keep total examples to 5-8 maximum
- Avoid redundant examples

### 4. Model & Temperature Selection

**Production settings:**
- Model: `gpt-4o` (NOT Claude Sonnet - poor performance)
- Temperature: `0.0` (maximum recall without precision loss)
- Test on 3-5 papers before full corpus run

## Specific Changes for Growth Conditions Template

### File: `templates/growth_conditions_hybrid.yaml`

#### Change 1: growth_condition_relationships field

**Current (base template):**
```yaml
prompt: >-
  Extract specific organism-growth condition relationships ONLY when explicitly stated in the text.
  Link the specific organism to its growth parameters.
  Format: "organism_name relationship_type condition_value"
  Examples: "Bacillus vietnamensis optimal_growth_temperature 28°C",
  "Geobacter species requires_oxygen_level strictly anaerobic",
  "Streptomyces strain grows_at_pH 6.5-8.0".
  Do NOT create relationships if no specific conditions are mentioned for that organism.
  If no relationships can be determined, write 'none'.
```

**NEW (hybrid template):**
```yaml
prompt: >-
  Extract ALL organism-growth condition relationships mentioned in the text. Be COMPREHENSIVE - do not omit relationships.

  Include ALL condition types:
  TEMPERATURE: Bacillus optimal_growth_temperature 28°C; Geobacter grows_at_temperature 15-45°C
  OXYGEN: Geobacter requires_oxygen_level anaerobic; Pseudomonas grows_aerobically
  pH: Streptomyces grows_at_pH 6.5-8.0; Lactobacillus optimal_pH 5.5
  SALINITY: Halomonas grows_at_salinity 3% NaCl; Bacillus tolerates_salinity 0-10% NaCl
  NEGATIVE: Psychrobacter does_not_grow_at_temperature 45°C; Bacillus does_not_grow_anaerobically

  Extract BOTH positive conditions (CAN grow) AND negative conditions (CANNOT grow). Be thorough.
exclude: Bacillus, Geobacter, Streptomyces, Lactobacillus, Halomonas, Pseudomonas, Psychrobacter, 28°C, 15-45°C, 6.5-8.0, 5.5, 3% NaCl, 0-10% NaCl, 45°C
```

**Key changes:**
- Added "Extract ALL" and "Be COMPREHENSIVE"
- Organized examples by category (TEMPERATURE, OXYGEN, pH, SALINITY, NEGATIVE)
- Added `exclude` annotation
- Removed "ONLY when explicitly stated" (too restrictive)
- Removed "write 'none'" instruction
- Added negative examples (does_not_grow)

#### Change 2: Add comprehensiveness to culture_medium_relationships

**Add to prompt:**
```yaml
prompt: >-
  Extract ALL strain-culture medium relationships mentioned in the text. Be COMPREHENSIVE.

  Examples: strain_15-1T grows_on TSB; ATCC_25922 requires Marine_Broth_2216;
  isolate_XYZ uses_medium glucose_minimal_medium
exclude: strain_15-1T, ATCC_25922, isolate_XYZ, TSB, Marine_Broth_2216, glucose_minimal_medium
```

## Specific Changes for Morphology Template

### File: `templates/morphology_hybrid.yaml`

#### Change 1: cell_shape_relationships field

**Current:**
```yaml
prompt: >-
  For each cell shape extracted above, create strain-to-shape relationships.
  Link specific strains to their cell shapes (e.g., "DA-C8 has_cell_shape rod-shaped").
  Convert ALL cell shapes mentioned above into structured relationships.
```

**NEW:**
```yaml
prompt: >-
  Extract ALL strain-cell shape relationships mentioned in the text. Be COMPREHENSIVE - do not omit any morphological features.

  Examples: Strain22A has_cell_shape rod; E_coli has_cell_shape rod-shaped_0.5x2.0um;
  Staphylococcus has_cell_shape coccus; Spirillum has_cell_shape spiral
exclude: Strain22A, E_coli, Staphylococcus, Spirillum, rod, coccus, spiral, rod-shaped_0.5x2.0um
```

#### Change 2: motility_relationships field

**NEW:**
```yaml
prompt: >-
  Extract ALL strain-motility relationships mentioned in the text. Be COMPREHENSIVE.

  Include ALL motility information:
  PRESENCE: E_coli has_motility motile; Klebsiella has_motility non-motile
  TYPE: Pseudomonas has_motility_type flagellar; Myxococcus has_motility_type gliding
  FLAGELLA: Vibrio has_flagella_arrangement polar; E_coli has_flagella_arrangement peritrichous
  NEGATIVE: Shigella does_not_have_motility; Klebsiella lacks_flagella

  Extract BOTH presence AND absence of motility features.
exclude: E_coli, Klebsiella, Pseudomonas, Myxococcus, Vibrio, Shigella, motile, non-motile, flagellar, gliding, polar, peritrichous
```

#### Change 3: gram_staining_relationships field

**NEW:**
```yaml
prompt: >-
  Extract ALL strain-Gram staining relationships mentioned in the text. Be COMPREHENSIVE.

  Examples: Bacillus has_gram_staining Gram-positive; E_coli has_gram_staining Gram-negative;
  Gardnerella has_gram_staining Gram-variable
exclude: Bacillus, E_coli, Gardnerella, Gram-positive, Gram-negative, Gram-variable
```

## Enum Reconciliation Strategy

### The Problem

Some enums in hybrid templates may not be directly derivable from METPO ontology:
- `chemical_utilization_hybrid.yaml` has manually curated chemical interaction predicates
- These were added based on CTD/literature patterns
- They may not all exist in METPO yet

### Solution Approach

**Short term (current work):**
1. Keep hybrid templates as-is with manually curated enums
2. Document which predicates are custom vs METPO-derived
3. Use hybrid templates for production runs (they work!)

**Medium term (future reconciliation):**
1. Review all custom predicates used in extractions
2. Add missing predicates to METPO ontology proper
3. Re-generate enum using Makefile population technique
4. Validate that regenerated template produces same results

**Long term (maintenance):**
1. Establish process: add to METPO first, then regenerate templates
2. Keep hybrid templates as "validated working versions"
3. Periodically sync with METPO updates

### Documenting Custom Predicates

For each hybrid template, maintain a section noting custom values:

**chemical_utilization_hybrid.yaml:**
```yaml
# CUSTOM PREDICATES (not yet in METPO):
# - oxidizes
# - reduces
# - ferments
# - does_not_degrade
# - does_not_fix
#
# These were added based on CTD database and literature patterns.
# TODO: Add to METPO ontology and regenerate via Makefile
```

## Testing Protocol

### 1. Create Hybrid Template
1. Copy base template to `{name}_hybrid.yaml`
2. Apply optimizations from this guide
3. Add custom predicates if needed
4. Document any custom enums

### 2. Test on 3-Paper Set
```bash
uv run ontogpt -vv \
    --cache-db cache/ontogpt-cache.db \
    extract \
    --show-prompt \
    -m gpt-4o \
    -p 0.0 \
    -t templates/{template}_hybrid.yaml \
    -i test-fullpaper-prototype \
    -o outputs/{template}_hybrid_test_$(date +%Y%m%d_%H%M%S).yaml \
    2>&1 | tee logs/{template}_hybrid_test_$(date +%Y%m%d_%H%M%S).log
```

### 3. Validate Results
```bash
uv run python validate_extractions.py outputs/{template}_hybrid_test_*.yaml
```

### 4. Compare to Base Template
```bash
uv run python compare_extractions.py \
    outputs/{template}_base_*.yaml \
    outputs/{template}_hybrid_*.yaml
```

### 5. Manual Ground Truth Check
- Pick 1 paper you know well
- List 5 expected relationships
- Verify hybrid template extracts all 5

### 6. If Successful, Run Full Corpus
```bash
uv run ontogpt -vv \
    --cache-db cache/ontogpt-cache.db \
    extract \
    --show-prompt \
    -m gpt-4o \
    -p 0.0 \
    -t templates/{template}_hybrid.yaml \
    -i CMM-AI/publications-txt \
    -o outputs/{template}_fullcorpus_gpt4o_t00_$(date +%Y%m%d_%H%M%S).yaml \
    2>&1 | tee logs/{template}_fullcorpus_gpt4o_t00_$(date +%Y%m%d_%H%M%S).log
```

## Results from Chemical Utilization Optimization

### Test Results (3 papers):
| Template | Relationships | Ground Truth (e00266-15) | Grounding |
|----------|---------------|--------------------------|-----------|
| V1 baseline | 23 | 2/5 (40%) | 73% |
| Hybrid (GPT-4o t=0.1) | 22 | 5/5 (100%) | 80% |
| Hybrid (GPT-4o t=0.0) | 34 | 5/5 (100%) | 80% |

### Full Corpus Results (24 papers):
- **Total relationships:** 1,214
- **Avg per paper:** 50.6
- **Papers with relationships:** 12/24 (50%)
- **Ground truth:** 5/5 (100%) maintained
- **Grounding:** 60.3% (lower due to diversity of papers)

### Key Finding:
Temperature 0.0 with GPT-4o gives maximum recall (34 vs 22 relationships) while maintaining perfect ground truth accuracy.

## Priority Actions

1. ✅ Document optimizations (this file)
2. ⬜ Create `growth_conditions_hybrid.yaml` with optimizations
3. ⬜ Create `morphology_hybrid.yaml` with optimizations
4. ⬜ Test both on 3-paper set
5. ⬜ Run full corpus if tests pass
6. ⬜ Update SESSION_NOTES.md with complete findings

## References

- Chemical utilization hybrid template: `templates/chemical_utilization_hybrid.yaml`
- Validation script: `validate_extractions.py`
- Comparison script: `compare_extractions.py`
- Session notes: `SESSION_NOTES.md`
