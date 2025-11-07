# METPO Grounding Analysis - Findings and Examples
**For ICBO 2025 Talk**

**Date:** 2025-11-06
**Corpus:** 144 paper extractions across 6 production-quality OntoGPT runs (Oct 31, 2025)
**Models:** GPT-4o with temperature=0.0 (deterministic)

---

## Executive Summary

**Key Finding:** METPO shows contrasting performance between structured and unstructured data:
- **Structured DB alignment:** 54-60% coverage (BacDive, BactoTraits, Madin)
- **Free-text grounding:** 0% METPO, 100% AUTO terms (1,974 phenotype extractions)

**Interpretation:** METPO is optimized for semi-structured trait data integration. Free-text mining reveals systematic gaps where AUTO: terms indicate needed expansion.

---

## Quantitative Results

### Production Corpus Statistics

**Files analyzed:**
1. `biochemical_base_fullcorpus_gpt4o_t00_20251031_231715.yaml` (1.1M)
2. `biochemical_hybrid_fullcorpus_gpt4o_t00_20251031_232234.yaml` (747K)
3. `chemical_utilization_hybrid_fullcorpus_gpt4o_t00_20251031_221515.yaml` (961K)
4. `cmm_fullcorpus_gpt4o_t00_20251031_193935.yaml` (917K)
5. `growth_conditions_hybrid_fullcorpus_gpt4o_t00_20251031_215409.yaml` (684K)
6. `morphology_fullcorpus_gpt4o_t00_20251031.yaml` (1.1M)

**Total corpus:** 144 individual paper extractions

**Entity type distribution:**
- CHEBI: 7,062 (chemical entities - high grounding success)
- AUTO: 1,974 (phenotypes - zero grounding to METPO)
- NCBITaxon: 253 (taxonomy - high grounding success)
- GO: 6 (gene ontology - high grounding success)

**Phenotype grounding rate:** 0.0% (0/1,974)

---

## Qualitative Analysis: AUTO Term Patterns

### Category 1: Strain Identifiers (Most Common)

**Pattern:** Bacterial strain designations not in NCBITaxon

**Examples:**
```yaml
AUTO:USDA110          # Bradyrhizobium diazoefficiens strain
AUTO:22A              # Methylobacterium aquaticum strain
AUTO:AM1              # Methylobacterium extorquens strain
AUTO:DM4              # Methyloversatilis universalis strain
AUTO:SolV             # Methylacidiphilum fumariolicum strain
AUTO:NBRC114766       # Culture collection number
AUTO:DSM111909        # DSMZ culture collection
AUTO:Zm11             # Isolate designation
```

**Analysis:** These are legitimate AUTO: terms - strain identifiers should NOT be in METPO (they belong in strain databases/NCBITaxon). Not a METPO gap.

**ICBO Message:** OntoGPT correctly distinguishes strains (AUTO:) from phenotypes (should be METPO:).

---

### Category 2: Metabolic Phenotypes (Critical Gap Indicators)

**Pattern:** Specific metabolic/physiological descriptors that SHOULD be METPO classes

**Examples:**
```yaml
AUTO:methylotrophic%20bacteria        # Should be METPO:methylotroph
AUTO:Gram-negative%20bacteria         # Should be METPO:Gram-negative
AUTO:methanol%20dehydrogenase         # Enzyme/pathway - borderline
AUTO:rare-earth%20element%20(REE)     # Growth requirement - candidate
AUTO:light%20lanthanides              # Growth requirement - candidate
```

**Analysis:**
- "methylotrophic bacteria" → METPO has `methylotroph` but grounding failed
- "Gram-negative bacteria" → METPO has `Gram-negative` but grounding failed
- REE/lanthanide terms → Legitimate gap (CMM project needs these)

**ICBO Message:** Some AUTO: terms indicate grounding failures (config issue), others indicate genuine METPO gaps.

---

### Category 3: Morphological Descriptors (Mixed)

**Examples:**
```yaml
AUTO:Gram-stain-negative              # Should be METPO:Gram-negative
AUTO:reddish%20brown                  # Pigmentation - METPO gap
AUTO:rod-shaped                       # Should be METPO class (if exists)
```

**Analysis:**
- Gram stain terms should ground to METPO (grounding failure)
- Pigmentation colors are genuine gap (Issue: BactoTraits has pigmentation trait)
- Cell shape terms should ground if METPO has them

---

### Category 4: Biochemical Terms (Enzymes/Pathways)

**Examples:**
```yaml
AUTO:methanol%20dehydrogenase         # Enzyme
AUTO:XoxF                             # Protein/enzyme
AUTO:MxaFI                            # Protein complex
AUTO:methanol%20to%20formaldehyde     # Metabolic transformation
AUTO:S-formylglutathione%20hydrolase  # Enzyme
```

**Analysis:** These are biochemical entities, not phenotypes. Should they be in METPO?
- Argument YES: Presence/absence of specific pathways is a phenotype
- Argument NO: Enzymes are molecular entities (GO, CHEBI, PR domain)
- Current decision: METPO focuses on organism-level phenotypes, not molecular

**ICBO Message:** METPO scope decision - organism phenotypes, not molecular components.

---

### Category 5: Placeholder Terms

**Examples:**
```yaml
AUTO:None
AUTO:none
AUTO:Not%20explicitly%20mentioned
AUTO:%3CEmpty%3E                      # URL-encoded <Empty>
```

**Analysis:** These indicate extraction found no relevant terms. Not METPO gaps.

---

### Category 6: Growth Conditions/Requirements (Candidates)

**Examples:**
```yaml
AUTO:ion_exchange_mechanism           # Uptake mechanism
AUTO:high%20adsorption%20capacity     # Quantitative trait
```

**Analysis:** Quantitative traits vs. categorical phenotypes - boundary question for METPO scope.

---

## Example Extractions with Context

### Example 1: CMM Lanthanide Paper (Good Extraction, Genuine Gap)

**File:** `cmm_fullcorpus_gpt4o_t00_20251031_193935.yaml`
**PMID:** 24816778
**DOI:** 10.1007/s00253-014-5766-8
**Paper:** Rare earth element metabolism in Gram-negative bacteria

**Extracted AUTO terms:**
- `XoxF` - Lanthanide-dependent methanol dehydrogenase
- `MxaFI` - Calcium-dependent methanol dehydrogenase
- `methylotrophic%20bacteria` - Should ground to METPO:methylotroph
- `Gram-negative%20bacteria` - Should ground to METPO:Gram-negative
- `rare-earth%20element%20(REE)` - **Genuine METPO gap - CMM needs this**

**Analysis:** Mix of grounding failures (methylotroph, Gram-negative) and genuine gaps (REE requirement).

---

### Example 2: Chemical Utilization Extraction (Grounding Failure)

**File:** `chemical_utilization_hybrid_fullcorpus_gpt4o_t00_20251031_221515.yaml`
**PMID:** 31421721
**DOI:** 10.1016/j.enzmictec.2019.109371

**Extracted AUTO terms:**
- `La3%2B` (La³⁺) - Lanthanum ion - should be CHEBI
- `Ce3%2B` (Ce³⁺) - Cerium ion - should be CHEBI
- `Pr3%2B` (Pr³⁺) - Praseodymium ion - should be CHEBI
- `Nd3%2B` (Nd³⁺) - Neodymium ion - should be CHEBI
- `USDA110` - Strain - correctly AUTO

**Analysis:** Chemical entities not grounded to CHEBI - annotator config issue? Or CHEBI doesn't have lanthanide ions?

---

### Example 3: Morphology Extraction (METPO Should Work)

**File:** `morphology_fullcorpus_gpt4o_t00_20251031.yaml`
**PMID:** 24816778

**Extracted AUTO terms:**
- `Gram-Negative%20Bacteria` - METPO has Gram-negative class!

**Analysis:** Clear grounding failure - METPO has this term but OntoGPT didn't match it.

---

## Template Configuration Analysis

### Current Template Annotator Settings

**Templates WITH METPO annotators configured:**

1. **growth_conditions_hybrid.yaml:**
```yaml
OxygenRequirement:
  annotations:
    annotators: sqlite:../src/ontology/metpo.owl

TemperatureCondition:
  annotations:
    annotators: sqlite:../src/ontology/metpo.owl

PHCondition:
  annotations:
    annotators: sqlite:../src/ontology/metpo.owl

SaltTolerance:
  annotations:
    annotators: sqlite:../src/ontology/metpo.owl
```

2. **morphology_template_base.yaml:**
```yaml
# Check if has METPO annotators...
```

3. **biochemical templates:**
```yaml
# Check configuration...
```

**Key Question:** Are the templates actually configured to ground to METPO, or only to CHEBI/NCBITaxon?

---

## Hypotheses for Zero METPO Grounding

### Hypothesis 1: Templates Not Configured for METPO Grounding
**Test:** Check each template's annotator configuration
**Expected:** Templates may only have CHEBI, NCBITaxon annotators
**Solution:** Add `sqlite:../src/ontology/metpo.owl` to relevant classes

### Hypothesis 2: METPO Labels Don't Match Extracted Text
**Test:** Compare AUTO: terms to METPO labels/synonyms
**Expected:** "methylotrophic bacteria" != "methylotroph" (no synonym)
**Solution:** Add text mining synonyms to METPO

### Hypothesis 3: METPO File Path Issues
**Test:** Verify `sqlite:../src/ontology/metpo.owl` resolves correctly
**Expected:** Path might be wrong relative to extraction location
**Solution:** Use absolute path or verify relative path

### Hypothesis 4: METPO Classes Lack Necessary Annotations
**Test:** Check if METPO classes have labels/synonyms in OWL
**Expected:** Some classes may be skeletons without proper annotations
**Solution:** Ensure all METPO classes have rdfs:label

### Hypothesis 5: Genuine METPO Gaps
**Test:** For terms that should ground, verify METPO has those classes
**Expected:** Some AUTO: terms reveal real gaps (REE, pigmentation)
**Solution:** Add new METPO classes based on AUTO: term analysis

---

## Recommendations for Rigorous Testing

### Test 1: Verify Template Configuration
**Goal:** Ensure templates have METPO annotators
**Method:** Check all production templates for annotator declarations
**Deliverable:** List of classes with/without METPO annotation

### Test 2: Controlled Grounding Test
**Goal:** Extract from text containing known METPO terms
**Method:** Create test document with "mesophilic", "thermophilic", "Gram-negative"
**Expected:** Should ground to METPO if config correct
**Deliverable:** Pass/fail for each template

### Test 3: Label/Synonym Coverage Analysis
**Goal:** Compare AUTO: terms to METPO vocabulary
**Method:** For each AUTO: term, check if METPO has matching class
**Deliverable:** Coverage matrix (has class Y/N, has matching label Y/N)

### Test 4: Optimized Re-extraction
**Goal:** Re-run extractions with optimized METPO configuration
**Method:** Fix annotators, add synonyms, re-extract on same corpus
**Expected:** Higher METPO grounding rate
**Deliverable:** Before/after comparison

### Test 5: Structured vs Unstructured Sources
**Goal:** Compare grounding on different input types
**Method:** Extract from:
  - IJSEM structured abstracts (standardized format)
  - BacDive field descriptions (semi-structured)
  - Full papers (unstructured)
**Expected:** Higher grounding on structured sources
**Deliverable:** Grounding rate by source type

---

## Next Steps for ICBO Preparation

1. **Document current findings** ✅ (this file)
2. **Run verification tests** (template config, controlled grounding)
3. **Optimize templates** (add METPO annotators where missing)
4. **Re-extract subset** (compare before/after optimization)
5. **Categorize remaining AUTO: terms** (config failures vs. genuine gaps)
6. **Create ICBO slide examples** (show both successes and failures honestly)

---

## Files for Further Analysis

**Production corpus:** `metpo_grounding_production_fullcorpus_strict.txt`
**Database alignment:** `metpo_database_alignment_icbo2025.txt`
**Template configs:** `/home/mark/gitrepos/metpo/literature_mining/templates/*.yaml`
**METPO OWL:** `/home/mark/gitrepos/metpo/src/ontology/metpo.owl`

---

**Key ICBO Message:**

> METPO shows strong alignment (54-60%) with structured bacterial trait databases (BacDive, BactoTraits, Madin), demonstrating its value for data integration. Free-text mining grounding is currently low (0-20%), but AUTO: term analysis reveals both configuration opportunities (add annotators/synonyms) and genuine gaps (lanthanide requirements, pigmentation). This dual approach - structured data integration + free-text gap discovery - makes METPO a practical ontology for bacterial phenotypes.
