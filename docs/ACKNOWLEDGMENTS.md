# Acknowledgments

METPO development and research relies on numerous external data sources and ontologies. We gratefully acknowledge the following projects and their contributors.

---

## Microbial Trait Databases

### BactoTraits
**Cébron, A., Bernier, C., Ragon, M., Benoit, N., Restrepo-Ortiz, C.X., Gaucherand, S., et al. (2021)**
"BactoTraits: A functional trait database for bacteria."
*Ecological Indicators*, DOI: [available from repository](https://github.com/TrEE-TIMC-MaMiV/BactoTraits)

- **Data**: 19,455 bacterial strains with functional trait annotations
- **Usage**: Reconciliation with METPO terms, coverage analysis
- **Repository**: https://github.com/TrEE-TIMC-MaMiV/BactoTraits
- **License**: See repository for terms

### Madin et al. Dataset
**Madin, J.S., Nielsen, D.A., Brbić, M., Corkrey, R., Danko, D., Edwards, K., et al. (2020)**
"A synthesis of bacterial and archaeal phenotypic trait data."
*Scientific Data*, 7:170. DOI: [10.1038/s41597-020-0497-4](https://doi.org/10.1038/s41597-020-0497-4)

- **Data**: 172,324 strain-level records with phenotypic traits, pathways, and carbon substrates
- **Usage**: Comprehensive trait coverage analysis, pathway mapping
- **Repository**: https://github.com/bacteria-archaea-traits/bacteria-archaea-traits
- **License**: See repository for terms

### BacDive
**Reimer, L.C., Sardà Carbasse, J., Koblitz, J., Ebeling, C., Podstawka, A., Overmann, J. (2022)**
"BacDive in 2022: the knowledge base for standardized bacterial and archaeal data."
*Nucleic Acids Research*, 50(D1):D741–D746. DOI: [10.1093/nar/gkab961](https://doi.org/10.1093/nar/gkab961)

- **Data**: Comprehensive bacterial and archaeal strain information
- **Usage**: Analysis via kg-microbe, oxygen phenotype mappings
- **Website**: https://bacdive.dsmz.de/
- **API**: REST service for programmatic access
- **License**: See website for terms

---

## External Ontologies

### OBO Foundry Ontologies

We use terms and mappings from numerous OBO Foundry ontologies:

**Core Phenotype Ontologies:**
- **PATO** (Phenotype And Trait Ontology) - http://purl.obolibrary.org/obo/pato.owl
- **OBA** (Ontology of Biological Attributes) - http://purl.obolibrary.org/obo/oba.owl
- **UPHENO** (Unified Phenotype Ontology) - http://purl.obolibrary.org/obo/upheno.owl

**Microbial-Specific Ontologies:**
- **MicrO** (Ontology of Microbial Phenotypes) - http://purl.obolibrary.org/obo/micro.owl
- **MCO** (Microbial Conditions Ontology) - http://purl.obolibrary.org/obo/mco.owl
- **FLOPO** (Flora Phenotype Ontology) - http://purl.obolibrary.org/obo/flopo.owl

**Environmental and Process Ontologies:**
- **ENVO** (Environment Ontology) - http://purl.obolibrary.org/obo/envo.owl
- **GO** (Gene Ontology) - http://purl.obolibrary.org/obo/go.owl
- **ChEBI** (Chemical Entities of Biological Interest) - http://purl.obolibrary.org/obo/chebi.owl

**Model Organism Phenotypes:**
- **FYPO** (Fission Yeast Phenotype Ontology) - http://purl.obolibrary.org/obo/fypo.owl
- **WBPhenotype** (C. elegans Phenotype Ontology) - http://purl.obolibrary.org/obo/wbphenotype.owl
- **MPO** (Mammalian Phenotype Ontology) - http://purl.obolibrary.org/obo/mpo.owl
- **ZFA** (Zebrafish Anatomy Ontology) - http://purl.obolibrary.org/obo/zfa.owl
- **XPO** (Xenopus Phenotype Ontology) - http://purl.obolibrary.org/obo/xpo.owl

**Plant and Agricultural Ontologies:**
- **TO** (Plant Trait Ontology) - http://purl.obolibrary.org/obo/to.owl
- **AGRO** (Agronomy Ontology) - http://purl.obolibrary.org/obo/agro.owl
- **PLANP** (Planarian Phenotype Ontology) - http://purl.obolibrary.org/obo/planp.owl

**Other Domain Ontologies:**
- **BCO** (Biological Collections Ontology) - http://purl.obolibrary.org/obo/bco.owl
- **GAZ** (Gazetteer) - http://purl.obolibrary.org/obo/gaz.owl
- **APOLLO_SV** (Apollo Structured Vocabulary) - http://purl.obolibrary.org/obo/apollo_sv.owl
- **MIRO** (Mosquito Insecticide Resistance Ontology) - http://purl.obolibrary.org/obo/miro.owl

**License**: OBO Foundry ontologies are typically released under CC-BY 4.0 or CC0 licenses. See individual ontology documentation for specific terms.

---

### BioPortal Ontologies

We use the following ontologies from NCBO BioPortal:

**Microbial Ontologies:**
- **OMP** (Ontology of Microbial Phenotypes) - https://bioportal.bioontology.org/ontologies/OMP
- **MPO** (MPO/RIKEN Microbial Phenotype Ontology) - https://bioportal.bioontology.org/ontologies/MPO
- **D3O** (DSMZ Digital Diversity Ontology) - https://bioportal.bioontology.org/ontologies/D3O
- **BIPON** (Bacterial Interlocked Process Ontology) - https://bioportal.bioontology.org/ontologies/BIPON
- **MISO** (Microbial Conditions Ontology) - https://bioportal.bioontology.org/ontologies/MISO
- **MEO** (Metagenome and Environment Ontology) - https://bioportal.bioontology.org/ontologies/MEO

**Food and Growth Media:**
- **FMPM** (Food Matrix for Predictive Microbiology) - https://bioportal.bioontology.org/ontologies/FMPM
- **GMO** (Growth Medium Ontology) - https://bioportal.bioontology.org/ontologies/GMO
- **OFSMR** (Open Predictive Microbiology Ontology) - https://bioportal.bioontology.org/ontologies/OFSMR

**Clinical and Typing:**
- **ID-AMR** (Infectious Diseases and Antimicrobial Resistance) - https://bioportal.bioontology.org/ontologies/ID-AMR
- **TYPON** (Microbial Typing Ontology) - https://bioportal.bioontology.org/ontologies/TYPON
- **MCCV** (Microbial Culture Collection Vocabulary) - https://bioportal.bioontology.org/ontologies/MCCV

**License**: See individual BioPortal ontology pages for license terms.

---

### Manual Ontologies

- **N4L Phenotypic Ontology (2016)** - Merged phenotypic ontology for chemical utilization
  - Source: Local curation and merging
  - Location: `external/ontologies/manual/n4l_merged.owl`

- **FAO** (Food Additive Ontology) - Chemical additives and food components
  - Source: https://s3.amazonaws.com/bbop-sqlite/fao.owl

---

## Semsql Databases

Pre-built semsql databases from the **Berkeley Bioinformatics Open-source Projects (BBOP)**:

- **BBOP S3 Bucket**: https://s3.amazonaws.com/bbop-sqlite/
- **Databases used**: mco.db, omp.db, fao.db
- **Tool**: semsql by linkml - https://github.com/INCATools/semantic-sql

---

## Embedding Infrastructure

### ChromaDB
- **Tool**: ChromaDB vector database - https://www.trychroma.com/
- **Usage**: 452,942 ontology term embeddings for semantic similarity search
- **Model**: OpenAI text-embedding-3-small (1536 dimensions)

### OpenAI
- **API**: OpenAI API for embeddings and LLM-based extraction
- **Cost**: ~$45-50 for non-OLS ontology embeddings
- **Usage**: Semantic matching, OntoGPT literature extraction

---

## Software Tools

### Ontology Development Kit (ODK)
- **Tool**: ODK - https://github.com/INCATools/ontology-development-kit
- **Usage**: METPO ontology build system
- **License**: BSD-3-Clause

### ROBOT
- **Tool**: ROBOT (A tool for working with OWL ontologies) - http://robot.obolibrary.org/
- **Usage**: Ontology processing, SPARQL queries, term extraction
- **License**: BSD-3-Clause

### OAKLib
- **Tool**: Ontology Access Kit - https://github.com/INCATools/ontology-access-kit
- **Usage**: Hierarchical queries, coherence analysis
- **License**: BSD-3-Clause

### OntoGPT
- **Tool**: OntoGPT - https://github.com/monarch-initiative/ontogpt
- **Usage**: Literature mining with METPO grounding
- **License**: BSD-3-Clause

### BioPortal
- **Service**: NCBO BioPortal - https://bioportal.bioontology.org/
- **METPO Page**: https://bioportal.bioontology.org/ontologies/METPO
- **Usage**: Primary ontology hosting, browsing, search, and API access
- **Maintainer**: National Center for Biomedical Ontology (NCBO)
- **License**: Service provided by Stanford University

---

## KG-Microbe Integration

**Project**: KG-Microbe - Knowledge Graph for Microbes
**Repository**: https://github.com/Knowledge-Graph-Hub/kg-microbe (assumed)

- **Data Processing**: BactoTraits, Madin, and BacDive transformations
- **Graph Construction**: Biolink model-compliant knowledge graph
- **Collaboration**: Shared data sources and workflows

---

## NCBI Taxonomy

**NCBI Taxonomy Database**
- **Source**: ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/
- **Files**: nodes.dmp (194M), names.dmp (258M)
- **Usage**: Taxonomic rank extraction, organism classification
- **License**: Public domain (U.S. Government work)

---

---

## Data Provenance and Loading Procedures

### BactoTraits MongoDB Import

**Source File**: `local/bactotraits/BactoTraits_databaseV2_Jun2022.csv` (8.6 MB, 19,455 strains)
- **Downloaded from**: https://github.com/TrEE-TIMC-MaMiV/BactoTraits
- **Version**: v2, June 2022
- **Format**: CSV with 106 trait columns

**Loading Procedure**:
```bash
make import-bactotraits
# Uses: metpo/tools/import_bactotraits.py
# Creates MongoDB database: bactotraits
# Collections: bactotraits (19,455 docs), field_mappings (106 docs), files (2 docs)
```

**Import Script**: `metpo/tools/import_bactotraits.py`
- Sanitizes field names for MongoDB compatibility (handles special characters, comparison operators)
- Converts binary trait values to integers
- Creates indexes on Bacdive_ID, ncbitaxon_id, and taxonomy fields
- See: `docs/bactotraits_reconciliation_and_pipeline.md` for full workflow

### Madin et al. MongoDB Import

**Source File**: `local/madin/madin_etal.csv` (44 MB, 172,324 strains)
- **Downloaded from**: https://github.com/bacteria-archaea-traits/bacteria-archaea-traits
- **Specific file**: `output/condensed_traits_NCBI.csv`
- **Via**: kg-microbe repository's download workflow
- **Taxonomy**: NCBI Taxonomy classification
- **Format**: CSV with 35 fields including `pathways` and `carbon_substrates`

**Loading Procedure**:
```bash
make import-madin
# Uses: mongoimport directly (CSV import)
# Creates MongoDB database: madin
# Collections: madin (172,324 docs), files (2 docs)
```

**Import Command**: `mongoimport --db madin --collection madin --type csv --file local/madin/madin_etal.csv --headerline --drop`
- See: `local/madin/madin_files_analysis.md` for detailed file provenance
- See: `docs/madin_field_analysis.md` for field structure documentation

### BacDive Data Access

**Raw Data Location**: `../kg-microbe/data/raw/bacdive_strains.json` (796 MB)
- **Downloaded via**: BacDive REST API (https://bacdive.dsmz.de/api/bacdive/)
- **Download script**: `~/Documents/gitrepos/kg-microbe/utils/download_bacdive.py`
- **Transformation**: Performed in kg-microbe repository (not in metpo)
- **Format**: JSON (strain-level records)

**METPO Analysis**: BacDive is NOT imported to MongoDB in metpo repository
- Analysis via SPARQL queries: `sparql/bacdive_oxygen_phenotype_mappings.rq`
- Mapping outputs: `data/generated/bacdive_oxygen_phenotype_mappings.tsv`
- Documentation: 6 analysis files in `docs/bacdive_*.md`

**Rationale**: BacDive transformation and graph construction happens in kg-microbe; METPO uses SPARQL to generate ontology mappings from the transformed data.

---

## Literature Mining Data Sources

### Abstracts and Full-Text Papers

**Source Repository**: CMM-AI (Critical Minerals and Materials AI project)
- **Location**: `../CMM-AI` (sibling repository)
- **GitHub**: [Not publicly available - LBNL internal project]
- **Project**: DOE BER FY26 CMM Pilot ($850K) - "Advanced Biorecovery of Critical Minerals"
- **PI**: Ning Sun (LBNL); Co-PI: Marcin Joachimiak (LBNL, KG-Microbe lead)

**Papers Copied to METPO**:
- **Full-text PDFs**: `literature_mining/CMM-AI/publications/` (49 PDFs, ~11 MB)
- **Extracted text**: `literature_mining/CMM-AI/publications-txt/` (24 TXT files)
- **Formats**: PDF, MHTML, Markdown extracts
- **Topics**: Rare earth element recovery, lanthanophore biosynthesis, microbial metal accumulation

### Abstract Fetching Workflow

**Tool**: artl-mcp 0.34.0 - https://github.com/monarch-initiative/artl-mcp
- **Method**: Europe PMC API via `get_europepmc_paper_by_id`
- **Input**: `literature_mining/publication_ids.tsv` (36 unique papers)
- **Output**: Individual abstract text files in `literature_mining/abstracts/`

**Retrieval Statistics** (documented in `literature_mining/abstract_fetching_report.md`):
- 19 papers retrieved via PMID (100% success)
- 10 papers retrieved via DOI (59% success, 8 PMIDs discovered)
- 7 papers unavailable in Europe PMC (arXiv, recent Elsevier, regional journals)
- **Total coverage**: 29/36 papers (81%)

**Fetching Scripts**:
- `literature_mining/scripts/fetch_doi_abstracts.py` - Europe PMC API fetching
- `literature_mining/scripts/extract_abstracts_from_files.py` - Local PDF text extraction
- `literature_mining/scripts/dedupe_and_filter_abstracts.py` - Deduplication

**Documentation**:
- `literature_mining/abstract_fetching_guide.md` - Workflow overview
- `literature_mining/abstract_fetching_report.md` - Detailed retrieval results
- `docs/icbo_cmm_details.md` - CMM project context and METPO's role

---

## How to Cite METPO

If you use METPO in your research, please cite:

**[To be added: METPO publication when available]**

And acknowledge the specific data sources and ontologies you used from the lists above.

---

## Contributing Acknowledgments

To add or correct acknowledgment information:
1. Open an issue: https://github.com/berkeleybop/metpo/issues
2. Or submit a pull request with updates to this file
3. Include: Citation, DOI/URL, brief description of usage

---

**Last Updated**: November 10, 2025
