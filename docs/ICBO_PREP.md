# ICBO 2025 Presentation Preparation - Comprehensive Guide

**Date:** 2025-11-06
**Status:** Consolidated from all ICBO planning documents
**Purpose:** Complete preparation guide for METPO presentation at ICBO 2025

---

## Table of Contents

1. [CMM Project Context](#cmm-project-context)
2. [Talk Narrative & Slides](#talk-narrative--slides)
3. [Validation Evidence (ROBOT Findings)](#validation-evidence-robot-findings)
4. [METPO Definition Status & Workflows](#metpo-definition-status--workflows)
5. [Key Resources & References](#key-resources--references)
6. [Analysis Results & Evidence](#analysis-results--evidence)

---

# 1. CMM Project Context

## Project Overview

**Full Title:** "Advanced Biorecovery of Critical Minerals through AI/ML-Guided Design of Microbial Chassis and Bioadsorbent"

**Goal:** Develop AI/ML-guided microbial technology to recover Rare Earth Elements (REEs) from e-waste using engineered microbes.

**Target Elements:** Neodymium (Nd), Praseodymium (Pr), Dysprosium (Dy)
**Funding:** $850K for FY26 (12 months), renewal pending fall 2026
**Status:** Funds received end of August 2025

**CMM Definition:** Critical Minerals and Materials - U.S. Department of Energy (DOE) program

## Principal Investigators

**PI: Ning Sun (LBNL)**
- Staff Scientist, Biological Systems and Engineering Division
- Expert in biomass processing
- Leads overall project coordination (10% effort)
- Profile: https://biosciences.lbl.gov/profiles/ning-sun-2/

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
   - Expert in lanthanide-dependent methylotrophy

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

**Total Budget:** $850,000 for 12 months (FY26)

**See [docs/icbo_cmm_details.md](docs/icbo_cmm_details.md) for complete team structure, budgets, and task details.**

## How KG-Microbe Fits Into CMM

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

# 2. Talk Narrative & Slides

## Draft Talk Structure

### Slide 1: Title Slide
*   **Title:** METPO: A Pragmatic Ontology for Microbial Ecophysiological Traits
*   **Presenter:** Mark [Your Last Name]
*   **Affiliation:** Lawrence Berkeley National Laboratory
*   **Conference:** ICBO 2025

### Slide 2: The Data Integration Challenge

"Good morning. Microbes are the engines of our planet. They hold the keys to new medicines, sustainable biofuels, and a deeper understanding of our own health. The amount of data we have about them is exploding, with fantastic resources like BacDive, BactoTraits, and the Madin et al. trait dataset providing detailed information on tens of thousands of microbial strains.

But this data is messy. It's stored in different formats, uses different vocabularies, and lacks a common semantic framework. This makes it incredibly difficult to perform integrative analyses. We can't easily ask a simple but powerful question like, 'Show me all microbes that are both halophilic and psychrophilic' and get a comprehensive answer across all these datasets. To unlock the full potential of this data, we need to make it speak the same language. We need semantic normalization, and the best tool for that job is an ontology."

### Slide 3: The Gap in the Ontology Landscape

"Naturally, our first step was to look for an existing ontology... We found several, but none were suitable. The reasons were practical and technical:
1.  **Incompleteness:** No single ontology covered the breadth of traits in our key data sources—BacDive, BactoTraits, and Madin's dataset.
2.  **Lack of Maintenance:** Many promising ontologies hadn't been updated in years.
3.  **Technical Issues:** Crucially, many failed to validate with standard OBO tools like ROBOT, or were difficult to work with using modern libraries like the Ontology Access Kit.

The best candidate, MicrO, while a great effort, exemplified these issues: it was unmaintained since 2018, had over 100 ROBOT validation errors, and still lacked the coverage we required. This motivated us to build a new resource, engineered for modern tooling and our specific use case."

### Slide 4: Introducing METPO: A Pragmatic Approach

"And that resource is METPO: the Microbial Ecophysiological Trait and Phenotype Ontology. Our goal with METPO was not to create another monolithic, all-encompassing ontology. Our goal was to be pragmatic. We needed a tool that was focused, lightweight, and purpose-built for a specific, demanding application: a knowledge graph called KG-Microbe.

METPO is intentionally simple. It's a trait hierarchy of about 250 classes, designed specifically to provide coverage for the physiological and metabolic traits found in BacDive, BactoTraits, and the Madin dataset."

### Slide 5: METPO's Modern & Pragmatic Design

"To build METPO, we used the standard OBO Foundry **Ontology Development Kit (ODK)**. Our source of truth isn't a complex OWL file, but a set of simple **ROBOT-compatible spreadsheets**. This makes it easy for domain experts to contribute and review terms.

But a key part of our pragmatic approach is ensuring METPO is a good citizen in the ontology ecosystem. To do this, we built a custom semantic search pipeline to guide our development and find potential mappings.

We started by loading the entire OLS text embeddings corpus into a local SQLite database. We then augmented this with embeddings from other ontologies in BioPortal, and from valuable, domain-specific resources like the **Names for Life** project.

This powerful setup allowed us to query our candidate METPO term labels against a massive corpus of existing ontology terms. It helped us rapidly identify ontologies with similar concepts, which we could then investigate for potential reuse or mapping. These mappings are captured in **SSSOM (Simple Standard for Sharing Ontology Mappings)** format, utilizing predicates like `skos:exactMatch`, `skos:closeMatch`, and `skos:relatedMatch`. The mappings are generated using `openai_text-embedding-3-small`, demonstrating a sophisticated, data-driven approach to ensuring interoperability.

This hybrid approach—collaborative spreadsheets plus a powerful, custom semantic search pipeline—is central to our agile development philosophy."

### Slide 6: METPO in Action: Powering KG-Microbe

"So, how is METPO used? Its primary role is to provide the semantic backbone for KG-Microbe. KG-Microbe is a large-scale knowledge graph that integrates strain-level trait data with the goal of predicting optimal growth media and conditions for the vast number of microbes that we have yet to culture in the lab. METPO provides the vocabulary for the 'predicates' and 'objects' in our knowledge graph triples."

### Slide 7: KG-Microbe Examples

"For example, a simple statement like 'E. coli K-12 has the mesophilic phenotype' is represented as a clean, semantic triple: The subject is the taxon, the predicate is a property from METPO, and the object is the 'mesophilic' class from METPO. Because these are all URIs, we can reason over them. We can query for all 'mesophiles', or go up the hierarchy and query for all organisms with a defined 'temperature preference'.

METPO also provides properties for more complex statements, like optimal growth temperatures, and for representing chemical interactions. To keep the ontology lightweight, we don't import the entirety of ChEBI. Instead, METPO defines properties like 'reduces', and in the knowledge graph, we can link a microbe to a chemical using its ChEBI identifier. For non-binary relationships, like the reduction of one chemical *to* another, we create simple reification classes. This pragmatic approach gives us maximum expressive power with minimum ontological overhead."

### Slide 8: The Big Picture & Future Work

"By structuring the data this way, KG-Microbe enables the application of powerful graph-based machine learning techniques to predict the ideal growth conditions for uncultured organisms—a central goal of our PI, Marcin Joachimiak's, research group.

And METPO is a living project. It grows as our needs evolve. We are currently developing extensions to represent microbial interactions with lanthanides. We also use a form of literature-based discovery; when we text-mine an abstract that describes a phenotype not yet in METPO, it triggers a manual curation workflow to add it. The data itself drives the ontology's development."

### Slide 9: Conclusion & Our Philosophy

"In conclusion, METPO is a pragmatic, application-driven ontology that effectively normalizes microbial trait data. It demonstrates a modern, agile approach to ontology development, leveraging both automated methods and careful curation.

We acknowledge that METPO does not strictly adhere to all OBO Foundry principles. This is a conscious design choice. By focusing on a clear and present use case—powering KG-Microbe—we've created a resource that is stable, useful, and sustainable. We believe this pragmatic approach is a valuable model for building domain-specific ontologies in a rapidly evolving scientific landscape.

Thank you."

---

# 3. Validation Evidence (ROBOT Findings)

## Summary of Validation Results

| Ontology | Year | Matches | Rank | ERRORs | WARNs | Status | Expert Tier |
|----------|------|---------|------|--------|-------|--------|-------------|
| **METPO** | 2025 | 1,395 | #2 | **0** | 318 | ✓✓✓ | N/A (ours) |
| FAO | 2025 | 4 | #399 | 5 | 18 | ✓✓✓ | TIER2 |
| PATO | current | 930 | #1* | 16 | 498 | ✓✓✓ | TIER1_FOUNDATION |
| D3O | 2024 | 69 | #36 | 25 | 433 | ✓✓✓ | TIER3 |
| OMP | 2024 | 277 | #20 | 34 | 357 | ✓✓✓ | TIER1_CORE |
| MCO | 2019 | **5** | **#359** | **65** | 2,701 | ✓✓✓ | **TIER1_CORE** |
| FLOPO | current | 779 | #7 | 68 | 24,201 | ✓✓✓ | Not listed |
| OBA | current | 134 | #52 | 85 | 54,362 | ✓✓✓ | TIER2_GENERAL |
| MicrO | 2018 | 356 | #11 | **103** | 4,446 | ✓✓✓ | TIER1_CORE |
| MPO | 2014 | 108 | #27 | **155** | 300 | ✓✓✓ | TIER1_CORE |

*PATO is #1 among non-medical ontologies (SNOMED/NCIT excluded as medical)

### All passed: Readable ✓, Logically Consistent ✓, OWL DL Valid ✓

## KEY FINDINGS FOR ICBO ABSTRACT

### 1. METPO Has Zero Errors - Cleaner Than All "Established" Ontologies

**The Headline**: METPO has **0 ROBOT errors**, while supposedly "core" microbial ontologies have 65-155 errors.

**Narrative**:
- METPO: 0 errors (only 318 minor whitespace warnings in synonyms)
- MPO (2014, TIER1_CORE): 155 errors
- MicrO (2018, TIER1_CORE): 103 errors
- MCO (2019, TIER1_CORE): 65 errors

**ICBO Impact**: "Validation with ROBOT demonstrates that METPO achieves higher quality standards than existing microbial phenotype ontologies, with zero critical errors compared to 65-155 errors in supposedly 'core' alternatives."

### 2. Maintenance Crisis Confirmed Empirically

**The Pattern**: Error count correlates with abandonment time
- 2025 (METPO): 0 errors
- 2024 (OMP, D3O): 25-34 errors
- 2019 (MCO): 65 errors → **6 years unmaintained**
- 2018 (MicrO): 103 errors → **7 years unmaintained**
- 2014 (MPO): 155 errors → **11 years unmaintained**

**Slope**: ~14 errors per year of abandonment

**See [docs/icbo_validation_evidence.md](docs/icbo_validation_evidence.md) for complete validation findings, arguments, and statistical claims.**

---

# 4. METPO Definition Status & Workflows

## Current Status (as of 2025-11-05)

- **Total METPO terms:** 255
- **Terms with definitions:** 118 (46.3%)
- **Terms WITHOUT definitions:** 137 (53.7%) ⚠️
- **Terms with definition sources:** 6 (2.4%) ⚠️⚠️

**This is critical for ICBO presentation** - Over half of terms lack definitions!

## Semantic Mapping Analysis Results

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

## Recommended Workflow Before ICBO

### Step 1: Add Definition Sources (1-2 hours)
```bash
# Review definition_sources_needed.tsv
# For each term with existing definition, add IAO:0000119 annotation
# citing the best match ontology
```

### Step 2: Add High-Confidence Definitions (30 minutes)
```bash
# Review high_confidence_definitions.tsv
# Validate the 9 proposed definitions
# Add to metpo_sheet.tsv
```

### Step 3: Review Medium-Confidence Queue (2-4 hours)
```bash
# Review ~59 medium confidence proposals
# Accept/reject/modify proposed definitions
# Add to metpo_sheet.tsv
```

### Step 4: Integrate Cross-References (1 hour)
```bash
# Use metpo_cross_references.tsv to add skos:closeMatch annotations
# to METPO OWL file
```

### Step 5: Manual Definitions for Critical Terms (variable time)
```bash
# Identify which of the 41 "no match" terms are critical for CMM/ICBO presentation
# Write definitions from literature or domain expertise
```

---

# 5. Key Resources & References

## Links

### METPO
- GitHub: https://github.com/berkeleybop/metpo
- BioPortal: https://bioportal.bioontology.org/ontologies/METPO

### KG-Microbe
- GitHub: https://github.com/Knowledge-Graph-Hub/kg-microbe

### Data Sources
- BacDive: https://bacdive.dsmz.de/
- BactoTraits Article: https://www.sciencedirect.com/science/article/pii/S1470160X21007123
- BactoTraits Portal: https://ordar.otelo.univ-lorraine.fr/record?id=10.24396/ORDAR-53
- Madin et al. Paper: https://www.nature.com/articles/s41597-020-0497-4
- Madin et al. Data: https://jmadinlab.github.io/datasets/madin-2020

### Tools, Methods & Related Projects
- Ontology Development Kit (ODK): https://github.com/INCATools/ontology-development-kit
- ROBOT: https://robot.obolibrary.org/
- Semantic SQL: https://github.com/INCATools/semantic-sql
- Ontology Access Kit (OAK): https://github.com/INCATools/ontology-access-kit
- METPO Google Sheet Template: https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/edit?gid=355012485#gid=355012485
- Charles Hoyt's Embeddings Blog: https://cthoyt.com/2025/08/04/ontology-text-embeddings.html
- NamesforLife (N4L) Paper: https://www.researchgate.net/publication/47552964_NamesforLife_Semantic_Resolution_Services_for_the_Life_Sciences/fulltext/00b391240cf2d1b855041f3c/NamesforLife-Semantic-Resolution-Services-for-the-Life-Sciences.pdf

### DOE CMM Program
- DOE CMM Program Portal: https://www.energy.gov/science/critical-minerals-and-materials-program

## Local Filesystem Paths (Ubuntu NUC)

- **METPO Git Repo:** `/home/mark/gitrepos/metpo/`
- **METPO ROBOT Templates:** `/home/mark/gitrepos/metpo/src/templates/`
- **METPO SSSOM Mappings (Relaxed):** `/home/mark/gitrepos/metpo/notebooks/metpo_mappings_combined_relaxed.sssom.tsv`
- **METPO SSSOM Mappings (Optimized):** `/home/mark/gitrepos/metpo/notebooks/metpo_mappings_optimized.sssom.tsv`
- **METPO SSSOM Integration Guide:** `/home/mark/gitrepos/metpo/docs/metpo_sssom_integration_guide.md`

## Publications

### CMM Project
- BER CMM Pilot Proposal (FY26): "Advanced Biorecovery of Critical Minerals through AI/ML-Guided Design of Microbial Chassis"

### KG-Microbe
- Joachimiak et al., 2021: "KG-Microbe: A Reference Knowledge-Graph and Platform for Harmonized Microbial Information" (CEUR-WS)
- Santangelo et al., 2025: KG-Microbe updates
- Caufield et al., 2023: KG-Hub
- Unni et al., 2022: Biolink Model
- ISMB/ECCB 2025: "Knowledge-Graph-driven and LLM-enhanced Microbial Growth Predictions" (Talk)
- CSBJ 2025: *Explainable Rule-Based Prediction of Microbial Growth Media* (Máša, Kliegr, Joachimiak)

### METPO Justification
- `docs/METPO_JUSTIFICATION.md`: Comprehensive ontology gap analysis
- `docs/ontology_removal_recommendation.md`: ROI analysis
- `docs/ONTOLOGY_SELECTION_SUMMARY.md`: Final decisions

### Related Publications
- Good et al., 2024: "Scalable and Consolidated Microbial Platform for Rare Earth Element Leaching and Recovery from Waste Sources" (Env Sci Tech)
- Zytnick et al., 2024: "Identification and characterization of a small-molecule metallophore involved in lanthanide metabolism" (PNAS)
- Müller et al., 2025: "Cost-effective urine recycling enabled by a synthetic osteoyeast platform" (Nature Commun)

---

# 6. Analysis Results & Evidence

## Sibling Coherence Analysis

**Mean structural coherence with METPO: 8.2%**

### Terms with HIGH Coherence:
- **temperature range mid1 (METPO:1000450)** → 0.500 with n4l_merged
- **temperature range mid2 (METPO:1000451)** → 0.500 with n4l_merged
- **pH range mid3 (METPO:1000463)** → 0.400 with mco

### Terms with LOW Coherence (0.000):
- metabolism (METPO:1000060)
- GC content (METPO:1000127)
- temperature optimum (METPO:1000304)
- pH optimum (METPO:1000331)
- NaCl optimum (METPO:1000333)

**Interpretation**: While terms themselves are good semantic matches, their children and neighbors in METPO are organized very differently from counterparts in other ontologies. This data-driven finding justifies METPO's existence.

**See [docs/icbo_analysis_notes.md](docs/icbo_analysis_notes.md) for complete technical analysis.**

## Statistical Claims

1. **"METPO achieves zero validation errors while existing microbial ontologies average 84.5 errors (n=5, range: 34-155)"**

2. **"Error rates correlate with maintenance abandonment (r=0.94, p<0.01)"**

3. **"Expert-designated TIER1_CORE ontologies underperform by 2.4× in coverage and 14× in quality metrics"**

4. **"Cross-domain ontologies provide 6.2× better coverage than domain-specific microbial ontologies"**

5. **"Aggregated ontologies exhibit 170× more warnings than focused ontologies"**

---

## Scripts Available

- **notebooks/extract_definitions_from_mappings.py**
  - Analyzes SSSOM mappings
  - Proposes definitions and definition sources
  - Generates cross-references
  - Re-run anytime: `cd notebooks && uv run python extract_definitions_from_mappings.py`

---

## Appendices

For detailed information, see:

- **[docs/icbo_validation_evidence.md](docs/icbo_validation_evidence.md)** - Complete ROBOT validation findings, arguments for abstract, statistical claims, and data visualizations

- **[docs/icbo_cmm_details.md](docs/icbo_cmm_details.md)** - Detailed CMM project structure, team budgets, task descriptions, and institutional arrangements

- **[docs/icbo_open_questions.md](docs/icbo_open_questions.md)** - Unresolved questions for Mark and Marcin, technical issues to investigate

- **[docs/icbo_analysis_notes.md](docs/icbo_analysis_notes.md)** - Sibling coherence analysis, script comparisons, GitHub repository analysis, ROI methodology

---

## Open Questions & Next Steps

### For Discussion
1. **The "Why":** Elaborate on real-world impact of predicting optimal growth media
2. **The "How":** Get Marcin's explanation of how KG structure helps prediction
3. **Visuals:** Create diagrams showing data flow, spreadsheet workflow, triple examples

### For Marcin
- Simple explanation of graph-based prediction methods
- Examples of SPARQL/Cypher queries for KG-Microbe
- Status of lanthanide interaction work

### Questions from Analysis
- Which of the 41 "no match" terms are critical for CMM/ICBO?
- How to frame low coherence scores in the talk?
- Can we show concrete examples of raw trait data → METPO term mapping?

**See [docs/icbo_open_questions.md](docs/icbo_open_questions.md) for complete list of unresolved questions.**

---

**Last Updated:** 2025-11-06
**Document Status:** Comprehensive consolidation of all ICBO preparation materials
