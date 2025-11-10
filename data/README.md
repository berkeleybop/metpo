# METPO Data Directory Structure

This directory contains generated data files for the METPO ontology project.

**Note:** Historical ID tracking data has been moved to `metadata/historical_usage_analysis/`
for better modularity. See that directory's README for BioPortal submissions and entity extracts.

## Directory Structure

```
data/
├── bactotraits/            # BactoTraits migration data and scripts
├── generated/              # Generated data from SPARQL queries
└── reports/                # Analysis reports
```

## File Descriptions

### bactotraits/
BactoTraits data migration materials:
- `1-s2.0-S1470160X21007123-main.pdf` - Cébron et al. (2021) BactoTraits paper
- `bactotraits_migration_ready.tsv` - Migration-ready data
- `bactotraits_to_minimal_classes_migration.tsv` - Class mappings
- `create_bactotraits_migration.py` - Migration script

### generated/
Generated data from SPARQL queries:
- `bacdive_oxygen_phenotype_mappings.tsv` - BacDive oxygen phenotype mappings

### reports/
Analysis reports for the METPO project.
- **METPO_Stability_Analysis_Comprehensive_Report.md**: Comprehensive analysis of METPO entity stability, IRI evolution, and BactoTraits integration

## Makefile Targets

```bash
# Clean all generated data
make clean-data
```

## Related Directories

- **`metadata/historical_usage_analysis/`**: Historical METPO ID tracking via BioPortal submissions and Google Sheets
- **`assets/`**: Static reference data (N4L phenotypic ontology)
- **`downloads/`, `large/`, `local/`**: Gitignored working directories