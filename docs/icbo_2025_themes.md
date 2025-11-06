# ICBO 2025 Themes Analysis

**Issue:** #287
**Purpose:** Identify themes requested/relevant for ICBO 2025 presentation
**Date:** 2025-11-06

---

## Workshops You're Attending

Based on your registration, you signed up for these workshops:

1. **Accelerating Ontology Curation with Agentic AI and GitHub** (Nov 18)
   - Theme: AI-assisted ontology development
   - Relevance to METPO: You used LLM-assisted curation (0 errors vs 34-155 in traditional)

2. **Annotating Data with Ontologies: LinkML Can Help** (Nov 5)
   - Theme: Data annotation and ontology integration
   - Relevance to METPO: METPO annotates BacDive, BactoTraits, Madin datasets

3. **Workshop on the Core Ontology for Biology and Biomedicine**
   - Theme: OBO Foundry interoperability and adoption
   - Relevance to METPO: Your pragmatic approach vs strict OBO adherence

4. **Food, Waste, and Sustainability** (Nov 14)
   - Theme: Sustainability ontologies
   - Relevance to METPO: Less direct, but CMM/critical minerals ties to sustainability

5. **14th Vaccine and Drug Ontology Studies (VDOS)** (Nov 7)
   - Theme: AI in ontology research, drug/vaccine representation
   - Relevance to METPO: Microbial traits relevant to vaccine/drug development

6. **The 9th International CELLS Workshop**
   - Theme: Cell biology ontologies
   - Relevance to METPO: Microbial cells, cellular processes

---

## Main Conference Themes (From Schedule)

### Day 1 (Sunday, Nov 9) Themes:
- **Keynote:** "Conspiracy theories: Are ontologies really under attack?" (Mark Musen)
- Ontology applications in disease risk prediction
- BFO and foundational ontologies
- Document analysis for ontology development
- Active/living organism ontologies
- Traditional medicine integration
- Ontology selection and term choice
- Vaccine adverse events
- PICO/PECO-guided LLM extraction

### Day 2 (Monday, Nov 10) Themes:
- **Keynote:** "Bridging Industry and Ontology" (Giovanni Nisato)
- **Workshop:** AI, Ontologies, and the Next Generation of Researchers
- Microbiome ontologies
- Concept discovery with machine learning
- Agentic workflows for ontology annotation
- Clinical decision support systems
- Data model-based ingestion pipelines
- SNOMED CT semantic analysis
- AI support in ontology construction

### Day 3 (Tuesday, Nov 11) - YOUR DAY! Themes:
- **Keynote:** "Ontologies for Semantic Interoperability in the Age of AI" (Michel Dumontier)
- Bioassay ontologies
- Healthcare/dental ontologies
- Rare disease data annotation
- Browser-based ontology development tools
- Visual standards for anatomical knowledge
- **Your talk:** METPO
- Statistical ontologies and fMRI
- Knowledge graph systems
- Bioprocessing ontologies

---

## Emerging Themes Across ICBO 2025

### 1. AI and LLMs in Ontology Development ⭐⭐⭐
**Highly Relevant to METPO**
- Multiple workshops on agentic AI, LLMs, prompt engineering
- Your METPO uses LLM-assisted curation
- Argument 4 in validation evidence: "LLM-assisted development produces higher quality"

**How METPO addresses this:**
- 0 errors with LLM assistance vs 34-155 with traditional curation
- Undergraduate-accessible workflows democratize contribution
- Sophisticated semantic search pipeline using embeddings

### 2. Pragmatic/Application-Driven Ontology Development ⭐⭐⭐
**Core METPO Philosophy**
- Tension between OBO Foundry principles and practical needs
- Industry needs (keynote on bridging industry and ontology)
- Real-world applications vs theoretical purity

**How METPO addresses this:**
- "We acknowledge that METPO does not strictly adhere to all OBO Foundry principles"
- Purpose-built for KG-Microbe (clear use case)
- Focused on coverage gaps, not comprehensive modeling

### 3. Ontology Quality and Maintenance ⭐⭐⭐
**METPO's Strongest Argument**
- Your validation evidence shows maintenance crisis
- 14 errors per year of abandonment
- Expert assessments fail to predict utility

**How METPO addresses this:**
- 0 ROBOT errors vs 65-155 in "core" ontologies
- Active maintenance commitment
- Modern tooling (ODK, ROBOT, OAK)

### 4. Semantic Interoperability ⭐⭐⭐
**Keynote Theme for Your Day**
- Data integration across sources
- SSSOM mappings
- Knowledge graphs

**How METPO addresses this:**
- Integrates BacDive, BactoTraits, Madin
- 158 terms mapped to 24 external ontologies
- Powers KG-Microbe for semantic queries

### 5. Domain-Specific vs General Ontologies ⭐⭐
**Interesting Tension**
- When to build new vs reuse existing
- Cross-domain spillover (plant ontologies for microbial traits!)

**How METPO addresses this:**
- Coverage analysis: 154 ontologies needed for 90% metabolism coverage
- FLOPO (plant) outperforms MCO (microbial) - surprising finding
- Strategic: import well-covered domains, curate fragmented areas

### 6. Community and Democratization ⭐⭐
**Workshop Theme**
- Next generation of researchers
- Lowering barriers to entry
- Collaborative workflows

**How METPO addresses this:**
- ROBOT-compatible spreadsheets (not complex OWL)
- Google Sheets for domain expert contribution
- Undergraduate-accessible LLM workflows

---

## Themes MISSING from METPO Coverage

### 1. Clinical Applications
- METPO is research-focused (CMM, KG-Microbe)
- Could mention potential for microbiome health applications
- Vaccine/drug development relevance (lanthanophore work)

### 2. BFO/Upper-Level Ontology Integration
- METPO is pragmatic, not BFO-aligned
- COB workshop focuses on this
- Could be a discussion point: when is BFO necessary?

### 3. Industry Adoption
- Monday keynote on industry-ontology bridge
- METPO is academic/DOE-funded
- Could mention: open data, BioPortal availability

### 4. Ethical/Governance Issues
- Workshop on AI ethics and governance
- METPO doesn't address this directly
- Could mention: open source, community governance principles

---

## Recommended Talk Adjustments Based on Themes

### Emphasize These Points:
1. **LLM-assisted development** - Ties to multiple workshops and talks
2. **Maintenance crisis** - Quantified evidence of ontology abandonment
3. **Pragmatic approach** - Balancing principles with practical needs
4. **Semantic interoperability** - Direct tie to Day 3 keynote theme
5. **Validation-driven decisions** - Empirical evidence > expert opinion

### Consider Adding:
1. **Future work slide:** How METPO could integrate with COB/BFO
2. **Industry relevance:** DOE funding, critical minerals applications
3. **Community governance:** How METPO handles contributions, quality control
4. **Comparison to AI approaches:** Your pipeline vs pure LLM extraction

### De-emphasize (unless asked):
1. **Technical details** of semantic search pipeline
2. **Deep ontology philosophy** (audience may be mixed)
3. **Exhaustive validation statistics** (keep to key findings)

---

## Questions You Might Get Based on Conference Themes

### 1. About LLMs/AI (Likely!)
- "How do you prevent hallucinations in LLM-assisted curation?"
- "What role does human expert review play?"
- "Could this approach work for other domains?"

### 2. About OBO Foundry (Possible)
- "Why not align with existing ontologies like MicrO or MPO?"
- "What about BFO/COB integration?"
- "Is fragmenting the ontology landscape helpful?"

### 3. About Maintenance (Possible)
- "How do you ensure METPO won't be abandoned too?"
- "What's your governance model?"
- "Who decides what goes into METPO?"

### 4. About Applications (Likely!)
- "What predictions has KG-Microbe made?"
- "Can this work for human microbiome?"
- "What about clinical applications?"

---

## Action Items for Issue #287

- [x] Identify workshop themes
- [x] Map METPO strengths to conference themes
- [x] Identify gaps in METPO coverage
- [x] Recommend talk adjustments
- [x] Prepare for likely questions

**Recommendation:** Keep your current 9-slide structure, but ensure you emphasize the themes that align with ICBO 2025 focus areas, especially AI/LLM assistance, maintenance crisis, and pragmatic development.
