# Data Sources: Formats and Reconciliation Strategy

**Date:** 2025-10-09
**Purpose:** Document the native formats of our three main structured data sources (Madin, BacDive, BactoTraits), available schema/analysis resources, and reconciliation strategy for METPO QC.

---

## Table of Contents

1. [Overview](#overview)
2. [Madin et al. Dataset](#madin-et-al-dataset)
3. [BacDive Dataset](#bacdive-dataset)
4. [BactoTraits Dataset](#bactotraits-dataset)
5. [Reconciliation Strategy](#reconciliation-strategy)
6. [Related GitHub Issues](#related-github-issues)

---

## Overview

METPO incorporates synonyms and mappings from three primary microbial trait databases. Understanding their native formats is critical for:

1. **Round-trip assessment** - Verifying METPO covers all source values (Issue #223)
2. **False claim detection** - Identifying synonyms METPO attributes to sources that don't actually appear in source data
3. **Gap analysis** - Finding high-value unmapped fields/values
4. **Independent QC** - Working independently from kg-microbe while cross-checking our work against theirs

---

## Madin et al. Dataset

### Native Format

**File:** `bacteria_archaea_traits` GitHub repository
**Format:** Standard flat CSV (comma-delimited)
**Structure:** Single header row, one record per row

**Key Characteristics:**
- **~170k strain-level records** and ~15k species-aggregated records
- **35 fields total** including:
  - 14 phenotypic traits (gram_stain, cell_shape, metabolism, motility, sporulation, etc.)
  - 5 quantitative genomic traits (genome_size, gc_content, coding_genes, etc.)
  - 4 environmental characteristics (isolation_source, etc.)
  - Taxonomic identifiers (org_name, species, genus, family, order, class, phylum, superkingdom)

**Data Types:**
- Categorical fields with controlled vocabularies (e.g., `gram_stain`: "positive", "negative")
- Numerical fields (gc_content, genome_size, optimum_tmp, optimum_ph, etc.)
- Free-text fields (org_name, data_source)
- Special case: `pathways` field contains **comma-separated lists** of metabolic pathways

**Example Fields and Values:**
```
gram_stain: positive, negative
metabolism: aerobic, anaerobic, facultative, obligate aerobic, obligate anaerobic, strictly anaerobic, microaerophilic
cell_shape: bacillus, coccus, spiral, vibrio, filament, flask, pleomorphic, ring, star, etc.
range_tmp: psychrophilic, mesophilic, thermophilic, extreme thermophilic, psychrotolerant, thermotolerant, facultative psychrophilic
range_salinity: non-halophilic, halotolerant, halophilic, moderate-halophilic, extreme-halophilic, euryhaline, stenohaline
motility: yes, no, flagella, axial filament, gliding
sporulation: yes, no
pathways: acetogenesis, methanogenesis, fermentation, aerobic_heterotrophy, photoautotrophy, methylotrophy, etc. (103 unique values)
```

### Available in METPO Repo

**Location:** No local copy - we query MongoDB for Madin data

**Reconciliation Completed:**
- **Script:** `src/scripts/reconcile_madin_coverage.py`
- **Report:** `reports/madin-metpo-reconciliation.yaml`
- **Makefile target:** `make reconcile-madin`
- **Status:** ✅ Complete (Issue #223)

**Key Findings:**
- 8/35 field names mapped to METPO
- 7/8 mapped fields have 100% value coverage
- `pathways` field: only 15/103 values (14.6%) mapped
- 70 total METPO-Madin synonyms, 62 verified, 0 false claims

---

## BacDive Dataset

### Native Format

**Source:** BacDive REST API (https://api.bacdive.dsmz.de/)
**Format:** Nested JSON documents
**Structure:** Hierarchical with 10 main sections, ~234 fields

**Key Characteristics:**
- **~99,392 bacterial/archaeal strains** (as of analyzed snapshot)
- **Document-oriented** with variable structure (not all strains have all fields)
- **Deeply nested** (3-4 levels deep in many cases)
- **Mix of controlled vocabularies and free text**
- **Reference-linked** (many fields include `@ref` for citation tracking)

**Top-Level Sections:**
1. `General` - IDs, keywords, description, NCBI tax id
2. `Name and taxonomic classification` - LPSN taxonomy, synonyms
3. `Morphology` - Cell shape, size, gram stain, motility
4. `Culture and growth conditions` - Media, temperature, pH
5. `Physiology and metabolism` - Metabolite utilization, enzymes, oxygen tolerance
6. `Isolation, sampling and environmental information` - Source categories
7. `Safety information` - Biosafety level, risk assessment
8. `Sequence information` - 16S, genome sequences
9. `Genome-based predictions` - Predicted capabilities
10. `External links` - Cross-references to other databases

**Example Nested Paths:**
```json
[].Physiology and metabolism.metabolite utilization.[].metabolite
[].Physiology and metabolism.metabolite utilization.[].utilization activity
[].Physiology and metabolism.oxygen tolerance.oxygen tolerance
[].Morphology.cell morphology.cell shape
[].Morphology.cell morphology.gram stain
[].Morphology.cell morphology.motility
[].Culture and growth conditions.culture temp.[].type
[].Culture and growth conditions.culture temp.[].growth
```

**Controlled Vocabulary Examples:**
```
utilization activity: +, -, +/-
oxygen tolerance: aerobe, anaerobe, facultative anaerobe, microaerophile, obligate aerobe, obligate anaerobe, aerotolerant, microaerotolerant
type strain: yes, no
domain: Bacteria, Archaea
cell shape: coccus-shaped, rod-shaped, spiral-shaped, curved-shaped, vibrio-shaped, filament-shaped, etc.
gram stain: positive, negative, variable
motility: yes, no
```

### Available Resources

#### 1. Genson-Inferred JSON Schema (bacphen-awareness repo)

**Location:** `~/Documents/gitrepos/bacphen-awareness/data/output/954eac922928d7abfd6130e7cc64a88c/`

**Files:**
- `bacdive_strains_genson_schema.json` (170K) - Complete JSON Schema automatically inferred from data
- `bacdive_path_counts_merged.tsv` (1,392 rows) - All JSON paths with occurrence and distinct value counts
- `bacdive_enum_values.tsv` (2,858 rows) - **All enumerated/controlled vocabulary values found in BacDive**
- `bacdive_path_to_enum.tsv` (980 rows) - Maps which paths contain controlled vocabularies
- `bacdive_distinct_value_counts.tsv` (1,392 rows) - Value cardinality analysis
- `bacdive_decision_log.tsv` (1,004 rows) - Processing decisions

**Key Insights from Analysis:**
- **881,660 metabolite utilization entries** with 953 distinct metabolites
- **577,932 enzyme entries** with 191 distinct enzyme values
- **99,392 strains** with taxonomic classification
- **2,858 controlled vocabulary terms** that should have METPO synonyms

**Example Path Counts:**
```
path_count	path	distinct_value_count
881660	[].Physiology and metabolism.metabolite utilization.[].metabolite	953
881629	[].Physiology and metabolism.metabolite utilization.[].utilization activity	4
577932	[].Physiology and metabolism.enzymes.[].value	191
99392	[].Name and taxonomic classification.species	23052
99392	[].General.BacDive-ID	99392
```

**Advantages of Genson Analysis:**
- ✅ **Complete coverage** - automatically discovered all fields
- ✅ **All enumerated values** (2,858 rows) - exact list of controlled vocabularies
- ✅ **Frequency data** - shows which fields are densely vs sparsely populated
- ✅ **Type information** - JSON Schema with anyOf for polymorphic fields
- ✅ **Regeneratable** - can be updated from new data dumps

#### 2. kg-microbe Field Path Documentation

**Location:** `docs/kg_microbe_complete_field_path_and_mapping_reference.md`

**Content:**
- Hand-curated field path documentation
- Mapping targets (which ontology each field should map to)
- Transform logic used in kg-microbe
- Semantic context and interpretation
- Workaround prefixes for unmapped terms

**Advantages:**
- ✅ Shows intended mappings and semantic interpretation
- ✅ Documents transform logic
- ✅ Includes workaround strategies

**Limitations:**
- ❌ May not cover ALL fields (curated subset)
- ❌ No frequency/distribution data
- ❌ Manual updates required

### Reconciliation Status

**Status:** ⏳ Planned (continuation of Issue #223)

**Strategy:**
- Use `bacdive_enum_values.tsv` as source of truth for BacDive controlled vocabularies
- Extract BacDive-attributed synonyms from METPO (`reports/synonym-sources.tsv`)
- Compare to find:
  - Values in BacDive missing from METPO
  - False claims (METPO synonyms not actually in BacDive)
- Focus on high-frequency paths (metabolite utilization, enzymes, oxygen tolerance)

---

## BactoTraits Dataset

### Native Format

**Source:** ORDaR institutional repository (University of Lorraine)
**File:** `BactoTraits_databaseV2_Jun2022.csv`
**Format:** **Hierarchical multi-row header CSV with one-hot encoding**

**File Properties:**
- Size: 8.6M
- Lines: 19,458 (19,455 strains + 3 header rows)
- Delimiter: **Semicolon** (`;` not comma)
- Encoding: UTF-8

### Native Format Description

**BactoTraits uses a hierarchical multi-row header CSV format with one-hot encoding for categorical traits.**

#### Key Characteristics:

1. **3-Row Header Structure:**
   ```
   Row 1: Trait categories (sparse - uses empty cells for continuation)
   Row 2: Units/metadata (%, Celsius degree, micrometer, etc.)
   Row 3: Specific field names (actual column identifiers)
   ```

2. **Header Organization Pattern:**
   - **Row 1 categories** use **forward-fill semantics**
   - Empty cells inherit the category from the previous non-empty cell
   - Example: `pH_Optimum;;;;` means the next 4 columns all belong to pH_Optimum category

3. **Categories (Row 1):**
   ```
   taxonomy, strain name, pH_Optimum, pH_Range, delta_pH, NaCl_Optimum, NaCl_Range,
   delta_NaCl, temp_Optimum, temp_Range, delta_temp, Oxygen, Gram, Motility, Spore,
   GC%, width, length, shape, TrophicType, Pigment
   ```

4. **Data Encoding:**
   - **Binary one-hot encoding** for categorical traits (0, 1, or NA)
   - Multiple related columns represent bins/categories of the same trait
   - Example: Oxygen preference encoded as 4 columns:
     - `Ox_anaerobic` (0 or 1)
     - `Ox_aerobic` (0 or 1)
     - `Ox_facultative_aerobe_anaerobe` (0 or 1)
     - `Ox_microerophile` (0 or 1)

5. **Field Naming Convention:**
   - **Prefix indicates category:**
     - `pHO_` = pH Optimum bins
     - `pHR_` = pH Range bins
     - `pHd_` = pH Delta bins
     - `NaO_` = NaCl Optimum bins
     - `NaR_` = NaCl Range bins
     - `Nad_` = NaCl Delta bins
     - `TO_` = Temperature Optimum bins
     - `TR_` = Temperature Range bins
     - `Td_` = Temperature Delta bins
     - `Ox_` = Oxygen preference
     - `G_` = Gram stain
     - `S_` = Cell Shape
     - `TT_` = Trophic Type
     - `GC_` = GC content bins
     - `W_` = Cell Width bins
     - `L_` = Cell Length bins
   - **Suffixes encode bins/ranges:** `0_to_6`, `<=42.65`, `>66.3`, `1_to_3`

#### Example Structure:

```csv
;;;taxonomy;;;;;;;strain name;pH_Optimum;;;;pH_Range;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;%;;;;;;;;
strain n°;Bacdive_ID;codes;Kingdom;Phylum;Class;...;Full_name;pHO_0_to_6;pHO_6_to_7;pHO_7_to_8;pHO_8_to_14;pHR_0_to_4;...
1;1;DSM 2002;Bacteria;Proteobacteria;...;Acetobacter aceti;NA;NA;NA;NA;NA;...
```

### Controlled Vocabularies in BactoTraits

The one-hot encoded columns represent these controlled vocabularies (~100 terms total):

| Category | Field Count | Values/Bins |
|----------|-------------|-------------|
| **pH Optimum** | 4 | 0_to_6, 6_to_7, 7_to_8, 8_to_14 |
| **pH Range** | 6 | 0_to_4, 4_to_6, 6_to_7, 7_to_8, 8_to_10, 10_to_14 |
| **pH Delta** | 6 | <=1, 1_2, 2_3, 3_4, 4_5, 5_9 |
| **NaCl Optimum** | 4 | <=1, 1_to_3, 3_to_8, >8 |
| **NaCl Range** | 4 | <=1, 1_to_3, 3_to_8, >8 |
| **NaCl Delta** | 4 | <=1, 1_3, 3_8, >8 |
| **Temp Optimum** | 7 | <=10, 10_to_22, 22_to_27, 27_to_30, 30_to_34, 34_to_40, >40 |
| **Temp Range** | 7 | <=10, 10_to_22, 22_to_27, 27_to_30, 30_to_34, 34_to_40, >40 |
| **Temp Delta** | 5 | 1_5, 5_10, 10_20, 20_30, >30 |
| **Oxygen** | 4 | anaerobic, aerobic, facultative_aerobe_anaerobe, microerophile |
| **Gram Stain** | 2 | negative, positive |
| **Motility** | 2 | motile, non-motile |
| **Spore Formation** | 2 | spore, no_spore |
| **GC Content** | 4 | <=42.65, 42.65_57.0, 57.0_66.3, >66.3 |
| **Cell Width** | 4 | <=0.5, 0.5_0.65, 0.65_0.9, >0.9 |
| **Cell Length** | 4 | <=1.3, 1.3_2, 2_3, >3 |
| **Cell Shape** | 6 | rod, sphere, curved_spiral, filament, ovoid, star_dumbbell_pleomorphic |
| **Trophic Type** | 9 | heterotroph, autotroph, organotroph, lithotroph, chemotroph, phototroph, copiotroph_diazotroph, methylotroph, oligotroph |
| **Pigment** | 10 | pink, yellow, brown, black, orange, white, cream, red, green, carotenoid |

### Why This Format?

This format is **designed for statistical/ecological analysis** rather than database storage:

- **One-hot encoding** makes it easy to compute correlations between traits
- **Binned numerical values** enable trait-based community analysis
- **Sparse binary matrix** structure is common in ecology/trait databases
- **Multi-row headers** provide metadata (units) alongside field names
- Optimized for tools like R, pandas, and statistical software

### Available Resources

#### 1. Original BactoTraits File (METPO repo)

**Location:** `/Users/MAM/Documents/gitrepos/metpo/downloads/BactoTraits_databaseV2_Jun2022.csv`

**Properties:**
- Size: 8.6M
- MD5: `e6bca5b947c1aa692d45ac24aa9025f3`
- Format: Semicolon-delimited with 3 header rows
- **Status: Unadulterated original** from ORDaR repository

#### 2. Header Reduction Code (kg-microbe repo)

**Location:** `/Users/MAM/Documents/gitrepos/kg-microbe/kg_microbe/bactotraits_to_mongo.py`

**Purpose:** Converts BactoTraits 3-row header CSV into MongoDB-compatible JSON with nested structure

**Key Functions:**

```python
def forward_fill_headers(header_row: List[str]) -> List[str]:
    """Forward fill empty cells in header row.

    Implements the forward-fill semantics of Row 1 categories.
    Empty cells inherit the value from the previous non-empty cell.
    """
    filled = []
    last_value = ""

    for cell in header_row:
        cell = cell.strip()
        if cell:
            last_value = cell
        filled.append(last_value)

    return filled

def create_field_path(category: str, field_name: str) -> str:
    """Create hierarchical field path from category and field name.

    Transforms flat column names into nested MongoDB paths.
    Examples:
        category="pH_Optimum", field="pHO_0_to_6" -> "ph.optimum.0_to_6"
        category="Oxygen", field="Ox_anaerobic" -> "oxygen.anaerobic"
        category="Gram", field="G_negative" -> "gram_stain.negative"
    """
    # ... 140 lines of field mapping logic
```

**Header Processing Steps:**

```python
# Lines 273-279: Parse 3-row headers
categories = next(reader)         # Row 1: categories (forward-fill these)
next(reader)                      # Row 2: units (skip completely)
field_names = next(reader)        # Row 3: actual field names

# Forward-fill the categories
filled_categories = forward_fill_headers(categories)

# For each data row, combine category + field_name to create hierarchical paths
for i, value in enumerate(row):
    field_name = field_names[i].strip()
    category = filled_categories[i].strip()
    field_path = create_field_path(category, field_name)
    # field_path examples: "ph.optimum.0_to_6", "oxygen.anaerobic", "gram_stain.negative"
```

**What the code does:**

1. **Reads 3 header rows** from semicolon-delimited CSV
2. **Forward-fills Row 1** (categories) - empty cells inherit from previous non-empty cell
3. **Skips Row 2** (units) completely
4. **Uses Row 3** as actual field names
5. **Combines categories + field names** into hierarchical MongoDB paths
6. **Parses values:**
   - Converts 0/1 to integers
   - Filters out 0 values (keeps only positive trait assignments)
   - Converts "NA" to null
7. **Outputs nested JSON** suitable for MongoDB

#### 3. Processed BactoTraits File (kg-microbe repo)

**Location:** `/Users/MAM/Documents/gitrepos/kg-microbe/kg_microbe/transform_utils/bactotraits/tmp/BactoTraits.tsv`

**Properties:**
- Size: 6.1M (smaller - removed units row, cleaned data)
- MD5: `879ddc0e22d81e35f6688618c448252b` (different from original)
- Format: **Tab-delimited with 1 header row** (categories merged into field names)
- Header example: `Bacdive_ID	ncbitaxon_id	culture collection codes	Kingdom	Phylum	...`

**Transformations applied:**
- ✅ Single header row (categories merged into field names)
- ✅ Tab-delimited instead of semicolon-delimited
- ✅ Added `ncbitaxon_id` column
- ✅ `Bacdive_ID` values prefixed with `bacdive:` (e.g., `bacdive:1`)
- ✅ Removed units row

**Note:** This processed version is specific to kg-microbe's MongoDB import workflow. For METPO reconciliation, we should use the original file.

### Reconciliation Status

**Status:** ⏳ Planned (continuation of Issue #223)

**Strategy:**
- Use original CSV with 3-row headers
- Borrow `forward_fill_headers()` function from kg-microbe for header parsing
- Extract all column headers (category + field combinations)
- Compare against METPO BactoTraits-attributed synonyms
- **Advantage:** One-hot encoding makes this simpler than BacDive
  - We just need to check if each column name has a corresponding METPO synonym
  - ~100 controlled vocabulary terms to check (vs 2,858 for BacDive)

---

## Reconciliation Strategy

### Completed: Madin (Issue #223)

**Implemented:** `src/scripts/reconcile_madin_coverage.py`

**Features:**
- Multiple modes: values, field_names, verify_synonyms, **integrated**
- Outputs structured YAML reports
- Special handling for comma-separated `pathways` field
- Field name exclusion from false claims detection
- MongoDB queries using pymongo
- Makefile integration: `make reconcile-madin`

**Integrated Report Structure:**
```yaml
madin_metpo_reconciliation:
  summary:
    total_fields: 35
    fields_with_name_mapping: 8
    fields_with_full_value_coverage: 7
    total_metpo_madin_synonyms: 70
    verified_synonyms: 62
    false_synonym_claims: 0
  fields:
    - field: cell_shape
      field_mapped: true
      field_metpo_id: METPO:1000666
      total_values: 19
      covered_values_count: 19
      value_coverage_percentage: 100.0
      covered_values: [...]
      missing_values: []
  high_value_unmapped_fields:
    - field: rRNA16S_genes
      unique_values: 17
  false_synonym_claims: []
```

### Planned: BacDive

**Data Source:**
- Primary: `bacphen-awareness` genson analysis
- Specifically: `bacdive_enum_values.tsv` (2,858 controlled vocabulary terms)

**Approach:**
1. Load BacDive-attributed synonyms from METPO (`synonym-sources.tsv` with source filter)
2. Load enumerated values from `bacdive_enum_values.tsv`
3. For each path in `bacdive_path_to_enum.tsv`:
   - Extract field name from JSON path
   - Check if field is mapped to METPO
   - For each value in `bacdive_enum_values.tsv` for that path:
     - Check if value has METPO synonym
     - Track coverage statistics
4. Generate integrated report similar to Madin

**Challenges:**
- **JSON path complexity:** Need to extract semantic field names from paths like `[].Physiology and metabolism.metabolite utilization.[].utilization activity`
- **High volume:** 2,858 controlled vocabulary terms vs 70 Madin synonyms
- **Polymorphic fields:** Some BacDive fields can be string, array, or object

**Advantages:**
- Genson analysis provides complete enumeration
- Frequency data helps prioritize (focus on high-count paths first)
- Can focus on specific sections (Oxygen tolerance, Cell morphology, etc.)

### Planned: BactoTraits

**Data Source:**
- Primary: Original CSV from METPO downloads
- Header processing: Borrow from kg-microbe `bactotraits_to_mongo.py`

**Approach:**
1. Parse 3-row header using `forward_fill_headers()`
2. Extract all column names (category + field combinations)
3. Load BactoTraits-attributed synonyms from METPO
4. For each one-hot encoded column:
   - Extract semantic term (e.g., "Ox_anaerobic" → "anaerobic" in "oxygen" category)
   - Check if term has METPO synonym
   - Track coverage for each category (pH, temp, oxygen, etc.)
5. Generate integrated report

**Advantages:**
- **Simpler than BacDive:** Only ~100 terms to check (vs 2,858)
- **Clear structure:** One-hot encoding means 1 column = 1 controlled vocabulary term
- **Reusable code:** Header parsing already implemented in kg-microbe

**Challenges:**
- **Multi-row headers:** Need to properly combine Row 1 + Row 3
- **Bin naming:** METPO may use different bin names (e.g., "0_to_6" vs "acidic")
- **Category semantics:** Need to handle category context (pH vs temp vs NaCl)

---

## Comparison Matrix

| Aspect | Madin | BacDive | BactoTraits |
|--------|-------|---------|-------------|
| **Format** | Flat CSV | Nested JSON | Multi-row header CSV |
| **Structure** | 1 header row | 10 sections, ~234 fields | 3 header rows, ~100 columns |
| **Delimiter** | Comma | N/A (JSON) | Semicolon |
| **Encoding** | Standard categorical | Mix of enums + free text | Binary one-hot |
| **Records** | ~170k strains | ~99k strains | ~19k strains |
| **Controlled Vocabs** | ~70 terms | ~2,858 terms | ~100 terms |
| **Access** | MongoDB | MongoDB | Local file |
| **Schema Docs** | Field lists in papers | Genson analysis (170K JSON Schema) | Multi-row headers encode schema |
| **Philosophy** | Flat table for R/pandas | Document store for flexibility | Statistical trait matrix |
| **Reconciliation** | ✅ Complete | ⏳ Planned | ⏳ Planned |
| **Complexity** | Low | High (nested paths) | Medium (header parsing) |

---

## Related GitHub Issues

### Completed

- **#223: round-trip assessment of METPO's coverage of our structured source's values** (CLOSED)
  - Implemented comprehensive Madin reconciliation
  - Created `reconcile_madin_coverage.py` with integrated mode
  - Generated `reports/madin-metpo-reconciliation.yaml`
  - Added Makefile target `make reconcile-madin`

- **#219: check in madin and bactotraits helpers in an appropriate directory** (CLOSED)
  - Documented helper code locations
  - Identified reusable components for reconciliation

- **#192: document the fact that madin, bacdive etc synonyms in the ROBOT sheet can contain paths to map from or values to map against** (CLOSED)
  - Established synonym attribution patterns
  - Documented in `synonym-sources.tsv` SPARQL query

### Open - Directly Related

- **#204: define quality metrics esp regarding how mappings are used in KG-Microbe** (OPEN)
  - Round-trip reconciliation provides key quality metrics
  - Metrics: field coverage %, value coverage %, false claim rate, high-value gaps

- **#227: report all (leaf?) terms that don't have any attributed synonyms** (OPEN)
  - Inverse of reconciliation: find METPO terms without source attribution
  - Helps identify terms that need synonym curation

### Open - Indirectly Related

- **#212: add grouping of the new classes restored from BactoTraits** (OPEN)
  - BactoTraits reconciliation will inform class organization

- **#211: Restore BactoTraits classes to production minimal_classes sheet** (OPEN)
  - Reconciliation will identify which BactoTraits values need METPO classes

- **#207: restore bacdive range classes to active classes google sheet** (OPEN)
  - BacDive reconciliation will identify which range classes are actually used

- **#209: use Bioportal API to validate synonyms and provide attribution** (OPEN)
  - Alternative validation approach to complement source-based reconciliation

- **#155: infer Bacdive JSON schema with genson** (OPEN)
  - Already completed in bacphen-awareness repo
  - Schema available for BacDive reconciliation

- **#152: continue making characteristics/phenotypes to align with Bacdive** (OPEN)
  - BacDive reconciliation will identify gaps in METPO phenotype coverage

- **#138: restore the script that makes a color coded NER coverage HTML** (OPEN)
  - Visualization tool for reconciliation results

---

## Next Steps

1. **Adapt Madin reconciliation script for BacDive**
   - Create `reconcile_bacdive_coverage.py`
   - Parse `bacdive_enum_values.tsv` from bacphen-awareness
   - Handle JSON path complexity
   - Generate integrated YAML report

2. **Adapt Madin reconciliation script for BactoTraits**
   - Create `reconcile_bactotraits_coverage.py`
   - Implement header parsing (borrow from kg-microbe)
   - Handle one-hot encoding semantics
   - Generate integrated YAML report

3. **Create unified Makefile targets**
   - `make reconcile-bacdive`
   - `make reconcile-bactotraits`
   - `make reconcile-all` (runs all three)

4. **Generate summary comparison report**
   - Cross-source term coverage
   - Shared vs unique terms
   - Priority gaps for METPO curation

5. **Create GitHub issue for BacDive/BactoTraits reconciliation**
   - Reference this documentation
   - Specify deliverables (scripts + reports)
   - Link to Issue #223 as template

---

## References

### Data Source Publications

- **Madin et al. (2020)** "A synthesis of bacterial and archaeal phenotypic trait data" *Scientific Data* 7, 170
  - https://www.nature.com/articles/s41597-020-0497-4

- **Reimer et al. (2022)** "BacDive in 2022: the knowledge base for standardized bacterial and archaeal data" *Nucleic Acids Research*
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC8728306/

- **Cébron et al. (2021)** "BactoTraits: A functional trait database to evaluate how natural and man-induced changes influence the assembly of bacterial communities" *Ecological Indicators*
  - https://ordar.otelo.univ-lorraine.fr/record?id=10.24396%2FORDAR-53

### Repository Documentation

- `docs/microbial_trait_datasets_background.md` - Overview of all three sources
- `docs/kg_microbe_complete_field_path_and_mapping_reference.md` - Field mappings in kg-microbe
- `docs/issue_223_insights_and_questions.md` - Madin reconciliation insights
- `src/sparql/synonym-sources.sparql` - SPARQL query to extract source-attributed synonyms

### External Resources

- Madin GitHub: https://github.com/jmadin/bacteria_archaea_traits
- BacDive API: https://api.bacdive.dsmz.de/
- BactoTraits ORDaR: https://ordar.otelo.univ-lorraine.fr/record?id=10.24396%2FORDAR-53
- kg-microbe: https://github.com/Knowledge-Graph-Hub/kg-microbe
- bacphen-awareness: Contains genson schema analysis for BacDive
