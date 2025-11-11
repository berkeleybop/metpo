# N4L (Names for Life) Integration Archive

**Last Updated:** 2025-11-11
**Status:** Archived (discontinued October 2025)

---

## Overview

This directory contains the complete documentation, code, and workflow artifacts from the Names for Life (N4L) phenotypic data integration exploration conducted in 2025. The work aimed to harmonize N4L protolog data with KG-Microbe and METPO, but was discontinued when analysis showed N4L would not provide substantially more taxon coverage than our three primary semistructured data sources: **BactoTraits**, **Madin et al.**, and **BacDive**.

---

## Directory Structure

```
docs/n4l/
├── README.md                           # This file
├── n4l-consolidated-report.md          # Complete analysis report (June 2025)
├── n4l-session-followup-report.md      # Follow-up session findings
├── N4L_Data_Transformation_Workflow.md # High-level workflow description
├── KG-Microbe_iri_patterns.md          # KG-Microbe IRI analysis
│
├── config/                             # Configuration files for transformation
│   ├── n4l-xlsx-parsing-config.tsv            # Excel parsing specifications
│   └── n4l_predicate_mapping_normalization.csv # RDF predicate normalization
│
├── transformation_code/                # Code that transforms N4L → RDF
│   ├── n4l_tables_to_quads.ipynb              # Main transformation: Excel → N-Quads
│   ├── classify_temperature_values.ipynb       # LLM-based temperature parsing
│   ├── categorize_temperature_ranges.ipynb     # Map temps to METPO classes
│   ├── regex_parse_n4l_temperatures.py         # Regex-based parser (pre-LLM)
│   └── temperature_pattern_library.ipynb       # Comprehensive regex patterns
│
└── graphdb_workflow/                   # OntoText GraphDB loading/analysis
    ├── README.md                       # Complete GraphDB workflow documentation
    ├── graphdb.Makefile                # Automation for GraphDB operations
    ├── repository_config.ttl           # GraphDB repository configuration
    └── sparql/                         # SPARQL queries and updates
        ├── temperature_query.rq
        ├── flatten_n4l_parsing_components.rq
        ├── metpo_classes_temperature_limits.rq
        ├── delete_most_0_value_triples.ru
        ├── direct_ncbitaxid_same_as.ru
        ├── property_hierarchy.ru
        └── shared_nm_id_same_as.ru
```

---

## Key Findings

### N4L Data Scope

- **Type Assertions:** 59,770 total (23,533 References, 2,247 Protologs, 33,990 OrganismNames)
- **Aboutness Links:** 4,279 total (Reference→Protolog→OrganismName chains)
- **Source:** Charles Parker's N4L phenotypic ontology dataset (2016)

### Why Integration Was Discontinued

The exploration was discontinued when it became apparent that **N4L would not provide substantially more taxon coverage than our existing primary data sources** (BactoTraits, Madin et al., and BacDive). The level of data processing required was not justified by the potential gains.

Key evidence:
- Reconciliation analysis in `../../data/n4l/n4l_ref_protolog_orgname_vs_kgmicrobe.csv` (3.8 MB)
- Significant overlap with existing sources
- Extensive data cleaning and normalization required

---

## Configuration Files (`config/`)

### `n4l-xlsx-parsing-config.tsv`

Specifies how to parse each N4L Excel/CSV file:
- Which sheets to process
- ID column names
- Whether transposition is needed
- Whether data is already in subject-predicate-object format

**Example row:**
```tsv
filename                                    sheet_name  id_column   skip   requires_transposition
article_download_status_20161222.xlsx      all_protologs  UID      False  False
```

**Usage:** Referenced by `transformation_code/n4l_tables_to_quads.ipynb`

### `n4l_predicate_mapping_normalization.csv`

Maps original N4L predicates to normalized RDF predicates:
```csv
original_predicate,normalized_predicate
http://example.com/n4l/NCBI_TaxID,http://example.com/n4l/ncbi_tax_id
http://example.com/n4l/sortOrder,http://example.com/n4l/sort_order
```

**Purpose:** Standardizes predicate names for consistent RDF generation

**Usage:** Referenced by `transformation_code/n4l_tables_to_quads.ipynb`

---

## Transformation Code (`transformation_code/`)

### Core Transformation

**`n4l_tables_to_quads.ipynb`** (21 KB, 596 lines)
- **Purpose:** Converts N4L Excel/CSV spreadsheets to RDF N-Quads format
- **Input:** `assets/N4L_phenotypic_ontology_2016/` (deleted June 2025)
- **Config:** Uses both config files above
- **Output:** `local/n4l-tables.nq` (used by GraphDB workflow)
- **Key features:**
  - Handles multiple Excel sheets per file
  - Creates named graphs for data provenance
  - Normalizes predicates using mapping file
  - Preserves original column structure

### Temperature Processing Pipeline

**`classify_temperature_values.ipynb`** (64 KB)
- **Purpose:** Parses free-text temperature descriptions using LLM/rules
- **Input:** Temperature triples from GraphDB (via SPARQL query)
- **Output:** Structured RDF with ParseGroup/ParseComponent pattern
- **Model:** Environmental Condition Parse Model v0.3 (see `../ontology/patterns/`)
- **Example transformation:**
  ```
  "25-30°C, optimum 28°C" →
  ParseGroup [
    ParseComponent { min: 25, max: 30, unit: Cel }
    ParseComponent { spot: 28, qualifier: optimum, unit: Cel }
  ]
  ```

**`categorize_temperature_ranges.ipynb`** (38 KB)
- **Purpose:** Maps numerical temperature ranges to METPO phenotype classes
- **Input:** Parsed temperature data (from classify_temperature_values)
- **Output:** Categorized as psychrophile, mesophile, thermophile, etc.
- **Logic:** Compares parsed ranges against METPO class boundaries

### Earlier Approaches (Pre-LLM)

**`regex_parse_n4l_temperatures.py`** (6.4 KB)
- **Purpose:** Regex-based temperature parser (before LLM approach)
- **Features:**
  - Handles ranges: "25-30°C", "25 to 30°C"
  - Handles lists: "25, 30, 35°C"
  - Handles qualifiers: "above 30°C", "up to 40°C"
  - Handles phenotypic labels: "mesophilic", "thermophilic"
- **Limitation:** Less flexible than LLM approach, requires exhaustive patterns

**`temperature_pattern_library.ipynb`** (12 KB)
- **Purpose:** Comprehensive regex pattern library for temperature strings
- **Contents:** 50+ regex patterns covering different formats found in N4L
- **Usage:** Reference for building parsers, understanding data variety
- **Examples:**
  - Mixed discrete values: `25, 30, 35-40°C`
  - Comma-separated ranges: `25-30°C, 40-50°C`
  - Prefix modifiers: `above 30°C`, `optimum 28°C`
  - Phenotypic labels: `mesophilic`, `thermotolerant`

---

## GraphDB Workflow (`graphdb_workflow/`)

See **`graphdb_workflow/README.md`** for complete documentation.

### Quick Overview

1. **Setup:** Create GraphDB repository with `repository_config.ttl`
2. **Load:** Import N-Quads generated by transformation notebooks
3. **Enrich:** Run SPARQL updates to:
   - Clean zero-value triples
   - Create `owl:sameAs` links (NCBI Taxonomy, shared IDs)
   - Establish property hierarchies
4. **Analyze:** Extract temperature data, parse, categorize, reload
5. **Export:** Generate reports and reconciliation data

**Makefile targets:**
```bash
make -f graphdb.Makefile create-repo          # Create GraphDB repository
make -f graphdb.Makefile load-nquads          # Load N-Quads
make -f graphdb.Makefile delete_most_0_value_triples
make -f graphdb.Makefile direct_ncbitaxid_same_as
```

---

## Related Documentation

- **Reports:** `n4l-consolidated-report.md`, `n4l-session-followup-report.md`
- **Workflow:** `N4L_Data_Transformation_Workflow.md`
- **Data model:** `../ontology/patterns/environmental_parse_model_v0.3.md`
- **Reconciliation data:** `../../data/n4l/n4l_ref_protolog_orgname_vs_kgmicrobe.csv`
- **Source inventory:** `../../data/n4l/N4L_phenotypic_ontology_2016-*.file_listing.txt`
- **KG-Microbe analysis:** `KG-Microbe_iri_patterns.md`

---

## Related GitHub Issues (All Closed October 2025)

- #42 - Add Charlie Parker's Names for Life phenotypic ontology
- #68 - Dump the DrugResponseProperty statements from N4L
- #87 - Make a table of properties about organisms
- #90 - Load KG-microbe and compare its volume of knowledge to N4L
- #91 - Summarize the initial comparison between N4L and KG-Microbe in Slack
- #101 - Document clearing of KG-Microbe graph, dumping and restoring
- #102 - Make a table of parsed N4L temperature statements
- #103 - Compare the categorical temperature vocabularies in METPO, N4L and KG-Microbe
- #104 - Identify shared technologies for METPO, N4L, KG-Microbe
- #110 - Load kg-microbe into a GraphDB repository; plan for alignment with METPO

---

## Missing Dependencies

⚠️ **The transformation code expects files that are no longer in the repository.**

### N4L Source Data (Deleted June 2025)

- `assets/N4L_phenotypic_ontology_2016/` - Google Drive download (571.7 MB)
- Source: Charles Parker's phenotypic ontology project
- File listing preserved: `../../data/n4l/*.file_listing.txt`

### Generated Intermediate Files (Not Version Controlled)

- `local/n4l-tables.nq` - RDF N-Quads (generated by `n4l_tables_to_quads.ipynb`)
- `local/noderanks.ttl` - NCBI taxon rank data
- `local/n4l-temperature.ttl` - Parsed temperature data

### To Reconstruct This Workflow

1. **Obtain N4L source data** from Google Drive or Charles Parker
2. **Run transformation notebook:** `n4l_tables_to_quads.ipynb`
3. **Setup GraphDB:** Follow `graphdb_workflow/README.md`
4. **Run temperature pipeline:** See workflow documentation

---

## Lessons Learned

### Methodology Insights

1. **LLM-based parsing** more flexible than regex for free-text extraction
2. **ParseGroup/ParseComponent pattern** effective for structured environmental data
3. **Named graphs** essential for data provenance in large integrations
4. **SPARQL updates** powerful for incremental data enrichment

### Integration Challenges

1. **Data cleaning overhead** significant for legacy phenotypic datasets
2. **Taxon coverage overlap** with existing sources (BactoTraits/Madin/BacDive)
3. **Predicate normalization** requires careful mapping for consistency
4. **Zero-value noise** common in spreadsheet-derived RDF

### Decision to Discontinue

- Focus shifted to three primary data sources with better coverage
- N4L required extensive processing for limited marginal value
- Methodology documentation preserved for potential future application

---

## Reusing This Methodology

While N4L integration was discontinued, the transformation approach may be valuable for:

1. **Other phenotypic data sources** with similar structure
2. **Environmental condition parsing** from literature
3. **GraphDB-based data integration** workflows
4. **ParseGroup/ParseComponent pattern** for any environmental data

All code and configuration is preserved for reference and adaptation.

---

**Archive Status:** Complete and documented
**Primary Data Sources:** BactoTraits, Madin et al., BacDive
**Contact:** See main project README for contributors
