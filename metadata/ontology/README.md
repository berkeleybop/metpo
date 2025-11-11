# Ontology Metadata

This directory contains metadata about METPO ontology submissions, historical usage analysis, and external ontology integrations.

## Purpose

Tracks:
- OLS (Ontology Lookup Service) submission records
- Historical BioPortal submissions and their entity usage
- Metadata about METPO's evolution and external representation

## Contents

### OLS Submission (`ols-submission.csv`)

CSV file tracking METPO's OLS submission history:
- Submission dates and versions
- Contact information
- Status tracking
- Configuration parameters

**Format**: Single CSV with one row per submission attempt

### Historical Submissions (`historical_submissions/`)

Analysis of METPO's historical presence on BioPortal and other ontology repositories.

**entity_extracts/**
- Entity extraction outputs from historical METPO versions
- Generated using ROBOT: `make extract-all-metpo-entities`
- One file per historical OWL version
- Used to analyze term evolution and compare with current METPO

**scripts/**
- Analysis scripts for historical submission data
- Entity extraction workflows
- Term evolution tracking

**README.md**
- Detailed documentation of historical analysis workflows
- Describes entity extraction methodology
- Analysis results and findings

## Usage

### Extract entities from historical submissions

Extract all entities:
```bash
make extract-all-metpo-entities
```

Extract from specific version:
```bash
make metadata/ontology/historical_submissions/entity_extracts/METPO_v2023-01-15.csv
```

### Clean generated files

Remove all entity extraction outputs:
```bash
make clean-entity-extracts
```

## Maintenance

- **entity_extracts/**: Generated files, not manually edited
- **ols-submission.csv**: Updated when submitting to OLS
- **scripts/**: Version-controlled analysis scripts
