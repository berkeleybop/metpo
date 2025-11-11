# N4L GraphDB Workflow Archive

**Last Updated:** 2025-11-11

## Overview

This directory contains the complete GraphDB-based workflow for loading and analyzing Names for Life (N4L) phenotypic data alongside KG-Microbe and METPO. This work was conducted in 2025 and documented in GitHub issues #87, #90, #91, #101-104, and #110 (all closed October 2025).

## Files

### `graphdb.Makefile`
Main automation workflow for the N4L/GraphDB pipeline.

**Key targets:**
- `create-repo` - Creates GraphDB repository from TTL config
- `load-nquads` - Loads N4L data from `local/n4l-tables.nq`
- `load-metpo` - Loads METPO ontology into named graph
- `load-taxon-ranks` - Loads NCBI taxon rank data
- `delete_most_0_value_triples` - Cleans zero-value data
- `direct_ncbitaxid_same_as` - Creates owl:sameAs links to NCBI Taxonomy
- `property_hierarchy` - Establishes property relationships
- `shared_nm_id_same_as` - Links entities by shared N4L IDs
- `load-temperatures-parsed` - Loads parsed temperature data
- `n4l-clean` - Cleanup and repository deletion

### `metpo_n4l_etc_automated.ttl`
GraphDB repository configuration:
- Repository ID: `metpo_n4l_etc_automated`
- Ruleset: `rdfsplus-optimized` (RDFS reasoning with optimizations)
- SameAs reasoning: Enabled
- Context indexing: Enabled (for named graph queries)

## SPARQL Files

### SPARQL Updates (`.ru`)

**`delete_most_0_value_triples.ru`**
Removes N4L triples with zero/null values to reduce noise.

**`direct_ncbitaxid_same_as.ru`**
Creates `owl:sameAs` assertions between N4L organism entities and NCBI Taxonomy IRIs, enabling cross-reference between N4L and KG-Microbe.

**`property_hierarchy.ru`**
Establishes rdfs:subPropertyOf relationships for N4L predicates.

**`shared_nm_id_same_as.ru`**
Links N4L entities that share the same `nm.` identifier (N4L internal IDs).

### SPARQL Queries (`.rq`)

**`temperature_query.rq`**
Extracts temperature-related triples from N4L data for parsing and categorization.

**`flatten_n4l_parsing_components.rq`**
Flattens parsed environmental condition data (ParseGroup/ParseComponent pattern) into tabular format for analysis.

**`metpo_classes_temperature_limits.rq`**
Extracts temperature range limits from METPO ontology classes for comparison with parsed N4L data.

## Workflow Overview

1. **Data Preparation**
   - Convert N4L spreadsheets to RDF N-Quads (via Jupyter notebooks)
   - Extract NCBI taxon rank data

2. **Repository Setup**
   - Create GraphDB repository with config
   - Load N4L N-Quads into named graphs
   - Load METPO ontology
   - Load taxon ranks

3. **Data Enrichment**
   - Run SPARQL updates to:
     - Clean zero-value triples
     - Create owl:sameAs links (NCBI Taxonomy, shared IDs)
     - Establish property hierarchies

4. **Temperature Processing**
   - Extract temperature data via SPARQL query
   - Parse free-text temperature descriptions (LLM/rules)
   - Categorize into METPO classes (psychrophile, mesophile, etc.)
   - Load parsed data back into GraphDB
   - Generate flattened reports

5. **Analysis & Export**
   - Run analytical queries
   - Export results to CSV/TSV
   - Generate reconciliation reports

## Data Model

**Named Graphs:**
- N4L type assertions: `<http://example.com/n4l/type_assertions>`
- N4L aboutness links: `<http://example.com/n4l/protolog_aboutness>`
- Protolog normalization: Multiple sheets (1000_proto_proj, Sheet2, Sheet3, etc.)
- Parsed temperatures: `<http://example.com/n4l_temperatures_parsed>`
- METPO ontology: `<https://w3id.org/metpo/metpo/releases/2025-04-25/metpo.owl>`
- Taxon ranks: `<http://purl.obolibrary.org/obo/ncbitaxon#has_rank>`

**Key Relationships:**
- Reference → is_about → Protolog → is_about → OrganismName
- OrganismName → owl:sameAs → NCBITaxon IRI
- Entities → owl:sameAs (via shared nm.IDs)

## Status

This workflow is **archived but incomplete**. The N4L data showed potential but required extensive additional processing. More importantly, the N4L dataset did not appear to provide information about significantly more taxa than are already covered by our three primary semistructured data sources: **BactoTraits**, **Madin et al.**, and **BacDive**.

The GraphDB exploration work was discontinued (October 2025), and insights from the investigation are documented in:
- `docs/n4l/` - Comprehensive reports and findings
- `data/n4l/` - Reconciliation data and exports
- `sparql/exploration/` - Additional exploratory queries

This archive is preserved for:
1. Reference documentation of the N4L exploration methodology
2. Understanding what was attempted and why it was discontinued
3. Reusing the GraphDB/SPARQL workflow patterns for other data sources
4. Historical context for the N4L→METPO→KG-Microbe integration investigation

## Related Documentation

- **Workflow documentation:** `docs/n4l/N4L_Data_Transformation_Workflow.md`
- **Consolidated report:** `docs/n4l/n4l-consolidated-report.md`
- **Follow-up session:** `docs/n4l/n4l-session-followup-report.md`
- **Environmental parse pattern:** `docs/ontology/patterns/environmental_parse_model_v0.3.md`
- **Reconciliation data:** `data/n4l/n4l_ref_protolog_orgname_vs_kgmicrobe.csv`

## Missing Dependencies (Not Restored)

⚠️ **This Makefile expects files and notebooks that are no longer in the repository.**

### Required Input Files (Not Included)

**Generated by Jupyter notebooks (deleted June 2025):**
- `local/n4l-tables.nq` - N4L data converted to RDF N-Quads
  - Generated by: `metpo/n4l_tables_to_quads.ipynb` (deleted)
  - Source: N4L Excel/CSV files from `assets/N4L_phenotypic_ontology_2016/` (cleaned up)
  - Used config: `assets/n4l-xlsx-parsing-config.tsv` (deleted)
  - Used mapping: `assets/n4l_predicate_mapping_normalization.csv` (deleted)

- `local/noderanks.ttl` - NCBI taxon rank data
  - Generated by: Unknown notebook or script
  - Source: NCBI Taxonomy database

- `local/n4l-temperature.ttl` - Parsed temperature data
  - Generated by: `metpo/classify_temperature_values.ipynb` (deleted)
  - Input: `local/n4l-temperature.csv` (generated by SPARQL query)

### Notebooks (Deleted)

The following Jupyter notebooks performed the data transformations but were removed during cleanup:

1. **`metpo/n4l_tables_to_quads.ipynb`**
   - Converted N4L Excel/CSV spreadsheets to RDF N-Quads
   - Output: `local/n4l-tables.nq`
   - Normalized predicates using mapping file
   - Created named graphs for different N4L data sources

2. **`metpo/classify_temperature_values.ipynb`**
   - Parsed free-text temperature descriptions using LLM/rules
   - Applied ParseGroup/ParseComponent pattern
   - Output: `local/n4l-temperature.ttl`

3. **`metpo/categorize_temperature_ranges.ipynb`**
   - Mapped parsed temperature ranges to METPO classes
   - Classified organisms as psychrophile/mesophile/thermophile
   - Output: `local/categorized_temperature_*.tsv`

### Why These Are Missing

All N4L source data, configuration files, and processing notebooks were deleted in the **June 2025 "major cleanup"** (commits `2c26e14`, `12adfe9`) to reduce repository bloat. The exploration was discontinued when it became apparent that N4L would not provide substantially more taxon coverage than our existing primary data sources (BactoTraits, Madin et al., and BacDive), and the level of data processing required was not justified by the potential gains. Key findings and reconciliation data were preserved in:

- Documentation: `docs/n4l/*.md`
- Reconciliation data: `data/n4l/*.csv`
- This workflow archive: `config/graphdb/`

### To Reconstruct This Workflow

If you need to rerun this pipeline:

1. **Obtain N4L source data** from Google Drive or Charles Parker
2. **Extract NCBI taxon ranks** from NCBI Taxonomy database
3. **Recreate conversion notebooks** using the documentation in:
   - `docs/n4l/N4L_Data_Transformation_Workflow.md`
   - `docs/ontology/patterns/environmental_parse_model_v0.3.md`
4. **Run the Makefile targets** in sequence as documented above

The SPARQL files and Makefile provide the operational knowledge, but the data transformation layer needs to be rebuilt.

## Requirements

- OntoText GraphDB (tested with localhost:7200)
- curl with JSON/RDF support
- jq for JSON parsing
- Jupyter (for N4L→N-Quads conversion notebooks)
- Python with OntoGPT/LLM support (for temperature parsing)
