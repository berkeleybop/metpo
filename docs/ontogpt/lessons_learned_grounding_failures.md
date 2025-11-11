# Lessons Learned: OntoGPT Grounding Failures

**Date:** 2025-11-11 (documented from 2025-08 experimental work)
**Context:** Analysis of failed ChEBI grounding experiments from PR #208

---

## Problem: Single-Letter False Matches

### What Happened

During experimental work with OAK/OntoGPT text matching for METPO metabolism terms, we attempted to ground terms against ChEBI. The results were **spurious single-letter matches**:

```tsv
METPO Term          → ChEBI ID    Matched Label
autotrophic        → CHEBI:13193  "A"
chemotrophic       → CHEBI:15356  "C"
heterotrophic      → CHEBI:15971  "H"
lithoautotrophic   → CHEBI:15603  "L"
methylotrophic     → CHEBI:16044  "M"
```

### Root Causes

1. **Substring matching without word boundaries**
   - Matcher found single letters within METPO labels
   - No requirement for complete word matches
   - "autotrophic" contains "a" → matched ChEBI entity with label "A"

2. **No minimum length filter**
   - Allowed matches on 1-character strings
   - Should require minimum 3-character matches for meaningful grounding

3. **Wrong ontology for entity type**
   - Metabolism phenotype terms should NOT be grounded to chemical entities
   - ChEBI is for chemical compounds, not microbial phenotypes
   - This was a conceptual mismatch, not just a technical issue

4. **ChEBI legitimately has single-letter labels**
   - These ARE real ChEBI entities (chemical symbols like "A" for adenine, "C" for cytosine)
   - The matches are technically correct substring matches
   - The problem is using ChEBI for the wrong purpose

---

## Lessons for OntoGPT Template Design

### ✅ Use Ontology-Appropriate Grounding

**Match entity types to ontologies:**
- **Taxon entities** → `sqlite:obo:ncbitaxon` (ONLY)
- **Chemical entities** → `sqlite:obo:chebi` (ONLY)
- **Phenotype entities** → `sqlite:obo:pato`, `sqlite:obo:omp`, or METPO itself
- **Strain entities** → No ontology grounding (keep as AUTO CURIEs)

**Don't cross-contaminate:**
- Don't ground metabolism phenotypes (autotrophic, chemotrophic) to chemical ontologies
- Don't ground chemical compounds to phenotype ontologies
- Use the right tool for the job

### ✅ Configure Matching Parameters

**For lexical matching, require:**
- **Minimum length:** ≥3 characters (prevents single-letter matches)
- **Word boundaries:** Complete word matches, not substrings
- **Case sensitivity:** Configure appropriately for domain
- **Stemming/lemmatization:** Consider for better recall

### ✅ Validate Grounding Results

**After running extraction:**
1. **Spot check groundings** - Review sample of matched entities
2. **Check for nonsense patterns** - Single letters, numbers, symbols
3. **Verify ontology relevance** - Do the matched terms make sense?
4. **Measure grounding rates** - >80% grounded is good, <50% suggests problems

### ✅ Template Optimization is Critical

**From CBORG GPT-5 analysis (Aug 2025):**
- Excessive annotators cause **4-5x performance degradation**
- More annotators ≠ better grounding
- Choose **one appropriate annotator per entity type**
- Strain annotators provide **no value** and should be removed

**Recommended minimal annotators:**
```yaml
taxon:
  annotations:
    annotators: sqlite:obo:ncbitaxon  # ONLY NCBITaxon

chemical:
  annotations:
    annotators: sqlite:obo:chebi  # ONLY ChEBI

strain:
  # NO annotators - keep as AUTO CURIEs
```

---

## Related Documentation

- **Template optimization:** `docs/ontogpt/CBORG_GPT5_Chemical_Extraction_Analysis_2025-08.md`
- **Current templates:** `literature_mining/templates/`
- **Annotator configuration:** See Makefile target `templates/%_populated.yaml`

---

## Takeaway

**The key insight:** This wasn't a bug in OAK/OntoGPT - it did exactly what it was asked to do (find substrings in labels). The mistake was **asking the wrong question** (grounding phenotypes to chemicals).

Good grounding requires:
1. Choosing the right ontology for the entity type
2. Configuring appropriate matching parameters
3. Validating results to catch misconfigurations early

This is why we now use **minimal, targeted annotators** in our OntoGPT templates.
