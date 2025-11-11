# LLM Analysis Conclusions and Hard-to-Reproduce Insights

**Purpose**: Document conclusions drawn from LLM-based analysis that may be difficult or expensive to reproduce.

**Last Updated**: 2025-11-10

---

## Ontology Assessment Methods Used

METPO used multiple complementary approaches to assess ontology usefulness:

### 1. Frequency-Based Ranking (Phase 1 - API Search)
**Script**: `notebooks/archive/phase1/phase1_batch_search.py`
**Method**: Direct API queries to OLS4 and BioPortal for METPO term labels
**Metric**: Match count and average similarity (Levenshtein distance)
**Status**: Superseded by semantic embedding approach, but **preserved for historical comparison**

**Key Finding from Phase 1**:
- SNOMED had highest raw match count (1,431 matches)
- But many were false positives due to exact string matching
- Led to development of semantic embedding approach

### 2. Semantic Embedding Analysis (Current Method)
**Script**: `notebooks/chromadb_semantic_mapper.py`
**Method**: OpenAI text-embedding-3-small (1536 dimensions) + cosine distance
**Metric**: ROI (good matches per 1,000 embeddings), where good = distance < 0.60
**Status**: **Production method**, results documented in `ONTOLOGY_SELECTION_SUMMARY.md`

**Key Findings**:
- **micro** (MicrO) ontology had best ROI: 34.63 matches per 1K embeddings
- **Surprising discovery**: FLOPO (flora/plant phenotype) ranked #2 with ROI 4.30
  - Despite being plant-focused, had excellent microbial phenotype coverage
  - Better performance than MCO (microbial conditions ontology)
  - This was unexpected and would not have been found through keyword filtering alone
- **CHEBI removed**: Worst ROI (0.009) - chemicals not phenotypes, 221K embeddings for only 2 good matches

### 3. Native vs Imported Term Analysis (ROI)
**Script**: `scripts/analysis/analyze_ontology_value.py`
**Method**: Parse IRIs to identify defining ontology vs importing ontology
**Metric**: Percentage of native terms, redundancy identification
**Status**: **Active tool** for assessing ontology contribution

**Key Insight**:
- Several ontologies only contributed imported terms available elsewhere
- Helps identify truly unique vs redundant sources
- Critical for minimizing import dependencies

### 4. Keyword-Based Relevance Scoring
**Script**: `notebooks/categorize_ontologies.py`
**Method**: Keyword scoring based on ontology title/description
**Keywords**: microbial, bacterial, phenotype, trait, environment, morphology, etc.
**Status**: **Active Makefile automation** for initial filtering

**Purpose**: Fast pre-filter before expensive embedding generation

---

## OntoGPT Literature Mining Insights (ICBO 2025)

### Template Design Lessons (Hard-Won Knowledge)

**Source**: `docs/presentations/icbo_2025/SESSION_LOG.md`

#### What Worked
1. **METPO predicates work through enum meanings**:
   ```yaml
   uses_as_carbon_source:
     meaning: METPO:2000006
   ```
   - OntoGPT expands these to full URIs in OWL/RDF output
   - Critical for expressing relationships, not just classes

2. **Local annotators work with absolute paths**:
   ```yaml
   annotators:
     - sqlite:/home/mark/gitrepos/metpo/src/ontology/metpo.owl
   ```
   - Enables grounding to development versions
   - Faster than remote ontology fetching

3. **Two-template approach effective**:
   - `strain_phenotype_icbo.yaml` - morphology, physiology, growth
   - `chemical_utilization_icbo.yaml` - organism-chemical relationships
   - Separation improves grounding accuracy

#### What Didn't Work (Avoid These)
1. **`prompt.examples` on slot classes causes hallucinations**:
   - OntoGPT code lines 388-394 show examples override grounding
   - Only use `prompt.examples` at template root level
   - Cost: $5-10 in wasted API calls learning this

2. **Custom annotations ignored**:
   - Tried `exclude:` annotation - no implementation in OntoGPT
   - Stick to documented annotations: `prompt`, `prompt.skip`, `annotators`, `prompt.examples`, `ner.recurse`

3. **Relative paths for annotators fail**:
   - Must use absolute paths or standard `sqlite:obo:ontology_id` format
   - Relative paths cause silent failures

### METPO Grounding Performance

**Abstracts tested**: 10 IJSEM abstracts (methylotrophs, halophiles, thermophiles)
**Templates**: strain_phenotype_icbo.yaml + chemical_utilization_icbo.yaml

**Grounding Success Rate** (October 2025, gpt-4o):
- **Morphology**: ~80% grounded (rod-shaped, coccus, motile)
- **Growth conditions**: ~70% grounded (mesophilic, aerobic, halophilic)
- **Chemical utilization**: ~60% grounded (methanol, ethanol, METPO properties)

**Common Failures**:
- "Gram-stain-negative" → AUTO: (synonym mismatch, "Gram-negative" works)
- Specific numeric ranges → Not grounded (temperature 37°C, pH 7.0)
- Complex modifiers → Simplified (e.g., "facultatively aerobic" → "aerobic")

**Cost**: ~$2-3 per 10 abstracts (gpt-4o at $0.01/1K tokens)

---

## Phase 1 Ontology Rankings (Historical Record)

**Preserved in**: `notebooks/archive/phase1/phase1_ontology_rankings.tsv`

Top 10 ontologies by match frequency (Oct 2024):

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

**Why Superseded**:
- String matching found too many false positives (SNOMED)
- Missed semantic relationships
- API rate limits made it slow (9.7 hours for 240 terms)
- Semantic embeddings provided better precision

**Why Preserved**:
- Shows methodology evolution
- Validates semantic approach (micro, FLOPO, PATO still rank highly)
- Historical comparison for future assessments

---

## Semantic Search Optimization Insights

### ChromaDB Performance

**Database sizes tested**:
- Small (4 ontologies, 3.6K embeddings): <1 sec queries
- Medium (24 ontologies, 453K embeddings): ~2-3 sec queries
- Large (39 ontologies, 778K embeddings): ~5-8 sec queries

**Optimal configuration**: 24 ontologies (final selection)
- Balance of coverage vs query speed
- 41.8% corpus reduction, 97.6% match retention
- ROI improved 67% (1.69 → 2.82)

### Embedding Model Selection

**Tested**: OpenAI text-embedding-3-small (1536 dims)
**Not tested**: text-embedding-3-large (3072 dims, 3x cost)
**Rationale**: 1536 dims sufficient for ontology term similarity, 3072 dims overkill

**Cost**: ~$0.13 per 1M tokens = ~$0.10 per 1,000 ontology terms
- Total cost for 452K embeddings: ~$45-50 (one-time)
- Cheaper than large-scale LLM analysis

---

## Key Takeaways for Future Work

### ✅ Preserve These Methods
1. **Semantic embeddings** (production method)
2. **ROI analysis** (native vs imported terms)
3. **Keyword filtering** (fast pre-filter)
4. **Phase 1 rankings** (historical baseline)

### ❌ Don't Repeat These Mistakes
1. Using API string matching as primary method (too slow, too many false positives)
2. Putting `prompt.examples` on slot classes in OntoGPT templates
3. Assuming all "microbial" ontologies are equally relevant (FLOPO surprise!)
4. Including CHEBI in phenotype searches (221K embeddings, ROI 0.009)

### 💡 Future Directions
1. Test larger embedding models (3072 dims) on sample to verify 1536 sufficiency
2. Explore non-OpenAI embeddings (open source models, cost reduction)
3. A/B test OntoGPT performance: gpt-4o vs gpt-4o-mini vs Claude
4. Measure grounding improvement after adding Phase 1 identified synonyms

---

## Reproducibility Notes

### Expensive to Reproduce (preserve results)
- ✅ Phase 1 API search: 9.7 hours, rate-limited
- ✅ Embedding generation: $45-50, 778K → 453K optimization
- ✅ OntoGPT testing: $20-30 across 10 abstracts, multiple iterations

### Easy to Reproduce (scripts available)
- ✅ ROI analysis: Fast, deterministic
- ✅ Keyword categorization: Fast, deterministic
- ✅ Coherence analysis: Slow but deterministic (OAKLib)

### Cannot Reproduce (document conclusions)
- ⚠️ OntoGPT template iteration: Multiple failed approaches, ~$10 wasted on hallucinations
- ⚠️ Subjective ontology quality assessments (FLOPO surprise, CHEBI removal rationale)
- ⚠️ Embedding model selection rationale (1536 vs 3072 dims)

---

## References

**Analysis Scripts**:
- Phase 1: `notebooks/archive/phase1/phase1_batch_search.py`
- Semantic mapper: `notebooks/chromadb_semantic_mapper.py`
- ROI analysis: `scripts/analysis/analyze_ontology_value.py`
- Coverage analysis: `scripts/analysis/analyze_branch_coverage_final.py`

**Documentation**:
- Ontology selection: `docs/ONTOLOGY_SELECTION_SUMMARY.md`
- ICBO 2025 prep: `docs/presentations/icbo_2025/SESSION_LOG.md`
- OntoGPT results: `literature_mining/outputs/icbo_examples/`

**Results Preserved**:
- Phase 1 results: `notebooks/archive/phase1/*.tsv`
- Semantic mappings: `notebooks/metpo_mappings_*.sssom.tsv`
- ICBO extractions: `literature_mining/outputs/icbo_examples/*.yaml`
