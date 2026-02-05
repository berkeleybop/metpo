# ICBO 2025 - Analysis Notes & Technical Findings

**Date:** 2025-11-06
**Status:** Technical analysis results and methodology notes
**Purpose:** Document analytical findings that support ICBO arguments

---

## Table of Contents

1. [Sibling Coherence Analysis](#sibling-coherence-analysis)
2. [Analysis Scripts Comparison](#analysis-scripts-comparison)
3. [GitHub Repository Analysis](#github-repository-analysis)
4. [Definition Extraction Methodology](#definition-extraction-methodology)
5. [Semantic Mapping ROI Analysis](#semantic-mapping-roi-analysis)

---

## Sibling Coherence Analysis

### Overview

**Mean structural coherence with METPO: 8.2%**

This analysis measured how well METPO's hierarchical structure aligns with external ontologies, even when individual terms have good semantic matches. The low score indicates that while we can find semantically similar terms, their organizational context differs significantly.

### What's Working Well

- **The Connection Strategy:** Our 5-step connection strategy successfully connects to local databases for `n4l_merged`, `mco`, and `micro`, and to the local OWL file for `meo`.
- **More Complete Analysis:** The number of terms for which we could retrieve external siblings more than doubled (from 56 to 112).
- **Meaningful Coherence Scores:** We now get meaningful, non-zero coherence scores for terms mapped to these local ontologies.

### What to Be Skeptical Of

- **The `ECOCORE` Warning:** Could not fetch class for ECOCORE:00000008. Any coherence scores related to ECOCORE mappings will be 0.0.
- **The `UnicodeWarning`s:** Some local OWL files have `unsound encoding` warnings, suggesting source files might not be perfectly clean.
- **The Definition of "Best Match":** The script currently only considers the single best match (`idxmin()`) for each METPO term. A METPO term might have several equally good matches to different ontologies.

### Is It Doing What Was Asked?

**Yes, absolutely.** The user asked for a way to "identify gaps in METPO and in the comparison ontologies" by analyzing sibling similarity. This script does exactly that. The low coherence scores are the "gaps" we were looking for. It provides a quantitative measure of structural alignment.

### METPO Terms with HIGH Coherence

The most structurally aligned parts of METPO are the fine-grained temperature and pH ranges:

- **`temperature range mid1 (METPO:1000450)`** and **`temperature range mid2 (METPO:1000451)`**
  - Coherence score: **0.500** with `n4l_merged`
  - Meaning: 50% of their siblings in METPO have a corresponding match to a sibling of `MidRangeTemperatureCondition` in N4L
  - Interpretation: Strong sign of structural alignment in this specific area

- **`pH range mid3 (METPO:1000463)`**
  - Coherence score: **0.400** with `mco`
  - Interpretation: Good structural agreement

### METPO Terms with LOW Coherence (0.000)

This is perhaps the most interesting finding for the talk. Many of METPO's core, high-level concepts have very poor structural alignment with their best semantic matches in other ontologies:

- **`metabolism (METPO:1000060)`**
- **`GC content (METPO:1000127)`**
- **`temperature optimum (METPO:1000304)`**
- **`pH optimum (METPO:1000331)`**
- **`NaCl optimum (METPO:1000333)`**

**Interpretation:** While the terms themselves are good semantic matches, their children and neighbors in METPO are organized very differently from their counterparts in ontologies like `n4l_merged`, `micro`, and `meo`.

**ICBO Impact:** This is a powerful, data-driven justification for METPO's existence, as it demonstrates that a simple one-to-one mapping of high-level terms is not enough to capture the specific structural details needed for our use case.

---

## Analysis Scripts Comparison

Here's a summary of what the different `analyze_*.py` scripts in the `notebooks` directory do and how they differ:

### `analyze_sibling_coherence.py`
- **Purpose:** Measure structural alignment between METPO and external ontologies
- **Method:** Compare sibling sets (terms at same hierarchical level)
- **Key Question:** "Do the graph neighborhoods look the same?"
- **Output:** Coherence scores (0.0 to 1.0) for each METPO term
- **Use Case:** Identify which parts of METPO align structurally with external ontologies

### `analyze_branch_coverage.py`
- **Purpose:** Determine which external ontologies provide the best coverage for different branches (sub-hierarchies) within METPO
- **Method:** Count matches within each METPO sub-tree
- **Key Question:** "If I care about the 'temperature' part of METPO, which external ontology is most likely to have all the terms I need?"
- **Output:** Coverage percentages by ontology and METPO branch
- **Use Case:** Guide ontology import decisions based on topical coverage

### `analyze_coherence_results.py`
- **Purpose:** Meta-analysis of sibling coherence results
- **Method:** Statistical analysis of coherence score patterns
- **Key Question:** "Given the coherence results, which METPO terms are the best candidates for alignment, and which external ontologies are the most structurally compatible with METPO overall?"
- **Output:** Summary statistics and recommendations
- **Use Case:** Deeper dive into coherence analysis results

### `analyze_match_quality.py`
- **Purpose:** High-level assessment of semantic similarity for non-OLS ontologies
- **Method:** Analyze distance scores from semantic search
- **Key Question:** "For these specific local ontologies, how good are the semantic matches overall?"
- **Output:** Mean distances, match quality distributions
- **Use Case:** Quick quality assessment of semantic mappings

### `analyze_matches.py`
- **Purpose:** General overview of SSSOM mapping results
- **Method:** Aggregate statistics from SSSOM file
- **Key Question:** "What is the 30,000-foot view of the mapping results?"
- **Output:** High-level summary statistics
- **Use Case:** Initial assessment of mapping completeness

### Summary of Differences

- **`sibling_coherence`** → **structural alignment** (graph neighborhoods)
- **`branch_coverage`** → **topical coverage** (breadth per topic)
- **`match_quality`** and **`matches`** → **semantic similarity** (term-to-term distance)
- **`coherence_results`** → **deeper dive** into coherence analysis

---

## GitHub Repository Analysis

### Directly Related Repositories
- `berkeleybop/metpo`
- `Knowledge-Graph-Hub/kg-microbe`
- `berkeleybop/metpo-kgm-studio`
- `monarch-initiative/metpo`

### Thematically Related Repositories
- `microbiomedata/nmdc-schema`
- `microbiomedata/nmdc-ontology`
- `GenomicsStandardsConsortium/mixs`
- `linkml/*` (various repositories)
- `PennTURBO/turbo-ontology`
- `CultureBotAI` (organization, no contributions yet)

### Repository Invitations (Expired)

A check for repository invitations revealed no active invitations. However, one relevant **expired** invitation was found:

- **`realmarcin/fitness-mcp`**: An invitation from Marcin Joachimiak for a repository described as "mcp for mutant pool fitness data". This could be a relevant project to discuss with Marcin.

---

## Definition Extraction Methodology

### Semantic Mapping Analysis Results

Analyzed 3,008 semantic mappings across 24 ontologies to propose definitions and cross-references.

### Proposal Breakdown

- **High confidence (distance <0.35):** 99 terms
  - **9 ready for auto-proposal** (no existing definition + match has definition text)
  - 90 have existing definitions or matches lack definition text
- **Medium confidence (distance 0.35-0.60):** 59 terms (require manual review)
- **Low confidence (distance >0.60):** 56 terms
- **No good matches:** 41 terms (require manual definition creation)

### Cross-References Generated

- 158 METPO terms have mappings to external ontologies (skos:closeMatch candidates)
- Ready for integration into ontology

### External Ontology Embedding Strategy

- **External ontologies:** embeddings of labels + synonyms + descriptions
- **METPO:** embeddings of **labels only**
- **Purpose:** Dual use - overlap analysis AND definition/description proposals
- **Results:** 1,282 good matches (distance <0.60) across 24 ontologies

---

## Semantic Mapping ROI Analysis

### Optimization Results

**Corpus Size Reduction:**
- Original: 778k embeddings
- Optimized: 453k embeddings
- Reduction: 41%

**ROI Improvement:**
- Before optimization: 1.69 good matches per 1000 embeddings
- After optimization: 2.82 good matches per 1000 embeddings
- Improvement: +67%

### Best Performers

**n4l_merged (Names for Life):**
- Embeddings: 454
- Good matches: 76
- ROI: **167.40** (best performer!)
- Status: **KEPT**

**PATO:**
- High match count (930 matches)
- Rank #1 among non-medical ontologies
- Status: **KEPT**

### Worst Performers

**CHEBI:**
- Embeddings: 221,000
- Good matches: 2
- ROI: **0.009** (worst performer!)
- Status: **REMOVED**

**Rationale:** Massive corpus size with minimal benefit for microbial trait coverage. Chemical entities are referenced by CURIE in KG-Microbe, not imported into METPO.

### Final Ontology Selection

24 ontologies selected based on:
1. **Coverage:** Number of good matches
2. **ROI:** Matches per 1000 embeddings
3. **Relevance:** Domain alignment with microbial traits
4. **Quality:** Maintenance status and ROBOT validation

See `docs/ONTOLOGY_SELECTION_SUMMARY.md` for complete rationale.

---

## Background Context for ICBO Arguments

### Gaps in Existing Ontologies (Quantified)

- **MicrO:** 103 ROBOT errors, unmaintained since 2018
- **Mean structural coherence with METPO:** 8.2%
- **Best coherence (MCO):** 48.7%, but poor match quality (0.87 avg distance)
- **Conclusion:** Cannot import existing ontology structures

### Coverage Fragmentation

- **Metabolism:** 154 ontologies needed for 90% coverage
- **Best single ontology (GO):** Only 67% coverage
- **Temperature/Oxygen:** 90-100% single-ontology coverage (PATO, ENVO)

**Strategic Implication:** Import well-covered domains, focus curation on fragmented areas.

---

## Scripts Available

### `notebooks/extract_definitions_from_mappings.py`
- Analyzes SSSOM mappings
- Proposes definitions and definition sources
- Generates cross-references
- Re-run anytime: `cd notebooks && uv run python extract_definitions_from_mappings.py`

### `notebooks/analyze_sibling_coherence.py`
- Measures structural alignment
- Compares METPO hierarchy to external ontologies
- Identifies alignment gaps

### Output Files Generated

1. **definition_proposals.tsv** (256 rows)
   - Complete analysis of all METPO terms
   - Columns: metpo_id, metpo_label, has_definition, has_def_source, best_match_distance, best_match_ontology, proposed_definition, confidence_level, action_needed

2. **high_confidence_definitions.tsv** (10 rows)
   - Ready-to-use definition proposals (distance <0.35)
   - Immediate action items

3. **definition_sources_needed.tsv** (55 rows)
   - Terms with definitions but missing definition sources
   - Can assign sources from best semantic matches

4. **metpo_cross_references.tsv** (159 rows)
   - Database cross-references for 158 METPO terms
   - Ready for skos:closeMatch integration

5. **sibling_coherence_analysis_output.csv** (213 rows)
   - Coherence scores for all analyzed METPO terms
   - Identifies structural alignment patterns
