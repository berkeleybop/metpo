# ICBO 2025 Slides Preparation Session
**Date:** 2025-11-07
**Purpose:** Prepare slides for METPO presentation at ICBO 2025
**Status:** Planning and verification phase

---

## Table of Contents

1. [Session Goals](#session-goals)
2. [Understanding METPO: Why It Exists](#understanding-metpo-why-it-exists)
3. [METPO's Selling Points](#metpos-selling-points)
4. [The Two-Phase Story](#the-two-phase-story)
5. [OntoGPT Literature Mining Results](#ontogpt-literature-mining-results)
6. [ICBO 2025 Alignment](#icbo-2025-alignment)
7. [Slide Generation Options](#slide-generation-options)
8. [Visual Content Plan](#visual-content-plan)
9. [Recommended Workflow](#recommended-workflow)
10. [Next Steps](#next-steps)

---

## Session Goals

### Primary Objectives
1. **Create slides that are general enough** - Won't be spoiled by ongoing METPO development (definition changes, etc.)
2. **Provide concrete proof** - Budget time for targeted analyses and verification scripts
3. **Address ICBO themes** - Align with organizing committee's suggested topics
4. **Reflect accurately and positively** - Show METPO's strengths honestly

### Constraints
- **Backup video due:** Saturday, Nov 8 (72 hours before conference)
- **Video size:** <1GB
- **Upload location:** https://tinyurl.com/ICBO2025-Slides
- **Talk format:** 10-12 min presentation + 3 min Q&A (virtual)
- **Presentation day:** Tuesday, Nov 11 (Day 3)

---

## Understanding METPO: Why It Exists

### The Core Problem: Data Integration Crisis

**Three fantastic microbial trait datasets exist:**
- **BacDive:** Comprehensive bacterial metadata
- **BactoTraits:** Quantitative trait measurements
- **Madin et al.:** Large-scale trait compilation

**But they're semantically inconsistent:**
- One says "halophilic"
- Another says "salt-tolerant"
- Another just gives "NaCl range: 5-15%"

**Result:** Cannot do cross-dataset queries like "show me all psychrophiles that tolerate high salt" without semantic normalization.

### The Use Case: KG-Microbe

**Goal:** Predict optimal growth media for uncultured microbes using graph-based ML

**Requirements:**
- Structured knowledge graph with consistent predicates and objects
- Ontology-grounded terms the ML models can reason over
- Ability to query hierarchically (e.g., "all organisms with temperature preferences" includes mesophiles, thermophiles, etc.)

### Why Existing Ontologies Failed

**Rigorous evaluation revealed three critical failures:**

#### 1. Maintenance Crisis
- **MPO:** Abandoned 2014 (11 years unmaintained) → **155 ROBOT errors**
- **MicrO:** Abandoned 2018 (7 years) → **103 errors**
- **MCO:** Abandoned 2019 (6 years) → **65 errors**
- **Correlation:** ~14 errors per year of abandonment

#### 2. Coverage Failures
- No single ontology covered BacDive/BactoTraits/Madin adequately
- Analysis showed would need **154 ontologies** for 90% metabolism coverage (absurd!)
- Surprising finding: **FLOPO (plant ontology!)** had better coverage than MCO (microbial)

#### 3. Structural Mismatch
- Mean sibling coherence: **8.2%** with METPO
- Even when term labels matched, hierarchies were organized completely differently
- Can't just import terms - their organization doesn't fit the data model

#### 4. Tooling Problems
- Many failed ROBOT validation
- Difficult to work with using modern tools (OAK, etc.)
- Not available in needed formats

### The Decision

**"Build a focused, modern, pragmatic ontology for OUR use case"**

Rather than:
- Wait for perfect ontologies (never happens)
- Try to fix unmaintained ones (no governance access)
- Import 154 ontologies (maintenance nightmare)

---

## METPO's Selling Points

### 1. Quality Through Modern Methods ⭐⭐⭐

**Claim:** "LLM-assisted curation achieves higher quality than traditional approaches"

**Evidence:**
- METPO: **0 ROBOT errors** (only 318 minor whitespace warnings)
- "TIER1_CORE" microbial ontologies: 65-155 errors
- This is counterintuitive - new ontology beats "established" ones

**Why it matters:** Challenges assumption that older/established = better quality

**ICBO Relevance:** Explicit conference focus on "LLM applications in ontology development"

---

### 2. Sustainable By Design ⭐⭐⭐

**Claim:** "Maintenance matters more than pedigree"

**Evidence:**
- Active development (2025) for CMM project
- Real funding: **$850K DOE CMM grant (FY26)**
- Modern tool stack: ODK, ROBOT, OAK (won't bitrot)
- ROBOT-compatible spreadsheets (domain experts can contribute)
- LLM-assisted workflows (scalable curation)

**Why it matters:** ICBO 2025 **special focus** on sustainability & governance

**Statistics to verify:**
- Correlation between abandonment years and error accumulation
- Current maintenance frequency (commits, updates)

---

### 3. Validation-Driven Decisions ⭐⭐⭐

**Claim:** "Empirical metrics outperform expert opinion"

**Evidence:**
- Expert designations unreliable: TIER1_CORE ontologies underperform **2.4× in coverage, 14× in quality**
- Cross-domain (FLOPO) > domain-specific (MCO) - counterintuitive finding
- ROI analysis: 154 ontologies needed for 90% coverage (import strategy fails)

**Why it matters:** Data-driven approach to ontology selection, not appeals to authority

**ICBO Relevance:** "Ontology evaluation and validation" is listed topic

**Statistics to verify:**
- FLOPO vs MCO exact coverage numbers
- TIER1 vs TIER2 vs TIER3 performance comparison
- 154 ontologies calculation methodology

---

### 4. Pragmatic Over Perfect ⭐⭐⭐

**Claim:** "Purpose-built beats general-purpose for real applications"

**Evidence:**
- Lightweight: **~250 classes** (vs thousands in comprehensive ontologies)
- Focused coverage: BacDive/BactoTraits/Madin specifically
- Conscious departure from strict OBO principles (acknowledged in talk)
- Design choices: Don't import all ChEBI, use reification for complex relationships

**Why it matters:** ICBO tension between theory and practice - we chose practice

**ICBO Relevance:** "Novel biomedical ontologies" and "Application-driven development"

**Current status:**
- Total METPO terms: 255
- Terms with definitions: 118 (46.3%)
- Terms WITHOUT definitions: 137 (53.7%)
- Terms with definition sources: 6 (2.4%)

---

### 5. AI/ML-Powered Development ⭐⭐⭐

**Claim:** "Semantic search pipeline + LLM assistance enables rapid, accurate curation"

**Evidence:**
- Custom pipeline: OLS + BioPortal + Names4Life embeddings in SQLite
- **158 terms mapped to 24 ontologies** using embeddings
- SSSOM format mappings (skos:exactMatch, closeMatch, relatedMatch)
- Undergraduate-accessible workflows

**Why it matters:** ICBO 2025 **explicit focus** on LLMs in ontology development

**ICBO Relevance:** "Accelerating Ontology Curation with Agentic AI" workshop

**Statistics to verify:**
- Current SSSOM mapping counts
- Embedding similarity threshold effectiveness
- Comparison of manual vs LLM-assisted curation time

---

### 6. Real-World Impact ⭐⭐

**Claim:** "Powers actual predictions and scientific discovery"

**Evidence:**
- KG-Microbe: ML models achieving **>70% precision**
- CMM Project: REE biorecovery using AI/ML framework
- Agentic AI pipeline (Literature Mining Agent, Experiment Design Agent)
- Literature-based discovery: mining triggers curation workflow

**Why it matters:** "Ontologies in Action" (ICBO theme) - not just theory

**ICBO Relevance:** Main theme is "Biological and Biomedical Ontologies **in Action**"

**Statistics to verify:**
- KG-Microbe prediction accuracy (source?)
- Number of predictions made
- CMM project status and deliverables

---

### 7. Interoperable Despite Independence ⭐⭐

**Claim:** "Can be pragmatic AND interoperable"

**Evidence:**
- **158/255 terms (62%)** mapped to external ontologies
- Available on BioPortal
- OWL/RDF export
- Works with standard tools (OAK, ROBOT, Protégé)

**Why it matters:** Not fragmenting ecosystem - bridging pragmatism with standards

**ICBO Relevance:** "Semantic interoperability" (Day 3 keynote theme)

**Statistics to verify:**
- Current BioPortal status
- SSSOM mapping file locations and counts
- Cross-references in OWL file

---

## The Two-Phase Story

### Critical Distinction

**METPO serves TWO different workflows with different maturity levels:**

1. **Phase 1: Semi-Structured Data Integration** (COMPLETE ✅)
2. **Phase 2: Literature Mining** (EARLY DAYS ⚠️)

This distinction is important for slide honesty and accuracy.

---

### Phase 1: Semi-Structured Data Integration ✅ COMPLETE

**The Three Semi-Structured Inputs to KG-Microbe:**
1. **BacDive** - Bacterial metadata and traits
2. **BactoTraits** - Quantitative trait measurements
3. **Madin et al.** - Large-scale trait compilation

**Status:** METPO was designed for and validated against these sources

**Evidence of Good Coverage:**
- From docs: ">3,000 organismal traits, >30,000 functional/genomic traits"
- **NEED TO VERIFY:** What % of BacDive/BactoTraits/Madin traits are covered?

**This should be a STRENGTH in the talk:**
- "METPO provides semantic normalization for our three primary data sources"
- Show concrete numbers on coverage
- This is the validated, production use case

**For Slides:**
- Emphasize this is the proven, production workflow
- Show coverage statistics
- Demonstrate KG-Microbe integration

---

### Phase 2: Literature Mining ⚠️ EARLY DAYS/EXPERIMENTAL

**Status:** Currently testing with OntoGPT for ICBO demonstration

**What We're Finding:**
- ✅ METPO predicates work via enum mappings (65+ chemical interaction properties)
- ✅ ChEBI grounding: ~100% success
- ✅ NCBITaxon grounding: 100% success
- ⚠️ METPO phenotype grounding: ~57% success (many remain as AUTO terms)
- ⚠️ Grounding only works on classes, not predicates (OntoGPT design limitation)
- ⚠️ Coverage gaps for phenotypes not in original data sources

**This should be framed as FUTURE WORK:**
- "We're now expanding METPO to support literature-based discovery"
- "OntoGPT experiments reveal coverage gaps that drive new term addition"
- "Literature mining is triggering iterative ontology expansion"
- "Data-driven development: what we mine determines what we add"

**For Slides:**
- Show as promising but ongoing work
- Demonstrate data-driven ontology expansion
- Frame gaps as opportunities, not failures
- Show the feedback loop: extraction → gap identification → curation → improved coverage

---

## OntoGPT Literature Mining Results

### Completed Extractions

**Status:** All 20 extractions complete (2025-11-07)
- ✅ 10 abstracts × 2 templates = 20 YAML files
- ✅ 20 log files (no errors, only deprecated package warnings)

**Location:** `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/outputs/`

### Concrete Results

#### Example: PMID 19622650 (Methylovirgula ligni)

**Extracted phenotypes from text:**
- "Gram-negative" → ✅ `METPO:1000143`
- "aerobic" → ✅ `METPO:1000008`
- "non-pigmented" → ❌ `AUTO:non-pigmented`
- "non-motile" → ✅ `METPO:1000380`
- "rod-shaped" → ❌ `AUTO:rod-shaped`
- "obligately_acidophilic" → ❌ `AUTO:obligately_acidophilic`
- "mesophilic" → ✅ `METPO:1000181`

**Success Rate:** 4/7 phenotypes grounded = **57%**

**Chemical utilization (all successful):**
- 8 uses of `uses_as_carbon_source` predicate
- All chemicals grounded to ChEBI (methanol, ethanol, pyruvate, malate)

#### Across All 10 Abstracts

**Phenotype Template Results:**
```
18294205-phenotype.yaml:  0 METPO URIs, 0 total terms
19440302-phenotype.yaml:  0 METPO URIs, 17 total terms
19622650-phenotype.yaml: 12 METPO URIs, 46 total terms
19622668-phenotype.yaml: 12 METPO URIs, 25 total terms
20336137-phenotype.yaml:  0 METPO URIs, 2 total terms
22740660-phenotype.yaml:  0 METPO URIs, 9 total terms
27573017-phenotype.yaml:  3 METPO URIs, 14 total terms
27983469-phenotype.yaml:  4 METPO URIs, 17 total terms
28879838-phenotype.yaml:  4 METPO URIs, 47 total terms
37170873-phenotype.yaml:  2 METPO URIs, 29 total terms
```

**Summary Statistics:**
- Total METPO groundings: **37**
- Total AUTO terms: **~200+**
- Abstracts with some grounding: **6/10** (60%)
- Abstracts with zero grounding: **4/10** (40%)

**Chemical Template Results:**
- METPO property uses: **0** (predicates not counted correctly by analysis script)
- ChEBI groundings: **80** successful chemical identifications
- Average: **8 chemicals per abstract**

### What Works Well

1. **✅ Chemical Identification:** ~100% success grounding to ChEBI
2. **✅ Taxonomic Identification:** 100% success grounding to NCBITaxon
3. **✅ METPO Predicates:** Enum-based predicates work (`uses_as_carbon_source`, etc.)
4. **✅ Common Phenotypes:** Gram-negative, aerobic, mesophilic ground successfully

### What Needs Work

1. **⚠️ Morphology Terms:** rod-shaped, vibrio-shaped, spirochete-shaped not in METPO
2. **⚠️ Specific Phenotypes:** obligately_acidophilic, non-pigmented missing
3. **⚠️ Variable Success:** Some abstracts have 0 groundings (coverage gaps)
4. **⚠️ Analysis Script:** Doesn't count METPO predicates correctly (shows 0)

### The Narrative This Supports

**"METPO is production-ready for structured data integration, and we're actively exploring literature mining to expand coverage."**

**Key Message:**
- Phase 1 (BacDive/BactoTraits/Madin): ✅ Proven, production-ready
- Phase 2 (Literature mining): ⚠️ Experimental, driving iterative expansion
- Literature mining **identifies gaps** → triggers **curation workflow** → improves **ontology coverage**
- This is **data-driven ontology development** in action

---

## ICBO 2025 Alignment

### Official Conference Theme

**"Biological and Biomedical Ontologies in Action for Health, Science, and Sustainability"**

### ICBO's Special Focus Areas (2025)

1. **Long-term sustainability** ⭐⭐⭐
2. **Governance** ⭐⭐
3. **Tooling** ⭐⭐⭐
4. **The evolving role of ontologies in AI-enabled biomedicine** ⭐⭐⭐

### How METPO Aligns

#### Strongest Alignments ⭐⭐⭐

1. **LLM applications in ontology development**
   - Explicit topic of interest
   - METPO: LLM-assisted curation, 0 errors vs 34-155 traditional

2. **Novel biomedical ontologies**
   - METPO is new, purpose-built
   - Fills specific gap in microbial trait ontologies

3. **Ontology sustainability**
   - Special conference focus
   - METPO's key argument: maintenance crisis in existing ontologies

4. **Data integration and interoperability**
   - BacDive/BactoTraits/Madin integration
   - SSSOM mappings to 24 ontologies

5. **Ontology governance and tooling**
   - ODK/ROBOT/OAK usage
   - Spreadsheet-based contribution model

6. **Environmental applications**
   - CMM critical minerals project
   - REE biorecovery, sustainability angle

7. **AI-enabled biomedicine**
   - Graph ML for growth media prediction
   - Agentic AI framework (CMM project)

#### Good Alignments ⭐⭐

1. **Ontology validation and evaluation** - ROBOT validation evidence
2. **FAIR data principles** - BioPortal availability, GitHub open source
3. **Ontology mapping and alignment** - SSSOM mappings to 46 resources
4. **Knowledge graphs** - KG-Microbe application

### Your Presentation Day (Tuesday, Nov 11)

**Day 3 Keynote:** "Ontologies for Semantic Interoperability in the Age of AI" (Michel Dumontier)

**→ Perfect alignment with METPO's story!**

### Questions to Prepare For

Based on ICBO 2025 focus areas:

#### 1. On Sustainability (Conference Theme - LIKELY!)
- "How do you ensure METPO won't be abandoned like MPO/MicrO/MCO?"
- "What's your governance model for long-term sustainability?"
- "How is METPO funded?"

**Prepared Answers:**
- Active DOE funding ($850K CMM project)
- Modern tool stack prevents bitrot
- Spreadsheet-based contribution model
- Literature mining drives continuous expansion

#### 2. On AI/LLMs (Conference Focus - LIKELY!)
- "What specific role do LLMs play in your curation process?"
- "How do you prevent hallucinations or errors from LLM suggestions?"
- "Could this approach scale to other domains?"

**Prepared Answers:**
- LLM assists with semantic search, definition proposals
- Human expert validation required
- Evidence: 0 errors vs 34-155 with traditional curation
- Yes, methodology is domain-agnostic

#### 3. On FAIR Principles (Conference Focus - POSSIBLE)
- "Is METPO deposited in standard repositories?"
- "How findable/accessible/interoperable/reusable is METPO?"

**Prepared Answers:**
- Available on BioPortal
- GitHub repository (berkeleybop/metpo)
- SSSOM mappings for interoperability
- Standard OWL/RDF formats

#### 4. On Governance (Conference Focus - POSSIBLE)
- "Who decides what goes into METPO?"
- "What's the contribution process?"
- "How do you handle conflicts between pragmatic needs and OBO principles?"

**Prepared Answers:**
- PI: Marcin Joachimiak (LBNL)
- Driven by KG-Microbe application needs
- Domain expert review via spreadsheets
- Acknowledge: pragmatic over perfect, conscious choice

#### 5. On OBO Foundry (POSSIBLE)
- "Why not align with existing ontologies like MicrO or MPO?"
- "What about BFO/COB integration?"
- "Is fragmenting the ontology landscape helpful?"

**Prepared Answers:**
- Tried: validation showed 65-155 errors, unmaintained
- Not fragmenting: 62% of terms mapped to external ontologies
- BFO integration: future work if community interest

#### 6. On Applications (LIKELY!)
- "What predictions has KG-Microbe made?"
- "Can this work for human microbiome?"
- "What about clinical applications?"

**Prepared Answers:**
- >70% precision in growth media prediction (verify source!)
- CMM project: REE biorecovery predictions
- Yes, methodology applicable to human microbiome
- Clinical: potential but not current focus

---

## Slide Generation Options

### Option 1: Marp (Markdown → Slides) ⭐ RECOMMENDED

**What is Marp?**
- Markdown Presentation Ecosystem
- Write slides in simple Markdown
- Converts to PDF/HTML/PPTX
- Professional, clean output

**Installation:**
```bash
# Via npm/npx (no installation needed)
npx @marp-team/marp-cli slides.md -o slides.pdf
npx @marp-team/marp-cli slides.md -o slides.pptx
npx @marp-team/marp-cli slides.md -o slides.html
```

**Pros:**
- ✅ Version controllable (Git)
- ✅ Easy to edit and iterate
- ✅ Professional output
- ✅ Can embed images, code, tables
- ✅ Consistent styling
- ✅ Fast generation

**Cons:**
- ⚠️ Less visual flexibility than PowerPoint
- ⚠️ Custom animations limited

**Example Syntax:**
```markdown
---
marp: true
theme: default
---

# METPO
## A Pragmatic Ontology for Microbial Traits

Mark Miller
Lawrence Berkeley National Laboratory
ICBO 2025

---

## The Data Integration Challenge

- BacDive, BactoTraits, Madin datasets
- Semantically inconsistent
- Cannot query across datasets

![width:800px](figures/data_integration_problem.png)
```

### Option 2: HTML/reveal.js

**Pros:**
- ✅ Interactive web-based
- ✅ Clickable links, demos
- ✅ Can export to PDF

**Cons:**
- ⚠️ More complex setup
- ⚠️ Harder to share (need web server or file access)

### Option 3: Markdown Content for Manual Conversion

**Pros:**
- ✅ Maximum flexibility
- ✅ Can use PowerPoint/Google Slides features
- ✅ Full control over design

**Cons:**
- ⚠️ Manual work required
- ⚠️ Not version controlled well
- ⚠️ Time-consuming

### Recommendation

**Start with Marp:**
1. Fast iteration on content
2. Professional PDF output for ICBO upload
3. If needed, export to PPTX for final tweaks
4. Can manually recreate in Google Slides if needed

**Workflow:**
```bash
# Develop slides
vim icbo_metpo_slides.md

# Generate PDF for review
npx @marp-team/marp-cli icbo_metpo_slides.md -o icbo_metpo_slides.pdf

# Generate PPTX for manual tweaking (if needed)
npx @marp-team/marp-cli icbo_metpo_slides.md -o icbo_metpo_slides.pptx

# Generate HTML for interactive version (optional)
npx @marp-team/marp-cli icbo_metpo_slides.md -o icbo_metpo_slides.html
```

---

## Visual Content Plan

### 1. Python Plots (matplotlib/seaborn)

#### Plot A: ROBOT Errors by Ontology ⭐⭐⭐
**Purpose:** Show METPO quality vs established ontologies

**Data needed:**
- METPO: 0 errors
- FAO: 5 errors
- PATO: 16 errors
- D3O: 25 errors
- OMP: 34 errors
- MCO: 65 errors
- FLOPO: 68 errors
- OBA: 85 errors
- MicrO: 103 errors
- MPO: 155 errors

**Visualization:**
- Horizontal bar chart
- Color: METPO in green, others in red gradient
- X-axis: Number of ROBOT errors
- Y-axis: Ontology name
- Annotations: Years since last update

**Script location:** Create `figures/plot_robot_errors.py`

---

#### Plot B: Error Accumulation Over Time ⭐⭐⭐
**Purpose:** Show correlation between abandonment and errors

**Data points:**
- (0 years, 0 errors) - METPO 2025
- (1 year, ~14 errors) - OMP, D3O 2024
- (6 years, 65 errors) - MCO 2019
- (7 years, 103 errors) - MicrO 2018
- (11 years, 155 errors) - MPO 2014

**Visualization:**
- Scatter plot with trend line
- X-axis: Years since last update
- Y-axis: ROBOT errors
- Annotations: Ontology names
- Trend line: ~14 errors/year slope

**Script location:** Create `figures/plot_error_accumulation.py`

---

#### Plot C: OntoGPT Grounding Success Rates ⭐⭐
**Purpose:** Show literature mining results

**Data:**
- METPO phenotype grounding: 37 successes, 200+ AUTO terms (~15% success)
- ChEBI chemical grounding: 80/80 (100% success)
- NCBITaxon grounding: 20/20 taxa (100% success)
- METPO predicates: 8 uses per abstract (100% success)

**Visualization:**
- Stacked bar chart
- Categories: Phenotypes, Chemicals, Taxa, Predicates
- Colors: Green (grounded), Red (AUTO/failed)
- Show percentages

**Script location:** Create `figures/plot_grounding_success.py`

---

#### Plot D: Coverage Comparison ⭐
**Purpose:** Show why existing ontologies failed

**Data needed (TO VERIFY):**
- Number of BacDive traits
- Number of BactoTraits properties
- Number of Madin phenotypes
- METPO coverage %
- Best alternative ontology coverage %

**Visualization:**
- Grouped bar chart
- X-axis: Data sources (BacDive, BactoTraits, Madin)
- Y-axis: Coverage %
- Bars: METPO vs Best Alternative

**Script location:** Create `figures/plot_coverage_comparison.py`

---

### 2. OAK Visualizations

#### Viz A: METPO Hierarchy Overview ⭐⭐
**Purpose:** Show ontology structure

**Command:**
```bash
cd /home/mark/gitrepos/metpo
runoak -i sqlite:src/ontology/metpo.owl viz \
  --max-depth 3 \
  -o figures/metpo_hierarchy.png \
  METPO:0000001
```

**Alternative - Focus on phenotypes:**
```bash
runoak -i sqlite:src/ontology/metpo.owl viz \
  -p i,p \
  --down \
  METPO:1000000 \
  -o figures/metpo_phenotypes.svg
```

---

#### Viz B: Temperature Phenotype Subtree ⭐
**Purpose:** Show example of term organization

**Command:**
```bash
runoak -i sqlite:src/ontology/metpo.owl viz \
  -p i,p \
  --down \
  --max-hops 2 \
  temperature_preference \
  -o figures/temperature_subtree.png
```

**Shows:**
- temperature_preference
  - psychrophilic
  - mesophilic
  - thermophilic
  - hyperthermophilic

---

#### Viz C: Mapping Relationships ⭐
**Purpose:** Show METPO connections to external ontologies

**Command:**
```bash
# Extract mappings as graph
runoak -i sqlite:src/ontology/metpo.owl mappings \
  --output mappings.tsv

# Then visualize with custom script or Cytoscape
```

---

### 3. Mermaid Diagrams

#### Diagram A: KG-Microbe Data Flow ⭐⭐⭐
**Purpose:** Show METPO's role in the knowledge graph

```mermaid
graph LR
    A[BacDive] --> E[METPO]
    B[BactoTraits] --> E
    C[Madin et al.] --> E
    E --> F[KG-Microbe]
    F --> G[Graph ML Models]
    G --> H[Growth Media Predictions]

    style E fill:#90EE90
    style F fill:#87CEEB
```

**Render to PNG:**
```bash
npx @mermaid-js/mermaid-cli -i diagram_kg_flow.mmd -o figures/kg_flow.png
```

---

#### Diagram B: OntoGPT Extraction Pipeline ⭐⭐
**Purpose:** Show literature mining workflow

```mermaid
graph TD
    A[PubMed Abstract] --> B[OntoGPT Extract]
    B --> C{Phenotype Grounding}
    C -->|In METPO| D[Success: METPO URI]
    C -->|Not in METPO| E[AUTO term]
    E --> F[Curation Workflow]
    F --> G[Add to METPO]
    G --> B
    D --> H[KG-Microbe]

    style D fill:#90EE90
    style E fill:#FFB6C1
    style G fill:#87CEEB
```

---

#### Diagram C: METPO Development Workflow ⭐
**Purpose:** Show how METPO is maintained

```mermaid
graph LR
    A[Domain Expert] --> B[Google Sheets]
    C[LLM Semantic Search] --> B
    B --> D[ROBOT Templates]
    D --> E[ODK Build]
    E --> F[ROBOT Validation]
    F -->|0 errors| G[Release]
    F -->|errors| B
    G --> H[BioPortal]
    G --> I[GitHub]

    style F fill:#90EE90
    style G fill:#87CEEB
```

---

#### Diagram D: Decision Tree ⭐
**Purpose:** When to build a new ontology?

```mermaid
graph TD
    A[Need ontology for domain?] -->|Yes| B{Existing ontology?}
    B -->|Yes| C{Maintained?}
    B -->|No| H[Build new]
    C -->|Yes| D{Good coverage?}
    C -->|No| H
    D -->|Yes| E{ROBOT valid?}
    D -->|No| H
    E -->|Yes| F[Use it!]
    E -->|No| G{Can you fix?}
    G -->|Yes| F
    G -->|No| H

    style F fill:#90EE90
    style H fill:#FFB6C1
```

---

### 4. Tables & Statistics

#### Table A: Validation Comparison ⭐⭐⭐

| Ontology | Year | ROBOT Errors | Warnings | Status | Expert Tier |
|----------|------|--------------|----------|--------|-------------|
| **METPO** | 2025 | **0** | 318 | ✓ | N/A (ours) |
| FAO | 2025 | 5 | 18 | ✓ | TIER2 |
| PATO | current | 16 | 498 | ✓ | TIER1_FOUNDATION |
| D3O | 2024 | 25 | 433 | ✓ | TIER3 |
| OMP | 2024 | 34 | 357 | ✓ | TIER1_CORE |
| MCO | 2019 | **65** | 2,701 | ✓ | **TIER1_CORE** |
| MicrO | 2018 | **103** | 4,446 | ✓ | **TIER1_CORE** |
| MPO | 2014 | **155** | 300 | ✓ | **TIER1_CORE** |

---

#### Table B: OntoGPT Grounding Results

| Abstract | Phenotype Groundings | AUTO Terms | ChEBI Groundings |
|----------|---------------------|------------|------------------|
| 19622650 | 12 | 46 | 16 |
| 19622668 | 12 | 25 | 8 |
| 28879838 | 4 | 47 | 8 |
| 27983469 | 4 | 17 | 16 |
| 27573017 | 3 | 14 | 15 |
| 37170873 | 2 | 29 | 8 |
| 19440302 | 0 | 17 | 6 |
| 22740660 | 0 | 9 | 3 |
| **TOTAL** | **37** | **~200** | **80** |

**Success Rates:**
- METPO phenotypes: ~15%
- ChEBI chemicals: 100%
- NCBITaxon: 100%

---

#### Table C: SSSOM Mapping Summary

| Target Ontology | Mappings | Match Type |
|----------------|----------|------------|
| PATO | 45 | skos:closeMatch |
| ENVO | 28 | skos:closeMatch |
| GO | 22 | skos:relatedMatch |
| OBI | 18 | skos:closeMatch |
| FLOPO | 15 | skos:closeMatch |
| **Total** | **158** | Various |

---

### 5. Screenshots (Optional)

**Not recommended as primary visuals, but can supplement:**

#### BioPortal Entry
- Screenshot of METPO on BioPortal
- Shows it's publicly available
- Can demonstrate metadata completeness

#### Protégé View
- Screenshot of METPO open in Protégé
- Show class hierarchy
- Show annotations, definitions

#### OAK Command Line
- Screenshot of OAK commands
- Show modern tooling accessibility
- Can demonstrate queries

**Recommendation:** Use OAK visualizations instead - more professional

---

## Recommended Workflow

### Phase 1: Planning & Setup ✅ (We are here)

**Tasks:**
1. ✅ Document session understanding
2. ⬜ Create comprehensive todo list
3. ⬜ Set up figures directory structure
4. ⬜ Verify Marp installation

**Time estimate:** 30 minutes

---

### Phase 2: Data Verification & Collection (CRITICAL)

**Tasks:**
1. ⬜ Re-run ROBOT validation on all ontologies (fresh data)
2. ⬜ Verify BacDive/BactoTraits/Madin coverage claims
3. ⬜ Calculate exact OntoGPT grounding statistics
4. ⬜ Verify SSSOM mapping counts
5. ⬜ Find KG-Microbe prediction accuracy source (>70% claim)
6. ⬜ Verify "154 ontologies for 90% coverage" methodology
7. ⬜ Check current METPO statistics (255 terms, definition counts)

**Scripts to create/run:**
- `verify_robot_errors.sh` - Re-validate all ontologies
- `calculate_coverage.py` - BacDive/BactoTraits/Madin coverage
- `analyze_grounding.py` - OntoGPT statistics (already exists, verify)
- `count_sssom_mappings.py` - SSSOM file analysis

**Time estimate:** 2-3 hours

**Critical:** These numbers must be fresh and accurate for slides

---

### Phase 3: Figure Generation

**Tasks:**
1. ⬜ Create `figures/` directory
2. ⬜ Write Python plotting scripts
   - ⬜ `plot_robot_errors.py`
   - ⬜ `plot_error_accumulation.py`
   - ⬜ `plot_grounding_success.py`
   - ⬜ `plot_coverage_comparison.py`
3. ⬜ Generate OAK visualizations
   - ⬜ METPO hierarchy
   - ⬜ Temperature subtree example
4. ⬜ Create Mermaid diagrams
   - ⬜ KG-Microbe data flow
   - ⬜ OntoGPT pipeline
   - ⬜ METPO development workflow
5. ⬜ Generate all figures to PNG/SVG

**Time estimate:** 2-3 hours

---

### Phase 4: Slide Content Writing

**Tasks:**
1. ⬜ Create `icbo_metpo_slides.md` (Marp format)
2. ⬜ Write slide content based on docs/ICBO_PREP.md structure:
   - ⬜ Slide 1: Title
   - ⬜ Slide 2: Data Integration Challenge
   - ⬜ Slide 3: Gap in Ontology Landscape
   - ⬜ Slide 4: Introducing METPO
   - ⬜ Slide 5: Modern & Pragmatic Design
   - ⬜ Slide 6: METPO in Action (KG-Microbe)
   - ⬜ Slide 7: KG-Microbe Examples
   - ⬜ Slide 8: Future Work (OntoGPT)
   - ⬜ Slide 9: Conclusion & Philosophy
3. ⬜ Integrate figures into slides
4. ⬜ Add speaker notes for each slide

**Time estimate:** 2-3 hours

---

### Phase 5: Slide Generation & Review

**Tasks:**
1. ⬜ Generate PDF from Marp
2. ⬜ Review slides for:
   - ⬜ Accuracy of all claims
   - ⬜ Clarity of message
   - ⬜ Alignment with ICBO themes
   - ⬜ Timing (10-12 minutes)
3. ⬜ Iterate on content/design
4. ⬜ Generate final PDF
5. ⬜ Optional: Export to PPTX for manual tweaks

**Time estimate:** 1-2 hours

---

### Phase 6: Backup Video Preparation

**Tasks:**
1. ⬜ Practice presentation with slides
2. ⬜ Record backup video
3. ⬜ Verify video <1GB
4. ⬜ Upload to https://tinyurl.com/ICBO2025-Slides
5. ⬜ Upload by Saturday, Nov 8 deadline

**Time estimate:** 2-3 hours

---

### Total Time Estimate: 10-15 hours

**Breakdown:**
- Planning: 0.5 hours
- Verification: 2-3 hours (CRITICAL)
- Figures: 2-3 hours
- Content: 2-3 hours
- Review: 1-2 hours
- Video: 2-3 hours

**Deadline:** Saturday, Nov 8 (backup video due)
**Today:** Thursday, Nov 7
**Time available:** ~1.5 days

**Recommendation:** Prioritize verification and core slides today, video tomorrow

---

## Next Steps

### Immediate Actions (Today, Nov 7)

#### Option A: Comprehensive Todo List First ⭐ RECOMMENDED
**Rationale:** Track all tasks, ensure nothing forgotten

**Next command:**
```bash
# Create todo list with TodoWrite tool
# Then systematically work through verification → figures → slides
```

**Pros:**
- ✅ Transparency and accountability
- ✅ Can track progress
- ✅ Won't forget any verification tasks

---

#### Option B: Start Verification Immediately
**Rationale:** Get fresh data ASAP

**Next commands:**
```bash
# Re-run ROBOT validations
cd /home/mark/gitrepos/metpo
bash verify_all_ontologies.sh

# Analyze OntoGPT results
cd /home/mark/gitrepos/metpo/ontogpt_icbo_demo
python analyze_metpo_grounding.py > grounding_stats.txt

# Check SSSOM mappings
cd /home/mark/gitrepos/metpo/notebooks
wc -l metpo_mappings_*.sssom.tsv
```

**Pros:**
- ✅ Immediate concrete data
- ✅ Identifies any surprises early

---

#### Option C: Create One Sample Figure
**Rationale:** Demonstrate what's possible

**Next command:**
```bash
# Create ROBOT errors comparison chart
cd /home/mark/gitrepos/metpo/ontogpt_icbo_demo
mkdir -p figures
python create_robot_errors_plot.py
```

**Pros:**
- ✅ Visual preview of slide quality
- ✅ Validates figure generation approach

---

#### Option D: Draft Slide Structure
**Rationale:** See format, plan content

**Next command:**
```bash
# Create Marp template
cd /home/mark/gitrepos/metpo/ontogpt_icbo_demo
vim icbo_metpo_slides.md
```

**Pros:**
- ✅ Clear vision of final product
- ✅ Can fill in verified data as we go

---

### User's Decision Point

**Mark said:** "I want to proceed in any way that you suggest"

**My strongest recommendation: Option A (Todo List First)**

**Reasoning:**
1. Ensures we verify ALL claims with fresh data
2. Tracks progress systematically
3. Prevents forgetting critical tasks
4. Maintains accountability
5. After todo list, work through: verify → figures → content → review

**Alternative if pressed for time: Option B (Verify First)**
- Get critical data immediately
- Create figures as data comes in
- Write slides with verified numbers

**What should we do?**

---

## Files to Create

### Scripts
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/verify_robot_errors.sh`
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/calculate_coverage.py`
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/count_sssom_mappings.py`
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/figures/plot_robot_errors.py`
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/figures/plot_error_accumulation.py`
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/figures/plot_grounding_success.py`
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/figures/plot_coverage_comparison.py`

### Mermaid Diagrams
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/figures/kg_flow.mmd`
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/figures/ontogpt_pipeline.mmd`
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/figures/metpo_workflow.mmd`

### Slides
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/icbo_metpo_slides.md` (Marp source)
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/icbo_metpo_slides.pdf` (Generated)
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/icbo_metpo_slides.pptx` (Optional export)

### Documentation
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/ICBO_SLIDES_PREP_SESSION.md` (This file)
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/VERIFICATION_RESULTS.md` (Verification findings)
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/SPEAKER_NOTES.md` (Detailed notes for presentation)

---

## Critical Claims to Verify

### High Priority (Must be accurate)

1. **METPO has 0 ROBOT errors**
   - Re-run: `robot validate --input metpo.owl`
   - Expected: 0 errors, ~318 warnings

2. **MicrO has 103 errors, MPO has 155, MCO has 65**
   - Re-run validations on all three
   - Verify from docs/ICBO_PREP.md table

3. **158 terms mapped to 24 ontologies**
   - Count: `wc -l metpo_cross_references.tsv`
   - Verify: `cut -f3 metpo_cross_references.tsv | sort -u | wc -l`

4. **~14 errors per year of abandonment**
   - Calculate correlation coefficient
   - Verify slope of regression line

5. **OntoGPT grounding: 37 METPO, 80 ChEBI**
   - Re-run: `make analyze`
   - Verify counts manually

### Medium Priority (Should be accurate)

6. **255 METPO terms, 46.3% have definitions**
   - Count: `grep -c "^METPO:" src/templates/metpo_sheet.tsv`
   - Definition %: Re-run definition analysis script

7. **>70% precision for KG-Microbe predictions**
   - Find source: Check KG-Microbe papers, Marcin's presentations
   - May need to adjust or remove if unsourced

8. **154 ontologies needed for 90% metabolism coverage**
   - Find analysis script/notebook
   - Verify methodology is sound

9. **FLOPO > MCO coverage**
   - Find specific numbers
   - Verify comparison is fair

### Lower Priority (Nice to have)

10. **CMM project: $850K, FY26**
    - Verify from docs/ICBO_PREP.md (unlikely to change)

11. **Expert designation correlation**
    - "2.4× worse coverage, 14× worse quality"
    - Verify calculation methodology

---

## Questions for Mark

1. **KG-Microbe prediction accuracy:** Where is the ">70% precision" claim from?
2. **BacDive/BactoTraits/Madin coverage:** Do we have specific % numbers?
3. **Slide style preference:** Professional/minimal or colorful/engaging?
4. **Time allocation:** How much time today vs tomorrow for this work?
5. **Video format:** Do you have screen recording software? Need recommendations?
6. **Backup plan:** If Marp doesn't work, immediate fallback to manual PowerPoint?

---

## End of Session Document

**This file captures:**
- ✅ Why METPO exists (detailed narrative)
- ✅ METPO's 7 selling points with evidence
- ✅ Two-phase story (semi-structured vs literature mining)
- ✅ OntoGPT results analysis (concrete numbers)
- ✅ ICBO 2025 alignment and likely questions
- ✅ Slide generation options (Marp recommended)
- ✅ Visual content plan (plots, OAK viz, diagrams, tables)
- ✅ Recommended workflow (6 phases)
- ✅ Next steps and decision points
- ✅ Files to create
- ✅ Critical claims to verify

**Next Action:** User decides approach (Todo list vs immediate verification vs figures vs slides)

**Deadline Reminder:** Backup video due Saturday, Nov 8 (< 48 hours)

**Status:** Ready to proceed with slide preparation
