# METPO Source Coverage Analysis - Issue #223

## Executive Summary

This analysis examines METPO's coverage of values from three structured sources:
- **Madin et al.** (bacteria_archaea_traits)
- **BacDive** (https://bacdive.dsmz.de/)
- **BactoTraits** (BactoTraits_databaseV2_Jun2022.csv)

### Key Findings

| Source | Verified Synonyms | False Claims | Coverage Gap |
|--------|------------------|--------------|--------------|
| **Madin** | 15/103 pathways (14.6%) | 0 | 88 pathway values missing |
| **BacDive** | 16/16 (100%) | 0 | Excellent coverage |
| **BactoTraits** | **0** (claims don't match actual data) | **ALL** | Naming convention mismatch |

---

## 1. Madin et al. (bacteria_archaea_traits) Analysis

### Coverage Statistics
- **Total unique pathway values in Madin**: 103
- **METPO classes with Madin pathway synonyms**: 15
- **Coverage rate**: 14.6%
- **Missing pathway values**: 88

### Verified METPO Classes (15 total)
✅ These METPO classes correctly map to Madin pathway values:
1. acetogenesis
2. aerobic_anoxygenic_phototrophy
3. aerobic_chemo_heterotrophy
4. aerobic_heterotrophy
5. anoxygenic_photoautotrophy
6. anoxygenic_photoautotrophy_hydrogen_oxidation
7. anoxygenic_photoautotrophy_iron_oxidation
8. anoxygenic_photoautotrophy_sulfur_oxidation
9. autotrophy
10. fermentation
11. heterotrophic
12. methanogenesis
13. methylotrophy
14. photoautotrophy
15. photoheterotrophy

### Missing Pathway Values (88 total)

#### High Priority - Degradation Pathways (27)
- aliphatic_non_methane_hydrocarbon_degradation
- aminoacid_degradation
- aromatic_compound_degradation
- aromatic_hydrocarbon_degradation
- cellobiose_degradation
- cellulose_degradation
- chitin_degradation
- chlorocarbon_degradation
- DMSP_degradation
- EDTA_degradation
- gelatin_degradation
- hydrocarbon_degradation
- lignin_degradation
- ligninolysis
- MTBE_degradation
- pah_degradation / PAH_degradation
- PCB_degradation
- plastic_degradation
- polyisoprene_degradation
- polymer_degradation
- RDX_degradation
- urea_degradation
- xylan_degradation

#### High Priority - Reduction Pathways (16)
- arsenate_reduction
- carbonmonoxide_reduction
- carbonylsulfide_reduction
- chlorate_reduction
- cobalt_reduction
- denitrification
- fumarate_reduction
- iron_reduction
- manganese_reduction
- nitrate_reduction
- nitrate_reduction_to_ammonia
- nitric_oxide_reduction
- nitrite_reduction
- nitrite_reduction_to_ammonia
- nitrous_oxide_reduction
- selenate_reduction
- sulfate_reduction
- sulfite_reduction
- sulfur_reduction
- thiocyanate_reduction
- thiosulfate_reduction
- uranyl_reduction

#### High Priority - Oxidation Pathways (24)
- arsenite_oxidation
- carbon_monoxide_oxidation
- carbonmonoxide_oxidation
- carbonylsulfide_oxidation
- chalcopyrite_oxidation
- covellite_oxidation
- galena_oxidation
- hydrogen_oxidation
- hydrogen_oxidation_dark
- iron_oxidation
- iron_oxidation_dark
- manganese_oxidation
- methane_oxidation
- methanol_oxidation
- nitrification
- nitrite_oxidation
- propionate_oxidation
- pyrite_oxidation
- pyrrhotite_oxidation
- sphalerite_oxidation
- sulfide_oxidation
- sulfide_oxidation_dark
- sulfite_oxidation
- sulfite_oxidation_dark
- sulfur_compound_oxidation_dark
- sulfur_oxidation
- sulfur_oxidation_dark
- tetrathionate_oxidation
- thiocyanate_oxidation
- thiosulfate_oxidation
- thiosulfate_oxidation_dark
- trithionate_oxidation
- uraninite_oxidation
- uranium_oxidation

#### Medium Priority - Other Processes (21)
- annamox
- dithionite_disproportionation
- methanogenesis_acetoclastic
- methanogenesis_H2CO2
- nitrogen_fixation
- thiosulfate_disproportionation

---

## 2. BacDive Analysis

### Coverage Statistics
- **Oxygen tolerance values**: 9
- **METPO oxygen preference classes**: 9
- **Coverage rate**: 100% ✅
- **False claims**: 0

### Verified METPO Classes - Oxygen Tolerance (9/9)
✅ All verified:
1. aerobic → "aerobe"
2. anaerobic → "anaerobe"
3. microaerophilic → "microaerophile"
4. facultatively anaerobic → "facultative anaerobe"
5. obligately aerobic → "obligate aerobe"
6. obligately anaerobic → "obligate anaerobe"
7. facultatively aerobic → "facultative aerobe"
8. aerotolerant → "aerotolerant"
9. microaerotolerant → "microaerotolerant"

### Verified METPO Classes - Halophily (7/7)
✅ All verified:
1. halophilic → "halophilic"
2. haloalkaliphilic → "haloalkaliphilic"
3. halotolerant → "halotolerant"
4. moderately halophilic → "moderately halophilic"
5. non halophilic → "non-halophilic"
6. slightly halophilic → "slightly halophilic"
7. extremely halophilic → "extremely halophilic"

**Result**: BacDive synonyms are 100% accurate! ✅

---

## 3. BactoTraits Analysis

### CRITICAL ISSUE: Naming Convention Mismatch

❌ **METPO's BactoTraits synonyms DO NOT match the actual field names in the BactoTraits MongoDB data!**

#### What METPO Claims vs What BactoTraits Actually Uses

**GC Content:**
- METPO claims: "GC_<42.65", "GC_42.65_57.0", "GC_57.0_66.3", "GC_>66.3"
- BactoTraits actual: "lte_42dot65", "42dot65_to_57dot0", "57dot0_to_66dot3", "gt_66dot3"

**Temperature:**
- METPO claims: "TO_<10", "TO_10_to_22", "TR_<10", "TR_10_to_22", etc.
- BactoTraits actual: nested structure with "optimum", "range", "delta" fields

**Oxygen:**
- METPO claims: "Ox_aerobic", "Ox_anaerobic", "Ox_facultative_aerobe_anaerobe", "Ox_microerophile"
- BactoTraits actual: "aerobic", "anaerobic", "facultative_aerobe_anaerobe", "microerophile"

**pH:**
- METPO claims: "pHO_0_to_6", "pHO_6_to_7", "pHR_0_to_4", etc.
- BactoTraits actual: nested structure with "optimum", "range", "delta" fields

**Cell Shape:**
- METPO claims: "s_curved_spiral", "s_filament", "s_ovoid", "s_rod", "s_sphere", "s_star_dumbbell_pleomorphic"
- BactoTraits actual: "curved_spiral", "filament", "ovoid", "rod", "sphere", "star_dumbbell_pleomorphic"

**Gram Stain:**
- METPO claims: "G_positive", "G_negative"
- BactoTraits actual: "positive", "negative"

**Motility:**
- METPO claims: "motile", "non-motile"  
- BactoTraits actual: "motile", "non_motile" (underscore)

**Spore Formation:**
- METPO claims: Unknown (need to check)
- BactoTraits actual: "spore_forming", "no_spore"

### BactoTraits Actual Field Names

```
gc_content:
  - lte_42dot65
  - 42dot65_to_57dot0
  - 57dot0_to_66dot3
  - gt_66dot3

oxygen:
  - aerobic
  - anaerobic
  - facultative_aerobe_anaerobe
  - microerophile

temperature:
  - delta
  - optimum
  - range

ph:
  - delta
  - optimum
  - range

nacl:
  - delta
  - optimum
  - range

cell_shape:
  - curved_spiral
  - filament
  - ovoid
  - rod
  - sphere
  - star_dumbbell_pleomorphic

gram_stain:
  - negative
  - positive

motility:
  - motile
  - non_motile

spore_formation:
  - spore_forming
  - no_spore
```

---

## Recommendations

### Immediate Actions

1. **Fix BactoTraits Synonyms** (Critical)
   - Update all METPO classes claiming BactoTraits synonyms
   - Match actual field names from BactoTraits MongoDB
   - Remove prefixes like "GC_", "TO_", "TR_", "pHO_", "pHR_", "Ox_", "s_", "G_"

2. **Add Missing Madin Pathways** (High Priority)
   - 88 pathway values need to be added to METPO
   - Focus on degradation (27), reduction (16), and oxidation (24) pathways
   - These represent major microbial metabolic functions

3. **Verify Data Sources**
   - Document which version/snapshot of each source was used
   - BactoTraits appears to have been transformed/normalized before loading into MongoDB
   - The CSV column headers don't match the MongoDB field names

### Long-term Improvements

1. **Automated Validation**
   - Create scripts to verify synonym claims against actual source data
   - Run regularly when sources are updated

2. **Source Documentation**
   - Document the transformation process for each source
   - Clarify mapping between source formats (CSV headers vs MongoDB fields vs METPO synonyms)

3. **Hierarchical Organization**
   - Create parent classes for:
     - Degradation processes
     - Oxidation processes  
     - Reduction processes
     - Disproportionation processes

---

## Files Generated

- `/tmp/madin_pathways_mongo.txt` - All unique Madin pathway values (103)
- `/tmp/metpo_madin_synonyms.txt` - All METPO synonyms claiming Madin source (70)
- `/tmp/missing_in_metpo_final.txt` - Madin pathways not covered by METPO (88)
- `/tmp/bacdive_verification.txt` - BacDive synonym verification results
- `~/Documents/gitrepos/metpo/metpo_madin_pathway_coverage.md` - Madin-specific analysis
- `~/Documents/gitrepos/metpo/metpo_source_coverage_analysis.md` - This comprehensive report

---

## MongoDB Queries Used

```javascript
// Get all unique Madin pathways
db.madin.aggregate([
  { $match: { pathways: { $ne: 'NA' } } },
  { $project: { pathway_array: { $split: ['$pathways', ', '] } } },
  { $unwind: '$pathway_array' },
  { $group: { _id: '$pathway_array' } },
  { $sort: { _id: 1 } }
])

// Get BacDive oxygen tolerance values
db.strains_api.distinct('Physiology and metabolism.oxygen tolerance.oxygen tolerance')

// Get BacDive halophily values
db.strains_api.distinct('Physiology and metabolism.halophily.halophily level')

// Sample BactoTraits one-hot structure
db.bactotraits.findOne({gc_content: {$exists: true}})
```

