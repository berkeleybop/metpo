# PR #290 and #208 Analysis and Closure Plan

**Date:** 2025-11-11
**Analyst:** Claude Code

---

## PR #290: "files on MacBook prior to 2025-11-07"

**Branch:** `mbp-20251106`
**Status:** Draft, opened 4 days ago
**Size:** 10,587 additions, 1 deletion

### Assessment Summary

**Overall Rating: 🗑️ 95% Junk, 5% Maybe**

This PR contains mostly temporary/internal files that should NOT be committed.

### File-by-File Analysis

#### 🔴 **DEFINITE JUNK - DO NOT MERGE (13 files)**

**API Key Testing & Logs:**
- `test_all_keys.sh` - Temporary testing script
- `test_jed_key.sh` - Temporary testing script
- `test_luke_key.sh` - Temporary testing script
- `test_openai_key.py` - Temporary testing script
- `test_all_keys.txt` (848 lines) - Test output logs
- `test_all_keys_2025-11-03.txt` (1,019 lines) - Test output logs

**⚠️ SENSITIVE INFORMATION:**
- `key_status_report.tsv` - Contains team email addresses, partial API keys, budget info
- `key_status_report_2025-11-03.tsv` - Same, dated version
- `key_status_report_detailed.tsv` - Same, detailed version

**Reasoning:** These contain internal team information (emails, API key prefixes, budgets) that should remain private. While API keys are redacted (`sk-...wP2A`), this reveals operational details about the team structure and spending patterns.

**Generated Intermediate Files:**
- `literature_mining/intermediates/db/metpo.owl` (7,466 lines) - Should be built, not committed
- `literature_mining/intermediates/db/metpo-relation-graph.tsv.gz` - Generated file
- `literature_mining/outputs/growth_conditions_20251101_132923.yaml` (758 lines) - Extraction output

#### 🟡 **MAYBE - REVIEW CAREFULLY (2 files)**

**Template File:**
- `literature_mining/templates/growth_conditions_populated.yaml` (365 lines)
  - **Check:** Compare with existing `growth_conditions_hybrid.yaml` and `growth_conditions_template_base.yaml`
  - **Decision:** If this adds value over existing templates, extract to main. Otherwise skip.
  - **Preliminary assessment:** Looks like an enriched/populated version with METPO terms pre-filled

**Makefile Changes:**
- `literature_mining/Makefile` (6 additions, 1 deletion)
  - Adds `.env` file loading for API keys
  - Adds debug echo for `OPENAI_API_KEY`
  - **Check:** Compare with current main branch version
  - **Decision:** If these improvements are useful and not already incorporated, cherry-pick

### Recommendations for PR #290

**DO NOT MERGE** - Close with explanation

**Actions:**
1. Compare `growth_conditions_populated.yaml` with existing templates - extract if valuable
2. Review Makefile changes - cherry-pick if improvements are useful
3. Close PR with comment explaining:
   - Testing/logging files should not be committed
   - Sensitive team information should remain private
   - Intermediate/generated files should not be committed
   - Any valuable changes can be extracted manually

---

## PR #208: "another backup branch"

**Branch:** `another-backup`
**Status:** Draft, opened Sep 24
**Size:** 39,891 additions, 0 deletions

### Assessment Summary

**Overall Rating: 🎁 20% Treasures, 80% Junk**

This PR contains valuable OntoGPT/CBORG experimental documentation mixed with logs and test outputs.

### File-by-File Analysis

#### 🟢 **TREASURES - EXTRACT THESE (6 files)**

**1. CBORG GPT-5 Extraction Analysis** ⭐⭐⭐
- `literature_mining/A/CBORG_GPT5_EXTRACTION_ANALYSIS.md` (163 lines)
- **Value:** Comprehensive analysis of CBORG/GPT-5 extraction performance
- **Key insights:**
  - Template optimization recommendations (fewer annotators = faster)
  - Cost analysis ($0.085/abstract)
  - Strain vs taxon normalization issues
  - Performance metrics (43 minutes for 9 abstracts)
- **Action:** Move to `docs/literature_mining/` or `docs/ontogpt/` with renamed title
- **Rename to:** `CBORG_GPT5_Chemical_Extraction_Analysis_2025-08.md`

**2. CBORG Extraction Script** ⭐⭐
- `literature_mining/A/cborg_chemical_extraction.py` (242 lines)
- **Value:** Production-quality script for OntoGPT extraction with CBORG endpoint
- **Features:**
  - API key management from `.env`
  - Cost tracking (before/after API calls)
  - Performance timing
  - Quality assessment integration
- **Action:** Move to `metpo/literature_mining/scripts/` with Click CLI conversion
- **Rename to:** `cborg_extract_with_tracking.py`
- **TODO:** Convert to Click interface, add to pyproject.toml

**3. Session Summary - Metabolism Hierarchy** ⭐⭐
- `session_summary.md` (108 lines)
- **Value:** Documents ontology structure analysis and proposed improvements for metabolism terms
- **Key insights:**
  - Analysis of flat metabolism hierarchy (232 terms under single parent)
  - Proposed intermediate classes (trophic type, respiratory type, metabolic trait)
  - Recommendations for better organization
- **Action:** Move to `docs/ontology/`
- **Rename to:** `metabolism_hierarchy_analysis_2025-08.md`

**4. Metabolism Term Regeneration** ⭐
- `regenerated_metabolism_terms.tsv` (76 lines)
- `regenerated_metabolism_terms_to_chebi.tsv` (76 lines)
- **Value:** Mapping tables for metabolism terms, possibly to ChEBI
- **Action:** Review content, move to `data/mappings/` if useful
- **Check:** Are these superseded by current METPO mappings?

**5. SPARQL Queries** ⭐
- `label_count_query.sparql` (10 lines)
- `regenerate_metabolism_terms.sparql` (19 lines)
- **Value:** Reusable queries for ontology analysis
- **Action:** Review content, move to `sparql/` if useful
- **Check:** Are these one-off queries or reusable patterns?

#### 🔴 **DEFINITE JUNK - DO NOT EXTRACT (22 files)**

**Experimental Directory:**
- `literature_mining/A/cborg_extraction_results_20250818_185847.json` (100 lines)
- `literature_mining/A/chemical_utilization_cborg_gpt5_20250818_181520.yaml` (1,435 lines)
- `literature_mining/A/chemical_utilization_populated.yaml` (282 lines)

**Extraction Logs (24k+ lines total):**
- `literature_mining/logs/ontogpt_verbose_20250819_114203.log` (23,114 lines)
- `literature_mining/logs/advanced_assessment_*.json` (4,970 lines)
- `literature_mining/logs/predicate_analysis_*.json` (811 lines)
- Plus 8 more JSON/YAML log files

**Extraction Outputs:**
- `literature_mining/outputs/chemical_utilization_*.yaml` (7 files, ~7,644 lines total)

**Test Data:**
- `literature_mining/test-chemical-3abstracts/11321104-abstract.txt`
- `literature_mining/test-chemical-3abstracts/16585689-abstract.txt`
- `literature_mining/test-chemical-3abstracts/19578151-abstract.txt`

**Reasoning:** These are all experimental runs, logs, and test data from August 2025 CBORG experimentation. The valuable insights are captured in the analysis markdown.

### Recommendations for PR #208

**DO NOT MERGE** - Extract treasures, then close

**Actions:**
1. Extract CBORG analysis markdown to `docs/ontogpt/`
2. Extract CBORG script to `metpo/literature_mining/scripts/` (with Click conversion)
3. Extract session summary to `docs/ontology/`
4. Review metabolism TSVs and SPARQL queries - extract if useful
5. Close PR with comment explaining what was extracted

---

## Extraction Plan

### Step 1: Compare with Current Main

Before extracting, check if any of this work is already incorporated:

```bash
# Check if growth_conditions templates already exist
ls literature_mining/templates/growth_conditions*

# Check if CBORG documentation already exists
find docs/ -name "*cborg*" -o -name "*gpt5*" -o -name "*gpt-5*"

# Check if metabolism analysis already exists
find docs/ -name "*metabolism*" -o -name "*hierarchy*"

# Check current Makefile
git diff main:literature_mining/Makefile mbp-20251106:literature_mining/Makefile
```

### Step 2: Extract Treasures to New Commits

For PR #208:
```bash
# Get the files
git fetch origin another-backup

# Extract documentation
git show origin/another-backup:literature_mining/A/CBORG_GPT5_EXTRACTION_ANALYSIS.md > \
  docs/ontogpt/CBORG_GPT5_Chemical_Extraction_Analysis_2025-08.md

git show origin/another-backup:session_summary.md > \
  docs/ontology/metabolism_hierarchy_analysis_2025-08.md

# Extract script
git show origin/another-backup:literature_mining/A/cborg_chemical_extraction.py > \
  metpo/literature_mining/scripts/cborg_extract_with_tracking.py

# Review and possibly extract
git show origin/another-backup:regenerated_metabolism_terms.tsv
git show origin/another-backup:label_count_query.sparql
```

For PR #290:
```bash
# Get the files
git fetch origin mbp-20251106

# Compare templates
git show origin/mbp-20251106:literature_mining/templates/growth_conditions_populated.yaml > /tmp/gc_pop.yaml
diff /tmp/gc_pop.yaml literature_mining/templates/growth_conditions_hybrid.yaml

# Review Makefile changes
git show origin/mbp-20251106:literature_mining/Makefile
```

### Step 3: Close PRs with Documentation

**Comment template for PR #290:**
```markdown
## PR #290 Closure Summary

This PR contained mostly temporary testing files and internal team information that should not be committed to the repository.

**Files reviewed:**
- ❌ API key testing scripts (13 files) - Temporary, not for repo
- ❌ Key status reports (3 files) - Contains sensitive team information
- ❌ Generated intermediate files - Should be built, not committed
- ✅ Extracted: [list any files that were valuable]

**Actions taken:**
- [List any extracted content]
- Closing PR to keep repository clean

**For future reference:**
- Use `.gitignore` for test scripts and logs
- Keep sensitive team information in private channels
- Commit source code and documentation, not generated files
```

**Comment template for PR #208:**
```markdown
## PR #208 Closure Summary

This backup branch contained valuable CBORG/OntoGPT experimental documentation mixed with logs and test data.

**Treasures extracted:**
- ✅ CBORG GPT-5 extraction analysis → `docs/ontogpt/CBORG_GPT5_Chemical_Extraction_Analysis_2025-08.md`
- ✅ CBORG extraction script → `metpo/literature_mining/scripts/cborg_extract_with_tracking.py`
- ✅ Metabolism hierarchy analysis → `docs/ontology/metabolism_hierarchy_analysis_2025-08.md`
- [List any other extracted files]

**Not extracted (logs/test data):**
- 22 log files and extraction outputs (experimental runs from Aug 2025)
- Test abstract files
- Experimental directory `literature_mining/A/`

**Result:** Valuable insights and code preserved, temporary experimental files discarded. Closing PR.
```

---

## Final Recommendations

1. **PR #290:** Close immediately after extracting template comparison (if valuable)
2. **PR #208:** Extract 3-6 files, then close
3. **Both PRs:** Add detailed closure comments explaining what was kept and why
4. **Future:** Establish clearer guidelines for backup branches vs. feature branches
