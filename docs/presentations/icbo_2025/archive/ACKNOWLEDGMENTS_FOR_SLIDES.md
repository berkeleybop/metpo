# ICBO 2025 Acknowledgments

**Last Updated:** 2025-11-11

---

## People to Acknowledge

### Core METPO Team
1. **Mark Andrew Miller** - Primary developer and maintainer (LBNL)
2. **Marcin P. Joachimiak** - Principal Investigator, Co-creator, KG-Microbe lead (LBNL)
3. **Chris Mungall** - Co-creator, OAK/ODK/ROBOT expert
4. **Sujay Patil** - Co-creator (LBNL)
5. **Nomi Harris** - Program Manager for Chris Mungall's group (LBNL)
   - [LinkedIn](https://www.linkedin.com/in/nomiharris/)

### CultureBot Project
6. **Adam Deutschbauer** - CultureBot co-lead with Marcin (EGSB/LBNL)
   - LDRD FY24-FY25, NCE through Dec 2025
   - ML models for predicting microbial growth conditions
   - [github.com/culturebotai](https://github.com/culturebotai)

### CMM-AI Project Collaborators
7. **Ning Sun** - Principal Investigator, DOE BER FY26 CMM Pilot (LBNL)
   - "Advanced Biorecovery of Critical Minerals" ($850K)
8. **Rita Kuo** - HTP Strain Screening Pipeline (CMM-AI)

### Data Contributors
9. **Charles Parker** / **Charlie Parker** - Names for Life (N4L) phenotypic ontology data provider
10. **Valerie Skye** - Google Drive N4L data steward/contributor

---

## Projects to Acknowledge

### Major Applications

**CultureBot** (LBNL LDRD FY24-FY25)
- **PIs:** Joachimiak + Deutschbauer (EGSB)
- **Goal:** ML methods to predict growth conditions for unculturable/not-yet-cultured organisms
- **METPO Role:** Provides structured training data via KG-Microbe
- **Repository:** [github.com/culturebotai](https://github.com/culturebotai)
- **Status:** Active through December 2025

**DOE CMM-REE Project** (FY26, $850K)
- **PI:** Ning Sun
- **Co-PI:** Marcin Joachimiak
- **Focus:** Advanced biorecovery of critical minerals (rare earth elements)
- **METPO Role:** Literature mining for lanthanophore biosynthesis pathways
- **Status:** Active funding

### Data Sources

**Primary Microbial Trait Databases:**
1. **BactoTraits** (Cébron et al. 2021, Ecological Indicators)
   - 19,455 bacterial strains with functional trait annotations
   - Repository: https://github.com/TrEE-TIMC-MaMiV/BactoTraits
   - License: CC BY-NC-SA

2. **Madin et al. Dataset** (2020, Scientific Data)
   - 172,324 strain-level records with phenotypic traits, pathways, carbon substrates
   - DOI: [10.1038/s41597-020-0497-4](https://doi.org/10.1038/s41597-020-0497-4)
   - Repository: https://github.com/bacteria-archaea-traits/bacteria-archaea-traits

3. **BacDive** (Reimer et al. 2022, Nucleic Acids Research)
   - Comprehensive bacterial and archaeal strain information (DSMZ)
   - DOI: [10.1093/nar/gkab961](https://doi.org/10.1093/nar/gkab961)
   - Website: https://bacdive.dsmz.de/

4. **Names for Life (N4L)** - Charlie Parker's phenotypic ontology (2016)
   - Chemical utilization phenotypes
   - Protolog data integration

### Related Knowledge Graphs

**KG-Microbe** - Knowledge Graph for Microbes
- **Lead:** Marcin Joachimiak (LBNL)
- **Repository:** https://github.com/Knowledge-Graph-Hub/kg-microbe
- **Role:** Integrated microbial trait knowledge graph
- **Relationship:** Primary application driving METPO development

---

## Ontology Infrastructure

### OBO Foundry Ontologies
**Core Phenotype Ontologies:**
- **PATO** (Phenotype And Trait Ontology)
- **OBA** (Ontology of Biological Attributes)
- **UPHENO** (Unified Phenotype Ontology)

**Microbial-Specific:**
- **MicrO** (Ontology of Microbial Phenotypes)
- **MCO** (Microbial Conditions Ontology)
- **OMP** (Ontology of Microbial Phenotypes - BioPortal)

**Environmental & Process:**
- **ENVO** (Environment Ontology)
- **GO** (Gene Ontology)
- **ChEBI** (Chemical Entities of Biological Interest)

### BioPortal Ontologies
Additional microbial ontologies:
- **D3O** (DSMZ Digital Diversity Ontology)
- **BIPON** (Bacterial Interlocked Process Ontology)
- **GMO** (Growth Medium Ontology)
- **TYPON** (Microbial Typing Ontology)

---

## Software & Tools

### Ontology Development
1. **Ontology Development Kit (ODK)** - INCATOOLS
   - https://github.com/INCATools/ontology-development-kit
   - License: BSD-3-Clause

2. **ROBOT** (ROBOT is an OBO Tool)
   - http://robot.obolibrary.org/
   - License: BSD-3-Clause

3. **OAK (Ontology Access Kit)** - INCATOOLS
   - https://github.com/INCATools/ontology-access-kit
   - License: BSD-3-Clause

4. **LinkML** (Linked Data Modeling Language)
   - https://linkml.io/
   - Schema definition framework

### Literature Mining
5. **OntoGPT** - Monarch Initiative
   - https://github.com/monarch-initiative/ontogpt
   - License: BSD-3-Clause
   - Literature extraction with METPO grounding

### Infrastructure
6. **NCBO BioPortal** - Stanford/NCBO
   - https://bioportal.bioontology.org/ontologies/METPO
   - Primary ontology hosting, browsing, search, API access

7. **ChromaDB** - Vector database
   - https://www.trychroma.com/
   - 452,942 ontology term embeddings for semantic similarity

8. **OpenAI API**
   - Embeddings (text-embedding-3-small, 1536 dimensions)
   - LLM-based extraction

---

## Funding Acknowledgments

### Current Active Funding
1. **LBNL LDRD** (FY24-FY25, NCE through Dec 2025)
   - **Project:** CultureBot
   - **PIs:** Joachimiak + Deutschbauer

2. **DOE BER FY26 CMM Pilot** ($850K)
   - **Project:** "Advanced Biorecovery of Critical Minerals"
   - **PI:** Ning Sun
   - **Co-PI:** Marcin Joachimiak

---

## Suggested Slide Format

### Minimal Acknowledgments (1 slide):

**People:**
- METPO Core: Mark Miller, Marcin Joachimiak, Chris Mungall, Sujay Patil, Nomi Harris (PM)
- CultureBot: Joachimiak + Deutschbauer
- CMM-AI: Ning Sun (PI), Rita Kuo

**Funding:**
- LBNL LDRD (CultureBot, FY24-25)
- DOE BER CMM Pilot ($850K, FY26)

**Data:**
- BactoTraits, Madin et al., BacDive, N4L

**Infrastructure:**
- OBO Foundry, NCBO BioPortal, ODK/ROBOT/OAK, OntoGPT, LinkML

### Expanded Acknowledgments (if space):

Add specific mentions of:
- Adam Deutschbauer (CultureBot co-lead)
- Charlie Parker (N4L data)
- Specific ontologies used (PATO, ENVO, ChEBI, MicrO, OMP)
- ChromaDB/OpenAI for semantic search infrastructure

---

## Notes

- CultureBot GitHub: [github.com/culturebotai](https://github.com/culturebotai)
- METPO is actively maintained for both CultureBot and CMM projects
- KG-Microbe is the primary application driving METPO development
- METPO hosted on NCBO BioPortal with full API access
