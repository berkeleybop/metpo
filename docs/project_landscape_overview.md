# Project Landscape Overview: METPO, KG-Microbe, and CultureBot

**Date:** 2025-10-03
**Purpose:** Comprehensive reference for data sources, modeling frameworks, technologies, and project relationships

---

## Project Relationships & Funding

### CultureBot (Primary Initiative)
- **Funding:** LDRD grant from Lawrence Berkeley National Laboratory
- **Primary Goal:** Develop machine learning methods to predict growth conditions for unculturable/not-yet-cultured organisms
- **PI:** [Name not specified - need to document]
- **Supporting Projects:** KG-Microbe (knowledge graph), METPO (ontology)

### KG-Microbe (Knowledge Graph)
- **Purpose:** Integrate microbial trait data from multiple sources into unified knowledge graph
- **Format:** KGX (Knowledge Graph Exchange format)
- **Relationship to CultureBot:** Provides structured training data for ML predictions
- **Note:** PI uses "very old practices" for KGX generation (details TBD)

### METPO (Microbial Ecophysiological Traits and Phenotypes Ontology)
- **Purpose:** Codify textual values from data sources into formal ontology terms
- **Role:** Standardize trait terminology for KG-Microbe nodes
- **Repository:** https://github.com/berkeleybop/metpo
- **Outputs:**
  - `metpo.owl` (OWL ontology)
  - `metpo.json` (JSON-LD)
  - ROBOT template-driven generation from TSV

---

## Data Sources

### Primary Microbial Trait Datasets

#### 1. Madin et al. (bacteria-archaea-traits)
- **What:** Reproducible synthesis of 26 sources into unified trait dataset
- **Coverage:** ~170k strain-level, ~15k species-aggregated records
- **Traits:** 14 phenotypic, 5 quantitative genomic, 4 environmental characteristics
- **Status:** Frozen 2020 snapshot (static, reproducible)
- **Access:**
  - GitHub: https://github.com/jmadin/bacteria_archaea_traits
  - Also: https://github.com/bacteria-archaea-traits/bacteria-archaea-traits
- **Format:** CSV/TSV with R scripts for rebuilding
- **Local MongoDB:** `madin.madin` collection (untransformed CSV/TSV)
- **Publication:** Madin, J.S. et al. (2020) Scientific Data 7, 170
  - https://www.nature.com/articles/s41597-020-0497-4
- **Project page:** https://jmadinlab.github.io/datasets/madin-2020
- **METPO Coverage:** 15/103 pathways (14.6%), 88 missing

#### 2. BacDive (Bacterial Diversity Metadatabase)
- **What:** Largest curated strain-linked knowledge base for bacteria/archaea
- **Curator:** DSMZ (German Collection of Microorganisms and Cell Cultures)
- **Status:** Continuously curated, actively updated
- **Access:**
  - Web portal: https://bacdive.dsmz.de/
  - REST API: https://api.bacdive.dsmz.de/ (JSON, registration required)
  - Python client: https://pypi.org/project/bacdive/
  - R client: https://api.bacdive.dsmz.de/client_examples
- **Format:** JSON (API), CSV (portal exports), HTML
- **Local MongoDB:** `bacdive.strains_api` collection (nested JSON from API)
- **Schema:** ~234 main fields in 10 sections
  - Field documentation: https://api.bacdive.dsmz.de/strain_fields_information
- **Publication:** Reimer, L.C. et al. (2022) Nucleic Acids Research
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC8728306/
- **Help/Overview:** https://bacdive.dsmz.de/help/
- **METPO Coverage:** 16/16 oxygen tolerance + 7/7 halophily (100% verified ✓)

#### 3. BactoTraits
- **What:** Bacterial functional-traits table derived primarily from BacDive
- **Coverage:** ~19,455 strains
- **Traits:** Oxygen preference, cell size/shape, motility, growth pH/temp (optimum/range), GC content, trophic type
- **Status:** Static release v2, June 2022
- **Access:**
  - Repository: https://ordar.otelo.univ-lorraine.fr/record?id=10.24396%2FORDAR-53
  - File: `BactoTraits_databaseV2_Jun2022.csv` + README
- **Format:** Single CSV (no API)
- **Local MongoDB:** `bactotraits.bactotraits` collection (one-hot encoded, transformed from CSV)
- **License:** CC BY-NC-SA
- **Publication:** Cébron, A. et al. (2021) Ecological Indicators
- **METPO Coverage:** CRITICAL ISSUE - naming mismatch between METPO claims and MongoDB representation
- **Note:** Crosswalk with BacDive identifiers recommended (BactoTraits derived from BacDive)

#### 4. MediaDive
- **What:** Culture media database from DSMZ
- **Access:** https://mediadive.dsmz.de/rest/media
- **Format:** JSON (REST API)
- **File:** `mediadive.json`

#### 5. Fermentation Explorer
- **What:** Fermentation pathways and products database
- **Access:** https://github.com/thackmann/FermentationExplorer
- **Format:** CSV
- **File:** `fermentation_explorer.csv`

#### 6. Disbiome
- **What:** Human microbiome-disease associations
- **Access:** https://disbiome.ugent.be:8080/experiment
- **Format:** JSON
- **File:** `disbiome.json`

#### 7. Wallen et al.
- **What:** Gut microbiome study (Nature Communications 2022)
- **Access:** Springer Nature supplementary materials
- **Format:** Excel
- **File:** `wallen_etal.xlsx`

### Ontologies

#### 8. ENVO (Environment Ontology)
- **Access:** http://purl.obolibrary.org/obo/envo.json
- **File:** `envo.json`

#### 9. ChEBI (Chemical Entities of Biological Interest)
- **Access:** http://purl.obolibrary.org/obo/chebi.owl.gz
- **Files:** `chebi.owl.gz`, `chebi.owl`, `chebi.json`, `chebi.db`

#### 10. GO (Gene Ontology)
- **Access:** http://purl.obolibrary.org/obo/go.json
- **Files:** `go.json`, `go.owl`

#### 11. NCBITaxon (NCBI Taxonomy)
- **Access:** http://purl.obolibrary.org/obo/ncbitaxon.owl.gz
- **Files:** `ncbitaxon.owl.gz`, `ncbitaxon.owl`, `ncbitaxon.db`

#### 12. MONDO (Mondo Disease Ontology)
- **Access:** https://purl.obolibrary.org/obo/mondo/mondo.json
- **File:** `mondo.json`

#### 13. HP (Human Phenotype Ontology)
- **Access:** https://purl.obolibrary.org/obo/hp/hp.json
- **File:** `hp.json`

#### 14. METPO (Microbial Ecophysiological Traits and Phenotypes Ontology)
- **Access:** https://raw.githubusercontent.com/berkeleybop/metpo/refs/heads/main/metpo.owl
- **Files:** `metpo.owl`, `metpo.json`

### Protein and Pathway Data

#### 15. UniProt Proteomes (Functional Microbes)
- **Access:** https://kghub.io/frozen_incoming_data/uniprot/uniprot_proteomes.tar.gz
- **File:** `uniprot_proteomes.tar.gz`

#### 16. UniProt Human
- **Access:** https://kghub.io/frozen_incoming_data/uniprot/uniprot_human.tar.gz
- **File:** `uniprot_human.tar.gz`

#### 17. Unipathways
- **Access:** https://github.com/geneontology/unipathway
- **Files:** `upa.owl`, `upa.json`

#### 18. EC (Enzyme Commission)
- **Access:** https://w3id.org/biopragmatics/resources/eccode/
- **Files:** `ec.json`, `ec.owl.gz`

#### 19. RHEA (Biochemical Reactions)
- **Access:** https://ftp.expasy.org/databases/rhea/tsv/
- **Files:** `rhea2go.tsv`, `rhea2ec.tsv`

### Disease and Chemical Associations

#### 20. CTD (Comparative Toxicogenomics Database)
- **What:** Chemical-disease associations
- **Access:** https://ctdbase.org/reports/CTD_chemicals_diseases.tsv.gz
- **File:** `CTD_chemicals_diseases.tsv.gz`

### Conversion Tables and Support Files

#### 21. Environments Conversion Table
- **Access:** https://github.com/bacteria-archaea-traits/bacteria-archaea-traits
- **File:** `environments.csv`

#### 22. EPM (Extended Prefix Map)
- **What:** OBO prefix mappings for CURIE resolution
- **Access:** https://github.com/biopragmatics/bioregistry
- **File:** `epm.json`

### Summary by Category
- **Primary Trait Sources:** 3 (BacDive, Madin, BactoTraits) + 4 specialized (MediaDive, Fermentation Explorer, Disbiome, Wallen)
- **Ontologies:** 7 (ENVO, ChEBI, GO, NCBITaxon, MONDO, HP, METPO)
- **Biochemical Data:** 5 (UniProt×2, Unipathways, EC, RHEA)
- **Disease/Association:** 2 (CTD, Disbiome)
- **Support Files:** 2 (Environments conversion, EPM)
- **Total:** 20+ distinct data sources

---

## Modeling Frameworks

### Biolink Model
- **Role:** Primary source for node categories/types in KG-Microbe
- **Priority:** Highest (1st choice for node classification)
- **Usage:** Standardized categories for knowledge graph elements
- **Documentation:** [Need to add link]

### LinkML (Linked Data Modeling Language)
- **Usage:** Schema definition for knowledge graphs
- **Relationship:** Used with PATO/OMP/MCO terms for trait normalization
- **Status:** [Need to document usage details]

### PATO (Phenotype and Trait Ontology)
- **Usage:** Phenotypic trait descriptions
- **Integration:** Used in LinkML schemas for trait normalization

### OMP (Ontology of Microbial Phenotypes)
- **Usage:** Microbial-specific phenotype terms
- **Integration:** Used alongside PATO in LinkML

### MCO (Microbial Conditions Ontology)
- **Usage:** Growth conditions and environmental parameters
- **Integration:** Used in LinkML schemas

### KGX (Knowledge Graph Exchange)
- **What:** Format for knowledge graph interchange
- **Usage:** Output format for KG-Microbe
- **Node Category Hierarchy:**
  1. Biolink Model (highest priority)
  2. High-profile ontologies (ChEBI, etc.)
  3. METPO (domain-specific traits)
  4. Legacy placeholder CURIEs (e.g., `oxygen:aerobic`) - pre-METPO

### Historical Context: Placeholder CURIEs
- **Example:** `oxygen:aerobic`
- **When:** Used before METPO was developed
- **Status:** Being transitioned to METPO CURIEs
- **Question:** Migration strategy unclear - coexistence? Replacement? Equivalence mappings?

---

## Technologies

### Ontology Development & Management

#### ROBOT (ROBOT is an OBO Tool)
- **Usage:** METPO build pipeline, template-driven ontology generation
- **Files:**
  - Templates: `src/templates/metpo_sheet.tsv`
  - Commands in Makefile for building OWL from templates
- **Documentation:** http://robot.obolibrary.org/

#### OWL (Web Ontology Language)
- **Usage:** Primary ontology format for METPO
- **Files:** `metpo.owl`

#### JSON-LD (JSON for Linked Data)
- **Usage:** Alternative METPO serialization
- **Files:** `metpo.json`

#### Protégé (implied)
- **Usage:** Likely used for ontology editing/visualization
- **Status:** [Need to confirm]

### Data Storage & Query

#### MongoDB
- **Usage:** Local storage for raw data from sources
- **Authentication:** Unauthenticated local instance
- **Collections:**
  - `madin.madin` - Untransformed CSV/TSV from Madin et al.
  - `bacdive.strains_api` - Nested JSON from BacDive API
  - `bactotraits.bactotraits` - One-hot encoded, transformed from CSV
- **Access:** `mongosh` command-line client
- **Queries:** Aggregation pipelines for data extraction/analysis

### Programming Languages

#### Python
- **Usage:** ETL pipelines, data processing, ML model development
- **Libraries:** [Need to document - likely pandas, scikit-learn, etc.]

#### R
- **Usage:** Madin et al. provides R scripts for data rebuilding
- **Status:** [Need to document if used in our pipelines]

### Version Control & Collaboration

#### Git/GitHub
- **Repositories:**
  - https://github.com/berkeleybop/metpo
  - https://github.com/berkeleybop/kg-microbe (implied location)
  - https://github.com/berkeleybop/bacphen-awareness (reference schemas)
- **Branch Strategy:** Feature branches for development

#### GitHub Actions (implied)
- **Usage:** Likely CI/CD for METPO builds
- **Status:** [Need to document]

### Data Processing

#### jq
- **Usage:** JSON processing and querying
- **Context:** Available in bash for data manipulation

#### awk/sed/grep
- **Usage:** Text processing, CSV manipulation
- **Context:** Used in analysis scripts

#### ripgrep (rg)
- **Usage:** Fast code/data searching
- **Context:** Preferred over grep

### Machine Learning

#### [Framework TBD]
- **Purpose:** CultureBot ML model development
- **Goal:** Predict growth conditions for unculturable organisms
- **Training Data:** KG-Microbe knowledge graph
- **Status:** [Need to document - scikit-learn? TensorFlow? PyTorch?]

---

## GitHub Repositories

### Primary Project Repositories

#### metpo
- **GitHub:** https://github.com/berkeleybop/metpo
- **Local:** ~/Documents/gitrepos/metpo
- **Purpose:** Microbial Ecophysiological Traits and Phenotypes Ontology
- **Key Outputs:** metpo.owl, metpo.json

#### kg-microbe
- **GitHub:** https://github.com/Knowledge-Graph-Hub/kg-microbe
- **Local:** ~/Documents/gitrepos/kg-microbe
- **Purpose:** Integrated microbial trait knowledge graph
- **Key Files:** download.yaml, data/raw/, KGX outputs

#### bacphen-awareness
- **GitHub:** https://github.com/turbomam/bacphen-awareness
- **Local:** ~/Documents/gitrepos/bacphen-awareness
- **Purpose:** Schema inference and awareness for bacterial phenotypes
- **Useful Resource:** BacDive inferred schema at `data/output/954eac922928d7abfd6130e7cc64a88c/bacdive_strains_genson_schema.json`
- **Tool:** genson (JSON schema inference)

### Data Source Repositories

#### bacteria-archaea-traits (Madin et al.)
- **GitHub:** https://github.com/bacteria-archaea-traits/bacteria-archaea-traits
- **Also:** https://github.com/jmadin/bacteria_archaea_traits (original)
- **Local:** ~/Documents/gitrepos/bacteria-archaea-traits
- **Purpose:** Reproducible synthesis of 26 microbial trait sources
- **Format:** CSV/TSV with R rebuild scripts

#### FermentationExplorer
- **GitHub:** https://github.com/thackmann/FermentationExplorer
- **Purpose:** Fermentation pathways and products database

#### Unipathways
- **GitHub:** https://github.com/geneontology/unipathway
- **Purpose:** Pathway ontology for biochemical reactions

#### Extended Prefix Map (EPM)
- **GitHub:** https://github.com/biopragmatics/bioregistry
- **Purpose:** OBO prefix mappings for CURIE resolution

### Related Local Repositories

The following repositories are present locally and may be relevant:

- **envo** (~/Documents/gitrepos/envo) - Environment Ontology development
- **linkml** (~/Documents/gitrepos/linkml) - Linked Data Modeling Language
- **linkml-runtime** - LinkML runtime library
- **linkml-store** - LinkML data store
- **ontogpt** - Ontology-based GPT tools
- **schema-automator** - Schema generation/automation
- **semantic-sql** - Semantic SQL tooling
- **relation-graph** - Ontology relation visualization
- **nmdc-schema** - National Microbiome Data Collaborative schema
- **nmdc-ontology** - NMDC ontology development
- **biolink-subset** - Biolink Model subset work
- **external-metadata-awareness** - Metadata awareness tooling
- **sample-annotator** - Sample annotation tools
- **geoloc-tools** - Geolocation tooling

### Infrastructure & Hub Resources

#### KGHub
- **What:** Knowledge graph hub infrastructure
- **Usage:** Hosts frozen/versioned data sources
- **Examples:** UniProt proteomes at https://kghub.io/frozen_incoming_data/

---

## File Locations

### METPO Repository
- **Location:** ~/Documents/gitrepos/metpo/
- **Key Files:**
  - `src/templates/metpo_sheet.tsv` - ROBOT template defining classes
  - `metpo.owl` - Generated OWL ontology
  - `metpo.json` - Generated JSON-LD
  - `Makefile` - Build pipeline
  - Various analysis/documentation markdown files

### KG-Microbe Repository
- **Location:** ~/Documents/gitrepos/kg-microbe/
- **Key Files:**
  - `download.yaml` - Configuration for all data source downloads
  - `data/raw/` - Raw downloaded data files
  - ETL scripts (location TBD)
  - Output KGX files (location TBD)

### bacphen-awareness Repository
- **Location:** ~/Documents/gitrepos/bacphen-awareness/
- **Key Files:**
  - `data/output/*/bacdive_strains_genson_schema.json` - Inferred BacDive schema

---

## Open Questions & Documentation Needs

### Project Structure
- [ ] What are the "old practices" for KGX generation?
- [ ] Is there a migration plan to newer KGX practices?
- [ ] What ML framework is CultureBot using?
- [ ] What are the specific deliverables for the LDRD grant?

### Data Pipeline
- [ ] Where is the BactoTraits CSV → MongoDB transformation code?
- [ ] What ETL tools are used for KG-Microbe construction?
- [ ] How are METPO terms integrated into KGX nodes?
- [ ] What's the build/release pipeline for KG-Microbe?

### Placeholder CURIE Migration
- [ ] How are legacy placeholder CURIEs (`oxygen:aerobic`) being transitioned to METPO?
- [ ] Are there mapping/equivalence files?
- [ ] What's the timeline for complete migration?

### Validation & Quality
- [ ] Are there existing validation scripts for KG-Microbe?
- [ ] How is METPO-source synchronization maintained?
- [ ] What QA/QC processes are in place?

### Collaboration & Roles
- [ ] Who is the PI? (for LDRD grant documentation)
- [ ] Team structure and responsibilities?
- [ ] External collaborators?

---

## Next Steps for Documentation

1. **Interview/Clarification Session:**
   - Get details on CultureBot ML approach
   - Understand "old practices" for KGX
   - Map out complete ETL pipeline
   - Identify all team members and roles

2. **Code Exploration:**
   - Examine KG-Microbe ETL scripts
   - Find placeholder CURIE usage in KGX output
   - Locate transformation code for BactoTraits
   - Document build pipelines

3. **Create Architecture Diagram:**
   - Data flow from sources → MongoDB → KG-Microbe → CultureBot ML
   - METPO's role in the pipeline
   - Technology stack at each stage

4. **Update This Document:**
   - Fill in [TBD] placeholders
   - Add missing links
   - Expand ML framework details
   - Document validation processes
