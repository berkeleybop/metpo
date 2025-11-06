# ICBO 2025 Presentation Preparation - Summary

**Date:** 2025-11-05
**Status:** Analysis Complete - Action Items Identified

## Key Findings

### 1. METPO Term Definition Status

**Current Situation:**
- **Total METPO terms:** 255
- **Terms with definitions:** 118 (46.3%)
- **Terms WITHOUT definitions:** 137 (53.7%) ⚠️
- **Terms with definition sources:** 6 (2.4%) ⚠️⚠️

**This is critical for ICBO presentation** - Over half of terms lack definitions!

### 2. Semantic Mapping Analysis Results

Analyzed 3,008 semantic mappings across 24 ontologies to propose definitions and cross-references:

**Proposal Breakdown:**
- **High confidence (distance <0.35):** 99 terms
  - **9 ready for auto-proposal** (no existing definition + good match with definition text)
  - 90 have existing definitions or matches lack definition text
- **Medium confidence (distance 0.35-0.60):** 59 terms (require manual review)
- **Low confidence (distance >0.60):** 56 terms
- **No good matches:** 41 terms (require manual definition creation)

**Cross-References Generated:**
- 158 METPO terms have mappings to external ontologies (skos:closeMatch candidates)
- Ready for integration into ontology

### 3. Outstanding Work Before Presentation

**Priority 1 - Definition Sources (Highest Impact):**
- **54 terms have definitions but no sources** ⚠️
- These can be assigned definition sources from semantic matches
- See: `notebooks/definition_sources_needed.tsv`

**Priority 2 - High-Confidence Definitions:**
- **9 terms ready for auto-proposal** (distance <0.35, no existing definition)
- See: `notebooks/high_confidence_definitions.tsv`
- Terms: copiotrophic, lithoautotrophic, methanotrophic, methylotrophic, organotrophic, organoheterotrophic, pleomorphic shaped, vibrio shaped, spirochete shaped

**Priority 3 - Manual Review Queue:**
- **59 terms with medium confidence** (distance 0.35-0.60)
- Require manual review to assess quality
- May provide good definitions or definition sources

**Priority 4 - Manual Creation:**
- **41 terms with no good matches** (distance >0.60 or no matches)
- Require definitions written from scratch or from literature

## Files Generated

All files in `notebooks/`:

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

5. **icbo_2025_background_summary_additions.md**
   - Draft sections for ICBO background document
   - Includes: ontology gaps, semantic mapping methodology, outstanding work

## Recommended Workflow

### Before ICBO Presentation:

**Step 1: Add Definition Sources (1-2 hours)**
```bash
# Review definition_sources_needed.tsv
# For each term with existing definition, add IAO:0000119 annotation
# citing the best match ontology
```

**Step 2: Add High-Confidence Definitions (30 minutes)**
```bash
# Review high_confidence_definitions.tsv
# Validate the 9 proposed definitions
# Add to metpo_sheet.tsv
```

**Step 3: Review Medium-Confidence Queue (2-4 hours)**
```bash
# Review ~59 medium confidence proposals
# Accept/reject/modify proposed definitions
# Add to metpo_sheet.tsv
```

**Step 4: Integrate Cross-References (1 hour)**
```bash
# Use metpo_cross_references.tsv to add skos:closeMatch annotations
# to METPO OWL file
```

**Step 5: Manual Definitions for Critical Terms (variable time)**
```bash
# Identify which of the 41 "no match" terms are critical
# Write definitions from literature or domain expertise
```

## Background Context for ICBO

### Why METPO Exists

**Gaps in Existing Ontologies (quantified):**
- MicrO: 103 ROBOT errors, unmaintained since 2018
- Mean structural coherence with METPO: **8.2%**
- Best coherence (MCO): 48.7%, but poor match quality (0.87 avg distance)
- Conclusion: Cannot import existing ontology structures

**Semantic Mapping Methodology:**
- **External ontologies:** embeddings of labels + synonyms + descriptions
- **METPO:** embeddings of **labels only**
- **Purpose:** Dual use - overlap analysis AND definition/description proposals
- **Results:** 1,282 good matches (distance <0.60) across 24 ontologies

**Ontology Selection (ROI Analysis):**
- Optimized corpus from 778k → 453k embeddings (41% reduction)
- ROI improvement: +67% (1.69 → 2.82 good matches per 1000 embeddings)
- Removed CHEBI (221k embeddings, only 2 matches, ROI 0.009 - worst performer!)
- Kept n4l_merged (454 embeddings, 76 matches, ROI 167.40 - best performer!)

### Team Context (from available sources)

**Principal Investigators:**

1. **Marcin Joachimiak (LBNL)**
   - Computational biologist and PI for KG-Microbe
   - Leads ontology, knowledge graph, and AI/ML work under CMM
   - Developer of METPO

2. **N. Cecilia Martinez-Gomez (UC Berkeley)**
   - Microbiologist specializing in lanthanide-dependent methylotrophy
   - Leads experimental research on microbial metabolism
   - Collaborates on metabolic trait integration

3. **Ning Sun (LBNL)**
   - Staff Scientist (biological engineer)
   - Biological Systems and Engineering Division
   - Expert in biomass processing
   - **Note:** Specific role in CMM project requires clarification (Slack/Google Docs needed)

### CMM Project

**Critical Minerals and Materials (CMM):**
- U.S. Department of Energy program
- Focus: Securing domestic supply chains for critical materials in energy/environmental tech
- KG-Microbe developed under CMM initiative

**Sources:**
- https://www.energy.gov/science/critical-minerals-and-materials-program
- DOE BER Budget documents
- LBNL Earth & Environmental Sciences documentation

### KG-Microbe Applications

1. **Predicting Optimal Growth Media**
   - ML models: >70% precision on benchmark datasets
   - Both explainable rule-based and black-box approaches

2. **Microbial Trait Prediction**
   - Graph embeddings infer traits (cell shape, metabolic strategy)
   - Works for uncultivated microbes

3. **Hypothesis Generation**
   - Multi-hop queries discover trait associations
   - Vector algebra enables finding potential microbial interactions

## Information Gaps (Require Slack/Google Docs)

1. **Ning Sun's specific role** in CMM project
2. **CMM project detailed scope** and objectives
3. **Additional KG-Microbe applications** or use cases
4. **Collaboration details** between PIs
5. **ICBO presentation timeline** and format

## Next Steps for You (Mark)

1. **Slack/Google Docs Mining:**
   - Search for: CMM, Ning, KG-Microbe applications, ICBO timeline
   - Export relevant threads/docs to `context_imports/` directory
   - I can then analyze and integrate

2. **Definition Completion:**
   - Review `high_confidence_definitions.tsv` - validate 9 proposals
   - Review `definition_sources_needed.tsv` - assign sources to 54 terms
   - Use `definition_proposals.tsv` for comprehensive view

3. **Background Document:**
   - Merge `icbo_2025_background_summary_additions.md` into main document
   - Add CMM/Ning details once clarified
   - Add any additional KG-Microbe applications

## Scripts Available

- **notebooks/extract_definitions_from_mappings.py**
  - Analyzes SSSOM mappings
  - Proposes definitions and definition sources
  - Generates cross-references
  - Re-run anytime with: `cd notebooks && uv run python extract_definitions_from_mappings.py`

## Questions?

Let me know if you need:
- Modified scripts
- Different analysis thresholds
- Additional data extraction
- Help integrating definitions into metpo_sheet.tsv
