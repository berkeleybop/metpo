# KG-Microbe Transform Files - Complete Reference

**Date:** 2025-10-03
**Location:** `~/Documents/gitrepos/kg-microbe/kg_microbe/transform_utils/`

---

## Overview

Each data source in kg-microbe has a dedicated transform module that:
1. Reads raw data from `data/raw/`
2. Transforms it into KGX format (nodes.tsv, edges.tsv)
3. Maps values to ontology terms (METPO, ChEBI, GO, ENVO, etc.)
4. Creates placeholder CURIEs when mappings don't exist

---

## Primary Trait Data Sources

### 1. Madin et al. (bacteria-archaea-traits)
- **File:** `kg_microbe/transform_utils/madin_etal/madin_etal.py`
- **Class:** `MadinEtAlTransform`
- **Input:** `condensed_traits_NCBI.csv` from https://github.com/bacteria-archaea-traits/bacteria-archaea-traits
- **Fields Processed:**
  - tax_id → NCBITaxon CURIE
  - org_name
  - metabolism → METPO mapping
  - pathways → METPO mapping (with fallback to GO NER or placeholder)
  - carbon_substrates → METPO mapping (with fallback to ChEBI NER or placeholder)
  - cell_shape → METPO mapping (with fallback to placeholder)
  - isolation_source → ENVO mapping
- **METPO Integration:**
  - Loads METPO mappings via `load_metpo_mappings("madin synonym or field")`
  - First tries METPO, then falls back to NER (Named Entity Recognition)
  - Creates placeholder CURIEs like `pathway:nitrate_reduction` when not in METPO
- **Predicates:**
  - Pathways: `biolink:capable_of` (default) or from METPO tree traversal
  - Metabolism: `biolink:has_phenotype` (default) or from METPO
  - Carbon substrates: `biolink:consumes` (default) or from METPO
  - Cell shape: `biolink:has_phenotype` (default) or from METPO
- **NER (Named Entity Recognition):**
  - Uses OAK (OntologyAccess Kit) to annotate pathways → GO
  - Uses OAK to annotate carbon_substrates → ChEBI
  - Output: `go_ner.tsv`, `chebi_ner.tsv`

### 2. BacDive
- **File:** `kg_microbe/transform_utils/bacdive/bacdive.py`
- **Class:** `BacDiveTransform`
- **Input:** `bacdive_strains.json` (from BacDive API)
- **Description:** Bacterial Diversity Metadatabase from DSMZ
- **Key Features:**
  - Handles nested JSON structure from API
  - Processes oxygen tolerance, halophily, antibiotic resistance
  - Links to culture collection numbers
  - Processes physiology and metabolism data
- **METPO Integration:** Uses BacDive keyword synonyms
- **Constants Used:**
  - `ACTIVITY_KEY`, `ANTIBIOGRAM`, `ANTIBIOTIC_RESISTANCE`
  - Various API field mappings

### 3. BactoTraits
- **File:** `kg_microbe/transform_utils/bactotraits/bactotraits.py`
- **Class:** `BactoTraitsTransform`
- **Input:** `BactoTraits_databaseV2_Jun2022.csv`
- **Description:** Bacterial functional traits database (~19,455 strains)
- **Key Features:**
  - Handles one-hot encoding
  - Links to BacDive IDs for crosswalking
  - Processes custom CURIEs from YAML file
  - Maps to NCBITaxon
- **METPO Integration:** Likely uses BactoTraits-specific synonyms
- **Fields:** Oxygen preference, cell shape, motility, temperature, pH, GC content, etc.
- **Constants Used:**
  - `BACDIVE_ID_COLUMN`, `BACDIVE_CULTURE_COLLECTION_NUMBER_COLUMN`
  - `CUSTOM_CURIES_YAML_FILE`
  - `HAS_PHENOTYPE`, `CAPABLE_OF_PREDICATE`

---

## Disease and Association Data Sources

### 4. CTD (Comparative Toxicogenomics Database)
- **File:** `kg_microbe/transform_utils/ctd/ctd.py`
- **Class:** `CTDTransform`
- **Input:** `CTD_chemicals_diseases.tsv.gz`
- **Description:** Chemical-disease associations
- **Key Features:**
  - Maps MeSH chemicals → ChEBI via xrefs
  - Maps MeSH diseases → MONDO via xrefs
  - Uses Node Normalizer for CURIE resolution
  - Handles CAS registry numbers
- **Predicates:** `chemical_to_disease_edge` (associated_with)
- **Ontology Mappings:**
  - MeSH → ChEBI (chemicals)
  - MeSH → MONDO (diseases)
- **Constants Used:**
  - `CAS_RN_PREFIX`, `MESH_PREFIX`, `MONDO_PREFIX`, `CHEBI_PREFIX`
  - `NODE_NORMALIZER_URL`
  - `CHEBI_XREFS_FILEPATH`, `MONDO_XREFS_FILEPATH`

### 5. Disbiome
- **File:** `kg_microbe/transform_utils/disbiome/disbiome.py`
- **Class:** `DisbiomeTransform`
- **Input:** `disbiome.json`
- **Description:** Human microbiome-disease associations
- **Key Features:**
  - Processes elevated/reduced microbe associations with diseases
  - Links organisms to NCBITaxon
  - Handles qualitative outcomes (increased/decreased likelihood)
- **Predicates:**
  - `associated_with_increased_likelihood_of`
  - `associated_with_decreased_likelihood_of`
- **Fields:**
  - `DISBIOME_ORGANISM_ID`, `DISBIOME_ORGANISM_NAME`
  - `DISBIOME_DISEASE_NAME`
  - `DISBIOME_ELEVATED`, `DISBIOME_REDUCED`
  - `DISIOME_QUALITATIVE_OUTCOME`

### 6. Wallen et al.
- **File:** `kg_microbe/transform_utils/wallen_etal/wallen_etal.py`
- **Class:** `WallenEtAlTransform`
- **Input:** Excel file with supplementary data (Nature Communications 2022)
- **Description:** Gut microbiome study - Parkinson's Disease associations
- **Key Features:**
  - Reads "Supplementary Data 1" tab
  - Processes FDR (False Discovery Rate) statistics
  - Compares relative abundance in PD vs NHC (neurotypical healthy controls)
- **Fields:**
  - `FDR_COLUMN` (False Discovery Rate)
  - `SPECIES_COLUMN`
  - `PD_ABUNDANCE_COLUMN` (Relative Abundance in PD)
  - `NHC_ABUNDANCE_COLUMN` (Relative Abundance in NHC)
- **Predicates:**
  - `associated_with_increased_likelihood_of`
  - `associated_with_decreased_likelihood_of`

---

## Culture Media and Fermentation

### 7. MediaDive
- **File:** `kg_microbe/transform_utils/mediadive/mediadive.py`
- **Class:** `MediaDiveTransform`
- **Input:** `mediadive.json` (from DSMZ REST API)
- **Description:** Culture media database
- **Key Features:**
  - Processes culture media recipes
  - Links media to organisms
  - Handles chemical components
  - Uses OAK for ontology lookups

---

## Protein and Pathway Data Sources

### 8. UniProt Functional Microbes
- **File:** `kg_microbe/transform_utils/uniprot_functional_microbes/uniprot_functional_microbes.py`
- **Class:** `UniprotFunctionalMicrobesTransform`
- **Input:** `uniprot_proteomes.tar.gz` (from kghub.io)
- **Description:** Proteomes for functional microbes
- **Key Features:**
  - Processes protein annotations
  - Maps to GO (Gene Ontology) biological processes
  - Uses GO category trees for hierarchy
  - Tracks obsolete GO terms
  - Links proteins to MONDO diseases
- **Files:**
  - `UNIPROT_PROTEOMES_FILE`
  - `GO_CATEGORY_TREES_FILE`
  - `go_obsolete_terms.tsv` (tracking file)
- **Uses:** Multiprocessing pool for parallel processing

### 9. UniProt Human
- **File:** `kg_microbe/transform_utils/uniprot_human/uniprot_human.py`
- **Class:** `UniprotHumanTransform`
- **Input:** `uniprot_human.tar.gz` (from kghub.io)
- **Description:** Human proteome
- **Key Features:**
  - Similar to functional microbes transform
  - Maps to GO biological processes
  - Links to MONDO diseases
  - Tracks obsolete terms
- **Files:**
  - `UNIPROT_HUMAN_FILE`
  - `go_obsolete_terms.tsv`

### 10. RHEA (Biochemical Reactions)
- **File:** `kg_microbe/transform_utils/rhea_mappings/rhea_mappings.py`
- **Class:** `RheaMappingsTransform`
- **Input:** RHEA TSV files from ftp.expasy.org
  - `rhea2go.tsv` (RHEA to GO mappings)
  - `rhea2ec.tsv` (RHEA to EC mappings)
- **Description:** Biochemical reaction database mappings
- **Key Features:**
  - Maps reactions to GO biological processes
  - Maps reactions to EC (Enzyme Commission) numbers
  - Uses PyOBO for relation extraction
  - Uses extended prefix map for CURIE conversion
  - Requests FTP for data access
- **Dependencies:**
  - `pyobo` (Python OBO library)
  - `requests_ftp`
  - `curies` (CURIE handling)
- **Ontologies Used:**
  - ChEBI (substrate/product chemicals)
  - GO (biological processes)
  - EC (enzyme classification)

---

## Ontology Processing

### 11. Ontologies Transform
- **File:** `kg_microbe/transform_utils/ontologies/ontologies_transform.py`
- **Class:** `OntologiesTransform`
- **Description:** Processes ontology files (OWL, JSON) into KGX format
- **Ontologies Handled:**
  - ENVO (Environment Ontology)
  - ChEBI (Chemical Entities of Biological Interest)
  - GO (Gene Ontology)
  - NCBITaxon (NCBI Taxonomy)
  - MONDO (Disease Ontology)
  - HP (Human Phenotype Ontology)
  - METPO (Microbial Ecophysiological Traits and Phenotypes)
  - EC (Enzyme Commission)
  - Unipathways
- **Key Features:**
  - Handles gzipped OWL files
  - Creates cross-reference (xref) files for mappings
  - Uses KGX transformer for OWL → TSV conversion
  - Filters terms using exclusion list
  - Extracts specific relations (enabled_by, part_of)
- **Files Generated:**
  - `CHEBI_XREFS_FILEPATH` - ChEBI cross-references
  - `MONDO_XREFS_FILEPATH` - MONDO cross-references
  - `EXCLUSION_TERMS_FILE` - Terms to exclude from graph
- **Relations:**
  - `ENABLED_BY_PREDICATE`, `ENABLED_BY_RELATION`
  - `PART_OF_PREDICATE`

---

## Special Files

### 12. Base Transform Class
- **File:** `kg_microbe/transform_utils/transform.py`
- **Class:** `Transform` (base class)
- **Description:** Abstract base class for all transforms
- **Provides:**
  - Common initialization
  - Output file paths (nodes.tsv, edges.tsv)
  - Header definitions
  - NLP/NER utilities directory
  - Progress tracking setup

### 13. Constants
- **File:** `kg_microbe/transform_utils/constants.py`
- **Description:** Centralized constants for all transforms
- **Contains:**
  - Prefix definitions (NCBITAXON_PREFIX, CHEBI_PREFIX, GO_PREFIX, etc.)
  - Column name constants
  - Edge/predicate types (HAS_PHENOTYPE, CAPABLE_OF_PREDICATE, etc.)
  - Category definitions (BIOLOGICAL_PROCESS, PATHWAY_CATEGORY, etc.)
  - File paths (ontology sources, temp directories)
  - Source names (MADIN_ETAL, BACDIVE, BACTOTRAITS, etc.)
  - Biolink predicates

### 14. Example Transform
- **File:** `kg_microbe/transform_utils/example_transform/example_transform.py`
- **Class:** `ExampleTransform`
- **Description:** Template/example for creating new transforms
- **Purpose:** Documentation and starting point for new data sources

---

## Data Flow Summary

### METPO Integration Pattern (used by multiple transforms)

```
Raw Data Value
    ↓
1. Check METPO mappings (load_metpo_mappings)
    ↓
2. If found:
   - Use METPO CURIE
   - Use METPO label
   - Traverse tree for biolink category
   - Get predicate from METPO properties
    ↓
3. If NOT found:
   - Try NER (Named Entity Recognition)
   - Use GO/ChEBI/ENVO ontology match
    ↓
4. If still NOT found:
   - Create placeholder CURIE
   - Format: {prefix}:{value}
   - Examples: pathway:nitrate_reduction, shape:bacillus
```

### Transform Workflow

```
1. Download (via download.yaml)
    ↓
2. Raw data in data/raw/
    ↓
3. Transform class processes:
   - Read raw format (CSV/JSON/TSV/Excel/OWL)
   - Map to ontology terms
   - Create nodes (id, category, name)
   - Create edges (subject, predicate, object, relation)
    ↓
4. Output KGX files:
   - nodes.tsv
   - edges.tsv
    ↓
5. Merge step (combines all transforms)
    ↓
6. Final KG-Microbe knowledge graph
```

---

## File Naming Conventions

### Transform Module Structure
```
kg_microbe/transform_utils/
├── {source_name}/
│   ├── __init__.py
│   └── {source_name}.py  # Contains {SourceName}Transform class
├── constants.py
└── transform.py  # Base class
```

### Examples
- `madin_etal/madin_etal.py` → `MadinEtAlTransform`
- `bacdive/bacdive.py` → `BacDiveTransform`
- `bactotraits/bactotraits.py` → `BactoTraitsTransform`

---

## METPO Mapping Files Referenced

All transforms that use METPO load mappings from GitHub:
- **URL:** `https://raw.githubusercontent.com/berkeleybop/metpo/refs/tags/2025-09-23/src/templates/metpo_sheet.tsv`
- **Synonym Columns:**
  - `madin synonym or field` (for Madin transform)
  - `bacdive keyword synonym` (for BacDive transform)
  - BactoTraits-specific column (likely exists)
- **Loaded by:** `kg_microbe/utils/mapping_file_utils.py::load_metpo_mappings()`

---

## Impact of Adding Terms to METPO

When new terms are added to METPO:

1. **Next kg-microbe build automatically uses them:**
   - Transform fetches latest METPO from GitHub
   - New synonyms create mappings
   - Placeholder CURIEs are replaced with METPO CURIEs

2. **Example: Adding missing Madin pathways**
   - Current: `pathway:nitrate_reduction` (placeholder)
   - After adding to METPO: `METPO:XXXXXXX` (proper CURIE)
   - Automatic biolink category inference
   - Proper predicate assignment

3. **No code changes required:**
   - Mapping is dynamic
   - Tree traversal finds biolink equivalents
   - Predicates inferred from parent classes

---

## Summary Statistics

| Data Source | Transform File | METPO Integration | Primary Output |
|-------------|----------------|-------------------|----------------|
| **Madin et al.** | madin_etal.py | Yes (pathways, metabolism, cell_shape, carbon_substrates) | Organism traits |
| **BacDive** | bacdive.py | Yes (oxygen tolerance, halophily) | Strain data |
| **BactoTraits** | bactotraits.py | Yes (phenotypic traits) | Functional traits |
| **CTD** | ctd.py | No (uses ChEBI, MONDO) | Chemical-disease |
| **Disbiome** | disbiome.py | No (uses NCBITaxon, disease names) | Microbiome-disease |
| **Wallen et al.** | wallen_etal.py | No (uses NCBITaxon, disease) | PD associations |
| **MediaDive** | mediadive.py | No (uses culture media) | Growth media |
| **UniProt Functional** | uniprot_functional_microbes.py | No (uses GO, MONDO) | Protein functions |
| **UniProt Human** | uniprot_human.py | No (uses GO, MONDO) | Human proteins |
| **RHEA** | rhea_mappings.py | No (uses GO, EC, ChEBI) | Reactions |
| **Ontologies** | ontologies_transform.py | Processes METPO itself | Ontology nodes |

**Total Transform Files:** 11 source-specific + 1 ontology processor + 1 base class + 1 constants

---

## Tools and Libraries Used

### Ontology Access
- **OAK (OntologyAccess Kit):** `oaklib.get_adapter()`
  - Used by: Madin, BacDive, MediaDive, UniProt transforms
  - Purpose: Query ontologies, perform NER

### NER (Named Entity Recognition)
- **Custom NER utilities:** `kg_microbe.utils.ner_utils`
  - Used by: Madin transform
  - Purpose: Annotate text with GO/ChEBI terms

### Data Processing
- **pandas:** CSV/TSV/Excel reading and manipulation
- **PyOBO:** OBO ontology handling (RHEA transform)
- **curies:** CURIE conversion and validation
- **requests/requests_ftp:** Downloading data
- **requests_cache:** Caching HTTP responses
- **tqdm:** Progress bars

### KGX (Knowledge Graph Exchange)
- **kgx.transformer.Transformer:** OWL → TSV conversion
- **kgx.cli.cli_utils.transform:** CLI utilities

### Parallel Processing
- **multiprocessing:** Used by UniProt transforms for speed

---

## Next Steps for Analysis

1. **Examine BactoTraits transform** to understand actual field mapping vs METPO claims
2. **Check which METPO synonym column** BactoTraits uses
3. **Review custom CURIEs YAML** file used by BactoTraits
4. **Analyze placeholder CURIE usage** across all transforms
5. **Document NER accuracy** for pathway and substrate annotations

---

## Questions to Investigate

1. Which METPO synonym column does BactoTraits transform use?
2. What's in the `CUSTOM_CURIES_YAML_FILE` for BactoTraits?
3. Are there other transforms (not in this list) that we haven't discovered?
4. What percentage of nodes use placeholder CURIEs vs proper ontology terms?
5. How often are NER results preferred over exact METPO matches?
6. Which transforms could benefit from expanded METPO coverage?
