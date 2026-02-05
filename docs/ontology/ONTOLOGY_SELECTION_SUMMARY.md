# Ontology Selection Summary for METPO Semantic Mapping

**Last Updated:** 2025-10-31
**Status:** Final decisions made, implementation in progress

## Quick Reference

**Final Configuration:**
- **24 ontologies kept** (20 OLS + 4 non-OLS)
- **15 ontologies removed** (7 OLS + 8 non-OLS)
- **Corpus reduced 41.8%** (778,496 → 452,942 embeddings)
- **Match retention: 97.6%** (keep 1,282 of 1,314 good matches)
- **ROI improvement: +67%** (1.69 → 2.82 good matches per 1000 embeddings)

## Databases

### Source Databases (Original)
- `chroma_ols_27/` - 768,323 embeddings, 27 OLS ontologies
- `embeddings_chroma/` - 10,173 embeddings, 13 non-OLS ontologies (BioPortal)
- `chroma_combined/` - 778,496 embeddings, 39 ontologies (OLS + non-OLS combined)

### Optimized Databases (New)
- `chroma_ols_20/` - ~449,319 embeddings, 20 OLS ontologies (filtered)
- `chroma_nonols_4/` - ~3,623 embeddings, 4 non-OLS ontologies (re-embedded, IRI format fixed)
- `chroma_24/` - ~452,942 embeddings, 24 ontologies (final optimized)

## Decision Criteria

**ROI (Return on Investment):** Good matches (distance < 0.60) per 1,000 embeddings

**Removal Thresholds:**
- ROI < 0.50 AND good matches < 20, OR
- Zero good matches

**Keep Thresholds:**
- ROI >= 1.0, OR
- ROI >= 0.5 AND good matches >= 10, OR
- Good matches >= 20 (high volume)

## Ontologies KEPT (24 total)

### OLS Ontologies (20)

**High ROI (ROI > 2.0):**
| Ontology | Embeddings | Good Matches | ROI | Description |
|----------|------------|--------------|-----|-------------|
| micro | 17,645 | 611 | 34.63 | Microbial ecology - PRIMARY SOURCE |
| flopo | 35,359 | 152 | 4.30 | Flora phenotype |
| ecocore | 6,086 | 33 | 5.42 | Ecological core |
| envo | 7,365 | 20 | 2.72 | Environment ontology |
| mco | 3,491 | 11 | 3.15 | Microbial conditions |
| cmpo | 1,134 | 3 | 2.65 | Cellular microscopy |

**Moderate ROI (1.0 - 2.0):**
| Ontology | Embeddings | Good Matches | ROI | Description |
|----------|------------|--------------|-----|-------------|
| pato | 9,061 | 14 | 1.55 | Phenotype attributes |
| eco | 3,449 | 5 | 1.45 | Evidence codes |
| phipo | 4,327 | 5 | 1.16 | Pathogen-host interaction |
| eupath | 5,406 | 6 | 1.11 | Eukaryotic pathogen |

**Small but Efficient (ROI > 6.0):**
| Ontology | Embeddings | Good Matches | ROI | Description |
|----------|------------|--------------|-----|-------------|
| pco | 435 | 5 | 11.49 | Population & community |
| exo | 175 | 2 | 11.43 | Experimental conditions |
| geo | 196 | 2 | 10.20 | Geographical |
| biolink | 974 | 9 | 9.24 | Semantic model |
| omp | 2,440 | 39 | 8.21 | Microbial phenotypes (OLS only) |
| apo | 646 | 4 | 6.19 | Ascomycete phenotypes |
| ohmi | 1,244 | 7 | 5.63 | Host-microbe interactions |

**High Volume (>60 good matches, lower ROI):**
| Ontology | Embeddings | Good Matches | ROI | Description |
|----------|------------|--------------|-----|-------------|
| oba | 73,148 | 69 | 0.94 | Biological attributes |
| upheno | 192,001 | 154 | 0.80 | Unified phenotype |
| go | 84,737 | 28 | 0.33 | Gene Ontology |

### Non-OLS Ontologies (4)

**All High ROI:**
| Ontology | Embeddings | Good Matches | ROI | Description | Source |
|----------|------------|--------------|-----|-------------|--------|
| n4l_merged | 454 | 76 | 167.40 | Microbial phenotypes | doi.org/10.1601 |
| d3o | 283 | 6 | 21.20 | DSMZ microbiology (GC content!) | purl.dsmz.de |
| miso | 387 | 6 | 15.50 | DSMZ microbial survey | purl.dsmz.de |
| meo | 2,499 | 15 | 6.00 | Metadata hub microbiology | mdatahub.org |

**Note:** These 4 will be **re-embedded** to fix IRI format inconsistency (remove angle brackets).

## Ontologies REMOVED (15 total)

### OLS Ontologies Removed (7)

| Ontology | Embeddings | Good Matches | ROI | Reason for Removal |
|----------|------------|--------------|-----|-------------------|
| chebi | 221,776 | 2 | 0.009 | WORST ROI - chemicals not phenotypes |
| foodon | 40,123 | 9 | 0.224 | Food ontology, low microbial relevance |
| cl | 17,521 | 6 | 0.342 | Cell types, not phenotypes |
| fypo | 17,232 | 7 | 0.406 | Fission yeast phenotypes |
| ecto | 12,404 | 5 | 0.403 | Environmental exposures |
| aro | 8,551 | 0 | 0.000 | Zero good matches |
| ddpheno | 1,397 | 0 | 0.000 | Zero matches |
| **TOTAL** | **319,004** | **29** | **0.091** | **41.2% of OLS corpus** |

### Non-OLS Ontologies Removed (8)

| Ontology | Embeddings | Good Matches | ROI | Reason for Removal |
|----------|------------|--------------|-----|-------------------|
| omp (non-OLS) | 2,309 | N/A | N/A | **DUPLICATE** - 99.5% overlap with OLS OMP |
| gmo | 1,557 | 0 | 0.000 | Zero good matches |
| bipon | 1,746 | 1 | 0.573 | Only 1 CHEBI import |
| mpo | 320 | 0 | 0.000 | Zero matches |
| id-amr | 271 | 2 | 7.380 | Only 2 matches total |
| ofsmr | 157 | 0 | 0.000 | Zero matches |
| fmpm | 155 | 0 | 0.000 | Zero matches |
| typon | 19 | 0 | 0.000 | Zero matches |
| mccv | 16 | 0 | 0.000 | Zero matches |
| **TOTAL** | **6,550** | **3** | **0.458** | **64.4% of non-OLS corpus** |

## Special Cases

### CHEBI - The Paradox

**Largest ontology removed:**
- 221,776 embeddings (28.5% of entire corpus)
- Only 2 good METPO matches (distance < 0.60)
- ROI: 0.009 - worst in entire collection

**Why so bad?** METPO is about microbial **phenotypes**, not chemical entities. Chemical entities appear in METPO mappings via context from other ontologies (GO, ENVO, etc.), but standalone CHEBI embeddings ("glucose", "phosphate") don't match phenotypes.

**Safe to remove?** Yes - the ontologies importing CHEBI that matched METPO (ecto, bipon) are also being removed.

### OMP - The Duplicate

**Appeared in both OLS and BioPortal:**
- OLS OMP: 2,440 embeddings (131 unique terms)
- Non-OLS OMP: 2,309 embeddings (0 unique terms, 99.5% overlap)

**IRI format difference:**
- OLS: `http://purl.obolibrary.org/obo/PATO_0000586`
- Non-OLS: `<http://purl.obolibrary.org/obo/PATO_0000586>` ← angle brackets!

**Decision:** Keep OLS version only (more complete, clean IRIs).

### N4L_MERGED - The Star

**Best ROI of any ontology:**
- Only 454 embeddings (0.06% of corpus)
- Provides 76 good matches (<0.60)
- ROI: 167.40 - 10x better than second place
- Covers 72 unique METPO terms

**Lesson:** Small, domain-specific ontologies can outperform large, general ones.

## IRI Format Standardization

**Problem Discovered:** Non-OLS embeddings have angle brackets in IRIs:
- `<http://doi.org/10.1601/...>`
- `<https://purl.dsmz.de/schema/...>`
- `<https://mdatahub.org/data/meo/...>`

**OLS Format (Standard):** Plain URIs without angle brackets:
- `http://purl.obolibrary.org/obo/...`

**Solution:** Re-embed the 4 non-OLS ontologies we're keeping (n4l_merged, d3o, meo, miso) with corrected IRI format.

**Cost:** ~$0.02 OpenAI API, ~5 minutes

**Future Standard:** All IRIs must be plain URIs without angle brackets.

## Distance Thresholds

Based on relaxed analysis (0.80 cutoff) vs strict (0.35 cutoff):

**For Production SSSOM Output:**
- **Distance < 0.60** - Recommended for balanced precision/recall
- Captures 1,282 good matches
- Filters out low-quality matches

**For High-Confidence Automation:**
- **Distance < 0.35** - Use for automated integration
- 328 excellent matches
- 71% precision (from manual validation)

**For Manual Review Queue:**
- **Distance 0.35 - 0.60** - Human curator review
- 954 matches requiring manual assessment
- May include valuable domain-specific matches

## Analysis History

### Analyses Performed

1. **Initial Combined Analysis** (distance < 0.35, top-10)
   - Result: 328 mappings across 21 ontologies
   - File: `metpo_mappings_combined.sssom.tsv`
   - Analysis: `ontology_value_analysis_combined.txt`

2. **Relaxed Analysis** (distance < 0.80, top-20)
   - Result: 3,008 mappings across 33 ontologies
   - File: `metpo_mappings_combined_relaxed.sssom.tsv`
   - Analysis: `ontology_value_analysis_relaxed.txt`
   - **Used for final ROI decisions**

3. **Match Quality Analysis**
   - Script: `analyze_match_quality.py`
   - Revealed most non-OLS ontologies have poor distance quality

4. **ChromaDB Audit** (full scan, no sampling)
   - Script: `audit_chromadb.py`
   - Result: `chromadb_audit_results.txt`
   - Report: `chromadb_audit_report.md`
   - Confirmed all 39 ontologies present, 778,496 embeddings

### Earlier Analysis (Superseded)

- `ontology_source_value_analysis.md` - Based on earlier, incomplete data (26 ontologies)
- **Status:** Superseded by `ontology_removal_recommendation.md`

## Implementation Plan

### Phase 1: Filter OLS ChromaDB ✓ IN PROGRESS
**Script:** `filter_ols_chromadb.py`
```bash
uv run python filter_ols_chromadb.py
```
- Input: `chroma_ols_27/` (27 ontologies, 768,323 embeddings)
- Output: `chroma_ols_20/` (20 ontologies, ~449,319 embeddings)
- Removes: chebi, foodon, cl, fypo, ecto, aro, ddpheno

### Phase 2: Re-embed 4 Non-OLS Ontologies (TODO)
**Script:** Find and fix the non-OLS embedding script
- Fix IRI format (remove angle brackets)
- Re-embed: n4l_merged, d3o, meo, miso
- Output: `chroma_nonols_4/` (4 ontologies, ~3,623 embeddings)

### Phase 3: Combine into Final ChromaDB (TODO)
**Script:** `combine_chromadb.py` (reuse existing)
- Input: `chroma_ols_20/` + `chroma_nonols_4/`
- Output: `chroma_24/` (24 ontologies, ~452,942 embeddings)

### Phase 4: Generate Production Mappings (TODO)
**Script:** `chromadb_semantic_mapper.py`
```bash
uv run python chromadb_semantic_mapper.py \
    --metpo-tsv ../src/templates/metpo_sheet.tsv \
    --chroma-path ./chroma_24 \
    --collection-name combined_embeddings \
    --output metpo_mappings_final.sssom.tsv \
    --top-n 20 \
    --label-only \
    --distance-cutoff 0.60
```
Expected: ~1,282 mappings

## Files to Keep

### Documentation (Keep)
- ✓ `ONTOLOGY_SELECTION_SUMMARY.md` - This file (master reference)
- ✓ `ontology_removal_recommendation.md` - Detailed ROI analysis
- ✓ `chromadb_audit_report.md` - Database integrity verification
- ✓ `vector_search_analysis.md` - Label-only vs label+parents comparison

### Scripts (Keep - Active Use)
- ✓ `chromadb_semantic_mapper.py` - Core semantic mapping tool
- ✓ `audit_chromadb.py` - Database audit/verification
- ✓ `analyze_ontology_value.py` - Native vs imported analysis
- ✓ `analyze_match_quality.py` - ROI calculation
- ✓ `analyze_sibling_coherence.py` - Structural alignment analysis
- ✓ `analyze_matches.py` - General match analysis
- ✓ `analyze_coherence_results.py` - Coherence results analysis
- ✓ `combine_chromadb.py` - Database merging
- ✓ `filter_ols_chromadb.py` - OLS filtering (new)

### Data Files (Keep - Reference)
- ✓ `metpo_mappings_combined_relaxed.sssom.tsv` - Used for final ROI decisions
- ✓ `chromadb_audit_results.txt` - Full database audit
- ✓ `ontology_value_analysis_relaxed.txt` - ROI analysis output

## Files to REMOVE

### Superseded Documentation
- ❌ `ontology_source_value_analysis.md` - Superseded by ontology_removal_recommendation.md
- ❌ `ontology_value_analysis_combined.txt` - Used strict cutoff, less informative

### Throwaway Scripts
- ❌ `test_gc_query.py` - One-off test for GC content
- ❌ `check_chromadb_ontologies.py` - Superseded by audit_chromadb.py
- ❌ `create_optimized_chromadb.py` - Incomplete, abandoned due to OMP duplication discovery
- ❌ `sanity_check_non_ols.py` - One-off sanity check
- ❌ `analyze_iri_duplicates.py` - One-off IRI analysis

### Superseded Data Files
- ❌ `metpo_mappings_combined.sssom.tsv` - Strict cutoff version, superseded by relaxed
- ❌ `metpo_mappings.sssom.tsv` - Earlier version before combined database

## Lessons Learned

1. **ROI is better than absolute count** - Small, focused ontologies (n4l_merged: 454 embeddings, ROI 167) outperform large, general ones (CHEBI: 221k embeddings, ROI 0.009)

2. **Domain alignment matters** - METPO is about phenotypes. Chemical entities, cell types, and food terms have low relevance.

3. **Deduplication is critical** - OMP appeared in both sources with 99.5% overlap but different IRI formats.

4. **IRI format consistency matters** - Angle brackets in non-OLS IRIs break deduplication and matching.

5. **Sample first, then decide** - Relaxed analysis (distance < 0.80) was necessary to see full picture before setting thresholds.

6. **Manual validation reveals edge cases** - Distance alone insufficient; semantic issues like negations and over-specificity affect match quality.

## Future Maintenance

**When to re-evaluate:**
- After major METPO updates (new term categories)
- Annually (ontology content evolves)
- When new domain-specific ontologies become available

**Re-evaluation process:**
1. Run semantic mapper with relaxed cutoff (0.80, top-20)
2. Calculate ROI for all ontologies
3. Apply same decision thresholds (ROI > 0.5 or matches > 20)
4. Document changes

**Quality checks:**
- Verify IRI format consistency (no angle brackets)
- Check for duplicate ontologies across sources
- Audit total embedding count matches expectations
- Sample mappings to verify quality

## Questions?

See detailed analysis in:
- `ontology_removal_recommendation.md` - Full ROI analysis with examples
- `chromadb_audit_report.md` - Database integrity and verification
- `vector_search_analysis.md` - Distance threshold analysis
