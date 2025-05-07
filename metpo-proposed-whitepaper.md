# METPO: Microbial Ecophysiological Traits and Phenotype Ontology

## Internal Whitepaper

**Author:** Mark A. Miller  
**Date:** May 2, 2025

## Executive Summary

The Microbial Ecophysiological Traits and Phenotype Ontology (METPO) is an evolving knowledge representation framework
designed to standardize and formalize microbial phenotypic and trait information. This document outlines the purpose,
history, challenges, and current development state of METPO, with specific focus on integration efforts with Names for
Life (N4L) data and alignment with existing ontologies. METPO aims to support named entity extraction from scientific
literature and enhance knowledge graph construction for microbial data.

## 1. Introduction and Background

### 1.1 Origin and Purpose

METPO originated as a ROBOT template from the work of Marcin Joachimiak at Berkeley BOP. The primary motivations for
developing METPO include:

- Creating a standardized framework for describing microbial phenotypes and ecophysiological traits
- Supporting named entity extraction from scientific literature, particularly from journals like the International
  Journal of Systematic and Evolutionary Microbiology
- Enhancing the knowledge graph for microbial data (KG-microbe) by adding semantic relationships
- Providing a controlled vocabulary that can bridge existing ontological resources while addressing the specific needs
  of microbial trait data

The ontology is currently maintained in the [Berkeley BOP GitHub repository](https://github.com/berkeleybop/metpo), with
all IRIs within the https://w3id.org/metpo/ namespace.

### 1.2 Relationship to Other Resources

METPO's development is influenced by several existing resources:

- **Knowledge frameworks**: METPO aims to add edges to [KG-microbe](https://github.com/Knowledge-Graph-Hub/kg-microbe)
- **Databases**: BacDive and MediaDive from DSMZ have strongly influenced the design
- **Grounding ontologies**: Currently leverages ChEBI, GO, UniProt, and NCBITaxon
- **Alignment potential**: Efforts have been made to explore alignment with:
    - DSMZ Digital Diversity Ontology (D3O)
    - Microbial Conditions Ontology (MCO)
    - Ontology of Host-Microbiome Interactions (OHMI)
    - Ontology of Microbial Phenotypes (OMP)
    - Phenotype And Trait Ontology (PATO)
    - Fission Yeast Phenotype Ontology (FYPO)

## 2. Current Development Status

### 2.1 Ontological Structure

The current METPO structure has been developed through multiple approaches:

- **Alignment attempts** with existing ontologies listed above
- **LLM-driven expansion** which has successfully:
    - Provided consistent hierarchical structure
    - Generated multiple synonyms in different word forms for many classes
    - Improved term coverage

However, several structural challenges remain:

- Some classes (e.g., "pan-genome") fall outside the scope of microbial phenotypes and should be removed
- The property hierarchy remains underdeveloped
- Some BFO-inspired class names (e.g., "material entity," "process," "quality") exist but without formal alignment to
  BFO

### 2.2 Names for Life (N4L) Integration

A significant recent development is access to the Names for Life (N4L) ontology and data files from Charles Parker. This
integration presents both opportunities and challenges:

- **Data structure**: N4L data comes in various formats (CSV, TSV, XLSX) covering:
    - Literature references
    - Media and ingredients
    - Microbial trait data indexed by "named ids" (nm. prefix)

- **Current progress**:
    - N4L sheets have been converted to triples in named graphs
    - owl:sameAs statements establish paths from NCBI Taxonomy identifiers to phenotype text
    - Initial efforts to parse complex text entries (particularly salinity preferences) are underway but challenging

## 3. Technical Challenges

### 3.1 Ontology Development Challenges

Several significant challenges face METPO's continued development:

1. **Scope definition**: Determining clear boundaries for included concepts
2. **Alignment strategy**: Deciding whether to:
    - Create new terms in the METPO namespace
    - Reuse terms and IRIs from existing ontologies
    - Create formal mappings between METPO terms and external ontologies

3. **Hierarchy completeness**: Ensuring sufficient coverage while maintaining manageable size
4. **OBO Foundry principles**: Working toward compliance
   with [OBO Foundry principles](https://obofoundry.org/principles/fp-000-summary.html)

### 3.2 N4L Data Integration Challenges

The integration of N4L data presents specific technical hurdles:

1. **Complex text parsing**: N4L contains rich descriptive text that requires sophisticated parsing
2. **Taxonomic granularity**: Statements currently associated with species may need mapping to specific strains
3. **Resource allocation**: Determining appropriate person-hour or LLM cost justification for parsing efforts

## 4. Current Focus: Salinity Data Parsing

A current priority is parsing salinity preference data from N4L. This effort exemplifies the challenges and approaches
being used in METPO development.

### 4.1 Parsing Requirements

The salinity parsing task requires extraction of structured data from complex text descriptions, including:

- **Value and range parsing**: Handling individual values, explicit ranges, and relational expressions
- **Unit normalization**: Standardizing various concentration units (%, g/L, mol/L, M, mM)
- **Qualifier extraction**: Identifying measurement qualifiers like (w/v), wt/vol
- **Growth pattern recognition**: Categorizing descriptions (weak, poor, enhances growth)
- **Chemical entity identification**: Recognizing salts and other relevant compounds

### 4.2 Methodological Approaches

Recent work has focused on:

- Leveraging LLMs (Claude/GPT-4) for complex text parsing
- Developing comprehensive parsing rules and expectations
- Exploring integration with tools like PydanticAI and Aurelian
- Attempting to apply lessons from ESS-Dive variable normalization

### 4.3 Technical Limitations

Current technical challenges include:

- LLM token limitations for large datasets
- Tool compatibility issues (e.g., Cborg Chat file loading)
- The need for specialized parsing approaches that differ from previous normalization tasks

## 5. Future Directions

### 5.1 Short-term Priorities

1. Refine salinity parsing capabilities based on established guidance
2. Evaluate cost-benefit of further N4L data parsing efforts
3. Remove out-of-scope classes
4. Improve property hierarchy

### 5.2 Medium-term Goals

1. Formalize alignment strategy with existing ontologies
2. Move more classes into appropriate hierarchies (or remove if not possible)
3. Complete integration of parsed N4L data into KG-microbe

### 5.3 Decision Points

Several key decisions will shape METPO's future:

1. **Degree of integration**: How deeply to integrate with N4L data
2. **Alignment strategy**: Whether to prioritize alignment with existing ontologies or focus on METPO's unique
   contributions
3. **Resource allocation**: Balancing manual curation, LLM assistance, and automated processing

## 6. Conclusions

METPO represents an important effort to standardize microbial trait and phenotype descriptions. Its development balances
several competing priorities:

- Creating a useful resource for named entity extraction
- Enhancing knowledge graph construction
- Maintaining compatibility with existing ontologies
- Efficiently leveraging available data sources like N4L

The current salinity parsing work serves as a test case for the broader challenges of integrating rich textual
descriptions into formal ontological structures. Success in this area will inform approaches to other microbial trait
categories and ultimately determine METPO's utility for knowledge extraction and representation.

## Appendix A: Salinity Parsing Guidelines

### A.1 Value and Range Parsing

- Parse individual values: `2%`, `3.0 M`, `30 g/L`, `0.5 mM`
- Parse explicit ranges: `3.0–3.5 M`, `20-80 gNaCl l-1`, `5 to 700 mM`
- Interpret relational expressions: `up to 4%`, `more than 6%`, `less than 2%`

### A.2 Value List Splitting

- Split multi-valued entries into separate rows
- Handle complex entries like `2, 4, 6, 8% (wt/vol), 10% (weak), 12% (weak)`

### A.3 Unit Normalization

- Standardize units: `%`, `g/L`, `mol/L`, `M`, `mM`, `mg/L`
- Handle malformed variants: `g 1^-l` → `g/L`, `mol/i` → `mol/L`

### A.4 Qualifier Extraction

- Extract and normalize qualifiers: `(w/v)`, `wt/vol`, `vol/vol`, `v/w`
- Exclude tokens like `most`, `all`, `near`, `range` from qualifiers

### A.5 Chemical Entity Recognition

- Identify specific chemicals: `NaCl`, `ASW`, `artificial sea salt`
- Create separate rows for different chemicals
- Canonicalize variations (e.g., `ASW` and `artificial sea water`)

### A.6 Output Structure

- growth_response
- concentration_value, concentration_range_min, concentration_range_max
- concentration_unit, concentration_qualifier
- chemical_entities
- growth_pattern, categorical_description, taxon_constraints
- unparsed_text (optional, no duplication)

## Appendix B: Key Resources

- [METPO GitHub Repository](https://github.com/berkeleybop/metpo)
- [ROBOT Template Documentation](https://robot.obolibrary.org/template.html)
- [KG-microbe Repository](https://github.com/Knowledge-Graph-Hub/kg-microbe)
- [OBO Foundry Principles](https://obofoundry.org/principles/fp-000-summary.html)
