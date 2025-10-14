# METPO Data Directory Structure

This directory contains organized data files generated during the METPO ontology stability analysis.

## Directory Structure

```
data/
├── bioportal_owl/           # BiPortal OWL submissions
│   ├── metpo_submission_2.owl
│   ├── metpo_submission_3.owl
│   ├── ...
│   └── metpo_submission_10.owl
├── entity_extracts/         # Extracted METPO entities
│   ├── metpo_submission_2_all_entities.tsv
│   ├── metpo_submission_3_all_entities.tsv
│   ├── ...
│   └── metpo_submission_10_all_entities.tsv
└── reports/                 # Analysis reports
    └── METPO_Stability_Analysis_Comprehensive_Report.md
```

## File Descriptions

### bioportal_owl/
Contains the original OWL files downloaded from BiPortal for METPO submissions 2-10.
- **Source**: BiPortal API (https://data.bioontology.org/ontologies/METPO/)
- **Format**: OWL/RDF-XML
- **Coverage**: Submissions 2-10 (submission 1 has no OWL file)
- **File sizes**: Range from ~107KB (submission 2) to ~1.25MB (submissions 4-5)

### entity_extracts/
Contains TSV files with extracted METPO entities from each OWL submission.
- **Source**: Generated via ROBOT SPARQL queries on BiPortal OWL files
- **Format**: Tab-separated values (TSV)
- **Columns**: `?entity`, `?type`, `?label`, `?deprecated`, `?synonym_type`, `?synonym`
- **Content**: All entities with IRIs starting with `https://w3id.org/metpo/`

### reports/
Contains comprehensive analysis reports.
- **METPO_Stability_Analysis_Comprehensive_Report.md**: 47-page comprehensive analysis of METPO entity stability, IRI evolution, and BactoTraits integration

## Analysis Tools

The analysis directory contains:
```
analysis/
├── sparql_queries/
│   └── query_metpo_entities.sparql    # SPARQL query for entity extraction
└── scripts/
    └── download_bioportal_submissions.sh  # BiPortal download script
```

## Makefile Targets

Use these Make targets to work with the data:

```bash
# Download all BiPortal submissions
make download-all-bioportal-submissions

# Extract entities from all submissions
make extract-all-metpo-entities

# Clean all generated data
make clean-data

# Clean specific data types
make clean-bioportal-submissions
make clean-entity-extracts
make clean-sheets
```

## Key Findings

The analysis revealed **critical IRI stability violations** in METPO:

1. **Three major numbering scheme changes**: `000xxx` → `0000xxx` → `1000xxx/2000xxx`
2. **54% entity discrepancy** between Google Sheets (280) and BiPortal (430)
3. **1,487+ external terms** imported then removed between submissions 4-6
4. **Complete abandonment** of original IRIs with no migration path

See the comprehensive report for detailed findings and recommendations.

## Data Integrity

All files include MD5 checksums for integrity verification. The BiPortal downloads were verified against submission-specific API endpoints to ensure version accuracy.

## Scientific Context

The analysis incorporates findings from:
- **Cébron et al. (2021)** BactoTraits research (19,455 bacterial strains)
- **Five functional groups** identified through fuzzy correspondence analysis
- **Direct integration** with METPO BactoTraits sheet mappings

## Usage Notes

- Files are organized for reproducible analysis workflows
- SPARQL queries can be rerun on any OWL file for updated extractions
- Reports include scientific validation context for trait-based approaches
- Directory structure supports both automated processing and manual inspection