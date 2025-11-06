# ICBO 2025 - CMM Project Details

**Date:** 2025-11-06
**Status:** Complete project context for ICBO presentation
**Purpose:** Detailed CMM project information, team structure, and METPO's role

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Principal Investigators & Team](#principal-investigators--team)
3. [How KG-Microbe Fits Into CMM](#how-kg-microbe-fits-into-cmm)
4. [CMM Project Structure](#cmm-project-structure)
5. [Data Flow Diagram](#data-flow-diagram)
6. [DOE BER Decision Letter](#doe-ber-decision-letter)

---

## Project Overview

**Full Title:** "Advanced Biorecovery of Critical Minerals through AI/ML-Guided Design of Microbial Chassis and Bioadsorbent"

**Goal:** Develop AI/ML-guided microbial technology to recover Rare Earth Elements (REEs) from e-waste using engineered microbes.

**Target Elements:** Neodymium (Nd), Praseodymium (Pr), Dysprosium (Dy)
**Funding:** $850K for FY26 (12 months), renewal pending fall 2026
**Status:** Funds received end of August 2025

**CMM Definition:** Critical Minerals and Materials - U.S. Department of Energy (DOE) program

---

## Principal Investigators & Team

### PI: Ning Sun (LBNL)
- Staff Scientist, Biological Systems and Engineering Division
- Expert in biomass processing
- Leads overall project coordination (10% effort)
- Profile: https://biosciences.lbl.gov/profiles/ning-sun-2/
- **Budget:** $264,870
- **Team:**
  - Rita Kuo (Research Support, 20%)
  - Saad Naseem (Postdoc, 50%)

### Co-PIs:

#### 1. Marcin Joachimiak (LBNL EGSB) - 10% effort
- Leads KG-CMREE (Knowledge Graph for Critical Minerals/REE)
- AI/ML framework development
- **Budget:** $131,682
- **Team:** Mark Miller (Software Developer, 20% effort)
- **This is where METPO and KG-Microbe fit!**
- **Dual role:** CMM AI/ML + METPO/KG-Microbe development

#### 2. N. Cecilia Martinez-Gomez (UC Berkeley) - 10% effort
- Bacterial strain engineering for REE selectivity
- Lanthanophore characterization
- Expert in lanthanide-dependent methylotrophy
- **Budget:** $158,599
- **Team:** Trinity Reiner (Lab Technician, 80% effort)

#### 3. Rebecca Abergel (LBNL Chemical Sciences) - 5% effort
- Spectroscopic assay development for REE detection
- f-element coordination chemistry
- **Budget:** $130,254
- **Team:** Alexander Brown (Postdoc, 50% effort)

#### 4. Yasuo Yoshikuni (JGI) - 5% effort
- Expanding bacterial/fungal chassis
- CRAGE (Chassis-independent Recombinase-Assisted Genome Engineering)
- **Budget:** $137,622
- **Team:** Yusuke Otani (Postdoc, 50% effort)

#### 5. Romy Chakraborty (LBNL EESA) - 2% effort
- Microbial ecology
- **Budget:** $26,973
- **Team:** Mingfei Chen (Postdoc, 5% effort)

**Total Budget:** $850,000 for 12 months (FY26)

### Institutional Arrangements
- IUT (Inter-University Transfer) between LBNL and UC Berkeley established
- MTA (Material Transfer Agreement) in progress
- Molecular Foundry user proposal submitted for advanced imaging

---

## How KG-Microbe Fits Into CMM

### Task 1.1: Construct KG-CMREE and Establish AI/ML Framework

KG-CMREE (Knowledge Graph for Critical Minerals and Rare Earth Elements) **extends KG-Microbe**:

#### Building on KG-Microbe foundation:
- >3,000 organismal traits
- >30,000 functional/genomic traits
- Harmonizes data from BacDive, BactoTraits, UniProt, MediaDive, etc.
- Uses Biolink model for semantic integration

#### New CMM-specific data:
- REE bioaccumulation phenotypes
- Lanthanophore biosynthetic pathways
- Spectroscopic measurements
- High-throughput screening results
- Bioprocess parameters

#### AI/ML Framework:
- **Agentic AI** with cooperating autonomous agents:
  - Literature Mining Agent (LLM-assisted extraction from publications)
  - Experiment Design Agent (predictive models, historical outcomes)
  - Failure Analysis Agent (learns from unsuccessful experiments)
- **Graph Transformers** for ranking candidate taxa/pathways/proteins
- **Neurosymbolic loop** combining symbolic rules + graph learning
- **Design-Build-Test-Learn (DBTL) cycles** for strain optimization

### Why METPO Matters for CMM

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

## CMM Project Structure

### Task 1: Technical Tool Development

#### Task 1.1: KG-CMREE and AI/ML Framework (Marcin Joachimiak)
- Extends KG-Microbe with REE-specific data
- Agentic AI with autonomous experiment orchestration
- Graph Transformers for strain ranking
- **METPO role:** Provides phenotype annotations for microbial traits

#### Task 1.2: Spectroscopic Assay Development (Rebecca Abergel)
- ICP-OES: Quantify REEs in digested cells
- Time-Resolved Luminescence (TRL): HTP REE detection
- 3,4,3-LI(1,2-HOPO) chelator for lanthanide fluorescence
- **METPO role:** Minimal (analytical chemistry focus)

#### Task 1.3: HTP Strain Screening Pipeline (Ning Sun/Rita Kuo)
- 6,000 samples/day automation capacity
- Automated E. coli transformation, colony picking, NGS validation
- Data processing pipelines for plate readers, HPLC, spectrometers
- **METPO role:** Annotates screened strains with phenotypes

### Task 2: AI/ML-Guided Microbial Engineering

#### Task 2.1: Bacterial Strain Engineering (Cici Martinez-Gomez)
- Engineer strains to hyperaccumulate REEs (Nd, Pr, Dy)
- Discover novel lanthanophore biosynthetic clusters
- Transcriptomic profiling + genomic analysis
- **METPO role:** Annotates metabolic and metal tolerance phenotypes

#### Task 2.2: Fungal/Bacterial Chassis Expansion (Yasuo Yoshikuni)
- CRAGE technology for extremophile domestication
- Acidithiobacillus (bioleaching), Methylobacterium (biosorption)
- Engineer acid/salt/temperature tolerance
- **METPO role:** Defines tolerance phenotypes (pH, temp, salinity ranges)

---

## Data Flow Diagram

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

## DOE BER Decision Letter

### Key Quote

> "BER is most interested in supporting LBNL objectives that seek to build a high-throughput strain screening and validation pipeline for ML guided bioengineering of REE accumulation, as these aims are more directly relevant to the request in the call to advance biodesign and synthetic biology for the extraction and recovery of CMM from natural and complex environments."

**Translation:** DOE prioritizes the AI/ML + HTP pipeline work (Marcin's Task 1.1 + Ning's Task 1.3) as the most innovative aspects of the proposal.

---

## KG-Microbe Applications

### Published Applications

#### 1. Predicting Optimal Growth Media
- ML models: >70% precision on benchmark datasets
- Both explainable rule-based and black-box approaches
- Publication: ISMB/ECCB 2025 talk
- Publication: CSBJ 2025 (Máša, Kliegr, Joachimiak)

#### 2. Microbial Trait Prediction
- Graph embeddings infer traits (cell shape, metabolic strategy)
- Works for uncultivated microbes

#### 3. Hypothesis Generation
- Multi-hop queries discover trait associations
- Vector algebra enables finding potential microbial interactions

### KG-CMREE Extensions (In Progress)

#### 4. AI-Guided Strain Discovery (CMM Task 1.1)
- Graph Transformers rank candidate taxa for REE accumulation
- Agentic AI orchestrates DBTL cycles
- Literature mining agent extracts knowledge from lanthanome publications

#### 5. Bioengineering Optimization (CMM Task 2)
- Predicts CRAGE integration efficiency in extremophiles
- Links genomic features to REE selectivity phenotypes
- Guides lanthanophore biosynthetic cluster discovery

#### 6. High-Throughput Experiment Design (CMM Task 1.3)
- AI-designed experiments for 6,000 samples/day pipeline
- Automated analysis of REE accumulation screening data
- Failure analysis improves future experiment design

---

## References for ICBO Talk

### CMM Project
- BER CMM Pilot Proposal (FY26): "Advanced Biorecovery of Critical Minerals through AI/ML-Guided Design of Microbial Chassis"
- DOE CMM Program: https://www.energy.gov/science/critical-minerals-and-materials-program

### KG-Microbe Publications
- Joachimiak et al., 2021: "KG-Microbe: A Reference Knowledge-Graph and Platform for Harmonized Microbial Information" (CEUR-WS)
- Santangelo et al., 2025: KG-Microbe updates
- Caufield et al., 2023: KG-Hub
- Unni et al., 2022: Biolink Model
- GitHub: github.com/Knowledge-Graph-Hub/kg-microbe

### Related Publications
- Good et al., 2024: "Scalable and Consolidated Microbial Platform for Rare Earth Element Leaching and Recovery from Waste Sources" (Env Sci Tech)
- Zytnick et al., 2024: "Identification and characterization of a small-molecule metallophore involved in lanthanide metabolism" (PNAS)
- Müller et al., 2025: "Cost-effective urine recycling enabled by a synthetic osteoyeast platform" (Nature Commun)
