# Column Guide for all_api_tests_unified.tsv

**File**: all_api_tests_unified.tsv (25 columns, 369 tests)

---

## Understanding the Redundant Columns

**You're right - there IS significant redundancy!** Multiple columns contain the same or very similar information. This appears to be how the original database was structured.

---

## The Four "Name" Columns (HIGHLY REDUNDANT)

### Column 3: `cupule`
**Example**: `1`, `2`, `3`
**Purpose**: Test position number on the physical strip (1-50)
**Usage**: Which well/cupule on the plastic strip

### Column 4: `cupule_Name_Kit` ⚠️ REDUNDANT
**Example**: `IND`, `URE`, `GLU`
**Purpose**: Test abbreviation **as printed on the bioMérieux kit**
**Usage**: What the manufacturer calls it
**Note**: Usually identical to `name_bacdive`

### Column 5: `name_bacdive` ⚠️ REDUNDANT
**Example**: `IND`, `URE`, `GLU`
**Purpose**: **BacDive's internal name for the test**
**Usage**: How BacDive refers to this test
**Note**: Usually identical to `cupule_Name_Kit`

### Column 8: `ID_microbiol` ⚠️ REDUNDANT
**Example**: `IND_20A`, `URE_20A`, `GLU_20A`
**Purpose**: Microbiological test identifier (test abbreviation + kit name)
**Usage**: Unique ID combining test name and kit
**Note**: Just `cupule_Name_Kit` + `_` + `kit_name`

---

## When They're ACTUALLY Different

### Rare cases where names differ:

**Example 1 - Longer kit name**:
```
cupule_Name_Kit: "LDC (Lys)"
name_bacdive: "LDC (Lys)"
ID_microbiol: "LDC_20E"
```

**Example 2 - Special formatting**:
```
cupule_Name_Kit: "ADH (Arg)"
name_bacdive: "ADH (Arg)"
ID_microbiol: "ADH_20E"
```

**Example 3 - Morphology tests**:
```
cupule_Name_Kit: "GRAM"
name_bacdive: "GRAM"
ID_microbiol: "GRAM_20A"
```

**In 95%+ of cases, these 3 columns are identical or trivially related.**

---

## Complete Column Reference

### Identifiers (4 columns - REDUNDANT)

| # | Column | Example | Purpose | Redundant? |
|---|--------|---------|---------|------------|
| 1 | **kit_name** | `20A_meta` | Which kit | ✅ Useful |
| 2 | **ID_kit_api_20A_meta** | `1` | Row ID in original CSV | ⚠️ Less useful |
| 3 | **cupule** | `1` | Well position on strip | ✅ Useful |
| 4 | **cupule_Name_Kit** | `IND` | Name on kit | ⚠️ Redundant with #5 |
| 5 | **name_bacdive** | `IND` | BacDive name | ⚠️ Redundant with #4 |
| 8 | **ID_microbiol** | `IND_20A` | Test+kit ID | ⚠️ Redundant (just #4+#1) |

**Recommendation**: Use `name_bacdive` (#5) as the canonical test name.

---

### Human-Readable Description (1 column)

| # | Column | Example | Purpose |
|---|--------|---------|---------|
| 6 | **reaction_name** | `Indole production` | ✅ Human-readable description |

**This is the most useful name column** - clear description of what the test detects.

---

### External Links (1 column)

| # | Column | Example | Purpose |
|---|--------|---------|---------|
| 7 | **external_Link** | `http://www.brenda-enzymes.org/enzyme.php?ecno=4.1.99.1` | Link to BRENDA or KEGG |

**Note**: These are 9 years old, some may be broken.

---

### Chemistry & Ontology IDs (6 columns - CORE DATA)

| # | Column | Example | Purpose | Coverage |
|---|--------|---------|---------|----------|
| 9 | **substrate** | `L-tryptophan` | ✅ Chemical substrate name | ~290 tests (79%) |
| 10 | **ID_CHEBI** | `16828` | ✅ CHEBI ID (number only) | ~290 tests (79%) |
| 11 | **CAS** | `73-22-3` | ✅ CAS Registry Number | ~280 tests (76%) |
| 12 | **kegg_comp** | `C00078` | ✅ KEGG Compound ID | ~250 tests (68%) |
| 13 | **brenda_ligand** | `119` | BRENDA ligand ID | ~110 tests (30%) |
| 14 | **enzyme** | `tryptophanase` | ✅ Enzyme name | ~110 tests (30%) |
| 15 | **EC_number** | `4.1.99.1` | ✅ EC classification | ~110 tests (30%) |

**These are the most valuable columns** - semantic ontology mappings.

---

### BacDive Integration Flags (9 columns - BOOLEAN FLAGS)

**Purpose**: Link this test to BacDive data field types

| # | Column | Example | Meaning |
|---|--------|---------|---------|
| 16 | **tf_api_enzyme** | `NULL` or `5` | Links to BacDive enzyme field |
| 17 | **tf_api_met_util** | `1` | Links to BacDive metabolite utilization field |
| 18 | **tf_api_met_prod** | `1` | Links to BacDive metabolite production field |
| 19 | **tf_api_met_test** | `1` | Links to BacDive metabolite test field |
| 20 | **tf_api_met_antibiotica** | `NULL` | Links to BacDive antibiotic field |
| 21 | **tf_api_spore_formation** | `NULL` | Links to BacDive spore formation field |
| 22 | **tf_api_cell_morphology** | `NULL` | Links to BacDive cell morphology field |
| 23 | **tf_api_colony_morphology** | `NULL` | Links to BacDive colony morphology field |
| 24 | **tf_api_culture_medium** | `NULL` | Links to BacDive culture medium field |

**What these mean**:
- Numbers (e.g., `1`, `5`) = ID in that BacDive field type
- `NULL` = Not linked to that BacDive field

**Example**: Indole test (IND_20A)
- `tf_api_met_util = 1` → This test appears as ID #1 in BacDive's "metabolite utilization" field
- `tf_api_met_prod = 1` → Also appears as ID #1 in "metabolite production" field
- `tf_api_met_test = 1` → Also appears as ID #1 in "metabolite test" field

**Use case**: If you're querying BacDive and see "metabolite utilization ID 1", you can look up that this refers to the indole test.

---

### Metadata (1 column)

| # | Column | Example | Purpose |
|---|--------|---------|---------|
| 25 | **last_change** | `2016-03-22 14:45:53` | Timestamp of last update |

**Note**: All rows have 2016-03-22 dates - data is 9 years old.

---

## Which Columns Should You Use?

### For Simple Use Cases (5 essential columns):

1. **name_bacdive** - Test abbreviation
2. **reaction_name** - Human-readable description
3. **ID_CHEBI** - Chemical ID
4. **EC_number** - Enzyme ID (if applicable)
5. **kit_name** - Which kit

**Example**:
```
IND, Indole production, CHEBI:16828, EC:4.1.99.1, 20A_meta
```

### For Complete Mappings (9 columns):

Add these ontology IDs:
- **substrate** - Chemical name
- **CAS** - CAS Registry Number
- **kegg_comp** - KEGG ID
- **enzyme** - Enzyme name

### For BacDive Integration (All 25 columns):

Use everything if you need to cross-reference with BacDive database structure.

---

## Example Rows Explained

### Example 1: Indole Test (IND)

```tsv
kit_name: 20A_meta
cupule: 1
cupule_Name_Kit: IND
name_bacdive: IND                    ← Same as cupule_Name_Kit
reaction_name: Indole production     ← Human-readable
ID_microbiol: IND_20A                ← Just IND + _20A
substrate: L-tryptophan
ID_CHEBI: 16828                      ← CHEBI:16828
enzyme: tryptophanase
EC_number: 4.1.99.1                  ← EC:4.1.99.1
```

**Redundancy**:
- Columns 4, 5, 8 all say essentially "IND" or "IND_20A"
- You really only need ONE of them

---

### Example 2: Glucose Fermentation (GLU)

```tsv
kit_name: 20A_meta
cupule: 3
cupule_Name_Kit: GLU
name_bacdive: GLU                    ← Same as cupule_Name_Kit
reaction_name: Acid from D-glucose   ← Human-readable
ID_microbiol: GLU_20A                ← Just GLU + _20A
substrate: D-glucose
ID_CHEBI: 17634                      ← CHEBI:17634
enzyme: NULL                         ← No specific enzyme
EC_number: NULL                      ← Not an enzyme test
```

**Redundancy**: Same pattern - columns 4, 5, 8 are trivially related

---

### Example 3: Gram Stain (GRAM)

```tsv
kit_name: 20A_meta
cupule: 22
cupule_Name_Kit: GRAM
name_bacdive: GRAM
reaction_name: Gram
ID_microbiol: GRAM_20A
substrate: NULL                      ← No chemical substrate
ID_CHEBI: NULL                       ← Morphology test
enzyme: NULL
EC_number: NULL
```

**Redundancy**: Still present, even when no chemistry IDs

---

## Why Does BacDive Have These Names?

Looking at your screenshots, the **BacDive values** you see are likely from the **BacDive web interface**, which might:
1. Use different display names than internal IDs
2. Show full reaction names instead of abbreviations
3. Format differently for human consumption

**These CSV files are internal database mappings**, not the public-facing names you see in BacDive's web UI.

**The `name_bacdive` column** likely refers to how BacDive stores these internally in their database schema, not what they display to users.

---

## Simplified Column Selection

### Minimal (5 columns) - For basic ontology mapping:
```bash
cut -f1,5,6,10,15 all_api_tests_unified.tsv > api_tests_minimal.tsv
# kit_name, name_bacdive, reaction_name, ID_CHEBI, EC_number
```

### Standard (10 columns) - For comprehensive mapping:
```bash
cut -f1,5,6,9,10,11,12,13,14,15 all_api_tests_unified.tsv > api_tests_standard.tsv
# kit_name, name_bacdive, reaction_name, substrate, ID_CHEBI, CAS, kegg_comp, brenda_ligand, enzyme, EC_number
```

### Complete (25 columns) - For BacDive integration:
```bash
# Use full file
```

---

## Column Recommendations

### ✅ Always Keep:
- `kit_name` (which kit)
- `name_bacdive` OR `cupule_Name_Kit` (pick ONE, they're the same)
- `reaction_name` (human-readable description)
- `ID_CHEBI` (chemical ID)
- `EC_number` (enzyme ID if applicable)

### ⚠️ Optional But Useful:
- `substrate` (chemical name)
- `CAS` (CAS number)
- `kegg_comp` (KEGG ID)
- `enzyme` (enzyme name)
- `cupule` (well position)

### ❌ Can Usually Skip:
- `ID_kit_api_20A_meta` (just row number)
- Pick ONE of: `cupule_Name_Kit`, `name_bacdive`, `ID_microbiol` (they're redundant)
- `tf_api_*` flags (only if integrating with BacDive)
- `brenda_ligand` (if you have EC number, can look this up)
- `last_change` (all same date anyway)

---

## Summary

**Your observation is correct**: There's significant redundancy in columns 2-5 and 8.

**Why it exists**: This appears to be how the database was structured - multiple ways to refer to the same test for different use cases.

**What to use**:
- **name_bacdive** (column 5) - Canonical test abbreviation
- **reaction_name** (column 6) - Human description
- **ID_CHEBI, EC_number, etc.** (columns 10-15) - Ontology mappings

**The core value** is in columns 9-15 (chemistry/enzyme ontology IDs), not the redundant name columns.
