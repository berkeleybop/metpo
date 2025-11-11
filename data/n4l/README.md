# N4L (Names for Life) Data Files

**Last Updated:** 2025-11-11

## Overview

This directory contains data files created during the Names for Life (N4L) phenotypic ontology integration work.

## Files

### `protolog_normalization_categories_with_1000_DB.csv` (407 KB)
User-created CSV export of protolog normalization categories from the N4L database processing work.

### `n4l_ref_protolog_orgname_vs_kgmicrobe.csv` (3.8 MB, 56,922 rows)
Reconciliation mapping between N4L and KG-Microbe organism references:
- Links N4L Reference IDs to Protolog statements to OrganismNames
- Maps to NCBI Taxonomy IDs for cross-reference with KG-Microbe
- Includes statement counts for phenotypic richness assessment
- Created during the N4L/KG-Microbe harmonization work (June 2025)

**Columns:**
- Reference metadata (year, PubMed IDs, DOIs)
- Organism properties (names, NCBI taxon IDs, taxonomic ranks)
- Protolog phenotype statement counts

This file provides a crude but valuable accounting of:
1. How N4L and KG-Microbe refer to organisms differently
2. The number of organisms represented in each resource
3. The overlap and gaps between the two knowledge bases

### `kg-microbe-types-biolink-relations.csv` (1.6 MB)
Analysis of Biolink relation patterns in KG-Microbe:
- Documents the flat categorization of named instances in KG-Microbe
- Contrasts with OBO Foundry-style hierarchical classification
- Shows subject category, predicate, object category, and counts
- Generated from `sparql/exploration/kg-microbe/kg-microbe-types-bioloink-relations.rq`

This file is valuable for understanding:
1. How KG-Microbe uses Biolink categories vs. ontological hierarchies
2. Patterns of association predicates between entity types
3. The structure of KG-Microbe's knowledge representation model

### `N4L_phenotypic_ontology_2016-20250408T190826Z-002.file_listing.txt` (1.9 MB)
Complete file inventory from the original N4L phenotypic ontology Google Drive download (April 2025).

Used to verify which files were user-created vs. originally downloaded during the repository cleanup (November 2025).

## Source

These files are derived from the Names for Life (N4L) phenotypic ontology data provided by Charles Parker.

## Related Documentation

See `docs/n4l/` for comprehensive documentation of the N4L integration workflow and findings.

## Status

The N4L integration work is complete (October 2025). These files are preserved for:
1. Future reference and reproducibility
2. Cross-referencing with KG-Microbe updates
3. Understanding organism coverage and reconciliation methodology
