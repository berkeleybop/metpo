# kg-microbe Data Sources

Based on the `download.yaml` configuration and raw data directory, here are all the datasets that feed into kg-microbe:

## Primary Microbial Trait Datasets

### 1. **BacDive** 
- URL: Google Drive (internal)
- File: `bacdive_strains.json`
- Description: Bacterial Diversity database - comprehensive strain-level information
- MongoDB collection: `bacdive.strains_api`

### 2. **Madin et al.** (bacteria-archaea-traits)
- URL: https://github.com/bacteria-archaea-traits/bacteria-archaea-traits
- File: `madin_etal.csv` (condensed_traits_NCBI.csv)
- Description: Condensed bacterial and archaeal traits compiled from literature
- MongoDB collection: `madin.madin`

### 3. **BactoTraits**
- URL: https://ordar.otelo.univ-lorraine.fr/files/ORDAR-53/BactoTraits_databaseV2_Jun2022.csv
- File: `BactoTraits_databaseV2_Jun2022.csv`
- Description: Bacterial traits database (June 2022 version)
- MongoDB collection: `bactotraits.bactotraits`

### 4. **MediaDive**
- URL: https://mediadive.dsmz.de/rest/media
- File: `mediadive.json`
- Description: Culture media database from DSMZ

### 5. **Fermentation Explorer**
- URL: https://github.com/thackmann/FermentationExplorer
- File: `fermentation_explorer.csv`
- Description: Fermentation pathways and products database

### 6. **Disbiome**
- URL: https://disbiome.ugent.be:8080/experiment
- File: `disbiome.json`
- Description: Human microbiome-disease associations

### 7. **Wallen et al.**
- URL: Springer Nature supplementary materials
- File: `wallen_etal.xlsx`
- Description: Study on gut microbiome (Nature Communications 2022)

## Ontologies

### 8. **ENVO** (Environment Ontology)
- URL: http://purl.obolibrary.org/obo/envo.json
- File: `envo.json`

### 9. **ChEBI** (Chemical Entities of Biological Interest)
- URL: http://purl.obolibrary.org/obo/chebi.owl.gz
- Files: `chebi.owl.gz`, `chebi.owl`, `chebi.json`, `chebi.db`

### 10. **GO** (Gene Ontology)
- URL: http://purl.obolibrary.org/obo/go.json
- Files: `go.json`, `go.owl`

### 11. **NCBITaxon** (NCBI Taxonomy)
- URL: http://purl.obolibrary.org/obo/ncbitaxon.owl.gz
- Files: `ncbitaxon.owl.gz`, `ncbitaxon.owl`, `ncbitaxon.db`

### 12. **MONDO** (Mondo Disease Ontology)
- URL: https://purl.obolibrary.org/obo/mondo/mondo.json
- File: `mondo.json`

### 13. **HP** (Human Phenotype Ontology)
- URL: https://purl.obolibrary.org/obo/hp/hp.json
- File: `hp.json`

### 14. **METPO** (Microbial Ecophysiological Traits and Phenotypes Ontology)
- URL: https://raw.githubusercontent.com/berkeleybop/metpo/refs/heads/main/metpo.owl
- Files: `metpo.owl`, `metpo.json`

## Protein and Pathway Data

### 15. **UniProt Proteomes** (Functional Microbes)
- URL: https://kghub.io/frozen_incoming_data/uniprot/uniprot_proteomes.tar.gz
- File: `uniprot_proteomes.tar.gz`

### 16. **UniProt Human**
- URL: https://kghub.io/frozen_incoming_data/uniprot/uniprot_human.tar.gz
- File: `uniprot_human.tar.gz`

### 17. **Unipathways**
- URL: https://github.com/geneontology/unipathway
- Files: `upa.owl`, `upa.json`

### 18. **EC** (Enzyme Commission)
- URL: https://w3id.org/biopragmatics/resources/eccode/
- Files: `ec.json`, `ec.owl.gz`

### 19. **RHEA** (Biochemical Reactions)
- URL: https://ftp.expasy.org/databases/rhea/tsv/
- Files: `rhea2go.tsv`, `rhea2ec.tsv`

## Disease and Chemical Associations

### 20. **CTD** (Comparative Toxicogenomics Database)
- URL: https://ctdbase.org/reports/CTD_chemicals_diseases.tsv.gz
- File: `CTD_chemicals_diseases.tsv.gz`
- Description: Chemical-disease associations

## Conversion Tables and Support Files

### 21. **Environments Conversion Table**
- URL: https://github.com/bacteria-archaea-traits/bacteria-archaea-traits
- File: `environments.csv`

### 22. **EPM** (Extended Prefix Map)
- URL: https://github.com/biopragmatics/bioregistry
- File: `epm.json`
- Description: OBO prefix mappings for CURIE resolution

## Summary by Category

**Primary Trait Sources (3):**
1. BacDive
2. Madin et al.
3. BactoTraits

**Ontologies (7):**
4. ENVO, ChEBI, GO, NCBITaxon, MONDO, HP, METPO

**Biochemical Data (5):**
5. UniProt (2 sources), Unipathways, EC, RHEA

**Disease/Association Data (3):**
6. Disbiome, CTD, Wallen et al.

**Other (2):**
7. MediaDive, Fermentation Explorer

**Total: 20+ distinct data sources**
