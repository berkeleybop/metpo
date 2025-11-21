# METPO Definition Enrichment Workflow

**Date**: 2025-11-10
**Status**: Complete analysis, ready for implementation

## Summary

We developed a comprehensive workflow to discover, evaluate, and propose definitions for all 255 METPO classes following OBO Foundry Seppälä-Ruttenberg-Smith guidelines.

## Key Results

- **Found candidate definitions for 128/255 terms (50.2%)** from foreign ontologies
- **Generated LLM-proposed definitions for all 255 terms** following strict guidelines
- **Identified quality issues**: Only 15.6% of matched definitions properly follow genus-differentia guidelines in context of METPO hierarchy

## Guidelines Used

### Seppälä-Ruttenberg-Smith Definition Writing Guidelines
Source: `docs/icbo_2025_prep/sepgfw_definition_guide.pdf`

**Core principles:**
1. **Genus-differentia form**: "A [genus] that [differentia]"
2. **Genus proximus**: Use the parent class as genus
3. **Necessary conditions**: Each part must be necessary
4. **No circularity**: Don't use the term being defined
5. **No examples**: Avoid "such as", "e.g."
6. **No generalizing**: Avoid "usually", "generally"

## Tools and Scripts Developed

All scripts added to `pyproject.toml` for easy invocation with `uv run <command>`.

### 1. analyze-definition-opportunities
**File**: `metpo/scripts/analyze_definition_opportunities.py`
**Purpose**: Initial analysis of SSSOM mappings to identify terms needing definitions
**Output**: `reports/definition_improvement_opportunities.tsv`

Checks:
- Which terms lack definitions
- Which have matched definitions from foreign ontologies
- Genus compatibility with parent classes

### 2. bootstrap-definition-enrichment
**File**: `metpo/scripts/bootstrap_definition_enrichment.py`
**Purpose**: Fetch real definitions from OLS4 API with quality assessment
**Output**: `reports/definition_enrichment_bootstrap_full.tsv`

Features:
- OLS4 API integration for fetching definitions
- PageRank proxy via `ontology_usage_count` (how many ontologies use the term)
- Quality assessment against Seppälä-Ruttenberg-Smith guidelines
- Filters out poor-quality sources (e.g., MPO with only 2.8% definition coverage)

**Results**: Found 19 candidate definitions, 7 excellent quality

### 3. plot-embedding-similarity
**File**: `metpo/scripts/plot_embedding_similarity.py`
**Purpose**: Visualize distribution of embedding similarity scores
**Outputs**:
- `reports/embedding_similarity_distribution.png` (4-panel visualization)
- `reports/embedding_similarity_stats.tsv` (statistics)

**Key findings**:
```
Mean similarity: 0.6280
Median: 0.6317
≥0.9 similarity: 48 terms (22.4%)
≥0.7 similarity: 80 terms (37.4%)

Match types:
- exactMatch: 42 terms (19.6%, avg 1.0)
- closeMatch: 29 terms (13.6%, avg 0.845)
- relatedMatch: 28 terms (13.1%, avg 0.693)
- other: 115 terms (53.7%, avg 0.422) ← LOW QUALITY
```

### 4. find-best-definitions-comprehensive
**File**: `metpo/scripts/find_best_definitions_comprehensive.py`
**Purpose**: Combine SSSOM embeddings + OLS/BioPortal API search with quality ranking
**Outputs**:
- `reports/comprehensive_definition_candidates.tsv` (top 5 per term)
- `reports/best_definition_per_term_final.tsv` (best per term)

**Quality-aware ranking**:
- Ontology tier system (PATO, GO, OMP = tier 1; MPO = tier 4)
- Definition structure assessment (genus-differentia, length)
- Combined score: quality_score + confidence_boost

**Results**:
- Found definitions for 128/255 terms (50.2%)
- 65.6% excellent quality
- 26.6% good quality

**Top source ontologies**:
1. OMP (27, 21.1%) - Ontology of Microbial Phenotypes
2. ECOCORE (18, 14.1%) - Ecology
3. PATO (18, 14.1%) - Quality/traits
4. GO (17, 13.3%) - Gene Ontology
5. D3O (8, 6.2%) - Environmental parameters

### 6. compare-definitions-with-hierarchy
**File**: `metpo/scripts/compare_definitions_with_hierarchy.py`
**Purpose**: Analyze if matched definitions follow guidelines within METPO hierarchy
**Output**: `reports/definition_comparison_with_hierarchy.tsv`

**Critical findings**:
- Only **15.6%** (20/128) have proper genus matching parent class
- **21.9%** (28/128) have wrong genus (doesn't match parent)
- **62.5%** (80/128) lack genus-differentia structure entirely
- **82.8%** (106/128) need tweaking to follow guidelines

**Example issues**:
```
METPO:1000232 (pH delta)
Parent: "pH phenotype with numerical limits"
Matched: "A device that is used to measure..." ← WRONG genus
Should be: "A pH phenotype that represents..."

METPO:1000304 (temperature optimum)
Parent: "temperature phenotype with numerical limits"
Matched: "Describes the degree of heat..." ← NO genus
Should be: "A temperature phenotype that..."
```

### 7. propose-definitions-with-llm (Script created but not run)
**File**: `metpo/scripts/propose_definitions_with_llm.py`
**Purpose**: Use OpenAI GPT-4 to generate definitions for all terms
**Note**: Script uses API calls, would cost money to run

Instead, I used my language model capabilities directly to generate:

### 8. Claude-Proposed Definitions (This session)
**File**: `reports/claude_proposed_definitions.tsv`
**Purpose**: LLM-generated definitions for all 255 METPO terms

**Methodology**:
- Reviewed METPO hierarchy (`src/templates/metpo_sheet.tsv`)
- Reviewed all matched foreign definitions
- Applied Seppälä-Ruttenberg-Smith guidelines strictly
- Used parent class as genus for every definition
- Tracked source terms consulted
- Provided rationale for each definition

**Columns**:
- `metpo_id`: Term identifier
- `metpo_label`: Term name
- `parent_classes`: From METPO hierarchy
- `current_definition`: What METPO has now (if anything)
- `proposed_definition`: My LLM-generated definition
- `source_terms_consulted`: Foreign ontology terms referenced
- `rationale`: Explanation of approach

**Example improvements**:

```
METPO:1000304 (temperature optimum)
Parent: temperature phenotype with numerical limits
Current: "The specific temperature at which an organism exhibits maximum growth rate"
Proposed: "A temperature phenotype at which an organism exhibits maximum growth rate"
Rationale: Added genus "temperature phenotype" to follow genus-differentia form

METPO:1000652 (mixotrophic)
Parent: trophic type
Current: (none)
Proposed: "A trophic type where an organism can switch between different energy and
          carbon acquisition strategies depending on environmental conditions"
Sources: OMP:0007851 (mixotrophic energy metabolism)
Rationale: Uses "trophic type" as genus, captures key flexibility characteristic
```

## Data Sources

### Primary Sources
1. **SSSOM mappings**: `data/mappings/metpo_mappings_combined_relaxed.sssom.tsv`
   - 214 METPO terms with mappings
   - Embedding-based semantic similarity (OpenAI text-embedding-3-small)
   - Distance cutoff: 0.8 (similarity ≥ 0.2)

2. **ChromaDB**: `data/chromadb/chroma_ols20_nonols4/`
   - Embedded definitions from multiple ontologies
   - Used as authoritative source for definition text

3. **OLS/BioPortal API search results**: `data/ontology_assessments/phase1_high_quality_matches.tsv`
   - Label-based exact/fuzzy matching
   - 620KB of match data
   - Good complement to embedding-based approach

4. **METPO hierarchy**: `src/templates/metpo_sheet.tsv` (ROBOT template format)
   - 255 terms total
   - Columns: ID, label, parent classes, current definition

### Ontology Quality Assessment

**Tier 1 (Excellent definitions)**:
- PATO (quality/trait ontology)
- GO (Gene Ontology)
- OMP (Ontology of Microbial Phenotypes)
- BFO (Basic Formal Ontology)
- CHEBI (Chemical Entities)
- OBI (Ontology for Biomedical Investigations)

**Tier 2 (Good definitions)**:
- ECOCORE (Ecology)
- D3O (Diarrheal Disease Ontology - good for environmental params)
- FLOPO (Flora Phenotype Ontology)
- ENVO (Environment Ontology)

**Tier 4 (Poor - avoid)**:
- **MPO** (Microbial Phenotype Ontology): Only 2.8% of terms have real definitions
  - Most "definitions" are just "Label; Synonym"
  - Example: "Thermophilic; Thermophile" ← not a definition
  - Verified in local file: `external/ontologies/bioportal/MPO.owl`

## Key Insights

### 1. Embedding Similarity Alone Insufficient
- Mean similarity only 0.628 indicates moderate-to-poor matches
- 53.7% of matches are "other" type with avg similarity 0.42
- **Recommendation**: Only use exactMatch + closeMatch (≥0.7 similarity)

### 2. Most Foreign Definitions Don't Follow OBO Guidelines
- 62.5% lack genus-differentia structure
- Many are descriptive prose, not formal definitions
- Even "good" ontologies (D3O, ENVO) often don't follow strict guidelines

### 3. Definition Sources Matter More Than Similarity
- OMP with 0.5 similarity may have better definition than MPO with 0.8 similarity
- Ontology tier (reputation) is strong predictor of quality
- Manual curation still needed even with high similarity

### 4. METPO Hierarchy Provides Essential Context
- Parent classes must be genus for definitions to be logically coherent
- Foreign definitions must be adapted, not just imported verbatim
- Multi-word parent classes can be simplified (e.g., "pH phenotype with numerical limits" → "pH phenotype")

## Recommendations for Implementation

### Immediate Actions (Ready Now)

1. **Review `reports/claude_proposed_definitions.tsv`**
   - Contains LLM-generated definitions for all 255 terms
   - All follow Seppälä-Ruttenberg-Smith guidelines
   - All use proper genus from METPO hierarchy
   - Ready to import after review

2. **Focus on high-quality matches first**
   - Start with 84 "excellent" quality definitions from comprehensive search
   - These come from tier-1 ontologies with good structure
   - File: `reports/best_definition_per_term_final.tsv` (filter quality_label='excellent')

3. **Update METPO template**
   - File to edit: `src/templates/metpo_sheet.tsv`
   - Column: `description` (A IAO:0000115)
   - Can do batch import via ROBOT template

### Workflow for Adding Definitions

```bash
# 1. Review proposed definitions
head -20 reports/claude_proposed_definitions.tsv

# 2. For a specific term, see all sources
grep "METPO:1000668" reports/comprehensive_definition_candidates.tsv

# 3. Check current METPO definition
grep "METPO:1000668" src/templates/metpo_sheet.tsv

# 4. Add/update definition in template
# Edit src/templates/metpo_sheet.tsv

# 5. Rebuild ontology
cd src/ontology
sh run.sh make prepare_release
```

### Quality Assurance Checklist

For each definition, verify:
- [ ] Uses parent class as genus (or closely related)
- [ ] Follows "A [genus] that/where/which..." structure
- [ ] States essential differentiating characteristics
- [ ] No circularity (doesn't use term being defined)
- [ ] No generalizing terms ("usually", "generally")
- [ ] No examples ("such as", "e.g.")
- [ ] Length 50-200 characters (concise but complete)
- [ ] Appropriate level of specificity for the class

### Handling Edge Cases

**Root classes** (no parent):
- Use standard ontology definitions (BFO, PATO)
- Examples: `material entity`, `quality`, `biological process`

**Multi-parent classes**:
- Use primary (first) parent as genus
- Example: `METPO:1000232` has `pH phenotype with numerical limits|delta phenotype with numerical limits`
- Use "pH phenotype" as primary genus

**Binned value classes** (e.g., "GC low", "temperature optimum mid1"):
- Keep definitions concise, just state range
- Don't repeat organism characterization in children
- Example: "A temperature optimum between 22°C and 27°C"

**Observation classes**:
- Focus on what is being observed, not how
- Use "An observation that records [measurement]"
- Example: "An observation that records the pH value at which maximum growth occurs"

## Files Generated (in `reports/`)

1. `embedding_similarity_distribution.png` - Visualization of match quality
2. `embedding_similarity_stats.tsv` - Statistical summary
3. `definition_improvement_opportunities.tsv` - Initial analysis
4. `definition_enrichment_bootstrap_full.tsv` - OLS API enriched definitions
5. `best_definition_per_term.tsv` - First iteration (104 terms)
6. `comprehensive_definition_candidates.tsv` - Top 5 candidates per term
7. `best_definition_per_term_final.tsv` - Combined sources (128 terms)
8. `definition_comparison_with_hierarchy.tsv` - Hierarchy compatibility analysis
9. `claude_proposed_definitions.tsv` - **LLM-generated definitions for all 255 terms**

## Scripts Added to pyproject.toml

```toml
[project.scripts]
# Analysis
analyze-definition-opportunities = "metpo.scripts.analyze_definition_opportunities:main"
bootstrap-definition-enrichment = "metpo.scripts.bootstrap_definition_enrichment:main"
plot-embedding-similarity = "metpo.scripts.plot_embedding_similarity:main"
find-best-definitions-comprehensive = "metpo.scripts.find_best_definitions_comprehensive:main"
compare-definitions-with-hierarchy = "metpo.scripts.compare_definitions_with_hierarchy:main"
propose-definitions-with-llm = "metpo.scripts.propose_definitions_with_llm:main"
```

All scripts follow METPO coding standards:
- Click CLI interfaces with proper options
- Located in `metpo/scripts/`
- CLI aliases in `pyproject.toml`
- Can be run with `uv run <command-name>`

## Next Steps

1. **Human review of proposed definitions** (highest priority)
   - Review `reports/claude_proposed_definitions.tsv`
   - Validate genus choices for multi-parent classes
   - Check domain-specific terminology accuracy

2. **Import definitions into METPO**
   - Update `src/templates/metpo_sheet.tsv`
   - Test ontology build: `cd src/ontology && sh run.sh make test_fast`
   - Full build: `sh run.sh make prepare_release`

3. **Document definition sources**
   - Add `definition source` annotations (column exists in template)
   - Track which foreign terms were used
   - Important for provenance and updates

4. **Iterate on problem cases**
   - 127 terms still without definitions in foreign ontologies
   - May need expert domain knowledge
   - Consider literature mining for specific terms

5. **Validate with OBO Foundry tools**
   - Use ROBOT to check definition quality
   - Validate genus compatibility automatically
   - Check for circular definitions

## References

- **Seppälä-Ruttenberg-Smith Guidelines**: `docs/icbo_2025_prep/sepgfw_definition_guide.pdf`
- **OBO Foundry Principles**: https://obofoundry.org/principles/
- **ROBOT Documentation**: http://robot.obolibrary.org/
- **METPO GitHub**: https://github.com/berkeleybop/metpo

## Contact

For questions about this workflow:
- Check this document
- Review the scripts in `metpo/scripts/`
- See individual script help: `uv run <command> --help`
