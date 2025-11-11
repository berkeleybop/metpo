# Data Schemas

**Last Updated:** 2025-11-11

## Overview

This directory contains schema definitions used for structured data modeling in METPO.

## Files

### `LinkMLModel_schema_v1.5.yaml`
LinkML schema implementation of the Environmental Condition Parse Model (v0.3).

**Defines:**
- `ParseGroup` class - Wrapper for raw text and structured components
- `ParseComponent` class - Structured extraction fragments
- Properties for numerical values (minimum, maximum, spot values)
- Properties for categorical labels and qualifiers
- Unit specifications (UCUM codes)

**Used for:**
- Temperature data parsing and normalization
- Salinity extraction from free text
- pH range processing
- General environmental parameter structuring

**Related Documentation:**
See `docs/ontology/patterns/environmental_parse_model_v0.3.md` for the conceptual model and design rationale.

## LinkML Resources

- LinkML Documentation: https://linkml.io/
- LinkML GitHub: https://github.com/linkml/linkml

## Future Schemas

This directory can accommodate additional schema definitions for:
- OntoGPT extraction templates
- Data validation schemas (SHACL)
- Pydantic models for data processing
- Other structured data formats
