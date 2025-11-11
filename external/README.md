# External Ontology Files and Databases

This directory contains all external ontology files and derived databases used by METPO workflows.

## Directory Structure

```
external/
├── ontologies/
│   ├── bioportal/          # Downloaded from BioPortal (gitignored)
│   └── manual/             # Manually added files (tracked in git)
├── databases/              # Derived semsql databases (gitignored)
└── metpo_historical/       # Historical METPO submissions (gitignored)
```

## Ontology Sources

### BioPortal Ontologies (`ontologies/bioportal/`)

Microbial ontologies downloaded from BioPortal that are not available through OLS:

- **MPO**: MPO/RIKEN Microbial Phenotype Ontology
- **OMP**: Ontology of Microbial Phenotypes
- **BIPON**: Bacterial interlocked Process Ontology
- **D3O**: D3O/DSMZ Digital Diversity Ontology
- **FMPM**: Food Matrix for Predictive Microbiology
- **GMO**: Growth Medium Ontology
- **HMADO**: Human Microbiome and Disease Ontology
- **ID-AMR**: Infectious Diseases and Antimicrobial Resistance
- **MCCV**: Microbial Culture Collection Vocabulary
- **MEO**: Metagenome and Environment Ontology
- **miso**: Microbial Conditions Ontology
- **OFSMR**: Open Predictive Microbiology Ontology
- **TYPON**: Microbial Typing Ontology

**Download:**
```bash
# Download all ontologies
make download-external-bioportal-ontologies

# Download specific ontology
uv run download-ontology D3O --output external/ontologies/bioportal/D3O.owl
```

**Note:** These files are tracked in git for convenience (total ~10 MB). They can be updated using the commands above.

### Manual Ontologies (`ontologies/manual/`)

Manually curated or merged ontology files tracked in git:

- **n4l_merged.owl**: Merged N4L phenotypic ontology

### Updating External Ontologies

**When to update:** External ontologies should be refreshed periodically to get latest versions from BioPortal.

**How to update:**
```bash
# 1. Clean existing downloads
make clean-external-bioportal-ontologies

# 2. Download fresh copies
make download-external-bioportal-ontologies

# 3. Update manifest tracking
make scan-manifest

# 4. Regenerate derived files if needed
make notebooks/non-ols-terms/D3O.tsv  # Example: regenerate term extractions
```

**Frequency:** Check for updates quarterly or when cited ontology versions change.

**Important:** Updating ontologies may affect downstream analyses. Document version changes in commit messages.

## Historical METPO Submissions (`metpo_historical/`)

Historical versions of METPO downloaded from BioPortal for ID stability analysis.

**Download:**
```bash
# Download all historical submissions
make download-all-bioportal-submissions

# Download specific submission
make external/metpo_historical/metpo_submission_5.owl
```

See `metadata/historical_usage_analysis/README.md` for detailed workflow.

## Derived Databases (`databases/`)

Semsql databases generated from ontology files.

**Currently:** No databases stored here yet. In the future, semsql .db files generated from external ontologies should be stored here for reuse.

**Example generation:**
```bash
# Generate semsql database (example, not yet implemented)
semsql make external/ontologies/bioportal/D3O.owl external/databases/d3o.db
```

## Git Tracking

- **Tracked**: All ontology files (`ontologies/bioportal/`, `ontologies/manual/`, `metpo_historical/`), directory structure, this README
- **Gitignored**: Only `databases/*.db` (derived files that can be regenerated)

External ontology files are tracked in git (~17 MB total) for convenience, so workflows can run immediately after checkout without requiring BioPortal downloads.

## Dependencies

- **download-ontology**: Python script for BioPortal downloads
- **ROBOT**: For ontology querying and processing
- **semsql**: For database generation (future)
- **BioPortal API key**: Required for downloads (set `BIOPORTAL_API_KEY` environment variable)

## Related Documentation

- **BioPortal downloads**: See Makefile targets starting with `download-external-`
- **Historical analysis**: `metadata/historical_usage_analysis/README.md`
- **Alignment pipeline**: `notebooks/README.md` (if exists)
