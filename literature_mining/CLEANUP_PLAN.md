# Literature Mining Cleanup Plan
**Date**: 2025-10-31
**Status**: READY FOR REVIEW

## Summary
- **17 templates** → Keep 6 production templates
- **23 output files** → Archive 17 superseded outputs
- **6 documentation files** → Merge into 2 comprehensive docs
- **4 Python scripts** → Keep all (each serves unique purpose)

---

## 1. TEMPLATES TO KEEP (Production)

### Keep These 6 Templates:
```
templates/chemical_utilization_hybrid.yaml          ✅ PRODUCTION - 100% accuracy on abstracts
templates/growth_conditions_hybrid.yaml             ✅ PRODUCTION - Testing on full corpus now
templates/morphology_template_base.yaml             ✅ PRODUCTION - Conservative (appropriate for sparse data)
templates/biochemical_template_base.yaml            ✅ PRODUCTION - Unused but ready
templates/taxa_template_base.yaml                   ✅ PRODUCTION - Unused but ready
templates/growth_conditions_template_base.yaml      ✅ KEEP - Baseline for comparison
```

---

## 2. TEMPLATES TO DELETE (Superseded/Failed)

### Chemical Utilization (DELETE 6):
```bash
rm templates/chemical_utilization_template_base.yaml     # Superseded by hybrid
rm templates/chemical_utilization_ctd_style.yaml         # Failed experiment (37.5% grounding)
rm templates/chemical_utilization_populated.yaml         # Superseded by v3
rm templates/chemical_utilization_populated_enhanced.yaml # Superseded by hybrid
rm templates/chemical_utilization_populated_v2.yaml      # Superseded by v3
rm templates/chemical_utilization_populated_v3.yaml      # Superseded by hybrid
```

**Rationale**: `chemical_utilization_hybrid.yaml` achieved 100% accuracy and supersedes all prior versions.

### Morphology (DELETE 4):
```bash
rm templates/morphology_populated.yaml    # Early experiment
rm templates/morphology_hybrid.yaml       # FAILED - 36.8% grounding, severe hallucinations
rm templates/morphology_v2.yaml           # FAILED - 50.0% grounding
rm templates/morphology_v3.yaml           # FAILED - 46.2% grounding
rm templates/morphology_v4.yaml           # FAILED - 54.5% grounding
```

**Rationale**: Morphology analysis (MORPHOLOGY_EXTRACTION_ANALYSIS.md) proved base template is optimal for CMM corpus.

---

## 3. OUTPUT FILES TO ARCHIVE

### Create Archive Directory:
```bash
mkdir -p outputs/archive/superseded
mkdir -p outputs/archive/experiments
```

### Chemical Utilization - Archive Superseded (6 files):
```bash
mv outputs/fullpaper_prototype_chemical_20251031_151234.yaml outputs/archive/superseded/
mv outputs/fullpaper_prototype_chemical_ctd_20251031_182359.yaml outputs/archive/superseded/
mv outputs/fullpaper_prototype_chemical_enhanced_20251031_180125.yaml outputs/archive/superseded/
mv outputs/fullpaper_prototype_chemical_v2_20251031_160738.yaml outputs/archive/superseded/
mv outputs/fullpaper_prototype_chemical_v3_20251031_163102.yaml outputs/archive/superseded/
```

### Keep:
```
outputs/fullpaper_prototype_chemical_hybrid_20251031_184029.yaml  ✅ BEST - 100% accuracy
```

### Morphology - Archive Experiments (5 files):
```bash
mv outputs/morphology_gpt-4o_20251030_174301.yaml outputs/archive/experiments/
mv outputs/morphology_gpt-4o_20251030_180642.yaml outputs/archive/experiments/
mv outputs/morphology_hybrid_gpt4o_t00_20251031_202849.yaml outputs/archive/experiments/
mv outputs/morphology_v2_gpt4o_t00_20251031.yaml outputs/archive/experiments/
mv outputs/morphology_v3_gpt4o_t00_20251031.yaml outputs/archive/experiments/
mv outputs/morphology_v4_gpt4o_t00_20251031.yaml outputs/archive/experiments/
```

### Keep:
```
outputs/morphology_test_gpt4o_t00_20251031_201811.yaml        ✅ 3-paper test (base template)
outputs/morphology_fullcorpus_gpt4o_t00_20251031.yaml         ✅ Full 24-paper corpus (base template)
```

### Growth Conditions - Keep All (Currently Running):
```
outputs/growth_conditions_hybrid_gpt4o_t00_20251031_212526.yaml  ✅ 3-paper test v1
outputs/growth_conditions_hybrid_gpt4o_t00_20251031_213345.yaml  ✅ 3-paper test v2 (453 extractions)
outputs/growth_conditions_hybrid_fullcorpus_gpt4o_t00_*.yaml     ✅ RUNNING NOW
```

---

## 4. DOCUMENTATION TO MERGE

### Current State:
```
DEVELOPMENT_NOTES.md              - Session-specific notes (Oct 30)
SESSION_NOTES.md                  - Session-specific notes (Oct 31)
SESSION_REPORT.md                 - Old session report
MORPHOLOGY_EXTRACTION_ANALYSIS.md - Comprehensive analysis ✅ KEEP
SPAN_ASSESSMENT_ANALYSIS.md       - Span validation study ✅ KEEP
README.md                          - Main documentation ✅ KEEP
```

### Consolidation Plan:

#### Option A: Merge All Session Notes
Create `TEMPLATE_OPTIMIZATION_HISTORY.md` containing:
- All experimental iterations
- Decision rationale
- Failed approaches with explanations
- Success patterns

Then DELETE:
- DEVELOPMENT_NOTES.md
- SESSION_NOTES.md
- SESSION_REPORT.md

#### Option B: Keep Hierarchical Structure
- README.md → Main entry point
- MORPHOLOGY_EXTRACTION_ANALYSIS.md → Keep as-is
- SPAN_ASSESSMENT_ANALYSIS.md → Keep as-is
- Create CHEMICAL_UTILIZATION_ANALYSIS.md from session notes
- Create GROWTH_CONDITIONS_ANALYSIS.md (pending full corpus results)
- DELETE: DEVELOPMENT_NOTES.md, SESSION_NOTES.md, SESSION_REPORT.md

**RECOMMENDED: Option B** - Better for future reference and searching.

---

## 5. PYTHON SCRIPTS - KEEP ALL

All scripts serve distinct purposes:
```
analyze_extractions.py    ✅ Core analysis tool
compare_extractions.py    ✅ Template comparison
validate_extractions.py   ✅ Ground truth validation
metpo_assessor.py         ✅ Span assessment
```

---

## 6. CONTRADICTIONS TO RESOLVE

### Check for Contradictions in Documentation:

**SESSION_NOTES.md** might claim morphology hybrid is good → **CONTRADICTS** MORPHOLOGY_EXTRACTION_ANALYSIS.md showing it failed.

**Need to verify:**
1. Are there conflicting recommendations about which templates to use?
2. Are there outdated performance claims?
3. Are there conflicting explanations of why things failed/succeeded?

---

## 7. EXECUTION COMMANDS

### Phase 1: Create Archives
```bash
mkdir -p outputs/archive/superseded
mkdir -p outputs/archive/experiments
```

### Phase 2: Archive Outputs
```bash
# Chemical superseded
mv outputs/fullpaper_prototype_chemical_20251031_151234.yaml outputs/archive/superseded/
mv outputs/fullpaper_prototype_chemical_ctd_20251031_182359.yaml outputs/archive/superseded/
mv outputs/fullpaper_prototype_chemical_enhanced_20251031_180125.yaml outputs/archive/superseded/
mv outputs/fullpaper_prototype_chemical_v2_20251031_160738.yaml outputs/archive/superseded/
mv outputs/fullpaper_prototype_chemical_v3_20251031_163102.yaml outputs/archive/superseded/

# Morphology experiments
mv outputs/morphology_gpt-4o_20251030_174301.yaml outputs/archive/experiments/
mv outputs/morphology_gpt-4o_20251030_180642.yaml outputs/archive/experiments/
mv outputs/morphology_hybrid_gpt4o_t00_20251031_202849.yaml outputs/archive/experiments/
mv outputs/morphology_v2_gpt4o_t00_20251031.yaml outputs/archive/experiments/
mv outputs/morphology_v3_gpt4o_t00_20251031.yaml outputs/archive/experiments/
mv outputs/morphology_v4_gpt4o_t00_20251031.yaml outputs/archive/experiments/
```

### Phase 3: Archive Superseded Templates
```bash
mkdir -p templates/archive/chemical_experiments
mkdir -p templates/archive/morphology_experiments

# Chemical
mv templates/chemical_utilization_template_base.yaml templates/archive/chemical_experiments/
mv templates/chemical_utilization_ctd_style.yaml templates/archive/chemical_experiments/
mv templates/chemical_utilization_populated.yaml templates/archive/chemical_experiments/
mv templates/chemical_utilization_populated_enhanced.yaml templates/archive/chemical_experiments/
mv templates/chemical_utilization_populated_v2.yaml templates/archive/chemical_experiments/
mv templates/chemical_utilization_populated_v3.yaml templates/archive/chemical_experiments/

# Morphology
mv templates/morphology_populated.yaml templates/archive/morphology_experiments/
mv templates/morphology_hybrid.yaml templates/archive/morphology_experiments/
mv templates/morphology_v2.yaml templates/archive/morphology_experiments/
mv templates/morphology_v3.yaml templates/archive/morphology_experiments/
mv templates/morphology_v4.yaml templates/archive/morphology_experiments/
```

### Phase 4: Documentation (After Review)
```bash
# Will create:
# - CHEMICAL_UTILIZATION_ANALYSIS.md (extract from session notes)
# - GROWTH_CONDITIONS_ANALYSIS.md (after full corpus completes)
# - TEMPLATE_OPTIMIZATION_GUIDELINES.md (synthesis of all learnings)

# Will delete after extraction:
# - DEVELOPMENT_NOTES.md
# - SESSION_NOTES.md
# - SESSION_REPORT.md
```

---

## 8. FINAL PRODUCTION STRUCTURE

After cleanup:

```
literature_mining/
├── templates/
│   ├── chemical_utilization_hybrid.yaml           ✅ PRODUCTION
│   ├── growth_conditions_hybrid.yaml              ✅ PRODUCTION
│   ├── morphology_template_base.yaml              ✅ PRODUCTION
│   ├── biochemical_template_base.yaml             ✅ PRODUCTION
│   ├── taxa_template_base.yaml                    ✅ PRODUCTION
│   ├── growth_conditions_template_base.yaml       ✅ BASELINE
│   └── archive/                                   📦 Historical experiments
├── outputs/
│   ├── chemical_utilization_hybrid_*.yaml         ✅ Production outputs
│   ├── growth_conditions_hybrid_*.yaml            ✅ Production outputs
│   ├── morphology_*.yaml                          ✅ Production outputs
│   └── archive/                                   📦 Superseded/experiments
├── docs/
│   ├── README.md                                  📖 Main entry
│   ├── CHEMICAL_UTILIZATION_ANALYSIS.md          📖 Chemical template analysis
│   ├── GROWTH_CONDITIONS_ANALYSIS.md             📖 Growth conditions analysis
│   ├── MORPHOLOGY_EXTRACTION_ANALYSIS.md         📖 Morphology analysis
│   ├── SPAN_ASSESSMENT_ANALYSIS.md               📖 Span validation study
│   └── TEMPLATE_OPTIMIZATION_GUIDELINES.md       📖 Best practices synthesis
├── analyze_extractions.py                         🔧 Core analysis
├── compare_extractions.py                         🔧 Template comparison
├── validate_extractions.py                        🔧 Ground truth validation
└── metpo_assessor.py                             🔧 Span assessment
```

---

## Next Steps

1. **REVIEW THIS PLAN** - Confirm deletions are acceptable
2. **CHECK FOR CONTRADICTIONS** - Read session docs for conflicts
3. **EXECUTE PHASE 1-3** - Archive files (non-destructive)
4. **WAIT FOR GROWTH CONDITIONS** - Let full corpus extraction complete
5. **CREATE SYNTHESIS DOCS** - Extract key insights into new analysis docs
6. **EXECUTE PHASE 4** - Delete redundant session notes after extraction
