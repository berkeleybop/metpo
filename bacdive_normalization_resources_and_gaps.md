# BacDive Normalization Resources and Gaps Analysis

**Date**: 2025-11-20
**Focus**: Understanding API assays, existing helper files, and holistic normalization opportunities

---

## Executive Summary

**Good News**: KG-Microbe already has excellent normalization resources that are **partially used** but **not fully leveraged**:
- ✅ **`bacdive_mappings.tsv`**: 370 API tests mapped to CHEBI, EC, CAS, KEGG
- ✅ **`metabolite_mapping.json`**: 140+ antibiotics mapped to CHEBI
- ✅ **`cas-rn_map.txt`**: 829KB CAS number mappings

**Problem**: These mappings create **chemical-to-assay edges** but **NOT organism-to-enzyme-to-chemical edges**

**Gap**: The system uses ad-hoc `assay:` nodes as intermediaries instead of direct semantic relationships

---

## API Assays: Background

### What is API?

**API** = **Analytical Profile Index**
- **Manufacturer**: bioMérieux (originally Analytab Products Inc., 1970s)
- **Inventor**: Pierre Janin
- **Purpose**: Rapid bacterial identification via biochemical tests
- **Format**: Plastic strips with 20-50 miniature test chambers
- **Usage**: Universal in clinical and research microbiology labs worldwide

### How API Works

1. **Strip contains dehydrated biochemical tests**
2. **Inoculate with bacterial culture**
3. **Incubate (typically 18-24 hours)**
4. **Read color changes** (positive/negative)
5. **Convert to numerical profile** (7-digit code)
6. **Look up in database** (APIWEB software identifies >700 species)

### API Test Kits Available

From BacDive data, **16 different API systems**:

| Kit Name | Tests | Target Organisms | Common Use |
|----------|-------|------------------|------------|
| **API 20E** | 20 | Enterobacteriaceae (gram-negative) | Most common, clinical labs |
| **API 20A** | 20 | Anaerobes | Anaerobic infections |
| **API 20NE** | 20 | Non-enteric gram-negatives | Environmental bacteria |
| **API 20STR** | 20 | Streptococci | Strep throat, etc. |
| **API 50CHas** | 50 | Carbohydrate fermentation | Lactic acid bacteria |
| **API 50CHac** | 50 | Carbohydrate acidification | Yeasts |
| **API zym** | 19 | Enzyme activities | General enzymology |
| **API ID32E** | 32 | Enterobacteriaceae (extended) | Research labs |
| **API ID32STA** | 32 | Staphylococcus | Staph infections |
| **API NH** | 12 | Haemophilus/Neisseria | Respiratory pathogens |
| **API STA** | 10 | Staphylococcus (basic) | Quick staph ID |
| **API coryne** | 20 | Corynebacterium | Skin bacteria |
| **API rID32A** | 32 | Anaerobes (rapid) | Fast anaerobe ID |
| **API rID32STR** | 32 | Streptococci (rapid) | Fast strep ID |
| **API CAM** | 32 | Campylobacter | Food poisoning bacteria |
| **API LIST** | 10 | Listeria | Food safety |

### API Test Abbreviations Explained

**Three-letter codes** are biochemical test abbreviations:

#### Common Tests (from bacdive_mappings.tsv):

| Abbreviation | Full Name | What It Tests | Enzyme/Process |
|--------------|-----------|---------------|----------------|
| **ONPG** | o-Nitrophenyl-β-D-galactopyranoside | β-galactosidase activity | EC:3.2.1.23 |
| **ADH** | Arginine DiHydrolase | Arginine decarboxylation | EC:3.5.3.6 |
| **LDC** | Lysine DeCarboxylase | Lysine decarboxylation | EC:4.1.1.18 |
| **ODC** | Ornithine DeCarboxylase | Ornithine decarboxylation | EC:4.1.1.17 |
| **CIT** | Citrate | Citrate utilization | Citrate permease |
| **H2S** | Hydrogen Sulfide | H2S production | Various sulfur metabolism |
| **URE** | Urease | Urea hydrolysis | EC:3.5.1.5 |
| **TDA** | Tryptophan DeAminase | Tryptophan deamination | EC:4.1.99.1 |
| **IND** | Indole | Indole production from tryptophan | EC:4.1.99.1 (tryptophanase) |
| **VP** | Voges-Proskauer | Acetoin production | 2,3-butanediol pathway |
| **GEL** | Gelatinase | Gelatin hydrolysis | EC:3.4.24.* (metalloproteases) |
| **GLU** | Glucose | Acid from glucose fermentation | Various glycolysis enzymes |
| **MAN** | Mannitol | Acid from mannitol fermentation | Mannitol dehydrogenase |
| **INO** | Inositol | Acid from inositol fermentation | Inositol oxygenase |
| **SOR** | Sorbitol | Acid from sorbitol fermentation | Sorbitol dehydrogenase |
| **RHA** | Rhamnose | Acid from rhamnose fermentation | L-rhamnose isomerase |
| **SAC** | Saccharose (sucrose) | Acid from sucrose fermentation | Invertase |
| **MEL** | Melibiose | Acid from melibiose fermentation | α-galactosidase |
| **AMY** | Amygdalin | Amygdalin hydrolysis | β-glucosidase |
| **ARA** | Arabinose | Acid from arabinose fermentation | L-arabinose isomerase |

**Pattern**: Most abbreviations are first 3 letters of substrate/enzyme name

### Documentation Available

**Official Sources**:
1. ✅ **bioMérieux Product Pages**: https://www.biomerieux.com/clinical/api
2. ✅ **Package Inserts**: PDF instruction manuals for each kit
3. ✅ **APIWEB Database**: Proprietary software with interpretation tables
4. ✅ **Scientific Literature**: Thousands of papers use API strips
5. ✅ **BacDive Data**: Contains test results from API strips in structured format

**Proprietary Aspects**:
- ⚠️ **Database is proprietary**: APIWEB numerical profile → species identification
- ✅ **Test chemistry is published**: What each test measures is documented
- ✅ **No single owner barrier**: Chemical reactions are standard biochemistry
- ✅ **Open databases exist**: EC numbers, CHEBI IDs for substrates/enzymes are public

**Our Advantage**: We don't need the APIWEB identification database - we already have NCBITaxon IDs! We just need the test → enzyme/substrate mappings, which are available.

---

## Existing Normalization Resources in KG-Microbe

### 1. bacdive_mappings.tsv

**Location**: `kg_microbe/transform_utils/bacdive/tmp/bacdive_mappings.tsv`
**Size**: 370 rows (API tests)
**Created by**: `notebooks/bacdive_mapping_resource.ipynb`
**Source**: Multiple CSV files (one per API kit) → combined

**Columns**:
- `CHEBI_ID`: Chemical identifier for substrate
- `substrate`: Human-readable substrate name
- `KEGG_ID`: KEGG compound identifier
- `CAS_RN_ID`: CAS Registry Number
- `EC_ID`: Enzyme Commission number
- `enzyme`: Enzyme name
- `pseudo_CURIE`: Ad-hoc identifier (e.g., `assay:API_20E_ONPG`)
- `reaction_name`: Description

**Example Row**:
```tsv
CHEBI:16828  L-tryptophan  KEGG:C00078  CAS-RN:73-22-3  EC:4.1.99.1  tryptophanase  assay:API_20A_IND  Indole production
```

**Coverage**:
- ✅ 370 API tests mapped
- ✅ CHEBI IDs present for most substrates
- ✅ EC numbers present for enzyme tests (~100 tests)
- ⚠️ Some tests lack EC numbers (fermentation tests)
- ⚠️ Some tests lack CHEBI IDs (complex substrates)

**Current Usage**:
- ✅ **Chemical → Assay edges**: `CHEBI:16828 → occurs_in → assay:API_20A_IND`
- ✅ **CAS → Assay edges**: `CAS-RN:73-22-3 → occurs_in → assay:API_20A_IND`
- ❌ **NOT used for**: Organism → EC number edges
- ❌ **NOT used for**: EC → CHEBI edges

**Problem**: Creates **assay nodes as intermediaries** instead of direct semantic relationships

---

### 2. metabolite_mapping.json

**Location**: `kg_microbe/transform_utils/bacdive/metabolite_mapping.json`
**Size**: 140+ entries
**Purpose**: Map CHEBI IDs to metabolite names (mainly antibiotics)

**Example Content**:
```json
{
    "CHEBI:3770": "co-trimoxazole",
    "CHEBI:71415": "nitrofurantoin",
    "CHEBI:2637": "amikacin",
    "CHEBI:28971": "ampicillin"
}
```

**Coverage**: Antibiotic resistance/sensitivity testing compounds

**Current Usage**:
- ✅ Used in antibiotic resistance processing
- ✅ Maps CHEBI IDs from BacDive antibiotic data to names

**Status**: ✅ **Well-utilized**

---

### 3. cas-rn_map.txt

**Location**: `kg_microbe/transform_utils/bacdive/cas-rn_map.txt`
**Size**: 829KB
**Purpose**: CAS Registry Number mappings

**Format**: Text file with CAS number → identifier mappings

**Current Usage**:
- ✅ Creates CAS-RN nodes
- ✅ Links CAS numbers to assays

**Status**: ✅ **Well-utilized** for what it does

---

### 4. METPO Mappings (Remote)

**Source**:
- `https://raw.githubusercontent.com/berkeleybop/metpo/refs/tags/2025-10-31/src/templates/metpo_sheet.tsv`
- `https://raw.githubusercontent.com/berkeleybop/metpo/refs/tags/2025-10-31/src/templates/metpo-properties.tsv`

**Loaded by**: `kg_microbe/utils/mapping_file_utils.py:load_metpo_mappings()`

**Column used**: `bacdive keyword synonym`

**Coverage**: 60+ METPO phenotype terms mapped to BacDive keywords

**Current Usage**:
- ✅ Keyword-based phenotype mapping
- ✅ Path-based METPO extraction (6 paths)

**Status**: ✅ **Well-utilized** for phenotypes

---

### 5. translation_table.yaml

**Location**: `kg_microbe/transform_utils/translation_table.yaml`
**Size**: ~32KB

**Purpose**: General string normalization and value mapping

**Current Usage**: Various string transformations

**Status**: ✅ **Utilized**

---

### 6. custom_curies.yaml

**Location**: `kg_microbe/transform_utils/custom_curies.yaml`
**Size**: ~18KB

**Purpose**: Define custom prefixes when standard ontologies don't exist

**Example**:
```yaml
production:
  methane_production:
    curie: "production:methane"
    name: "methane production"
    category: "biolink:ChemicalSubstance"
    predicate: "biolink:produces"
```

**Current Usage**:
- Pigment production
- Pathogenicity
- Quantitative ranges (pH, temperature, NaCl)

**Status**: ✅ **Appropriate use** for non-semantic ranges

---

## Current State: How API Data Flows Through KG-M

### Data Flow Diagram

```
BacDive JSON
  └─ API test results: {"ONPG": "+", "ADH": "-", ...}
      ↓
bacdive.py (lines 1610-1655)
  └─ Creates assay nodes for "+" results only
      ↓
Nodes: assay:API_20E_ONPG
  ├─ category: biolink:PhenotypicQuality
  └─ name: "API 20E - ONPG"
      ↓
Edges (from bacdive_mappings.tsv):
  ├─ CHEBI:75055 → occurs_in → assay:API_20E_ONPG
  ├─ CAS-RN:369-07-3 → occurs_in → assay:API_20E_ONPG
  └─ assay:API_20E_ONPG → assesses → NCBITaxon:12345
```

### What's Missing

**The mappings file contains EC numbers and CHEBI IDs but they're NOT being used for direct edges!**

**Should create**:
```
NCBITaxon:12345 → capable_of → EC:3.2.1.23 (β-galactosidase)
EC:3.2.1.23 → consumes → CHEBI:75055 (ONPG substrate)
```

**Currently creates**:
```
assay:API_20E_ONPG → assesses → NCBITaxon:12345
CHEBI:75055 → occurs_in → assay:API_20E_ONPG
```

**Result**: Disconnected graph - can't traverse from organism → enzyme → substrate!

---

## Nodes and Edges File Analysis

### Assay Nodes

**From nodes.tsv**:
```tsv
id                              category                   name
assay:API_zym_Trypsin          biolink:PhenotypicQuality  API zym - Trypsin
assay:API_20E_ONPG             biolink:PhenotypicQuality  API 20E - ONPG
assay:API_20NE_URE             biolink:PhenotypicQuality  API 20NE - URE
```

**Characteristics**:
- ✅ All have `name` field (human-readable)
- ❌ Category is too generic (`PhenotypicQuality` vs. `MolecularActivity`)
- ❌ No definition
- ❌ No mapping to external ontologies
- ❌ Ad-hoc prefix

**Count**: 511 assay nodes

---

### Assay Edges

**Chemical → Assay**:
```tsv
subject              predicate            object                     relation    source
CHEBI:16828          biolink:occurs_in    assay:API_20A_IND         RO:0000056  bacdive_mappings.tsv
CAS-RN:73-22-3       biolink:occurs_in    assay:API_20A_IND         RO:0000056  bacdive_mappings.tsv
```

**Assay → Organism**:
```tsv
subject              predicate           object          relation    source
assay:API_20E_ONPG   biolink:assesses    NCBITaxon:562  RO:0000053  bacdive:12345
```

**Problem**: Two-hop path with non-semantic intermediate node

**What we want**: One-hop semantic paths:
```tsv
NCBITaxon:562        biolink:capable_of  EC:3.2.1.23    RO:0002215  bacdive:12345
EC:3.2.1.23          biolink:consumes    CHEBI:75055    RO:0000057  bacdive_mappings.tsv
```

---

## Other Normalization Gaps

### 1. Fatty Acid Notation

**Issue**: Fatty acids use shorthand notation (e.g., "16:0", "18:1")
- **16:0** = Palmitic acid (16 carbons, 0 double bonds) = CHEBI:15756
- **18:1** = Oleic acid (18 carbons, 1 double bond) = CHEBI:16196

**Current Status**: ❌ **Completely unused** (fatty acid profile field extracted but not processed)

**Needed**: Fatty acid notation → CHEBI mapping table

**Estimated entries**: ~50 common bacterial fatty acids

**Effort**: Medium (need to create mapping table from literature)

---

### 2. Medium Names

**Issue**: Culture media names are free text (e.g., "Marine Broth", "TSA", "LB")

**Current Status**: ⚠️ **Ad-hoc prefix** (`medium:Marine_Broth`)

**Could map to**:
- OBI (Ontology for Biomedical Investigations) has some media terms
- Custom METPO terms for common media?
- Leave as-is (lower priority than enzyme/chemical normalization)

**Count**: 1,571 medium nodes

**Priority**: Low (media composition is complex, ad-hoc prefix acceptable here)

---

### 3. Isolation Source

**Issue**: Environmental sources are free text (e.g., "soil", "marine water", "clinical sample")

**Current Status**: ⚠️ **Ad-hoc prefix** (`isolation_source:soil`)

**Could map to**: ENVO (Environment Ontology)

**Count**: 353 isolation source nodes

**Priority**: Medium (ENVO mapping would be valuable for ecological analysis)

**Effort**: Medium (need NER or manual mapping for 353 terms)

---

### 4. Murein/Peptidoglycan Types

**Issue**: Murein types use specialized notation (e.g., "A3α", "A4β")

**Current Status**: ✅ **Extracted** (line 898), ⚠️ **Usage unknown**

**Could map to**:
- CHEBI (peptidoglycan structures)
- Custom METPO structural terms?

**Priority**: Low (structural chemistry, not enzyme/metabolism)

---

### 5. Compound Production (Free Text)

**Issue**: Compound names without CHEBI IDs (e.g., "indole", "acetoin")

**Current Status**: ❌ **Completely unused**

**Needs**: NER mapping to CHEBI (like Madin transform does)

**Priority**: High (see earlier analysis)

---

### 6. Metabolite Tests

**Issue**: Classic microbi tests (indole, VP, methyl red, citrate)

**Current Status**: ❌ **Completely unused** but HAS CHEBI IDs!

**Priority**: **HIGHEST** (easy win with CHEBI IDs already present)

---

## Holistic Normalization Opportunities

### Opportunity 1: Leverage bacdive_mappings.tsv Fully (HIGHEST IMPACT)

**Current**: Mappings file creates chemical → assay edges only

**Should create**:
1. **Organism → EC number edges** (enzyme activity)
2. **EC number → CHEBI edges** (enzyme-substrate relationships)
3. **Remove assay intermediary nodes entirely**

**Benefits**:
- Remove 511 ad-hoc nodes (31.5% of problematic nodes)
- Create semantic enzyme activity graph
- Enable graph traversal: Organism → Enzyme → Substrate
- Compatible with other databases (BRENDA, ExplorEnz use same EC numbers)

**Implementation**:
```python
# Instead of creating assay nodes
for api_result in api_tests:
    if api_result.value == "+":
        # Look up in bacdive_mappings.tsv
        mapping = mappings_df[mappings_df['pseudo_CURIE'] == f"assay:API_{kit}_{test}"]

        if mapping['EC_ID'].notna():
            # Create organism → EC edge
            write_edge(organism_id, "biolink:capable_of", mapping['EC_ID'])

            # Create EC → substrate edge
            if mapping['CHEBI_ID'].notna():
                write_edge(mapping['EC_ID'], "biolink:consumes", mapping['CHEBI_ID'])
```

**Effort**: Medium (2-3 days to refactor transform code)

**Impact**: Eliminate 31.5% of non-semantic edges!

---

### Opportunity 2: Capture Negative Results (HIGH VALUE)

**Current**: Only "+" results captured

**Should**: Capture "-" results with edge properties

**Benefits**:
- Double training data for ML models
- Essential for supervised learning (need positive AND negative examples)
- Same code refactor as Opportunity 1

**Implementation**: Add `evidence: "+"` or `evidence: "-"` edge property

---

### Opportunity 3: Create Fatty Acid Mapping Table

**Needed**: `fatty_acid_notation_to_chebi.yaml`

**Format**:
```yaml
"16:0":
  chebi: "CHEBI:15756"
  name: "palmitic acid"
"18:1":
  chebi: "CHEBI:16196"
  name: "oleic acid"
# ... ~50 more
```

**Source**: Bacterial fatty acid literature, CHEBI database

**Effort**: Medium (3-5 days to research and create)

**Impact**: Enable fatty acid profile processing (currently unused)

---

### Opportunity 4: ENVO Mapping for Isolation Sources

**Needed**: NER or manual mapping of 353 isolation source terms → ENVO

**Example**:
- "soil" → ENVO:00001998
- "marine water" → ENVO:00002149
- "clinical sample" → not in ENVO (keep ad-hoc)

**Effort**: Medium (use OAK NER like Madin transform)

**Impact**: Semantic environmental context

**Priority**: Medium (useful but not critical for enzyme/metabolism focus)

---

## Summary: Current Helper Files vs. Opportunities

| Resource | Exists? | Well-Used? | Opportunity |
|----------|---------|------------|-------------|
| **bacdive_mappings.tsv** | ✅ Yes | ⚠️ Partial | **Use for direct org→EC→CHEBI edges** |
| **metabolite_mapping.json** | ✅ Yes | ✅ Good | Continue using |
| **cas-rn_map.txt** | ✅ Yes | ✅ Good | Continue using |
| **METPO mappings** | ✅ Yes | ✅ Good | Expand path-based extraction |
| **Fatty acid mapping** | ❌ No | N/A | **Create new table** |
| **ENVO isolation mapping** | ❌ No | N/A | Use OAK NER |
| **Compound production mapping** | ❌ No | N/A | Use OAK NER (like Madin) |

---

## Recommended Actions

### Priority 1: Refactor API Test Processing (HIGHEST IMPACT)

**Goal**: Use bacdive_mappings.tsv to create semantic edges instead of ad-hoc assay nodes

**Steps**:
1. Load bacdive_mappings.tsv in transform
2. For each positive API result:
   - Look up EC number and CHEBI ID from mappings
   - Create organism → capable_of → EC edge
   - Create EC → consumes → CHEBI edge
   - Skip creating assay node entirely
3. For negative results: same but with `evidence: "-"` property

**Effort**: 2-3 days
**Impact**: Remove 511 ad-hoc nodes, create semantic graph paths

---

### Priority 2: Implement Metabolite Tests (EASY WIN)

**Goal**: Process metabolite tests field (has CHEBI IDs, currently unused)

**Steps**:
1. Add processing code similar to metabolite utilization
2. Extract test results (indole, VP, citrate, methyl red)
3. Create organism → CHEBI edges with test type metadata

**Effort**: 1-2 days
**Impact**: Thousands of new semantic edges

---

### Priority 3: Create Fatty Acid Mapping Table

**Goal**: Enable fatty acid profile processing

**Steps**:
1. Research bacterial fatty acids in literature
2. Map notation (16:0, 18:1, etc.) → CHEBI IDs
3. Create YAML mapping file
4. Implement fatty acid profile processing

**Effort**: 3-5 days
**Impact**: Enable unused data source with taxonomic value

---

### Priority 4: ENVO Mapping for Isolation Sources

**Goal**: Replace ad-hoc isolation_source prefix with ENVO terms

**Steps**:
1. Use OAK NER on 353 isolation source strings
2. Manual curation for ambiguous terms
3. Update transform to use ENVO IDs where available

**Effort**: 2-3 days
**Impact**: Semantic environmental context

---

## Key Insights

### What We Learned

1. **API = Analytical Profile Index** (bioMérieux, universal in microbiology)
2. **16 different API kits** with 10-50 tests each
3. **Excellent mapping resource exists** (`bacdive_mappings.tsv`) with 370 tests
4. **Mappings are underutilized** - create chemical→assay edges but not org→EC→CHEBI
5. **Documentation is available** - test chemistry is published, no IP barrier
6. **EC numbers and CHEBI IDs are already mapped** - just need to use them!

### Biggest Opportunity

**Refactor API test processing** to eliminate ad-hoc prefix and create semantic enzyme-substrate graph. This single change removes 31.5% of non-semantic edges and makes the KG queryable by enzyme activity.

---

## Related Files

- Analysis: `bacdive_chemical_enzyme_gap_analysis.md`
- Path matrix: `bacdive_path_usage_matrix.md`
- Complete audit: `bacdive_complete_chemistry_audit.md`
- Issue #25: Chemical-Enzyme Interactions Gap Analysis

---

**Reminder about Luke**: Don't forget to document auto-prefix grounding failures for Luke! 😊
