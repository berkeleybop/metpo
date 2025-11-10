# Script Inventory and Improvement Plan

**Status:** Post-deletion check - 2 scripts safely deleted, all automation intact
**Goal:** Improve remaining scripts to production standards

---

## Scripts Used by Automation (DO NOT DELETE)

### Makefile Dependencies

**notebooks/ (7 scripts used by Makefile alignment targets):**
```
✅ fetch_ontology_names.py          - Makefile: alignment-fetch-ontology-names
✅ categorize_ontologies.py         - Makefile: alignment-categorize
✅ chromadb_semantic_mapper.py      - Makefile: alignment-run-semantic-mapper
✅ analyze_matches.py               - Makefile: alignment-analyze-matches
✅ analyze_sibling_coherence.py     - Makefile: alignment-analyze-coherence
✅ analyze_coherence_results.py     - Makefile: alignment-identify-candidates
✅ embed_ontology_to_chromadb.py    - Makefile: (embedded in target)
```

**metpo/scripts/ (2 scripts used by Makefile report targets):**
```
✅ bactotraits_metpo_set_difference.py  - Makefile: reports/bactotraits-metpo-set-diff.yaml
✅ reconcile_bactotraits_coverage.py    - Makefile: reports/bactotraits-metpo-reconciliation.yaml
```

**Status:** All 9 automation scripts present and accounted for

---

## Scripts with CLI Aliases in pyproject.toml (Production Tools)

```
✅ metpo/extract_rank_triples.py                      → extract-rank-triples
✅ metpo/convert_chem_props.py                        → convert-chem-props
✅ metpo/import_bactotraits.py                        → import-bactotraits
✅ metpo/scripts/reconcile_bactotraits_coverage.py    → reconcile-bactotraits-coverage
✅ metpo/scripts/reconcile_madin_coverage.py          → reconcile-madin-coverage
✅ metpo/scripts/bactotraits_metpo_set_difference.py  → bactotraits-metpo-set-difference
✅ metpo/scripts/create_bactotraits_header_mapping.py → create-bactotraits-field-mappings
✅ metpo/scripts/create_bactotraits_file_versions.py  → create-bactotraits-file-versions
✅ metpo/scripts/create_bactotraits_files.py          → create-bactotraits-files
✅ metpo/scripts/update_manifest.py                   → update-manifest
✅ metpo/scripts/scan_manifest.py                     → scan-manifest
✅ metpo/scripts/download_ontology.py                 → download-ontology
✅ metpo/scripts/query_ontology.py                    → query-ontology
```

**Status:** 13 production scripts - already meet standards

---

## Remaining Scripts to Evaluate (42 scripts)

### Category A: ChromaDB Analysis Scripts (notebooks/) - 10 remaining

**Used by Makefile (7) - Already listed above**

**Not used by Makefile (10):**
```
notebooks/analyze_branch_coverage_final.py     - Branch coverage analysis
notebooks/analyze_coverage_landscape.py        - Coverage landscape analysis
notebooks/analyze_match_quality.py             - Match quality metrics
notebooks/analyze_ontology_value.py            - ROI analysis per ontology
notebooks/audit_chromadb.py                    - Database integrity checks
notebooks/combine_chromadb.py                  - Merge ChromaDB collections
notebooks/extract_definitions_from_mappings.py - Extract definitions for METPO terms
notebooks/filter_ols_chromadb.py               - Filter OLS ontologies
notebooks/migrate_to_chromadb_resilient.py     - Migration with error handling
notebooks/phase1_batch_search.py               - Batch semantic search
```

### Category B: Literature Mining Analysis Scripts (10 main + 9 utils)

**Main analysis (10):**
```
literature_mining/analyze_coverage_by_source_type.py    - Coverage by source
literature_mining/analyze_extractions.py                - Extraction analysis
literature_mining/analyze_metpo_database_alignment.py   - Database alignment
literature_mining/analyze_metpo_efficiency.py           - Efficiency metrics
literature_mining/analyze_metpo_grounding_filtered.py   - Filtered grounding
literature_mining/analyze_metpo_grounding.py            - Main grounding analysis
literature_mining/compare_extractions.py                - Template comparison
literature_mining/extract_metpo_entities.py             - Entity extraction
literature_mining/find_metpo_terms.py                   - Term finder
literature_mining/validate_extractions.py               - Validation
```

**Utility scripts (9):**
```
literature_mining/scripts/calculate_metrics.py          - Metrics calculation
literature_mining/scripts/cborg_chemical_extraction.py  - Chemical extraction
literature_mining/scripts/count_extraction_results.py   - Count results
literature_mining/scripts/dedupe_and_filter_abstracts.py - Deduplication
literature_mining/scripts/dedupe_by_content.py          - Content dedup
literature_mining/scripts/extract_abstracts_from_files.py - PDF extraction
literature_mining/scripts/fetch_abstracts_from_dois.py  - DOI fetching
literature_mining/scripts/filter_none_values.py         - Filter nulls
literature_mining/scripts/unwrap_abstracts.py           - Format cleaning
```

**Old/unused (1):**
```
literature_mining/metpo_assessor.py                     - Aug 25, superseded?
```

### Category C: metpo/scripts/ Without CLI Aliases (3)

```
metpo/scripts/analyze_sheet_overlap.py        - Google Sheets overlap analysis
metpo/scripts/create_stubs.py                 - Class stub generator
metpo/scripts/migrate_range_metadata_v2.py    - Range metadata migration (one-time?)
```

---

## Deletion Candidates (Need Your Approval)

### Definitely Duplicates (0 found after careful review)

None found. The scripts I thought were duplicates serve different purposes:
- `analyze_branch_coverage.py` vs `analyze_branch_coverage_final.py` - DELETED (final supersedes)
- `analyze_coherence_results.py` vs `analyze_sibling_coherence.py` - DIFFERENT (kept both)
- `fetch_doi_abstracts.py` vs `fetch_abstracts_from_dois.py` - DELETED (duplicate)

### Possibly Superseded (Need verification)

```
literature_mining/metpo_assessor.py (Aug 25)
  - Is this superseded by analyze_metpo_grounding.py (Nov 7)?
  - ACTION: Compare functionality before deciding
```

```
metpo/scripts/migrate_range_metadata_v2.py
  - Was this a one-time migration?
  - Is the migration complete?
  - ACTION: Check if still needed
```

### Possibly One-Off Data Prep (Need verification)

```
literature_mining/scripts/dedupe_and_filter_abstracts.py
literature_mining/scripts/dedupe_by_content.py
literature_mining/scripts/extract_abstracts_from_files.py
literature_mining/scripts/unwrap_abstracts.py
literature_mining/scripts/filter_none_values.py
  - Were these one-time data preparation?
  - Are abstracts already clean?
  - ACTION: Check if data prep is complete
```

```
literature_mining/scripts/cborg_chemical_extraction.py (Aug 25)
  - Superseded by OntoGPT templates?
  - ACTION: Verify not used anywhere
```

---

## Improvement Plan for Scripts We're Keeping

### Phase 1: Add Click CLIs to Makefile-Used Scripts (7 scripts)

These are already used by Makefile but lack proper CLI interfaces:

**Priority 1 (Used in automation):**
```
notebooks/fetch_ontology_names.py
notebooks/categorize_ontologies.py
notebooks/chromadb_semantic_mapper.py
notebooks/analyze_matches.py
notebooks/analyze_sibling_coherence.py
notebooks/analyze_coherence_results.py ✅ Already has Click
notebooks/embed_ontology_to_chromadb.py
```

**Actions:**
1. Add Click CLI to each (if missing)
2. Add CLI alias to pyproject.toml
3. Update Makefile to use CLI alias instead of direct python call
4. Test each Makefile target

### Phase 2: Add Click CLIs to Valuable Analysis Scripts (Priority order)

**High value - frequently rerun:**
```
notebooks/extract_definitions_from_mappings.py   - Generates ICBO data
notebooks/analyze_ontology_value.py              - ROI analysis
literature_mining/analyze_metpo_grounding.py     - Main grounding
```

**Medium value - occasionally rerun:**
```
notebooks/analyze_branch_coverage_final.py
notebooks/analyze_coverage_landscape.py
notebooks/audit_chromadb.py
literature_mining/compare_extractions.py
literature_mining/validate_extractions.py
```

**Low value - rare rerun:**
```
notebooks/combine_chromadb.py
notebooks/filter_ols_chromadb.py
notebooks/migrate_to_chromadb_resilient.py
literature_mining/analyze_metpo_efficiency.py
literature_mining/find_metpo_terms.py
```

### Phase 3: Consolidate metpo/scripts/

Move scripts without CLI aliases:
```
metpo/scripts/analyze_sheet_overlap.py  → analysis_archive/
metpo/scripts/create_stubs.py           → analysis_archive/ (or add CLI if still used)
metpo/scripts/migrate_range_metadata_v2.py → analysis_archive/ (if migration complete)
```

---

## Questions for You

Before proceeding, I need your input on:

1. **metpo_assessor.py (Aug 25)** - Is this superseded by analyze_metpo_grounding.py? Can we delete it?

2. **Data prep scripts (5 files)** - Are these one-time scripts? Abstracts already clean?
   - dedupe_and_filter_abstracts.py
   - dedupe_by_content.py
   - extract_abstracts_from_files.py
   - unwrap_abstracts.py
   - filter_none_values.py

3. **cborg_chemical_extraction.py** - Superseded by OntoGPT? Safe to delete?

4. **migrate_range_metadata_v2.py** - Migration complete? Safe to archive?

5. **Priority for adding CLIs** - Which scripts do you want Click CLIs added to first?

---

## Next Steps (Awaiting Your Approval)

1. You review questions above and tell me what to delete
2. I verify no automation uses those scripts
3. I delete with your explicit approval
4. I add Click CLIs to scripts you prioritize
5. I update pyproject.toml with new CLI aliases
6. I update Makefile to use CLI aliases
7. I test all automation still works

**No more mistakes. Every action approved by you first.**
