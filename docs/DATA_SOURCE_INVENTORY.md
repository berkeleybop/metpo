# Data Source Inventory: BacDive, BactoTraits, and Madin

**Purpose**: Document provenance, acknowledgments, and consistency of external microbial trait data sources used in METPO.

**Date**: November 10, 2025

---

## Summary

| Data Source | Raw Data | Transformed | MongoDB | Scripts | Reports | Documentation | Citations |
|-------------|----------|-------------|---------|---------|---------|---------------|-----------|
| **BactoTraits** | ✅ 2 versions | ✅ metpo | ✅ Yes | ✅ 8 scripts | ✅ 2 reports | ✅ 3 docs | ✅ Yes |
| **Madin et al.** | ✅ 4 versions | ✅ metpo+kg-microbe | ✅ Yes | ✅ 2 scripts | ✅ 1 report | ✅ 2 docs | ✅ Yes |
| **BacDive** | ✅ kg-microbe | ✅ kg-microbe | ❌ No | ✅ 1 SPARQL | ❌ No | ✅ 6 docs | ✅ Yes |

---

## 1. BactoTraits

### Citation

**Cébron, A. et al. (2021)**
- Title: "BactoTraits: A Functional Trait Database for Bacteria"
- Journal: *Ecological Indicators*
- DOI: Available from repository landing page
- Repository: https://github.com/TrEE-TIMC-MaMiV/BactoTraits

### Data Provenance

#### **Primary Source** (Original Provider Version)
**Location**: `local/bactotraits/BactoTraits_databaseV2_Jun2022.csv`
- **Size**: 8.6 MB
- **Rows**: 19,455 bacterial strains
- **Version**: v2, June 2022
- **Source**: Downloaded from BactoTraits GitHub repository
- **Used in**: MongoDB `bactotraits` database
- **Status**: ✅ **PRIMARY SOURCE** for imports

#### **KG-Microbe Version** (Transformed)
**Location**: `local/bactotraits/BactoTraits.tsv`
- **Size**: 6.1 MB
- **Source**: From kg-microbe repository (`data/raw/BactoTraits_databaseV2_Jun2022.csv`)
- **Transformation**: Reformatted to TSV, possibly filtered
- **Used in**: kg-microbe graph database
- **Status**: ✅ Available for comparison

### Data Workflow

```
BactoTraits GitHub
  ↓ download
local/bactotraits/BactoTraits_databaseV2_Jun2022.csv (8.6M)
  ↓ make import-bactotraits
MongoDB bactotraits.bactotraits collection (19,455 docs)
  ↓ reconcile-bactotraits-coverage
reports/bactotraits-metpo-reconciliation.yaml
```

### Scripts (8 total)

**Location**: `metpo/bactotraits/`
1. `bactotraits_metpo_set_difference.py` - Terms in BactoTraits not in METPO
2. `create_bactotraits_file_versions.py` - Version metadata generation
3. `create_bactotraits_files.py` - File metadata for MongoDB
4. `create_bactotraits_header_mapping.py` - Field name mappings
5. `reconcile_bactotraits_coverage.py` - Coverage analysis vs METPO
6. `reconcile_madin_coverage.py` - Compare with Madin
7. `create_stubs.py` - ROBOT template stubs
8. `import_bactotraits.py` (`metpo/tools/`) - MongoDB import tool

**CLI Commands**:
- `uv run reconcile-bactotraits-coverage`
- `uv run bactotraits-metpo-set-difference`
- `uv run create-bactotraits-field-mappings`

### Reports (2 files)

**Location**: `reports/`
1. `bactotraits-metpo-reconciliation.yaml` - Full coverage analysis
2. `bactotraits-metpo-set-diff.yaml` - Terms not in METPO

### Documentation (3 files)

**Location**: `docs/`
1. `bactotraits_metpo_action_plan.md` - Integration strategy
2. `bactotraits_naming_reference.md` - Field naming conventions
3. `bactotraits_reconciliation_and_pipeline.md` - Workflow documentation

### Metadata

**Location**: `metadata/databases/bactotraits/`
- `bactotraits_field_mappings.json` - 106 field mappings (provider → kg-microbe → MongoDB)
- `bactotraits_files.json` - 2 file versions metadata

### MongoDB

**Database**: `bactotraits`
**Collections**:
- `bactotraits` - 19,455 documents (main data)
- `field_mappings` - 106 documents (field transformations)
- `files` - 2 documents (file metadata)

**Import**: `make import-bactotraits`

### Status: ✅ Complete and Well-Documented

---

## 2. Madin et al. Dataset

### Citation

**Madin, J.S. et al. (2020)**
- Title: "A synthesis of bacterial and archaeal phenotypic trait data"
- Journal: *Scientific Data*, Volume 7, Article 170
- DOI: https://doi.org/10.1038/s41597-020-0497-4
- Repository: https://github.com/bacteria-archaea-traits/bacteria-archaea-traits

### Data Provenance

#### **Primary Source** (KG-Microbe Uses This)
**Location**: `local/madin/madin_etal.csv`
- **Size**: 44 MB
- **Rows**: 172,324 strain-level records
- **Columns**: 35 fields
- **Origin**: Downloaded from Madin GitHub as `condensed_traits_NCBI.csv`
- **Copied from**: `../kg-microbe/data/raw/madin_etal.csv`
- **Taxonomy**: NCBI Taxonomy classification
- **Key fields**: `pathways`, `carbon_substrates` (comma-delimited lists)
- **Used in**: MongoDB `madin` database
- **Status**: ✅ **PRIMARY SOURCE** for imports

#### **Original Strain Data** (Not Used)
**Location**: `local/madin/condensed_traits.csv`
- **Size**: 38 MB
- **Rows**: 151,519 strains
- **Columns**: 34 fields (missing `pathways` and `carbon_substrates`)
- **Source**: Downloaded from Madin GitHub (non-NCBI version or older)
- **Status**: ⚠️ Don't use - missing key fields

#### **Species Aggregations** (Not Used)
**Location**: `local/madin/condensed_species.csv`
- **Size**: 5.8 MB
- **Rows**: 14,756 species
- **Columns**: 78 fields (includes .count, .prop, .stdev aggregations)
- **Purpose**: Species-level statistical summaries
- **Status**: Available for future analysis, not in MongoDB

#### **Unrelated Genomic Dataset** (Not Used)
**Location**: `local/madin/Bacteria_archaea_traits_dataset.csv`
- **Size**: 268 KB
- **Rows**: 1,729 records
- **Columns**: 20 fields (completely different schema)
- **Content**: Genomic statistics (GC content, gene counts, codon usage)
- **Status**: ⚠️ Different dataset, not related to Madin et al. 2020

#### **Decomposition Analysis** (Derived)
**Location**: `local/madin/madin.madin_decomposed_2025-09-29-19-18-EDT.csv`
- **Size**: 18 KB
- **Rows**: 234 pathway term splits
- **Purpose**: Analysis of how pathway strings were parsed/normalized
- **Source**: MongoDB export from metpo analysis
- **Status**: Our own derived analysis

### Data Workflow

```
Madin GitHub: condensed_traits_NCBI.csv
  ↓ download (via kg-microbe)
local/madin/madin_etal.csv (44M, 172,324 rows)
  ↓ make import-madin
MongoDB madin.madin collection (172,324 docs)
  ↓ reconcile-madin-coverage
reports/madin-metpo-reconciliation.yaml
```

### Scripts (2 total)

**Location**: `metpo/bactotraits/`
1. `reconcile_madin_coverage.py` - Coverage analysis vs METPO

**CLI Commands**:
- `uv run reconcile-madin-coverage`

### Reports (1 file)

**Location**: `reports/`
1. `madin-metpo-reconciliation.yaml` - Coverage analysis (70 METPO-Madin synonyms, 62 verified)

### Documentation (2 files)

**Location**: `docs/` and `local/madin/`
1. `docs/madin_field_analysis.md` - Field structure documentation
2. `docs/metpo_madin_pathway_coverage.md` - Pathway term coverage
3. `local/madin/madin_files_analysis.md` - **COMPREHENSIVE** file provenance analysis

### Metadata

**Location**: `metadata/databases/madin/`
- `madin_files.json` - 2 file versions metadata (provider + kg-microbe)

### MongoDB

**Database**: `madin`
**Collections**:
- `madin` - 172,324 documents (main data)
- `files` - 2 documents (file metadata)

**Import**: `make import-madin`

### Key Findings

From `local/madin/madin_files_analysis.md`:
- ✅ `pathways` and `carbon_substrates` fields already exist in Madin GitHub source
- ✅ kg-microbe downloads and renames but doesn't modify the CSV
- ✅ NCBI taxonomy version used (not GTDB)
- ✅ MongoDB exactly matches `madin_etal.csv` (172,324 documents)

### Status: ✅ Complete with Excellent Provenance Documentation

---

## 3. BacDive

### Citation

**Reimer, L.C. et al. (2022)**
- Title: "BacDive in 2022: the knowledge base for standardized bacterial and archaeal data"
- Journal: *Nucleic Acids Research*, Volume 50, Issue D1, Pages D741–D746
- DOI: https://doi.org/10.1093/nar/gkab961
- Website: https://bacdive.dsmz.de/
- API: REST service for large-scale retrieval

### Data Provenance

#### **Raw JSON Data** (in kg-microbe)
**Location**: `../kg-microbe/data/raw/bacdive_strains.json`
- **Size**: 796 MB
- **Format**: JSON (strain-level records from BacDive API)
- **Source**: Downloaded via BacDive REST API
- **Status**: Full BacDive dataset snapshot

#### **Subset for Testing** (in kg-microbe)
**Location**: `../kg-microbe/data/raw/bacdive_strains_subset.json`
- **Size**: 11 MB
- **Purpose**: Smaller subset for development/testing

### Data Workflow (in kg-microbe)

```
BacDive API
  ↓ download via kg-microbe/utils/download_bacdive.py
../kg-microbe/data/raw/bacdive_strains.json (796 MB)
  ↓ transform via kg-microbe/transform_utils/bacdive/
../kg-microbe/data/transformed/bacdive/
  ├── nodes.tsv
  └── edges.tsv
```

### Analysis in METPO (No Import)

**BacDive is NOT imported to MongoDB in metpo repo**. Instead, we have:

#### SPARQL Query (1 file)
**Location**: `sparql/bacdive_oxygen_phenotype_mappings.rq`
- Maps BacDive oxygen tolerance terms to METPO classes
- Generates: `data/generated/bacdive_oxygen_phenotype_mappings.tsv`

#### Documentation (6 files)

**Location**: `docs/`
1. `bacdive_array_structure_summary.md` - Data structure analysis
2. `bacdive_colony_morphology_analysis.md` - Morphology term analysis
3. `bacdive_culture_temp_analysis.md` - Temperature data analysis
4. `bacdive_keywords_analysis.md` - Controlled vocabulary analysis
5. `bacdive_keywords_key_findings.md` - Summary findings
6. `bacdive_oxygen_tolerance_analysis.md` - Oxygen terms analysis
7. `kg_microbe_bacdive_implementation_analysis.md` - KG transformation details

**Additional**:
- `bacdive_keywords_inventory.tsv` - 2,858 controlled vocabulary terms
- `bacdive_structured_path_value_counts.tsv` - Data path statistics

#### OntoGPT Integration

**Location**: `literature_mining/bacdive_chemical_utilization/`
- `bacdive_utilization_template.yaml` - OntoGPT template for chemical utilization
- `bacdive_utilizations.Makefile` - Extraction workflow
- `bacdive_utilizations_template_legacy.yaml` - Legacy template

### Status: ⚠️ Inconsistent

**Issues**:
1. ❌ Raw data only in kg-microbe (796 MB JSON not in metpo)
2. ❌ No MongoDB import (unlike BactoTraits and Madin)
3. ❌ No reconciliation report (unlike BactoTraits and Madin)
4. ✅ Good documentation (6 analysis docs)
5. ✅ SPARQL mapping for oxygen phenotypes
6. ⚠️ OntoGPT templates exist but workflow unclear

**Recommendation**:
- Decide if BacDive should be imported to MongoDB for consistency
- If not, document why (size? licensing? different use case?)
- Consider: Is BacDive analysis happening only in kg-microbe?

---

## Consistency Analysis

### What's Consistent ✅

**BactoTraits and Madin both have:**
1. ✅ Raw CSV files in `local/` directory
2. ✅ MongoDB databases with documented collections
3. ✅ Makefile import targets (`make import-bactotraits`, `make import-madin`)
4. ✅ Reconciliation scripts comparing coverage with METPO
5. ✅ YAML reports showing coverage statistics
6. ✅ Metadata JSON files in `metadata/databases/`
7. ✅ Multiple documentation files
8. ✅ Citations with DOI links

### What's Inconsistent ⚠️

**BacDive differs:**
1. ❌ No local raw data (only in kg-microbe: 796 MB JSON)
2. ❌ No MongoDB import workflow
3. ❌ No reconciliation report
4. ❌ Only 1 SPARQL query (oxygen phenotypes)
5. ❌ No `metadata/databases/bacdive/` directory
6. ✅ BUT: Excellent documentation (6 analysis docs)
7. ✅ BUT: Has citation info

### Gaps in Provenance Documentation

1. ✅ **Citations exist** in `docs/microbial_trait_datasets_background.md`
2. ✅ **Download URLs documented** for Madin (in `madin_files_analysis.md`)
3. ⚠️ **BactoTraits download process not documented** (assume manual from GitHub)
4. ⚠️ **BacDive API access not documented in metpo** (only in kg-microbe)
5. ❓ **License information missing** for all three sources

---

## Recommendations

### 1. Create Unified Provenance Document

Create `docs/DATA_SOURCES_PROVENANCE.md` with:
- **Citations**: Full bibliographic info + DOIs
- **Licenses**: License terms for each dataset
- **Download URLs**: Exact links to source data
- **Download dates**: When data was acquired
- **Versions**: Dataset version numbers
- **Acknowledgments**: Required attributions

### 2. Decide on BacDive Strategy

**Option A**: Import BacDive to MongoDB
- Copy 796 MB JSON to `local/bacdive/`
- Create MongoDB import workflow
- Generate reconciliation report
- Add metadata to `metadata/databases/bacdive/`

**Option B**: Document BacDive as "kg-microbe only"
- Explain why it's not in metpo MongoDB
- Document the analysis workflow in kg-microbe
- Keep SPARQL mappings as interface point

### 3. Complete Documentation

For each data source, document:
- [ ] Download date and version
- [ ] Original file checksums (MD5/SHA256)
- [ ] License and usage restrictions
- [ ] Required acknowledgments
- [ ] Update frequency (how often to refresh)

### 4. Add License Files

Create `local/*/LICENSE.txt` for each data source with:
- License text
- Required citations
- Usage restrictions
- Distribution terms

---

## File Inventory Summary

### BactoTraits Files (14 locations)
- Raw: 2 files (8.6M + 6.1M)
- Scripts: 8 Python files
- Reports: 2 YAML files
- Docs: 3 markdown files
- Metadata: 2 JSON files
- MongoDB: 3 collections

### Madin Files (15 locations)
- Raw: 5 CSV files (44M primary + 4 others)
- Scripts: 2 Python files
- Reports: 1 YAML file
- Docs: 3 markdown files
- Metadata: 1 JSON file
- MongoDB: 2 collections

### BacDive Files (15 locations in metpo, more in kg-microbe)
- Raw: 0 in metpo (796M in kg-microbe)
- Scripts: 1 SPARQL query
- Reports: 0
- Docs: 6 markdown files + 2 TSV inventories
- Metadata: 0
- MongoDB: 0 collections
- OntoGPT: 3 files (2 templates + 1 Makefile)

---

## Next Steps

1. ✅ This document created (comprehensive inventory)
2. ⏳ Create `DATA_SOURCES_PROVENANCE.md` with citations/licenses
3. ⏳ Decide BacDive import strategy
4. ⏳ Add license files to `local/*/`
5. ⏳ Document download procedures
6. ⏳ Add version tracking for datasets

---

## Related Documentation

- `local/madin/madin_files_analysis.md` - **Best example** of provenance documentation
- `docs/microbial_trait_datasets_background.md` - Citations and background
- `docs/data_sources_formats_and_reconciliation.md` - Format details
- `local/mongodb_dumps/README.md` - Database backup documentation
- `metadata/databases/README.md` - Metadata collections overview
