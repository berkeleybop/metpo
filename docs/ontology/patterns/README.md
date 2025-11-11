# METPO Ontology Design Patterns

**Last Updated:** 2025-11-11

## Overview

This directory contains reusable ontology design patterns used in METPO development.

## Patterns

### Environmental Condition Parse Model (v0.3)

**File:** `environmental_parse_model_v0.3.md`

A factor-agnostic ontology pattern for normalizing free-text statements about microbial relationships to environmental conditions.

**Key Features:**
- ParseGroup wrapper with raw text preservation
- ParseComponent children for structured extraction
- Supports multiple environmental factors: temperature, pH, salinity, oxygen, pressure
- Handles numerical values, ranges, categorical labels, and qualifiers
- UCUM unit codes for standardization

**Use Cases:**
- Temperature preferences (e.g., "15-37°C (optimum 30°C)")
- pH ranges and optima
- Salinity requirements
- Oxygen relationships
- Any environmental parameter with numerical or categorical values

**Related Schema:**
See `data/schemas/LinkMLModel_schema_v1.5.yaml` for the LinkML implementation.

## Background

These patterns emerged from the N4L data transformation workflow, where free-text phenotypic descriptions needed to be parsed into structured, semantically enriched RDF that integrates with the METPO ontology.

The ParseGroup/ParseComponent pattern has proven effective for:
1. Preserving original source text (traceability)
2. Extracting structured data (numerical ranges, units, categories)
3. Supporting LLM-based parsing with validation
4. Enabling semantic reasoning over phenotypic traits

## Future Work

- SHACL shape library for pattern validation
- Factor-specific cheat sheets (valid units, categorical tokens, qualifiers)
- Confidence scoring and parse error telemetry
