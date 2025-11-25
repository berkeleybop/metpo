# KG-Microbe Mapping Resources Audit

**Date**: 2025-11-20
**Concern**: Multiple mapping resources in various formats with unclear provenance and reliability

---

## Executive Summary

KG-Microbe has **7 distinct mapping resources** in 4 different formats serving different purposes. The most critical resource (`bacdive_mappings.tsv`) appears to be **manually curated** with no clear documentation of its provenance, raising significant reliability concerns.

### Key Findings:

🚨 **CRITICAL GAPS**:
1. **No public API→CHEBI→EC mapping database exists** - this is manual curation work
2. **bacdive_mappings.tsv provenance unknown** - 370 rows, unclear who/how/when created
3. **Source CSV files missing** - notebook references `data/raw/bacdive/*.csv` but files don't exist in repo
4. **No validation or QC documented** - unclear how accurate the mappings are

✅ **RELIABLE**:
- `chemical_mappings.tsv` (17K rows) - mostly from KEGG Compound (public database)
- METPO sheet mappings - version controlled, systematic

⚠️ **CONCERNS**:
- Mix of manual curation vs. systematic extraction
- No clear quality control process
- Missing source data for critical mappings

---

## Complete Mapping Resource Inventory

### 1. **bacdive_mappings.tsv** ⚠️ PROVENANCE UNCLEAR

**Location**: `kg_microbe/transform_utils/bacdive/tmp/bacdive_mappings.tsv`
**Size**: 370 rows
**Format**: TSV with 8 columns

**Columns**:
```
CHEBI_ID | substrate | KEGG_ID | CAS_RN_ID | EC_ID | enzyme | pseudo_CURIE | reaction_name
```

**Example**:
```tsv
CHEBI:16828  L-tryptophan  KEGG:C00078  CAS-RN:73-22-3  EC:4.1.99.1  tryptophanase  assay:API_20A_IND  Indole production
```

**Created by**: `notebooks/bacdive_mapping_resource.ipynb`

**Source data**: References 15 CSV files that should be in `data/raw/bacdive/`:
- `kit_api_20A_meta.csv`
- `kit_api_20E_meta.csv`
- `kit_api_20NE_meta.csv`
- `kit_api_20STR_meta.csv`
- `kit_api_50CHas_meta.csv`
- `kit_api_CAM_meta.csv`
- `kit_api_coryne_meta.csv`
- `kit_api_ID32E_meta.csv`
- `kit_api_ID32STA_meta.csv`
- `kit_api_LIST_meta.csv`
- `kit_api_NH_meta.csv`
- `kit_api_rID32A_meta.csv`
- `kit_api_rID32STR_meta.csv`
- `kit_api_STA_meta.csv`
- `kit_api_zym_ec.csv`

**❌ PROBLEM**: These CSV files **do not exist in the repository**!

**Coverage**: Maps API test abbreviations to semantic IDs
- CHEBI IDs: Present for ~80% of tests
- EC numbers: Present for ~30% of tests (enzyme-based tests only)
- KEGG IDs: Present for ~80%
- CAS numbers: Present for ~80%

**Current Usage**: Creates `chemical → occurs_in → assay` edges only (underutilized)

**Quality**: Unknown - no validation documented

**Questions**:
- Who created the source CSV files?
- When were they created?
- What was the curation methodology?
- How accurate are the mappings?
- Where are the source CSV files stored?
- Is this being version controlled anywhere?

---

### 2. **chemical_mappings.tsv** ✅ MOSTLY RELIABLE

**Location**: `kg_microbe/mappings/chemical_mappings.tsv`
**Size**: 17,294 rows
**Format**: TSV with 6 columns

**Columns**:
```
original_term | term_source | chebi_id | chebi_label | chebi_formula | mapping_quality
```

**Sources**:
- **kegg_compound**: 16,808 rows (97%) - HIGH quality
- **bacdive_metabolite**: 196 rows (1%) - HIGH quality
- **chemicals_sssom**: 193 rows (1%) - MEDIUM quality
- **bacdive_api**: 89 rows (0.5%) - HIGH quality
- **madin_etal_manual**: 7 rows (0.04%) - HIGH quality

**Quality Distribution**:
- High: 17,100 rows (99%)
- Medium: 193 rows (1%)

**Provenance**:
- ✅ KEGG Compound is a public database
- ✅ SSSOM is standard ROBOT mapping format
- ⚠️ bacdive_api and bacdive_metabolite sources unclear

**Current Usage**: General chemical name → CHEBI lookup

**Assessment**: **MOSTLY RELIABLE** - dominated by public database (KEGG)

---

### 3. **chemical_mappings_mismatches.tsv**

**Location**: `kg_microbe/mappings/chemical_mappings_mismatches.tsv`
**Size**: 10 rows
**Purpose**: Documents problematic mappings that need review

**Example**:
```tsv
NA  chemicals_sssom  CHEBI:26708  sodium atom  medium  na  sodium atom
NA  chemicals_sssom  CHEBI:29101  sodium(1+)   medium  na  sodium1
```

**Assessment**: QC artifact, useful for tracking issues

---

### 4. **metabolite_mapping.json** ✅ RELIABLE

**Location**: `kg_microbe/transform_utils/bacdive/metabolite_mapping.json`
**Size**: 140+ entries
**Format**: JSON dict

**Purpose**: Maps antibiotic CHEBI IDs to common names

**Example**:
```json
{
  "CHEBI:17334": "penicillin G",
  "CHEBI:46195": "gentamicin"
}
```

**Provenance**: ⚠️ Unknown - appears manually curated

**Current Usage**: ✅ Well-utilized in antibiotic resistance edges

**Assessment**: **RELIABLE** - antibiotics are well-characterized compounds

---

### 5. **cas-rn_map.txt**

**Location**: `kg_microbe/transform_utils/bacdive/cas-rn_map.txt`
**Size**: 829KB
**Format**: Text file

**Purpose**: CAS Registry Number mappings

**Provenance**: ⚠️ Unknown

**Current Usage**: ✅ Well-utilized

**Assessment**: CAS numbers are from Chemical Abstracts Service (reliable), but extraction method unclear

---

### 6. **BactoTraits_mapping.tsv**

**Location**: `kg_microbe/transform_utils/bactotraits/tmp/BactoTraits_mapping.tsv`
**Size**: 32,264 rows
**Format**: TSV

**Columns**:
```
Bacdive_ID | culture_collection_number | ncbitaxon_id
```

**Purpose**: Maps BactoTraits strain IDs to BacDive and NCBITaxon

**Provenance**: Generated from BactoTraits data processing

**Assessment**: **RELIABLE** - systematic extraction from BactoTraits

---

### 7. **metpo_sheet.tsv** ✅ RELIABLE

**Location**: `metpo/src/templates/metpo_sheet.tsv` (also remote URL)
**Remote**: `https://raw.githubusercontent.com/berkeleybop/metpo/refs/tags/2025-10-31/src/templates/metpo_sheet.tsv`
**Format**: ROBOT template TSV

**Purpose**: Maps BacDive/BactoTraits/Madin values → METPO terms

**Key Columns**:
- `bacdive keyword synonym` - for General.keywords
- `bactotraits related synonym` - for BactoTraits columns
- `madin synonym or field` - for Madin data

**Provenance**: ✅ Version controlled in METPO repository, curated by ontology team

**Known Issue**: Normalization bug (spaces/hyphens not handled)

**Assessment**: **RELIABLE** - systematic ontology development process

---

## Public API Test Mapping Resources

### What's Available Publicly?

I searched for public databases mapping API biochemical tests to semantic ontologies. **Result: NOTHING comprehensive exists publicly.**

**What I found**:

#### 1. BRENDA Enzyme Database ✅ Public, High Quality
- **URL**: https://www.brenda-enzymes.org/
- **Coverage**: Comprehensive enzyme data (EC numbers, substrates, products, kinetics)
- **Size**: 79,000+ literature references, manually curated
- **Access**: Free worldwide
- **Limitations**:
  - Does NOT directly map API test abbreviations
  - Need to know enzyme name or EC number first
  - Would require manual lookup: "API 20E ONPG test" → β-galactosidase → EC:3.2.1.23 → search BRENDA

**How BRENDA could help**:
- Validate EC numbers in bacdive_mappings.tsv
- Find missing substrate CHEBI IDs
- But requires manual work per test

---

#### 2. ChEBI Database ✅ Public, High Quality
- **URL**: https://www.ebi.ac.uk/chebi/
- **Coverage**: 46,500+ chemical entities
- **API**: Yes (libChEBI in Java, Python, MATLAB)
- **Limitations**:
  - Chemical entities only, not assays
  - No connection to API test system
  - Good for validating CHEBI IDs we already have

---

#### 3. API Test Documentation 📚 Public, But Not Structured Data
- **Available**: Microbiological test interpretation guides
- **Examples**:
  - Wikipedia: Analytical Profile Index
  - Microbe Online tutorials
  - bioMérieux product inserts
- **Format**: Human-readable text, PDFs
- **NOT Available**: Structured database with CHEBI/EC mappings

---

### The Gap: API → Ontology Mappings

**Bottom line**: There is **NO public database** that directly maps:
```
API test abbreviation → (EC number, CHEBI substrate, KEGG, CAS)
```

**This means**:
1. The work in `bacdive_mappings.tsv` is **original curation**
2. Someone (unknown) did manual work to create these mappings
3. This is **valuable intellectual work** that should be:
   - Documented
   - Validated
   - Version controlled
   - Ideally published/shared publicly

**Similar situation for**:
- Fatty acid notation → CHEBI mappings (none public)
- Culture media names → OBI terms (partial)
- Isolation sources → ENVO terms (partial via GOLD)

---

## Notebooks vs. Transform Code

### Role of Notebooks in kg-microbe

**Total notebooks**: 10

**Purposes**:

1. **Exploration** (4 notebooks):
   - `BacDive-exploration.ipynb`
   - `MergedKG_exploration.ipynb`
   - `kg_microbe_summary.ipynb`
   - `feba.ipynb`

2. **Mapping generation** (1 notebook):
   - `bacdive_mapping_resource.ipynb` ← Creates bacdive_mappings.tsv

3. **Analysis/Visualization** (3 notebooks):
   - `get_taxa_features.ipynb`
   - `pivot-merged-kg-edges-NCBITaxon.ipynb`
   - `test-pivot-kg-subset.ipynb`

4. **External data processing** (2 notebooks):
   - `bacdive-api-test.ipynb` - Testing BacDive API access
   - `metacyc_pathway_hierarchy.ipynb` - MetaCyc pathway processing

**Pattern**: Notebooks are for:
- ✅ Exploratory data analysis
- ✅ One-time data extraction/transformation
- ✅ Visualization
- ❌ NOT for production transforms (those are in `kg_microbe/transform_utils/`)

---

### Core Python Code (Beyond Transforms)

**Main modules**:
- `kg_microbe/run.py` - Pipeline orchestration
- `kg_microbe/download.py` - Data fetching
- `kg_microbe/query.py` - KG querying
- `kg_microbe/merge_utils/merge_kg.py` - Merge multiple sources

**Utility modules** (`kg_microbe/utils/`):
- `mapping_file_utils.py` ← Loads METPO mappings
- `oak_utils.py` - Ontology access via OAK
- `ner_utils.py` - Named Entity Recognition
- `pandas_utils.py` - DataFrame operations
- `sanitize_curies.py` - CURIE validation
- `ontology_utils.py` - Ontology operations
- `download_bacdive.py` - BacDive API client
- `robot_utils.py` - ROBOT template processing
- Several more specialized utils

**Transform code** (`kg_microbe/transform_utils/`):
- `bacdive/bacdive.py` - BacDive transform (2K lines)
- `bactotraits/bactotraits.py` - BactoTraits transform
- `madin/phenotype_term_mapping.py` - Madin NER transform

**Total architecture**:
- Production transforms: Structured Python modules in `transform_utils/`
- Utilities: Reusable functions in `utils/`
- Notebooks: One-off analysis, exploration, manual curation
- Mapping files: Mix of generated (bacdive_mappings.tsv) and manual (metabolite_mapping.json)

---

## Mapping Reliability Assessment

### High Confidence (✅ Reliable)

**1. KEGG-based mappings** (16,808 rows)
- Source: Public KEGG Compound database
- Quality: High (manually curated by KEGG team)
- Validation: KEGG is well-established, widely used

**2. METPO sheet mappings**
- Source: Version-controlled ontology development
- Quality: High (systematic curation process)
- Known issue: Normalization bug (fixable)

**3. Antibiotic mappings** (metabolite_mapping.json)
- Source: Unknown, but antibiotics are well-characterized
- Quality: Likely high (easy to validate)
- Size: Only 140 compounds (manageable to review)

---

### Medium Confidence (⚠️ Needs Validation)

**1. bacdive_mappings.tsv** (370 rows) ← **BIGGEST CONCERN**
- Source: **UNKNOWN** - CSV files not in repo
- Creator: **UNKNOWN**
- Methodology: **UNKNOWN**
- Validation: **NONE DOCUMENTED**
- Last updated: **UNKNOWN**

**Concerns**:
- Missing source data
- No documentation of curation process
- No validation against BRENDA or other authorities
- Some entries missing EC numbers (expected for non-enzyme tests)
- Some entries missing CHEBI IDs (problematic)

**How to validate**:
1. Check EC numbers against BRENDA
2. Check CHEBI IDs against ChEBI database
3. Check KEGG IDs against KEGG API
4. Cross-reference CAS numbers
5. Review enzyme names for accuracy

**Example potential issues** (need to check):
- Line with `EC:1.9.3.1` - Is this cytochrome c oxidase? (BRENDA check needed)
- Lines with no CHEBI ID - Can we find them in ChEBI?
- Lines with no EC number for enzyme tests - Should they have one?

---

### Low Confidence / Unknown (❓ Unclear)

**1. CAS-RN map** (cas-rn_map.txt)
- Source: Unknown
- Size: 829KB (thousands of entries)
- Validation: None documented
- CAS numbers are authoritative when correct, but extraction method unknown

**2. chemicals_sssom** (193 rows, medium quality)
- Source: SSSOM format suggests ROBOT-generated
- Marked as "medium" quality in file itself
- 10 mismatches documented separately
- Needs review

---

## Noise Sources and Quality Concerns

### What Could Cause Mapping Errors?

#### 1. **Manual Entry Errors**
- Typos in CHEBI IDs
- Wrong EC number association
- Copy-paste errors
- Example: If `EC:1.9.3.1` should be `EC:1.9.3.-` (family not specific enzyme)

#### 2. **Ambiguous Test Names**
- API tests can detect multiple activities
- Example: "ONPG" specifically tests β-galactosidase, but enzyme could act on other substrates
- Mapping one test → one enzyme may oversimplify

#### 3. **Database Drift**
- CHEBI IDs can be deprecated/merged
- EC numbers can be reclassified
- KEGG entries can be updated
- When were mappings created? Are they current?

#### 4. **Incomplete Mappings**
- Not all tests have enzymes (e.g., acid production from sugars)
- Not all substrates have CHEBI IDs (especially older compounds)
- Missing data ≠ wrong data, but creates coverage gaps

#### 5. **Normalization Mismatches**
- We know METPO has space/hyphen normalization bug
- Could similar issues affect other mappings?
- Example: "D-glucose" vs "D glucose" vs "D_glucose"

---

### How to Assess Reliability

**Systematic validation checklist**:

1. **Check EC numbers in BRENDA**:
   ```python
   # For each EC number in bacdive_mappings.tsv
   # Query BRENDA API or web interface
   # Verify enzyme name matches
   # Check if substrate is listed
   ```

2. **Validate CHEBI IDs**:
   ```python
   from oaklib import get_adapter
   oak = get_adapter("sqlite:obo:chebi")
   for chebi_id in mappings['CHEBI_ID']:
       # Check if ID exists
       # Check if ID is current (not obsolete)
       # Verify label matches
   ```

3. **Cross-reference multiple IDs**:
   - If have CHEBI, KEGG, CAS for same compound, do they all refer to same chemical?
   - KEGG API can return CHEBI ID for comparison

4. **Literature review**:
   - For enzyme tests, check at least one paper using that API test
   - Verify interpretation (e.g., "ONPG test detects β-galactosidase")

5. **bioMérieux documentation**:
   - Request product inserts for API kits
   - Compare our interpretations to manufacturer specs

---

## Critical Questions Needing Answers

### About bacdive_mappings.tsv (URGENT):

1. **Who created the source CSV files** (`kit_api_*_meta.csv`)?
2. **When were they created?**
3. **What was the methodology?** (Manual curation? Scraped from where?)
4. **Where are the source files?** (Not in git repo - separate storage?)
5. **Has anyone validated these mappings?**
6. **Are they current?** (CHEBI/EC numbers up to date?)
7. **Should this be published?** (If original work, could be a data paper)

### About other mappings:

8. **Who maintains metabolite_mapping.json?**
9. **Where did cas-rn_map.txt come from?**
10. **What is the update/review process for all mappings?**

---

## Recommendations

### Immediate Actions

1. **Locate source CSV files** for bacdive_mappings.tsv
   - Check with team members
   - Search other repos/drives
   - If lost, document what notebook does

2. **Document provenance** for ALL mapping files
   - Add README in `mappings/` directory
   - Include: source, creator, date, methodology, validation status

3. **Validate critical mappings**:
   - Priority 1: bacdive_mappings.tsv (370 rows, manageable to review)
   - Check 20-30 random entries against BRENDA/ChEBI
   - Document any errors found

4. **Version control mapping updates**:
   - Clear git commit messages when mappings change
   - Include justification for changes
   - Track who reviewed/approved

### Short-Term

5. **Create mapping validation pipeline**:
   ```python
   # Script to validate mappings.tsv files
   # - Check IDs exist in source ontologies
   # - Flag deprecated IDs
   # - Cross-reference multiple IDs for same compound
   # - Generate QC report
   ```

6. **Publish mapping work**:
   - If bacdive_mappings is original curation, consider publishing as:
     - Data paper (Journal of Cheminformatics, Scientific Data)
     - Zenodo dataset with DOI
     - Contribution back to bioMérieux/community

7. **Establish mapping update process**:
   - Quarterly review of mappings
   - Check for deprecated ontology terms
   - Update based on new BRENDA/ChEBI releases

### Long-Term

8. **Public API mapping database**:
   - Could create community resource
   - API tests → EC, CHEBI, KEGG mappings
   - Would benefit entire microbiology community

9. **Automated validation**:
   - CI/CD checks on mapping file changes
   - Ontology term existence checks
   - Cross-reference validation

10. **Standardize formats**:
    - All mapping files use consistent TSV format
    - Standard columns: source_term, source_id, target_ontology, target_id, mapping_quality, curator, date

---

## Public Resources Available for Validation

### ✅ Can Use for Validation:

1. **BRENDA** (https://www.brenda-enzymes.org/)
   - Validate EC numbers
   - Check enzyme-substrate relationships
   - Free, no authentication required

2. **ChEBI** (https://www.ebi.ac.uk/chebi/)
   - Validate CHEBI IDs
   - Check for obsolete terms
   - API available via OAK

3. **KEGG** (https://www.genome.jp/kegg/)
   - Validate KEGG Compound IDs
   - Cross-reference CHEBI IDs
   - REST API available

4. **CAS Common Chemistry** (https://commonchemistry.cas.org/)
   - Validate CAS Registry Numbers
   - Free for up to 50 lookups/day
   - Limited but useful for spot checks

5. **ExplorEnz** (https://www.enzyme-database.org/)
   - Alternative enzyme database
   - Can cross-check BRENDA results

### ❌ NOT Available:

- Direct API test → ontology mapping database
- Standardized fatty acid notation → CHEBI mappings
- Comprehensive culture media → OBI mappings

---

## Summary Assessment

### What We Know:

✅ **Reliable**:
- KEGG-based chemical mappings (17K rows)
- METPO mappings (with known normalization bug to fix)
- Antibiotic mappings (small, easy to validate)

⚠️ **Concerning**:
- **bacdive_mappings.tsv provenance completely unknown**
- Source CSV files missing from repository
- No documented validation process
- Could contain errors we're propagating into KG

❓ **Unknown**:
- CAS-RN map source
- metabolite_mapping.json creator
- Update/maintenance process for any mappings

### What We Need:

🎯 **Urgent**:
1. Find or document source of bacdive_mappings.tsv
2. Validate at least sample of entries
3. Document provenance for all mapping files

📊 **Important**:
4. Create validation pipeline
5. Establish maintenance process
6. Consider publishing as community resource

🔬 **Future**:
7. Build public API test mapping database
8. Automate validation in CI/CD
9. Standardize formats across all mappings

---

## Related Issues

- Issue #25: Chemical-Enzyme Interactions Gap Analysis
- Issue #22: BacDive Ingestion Lifecycle
- (New issue needed): Mapping Resource Provenance and Validation

---

**Don't forget about helping Luke report the auto-prefix grounding failures!** 😊
