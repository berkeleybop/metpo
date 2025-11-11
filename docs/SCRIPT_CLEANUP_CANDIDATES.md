# Script Cleanup Candidates

**Date**: 2025-11-10
**Purpose**: Identify scripts that may be candidates for deletion or consolidation

---

## Summary

**Total Python files**: 72
**Registered CLI commands**: 26
**Unregistered scripts**: 46

---

## Categories

### ✅ Keep - Registered CLI Tools (26 files)

These are in `pyproject.toml [project.scripts]` and actively used:

**Tools (3):**
- `metpo/tools/extract_rank_triples.py` → `extract-rank-triples`
- `metpo/tools/convert_chem_props.py` → `convert-chem-props`
- `metpo/tools/import_bactotraits.py` → `import-bactotraits`

**BactoTraits (10):**
- All in `metpo/bactotraits/` with CLI commands

**Pipeline (7):**
- All in `metpo/pipeline/` with CLI commands

**Database (4):**
- All in `metpo/database/` with CLI commands

**Analysis (2):**
- `metpo/analysis/analyze_ontology_value.py`
- `metpo/analysis/analyze_match_quality.py`

---

## ⚠️ Review - Unregistered Scripts

### 1. Scripts in Data Directories (SHOULD NOT BE HERE!)

**⚠️ data/bactotraits/create_bactotraits_migration.py** (9.2K)
- Purpose: Converts BactoTraits sheet to minimal_classes format
- Usage: One-time data migration
- Last modified: 2025-11-07 (reorganization commit)
- **Problem**: Python scripts should NOT be in data/ directories!
- **Recommendation**: Move to `metpo/bactotraits/` or delete if complete

**⚠️ large/make_bacdive_utilization_enum.py** (6.7K)
- Purpose: Convert TSV to LinkML enumeration for BacDive utilization
- Usage: One-time schema generation
- Last modified: 2025-11-07 (reorganization commit)
- Context: `large/` is 578MB (gitignored), contains:
  - N4L_phenotypic_ontology_2016/ (574MB of reference data)
  - n4l_ref_protolog_orgname_vs_kgmicrobe.csv (3.8MB)
  - SPARQL queries, notes, reports
- **Problem**: Python script mixed with reference data
- **Recommendation**: Move to `metpo/tools/` or `scripts/one-time/` if historical

**Directory Organization Issue:**
- `data/` should contain only data files (TSV, CSV, JSON)
- `large/` is gitignored reference data - fine, but Python scripts should be elsewhere

---

### 2. Literature Mining Analysis Scripts (11 files)

**In `literature_mining/` root:**

Active analysis scripts (✅ Keep for now):
- `analyze_metpo_grounding.py` - Primary grounding analysis
- `analyze_metpo_grounding_filtered.py` - Filtered grounding analysis
- `extract_metpo_entities.py` - Entity extraction
- `find_metpo_terms.py` - Term finding utilities

Possibly redundant (⚠️ Review):
- `analyze_extractions.py` - Generic extraction analysis (overlaps with analyze_metpo_grounding?)
- `compare_extractions.py` - Comparison script (one-time use?)
- `validate_extractions.py` - Validation (covered by analyze_metpo_grounding?)
- `analyze_coverage_by_source_type.py` - Source type analysis (one-time?)
- `analyze_metpo_efficiency.py` - Efficiency metrics (one-time?)
- `analyze_metpo_database_alignment.py` - Database alignment (one-time?)
- `metpo_assessor.py` - Assessment tool (deprecated?)

**Recommendation**:
- Keep: `analyze_metpo_grounding*.py`, `extract_metpo_entities.py`, `find_metpo_terms.py`
- Consider consolidating or archiving the rest

---

### 3. Literature Mining Utility Scripts (9 files)

**In `literature_mining/scripts/`:**

Active utilities (✅ Keep):
- `fetch_abstracts_from_dois.py` - Abstract fetching (documented in ACKNOWLEDGMENTS)
- `extract_abstracts_from_files.py` - File extraction
- `dedupe_and_filter_abstracts.py` - Deduplication (documented)
- `dedupe_by_content.py` - Content-based dedup

Possibly redundant (⚠️ Review):
- `calculate_metrics.py` - Metrics calculation (overlaps with analysis scripts?)
- `count_extraction_results.py` - Result counting (simple utility, keep or integrate?)
- `filter_none_values.py` - None value filtering (simple utility)
- `unwrap_abstracts.py` - Abstract unwrapping (preprocessing, keep?)
- `cborg_chemical_extraction.py` - CBORG-specific extraction (one-time?)

**Recommendation**:
- Keep the fetching and dedup scripts (documented in provenance)
- Review the metric/counting scripts - could be consolidated

---

### 4. ICBO Presentation Scripts (9 files)

**In `docs/presentations/icbo_2025/figures/`:**

All 9 scripts generate figures for ICBO 2025 presentation:
- `analyze_bactotraits.py`
- `analyze_kg_microbe_metpo.py`
- `analyze_madin_etal.py`
- `analyze_ontogpt_grounding.py`
- `analyze_ontology_landscape.py`
- `analyze_primary_sources.py`
- `analyze_sssom_mappings.py`
- `calculate_minimum_import_set.py`
- `generate_feedback_loop.py`

**Status**: ✅ Keep all - documented research outputs for presentation

---

### 5. Analysis Scripts Not in CLI (4 files)

**In `metpo/analysis/`:**

Not registered as CLI commands:
- `analyze_branch_coverage_final.py` - Branch coverage analysis
- `analyze_coverage_landscape.py` - Coverage landscape
- `assess_ontology_by_api_search.py` - API search assessment
- `extract_definitions_from_mappings.py` - Definition extraction

**Recommendation**:
- These produce data files used in reports
- Consider adding CLI commands if used regularly
- Or document as "run directly with python" tools

---

### 6. Other Unregistered Scripts (2 files)

**metpo/bactotraits/analyze_sheet_overlap.py**
- Purpose: Analyze overlap between sheets
- Status: ❓ One-time analysis or recurring tool?
- Recommendation: Add to CLI or archive

**literature_mining/bacdive_chemical_utilization/visualize_ner.py**
- Purpose: NER visualization for BacDive chemicals
- Status: ❓ Experimental/exploratory
- Recommendation: Keep if used, delete if obsolete

---

## Deletion Candidates (High Confidence)

### Scripts that are likely complete one-time tasks:

1. **data/bactotraits/create_bactotraits_migration.py** - Migration complete?
2. **large/make_bacdive_utilization_enum.py** - Schema generated?
3. **literature_mining/compare_extractions.py** - One-time comparison?
4. **literature_mining/analyze_coverage_by_source_type.py** - One-time analysis?
5. **literature_mining/analyze_metpo_efficiency.py** - One-time metrics?
6. **literature_mining/scripts/cborg_chemical_extraction.py** - CBORG-specific, now complete?

### Scripts that may overlap with others:

7. **literature_mining/analyze_extractions.py** - Overlaps with analyze_metpo_grounding?
8. **literature_mining/validate_extractions.py** - Validation covered elsewhere?
9. **literature_mining/metpo_assessor.py** - Old/deprecated assessor?

---

## Consolidation Opportunities

### Metric/Counting Scripts
Could consolidate into a single `literature_mining/scripts/calculate_extraction_metrics.py`:
- `calculate_metrics.py`
- `count_extraction_results.py`
- `filter_none_values.py`

### Analysis Scripts
Could register more as CLI commands in pyproject.toml:
- `metpo/analysis/analyze_branch_coverage_final.py` → `analyze-branch-coverage`
- `metpo/analysis/analyze_coverage_landscape.py` → `analyze-coverage-landscape`
- `metpo/analysis/assess_ontology_by_api_search.py` → `assess-ontology`
- `metpo/analysis/extract_definitions_from_mappings.py` → `extract-definitions`

---

## Action Plan

1. **Ask User**: Were these migrations complete?
   - `data/bactotraits/create_bactotraits_migration.py`
   - `large/make_bacdive_utilization_enum.py`

2. **Check Git History**: When were these last used?
   - One-time analysis scripts in literature_mining/

3. **Test Deletion**: Remove candidates and verify nothing breaks
   - Run `make all-reports`
   - Run `make test-workflow`

4. **Archive vs Delete**:
   - Move to `archive/scripts/` if historical value
   - Delete if truly obsolete

5. **Register Useful Scripts**: Add CLI commands for frequently-used tools

---

## Files to Review With User

**Priority 1 (Likely Delete):**
- [ ] data/bactotraits/create_bactotraits_migration.py
- [ ] large/make_bacdive_utilization_enum.py
- [ ] literature_mining/scripts/cborg_chemical_extraction.py

**Priority 2 (Possibly Consolidate):**
- [ ] literature_mining/compare_extractions.py
- [ ] literature_mining/analyze_coverage_by_source_type.py
- [ ] literature_mining/analyze_metpo_efficiency.py
- [ ] literature_mining/analyze_extractions.py
- [ ] literature_mining/validate_extractions.py
- [ ] literature_mining/metpo_assessor.py

**Priority 3 (Register as CLI or Document):**
- [ ] metpo/bactotraits/analyze_sheet_overlap.py
- [ ] metpo/analysis/* (4 unregistered scripts)

---

**Next Steps**:
1. User confirms which scripts were one-time tasks
2. Check git log for last use dates
3. Test deletions don't break workflows
4. Create archive/ directory for historical scripts if needed

---

## Summary: Python Scripts in Wrong Locations

### Scripts Found Outside Standard Locations

**✅ Good Locations:**
- `metpo/` - Main package with organized subpackages
- `literature_mining/scripts/` - Utility scripts
- `docs/presentations/icbo_2025/figures/` - Presentation scripts (OK for docs)

**⚠️ Problematic Locations:**
- `data/bactotraits/` - Contains 1 Python script (should be data only!)
- `large/` - Contains 1 Python script mixed with 578MB reference data

**📊 Count by Directory:**
```
metpo/                      -> 46 files (✅ well-organized)
literature_mining/          -> 20 files (⚠️ could organize better)
docs/presentations/         -> 9 files (✅ OK for presentations)
data/bactotraits/           -> 1 file (❌ should not have code!)
large/                      -> 1 file (❌ should not have code!)
```

---

## Immediate Actions

### High Priority (Wrong Locations):

1. **Move or delete**: `data/bactotraits/create_bactotraits_migration.py`
   - Check if migration TSV files exist (they do: bactotraits_migration_ready.tsv)
   - If complete, DELETE
   - If needed, move to `metpo/bactotraits/`

2. **Move or delete**: `large/make_bacdive_utilization_enum.py`
   - Check if LinkML enum was generated
   - If complete, DELETE  
   - If needed, move to `metpo/tools/` or `scripts/utilities/`

### Medium Priority (Unorganized):

3. **Organize**: 11 analysis scripts in `literature_mining/` root
   - Create `literature_mining/analysis/` subdirectory?
   - Or register as CLI commands if frequently used

4. **Review**: 9 utility scripts in `literature_mining/scripts/`
   - Consolidate metric/counting scripts
   - Document which are one-time vs reusable
