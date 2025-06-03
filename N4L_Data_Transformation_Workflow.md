# N4L Data Transformation Workflow

## Overview

This document summarizes the workflow for transforming Names for Life (N4L) phenotypic data into structured RDF that integrates with the Microbial Ecophysiological Trait and Phenotype Ontology (METPO).

## Workflow Steps

1. **Data Source**: Names for Life (N4L) phenotypic data in various formats (CSV, TSV, XLSX) containing microbial trait information.

2. **Initial Transformation**: 
   - `n4l_tables_to_quads.ipynb` converts N4L spreadsheets to RDF N-Quads format
   - Data is stored in named graphs with context (provenance)
   - Predicates are normalized using mapping files

3. **GraphDB Integration**:
   - N-Quads are loaded into GraphDB repository
   - SPARQL updates establish relationships:
     - Delete zero-value triples
     - Create owl:sameAs connections between taxonomic IDs
     - Build property hierarchies
     - Link shared identifiers

4. **Environmental Parameter Parsing**:
   - Specialized extraction of structured data from free-text descriptions
   - Follows the Environmental Condition Parse Model (v0.3)
   - Creates ParseGroup and ParseComponent structures for each trait
   - Parameters include temperature, salinity, pH, oxygen requirements

5. **Temperature Processing Pipeline**:
   - SPARQL queries extract temperature-related triples
   - `classify_temperature_values.ipynb` parses free-text temperature descriptions
   - Creates structured RDF with numerical ranges and qualifiers
   - Results stored in named graph

6. **Categorical Classification**:
   - `categorize_temperature_ranges.ipynb` assigns temperature categories
   - Maps numerical values to classes like psychrophilic, mesophilic, thermophilic
   - Links to METPO ontology class hierarchy

7. **Salinity Processing**:
   - Similar to temperature but with specialized rules
   - `parse_salinity_llm.py` and Jupyter notebooks use LLM-powered parsing
   - Extract concentration values, ranges, units, qualifiers
   - Recognize chemical entities (NaCl, sea water)
   - Creates structured RDF output

8. **METPO Ontology Integration**:
   - Parsed data links to formal METPO ontology classes
   - Enables semantic reasoning over numerical ranges
   - Provides standardized vocabulary for microbial traits
   - Supports downstream text mining applications

9. **Quality Control and Validation**:
   - SPARQL queries verify parsing results
   - LLM validation of parsing accuracy
   - Temperature ranges mapped to formal ontology classes

## Automation

The entire workflow is automated through Makefiles, with two primary drivers:

1. **Main Makefile**: Orchestrates the overall process, including:
   - Downloading and extracting NCBI taxonomy data
   - Running Jupyter notebooks for data conversion and parsing
   - Calling the GraphDB-specific targets

2. **GraphDB Makefile**: Manages GraphDB-specific operations:
   - Repository creation and configuration
   - Data loading and SPARQL updates
   - Result extraction and reporting

The `n4l-pipeline` target combines all steps into a single end-to-end process.

## Key Components

- **Jupyter Notebooks**: Primary tools for data transformation and analysis
- **SPARQL Queries**: Extract and transform data within GraphDB
- **LLM-Assisted Parsing**: Advanced text parsing, especially for salinity data
- **Environmental Parse Model**: Structural pattern for normalizing conditions
- **METPO Ontology**: Provides formal semantic structure for parsed data

This workflow transforms unstructured N4L text data into structured, semantically enriched RDF that can integrate with the METPO ontology and ultimately feed into knowledge graphs like KG-Microbe.