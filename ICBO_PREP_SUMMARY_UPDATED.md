# ICBO 2025 Presentation Preparation - Complete Summary

**Date:** 2025-11-06
**Status:** Analysis Complete with Full CMM Context

---

## CMM Project Context - The Big Picture

### Project Overview
**Full Title:** "Advanced Biorecovery of Critical Minerals through AI/ML-Guided Design of Microbial Chassis and Bioadsorbent"

**Goal:** Develop AI/ML-guided microbial technology to recover Rare Earth Elements (REEs) from e-waste using engineered microbes.

**Target Elements:** Neodymium (Nd), Praseodymium (Pr), Dysprosium (Dy)
**Funding:** $850K for FY26 (12 months), renewal pending fall 2026
**Status:** Funds received end of August 2025

### Principal Investigators

**PI: Ning Sun (LBNL)**
- Staff Scientist, Biological Systems and Engineering Division
- Expert in biomass processing
- Leads overall project coordination (10% effort)

**Co-PIs:**

1. **Marcin Joachimiak (LBNL EGSB)** - 10% effort
   - Leads KG-CMREE (Knowledge Graph for Critical Minerals/REE)
   - AI/ML framework development
   - Software lead: Mark Miller (20% effort)
   - **This is where METPO and KG-Microbe fit!**

2. **N. Cecilia Martinez-Gomez (UC Berkeley)** - 10% effort
   - Bacterial strain engineering for REE selectivity
   - Lanthanophore characterization
   - Lab technician: Trinity Reiner (80% effort)

3. **Rebecca Abergel (LBNL Chemical Sciences)** - 5% effort
   - Spectroscopic assay development for REE detection
   - f-element coordination chemistry
   - Postdoc: Alexander Brown (50% effort)

4. **Yasuo Yoshikuni (JGI)** - 5% effort
   - Expanding bacterial/fungal chassis
   - CRAGE (Chassis-independent Recombinase-Assisted Genome Engineering)
   - Postdoc: Yusuke Otani (50% effort)

5. **Romy Chakraborty (LBNL EESA)** - 2% effort
   - Microbial ecology
   - Postdoc: Mingfei Chen (5% effort)

### How KG-Microbe Fits Into CMM

**Task 1.1: Construct KG-CMREE and Establish AI/ML Framework**

KG-CMREE (Knowledge Graph for Critical Minerals and Rare Earth Elements) **extends KG-Microbe**:

- **Building on KG-Microbe foundation:**
  - >3,000 organismal traits
  - >30,000 functional/genomic traits
  - Harmonizes data from BacDive, BactoTraits, UniProt, MediaDive, etc.
  - Uses Biolink model for semantic integration

- **New CMM-specific data:**
  - REE bioaccumulation phenotypes
  - Lanthanophore biosynthetic pathways
  - Spectroscopic measurements
  - High-throughput screening results
  - Bioprocess parameters

- **AI/ML Framework:**
  - **Agentic AI** with cooperating autonomous agents:
    - Literature Mining Agent (LLM-assisted extraction from publications)
    - Experiment Design Agent (predictive models, historical outcomes)
    - Failure Analysis Agent (learns from unsuccessful experiments)
  - **Graph Transformers** for ranking candidate taxa/pathways/proteins
  - **Neurosymbolic loop** combining symbolic rules + graph learning
  - **Design-Build-Test-Learn (DBTL) cycles** for strain optimization

**Why METPO Matters for CMM:**

Microbial phenotypes are critical for REE recovery:
- **pH tolerance:** REE recovery processes can be acidic (bioleaching) or neutral/alkaline
- **Temperature tolerance:** Some strains are extremophiles
- **Oxygen requirements:** Aerobic vs anaerobic metabolism affects REE accumulation
- **Metal tolerance:** Microbes must survive in presence of REEs and competing metals
- **Metabolic capabilities:** Determines which REE chelators (lanthanophores) can be produced

**METPO provides the phenotype ontology needed to:**
1. Annotate microbial traits in KG-CMREE
2. Enable AI models to predict which microbes can thrive in REE recovery conditions
3. Link genomic features to phenotypic capabilities for strain engineering

---

## Key Findings - METPO Definition Status

### Current Situation (as of 2025-11-05)

- **Total METPO terms:** 255
- **Terms with definitions:** 118 (46.3%)
- **Terms WITHOUT definitions:** 137 (53.7%) ⚠️
- **Terms with definition sources:** 6 (2.4%) ⚠️⚠️

**This is critical for ICBO presentation** - Over half of terms lack definitions!

### Semantic Mapping Analysis Results

Analyzed 3,008 semantic mappings across 24 ontologies to propose definitions and cross-references:

**Proposal Breakdown:**
- **High confidence (distance <0.35):** 99 terms
  - **9 ready for auto-proposal** (no existing definition + match has definition text)
  - 90 have existing definitions or matches lack definition text
- **Medium confidence (distance 0.35-0.60):** 59 terms (require manual review)
- **Low confidence (distance >0.60):** 56 terms
- **No good matches:** 41 terms (require manual definition creation)

**Cross-References Generated:**
- 158 METPO terms have mappings to external ontologies (skos:closeMatch candidates)
- Ready for integration into ontology

---

## Outstanding Work Before Presentation

### Priority 1 - Definition Sources (Highest Impact)
- **54 terms have definitions but no sources** ⚠️
- These can be assigned definition sources from semantic matches
- See: `notebooks/definition_sources_needed.tsv`

### Priority 2 - High-Confidence Definitions
- **9 terms ready for auto-proposal** (distance <0.35, no existing definition)
- See: `notebooks/high_confidence_definitions.tsv`
- Terms: copiotrophic, lithoautotrophic, methanotrophic, methylotrophic, organotrophic, organoheterotrophic, pleomorphic shaped, vibrio shaped, spirochete shaped

### Priority 3 - Manual Review Queue
- **59 terms with medium confidence** (distance 0.35-0.60)
- Require manual review to assess quality
- May provide good definitions or definition sources

### Priority 4 - Manual Creation
- **41 terms with no good matches** (distance >0.60 or no matches)
- Require definitions written from scratch or from literature

---

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

---

## Recommended Workflow Before ICBO

### Step 1: Add Definition Sources (1-2 hours)
Review `definition_sources_needed.tsv` and add IAO:0000119 annotations citing the best match ontology for each term with existing definition.

### Step 2: Add High-Confidence Definitions (30 minutes)
Review `high_confidence_definitions.tsv`, validate the 9 proposed definitions, add to `metpo_sheet.tsv`.

### Step 3: Review Medium-Confidence Queue (2-4 hours)
Review ~59 medium confidence proposals, accept/reject/modify proposed definitions, add to `metpo_sheet.tsv`.

### Step 4: Integrate Cross-References (1 hour)
Use `metpo_cross_references.tsv` to add skos:closeMatch annotations to METPO OWL file.

### Step 5: Manual Definitions for Critical Terms (variable time)
Identify which of the 41 "no match" terms are critical for CMM/ICBO presentation, write definitions from literature or domain expertise.

---

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

### KG-Microbe Applications (Published)

1. **Predicting Optimal Growth Media**
   - ML models: >70% precision on benchmark datasets
   - Both explainable rule-based and black-box approaches
   - Publication: ISMB/ECCB 2025 talk
   - Publication: CSBJ 2025 (Máša, Kliegr, Joachimiak)

2. **Microbial Trait Prediction**
   - Graph embeddings infer traits (cell shape, metabolic strategy)
   - Works for uncultivated microbes

3. **Hypothesis Generation**
   - Multi-hop queries discover trait associations
   - Vector algebra enables finding potential microbial interactions

### KG-Microbe + CMM Integration (In Progress)

**KG-CMREE extends KG-Microbe for REE biorecovery:**

4. **AI-Guided Strain Discovery** (CMM Task 1.1)
   - Graph Transformers rank candidate taxa for REE accumulation
   - Agentic AI orchestrates DBTL cycles
   - Literature mining agent extracts knowledge from lanthanome publications

5. **Bioengineering Optimization** (CMM Task 2)
   - Predicts CRAGE integration efficiency in extremophiles
   - Links genomic features to REE selectivity phenotypes
   - Guides lanthanophore biosynthetic cluster discovery

6. **High-Throughput Experiment Design** (CMM Task 1.3)
   - AI-designed experiments for 6,000 samples/day pipeline
   - Automated analysis of REE accumulation screening data
   - Failure analysis improves future experiment design

### Team Context

**CMM Project Team (FY26):**

1. **Ning Sun (LBNL BSE)** - PI
   - Biomass processing expert
   - Leads overall project (10% effort)
   - Budget: $264,870
   - Team: Rita Kuo (Research Support, 20%), Saad Naseem (Postdoc, 50%)

2. **Marcin Joachimiak (LBNL EGSB)** - Co-PI
   - KG-CMREE and AI/ML framework lead
   - 10% effort on CMM
   - Budget: $131,682
   - Team: Mark Miller (Software Developer, 20%)
   - **Dual role:** CMM AI/ML + METPO/KG-Microbe development

3. **N. Cecilia Martinez-Gomez (UC Berkeley)** - Co-PI
   - Lanthanide-dependent methylotrophy expert
   - Bacterial strain engineering (10% effort)
   - Budget: $158,599
   - Team: Trinity Reiner (Lab Technician, 80%)

4. **Rebecca Abergel (LBNL CSD)** - Co-PI
   - f-element coordination chemistry
   - Spectroscopic assay development (5% effort)
   - Budget: $130,254
   - Team: Alexander Brown (Postdoc, 50%)

5. **Yasuo Yoshikuni (JGI)** - Co-PI
   - Synthetic biology, CRAGE technology
   - Fungal/bacterial chassis expansion (5% effort)
   - Budget: $137,622
   - Team: Yusuke Otani (Postdoc, 50%)

6. **Romy Chakraborty (LBNL EESA)** - Co-PI
   - Microbial ecology (2% effort)
   - Budget: $26,973
   - Team: Mingfei Chen (Postdoc, 5%)

**Total Budget:** $850,000 for 12 months (FY26)

**Institutional Arrangements:**
- IUT (Inter-University Transfer) between LBNL and UC Berkeley established
- MTA (Material Transfer Agreement) in progress
- Molecular Foundry user proposal submitted for advanced imaging

### DOE BER Decision Letter (Key Quote)

> "BER is most interested in supporting LBNL objectives that seek to build a high-throughput strain screening and validation pipeline for ML guided bioengineering of REE accumulation, as these aims are more directly relevant to the request in the call to advance biodesign and synthetic biology for the extraction and recovery of CMM from natural and complex environments."

**Translation:** DOE prioritizes the AI/ML + HTP pipeline work (Marcin's Task 1.1 + Ning's Task 1.3) as the most innovative aspects of the proposal.

---

## CMM Project Structure - How It All Connects

### Task 1: Technical Tool Development

**Task 1.1: KG-CMREE and AI/ML Framework (Marcin Joachimiak)**
- Extends KG-Microbe with REE-specific data
- Agentic AI with autonomous experiment orchestration
- Graph Transformers for strain ranking
- **METPO role:** Provides phenotype annotations for microbial traits

**Task 1.2: Spectroscopic Assay Development (Rebecca Abergel)**
- ICP-OES: Quantify REEs in digested cells
- Time-Resolved Luminescence (TRL): HTP REE detection
- 3,4,3-LI(1,2-HOPO) chelator for lanthanide fluorescence
- **METPO role:** Minimal (analytical chemistry focus)

**Task 1.3: HTP Strain Screening Pipeline (Ning Sun/Rita Kuo)**
- 6,000 samples/day automation capacity
- Automated E. coli transformation, colony picking, NGS validation
- Data processing pipelines for plate readers, HPLC, spectrometers
- **METPO role:** Annotates screened strains with phenotypes

### Task 2: AI/ML-Guided Microbial Engineering

**Task 2.1: Bacterial Strain Engineering (Cici Martinez-Gomez)**
- Engineer strains to hyperaccumulate REEs (Nd, Pr, Dy)
- Discover novel lanthanophore biosynthetic clusters
- Transcriptomic profiling + genomic analysis
- **METPO role:** Annotates metabolic and metal tolerance phenotypes

**Task 2.2: Fungal/Bacterial Chassis Expansion (Yasuo Yoshikuni)**
- CRAGE technology for extremophile domestication
- Acidithiobacillus (bioleaching), Methylobacterium (biosorption)
- Engineer acid/salt/temperature tolerance
- **METPO role:** Defines tolerance phenotypes (pH, temp, salinity ranges)

### Data Flow Diagram

```
Literature → Agentic AI → KG-CMREE ← Experimental Data
                ↓                          ↑
         Predictions              (Task 1.2, 1.3, 2.1, 2.2)
                ↓                          ↑
         Experiment Design → HTP Screening ↑
                                    ↓
                            Strain Validation
                                    ↓
                            REE Recovery!
```

**METPO's role:** Provides the semantic layer in KG-CMREE that connects:
- Genomic features → Phenotypic traits → REE recovery capabilities

---

## Next Steps for You (Mark)

### 1. Definition Completion (Priority)
- [ ] Review `high_confidence_definitions.tsv` - validate 9 proposals
- [ ] Review `definition_sources_needed.tsv` - assign sources to 54 terms
- [ ] Use `definition_proposals.tsv` for comprehensive view

### 2. ICBO Presentation Narrative

**Suggested Structure:**

1. **Context:** CMM project and critical minerals crisis
2. **Problem:** Existing phenotype ontologies inadequate (8.2% coherence, MicrO unmaintained)
3. **Solution:** METPO as focused, KG-optimized phenotype ontology
4. **Methods:** Vector search with ROI-based ontology selection
5. **Results:** 24 ontologies, 1,282 mappings, integrated into KG-CMREE
6. **Impact:** Enables AI-guided microbial strain design for REE recovery

**Key Messages:**
- METPO fills a real need in active DOE-funded research
- Pragmatic, data-driven approach (ROI analysis, embedding search)
- Integrated into larger AI/ML framework (not standalone)
- Acknowledges precedent while maintaining structural coherence

### 3. Integrate CMM Context into Background Doc
- Merge sections from this file into `icbo_2025_background_summary.md`
- Emphasize KG-CMREE extension of KG-Microbe
- Highlight agentic AI framework as cutting-edge application

---

## Scripts Available

- **notebooks/extract_definitions_from_mappings.py**
  - Analyzes SSSOM mappings
  - Proposes definitions and definition sources
  - Generates cross-references
  - Re-run anytime: `cd notebooks && uv run python extract_definitions_from_mappings.py`

---

## References for ICBO Talk

### CMM Project
- BER CMM Pilot Proposal (FY26): "Advanced Biorecovery of Critical Minerals through AI/ML-Guided Design of Microbial Chassis"
- DOE CMM Program: https://www.energy.gov/science/critical-minerals-and-materials-program

### KG-Microbe
- Joachimiak et al., 2021: "KG-Microbe: A Reference Knowledge-Graph and Platform for Harmonized Microbial Information" (CEUR-WS)
- Santangelo et al., 2025: KG-Microbe updates
- Caufield et al., 2023: KG-Hub
- Unni et al., 2022: Biolink Model
- GitHub: github.com/Knowledge-Graph-Hub/kg-microbe

### METPO Justification
- `docs/METPO_JUSTIFICATION.md`: Comprehensive ontology gap analysis
- `notebooks/ontology_removal_recommendation.md`: ROI analysis
- `notebooks/ONTOLOGY_SELECTION_SUMMARY.md`: Final decisions

### Related Publications
- Good et al., 2024: "Scalable and Consolidated Microbial Platform for Rare Earth Element Leaching and Recovery from Waste Sources" (Env Sci Tech)
- Zytnick et al., 2024: "Identification and characterization of a small-molecule metallophore involved in lanthanide metabolism" (PNAS)
- Müller et al., 2025: "Cost-effective urine recycling enabled by a synthetic osteoyeast platform" (Nature Commun)

---

## Questions?

Let me know if you need:
- Modified scripts
- Different analysis thresholds
- Additional data extraction
- Help integrating definitions into metpo_sheet.tsv
- Slide deck outline for ICBO
- Specific talking points about CMM integration
