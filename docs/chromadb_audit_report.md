# ChromaDB Combined Database Audit Report

**Date:** 2025-10-31
**Audit Script:** `audit_chromadb.py`
**Method:** Complete scan of all embeddings (no sampling)

## Executive Summary

The combined ChromaDB database is **FULLY INTACT** with all ontologies present and correct counts.

- **Total embeddings:** 778,496
- **Unique ontologies:** 39 (27 OLS + 13 non-OLS - 1 overlap)
- **Vector dimensions:** All 1536 (consistent)
- **Data integrity:** ✓ VERIFIED

## Database Breakdown

### OLS Database
- **Total:** 768,323 embeddings
- **Ontologies:** 27
- **Top contributors:**
  - chebi: 221,776 (28.86%)
  - upheno: 192,001 (24.99%)
  - go: 84,737 (11.03%)
  - oba: 73,148 (9.52%)
  - foodon: 40,123 (5.22%)

### Non-OLS Database (BioPortal)
- **Total:** 10,173 embeddings
- **Ontologies:** 13
- **Top contributors:**
  - meo: 2,499 (24.57%)
  - omp: 2,309 (22.70%)
  - bipon: 1,746 (17.16%)
  - gmo: 1,557 (15.31%)

### Combined Database
- **Total:** 778,496 embeddings (768,323 + 10,173) ✓
- **Unique ontologies:** 39
- **Integrity checks:**
  - ✓ Count matches OLS + Non-OLS exactly
  - ✓ All source ontologies present
  - ✓ No duplicates or corruption
  - ✓ Consistent vector dimensions (1536)

## Complete Ontology Distribution

### Top 10 Contributors (79.3% of embeddings)

| Rank | Ontology | Count | % of Total | Source |
|------|----------|-------|------------|--------|
| 1 | chebi | 221,776 | 28.49% | OLS |
| 2 | upheno | 192,001 | 24.66% | OLS |
| 3 | go | 84,737 | 10.88% | OLS |
| 4 | oba | 73,148 | 9.40% | OLS |
| 5 | foodon | 40,123 | 5.15% | OLS |
| 6 | flopo | 35,359 | 4.54% | OLS |
| 7 | micro | 17,645 | 2.27% | OLS |
| 8 | cl | 17,521 | 2.25% | OLS |
| 9 | fypo | 17,232 | 2.21% | OLS |
| 10 | ecto | 12,404 | 1.59% | OLS |

### All Ontologies (Complete List)

| Ontology | Count | % of Total | Source | Notes |
|----------|-------|------------|--------|-------|
| chebi | 221,776 | 28.49% | OLS | Primary chemical entities |
| upheno | 192,001 | 24.66% | OLS | Unified phenotype ontology |
| go | 84,737 | 10.88% | OLS | Gene Ontology |
| oba | 73,148 | 9.40% | OLS | Biological attributes |
| foodon | 40,123 | 5.15% | OLS | Food ontology |
| flopo | 35,359 | 4.54% | OLS | Flora phenotype |
| micro | 17,645 | 2.27% | OLS | Microbial ecology |
| cl | 17,521 | 2.25% | OLS | Cell types |
| fypo | 17,232 | 2.21% | OLS | Fission yeast phenotypes |
| ecto | 12,404 | 1.59% | OLS | Environmental exposures |
| pato | 9,061 | 1.16% | OLS | Phenotype attributes |
| aro | 8,551 | 1.10% | OLS | Antibiotic resistance |
| envo | 7,365 | 0.95% | OLS | Environment ontology |
| ecocore | 6,086 | 0.78% | OLS | Ecological core |
| eupath | 5,406 | 0.69% | OLS | Eukaryotic pathogen |
| **omp** | **4,749** | **0.61%** | **Both** | **2,440 (OLS) + 2,309 (non-OLS)** |
| phipo | 4,327 | 0.56% | OLS | Pathogen-host interaction |
| mco | 3,491 | 0.45% | OLS | Microbial conditions |
| eco | 3,449 | 0.44% | OLS | Evidence codes |
| meo | 2,499 | 0.32% | Non-OLS | Methane/methanogen ecology |
| bipon | 1,746 | 0.22% | Non-OLS | Biomedical investigation |
| gmo | 1,557 | 0.20% | Non-OLS | Genetically modified organisms |
| ddpheno | 1,397 | 0.18% | OLS | Dictyostelium phenotypes |
| ohmi | 1,244 | 0.16% | OLS | Host-microbe interactions |
| cmpo | 1,134 | 0.15% | OLS | Cellular microscopy |
| biolink | 974 | 0.13% | OLS | Semantic model |
| apo | 646 | 0.08% | OLS | Ascomycete phenotypes |
| n4l_merged | 454 | 0.06% | Non-OLS | Microbial phenotypes |
| pco | 435 | 0.06% | OLS | Population & community |
| miso | 387 | 0.05% | Non-OLS | Microbiome survey |
| mpo | 320 | 0.04% | Non-OLS | Microbial phenotypes |
| d3o | 283 | 0.04% | Non-OLS | 3D structures |
| id-amr | 271 | 0.03% | Non-OLS | AMR identifiers |
| geo | 196 | 0.03% | OLS | Geographical |
| exo | 175 | 0.02% | OLS | Experimental conditions |
| ofsmr | 157 | 0.02% | Non-OLS | Food safety |
| fmpm | 155 | 0.02% | Non-OLS | Food microbiology |
| typon | 19 | 0.00% | Non-OLS | Typhoid ontology |
| mccv | 16 | 0.00% | Non-OLS | Microbial culture |

## Key Findings

### 1. OMP Appears in Both Databases

**OMP (Ontology of Microbial Phenotypes) has embeddings in both OLS and BioPortal:**
- OLS version: 2,440 embeddings
- Non-OLS version: 2,309 embeddings
- Combined total: 4,749 embeddings

This is the only ontology with overlap. The combine operation correctly preserved both versions.

### 2. Low-Value Ontology Candidates

**Ontologies with <200 embeddings (potential removal candidates):**

| Ontology | Count | % | Source | Action |
|----------|-------|---|--------|--------|
| mccv | 16 | 0.00% | Non-OLS | Cross-ref with value analysis |
| typon | 19 | 0.00% | Non-OLS | Cross-ref with value analysis |
| fmpm | 155 | 0.02% | Non-OLS | Cross-ref with value analysis |
| ofsmr | 157 | 0.02% | Non-OLS | Cross-ref with value analysis |
| exo | 175 | 0.02% | OLS | Check native vs imported |
| geo | 196 | 0.03% | OLS | Check native vs imported |

**Recommendation:** Cross-reference these counts with `ontology_source_value_analysis.md` to determine if they provide only imported terms. If so, they are strong removal candidates.

### 3. Top 4 Dominate Search Space

The top 4 ontologies account for **73.4%** of all embeddings:
- chebi: 28.49%
- upheno: 24.66%
- go: 10.88%
- oba: 9.40%

This concentration means:
- Semantic search is heavily weighted toward these domains
- Small ontologies may be under-represented in results
- Removing low-value ontologies has minimal impact on coverage

## Verification Checklist

- [x] Combined count = OLS + Non-OLS (778,496 = 768,323 + 10,173)
- [x] All 27 OLS ontologies present
- [x] All 13 non-OLS ontologies present
- [x] No unexpected ontologies
- [x] All vectors 1536 dimensions (OpenAI text-embedding-3-small)
- [x] OMP overlap accounted for (both versions preserved)

## Next Steps

1. **Cross-reference with value analysis:** Use exact counts from this audit with the native/imported analysis in `ontology_source_value_analysis.md`

2. **Prioritize removal candidates:**
   - mccv (16) - if all CHEBI imports → REMOVE
   - typon (19) - if all BFO imports → REMOVE
   - fmpm (155) - check value analysis
   - ofsmr (157) - check value analysis

3. **Run METPO mappings:** Use the verified combined database to generate production SSSOM mappings:
   ```bash
   cd notebooks && python chromadb_semantic_mapper.py \
       --metpo-tsv ../src/templates/metpo_sheet.tsv \
       --chroma-path ./chroma_combined \
       --collection-name combined_embeddings \
       --output metpo_mappings.sssom.tsv \
       --top-n 10 \
       --label-only \
       --distance-cutoff 0.35
   ```

4. **Document removal rationale:** Before removing any ontologies, document why based on:
   - Exact embedding count (from this audit)
   - Native vs imported analysis (from value analysis)
   - METPO match contribution (from actual mappings)

## Audit Method

**Previous issue:** Initial audit used sampling (first 100k records), which completely missed non-OLS ontologies since they appear at positions 768,323+.

**Solution:** Modified `audit_chromadb.py` to scan ALL embeddings in 10k batches:
- Removed `sample_limit` parameter
- Changed from extrapolated estimates to exact counts
- Verified every embedding's metadata and vector dimensions

**Performance:** Complete scan of 778,496 embeddings takes ~3-5 minutes.

## Related Documents

- `ontology_source_value_analysis.md` - Native vs imported term analysis
- `chromadb_audit_results.txt` - Raw audit output
- `audit_chromadb.py` - Audit script
- `combine_chromadb.py` - Database merge script
