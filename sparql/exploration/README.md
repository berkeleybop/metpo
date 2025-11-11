# SPARQL Exploration Queries

**Last Updated:** 2025-11-11

## Overview

This directory contains historical SPARQL queries used during exploratory data analysis and integration work. These queries are **archived for reference** - they were used during active development but are not part of current production workflows.

## Subdirectories

### `kg-microbe/`
Queries used to explore KG-Microbe structure when loaded into GraphDB (2025):
- Biolink Association and OrganismTaxon predicate analysis
- IRI pattern discovery
- Biolink relation type enumeration
- Identifying organisms with highest triple counts

**Related Issues:** #110 (Load kg-microbe into a GraphDB repository)

### `n4l/`
Queries used during N4L/KG-Microbe harmonization work:
- Organism statement counting
- Identifying phenotypically rich taxa in N4L data
- Cross-referencing with NCBI Taxonomy

**Related Issues:** #87, #90, #91, #101-104 (N4L/KG-Microbe comparison work)

## Context

These queries were developed during a GraphDB-based exploration phase where both N4L and KG-Microbe data were loaded into OntoText GraphDB repositories for:
1. Understanding data structure and coverage
2. Developing aboutness chain traversals (Reference→Protolog→Organism)
3. Comparing vocabularies and entity coverage
4. Identifying integration opportunities and gaps

All related GitHub issues were **closed in October 2025**, indicating this exploratory work is complete.

## Status

These queries are **not actively maintained** and may reference named graphs, repository configurations, or data structures that no longer exist in the current workflow.

They are preserved for:
- Historical reference
- Understanding past integration methodology
- Potential reuse if GraphDB-based exploration is needed again

## Production Queries

For current production SPARQL queries, see the root `sparql/` directory.
