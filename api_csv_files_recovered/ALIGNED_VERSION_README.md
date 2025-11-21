# Aligned Version: all_api_tests_aligned.tsv

**Created**: 2025-11-20
**Purpose**: Properly aligned version handling different structures between zym_ec and standard kits
**Rows**: 370 (369 tests + header)
**Columns**: 29 (standardized across all kits)

---

## Problem Solved

### Issue Discovered

The **zym_ec kit has a different column structure** than the other 14 kits:

**Standard kits (14 files)**:
- 24 columns
- EC number in single column: `EC_number`
- Substrate lowercase: `substrate`
- Has `reaction_name` column

**Zym kit (1 file)**:
- 26 columns
- EC number split into 5 columns: `EC`, `EC1`, `EC2`, `EC3`, `EC4`
- Substrate uppercase: `Substrate`
- Uses `Enzyme_Name_Kit` instead of `cupule_Name_Kit`
- Has `BRENDA_Link` instead of `external_Link`
- NO `reaction_name` column
- NO separate `enzyme` column

### Previous File Problem

`all_api_tests_unified.tsv` (the original unified file):
- ❌ Columns didn't align properly
- ❌ Zym rows had values in wrong positions
- ❌ Made analysis difficult

### Solution

`all_api_tests_aligned.tsv` (this file):
- ✅ All rows have same 29 columns
- ✅ Empty cells where kit doesn't have that data
- ✅ EC number parts preserved for zym
- ✅ Consistent column positions across all kits

---

## Column Structure (29 columns)

### Core Identifiers (8 columns)

| # | Column | Example (standard) | Example (zym) | Notes |
|---|--------|-------------------|---------------|-------|
| 1 | **kit_name** | `20E_meta` | `zym_ec` | Which kit |
| 2 | **ID_kit_api_meta** | `5` | `8` | Row ID in original file |
| 3 | **cupule** | `5` | `8` | Well position |
| 4 | **cupule_Name_Kit** | `CIT` | `Cystine arylamidase` | Test name on kit |
| 5 | **name_bacdive** | `CIT` | `Cystine arylamidase` | BacDive name |
| 6 | **reaction_name** | `Citrate utilization` | *(empty)* | Human description |
| 7 | **external_Link** | `http://www.genome.jp/...` | `NULL` or BRENDA | Link to database |
| 8 | **ID_microbiol** | `CIT_20E` | `test_8_ZYM` | Microbiological ID |

---

### Chemistry & Ontology (7 columns)

| # | Column | Example (standard) | Example (zym) | Notes |
|---|--------|-------------------|---------------|-------|
| 9 | **substrate** | `Citric acid` | `L-cystyl-2-naphthylamide` | Chemical name |
| 10 | **ID_CHEBI** | `30769` | `90426` | CHEBI ID (number only) |
| 11 | **CAS** | `77-92-9` | `65322-97-6` | CAS Registry Number |
| 12 | **kegg_comp** | `C00158` | *(empty)* | KEGG Compound ID |
| 13 | **brenda_ligand** | `1714` | *(empty)* | BRENDA ligand ID |
| 14 | **enzyme** | *(empty)* | *(empty)* | Enzyme name |
| 15 | **EC_number** | *(empty)* | `NULL` or `3.4.21.4` | Full EC number |

---

### EC Number Parts (4 columns - ZYM SPECIFIC)

| # | Column | Example (standard) | Example (zym) | Meaning |
|---|--------|-------------------|---------------|---------|
| 16 | **EC1** | *(empty)* | `3` | EC class (e.g., 3 = hydrolases) |
| 17 | **EC2** | *(empty)* | `4` | EC subclass |
| 18 | **EC3** | *(empty)* | `21` | EC sub-subclass |
| 19 | **EC4** | *(empty)* | `4` | EC serial number |

**For standard kits**: These columns are empty
**For zym kit**: EC number is split into parts (e.g., `EC:3.4.21.4` → `3`, `4`, `21`, `4`)

**Why zym does this**: API ZYM kit focuses on enzyme profiling, so EC classification is more detailed

---

### BacDive Integration Flags (9 columns)

| # | Column | Meaning |
|---|--------|---------|
| 20 | **tf_api_enzyme** | Links to BacDive enzyme field |
| 21 | **tf_api_met_util** | Links to metabolite utilization field |
| 22 | **tf_api_met_prod** | Links to metabolite production field |
| 23 | **tf_api_met_test** | Links to metabolite test field |
| 24 | **tf_api_met_antibiotica** | Links to antibiotic field |
| 25 | **tf_api_spore_formation** | Links to spore formation field |
| 26 | **tf_api_cell_morphology** | Links to cell morphology field |
| 27 | **tf_api_colony_morphology** | Links to colony morphology field |
| 28 | **tf_api_culture_medium** | Links to culture medium field |

**Values**: Number (BacDive field ID) or NULL/empty

---

### Metadata (1 column)

| # | Column | Value |
|---|--------|-------|
| 29 | **last_change** | `2016-03-22 HH:MM:SS` |

---

## Examples Showing Alignment

### Standard Kit Example (API 20E - Citrate test)

```tsv
kit_name: 20E_meta
cupule: 5
cupule_Name_Kit: CIT
name_bacdive: CIT
reaction_name: Citrate utilization          ← Has description
external_Link: http://www.genome.jp/...     ← KEGG link
ID_microbiol: CIT_20E
substrate: Citric acid
ID_CHEBI: 30769
EC_number: (empty)                          ← No EC for this test
EC1: (empty)                                ← Standard kits don't split EC
EC2: (empty)
EC3: (empty)
EC4: (empty)
```

### Zym Kit Example (API ZYM - Trypsin test)

```tsv
kit_name: zym_ec
cupule: 9
cupule_Name_Kit: Trypsin                    ← Long name, not abbreviation
name_bacdive: Trypsin
reaction_name: (empty)                      ← Zym doesn't have this
external_Link: NULL                         ← Or BRENDA link
ID_microbiol: test_9_ZYM
substrate: N-benzoyl-DL-arginine-2-naphthylamide
ID_CHEBI: (empty or NULL)
EC_number: 3.4.21.4                         ← Full EC number
EC1: 3                                      ← EC parts split out
EC2: 4
EC3: 21
EC4: 4
```

---

## Key Differences Between Kits

### Standard Kits (20A, 20E, 20NE, etc.)

**Focus**: Carbohydrate fermentation, metabolite tests
**Test names**: Short abbreviations (IND, URE, GLU)
**Has**: `reaction_name` column
**EC numbers**: Single column, only for enzyme tests (~30%)
**Typical row**: Glucose fermentation test

### Zym Kit (API ZYM)

**Focus**: Enzyme activity profiling
**Test names**: Full enzyme names (Trypsin, Chymotrypsin)
**Lacks**: `reaction_name` column (name is already descriptive)
**EC numbers**: Split into 4 parts for all 20 enzyme tests
**Typical row**: Enzyme substrate hydrolysis test

---

## How to Use This File

### Reading All Tests

```python
import pandas as pd

df = pd.read_csv('all_api_tests_aligned.tsv', sep='\t')

# Show all columns
print(df.columns.tolist())

# Count tests per kit
print(df.groupby('kit_name').size())

# Find all tests with EC numbers
df_ec = df[df['EC_number'].notna() & (df['EC_number'] != '')]
print(f"Tests with EC numbers: {len(df_ec)}")
```

### Reconstructing Full EC Numbers for Zym

```python
# For zym tests, EC_number column has the full EC
# But you can also reconstruct from parts:
def reconstruct_ec(row):
    if row['kit_name'] == 'zym_ec' and pd.notna(row['EC1']):
        return f"EC:{row['EC1']}.{row['EC2']}.{row['EC3']}.{row['EC4']}"
    elif pd.notna(row['EC_number']) and row['EC_number'] != '':
        return f"EC:{row['EC_number']}"
    return None

df['EC_full'] = df.apply(reconstruct_ec, axis=1)
```

### Comparing Kit Types

```python
# Standard kits
standard = df[df['kit_name'] != 'zym_ec']
print(f"Standard kits: {len(standard)} tests")
print(f"With CHEBI: {standard['ID_CHEBI'].notna().sum()}")

# Zym kit
zym = df[df['kit_name'] == 'zym_ec']
print(f"Zym kit: {len(zym)} tests")
print(f"All have EC numbers: {zym['EC_number'].notna().sum()}/{len(zym)}")
```

### Filtering by Columns That Exist

```python
# Get tests with reaction names (standard kits only)
has_reaction = df[df['reaction_name'].notna() & (df['reaction_name'] != '')]

# Get tests with EC parts (zym only)
has_ec_parts = df[df['EC1'].notna() & (df['EC1'] != '')]
```

---

## Empty vs NULL

### Why You See Both

**Empty string** (`''`):
- Column doesn't exist in that kit type
- Example: `reaction_name` for zym rows

**NULL**:
- Column exists but no data for that specific test
- Example: `enzyme` column for non-enzymatic tests

**In TSV**: Both appear as empty cells, but can distinguish in original CSVs

---

## File Comparison

### all_api_tests_unified.tsv (original)

- ❌ 25 columns
- ❌ Zym rows misaligned
- ❌ EC parts missing
- ✅ Smaller file

### all_api_tests_aligned.tsv (this file)

- ✅ 29 columns (standardized)
- ✅ All rows properly aligned
- ✅ Preserves zym EC parts
- ✅ Easy to analyze
- ⚠️ More empty cells

**Recommendation**: Use `all_api_tests_aligned.tsv` for analysis

---

## Coverage Statistics

### By Kit Type

**Standard kits** (349 tests across 14 kits):
- ~80% have CHEBI IDs
- ~25% have EC numbers (enzyme tests only)
- ~70% have KEGG IDs
- 100% have `reaction_name`
- 0% have EC parts (EC1-EC4)

**Zym kit** (20 tests):
- ~50% have CHEBI IDs (some substrates are mixtures)
- 100% have EC numbers (all enzyme tests)
- ~0% have KEGG IDs
- 0% have `reaction_name`
- 100% have EC parts (EC1-EC4)

### Combined (369 tests total)

- ~79% have CHEBI IDs (~290 tests)
- ~35% have EC numbers (~130 tests)
- ~68% have KEGG IDs (~250 tests)
- ~95% have `reaction_name` (all except zym)
- ~5% have EC parts (zym only)

---

## Recommendations

### For Ontology Mapping

Use these columns:
- `name_bacdive` - Test identifier
- `reaction_name` - Description (if available)
- `ID_CHEBI` - Chemical substrate
- `EC_number` - Enzyme classification
- For zym only: `EC1`, `EC2`, `EC3`, `EC4` for detailed EC info

### For BacDive Integration

Use these columns:
- `ID_microbiol` - Cross-reference to BacDive
- `tf_api_*` columns - Link to BacDive field IDs
- `kit_name` - Which API kit system

### For Data Quality

Check these:
- `last_change` - All 2016, needs validation
- `external_Link` - May have broken URLs
- Empty CHEBI/EC - Expected for morphology tests

---

## Summary

**Problem**: Zym kit had different structure than other 14 kits
**Solution**: Created aligned file with 29 standard columns
**Result**: All 369 tests now in consistent format
**Trade-off**: More empty cells, but proper alignment
**Use case**: Easy analysis across all kits

This is the **recommended file** for working with the complete API test dataset.
