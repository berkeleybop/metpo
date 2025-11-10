# METPO Term Labels

This directory contains extracted term labels from the METPO ontology for use in analysis scripts and notebooks.

## Files

### metpo_all_labels.tsv
**Location**: `data/metpo_terms/metpo_all_labels.tsv`
**Format**: Tab-separated, 2 columns (no header)
**Size**: 250 terms
**Columns**:
- Column 1: METPO ID (e.g., `METPO:1000678`)
- Column 2: Label (e.g., `oval shaped`)

**Purpose**: Complete set of METPO term labels for full-scale analysis.

**Used by**:
- `scripts/analysis/assess_ontology_by_api_search.py` - Standalone script for ontology coverage assessment

### metpo_sample_labels.tsv
**Location**: `data/metpo_terms/metpo_sample_labels.tsv`
**Format**: Tab-separated, 2 columns (no header)
**Size**: 50 terms (20% sample)
**Columns**:
- Column 1: METPO ID (e.g., `METPO:1000678`)
- Column 2: Label (e.g., `oval shaped`)

**Purpose**: Smaller sample for rapid prototyping and testing notebooks without long API wait times.

**Used by**:
- `notebooks/assess_ontology_by_api_search.ipynb` - Interactive notebook for exploring ontology search APIs

**Example content**:
```
METPO:1000678	oval shaped
METPO:1000481	NaCl delta mid2
METPO:1001002	growth temperature observation
METPO:1000802	Anaerobic respiration
METPO:1000883	cell length very small
```

## How to Regenerate

These files can be regenerated from the METPO ontology using OAK (Ontology Access Kit):

### Generate metpo_all_labels.tsv (all terms)

```bash
# Extract all term IDs and labels from METPO ontology
uv run runoak -i src/ontology/metpo.owl labels --output data/metpo_terms/metpo_all_labels.tsv

# Alternative: Use ROBOT
robot query --input src/ontology/metpo.owl \
  --query scripts/sparql/extract_labels.sparql \
  data/metpo_terms/metpo_all_labels.tsv
```

### Generate metpo_sample_labels.tsv (20% sample)

```bash
# Create 20% random sample (50 out of 250 terms)
shuf -n 50 data/metpo_terms/metpo_all_labels.tsv > data/metpo_terms/metpo_sample_labels.tsv

# Or use head for consistent first 50 terms
head -n 50 data/metpo_terms/metpo_all_labels.tsv > data/metpo_terms/metpo_sample_labels.tsv
```

### Using Python

```python
import pandas as pd

# Load full labels
all_labels = pd.read_csv(
    "src/ontology/metpo.owl",
    # ... OAK or rdflib parsing ...
)

# Save all labels
all_labels.to_csv(
    "data/metpo_terms/metpo_all_labels.tsv",
    sep="\t",
    header=False,
    index=False
)

# Create 20% sample
sample = all_labels.sample(frac=0.2, random_state=42)
sample.to_csv(
    "data/metpo_terms/metpo_sample_labels.tsv",
    sep="\t",
    header=False,
    index=False
)
```

## Why Two Files?

**metpo_all_labels.tsv** (250 terms):
- Used for production analysis
- Complete coverage assessment
- Longer runtime (~8-10 minutes for API searches)

**metpo_sample_labels.tsv** (50 terms):
- Used for interactive exploration in notebooks
- Faster iteration during development (~2 minutes for API searches)
- Maintains statistical representativeness with 20% sample

## File Origin

These files were originally created in commit `9be7f82` (2024-10-24) as part of initial OLS/BioPortal search notebooks. They were:
1. Extracted manually from the METPO ontology
2. Moved from `notebooks/` to `data/metpo_terms/` in commit `4a5253b` (2024-11-10)

The extraction method is not documented in git history, but can be recreated using the commands above.

## Related Files

- **Source**: `src/ontology/metpo.owl` - METPO ontology (OWL format)
- **Analysis**: `scripts/analysis/assess_ontology_by_api_search.py` - Uses metpo_all_labels.tsv
- **Notebook**: `notebooks/assess_ontology_by_api_search.ipynb` - Uses metpo_sample_labels.tsv
- **Output**: `data/ontology_assessments/phase1_raw_results.tsv` - Search results from notebooks
