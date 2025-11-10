# API Search Method for Ontology Assessment

**Method**: Frequency-based ontology assessment using direct API queries
**Script**: `scripts/analysis/assess_ontology_by_api_search.py`
**Notebook**: `notebooks/assess_ontology_by_api_search.ipynb`
**Status**: Complementary method to semantic embeddings

## Purpose

Assesses ontology usefulness by counting match frequency through direct API queries to OLS4 and BioPortal. This provides a **label-based** assessment that complements the **semantic-based** approach used by the current production pipeline.

## Method Overview

1. **Input**: METPO term labels (`metpo_all_labels.tsv`)
2. **Search**: Query each label against OLS4 and BioPortal APIs
3. **Scoring**: Calculate similarity using Levenshtein distance
4. **Ranking**: Rank ontologies by match count and average similarity

## Results (October 2024)

### Files in this Directory

- `phase1_raw_results.tsv` (6.1MB) - All API responses with similarity scores
- `phase1_high_quality_matches.tsv` (3.6MB) - Filtered results (similarity ≥ 0.5)
- `phase1_ontology_rankings.tsv` (19KB) - **Ontologies ranked by match frequency**
- `phase1_summary_stats.json` (1.7KB) - Summary statistics

### Top 10 Ontologies by Match Frequency

| Rank | Ontology | High Quality Matches | Avg Similarity | Total Matches |
|------|----------|---------------------|----------------|---------------|
| 1 | SNOMED | 1,431 | 0.515 | 2,640 |
| 2 | METPO | 1,395 | 0.699 | 1,732 |
| 3 | NCIT | 908 | 0.492 | 1,855 |
| 4 | PATO | 691 | 0.575 | 827 |
| 5 | NCBITaxon | 616 | 0.418 | 1,688 |
| 6 | SNOMEDCT | 549 | 0.526 | 986 |
| 7 | FLOPO | 449 | 0.583 | 664 |
| 8 | AFO | 443 | 0.566 | 577 |
| 9 | OCHV | 431 | 0.593 | 600 |
| 10 | micro | 356 | 0.546 | 590 |

## Comparison with Semantic Embedding Method

### API Search Method (This Approach)
- **Pros**: Fast initial discovery, no embedding costs, finds exact label matches
- **Cons**: Misses semantic relationships, false positives from string similarity, API rate limits
- **Best for**: Initial ontology discovery, validating semantic results, label-based assessment

### Semantic Embedding Method (Current Production)
- **Script**: `notebooks/chromadb_semantic_mapper.py`
- **Pros**: Captures semantic relationships, better precision, faster queries (post-embedding)
- **Cons**: Upfront embedding cost ($45-50), requires OpenAI API, black-box similarity
- **Best for**: Production mapping, semantic similarity, relationship discovery

## Key Findings

### Validated by Both Methods
- **PATO**, **FLOPO**, **micro** rank highly in both approaches
- Confirms these are genuinely valuable sources
- Provides confidence in semantic method

### Divergences
- **SNOMED** ranks #1 in API search but has low ROI in semantic search
  - Reason: Many false positives from broad medical terminology
  - Lesson: Match frequency ≠ match quality

- **FLOPO** (plant ontology) ranks #7 here, #2 in semantic ROI
  - Semantic search better captures cross-domain phenotype applicability
  - API search biased toward exact microbial terminology

## When to Use This Method

✅ **Use API search when**:
- Exploring new ontologies for first time
- Validating semantic search results
- Need human-readable exact label matches
- Want to avoid embedding generation costs
- Investigating specific synonym coverage

❌ **Don't use API search when**:
- Need semantic relationships (use embeddings)
- Processing large term sets (too slow, 9.7 hours for 240 terms)
- Require high precision (too many false positives)
- Building production pipelines (use semantic search)

## Reproducibility

**Cost**: Free (public APIs)
**Time**: ~9.7 hours for 240 terms (API rate limits)
**Dependencies**: OLS4 API, BioPortal API (requires free API key)

**To run**:
```bash
# From repository root
cd scripts/analysis
python assess_ontology_by_api_search.py

# Or use notebook for interactive exploration
jupyter notebook notebooks/assess_ontology_by_api_search.ipynb
```

## References

**Current production method**: See `notebooks/chromadb_semantic_mapper.py`
**Ontology selection**: See `docs/ONTOLOGY_SELECTION_SUMMARY.md`
**Methodology comparison**: See `docs/LLM_ANALYSIS_CONCLUSIONS.md`
