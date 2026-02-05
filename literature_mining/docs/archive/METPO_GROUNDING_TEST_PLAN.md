# METPO Grounding Optimization - Test Plan
**For ICBO 2025 - Rigorous Evaluation**

**Date:** 2025-11-06
**Goal:** Maximize METPO grounding in OntoGPT extractions and identify genuine gaps

---

## Current State Analysis

### Template Annotator Configuration Audit

**Templates WITH METPO annotators:**

1. **growth_conditions_hybrid.yaml** ✅
   - Uses: `sqlite:../src/ontology/metpo.owl` (local file)
   - Classes annotated: OxygenRequirement, TemperatureCondition, PHCondition, SaltTolerance, AtmosphericRequirement

2. **growth_conditions_template_base.yaml** ✅
   - Uses: `sqlite:../src/ontology/metpo.owl` (local file)
   - Same configuration as hybrid version

3. **morphology_template_base.yaml** ⚠️
   - Uses: `sqlite:obo:metpo` (OBO Library version - **potentially outdated!**)
   - Classes annotated: CellShape, Motility, Endospore, GramStain, CellWall, CellSurface, CellArrangement, CellularInclusion

**Templates WITHOUT METPO annotators:** ❌

4. **biochemical_hybrid.yaml**
   - Annotators: NCBITaxon, GO, RHEA, CHEBI
   - **Missing METPO for metabolic phenotypes!**

5. **biochemical_template_base.yaml**
   - Annotators: NCBITaxon, GO, RHEA, CHEBI
   - **Missing METPO!**

6. **chemical_utilization_hybrid.yaml**
   - Annotators: NCBITaxon, CHEBI
   - **Missing METPO for nutritional phenotypes!**

7. **taxa_template_base.yaml**
   - Annotators: NCBITaxon only
   - **Not relevant for phenotypes**

---

## Problem Identified: Two METPO Paths

### Path 1: Local File (RECOMMENDED)
```yaml
annotators: sqlite:../src/ontology/metpo.owl
```
- **Pros:** Always uses latest METPO development version
- **Cons:** Requires correct relative path
- **Used by:** growth_conditions templates

### Path 2: OBO Library (RISKY)
```yaml
annotators: sqlite:obo:metpo
```
- **Pros:** Simpler syntax
- **Cons:** May be outdated, unclear which version
- **Used by:** morphology_template_base

**Recommendation:** Use local file path for all templates to ensure latest METPO version.

---

## Rigorous Test Plan

### Test 1: Controlled Grounding Validation

**Goal:** Verify OntoGPT can ground to METPO when properly configured

**Method:**
1. Create test document with known METPO terms
2. Run extraction with growth_conditions template (has METPO)
3. Verify successful grounding

**Test Document Content:**
```text
Title: Growth characteristics of mesophilic bacteria

The bacterium grows optimally at 37°C (mesophilic). It is a facultative anaerobe,
capable of both aerobic and anaerobic growth. The organism is Gram-negative and
shows optimal growth at pH 7.0 (neutrophilic). It tolerates up to 3% NaCl (halotolerant).

The species is thermophilic with a temperature range of 45-80°C. It is an obligate aerobe
and alkaliphilic, growing best at pH 9.5.
```

**Expected METPO Groundings:**
- mesophilic → METPO:0000025
- thermophilic → METPO:0000026
- facultative anaerobe → METPO:0000030
- obligate aerobe → METPO:0000028
- Gram-negative → METPO:0000010
- neutrophilic → METPO:0000033
- alkaliphilic → METPO:0000034
- halotolerant → METPO:0000036

**Command:**
```bash
uv run ontogpt extract \
  -t templates/growth_conditions_hybrid.yaml \
  -i test_metpo_grounding.txt \
  -o test_results/metpo_grounding_test.yaml
```

**Success Criteria:** >80% of expected terms ground to METPO

---

### Test 2: Template Optimization - Add METPO Annotators

**Goal:** Fix biochemical and chemical utilization templates

**Files to Modify:**
1. `templates/biochemical_hybrid.yaml`
2. `templates/chemical_utilization_hybrid.yaml`

**Changes Needed:**

#### For biochemical_hybrid.yaml:

Add METPO annotator to metabolic phenotype classes:

```yaml
MetabolicPhenotype:
  is_a: NamedEntity
  description: >-
    Metabolic capabilities and nutritional requirements of organisms
  annotations:
    annotators: sqlite:../src/ontology/metpo.owl, sqlite:obo:go, sqlite:obo:chebi

NutritionalType:
  is_a: NamedEntity
  description: >-
    Carbon and nitrogen source utilization patterns
  annotations:
    annotators: sqlite:../src/ontology/metpo.owl, sqlite:obo:chebi
```

#### For chemical_utilization_hybrid.yaml:

Add METPO for substrate utilization:

```yaml
SubstrateUtilization:
  is_a: NamedEntity
  description: >-
    Compounds that organisms can use as carbon or energy sources
  annotations:
    annotators: sqlite:../src/ontology/metpo.owl, sqlite:obo:chebi
```

---

### Test 3: Before/After Comparison

**Goal:** Measure improvement from template optimization

**Corpus:** Same 6 fullcorpus files from production analysis

**Method:**
1. Run BEFORE: Use existing templates (baseline)
2. Modify templates: Add METPO annotators
3. Run AFTER: Re-extract with optimized templates
4. Compare: METPO grounding rate before vs. after

**Extraction Commands:**

```bash
# Create test directory
mkdir -p test_results/before
mkdir -p test_results/after

# BEFORE (existing templates)
uv run ontogpt extract -t templates/biochemical_hybrid.yaml \
  -i CMM-AI/publications/doi_10_1007-s00253-014-5766-8.pdf \
  -o test_results/before/biochemical_test.yaml

# AFTER (optimized templates)
# First: modify templates to add METPO annotators
# Then: re-run same extraction
uv run ontogpt extract -t templates/biochemical_hybrid_optimized.yaml \
  -i CMM-AI/publications/doi_10_1007-s00253-014-5766-8.pdf \
  -o test_results/after/biochemical_test.yaml

# Compare grounding rates
uv run python analyze_metpo_grounding_filtered.py test_results/before
uv run python analyze_metpo_grounding_filtered.py test_results/after
```

**Success Metrics:**
- METPO grounding rate increases from 0% to >20%
- AUTO: term count decreases for phenotype categories
- Remaining AUTO: terms are genuine gaps (not config failures)

---

### Test 4: Input Source Type Comparison

**Goal:** Test if input format affects METPO grounding

**Sources to Test:**
1. **IJSEM abstracts** (structured, standardized format)
2. **BacDive field descriptions** (semi-structured)
3. **Full research papers** (unstructured)

**Hypothesis:** Structured sources should have higher grounding rates

**IJSEM Abstract Test:**
```bash
# Query MongoDB for IJSEM abstracts with standard phenotype descriptions
mongosh "mongodb://192.168.0.218:27017/europepmc" --eval "
  db.ijsem_articles.find(
    { title: /thermophilic|mesophilic|halophilic/ },
    { pmid: 1, title: 1, abstractText: 1 }
  ).limit(10)
" > test_inputs/ijsem_abstracts.json

# Extract phenotypes
uv run ontogpt extract \
  -t templates/growth_conditions_hybrid.yaml \
  -i test_inputs/ijsem_abstracts.json \
  -o test_results/ijsem_grounding.yaml
```

**Full Paper Test:**
```bash
# Use existing CMM papers
uv run ontogpt extract \
  -t templates/growth_conditions_hybrid.yaml \
  -i CMM-AI/publications/doi_10_1007-s00253-014-5766-8.pdf \
  -o test_results/fullpaper_grounding.yaml
```

**Expected Results:**
- IJSEM abstracts: Higher METPO grounding (standardized terminology)
- Full papers: More AUTO: terms (varied terminology)

---

### Test 5: METPO Label/Synonym Coverage

**Goal:** Identify why valid METPO classes don't ground

**Method:**
1. Extract all AUTO: phenotype terms from production corpus
2. For each AUTO: term, check if METPO has matching class
3. For matches, check if labels/synonyms are aligned

**Example Analysis:**

```python
# AUTO: term found in extraction
auto_term = "Gram-negative bacteria"

# METPO has class
metpo_class = "METPO:0000010"
metpo_label = "Gram-negative"

# Label matching analysis
exact_match = False  # "Gram-negative bacteria" != "Gram-negative"
partial_match = True # "Gram-negative" in "Gram-negative bacteria"

# Recommendation: Add synonym to METPO
# In metpo.owl:
# <oboInOwl:hasSynonym>Gram-negative bacteria</oboInOwl:hasSynonym>
```

**Deliverable:** TSV file with columns:
- AUTO_term
- METPO_class_exists (Y/N)
- METPO_label
- Exact_match (Y/N)
- Partial_match (Y/N)
- Recommendation (add_synonym / new_class / not_phenotype)

---

### Test 6: Genuine Gap Identification

**Goal:** After optimization, identify AUTO: terms that indicate real METPO gaps

**Method:**
1. Run optimized extractions
2. Categorize remaining AUTO: terms:
   - **Config failures:** Should ground but don't (need synonym)
   - **Genuine gaps:** METPO doesn't have this concept (need new class)
   - **Out of scope:** Not a phenotype (strain ID, enzyme name, etc.)

**Categories for Manual Review:**

#### Genuine Gaps - Candidate New Classes:
```yaml
AUTO:rare-earth%20element%20(REE)  # Growth requirement - CMM project needs
AUTO:light%20lanthanides            # Growth requirement - CMM project needs
AUTO:reddish%20brown                # Pigmentation - BactoTraits has this
AUTO:high%20adsorption%20capacity   # Quantitative trait - scope decision
```

#### Config Failures - Need Synonyms:
```yaml
AUTO:methylotrophic%20bacteria      # METPO has "methylotroph"
AUTO:Gram-negative%20bacteria       # METPO has "Gram-negative"
AUTO:rod-shaped                     # METPO has cell shape classes
```

#### Out of Scope - Correctly AUTO:
```yaml
AUTO:USDA110                        # Strain ID
AUTO:XoxF                           # Enzyme/protein
AUTO:methanol%20dehydrogenase       # Molecular entity
```

---

## Recommended Extraction Experiments

### Experiment 1: Optimized Growth Conditions Extraction

**Input Files:** IJSEM abstracts from MongoDB

**Template:** `growth_conditions_hybrid.yaml` (already has METPO)

**MongoDB Query:**
```javascript
// Get 50 IJSEM abstracts with diverse phenotypes
db.ijsem_articles.find(
  { $or: [
    { abstractText: /thermophilic|mesophilic|psychrophilic/ },
    { abstractText: /halophilic|alkaliphilic|acidophilic/ },
    { abstractText: /aerobic|anaerobic|facultative/ },
    { abstractText: /Gram-positive|Gram-negative/ }
  ]},
  { pmid: 1, doi: 1, title: 1, abstractText: 1 }
).limit(50)
```

**Save Abstracts:**
```bash
mongosh "mongodb://192.168.0.218:27017/europepmc" \
  --quiet --eval "
  db.ijsem_articles.find(
    { abstractText: /thermophilic|mesophilic|halophilic|aerobic/ },
    { pmid: 1, doi: 1, title: 1, abstractText: 1 }
  ).limit(50).forEach(doc => print(JSON.stringify(doc)))
  " > test_inputs/ijsem_phenotype_abstracts.jsonl
```

**Extract:**
```bash
uv run ontogpt extract \
  -t templates/growth_conditions_hybrid.yaml \
  -i test_inputs/ijsem_phenotype_abstracts.jsonl \
  -o test_results/ijsem_optimized_extraction.yaml \
  --model gpt-4o \
  --temperature 0.0
```

**Expected Result:** Higher METPO grounding due to:
- Template already has METPO annotators
- IJSEM abstracts use standardized phenotype terminology
- Controlled vocabulary matches METPO labels

---

### Experiment 2: Morphology Extraction with OBO vs Local METPO

**Goal:** Compare sqlite:obo:metpo vs sqlite:../src/ontology/metpo.owl

**Files:**
1. Create `morphology_template_local.yaml` - change annotator to local file
2. Keep `morphology_template_base.yaml` - uses OBO library

**Test Document:** Same morphology-rich text for both

**Commands:**
```bash
# Test 1: OBO library version
uv run ontogpt extract \
  -t templates/morphology_template_base.yaml \
  -i test_inputs/morphology_test.txt \
  -o test_results/morphology_obo.yaml

# Test 2: Local file version
uv run ontogpt extract \
  -t templates/morphology_template_local.yaml \
  -i test_inputs/morphology_test.txt \
  -o test_results/morphology_local.yaml

# Compare results
diff test_results/morphology_obo.yaml test_results/morphology_local.yaml
```

**Expected:** Local version may ground better if OBO library is outdated

---

### Experiment 3: Biochemical Extraction - Before/After METPO Annotation

**Input:** CMM lanthanide papers (known to have metabolic phenotypes)

**Templates:**
- BEFORE: `biochemical_hybrid.yaml` (current - no METPO)
- AFTER: `biochemical_hybrid_metpo.yaml` (modified - add METPO)

**Input Files:**
```
CMM-AI/publications/doi_10_1007-s00253-014-5766-8.pdf  (Rare earth element metabolism)
CMM-AI/publications/doi_10_1038-nchembio_1947.pdf     (Lanthanide biochemistry)
CMM-AI/publications/fmicb-13-921635.pdf                (REE biorecovery)
```

**Commands:**
```bash
# BEFORE
uv run ontogpt extract \
  -t templates/biochemical_hybrid.yaml \
  -i CMM-AI/publications/doi_10_1007-s00253-014-5766-8.pdf \
  -o test_results/before_biochem.yaml

# Create optimized template (add METPO annotators to relevant classes)
cp templates/biochemical_hybrid.yaml templates/biochemical_hybrid_metpo.yaml
# Edit to add: annotators: sqlite:../src/ontology/metpo.owl

# AFTER
uv run ontogpt extract \
  -t templates/biochemical_hybrid_metpo.yaml \
  -i CMM-AI/publications/doi_10_1007-s00253-014-5766-8.pdf \
  -o test_results/after_biochem.yaml

# Compare
uv run python compare_extractions.py \
  test_results/before_biochem.yaml \
  test_results/after_biochem.yaml
```

**Expected AUTO→METPO Improvements:**
- methylotrophic → METPO:methylotroph
- Gram-negative → METPO:Gram-negative
- aerobic → METPO:aerobic

**Expected Remaining AUTO (genuine gaps):**
- rare-earth element → NEW METPO CLASS NEEDED
- lanthanide requirement → NEW METPO CLASS NEEDED

---

## Deliverables

### 1. Template Modifications
- [ ] `biochemical_hybrid_metpo.yaml` - Add METPO annotators
- [ ] `chemical_utilization_hybrid_metpo.yaml` - Add METPO annotators
- [ ] `morphology_template_local.yaml` - Use local METPO instead of OBO

### 2. Test Results
- [ ] `test_results/metpo_grounding_test.yaml` - Controlled validation
- [ ] `test_results/ijsem_optimized_extraction.yaml` - Structured abstracts
- [ ] `test_results/before_after_comparison.tsv` - Grounding improvement metrics

### 3. Analysis Reports
- [ ] `AUTO_TERM_CATEGORIZATION.tsv` - Manual classification of AUTO: terms
- [ ] `METPO_LABEL_COVERAGE.tsv` - Label/synonym gaps
- [ ] `NEW_CLASS_RECOMMENDATIONS.md` - Genuine gaps for METPO expansion

### 4. ICBO Presentation Materials
- [ ] Example showing successful METPO grounding
- [ ] Example showing config failure (fixed by adding annotator)
- [ ] Example showing genuine gap (REE requirement)
- [ ] Before/after metrics from template optimization

---

## Timeline

**Day 1 (Today):**
- ✅ Template configuration audit
- ✅ Test plan creation
- [ ] Test 1: Controlled grounding validation
- [ ] Experiment 1: IJSEM abstracts

**Day 2:**
- [ ] Template modifications (add METPO annotators)
- [ ] Test 3: Before/after comparison
- [ ] Experiment 3: Biochemical optimization

**Day 3:**
- [ ] Test 5: Label/synonym coverage analysis
- [ ] Test 6: Genuine gap identification
- [ ] Categorize all AUTO: terms
- [ ] Draft ICBO slide examples

---

## Success Criteria

**Minimum Success:**
- Controlled test shows METPO grounding works when configured
- At least one template improves from 0% to >20% METPO grounding
- Clear categorization of AUTO: terms (failures vs. gaps)

**Target Success:**
- Growth conditions template: >80% METPO grounding on IJSEM
- Biochemical template (optimized): >40% METPO grounding
- <20 genuine METPO gaps identified for future work

**Stretch Success:**
- All production templates optimized with METPO annotators
- Comprehensive label/synonym additions to METPO
- GitHub issues filed for each genuine gap with examples

---

**Next Steps:** Run Test 1 (controlled validation) to verify OntoGPT+METPO works correctly.
