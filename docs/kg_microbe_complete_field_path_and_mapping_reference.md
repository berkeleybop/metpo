# KG-Microbe Complete Field Path and Mapping Reference

**Date:** 2025-10-03
**Purpose:** Meticulous documentation of all field paths, workaround prefixes, and mapping sources in kg-microbe

---

## Table of Contents

1. [Workaround Prefixes (Placeholder CURIEs)](#workaround-prefixes)
2. [BacDive Field Paths](#bacdive-field-paths)
3. [BactoTraits Field Paths](#bactotraits-field-paths)
4. [Madin et al. Field Paths](#madin-field-paths)
5. [Mapping Files and Sources](#mapping-files-and-sources)
6. [Reusable Patterns](#reusable-patterns)

---

## Workaround Prefixes

These are placeholder CURIE prefixes used when proper ontology mappings don't exist. They create temporary identifiers until METPO or other ontologies provide proper terms.

### Core Placeholder Prefixes (from `constants.py`)

| Prefix | Example | Usage | When Used | Target Ontology |
|--------|---------|-------|-----------|-----------------|
| `pathways:` | `pathways:nitrate_reduction` | Madin pathways not in METPO | Pathway value exists in Madin but not in METPO, and GO NER fails | METPO (add missing) |
| `carbon_substrates:` | `carbon_substrates:glucose` | Madin carbon substrates not in METPO/ChEBI | Substrate value not in METPO and ChEBI NER fails | METPO or ChEBI |
| `cell_shape:` | `cell_shape:bacillus` | Madin cell shapes not in METPO | Cell shape value not in METPO | METPO |
| `isolation_source:` | `isolation_source:soil` | Madin isolation sources not in ENVO | Isolation source not mapped to ENVO | ENVO |
| `strain:` | `strain:DSM14760` | Strain identifiers | Individual strain references | NCBITaxon or BacDive |
| `bacdive:` | `bacdive:100` | BacDive IDs | BacDive strain database ID | BacDive (internal) |
| `assay:` | `assay:API_ZYM` | Metabolic assays | BacDive metabolite utilization tests | OBI or custom |
| `medium:` | `medium:104c` | MediaDive media IDs | Culture medium identifier | MediaDive |
| `ingredient:` | `ingredient:yeast_extract` | MediaDive ingredients | Medium component | ChEBI |
| `solution:` | `solution:vitamin_solution` | MediaDive solutions | Pre-mixed solutions | ChEBI or custom |
| `medium-type:` | `medium-type:complex` | Medium types | Defined vs complex media | Custom |
| `BSL:` | `BSL:1` | Biosafety levels | Risk assessment levels | Custom |

### BactoTraits-Specific Placeholders (from `custom_curies.yaml`)

These are used by BactoTraits transform for one-hot encoded fields:

| Category | Prefix | Example | Mapping |
|----------|--------|---------|---------|
| **Salinity** | `salinity:` | `salinity:halophilic` | 7 values (moderately_halophilic, halophilic, non_halophilic, etc.) |
| **Trophic Type** | `trophic_type:` | `trophic_type:heterotrophy` | 28 values (chemoautotroph, heterotroph, methylotroph, etc.) |
| **Cell Shape** | `cell_shape:` | `cell_shape:rod` | 16 values (rod, sphere, coccus, spiral, ovoid, filament, etc.) |
| **Gram Stain** | `gram_stain:` | `gram_stain:positive` | 4 values (positive, negative, variable, indeterminate) |
| **Production** | `production:` | `production:antibiotic_compound` | 8 values (antibiotic, alcohol, toxin, amino_acid, etc.) |
| **Pathogen** | `pathogen:` | `pathogen:human` | 3 values (human, animal, plant) |
| **Motility** | `motility:` | `motility:motile` | 2 values (motile, non_motile) |
| **Sporulation** | `sporulation:` | `sporulation:spore_forming` | 2 values (spore_forming, non_spore_forming) |
| **GC Content** | `gc:` | `gc:low` | 4 bins (low, mid1, mid2, high) |
| **Pigment** | `pigment:` | `pigment:pink` | 10 colors (pink, yellow, brown, red, orange, etc.) |
| **pH Optimal** | `pH_opt:` | `pH_opt:low` | 4 bins (low, mid1, mid2, high) |
| **pH Range** | `pH_range:` | `pH_range:mid2` | 6 bins (low, mid1, mid2, mid3, mid4, high) |
| **pH Delta** | `pH_delta:` | `pH_delta:very_low` | 6 bins (very_low, low, mid1, mid2, mid3, high) |
| **NaCl Optimal** | `NaCl_opt:` | `NaCl_opt:very_low` | 4 bins (very_low, low, mid, high) |
| **NaCl Range** | `NaCl_range:` | `NaCl_range:low` | 4 bins (very_low, low, mid, high) |
| **NaCl Delta** | `NaCl_delta:` | `NaCl_delta:mid` | 4 bins (very_low, low, mid, high) |
| **Temperature Optimal** | `temp_opt:` | `temp_opt:mid2` | 7 bins (very_low, low, mid1, mid2, mid3, mid4, high) |
| **Temperature Range** | `temp_range:` | `temp_range:mid3` | 7 bins (very_low, low, mid1, mid2, mid3, mid4, high) |
| **Temperature Delta** | `temp_delta:` | `temp_delta:low` | 6 bins (very_low, low, mid1, mid2, mid3, high) |
| **Cell Width** | `cell_width:` | `cell_width:low` | 4 bins (very_low, low, mid, high) |
| **Cell Length** | `cell_length:` | `cell_length:mid` | 4 bins (very_low, low, mid, high) |

**Note:** Many of these custom CURIEs could/should map to METPO once appropriate terms are added.

---

## BacDive Field Paths

BacDive data is stored in MongoDB with nested JSON structure. Field paths use dot notation.

### Top-Level Sections

```
Document Root
├── General
├── Name and taxonomic classification
├── Morphology
├── Culture and growth conditions
├── Physiology and metabolism
├── Isolation, sampling and environmental information
├── Safety information
├── Sequence information
├── Genome-based predictions
├── External links
└── Reference
```

### General Section

**Path Pattern:** `General.{field_name}`

| Field | Type | Mapped To | Notes |
|-------|------|-----------|-------|
| `General.BacDive-ID` | Integer | `bacdive:{value}` | Primary identifier |
| `General.DSM-Number` | Integer | DSM number column | DSMZ collection number |
| `General.keywords` | Array[String] | Keywords column | Descriptive terms |
| `General.description` | String | Description column | Textual description |
| `General.NCBI tax id` | Array[Object] | `NCBITaxon:{value}` | May have multiple with matching levels |
| `General.NCBI tax id.{}.NCBI tax id` | Integer | Taxon ID | |
| `General.NCBI tax id.{}.Matching level` | String | | "species" or "strain" |
| `General.strain history.history` | String | | Provenance text |
| `General.doi` | String | | BacDive DOI |

### Name and Taxonomic Classification

**Path Pattern:** `Name and taxonomic classification.{field_name}`

| Field | Type | Notes |
|-------|------|-------|
| `Name and taxonomic classification.domain` | String | Bacteria, Archaea |
| `Name and taxonomic classification.phylum` | String | |
| `Name and taxonomic classification.class` | String | |
| `Name and taxonomic classification.order` | String | |
| `Name and taxonomic classification.family` | String | |
| `Name and taxonomic classification.genus` | String | |
| `Name and taxonomic classification.species` | String | |
| `Name and taxonomic classification.full scientific name` | String | Includes HTML |
| `Name and taxonomic classification.strain designation` | String | |
| `Name and taxonomic classification.type strain` | String | "yes"/"no" |
| `Name and taxonomic classification.LPSN.{field}` | Various | LPSN cross-reference |

### Morphology Section

**Path Pattern:** `Morphology.{field_name}`

| Field | Constants | Notes |
|-------|-----------|-------|
| `Morphology.multimedia` | `MULTIMEDIA` | Images, micrographs |
| `Morphology.multicellular morphology` | `MULTICELLULAR_MORPHOLOGY` | |
| `Morphology.colony morphology` | `COLONY_MORPHOLOGY` | |
| `Morphology.cell morphology` | `CELL_MORPHOLOGY` | |
| `Morphology.pigmentation` | `PIGMENTATION` | |

### Culture and Growth Conditions

**Path Pattern:** `Culture and growth conditions.{field_name}`

| Field Path | Mapped To | Notes |
|------------|-----------|-------|
| `Culture and growth conditions.culture medium` | Array/Object | May be array or single object |
| `Culture and growth conditions.culture medium.{}.name` | Medium name | |
| `Culture and growth conditions.culture medium.{}.growth` | String | "yes"/"no" |
| `Culture and growth conditions.culture medium.{}.link` | URL | MediaDive URL |
| `Culture and growth conditions.culture medium.{}.composition` | String | Medium recipe |
| `Culture and growth conditions.culture temp` | Array/Object | Temperature conditions |
| `Culture and growth conditions.culture temp.{}.growth` | String | "positive"/"negative" |
| `Culture and growth conditions.culture temp.{}.type` | String | "growth"/"optimum"/"range" |
| `Culture and growth conditions.culture temp.{}.temperature` | String/Number | Degrees C |

### Physiology and Metabolism Section

**Path Pattern:** `Physiology and metabolism.{field_name}`

**CRITICAL:** These paths are what METPO's BacDive synonyms should match!

| Field Path | Values | METPO Mapping | Constants |
|------------|--------|---------------|-----------|
| `Physiology and metabolism.oxygen tolerance.oxygen tolerance` | aerobe, anaerobe, facultative aerobe, facultative anaerobe, obligate aerobe, obligate anaerobe, microaerophile, microaerotolerant, aerotolerant | `METPO:100060X` classes | `OXYGEN_TOLERANCE` |
| `Physiology and metabolism.halophily.halophily level` | halophilic, halotolerant, non-halophilic, moderately halophilic, slightly halophilic, extremely halophilic, haloalkaliphilic | METPO halophily classes | `HALOPHILY` |
| `Physiology and metabolism.spore formation.spore formation` | yes, no | METPO sporulation | `SPORE_FORMATION` |
| `Physiology and metabolism.enzymes` | Array | EC numbers | `ENZYMES` |
| `Physiology and metabolism.metabolite utilization` | Array[Object] | ChEBI or placeholder | `METABOLITE_UTILIZATION` |
| `Physiology and metabolism.metabolite production` | Array[Object] | ChEBI or placeholder | `METABOLITE_PRODUCTION` |
| `Physiology and metabolism.metabolite tests` | Array[Object] | Assay results | `METABOLITE_TESTS` |
| `Physiology and metabolism.compound production` | Array | Chemical production | `COMPOUND_PRODUCTION` |
| `Physiology and metabolism.fatty acid profile` | Array | Fatty acids | `FATTY_ACID_PROFILE` |
| `Physiology and metabolism.tolerance` | Array | Tolerance conditions | `TOLERANCE` |
| `Physiology and metabolism.antibiogram` | Array[Object] | Antibiotic resistance | `ANTIBIOGRAM` |
| `Physiology and metabolism.antibiotic resistance` | Array[Object] | Resistance data | `ANTIBIOTIC_RESISTANCE` |
| `Physiology and metabolism.nutrition type` | Array | Trophic types | `NUTRITION_TYPE` |
| `Physiology and metabolism.murein` | Object | Cell wall composition | `MUREIN` |

**Metabolite Utilization Structure:**
```javascript
"metabolite utilization": [
  {
    "metabolite": "glucose",
    "Chebi-ID": "CHEBI:17234",
    "utilization activity": "+",
    "kind of utilization tested": "carbon source"
  }
]
```

**Antibiogram Structure:**
```javascript
"antibiogram": [
  {
    "antibiotic": "ampicillin",
    "Chebi-ID": "CHEBI:28971",
    "activity": "is resistant"  // or "is sensitive"
  }
]
```

### Isolation, Sampling and Environmental Information

**Path Pattern:** `Isolation, sampling and environmental information.{field_name}`

| Field Path | Mapped To | Constants |
|------------|-----------|-----------|
| `Isolation, sampling and environmental information.isolation` | Object | `ISOLATION` |
| `Isolation, sampling and environmental information.isolation.sample type` | String | Sample description |
| `Isolation, sampling and environmental information.isolation.country` | String | Country name |
| `Isolation, sampling and environmental information.isolation.origin.country` | String | ISO code |
| `Isolation, sampling and environmental information.isolation.continent` | String | Continent name |
| `Isolation, sampling and environmental information.isolation source categories` | Array[Object] | Hierarchical categories | `ISOLATION_SOURCE_CATEGORIES` |

**Isolation Source Categories Structure:**
```javascript
"isolation source categories": [
  {
    "Cat1": "#Host",
    "Cat2": "#Mammals"
  },
  {
    "Cat1": "#Host Body Product",
    "Cat2": "#Gastrointestinal tract",
    "Cat3": "#Feces (Stool)"
  }
]
```

### Safety Information

**Path Pattern:** `Safety information.{field_name}`

| Field Path | Mapped To | Constants |
|------------|-----------|-----------|
| `Safety information.risk assessment` | Object | `RISK_ASSESSMENT` |
| `Safety information.risk assessment.biosafety level` | String | `BSL:{value}` | `BIOSAFETY_LEVEL` |
| `Safety information.risk assessment.biosafety level comment` | String | Risk classification | |

### Sequence Information

**Path Pattern:** `Sequence information.{field_name}`

| Field Path | Type | Notes |
|------------|------|-------|
| `Sequence information.16S sequences` | Object/Array | 16S rRNA sequences |
| `Sequence information.16S sequences.description` | String | |
| `Sequence information.16S sequences.accession` | String | GenBank accession |
| `Sequence information.16S sequences.length` | Integer | Sequence length |
| `Sequence information.16S sequences.database` | String | Source database |
| `Sequence information.16S sequences.NCBI tax ID` | Integer | |
| `Sequence information.Genome sequences` | Array[Object] | Genome assemblies |
| `Sequence information.GC content.GC-content` | String | GC% range |

### External Links

**Path Pattern:** `External links.{field_name}`

| Field Path | Mapped To | Constants |
|------------|-----------|-----------|
| `External links.culture collection no.` | String | Comma-separated IDs | `EXTERNAL_LINKS_CULTURE_NUMBER` |
| `External links.straininfo link.straininfo` | Integer | StrainInfo ID | |
| `External links.literature` | Array[Object] | Publications | |

---

## BactoTraits Field Paths

BactoTraits uses **one-hot encoding** with nested objects in MongoDB. The CSV has different column headers than the MongoDB representation.

### MongoDB Structure (Actual)

```javascript
{
  bacdive_id: "123",
  ncbitaxon_id: 12345,

  // One-hot encoded phenotypes
  oxygen: {
    aerobic: 1,
    anaerobic: 0,
    facultative_aerobe_anaerobe: 0,
    microerophile: 0
  },

  cell_shape: {
    curved_spiral: 0,
    filament: 0,
    ovoid: 0,
    rod: 1,
    sphere: 0,
    star_dumbbell_pleomorphic: 0
  },

  gram_stain: {
    negative: 0,
    positive: 1
  },

  motility: {
    motile: 1,
    non_motile: 0
  },

  spore_formation: {
    spore_forming: 0,
    no_spore: 1
  },

  gc_content: {
    lte_42dot65: 0,
    "42dot65_to_57dot0": 1,
    "57dot0_to_66dot3": 0,
    gt_66dot3: 0
  },

  // Nested quantitative values
  temperature: {
    optimum: 25.5,
    range: [15, 35],
    delta: 20
  },

  ph: {
    optimum: 7.0,
    range: [6.0, 8.0],
    delta: 2.0
  },

  nacl: {
    optimum: 1.0,
    range: [0.0, 3.0],
    delta: 3.0
  }
}
```

### Field Access Patterns

| Field Category | Original CSV Column | MongoDB Path (Transformed) | METPO Synonym (Correct!) |
|----------------|---------------------|----------------------------|--------------------------|
| **Oxygen** | `Ox_anaerobic`, `Ox_aerobic`, `Ox_facultative_aerobe_anaerobe`, `Ox_microerophile` | `oxygen.{aerobic,anaerobic,facultative_aerobe_anaerobe,microerophile}` | Ox_aerobic, Ox_anaerobic, etc. ✓ |
| **Cell Shape** | `S_rod`, `S_sphere`, `S_curved_spiral`, `S_filament`, `S_ovoid`, `S_star_dumbbell_pleomorphic` | `cell_shape.{rod,sphere,curved_spiral,filament,ovoid,star_dumbbell_pleomorphic}` | S_rod, S_sphere, etc. ✓ |
| **Gram Stain** | `G_negative`, `G_positive` | `gram_stain.{negative,positive}` | G_negative, G_positive ✓ |
| **Motility** | `motile`, `non-motile` | `motility.{motile,non_motile}` | motile, non-motile ✓ |
| **Spore Formation** | `spore`, `no_spore` | `spore_formation.{spore_forming,no_spore}` | spore, no_spore ✓ |
| **GC Content** | `GC_<=42.65`, `GC_42.65_57.0`, `GC_57.0_66.3`, `GC_>66.3` | `gc_content.{lte_42dot65,42dot65_to_57dot0,57dot0_to_66dot3,gt_66dot3}` | GC_<=42.65, etc. ✓ |
| **Temperature Optimum** | `TO_<=10`, `TO_10_to_22`, `TO_22_to_27`, `TO_27_to_30`, `TO_30_to_34`, `TO_34_to_40`, `TO_>40` | `temperature.optimum` (Float) | TO_<=10, TO_10_to_22, etc. ✓ |
| **Temperature Range** | `TR_<=10`, `TR_10_to_22`, ... , `TR_>40` | `temperature.range` (Array[Float]) | TR_<=10, TR_10_to_22, etc. ✓ |
| **Temperature Delta** | `Td_1_5`, `Td_5_10`, `Td_10_20`, `Td_20_30`, `Td_>30` | `temperature.delta` (Float) | Td_1_5, Td_5_10, etc. ✓ |
| **pH Optimum** | `pHO_0_to_6`, `pHO_6_to_7`, `pHO_7_to_8`, `pHO_8_to_14` | `ph.optimum` (Float) | pHO_0_to_6, pHO_6_to_7, etc. ✓ |
| **pH Range** | `pHR_0_to_4`, `pHR_4_to_6`, `pHR_6_to_7`, `pHR_7_to_8`, `pHR_8_to_10`, `10_to_14` | `ph.range` (Array[Float]) | pHR_0_to_4, pHR_4_to_6, etc. ✓ |
| **pH Delta** | `pHd_<=1`, `pHd_1_2`, `pHd_2_3`, `pHd_3_4`, `pHd_4_5`, `pHd_5_9` | `ph.delta` (Float) | pHd_<=1, pHd_1_2, etc. ✓ |
| **NaCl Optimum** | `NaO_<=1`, `NaO_1_to_3`, `NaO_3_to_8`, `NaO_>8` | `nacl.optimum` (Float) | NaO_<=1, NaO_1_to_3, etc. ✓ |
| **NaCl Range** | `NaR_<=1`, `NaR_1_to_3`, `NaR_3_to_8`, `NaR_>8` | `nacl.range` (Array[Float]) | NaR_<=1, NaR_1_to_3, etc. ✓ |
| **NaCl Delta** | `Nad_<=1`, `Nad_1_3`, `Nad_3_8`, `Nad_>8` | `nacl.delta` (Float) | Nad_<=1, Nad_1_3, etc. ✓ |

**IMPORTANT:** METPO's BactoTraits synonyms are **CORRECT** - they match the original CSV column headers from the BactoTraits database!

**Source:** `https://ordar.otelo.univ-lorraine.fr/files/ORDAR-53/BactoTraits_databaseV2_Jun2022.csv` (19,457 strains)
- CSV has 3 header rows: category groupings, units, actual column names
- Row 3 contains the actual column headers that METPO correctly claims

**MongoDB Transformation Logic:** The CSV → MongoDB transformation uses the **multi-level CSV headers** to infer nested structure:
- **Row 1 (Categories):** `Oxygen`, `Gram`, `shape`, `pH_Optimum`, `temp_Optimum` → Parent keys in MongoDB
- **Row 2 (Units/Metadata):** `%`, `Celsius degree`, etc. → Used for context
- **Row 3 (Column Names):** `Ox_aerobic`, `G_positive`, `S_rod`, `pHO_6_to_7` → Child keys (with prefix stripped)

**Transformation Rules:**
- **Removed prefixes:** `Ox_aerobic` → `oxygen.aerobic`, `S_rod` → `cell_shape.rod` (prefix = Row 1 category)
- **Created nested objects:** Flat columns → `oxygen.{value}`, `cell_shape.{value}`, `ph.{optimum,range,delta}`
- **Converted binned to continuous:** `TO_10_to_22` (Boolean column) → `temperature.optimum` (Float value)
- **Normalized symbols:** `GC_<=42.65` → `gc_content.lte_42dot65` (made field-name safe)

**Row Count Verification:**
- Original CSV: 19,457 data rows (19,458 lines including header)
- MongoDB: 19,455 documents
- Difference: 2 rows (likely parsing errors or invalid data)

---

## Madin et al. Field Paths

Madin data is flat CSV/TSV loaded directly into MongoDB with minimal transformation.

### Field List (35 total)

| Field Name | Type | Unique Values | Completeness | METPO Processing |
|------------|------|---------------|--------------|------------------|
| `tax_id` | Integer | 49,155 | 100% | → `NCBITaxon:{value}` |
| `species_tax_id` | Integer | 21,500 | 100% | Taxon identifier |
| `org_name` | String | 116,704 | 94.6% | Organism name |
| `species` | String | 21,500 | 100% | Species name |
| `genus` | String | 2,885 | 99.1% | Genus |
| `family` | String | 481 | 98.6% | Family |
| `order` | String | 212 | 98.9% | Order |
| `class` | String | 95 | 98.9% | Class |
| `phylum` | String | 75 | 100% | Phylum |
| `superkingdom` | String | 2 | 100% | Archaea/Bacteria |
| `data_source` | String | 26 | 100% | Source attribution |
| `ref_id` | Integer | 20,277 | 93.6% | Reference ID |
| **Phenotypic Traits** |
| `gram_stain` | Categorical | 3 | 25.7% | positive, negative, NA → METPO lookup |
| `metabolism` | Categorical | 8 | 20.1% | aerobic, anaerobic, facultative, etc. → METPO lookup |
| `pathways` | Comma-separated | 161 combos (103 unique) | 9.3% | Split on "," → METPO lookup → GO NER → placeholder |
| `carbon_substrates` | Comma-separated | 3,978 combos | 2.7% | Split on "," → METPO lookup → ChEBI NER → placeholder |
| `cell_shape` | Categorical | 20 | 16.4% | bacillus, coccus, spiral, etc. → METPO lookup → placeholder |
| `sporulation` | Categorical | 3 | 11.1% | yes, no, NA → METPO lookup |
| `motility` | Categorical | 6 | 13.2% | yes, no, flagella, gliding, axial filament, NA |
| **Environmental** |
| `isolation_source` | Categorical | 75 | 30.2% | Controlled vocabulary → ENVO mapping |
| `range_tmp` | Categorical | 8 | 5.1% | Temperature preference (mesophilic, thermophilic, etc.) |
| `range_salinity` | Categorical | 8 | 0.5% | Salinity preference (halophilic, halotolerant, etc.) |
| **Quantitative** |
| `optimum_tmp` | Numeric | 189 | 8.8% | Optimal temperature (°C) |
| `optimum_ph` | Numeric | 131 | 2.7% | Optimal pH |
| `growth_tmp` | Numeric | 341 | 7.9% | Growth temperature |
| `doubling_h` | Numeric | 651 | 0.7% | Doubling time (hours) |
| **Cell Dimensions** |
| `d1_lo` | Numeric | 152 | 2.9% | Cell dimension 1 lower |
| `d1_up` | Numeric | 72 | 1.0% | Cell dimension 1 upper |
| `d2_lo` | Numeric | 246 | 2.9% | Cell dimension 2 lower |
| `d2_up` | Numeric | 121 | 1.2% | Cell dimension 2 upper |
| **Genomic** |
| `genome_size` | Numeric | 87,040 | 63.0% | Genome size (bp) |
| `gc_content` | Numeric | 9,753 | 17.1% | GC% |
| `coding_genes` | Numeric | 5,889 | 10.2% | Number of coding genes |
| `rRNA16S_genes` | Numeric | 18 | 4.2% | Number of 16S rRNA genes |
| `tRNA_genes` | Numeric | 151 | 7.5% | Number of tRNA genes |

### Processing Logic (from `madin_etal.py`)

```python
# Fields processed by transform
traits_columns_of_interest = [
    "tax_id",           # → NCBITaxon:{value}
    "org_name",         # → organism label
    "metabolism",       # → METPO mapping
    "pathways",         # → METPO → GO NER → placeholder
    "carbon_substrates",# → METPO → ChEBI NER → placeholder
    "cell_shape",       # → METPO → placeholder
    "isolation_source"  # → ENVO mapping
]

# Pathways processing
pathways = line["pathways"].split(",")  # Comma-separated
for pathway in pathways:
    metpo_mapping = self.madin_metpo_mappings.get(pathway.strip())
    if metpo_mapping:
        # Use METPO CURIE, category, predicate
    else:
        # Try GO NER
        # Fall back to pathways:{value}

# Carbon substrates processing
carbon_substrates = line["carbon_substrates"].split(",")
for substrate in carbon_substrates:
    metpo_mapping = self.madin_metpo_mappings.get(substrate.strip())
    if metpo_mapping:
        # Use METPO
    else:
        # Try ChEBI NER
        # Fall back to carbon_substrates:{value}

# Isolation source
isolation_source_mapping = envo_mapping.get(line["isolation_source"])
if isolation_source_mapping:
    # Use ENVO ID
else:
    # Use isolation_source:{value}
```

---

## Mapping Files and Sources

### 1. METPO Mappings (Dynamic, from GitHub)

**Source:** Remote fetch from METPO repository
**URL:** `https://raw.githubusercontent.com/berkeleybop/metpo/refs/tags/2025-09-23/src/templates/metpo_sheet.tsv`
**Loaded by:** `kg_microbe/utils/mapping_file_utils.py::load_metpo_mappings(synonym_column)`
**Update frequency:** On each kg-microbe build (fetches latest from pinned tag)

**Synonym Columns Used:**
- `"madin synonym or field"` - For Madin transform
- `"bacdive keyword synonym"` - For BacDive transform
- (likely) BactoTraits-specific column

**Structure:**
```python
{
  "aerobic": {
    "curie": "METPO:1000602",
    "label": "aerobic",
    "predicate": "has_phenotype",
    "predicate_biolink_equivalent": "biolink:has_phenotype",
    "biolink_equivalent": "...",
    "inferred_category": "biolink:OxygenPreference"
  }
}
```

**Tree Traversal:** Builds parent-child hierarchy to infer biolink categories and predicates from ancestors.

### 2. Custom CURIEs (YAML)

**File:** `kg_microbe/transform_utils/custom_curies.yaml`
**Size:** 700 lines
**Usage:** BactoTraits transform, supplementary mappings
**Format:** Nested YAML with YAML anchors/aliases for reuse

**Structure:**
```yaml
phenotypic_quality: &phenotypic_quality_block
  category: "biolink:PhenotypicQuality"
  predicate: "biolink:has_phenotype"

salinity:
  moderately_halophilic:
    curie: "salinity:moderately_halophilic"
    name: "moderately halophilic"
    <<: *phenotypic_quality_block  # Inherits category and predicate
```

**Categories Defined:**
- Salinity (7 values)
- Trophic types (28 values including combinations)
- Cell shapes (16 values including combinations like `s_curved_spiral`)
- Gram stain (4 values)
- Production types (8 values)
- Pathogens (3 values)
- Motility (2 values)
- Sporulation (2 values + aliases)
- GC content bins (4)
- Pigment colors (10)
- pH optimal/range/delta bins (4-6 bins each)
- NaCl optimal/range/delta bins (4 each)
- Temperature optimal/range/delta bins (6-7 each)
- Cell width/length bins (4 each)

**Reusable Blocks:**
- `&phenotypic_quality_block`
- `&phenotypic_capability_block`
- `&biological_process_block`
- `&chemical_production_block`

**Combination Handling:**
```yaml
s_curved_spiral:
  curie: "cell_shape:curved_spiral"
  name: "curved spiral shaped cell"
  combo:  # Creates edges to multiple shapes
    - *curved_shaped_block
    - *spiral_shaped_block
```

### 3. Prefix Map (JSON)

**File:** `kg_microbe/transform_utils/prefixmap.json`
**Size:** 3 lines
**Content:**
```json
{
    "METPO": "https://w3id.org/metpo/"
}
```

**Purpose:** CURIE expansion for METPO identifiers.

### 4. Translation Table (YAML)

**File:** `kg_microbe/transform_utils/translation_table.yaml`
**Size:** 820 lines
**Purpose:** Global ontology term mappings (NOT microbial-specific)
**Usage:** General KGX infrastructure, not specific to microbe data

**Contains:** Standard ontology CURIEs (BFO, CHEBI, ECO, GO, HP, MONDO, NCBITaxon, OBI, RO, SO, etc.)

### 5. BacDive Metabolite Mapping (JSON)

**File:** `kg_microbe/transform_utils/bacdive/metabolite_mapping.json`
**Size:** 200 lines
**Purpose:** Map metabolite names → ChEBI IDs for BacDive antibiotic resistance data

**Structure:**
```json
{
  "CHEBI:3770": "co-trimoxazole",
  "CHEBI:71415": "nitrofurantoin",
  "CHEBI:2637": "amikacin",
  ...
  "CHEBI:36047": "antibiotic_compound",
  "CHEBI:27026": "toxin",
  "CHEBI:33709": "amino_acid"
}
```

**Coverage:** ~200 antibiotics + general categories

### 6. Madin ChEBI Manual Annotation (TSV)

**File:** `kg_microbe/transform_utils/madin_etal/chebi_manual_annotation.tsv`
**Size:** 7 mappings
**Purpose:** Manual corrections for ChEBI NER results

**Content:**
```tsv
object_id	object_label	traits_dataset_term	action
CHEBI:28885	butan-1-ol	butanol	REPLACE
CHEBI:51850	Methyl pyruvate	pyruvic acid methyl ester	REPLACE
CHEBI:16000	ethanolamine	2-aminethanol	REPLACE
CHEBI:30832	adipic acid	adipate	REPLACE
CHEBI:18276	dihydrogen	H2_CO2	SUPPLEMENT
CHEBI:18276	dihydrogen	H2_methanol	SUPPLEMENT
```

**Actions:**
- REPLACE: Substitute NER result
- SUPPLEMENT: Add additional mapping

### 7. Environments Conversion Table (CSV)

**File:** From Madin repository
**Local:** `kg_microbe/data/raw/environments.csv` (downloaded via download.yaml)
**Purpose:** Map Madin `isolation_source` values → ENVO terms

**Structure:**
```csv
TYPE,ENVO_TERMS,ENVO_ID
soil,soil environment,"ENVO:00002041"
water_fresh,freshwater environment,"ENVO:01000306"
...
```

**Usage:**
```python
envo_df = pd.read_csv(self.environments_file)
envo_mapping = envo_df.set_index("TYPE").T.to_dict()
isolation_source = envo_mapping.get(filtered_row["isolation_source"])
```

### 8. Generated/Temporary Mapping Files

These are created during transform runs:

| File | Purpose | Generated By |
|------|---------|--------------|
| `kg_microbe/transform_utils/bacdive/tmp/bacdive_mappings.tsv` | BacDive field mappings | BacDive transform |
| `kg_microbe/transform_utils/bactotraits/tmp/BactoTraits_mapping.tsv` | BactoTraits mappings | BactoTraits transform |
| `kg_microbe/transform_utils/madin_etal/nlp_output/go_ner.tsv` | GO NER results for pathways | OAK NER on Madin pathways |
| `kg_microbe/transform_utils/madin_etal/nlp_output/chebi_ner.tsv` | ChEBI NER results for substrates | OAK NER on Madin carbon_substrates |
| `kg_microbe/transform_utils/ontologies/xrefs/chebi_xrefs.tsv` | ChEBI cross-references | Ontology transform |
| `kg_microbe/transform_utils/ontologies/xrefs/mondo_xrefs.tsv` | MONDO cross-references | Ontology transform |
| `kg_microbe/transform_utils/ontologies/trees/go_category_trees.tsv` | GO hierarchy | Ontology transform |

---

## Reusable Patterns

### Pattern 1: METPO Mapping with NER Fallback

**Used by:** Madin pathways, Madin carbon_substrates, Madin cell_shape
**Steps:**
1. Load METPO mappings from GitHub
2. Try exact match on synonym
3. If found: Use METPO CURIE + inferred category + biolink predicate
4. If not found: Try NER (ontology-specific)
5. If NER fails: Create placeholder CURIE

**Code Pattern:**
```python
# 1. Load mappings
self.madin_metpo_mappings = load_metpo_mappings("madin synonym or field")

# 2. Try METPO first
metpo_mapping = self.madin_metpo_mappings.get(value.strip())
if metpo_mapping:
    node = [
        metpo_mapping["curie"],         # METPO:XXXXXXX
        metpo_mapping.get("inferred_category", DEFAULT_CATEGORY),
        metpo_mapping["label"]
    ]
    predicate = metpo_mapping.get("predicate_biolink_equivalent", DEFAULT_PREDICATE)

# 3. Fall back to NER
else:
    ner_result = find_in_ner_results(value)
    if ner_result:
        node = [ner_result.object_id, CATEGORY, ner_result.object_label]
    else:
        # 4. Placeholder
        node = [f"{PREFIX}:{value}", CATEGORY, value]
```

### Pattern 2: One-Hot Decoding

**Used by:** BactoTraits transform
**Steps:**
1. For each one-hot category (oxygen, cell_shape, etc.)
2. Find which field has value = 1
3. Look up in custom_curies.yaml
4. Create node + edge

**Code Pattern:**
```python
# Assuming one-hot object like: {"aerobic": 1, "anaerobic": 0, ...}
for field_name, value in doc["oxygen"].items():
    if value == 1:
        # Look up in custom CURIEs or METPO
        curie_info = custom_curies["oxygen"][field_name]
        node = [curie_info["curie"], curie_info["category"], curie_info["name"]]
        edge = [tax_id, curie_info["predicate"], curie_info["curie"], ...]
```

### Pattern 3: Nested Path Traversal

**Used by:** BacDive transform
**Steps:**
1. Handle optional fields with `.get()`
2. Handle arrays vs single objects
3. Extract nested values with multiple `.get()` calls

**Code Pattern:**
```python
# Safe nested access
oxygen_data = doc.get("Physiology and metabolism", {}).get("oxygen tolerance", {})
oxygen_value = oxygen_data.get("oxygen tolerance")

# Array handling
culture_media = doc.get("Culture and growth conditions", {}).get("culture medium", [])
if not isinstance(culture_media, list):
    culture_media = [culture_media]

for medium in culture_media:
    medium_name = medium.get("name")
    growth = medium.get("growth")
```

### Pattern 4: Comma-Separated Splitting

**Used by:** Madin pathways, Madin carbon_substrates
**Steps:**
1. Check for "NA"
2. Split on ", " (comma + space)
3. Strip whitespace
4. Process each value independently

**Code Pattern:**
```python
pathways = (
    None
    if filtered_row["pathways"].split(",") == ["NA"]
    else [pathway.strip() for pathway in filtered_row["pathways"].split(",")]
)

if pathways:
    for pathway in pathways:
        # Process each pathway
```

### Pattern 5: Controlled Vocabulary Mapping

**Used by:** Madin isolation_source → ENVO
**Steps:**
1. Load controlled vocabulary CSV
2. Create dictionary mapping
3. Look up value
4. Handle missing with placeholder

**Code Pattern:**
```python
# Load mapping
envo_df = pd.read_csv(environments_file, usecols=["TYPE", "ENVO_TERMS", "ENVO_ID"])
envo_mapping = envo_df.set_index("TYPE").T.to_dict()

# Look up
isolation_source = envo_mapping.get(value)
if isolation_source and isolation_source["ENVO_ID"]:
    node = [isolation_source["ENVO_ID"], ENVIRONMENT_CATEGORY, isolation_source["ENVO_TERMS"]]
else:
    node = [f"isolation_source:{value}", ENVIRONMENT_CATEGORY, value]
```

### Pattern 6: Tree Traversal for Category Inference

**Used by:** METPO mapping loader
**Steps:**
1. Build tree from parent-child relationships
2. For each node, traverse up to find ancestor with biolink equivalent
3. Use that ancestor's biolink equivalent as category
4. Find matching property by looking up ancestor's label in properties sheet

**Code Pattern:**
```python
# Build tree
nodes = {}
for row in reader:
    iri = row["ID"]
    parent_label = row["parent class"]
    nodes[iri] = MetpoTreeNode(iri, row["label"], row["synonyms"], row["biolink equivalent"])

# Link parents
for iri, node in nodes.items():
    parent_iri = find_by_label(parent_label)
    if parent_iri:
        nodes[parent_iri].add_child(node)

# Traverse for category
current = node
while current:
    if current.biolink_equivalent:
        category = current.biolink_equivalent
        predicate = range_to_predicate[current.label]
        break
    current = current.parent
```

---

## Summary: Critical Actions Needed

### 1. Fix BactoTraits METPO Synonyms

**Problem:** Synonyms have prefixes that don't exist in MongoDB.

**Solution Options:**
- **Option A:** Update METPO synonyms to match MongoDB structure
  - Remove prefixes: `Ox_aerobic` → `aerobic`
  - Match nested paths: `TO_<10` → need to bin `temperature.optimum` values
- **Option B:** Document the CSV → MongoDB transformation and map both
- **Option C:** Regenerate MongoDB from CSV without transformation

**Recommendation:** Option A with clear documentation of binning logic.

### 2. Add Missing Madin Pathways to METPO

**88 missing pathway values** → These will reduce placeholder CURIEs in kg-microbe.

**Priority:**
1. Degradation pathways (27)
2. Oxidation pathways (24)
3. Reduction pathways (16)
4. Other processes (21)

### 3. Document CSV → MongoDB Transformations

For each source, document:
- Original file structure (CSV columns)
- MongoDB field names
- Any normalization/transformation applied
- Version/date of transformation

### 4. Create Validation Scripts

Check that:
- METPO synonyms match actual source data
- Placeholder CURIEs are minimized
- All mapping files are in sync

---

**End of Reference Document**
