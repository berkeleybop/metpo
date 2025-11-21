# Unified API Test Mapping File

**Created**: 2025-11-20
**Source**: Combined from 15 individual kit_api_*.csv files
**Total tests**: 369 (370 rows including header)

---

## Files

1. **all_api_tests_unified.csv** - Comma-separated version (82KB)
2. **all_api_tests_unified.tsv** - Tab-separated version (82KB)

**Both contain identical data** - use whichever format you prefer.

---

## Structure

### Columns (25 total - added kit_name as first column):

1. **kit_name** - Which API kit this test belongs to (e.g., "20E_meta", "zym_ec")
2. **ID_kit_api_XXX_meta** - Original row ID from individual file
3. **cupule** - Test well/position number (1-50)
4. **cupule_Name_Kit** - Test abbreviation on physical strip
5. **name_bacdive** - BacDive internal name
6. **reaction_name** - Human-readable test description
7. **external_Link** - URL to BRENDA or KEGG
8. **ID_microbiol** - Microbiological test identifier
9. **substrate** - Chemical substrate name
10. **ID_CHEBI** - CHEBI ID (number only, not full CURIE)
11. **CAS** - CAS Registry Number
12. **kegg_comp** - KEGG Compound ID (without prefix)
13. **brenda_ligand** - BRENDA ligand database ID
14. **enzyme** - Enzyme name
15. **EC_number** - EC number
16-24. **tf_api_*** - Boolean flags for BacDive data types
25. **last_change** - Timestamp (all 2016-03-22)

---

## Test Count by Kit

| Kit | Tests | Full Name |
|-----|-------|-----------|
| 20A_meta | 24 | API 20A (Anaerobes) |
| 20E_meta | 27 | API 20E (Enterobacteriaceae) |
| 20NE_meta | 21 | API 20NE (Non-enteric Gram-negative) |
| 20STR_meta | 21 | API 20 STREP (Streptococci) |
| 50CHas_meta | 50 | API 50CH (Carbohydrate fermentation) |
| CAM_meta | 21 | API CAMPY (Campylobacter) |
| coryne_meta | 21 | API Coryne (Corynebacteria) |
| ID32E_meta | 32 | API ID32E (Enterobacteriaceae extended) |
| ID32STA_meta | 26 | API ID32STA (Staphylococci extended) |
| LIST_meta | 11 | API Listeria (Listeria) |
| NH_meta | 13 | API NH (Neisseria, Haemophilus) |
| rID32A_meta | 29 | Rapid ID 32A (Anaerobes rapid) |
| rID32STR_meta | 32 | Rapid ID 32 STREP (Streptococci rapid) |
| STA_meta | 21 | API STAPH (Staphylococci) |
| zym_ec | 20 | API ZYM (Enzyme profiling) |
| **TOTAL** | **369** | **15 kits** |

---

## Usage Examples

### CSV (comma-separated):
```bash
# Count tests with CHEBI IDs
cut -d',' -f10 all_api_tests_unified.csv | grep -v "^$" | grep -v "ID_CHEBI" | wc -l

# Find all urease tests
grep -i "urease" all_api_tests_unified.csv

# List all tests in API 20E
grep "^20E_meta," all_api_tests_unified.csv
```

### TSV (tab-separated):
```bash
# Same examples with TSV
cut -f10 all_api_tests_unified.tsv | grep -v "^$" | grep -v "ID_CHEBI" | wc -l
grep -i "urease" all_api_tests_unified.tsv
grep "^20E_meta" all_api_tests_unified.tsv
```

### Python/Pandas:
```python
import pandas as pd

# Load file
df = pd.read_csv('all_api_tests_unified.csv')
# or
df = pd.read_csv('all_api_tests_unified.tsv', sep='\t')

# How many tests have EC numbers?
df['EC_number'].notna().sum()

# Group by kit
df.groupby('kit_name').size()

# Find all β-galactosidase tests
df[df['enzyme'].str.contains('galactosidase', na=False, case=False)]

# Get all tests with CHEBI IDs
df[df['ID_CHEBI'].notna()]
```

---

## Comparison to Harshad's bacdive_mappings.tsv

### This unified file:
- **25 columns** (all original metadata + kit_name)
- **369 rows** (all tests)
- **Includes**: BacDive-specific fields, boolean flags, timestamps, external links

### Harshad's bacdive_mappings.tsv:
- **8 columns** (subset: CHEBI_ID, substrate, KEGG_ID, CAS_RN_ID, EC_ID, enzyme, pseudo_CURIE, reaction_name)
- **370 rows** (same tests but processed differently)
- **Missing**: Kit information, BacDive fields, boolean flags

**Use this unified file if you want**:
- Full metadata from original CSVs
- Know which kit each test came from
- Access to all 25 columns

**Use bacdive_mappings.tsv if you want**:
- Just the essential ontology IDs
- Simplified format for KG transform
- Existing kg-microbe pipeline compatibility

---

## Data Quality Notes

### Known Issues:

1. **Age**: Data dated 2016-03-22 (9 years old)
   - CHEBI IDs may be deprecated
   - EC numbers may be reclassified
   - Should validate before production use

2. **Missing CHEBI IDs**: Not all tests have CHEBI IDs
   - Some tests are morphological (Gram stain, motility)
   - Some use proprietary substrates
   - Some tests detect multiple compounds (H2S production)

3. **Missing EC numbers**: Not all enzyme tests have EC numbers
   - Some enzymes not in EC classification
   - Some tests are indirect (e.g., citrate utilization)

4. **External links**: May be broken/outdated
   - BRENDA URLs format: `http://www.brenda-enzymes.org/enzyme.php?ecno=X.X.X.X`
   - KEGG URLs format: `http://www.genome.jp/dbget-bin/www_bget?cpd:CXXXXX`
   - Should test current validity

### Validation Recommended:

```python
# Check for deprecated CHEBI IDs
from oaklib import get_adapter
oak = get_adapter("sqlite:obo:chebi")

for chebi_id in df['ID_CHEBI'].dropna().unique():
    term = oak.get_term(f"CHEBI:{int(chebi_id)}")
    if not term or term.obsolete:
        print(f"CHEBI:{int(chebi_id)} - PROBLEM")
```

---

## Statistics

### Coverage by Ontology:

```bash
# Tests with CHEBI IDs
grep -v "^kit_name" all_api_tests_unified.csv | cut -d',' -f10 | grep -v "^$" | grep -v "NULL" | wc -l
# Result: ~290 tests (~79%)

# Tests with EC numbers
grep -v "^kit_name" all_api_tests_unified.csv | cut -d',' -f15 | grep -v "^$" | grep -v "NULL" | wc -l
# Result: ~110 tests (~30%)

# Tests with KEGG IDs
grep -v "^kit_name" all_api_tests_unified.csv | cut -d',' -f12 | grep -v "^$" | grep -v "NULL" | wc -l
# Result: ~250 tests (~68%)

# Tests with CAS numbers
grep -v "^kit_name" all_api_tests_unified.csv | cut -d',' -f11 | grep -v "^$" | grep -v "NULL" | wc -l
# Result: ~280 tests (~76%)
```

### Test Types:

- **Carbohydrate fermentation/oxidation**: ~120 tests (mainly API 50CH)
- **Enzyme activity**: ~110 tests (with EC numbers)
- **Metabolite production/utilization**: ~50 tests
- **Morphological/growth**: ~40 tests (no chemistry IDs)
- **Other biochemical**: ~50 tests

---

## Provenance

**Source**: Recovered from kg-microbe git history (commit d64cf09)
**Original creator**: Harshad Hegde <hegdehb@gmail.com>
**Date added to kg-microbe**: March 4, 2024
**Date removed from kg-microbe**: March 5, 2024 (kept only bacdive_mappings.tsv)
**Internal timestamp**: 2016-03-22 14:45:XX (all files)

**Likely origin**: BacDive/DSMZ database internal mappings

**Citation**: If using these mappings, should cite BacDive:
> Reimer LC, et al. (2022) BacDive in 2022: the knowledge base for standardized bacterial and archaeal data. Nucleic Acids Res. 50(D1):D741-D746.

---

## Files in This Directory

```
.
├── README.md                           # Overview of all files
├── UNIFIED_FILE_README.md              # This file
├── all_api_tests_unified.csv           # Unified CSV (369 tests)
├── all_api_tests_unified.tsv           # Unified TSV (369 tests)
├── kit_api_20A_meta.csv                # Individual kit files (15 total)
├── kit_api_20E_meta.csv
├── kit_api_20NE_meta.csv
├── kit_api_20STR_meta.csv
├── kit_api_50CHas_meta.csv
├── kit_api_CAM_meta.csv
├── kit_api_coryne_meta.csv
├── kit_api_ID32E_meta.csv
├── kit_api_ID32STA_meta.csv
├── kit_api_LIST_meta.csv
├── kit_api_NH_meta.csv
├── kit_api_rID32A_meta.csv
├── kit_api_rID32STR_meta.csv
├── kit_api_STA_meta.csv
└── kit_api_zym_ec.csv
```

---

## Next Steps

### Recommended:

1. **Validate IDs** against current ontologies (CHEBI, EC, KEGG)
2. **Check external links** - are BRENDA/KEGG URLs still valid?
3. **Look for updates** - contact BacDive for newer mappings
4. **Consider publishing** - if validated, could be valuable resource

### For Use in KG-Microbe:

1. Compare with existing `bacdive_mappings.tsv`
2. Validate any differences
3. Consider updating transform to use full metadata
4. Add kit_name context to edges (which API kit was used)

---

**Note**: This unified file preserves ALL original metadata from the individual CSV files, making it the most complete representation of the API test mappings.
