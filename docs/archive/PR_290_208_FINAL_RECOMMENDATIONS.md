# PR #290 & #208: Final Extraction Recommendations

**Date:** 2025-11-11
**Criteria:** Keep only what helps improve what we already have; no API key analysis, no extraction outputs/logs/templates

---

## PR #290: "files on MacBook prior to 2025-11-07"

### Decision: **CLOSE WITHOUT EXTRACTING**

**Rationale:**
- API key testing scripts & reports → Not needed (issue resolved, better docs on NUC)
- Generated files (metpo.owl, extraction outputs) → Should be built, not committed
- Makefile changes → Minimal (.env loading) - check if already in main, but likely not worth cherry-picking
- growth_conditions_populated.yaml → Just another template variant, doesn't improve current templates

**No treasures identified that improve current codebase.**

---

## PR #208: "another backup branch"

### Decision: **EXTRACT 1-2 ITEMS, THEN CLOSE**

### ✅ DEFINITE KEEP: CBORG Analysis Document

**File:** `literature_mining/A/CBORG_GPT5_EXTRACTION_ANALYSIS.md` (163 lines)

**Why it helps improve what we have:**
1. **Template optimization insights:**
   - Documents that excessive annotators cause 4-5x performance degradation
   - Recommends removing strain annotators entirely (provide no value)
   - Specific annotator recommendations: NCBITaxon only for taxa, ChEBI only for chemicals

2. **Cost-performance benchmarks:**
   - $0.085/abstract for GPT-5 via CBORG
   - 43 minutes for 9 abstracts (baseline for capacity planning)
   - Grounding rate: 46.8% (benchmark for quality assessment)

3. **Strain vs taxon normalization strategy:**
   - Clear recommendations for CompoundExpression structure
   - Documents that strain identifiers should be AUTO CURIEs
   - Explains why full taxonomic context in strains is problematic

4. **Actionable next steps:**
   - Make recommendations for template regeneration
   - Identifies assessment tool integration needs
   - Proposes benchmarking methodology

**Where to put it:** `docs/ontogpt/CBORG_GPT5_Chemical_Extraction_Analysis_2025-08.md`

**Value:** This is **methodology documentation** that informs future OntoGPT work - not just extraction logs.

---

### 🟡 MAYBE KEEP: Session Summary

**File:** `session_summary.md` (108 lines)

**What it documents:**
- Analysis of METPO metabolism hierarchy (flat structure problem)
- Proposed hierarchy improvements (intermediate classes)
- 73 metabolism leaf terms identified
- ID conflict found (1000666 used twice)

**Why it might help:**
- Documents ontology design analysis session
- Proposes structural improvements to metabolism terms
- Historical context for hierarchy decisions

**Concern:**
- Is this analysis still relevant?
- Have these hierarchy improvements been implemented?
- Is the flat hierarchy still a problem?

**Decision needed:** Compare with current `src/templates/metpo_sheet.tsv` to see if:
1. The flat hierarchy has been fixed
2. The proposed improvements have been implemented
3. This represents unfinished work

**If still relevant:** Move to `docs/ontology/metabolism_hierarchy_analysis_2025-08.md`
**If superseded:** Skip it

---

### ❌ DO NOT KEEP

**Metabolism TSV files:**
- `regenerated_metabolism_terms.tsv` - Just a list of existing METPO IDs (already in repo)
- `regenerated_metabolism_terms_to_chebi.tsv` - **Spurious false matches** (single-letter matches like "C" → CHEBI:15356)

**SPARQL queries:**
- `label_count_query.sparql` - Trivial 10-line query (count labels per class)
- `regenerate_metabolism_terms.sparql` - Simple subClassOf query, not reusable pattern

**All literature_mining/ files:**
- cborg_chemical_extraction.py - API key tracking script, not production tool
- All extraction outputs, logs, test files - Not helping improve current work

---

## Summary of Actions

### PR #290
**Action:** Close with brief comment
**Comment:**
```
Closing this backup PR. Reviewed all files:
- API key testing/reports: Not needed (issue resolved)
- Generated files: Should not be committed
- Template/Makefile changes: No improvements over current main

No content extracted.
```

### PR #208
**Action:** Extract CBORG analysis, evaluate session summary, then close

**Step 1: Extract CBORG analysis**
```bash
git fetch origin another-backup
git show origin/another-backup:literature_mining/A/CBORG_GPT5_EXTRACTION_ANALYSIS.md > \
  docs/ontogpt/CBORG_GPT5_Chemical_Extraction_Analysis_2025-08.md
git add docs/ontogpt/CBORG_GPT5_Chemical_Extraction_Analysis_2025-08.md
git commit -m "docs: Add CBORG GPT-5 extraction analysis from PR #208

Extracted from experimental backup branch. Documents:
- Template optimization recommendations
- Cost-performance benchmarks
- Strain/taxon normalization strategy
- Assessment tool integration needs

This is methodology documentation informing future OntoGPT work."
```

**Step 2: Evaluate session summary**
Check if metabolism hierarchy analysis is still relevant:
```bash
# Compare current metabolism terms
grep "1000631\|1000800\|1000060" src/templates/metpo_sheet.tsv
# Check if flat hierarchy persists
# Decide: Extract or skip
```

**Step 3: Close PR**
**Comment:**
```
Closing this experimental backup PR. Reviewed all files against criteria: "keep only what helps improve what we already have."

**Extracted:**
- ✅ CBORG GPT-5 extraction analysis → `docs/ontogpt/`
  (Methodology documentation with template optimization insights and benchmarks)
[- ✅ Metabolism hierarchy analysis → `docs/ontology/` (if still relevant)]

**Not extracted:**
- ❌ Metabolism TSV files: Spurious ChEBI matches, no value
- ❌ SPARQL queries: Trivial, not reusable patterns
- ❌ Extraction script: API key tracking, not production tool
- ❌ All extraction outputs/logs/test files: Don't improve current work

Total: 1-2 files extracted, 28 files discarded. Core insights preserved.
```

---

## Decision Tree Applied

For each file, asked:
1. **Does it help improve what we already have?**
   - CBORG analysis: ✅ Yes (informs template optimization, benchmarking)
   - Session summary: 🟡 Maybe (depends on current state)
   - Everything else: ❌ No

2. **Is it documentation/methodology or just outputs?**
   - CBORG analysis: Documentation
   - Session summary: Documentation
   - TSVs/SPARQL/scripts/logs: Outputs

3. **Is it superseded or still relevant?**
   - CBORG analysis: Still relevant (Aug 2025, recent insights)
   - Session summary: Unknown (check current state)
   - Metabolism TSVs: Superseded (already in repo)

**Result:** Extract 1-2 files maximum, close both PRs.
