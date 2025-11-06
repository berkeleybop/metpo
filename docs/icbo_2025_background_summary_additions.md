# Additions to ICBO 2025 Background Summary

## Ning Sun (LBNL)
- Staff Scientist (biological engineer) 
- Biological Systems and Engineering Division, LBNL
- Expert in biomass processing
- **Note**: Role in CMM project requires clarification from Slack/Google Docs

## Gaps in Existing Phenotype Ontologies - Why METPO?

### The Landscape of Microbial Phenotype Ontologies

Multiple microbial phenotype ontologies exist, but none adequately address bacterial ecophysiological traits for our use case:

| Ontology | Domain | Status | Key Issues |
|----------|--------|--------|------------|
| **MicrO** | Prokaryotic phenotypes | Unmaintained | 103 ROBOT validation errors; no updates since 2018; only 4 benchmark domains at ≥80% coverage |
| **OMP** | Microbial phenotypes | Active | Low structural coherence (3.6% with METPO); 281 matches but poor quality (0.80+ distance) |
| **MCO** | Growth conditions | Active | Best coherence (48.7%) but poor semantic matches (0.87 avg distance); only 10 overlapping terms |
| **PATO** | Generic qualities | Active | Too abstract; 0% structural coherence; not microbial-specific |
| **APO/FYPO/DDPHENO** | Eukaryotic microbes | Active | Fungi, yeast, amoeba - not bacterial |
| **ARO** | Antibiotic resistance | Active | Narrow domain; zero METPO matches |

### Quantitative Justification for METPO

**Structural Coherence Analysis:**
- Mean coherence across all ontologies: **8.2%** (very low!)
- Only 6/250 METPO terms (2.4%) achieved ≥50% structural coherence with any external ontology
- Interpretation: METPO's classification structure is **novel** and cannot be imported from existing sources

**Ontology Performance Against METPO:**
- MCO: 48.7% mean coherence, but poor match quality (0.87 avg distance)
- OBA: 4.1% coherence (7 terms analyzed, 0.91 avg distance)
- OMP: 3.6% coherence (3 terms analyzed, 0.80 avg distance)
- All others: 0% coherence

**What This Means:**
- Coverage ≠ Structural Alignment: Ontologies may have similar terms but organize them differently
- Cannot wholesale import existing hierarchies - would need to restructure ~92% of mappings
- METPO provides clean hierarchies needed for KG reasoning and SPARQL queries

### METPO's Advantages

1. **Focused Scope:** 255 core classes optimized for bacterial ecophysiology (not generic cross-species traits)
2. **Quality:** 0 ROBOT validation errors (vs. MicrO's 103 errors)
3. **Active Maintenance:** Responsive to literature mining and database integration needs
4. **KG-Optimized:** Clean hierarchies, reification classes, designed for knowledge graph reasoning
5. **Acknowledges Precedent:** Uses skos:closeMatch and IAO:0000119 (definition source) to link to existing ontologies

**See:** `docs/METPO_JUSTIFICATION.md` for comprehensive analysis

## Semantic Mapping Methodology and Results

### Vector Search Approach

**Embedding Strategy:**
- **External Ontologies:** Embeddings include labels + synonyms + descriptions (full text)
- **METPO:** Embeddings are **label-only**
- **Purpose:** Dual objectives:
  1. Analyze overlap/coherence between ontologies
  2. Propose definitions and descriptions for METPO terms
  3. Assign definition sources (IAO:0000119) and database cross-references
  4. Generate skos:closeMatch mappings

**Technical Implementation:**
- OpenAI text-embedding-3-small (1536 dimensions)
- ChromaDB vector database: 452,942 embeddings across 24 ontologies
- Distance threshold: <0.60 for good matches, <0.35 for high-confidence automation

### Ontology Selection via ROI Analysis

**Method:** Return on Investment = (good matches / embeddings) × 1000

**Corpus Optimization:**
- Started with: 778,496 embeddings, 39 ontologies
- Optimized to: 452,942 embeddings (-41.8%), 24 ontologies
- Match retention: 97.6% (1,282 of 1,314 good matches kept)
- ROI improvement: +67% (1.69 → 2.82 good matches per 1000 embeddings)

**Notable Removals:**
- **CHEBI** (221,776 embeddings): Only 2 good matches, ROI 0.009 - worst performer
  - Reason: Chemical entities ≠ microbial phenotypes
- **FOODON, CL, FYPO, ECTO, ARO, DDPHENO:** Domain mismatch or zero matches

**Top Performers Kept:**
- **n4l_merged** (454 embeddings): 76 good matches, ROI 167.40 - best in collection!
- **MicrO** (17,645 embeddings): 611 matches, ROI 34.63 - primary source despite validation issues
- **FLOPO** (35,359 embeddings): 152 matches, ROI 4.30
- **High-volume keepers:** OBA (69 matches), UPHENO (154 matches), GO (28 matches)

**See:** `notebooks/ontology_removal_recommendation.md` and `notebooks/ONTOLOGY_SELECTION_SUMMARY.md`

## Outstanding Work Before Presentation

### Critical Gap: METPO Term Definitions

**Current Status (as of 2025-11-05):**
- Total METPO terms: **255**
- Terms with definitions: **118 (46%)**
- **Terms needing definitions: 137 (54%)**
- Terms with definition source annotations: **6 (2%)**
- **Terms needing definition sources: 249 (98%)**

**Data Available for Completion:**
- Semantic mapping results: 1,282 good matches (distance <0.60) to external ontologies
- Top matches available for each of 250 METPO terms
- Source ontology definitions available for reuse/adaptation

**Required Actions:**
1. Extract definitions from matched ontology terms (distance <0.35 for high-confidence)
2. Assign definition sources (IAO:0000119) citing source ontologies
3. Add database cross-references (e.g., skos:closeMatch, oboInOwl:hasDbXref)
4. Generate proposed definitions for manual review queue (distance 0.35-0.60)
5. Validate and integrate before ICBO presentation

**Tools Needed:**
- Script to extract definitions from SSSOM mapping results
- Automated proposal generation for definition sources
- Review queue for manual curation of ambiguous matches
