# ChromaDB and Qdrant Status - METPO Vector Search

**Date:** 2025-11-06
**Purpose:** Document decisions and status of vector search infrastructure for METPO semantic mapping

---

## Executive Summary

### ✅ **DECIDED: ChromaDB is the official vector database**

- **Decision made:** October 31, 2025 (PR #278 merged, Issue #277 closed)
- **Qdrant status:** Evaluated but abandoned due to memory issues
- **Current state:** ChromaDB fully implemented with optimized 24-ontology corpus
- **Location:** `/home/mark/gitrepos/metpo/notebooks/chroma_*` directories

### 🎯 **Current Vector Search Infrastructure**

**Active ChromaDB Database:** `chroma_ols20_nonols4/`
- **24 ontologies** (20 OLS + 4 non-OLS)
- **452,942 embeddings** (reduced from 778,496)
- **1536 dimensions** (OpenAI text-embedding-3-small)
- **Size:** 648 MB (down from 1.3 GB)

**Performance Optimizations:**
- Removed 15 low-value ontologies (41.8% corpus reduction)
- **ROI improved +67%** (1.69 → 2.82 good matches per 1000 embeddings)
- **97.6% match retention** (kept 1,282 of 1,314 good matches)

---

## The Vector Database Decision Timeline

### Phase 1: Initial Exploration (Earlier 2025)

**Problem:** Need to search 255 METPO terms against 773K+ ontology embeddings from OLS

**Evaluated Options:**
1. **ChromaDB** - Python-native, SQLite-backed, HNSW index
2. **Qdrant** - Rust-based, specialized for production scale
3. **Faiss** - Facebook's library, requires more manual work
4. **Brute-force NumPy** - Simple but slow

### Phase 2: Qdrant Trial (Mid-2025)

**Attempted:** Migrate 9.57M embeddings (full OLS dataset) to Qdrant

**Result:** FAILED due to memory constraints
- Migration worked (sequential writes)
- Querying crashed (HNSW index load required 62GB+ RAM)
- Projected RAM for full dataset: **750GB+**
- **Conclusion:** Not suitable for local machine

**Evidence:** `docs/vector_search_analysis.md`

### Phase 3: ChromaDB Migration (Oct 2025)

**Approach:**
1. Migrate subset (27 OLS ontologies, 768K embeddings) to ChromaDB
2. Add 13 non-OLS ontologies from BioPortal (10K embeddings)
3. Combine into single database (778K embeddings)

**Result:** ✅ SUCCESS
- Full migration completed
- Query performance acceptable for batch processing
- Much lower memory footprint than Qdrant

**Evidence:** `docs/chromadb_audit_report.md`

### Phase 4: Optimization (Oct 31, 2025)

**Discovery:** ROI analysis revealed massive waste
- CHEBI (221K embeddings, 28% of corpus) → only 2 good METPO matches
- ROI: 0.009 matches per 1000 embeddings (worst performer)
- 15 ontologies provided <1% of value

**Action:** Remove low-ROI ontologies
- Kept 24 highest-value ontologies
- Reduced corpus 41.8% (778K → 453K embeddings)
- Improved ROI +67%
- Lost only 2.4% of good matches

**Evidence:** `docs/ontology_removal_recommendation.md`, `docs/ONTOLOGY_SELECTION_SUMMARY.md`

### Phase 5: Finalization (Oct 31, 2025)

**Decision:** ChromaDB is official, remove Qdrant scripts
- **PR #278 merged:** "Finalize ChromaDB as vector DB and remove Qdrant migration scripts"
- **Issue #277 closed:** "Finalize vector DB choice and remove unused migration scripts"
- Qdrant scripts deleted
- `.gitignore` updated to remove Qdrant patterns

---

## ChromaDB Infrastructure Status

### Active Databases

**Location:** `/home/mark/gitrepos/metpo/notebooks/`

| Database | Ontologies | Embeddings | Size | Status |
|----------|------------|------------|------|--------|
| `chroma_combined/` | 39 (27 OLS + 12 non-OLS) | 778,496 | 1.3 GB | Archive (superseded) |
| `chroma_ols_27/` | 27 (OLS only) | 768,323 | Not listed | Archive |
| `chroma_ols_20/` | 20 (OLS filtered) | ~449,319 | 671 MB | Intermediate |
| `chroma_nonols_4/` | 4 (non-OLS re-embedded) | ~3,623 | 11 MB | Intermediate |
| **`chroma_ols20_nonols4/`** | **24 (optimized)** | **~452,942** | **648 MB** | **✅ PRODUCTION** |

### Ontology Composition

**20 OLS Ontologies Kept:**
- **Top performers (ROI > 2.0):** micro (34.63), flopo (4.30), ecocore (5.42), envo (2.72), mco (3.15), cmpo (2.65)
- **Efficient small ontologies:** pco (11.49), exo (11.43), geo (10.20), biolink (9.24), omp (8.21), apo (6.19), ohmi (5.63)
- **Moderate ROI:** pato (1.55), eco (1.45), phipo (1.16), eupath (1.11)
- **High volume exceptions:** oba (0.94), upheno (0.80), go (0.33) - kept despite low ROI due to >60 good matches

**4 Non-OLS Ontologies Kept:**
- **n4l_merged** (ROI: 167.40!) - Names for Life, microbial phenotypes - STAR PERFORMER
- **d3o** (ROI: 21.20) - DSMZ 3D structures, has GC content terms
- **miso** (ROI: 15.50) - DSMZ microbial survey
- **meo** (ROI: 6.00) - Metadata hub microbiology

**15 Ontologies Removed:**
- **OLS (7):** chebi, foodon, cl, fypo, ecto, aro, ddpheno
- **Non-OLS (8):** omp (duplicate), gmo, bipon, mpo, id-amr, ofsmr, fmpm, typon, mccv

### Key Scripts

**Active (Keep):**
- `chromadb_semantic_mapper.py` - Core mapping tool
- `audit_chromadb.py` - Database integrity verification
- `combine_chromadb.py` - Merge multiple ChromaDBs
- `filter_ols_chromadb.py` - Filter OLS database by ontology list
- `embed_ontology_to_chromadb.py` - Embed new ontologies
- `analyze_ontology_value.py` - ROI analysis
- `analyze_match_quality.py` - Match quality metrics

**Removed (Qdrant):**
- ~~`migrate_to_qdrant_resilient.py`~~ - Deleted
- ~~`query_metpo_terms_qdrant.py`~~ - Deleted
- ~~`cleanup_qdrant.sh`~~ - No longer needed

---

## Problems That Remain

### 🔴 **CRITICAL: ChromaDB peek() Failure**

**Issue:** `collection.peek()` fails after HNSW index rebuild

**Status:** UNRESOLVED - Documented in `docs/CHROMADB_PEEK_ISSUE.md`

**Symptoms:**
- `collection.peek(limit=N)` → "Error finding id"
- `collection.count()` → Works fine
- `collection.query()` → Works fine
- `collection.get()` → Works fine

**Impact:** LOW - peek() not needed for semantic mapping workflow

**Workarounds:**
- Use `collection.get(limit=N)` instead of `peek(N)`
- Use `collection.query()` for exploration

**Root Cause:** Suspected issue with internal ID mapping after HNSW index rebuild

**Next Steps:**
- Document as known limitation
- Consider reporting to ChromaDB project
- Not blocking for METPO work

### ⚠️ **MEDIUM: Full OLS Dataset (9.57M embeddings) Not Migrated**

**Current State:**
- Only 27 of 273 OLS ontologies migrated (8% of total)
- Full dataset: 288GB SQLite, 9.57M embeddings
- Current migration: 453K embeddings (4.7% of total)

**Why Not Migrated:**
- Memory constraints (would require 750GB+ RAM for HNSW)
- Diminishing returns (top 24 ontologies provide 97.6% of value)
- Processing time (hours per query on full dataset)

**Options:**
1. **Status quo (RECOMMENDED):** 24 ontologies sufficient for METPO
2. **Cloud vector DB:** Qdrant Cloud or Pinecone (~$200-500/month)
3. **Faiss with quantization:** More memory-efficient but still risky
4. **Brute-force NumPy:** Works but slow (5-10 sec per query)

**Decision:** Keep current 24-ontology setup unless specific use case requires more

### ⚠️ **MEDIUM: OMP Duplication Resolved**

**Problem (RESOLVED):** OMP appeared in both OLS and BioPortal sources
- OLS version: 2,440 embeddings
- Non-OLS version: 2,309 embeddings (99.5% overlap)
- **Issue:** Different IRI formats (angle brackets in non-OLS)

**Solution:**
- Kept OLS version only
- Removed non-OLS duplicate
- Fixed IRI format inconsistency in remaining 4 non-OLS ontologies

**Status:** ✅ RESOLVED in optimized database

### ⚠️ **LOW: Non-OLS IRI Format Inconsistency**

**Problem (RESOLVED):** Non-OLS embeddings had angle brackets in IRIs
- Example: `<http://doi.org/10.1601/...>` instead of `http://doi.org/10.1601/...`
- Caused deduplication issues

**Solution:**
- Re-embedded 4 non-OLS ontologies with corrected IRI format
- Cost: ~$0.02 OpenAI API
- Database: `chroma_nonols_4/`

**Status:** ✅ RESOLVED in optimized database

---

## METPO Semantic Mapping Results

### Mappings Generated

**File:** `notebooks/metpo_mappings_combined_relaxed.sssom.tsv`

**Settings:**
- Distance cutoff: <0.80 (relaxed for analysis)
- Top-N: 20 matches per term
- Total mappings: 3,008

**Quality Distribution:**
- **Excellent (<0.35):** 328 mappings - ready for auto-integration
- **Good (0.35-0.60):** 954 mappings - manual review queue
- **Fair (0.60-0.80):** 1,726 mappings - exploratory only

**Usage for ICBO:**
- **High-confidence definitions:** 9 terms ready for auto-proposal
- **Definition sources:** 54 terms need sources added
- **Cross-references:** 158 terms have skos:closeMatch candidates

**Evidence:** `notebooks/definition_proposals.tsv`, `notebooks/high_confidence_definitions.tsv`

---

## GitHub Issues Status

### Open Issues

**#255** - Consider alternatives to ChromaDB like linkml-store
- **Status:** SUPERSEDED by ChromaDB finalization
- **Action:** Can be closed with note that ChromaDB was chosen

**#256** - Does composition of OLS embeddings limit usefulness?
- **Question:** OLS embeddings use label+description+synonyms but NOT parent class
- **Status:** Open question, not blocking
- **Impact:** May affect hierarchical reasoning

**#258** - Create OLS-style embeddings for non-OLS ontologies
- **Status:** COMPLETED for 4 ontologies kept (n4l_merged, d3o, miso, meo)
- **Action:** Can be closed or updated with completion status

### Closed Issues

**#277** - Finalize vector DB choice and remove unused migration scripts
- **Status:** CLOSED (Oct 31, 2025)
- **Resolution:** ChromaDB chosen, Qdrant scripts removed

**#278** - (Merged PR) Finalize ChromaDB as vector DB and remove Qdrant migration scripts
- **Status:** MERGED (Oct 31, 2025)
- **Changes:** Deleted Qdrant scripts, updated .gitignore

**#275** - (Merged PR) Enhance non-OLS ontology pipeline with ChromaDB integration
- **Status:** MERGED
- **Changes:** Added non-OLS embedding and analysis tools

---

## Recommendations for ICBO Talk

### What to Emphasize

1. **Pragmatic approach to semantic search:**
   - Started with 9.57M embeddings (impractical locally)
   - Optimized to 453K embeddings (4.7% of original)
   - **Lost only 2.4% of value** (97.6% match retention)
   - **Improved ROI by 67%**

2. **Data-driven ontology selection:**
   - ROI-based removal decisions
   - Small, domain-specific ontologies outperform large general ones
   - n4l_merged (454 embeddings) → 167 ROI vs CHEBI (221K embeddings) → 0.009 ROI

3. **Hybrid curation approach:**
   - Automated semantic search (ChromaDB + OpenAI embeddings)
   - ROI-based filtering
   - Manual quality assessment
   - 328 high-confidence matches (<0.35 distance)

### What NOT to Mention

- ❌ Qdrant evaluation failure (technical dead-end)
- ❌ ChromaDB peek() issue (minor technical glitch)
- ❌ IRI format issues (implementation details)

### Key Statistics for Abstract/Slides

- **778K → 453K embeddings** (41.8% reduction, 97.6% value retention)
- **39 → 24 ontologies** (removed 15 low-ROI ontologies)
- **ROI improved +67%** (1.69 → 2.82 good matches per 1000 embeddings)
- **3,008 semantic mappings** across 24 ontologies
- **328 high-confidence mappings** (distance <0.35)
- **158 METPO terms** have cross-references ready for integration

---

## Next Steps for ICBO Preparation

### High Priority (Definition Work)

1. **Mine EuropePMC/IJSEM for trait definitions** ⭐
   - 13,925 IJSEM bacterial species descriptions
   - 417,862 text-mined organism annotations
   - Query for METPO terms needing definitions
   - Use PMIDs as authoritative sources

2. **Add definition sources to 54 terms** (1-2 hours)
   - File: `notebooks/definition_sources_needed.tsv`
   - Use semantic matches to assign IAO:0000119 sources

3. **Add 9 high-confidence definitions** (30 minutes)
   - File: `notebooks/high_confidence_definitions.tsv`
   - Terms ready for auto-proposal

4. **Integrate 158 cross-references** (1 hour)
   - File: `notebooks/metpo_cross_references.tsv`
   - Add skos:closeMatch annotations to OWL

### Medium Priority (Documentation)

5. **Update GitHub issue statuses**
   - Close #255 (ChromaDB finalized)
   - Update #258 (non-OLS embeddings completed)
   - Document #256 decision (defer or close)

6. **Update ICBO_PREP.md with ChromaDB stats**
   - Add ROI improvement numbers
   - Add semantic mapping statistics
   - Reference this document

### Low Priority (Cleanup)

7. **Archive old ChromaDB databases**
   - Move `chroma_combined/`, `chroma_ols_27/` to archive directory
   - Keep `chroma_ols20_nonols4/` as production

8. **Consider closing ChromaDB peek() issue**
   - Document as known limitation
   - Not blocking for METPO workflow
   - Report to ChromaDB project if desired

---

## File Locations Quick Reference

### Documentation
- **This file:** `/home/mark/gitrepos/metpo/docs/icbo_2025_prep/CHROMADB_QDRANT_STATUS.md`
- **ChromaDB audit:** `/home/mark/gitrepos/metpo/docs/chromadb_audit_report.md`
- **Ontology selection:** `/home/mark/gitrepos/metpo/docs/ONTOLOGY_SELECTION_SUMMARY.md`
- **ROI analysis:** `/home/mark/gitrepos/metpo/docs/ontology_removal_recommendation.md`
- **Vector search analysis:** `/home/mark/gitrepos/metpo/docs/vector_search_analysis.md`
- **ChromaDB peek issue:** `/home/mark/gitrepos/metpo/docs/CHROMADB_PEEK_ISSUE.md`

### Active Databases
- **Production:** `/home/mark/gitrepos/metpo/notebooks/chroma_ols20_nonols4/` (648 MB, 24 ontologies)
- **OLS filtered:** `/home/mark/gitrepos/metpo/notebooks/chroma_ols_20/` (671 MB, 20 ontologies)
- **Non-OLS:** `/home/mark/gitrepos/metpo/notebooks/chroma_nonols_4/` (11 MB, 4 ontologies)

### Semantic Mapping Results
- **Relaxed mappings:** `/home/mark/gitrepos/metpo/notebooks/metpo_mappings_combined_relaxed.sssom.tsv` (3,008 mappings)
- **Definition proposals:** `/home/mark/gitrepos/metpo/notebooks/definition_proposals.tsv` (256 terms analyzed)
- **High-confidence defs:** `/home/mark/gitrepos/metpo/notebooks/high_confidence_definitions.tsv` (9 ready)
- **Definition sources needed:** `/home/mark/gitrepos/metpo/notebooks/definition_sources_needed.tsv` (54 terms)
- **Cross-references:** `/home/mark/gitrepos/metpo/notebooks/metpo_cross_references.tsv` (158 terms)

### Scripts
- **Semantic mapper:** `/home/mark/gitrepos/metpo/notebooks/chromadb_semantic_mapper.py`
- **Database audit:** `/home/mark/gitrepos/metpo/notebooks/audit_chromadb.py`
- **ROI analysis:** `/home/mark/gitrepos/metpo/notebooks/analyze_ontology_value.py`

---

## Questions Answered

### Why ChromaDB over Qdrant?
- **Qdrant failed** due to memory constraints (62GB+ for 8% of data)
- **ChromaDB succeeded** with acceptable performance and memory usage
- **Pragmatic choice** - works on local machine, good enough for batch processing

### Why only 24 ontologies (4.7% of full OLS)?
- **ROI-based filtering** showed 41% of corpus provided <1% of value
- **97.6% value retention** despite 41.8% size reduction
- **Diminishing returns** - remaining ontologies unlikely to improve results
- **Memory/time constraints** - full dataset requires cloud infrastructure

### What about the full 9.57M embeddings?
- **Not needed for METPO** - 24 ontologies provide sufficient coverage
- **Could migrate if needed** - via cloud vector DB (~$200-500/month)
- **Alternative approach** - query OLS API directly for specific lookups

### Is ChromaDB peek() issue blocking?
- **No** - peek() not used in semantic mapping workflow
- **Workaround exists** - use get(limit=N) instead
- **Low priority** - can be reported to ChromaDB project or ignored

---

**Last Updated:** 2025-11-06
**Status:** FINALIZED - ChromaDB is official vector database
**Next Action:** Use semantic mappings for METPO definition work (EuropePMC mining)
