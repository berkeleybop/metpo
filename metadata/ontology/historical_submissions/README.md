# Historical METPO ID Usage Analysis

This directory contains a self-contained workflow for tracking historical METPO ID usage across BioPortal submissions and Google Sheets.

## Purpose

Track METPO entity stability and ID reuse patterns over time to:
- Identify IRI numbering scheme changes
- Detect entity additions/removals between versions
- Compare BioPortal submissions with Google Sheets sources
- Support ID migration planning

## Directory Structure

```
metadata/historical_usage_analysis/
├── scripts/
│   └── download_bioportal_submissions.sh  # Download historical submissions
└── entity_extracts/                        # Extracted entities (generated)
    ├── metpo_submission_2_all_entities.tsv
    ├── metpo_submission_3_all_entities.tsv
    └── ...

external/metpo_historical/                  # Downloaded OWL files (generated)
├── metpo_submission_2.owl
├── metpo_submission_3.owl
└── ...
```

## Complete Workflow

### 1. Download BioPortal Submissions

**Using Makefile (recommended):**
```bash
# Download all submissions (2-10)
make download-all-bioportal-submissions

# Download specific submission
make external/metpo_historical/metpo_submission_5.owl

# List available submissions
make list-bioportal-submissions
```

**Using script directly:**
```bash
# Requires BIOPORTAL_API_KEY environment variable
export BIOPORTAL_API_KEY="your-key-here"
./metadata/historical_usage_analysis/scripts/download_bioportal_submissions.sh
```

**Output:** OWL files in `external/metpo_historical/` (submissions 2-10, ~4.3 MB total)

### 2. Extract METPO Entities

**Using Makefile:**
```bash
# Extract entities from all submissions
make extract-all-metpo-entities
```

**Manual extraction:**
```bash
# Extract from a specific submission
robot query \
  --input external/metpo_historical/metpo_submission_5.owl \
  --query sparql/query_metpo_entities.sparql \
  metadata/historical_usage_analysis/entity_extracts/metpo_submission_5_all_entities.tsv
```

**Output:** TSV files in `entity_extracts/` with columns:
- `?entity` - METPO IRI
- `?type` - OWL class type
- `?label` - rdfs:label
- `?deprecated` - Deprecation status
- `?synonym_type` - Synonym type (exact/related)
- `?synonym` - Synonym value

### 3. Analyze Results

Entity extracts can be used for:
- **Diff analysis**: Compare entities between submissions
- **IRI pattern analysis**: Track numbering scheme changes
- **Coverage analysis**: Identify gaps between BioPortal and Google Sheets
- **Stability reports**: Document ID reuse violations

See `data/reports/METPO_Stability_Analysis_Comprehensive_Report.md` for comprehensive findings.

## Key Findings

Historical analysis revealed:

1. **Three major numbering scheme changes**: `000xxx` → `0000xxx` → `1000xxx/2000xxx`
2. **54% entity discrepancy** between Google Sheets (280) and BiPortal (430)
3. **1,487+ external terms** imported then removed between submissions 4-6
4. **Complete abandonment** of original IRIs with no migration path

## Cleaning Up

```bash
# Remove downloaded submissions
make clean-bioportal-submissions

# Remove extracted entities
make clean-entity-extracts

# Clean all historical data
make clean-data  # (includes both above)
```

## Related Tools

- **SPARQL Query**: `sparql/query_metpo_entities.sparql` - Extracts all METPO entities
- **Makefile targets**: Full automation in root `Makefile`
- **Google Sheets**: Tracked separately in `downloads/sheets/` (gitignored)

## Dependencies

- **ROBOT**: Ontology processing (entity extraction)
- **curl**: BioPortal API downloads
- **BioPortal API key**: Required for downloads (free registration)

## Scientific Context

Analysis incorporates:
- **Cébron et al. (2021)** BactoTraits research (19,455 bacterial strains)
- **Five functional groups** identified through fuzzy correspondence analysis
- **Direct integration** with METPO BactoTraits sheet mappings

## Self-Contained Design

This directory is fully self-contained:
- All scripts and queries referenced are in predictable locations
- All generated data stays within this directory
- Makefile targets provide complete automation
- Can be archived or moved as a unit for historical reference
