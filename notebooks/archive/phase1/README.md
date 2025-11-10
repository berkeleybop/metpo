# Phase 1 Discovery Archive

**Status**: Superseded by semantic mapper workflow (chromadb_semantic_mapper.py)

## Historical Context

Phase 1 was the initial discovery phase of METPO's ontology alignment project, using direct API queries to OLS4 and BioPortal to find potential matches for METPO terms.

## Archived Materials

### Scripts
- `phase1_batch_search.py` - Batch search METPO labels via OLS/BioPortal APIs
- `phase1_batch_search.ipynb` - Interactive notebook version

### Results (October 2024)
- `phase1_raw_results.tsv` (6.1MB) - All API responses
- `phase1_high_quality_matches.tsv` (3.6MB) - Filtered high-quality matches
- `phase1_ontology_rankings.tsv` (19KB) - Ontology rankings by match count
- `phase1_summary_stats.json` (1.7KB) - Summary statistics

## Why Superseded

Phase 1 approach had limitations:
- **API rate limits**: Slow batch processing
- **Exact matching**: Missed semantic similarities
- **No embeddings**: Couldn't capture conceptual closeness

## Current Approach

Replaced by semantic embedding workflow:
1. **Embedding generation**: `embed_ontology_to_chromadb.py`
2. **Semantic search**: `chromadb_semantic_mapper.py`
3. **Quality analysis**: `analyze_matches.py`
4. **Coherence validation**: `analyze_sibling_coherence.py`

See main Makefile targets: `alignment-*`

## Preservation Rationale

Archived for:
- Historical record of methodology evolution
- Reproducibility of early exploration
- Comparison with current semantic approach
- Documentation of lessons learned
