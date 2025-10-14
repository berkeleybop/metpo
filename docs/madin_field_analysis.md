# Madin et al. MongoDB Field Analysis

**Date:** 2025-10-03
**Collection:** `madin.madin`
**Total Documents:** 172,324

---

## Overview

Analysis of all 35 fields in the Madin collection, including unique value counts, NA distribution, and categorical value enumeration.

---

## Field Summary Table

| Field | Unique Values | NA Count | Non-NA Count | % Complete | Type |
|-------|--------------|----------|--------------|------------|------|
| **Taxonomy Fields** |
| superkingdom | 2 | 0 | 172,324 | 100.0% | Categorical |
| phylum | 75 | 85 | 172,239 | 100.0% | Categorical |
| class | 95 | 1,975 | 170,349 | 98.9% | Categorical |
| order | 212 | 1,862 | 170,462 | 98.9% | Categorical |
| family | 481 | 2,487 | 169,837 | 98.6% | Categorical |
| genus | 2,885 | 1,566 | 170,758 | 99.1% | Categorical |
| species | 21,500 | 0 | 172,324 | 100.0% | Categorical |
| org_name | 116,704 | 9,293 | 163,031 | 94.6% | Text |
| tax_id | 49,155 | 0 | 172,324 | 100.0% | Numeric ID |
| species_tax_id | 21,500 | 0 | 172,324 | 100.0% | Numeric ID |
| **Phenotypic Traits** |
| gram_stain | 3 | 128,126 | 44,198 | 25.7% | Categorical |
| metabolism | 8 | 137,737 | 34,587 | 20.1% | Categorical |
| pathways | 161 | 156,328 | 15,996 | 9.3% | **Comma-separated list** |
| carbon_substrates | 3,978 | 167,640 | 4,684 | 2.7% | Comma-separated list |
| sporulation | 3 | 153,242 | 19,082 | 11.1% | Categorical |
| motility | 6 | 149,559 | 22,765 | 13.2% | Categorical |
| cell_shape | 20 | 143,987 | 28,337 | 16.4% | Categorical |
| **Environmental Ranges** |
| range_tmp | 8 | 163,525 | 8,799 | 5.1% | Categorical |
| range_salinity | 8 | 171,402 | 922 | 0.5% | Categorical |
| isolation_source | 75 | 120,345 | 51,979 | 30.2% | Categorical |
| **Quantitative Traits** |
| optimum_tmp | 189 | 157,124 | 15,200 | 8.8% | Numeric |
| optimum_ph | 131 | 167,720 | 4,604 | 2.7% | Numeric |
| growth_tmp | 341 | 158,659 | 13,665 | 7.9% | Numeric |
| doubling_h | 651 | 171,190 | 1,134 | 0.7% | Numeric |
| **Cell Dimensions** |
| d1_lo | 152 | 167,344 | 4,980 | 2.9% | Numeric |
| d1_up | 72 | 170,528 | 1,796 | 1.0% | Numeric |
| d2_lo | 246 | 167,326 | 4,998 | 2.9% | Numeric |
| d2_up | 121 | 170,262 | 2,062 | 1.2% | Numeric |
| **Genomic Traits** |
| genome_size | 87,040 | 63,765 | 108,559 | 63.0% | Numeric |
| gc_content | 9,753 | 142,942 | 29,382 | 17.1% | Numeric |
| coding_genes | 5,889 | 154,793 | 17,531 | 10.2% | Numeric |
| rRNA16S_genes | 18 | 165,078 | 7,246 | 4.2% | Numeric |
| tRNA_genes | 151 | 159,459 | 12,865 | 7.5% | Numeric |
| **Metadata** |
| data_source | 26 | 0 | 172,324 | 100.0% | Categorical |
| ref_id | 20,277 | 11,032 | 161,292 | 93.6% | Numeric ID |

---

## Categorical Field Values

### Superkingdom (2 values)
- Archaea
- Bacteria

### Gram Stain (2 values + NA)
- negative
- positive
- **NA:** 128,126 (74.3%)

### Sporulation (2 values + NA)
- no
- yes
- **NA:** 153,242 (88.9%)

### Motility (5 values + NA)
- axial filament
- flagella
- gliding
- no
- yes
- **NA:** 149,559 (86.8%)

### Metabolism (7 values + NA)
- aerobic
- anaerobic
- facultative
- microaerophilic
- obligate aerobic
- obligate anaerobic
- strictly anaerobic
- **NA:** 137,737 (79.9%)

**METPO Coverage Analysis:**
- METPO has oxygen tolerance/preference classes
- Overlap with BacDive oxygen tolerance terms
- Some Madin metabolism values may map to existing METPO classes

### Temperature Range (7 values + NA)
- extreme thermophilic
- facultative psychrophilic
- mesophilic
- psychrophilic
- psychrotolerant
- thermophilic
- thermotolerant
- **NA:** 163,525 (94.9%)

**METPO Coverage:** Need to assess if METPO has temperature preference classes

### Salinity Range (7 values + NA)
- euryhaline
- extreme-halophilic
- halophilic
- halotolerant
- moderate-halophilic
- non-halophilic
- stenohaline
- **NA:** 171,402 (99.5%)

**METPO Coverage:** BacDive halophily terms cover some of these (halophilic, halotolerant, etc.)

### Cell Shape (19 values + NA)
- bacillus
- branced
- coccobacillus
- coccus
- disc
- filament
- flask
- fusiform
- irregular
- pleomorphic
- ring
- spindle
- spiral
- spirochete
- square
- star
- tailed
- triangular
- vibrio
- **NA:** 143,987 (83.6%)

**METPO Coverage:** BactoTraits has cell shape categories (curved_spiral, filament, ovoid, rod, sphere, star_dumbbell_pleomorphic)
- Potential overlap/mapping needed between Madin and BactoTraits cell shape terms

### Isolation Source (74 values + NA)

**Top-level categories:**
- **Host-associated (26):** host_animal_endotherm_*, host_plant_*, host_fungus, host_algae
- **Aquatic (21):** water_*, sediment_*
- **Terrestrial (9):** soil_*
- **Built/Industrial (5):** bioreactor, wastewater, sludge, built_environment_surfaces, compost
- **Other (13):** biofilm, food, petroleum, rock, volcanic_active, hypersaline, etc.

**Full list:**
- biofilm
- bioreactor
- bioreactor/digester
- built_environment_surfaces
- compost
- food
- food_fermented
- host
- host_algae
- host_animal
- host_animal_ectotherm
- host_animal_endotherm
- host_animal_endotherm_blood
- host_animal_endotherm_feces
- host_animal_endotherm_intestinal
- host_animal_endotherm_intratissue
- host_animal_endotherm_nasopharyngeal
- host_animal_endotherm_oral
- host_animal_endotherm_rumen
- host_animal_endotherm_surface
- host_animal_endotherm_vagina
- host_fungus
- host_plant
- host_plant_leaf-associated
- host_plant_root-associated
- host_plant_rootnodule
- host_plant_vasculature
- hypersaline
- litter
- milk
- other
- petroleum
- plant
- rock
- rock_deep
- rock_surface
- sediment
- sediment_brackish
- sediment_fresh
- sediment_fresh_alkaline
- sediment_hypersaline
- sediment_marine
- sediment_marine_cold
- sediment_marine_deep
- sediment_marine_hydrothermal
- sludge
- soil
- soil_agricultural
- soil_arid
- soil_contaminated
- soil_forest
- soil_grassland
- soil_hydrocarbon_contaminated
- soil_marshland
- soil_mineral
- soil_organic_peat
- soil_organic_permafrost
- soil_saline
- volcanic_active
- wastewater
- water
- water_brackish
- water_fresh
- water_fresh_alkaline
- water_fresh_cold
- water_groundwater
- water_groundwater_deepsubsurface
- water_groundwater_surface
- water_hotspring
- water_hypersaline
- water_marine
- water_marine_cold
- water_marine_deep
- water_marine_hydrothermal

**NA:** 120,345 (69.8%)

**METPO Coverage:** Should map to ENVO terms rather than creating METPO classes

### Data Source (26 values, no NA)

**Complete list:**
- amend-shock
- bacdive-microa
- campedelli
- corkrey
- edwards
- engqvist
- faprotax
- fierer
- genbank
- gold
- jemma-refseq
- kegg
- kremer
- masonmm
- mediadb
- methanogen
- microbe-directory
- nielsensl
- pasteur
- patric
- prochlorococcus
- protraits
- roden-jin
- rrndb
- schulz-jorgensen
- silva

**Note:** This is the 26 sources mentioned in the Madin et al. 2020 paper

---

## Pathways Field Analysis

**Statistics:**
- **Unique combined values:** 161 (but this is misleading - see below)
- **Unique individual pathway values:** 103 (from previous analysis)
- **Records with pathway data:** 15,996 (9.3%)
- **Records with NA:** 156,328 (90.7%)

**Structure:** Comma-separated list of pathway values

**METPO Coverage (from issue #223 analysis):**
- 15/103 pathways covered (14.6%)
- 88 pathways missing
- Categories of missing pathways:
  - 27 degradation pathways
  - 24 oxidation pathways
  - 16 reduction pathways
  - 2 disproportionation
  - 2 nitrogen cycle
  - 2 methanogenesis subtypes

---

## Data Completeness Analysis

### High Completeness (>90%)
1. **Taxonomy:** superkingdom, phylum, class, order, family, genus, species (98-100%)
2. **IDs:** tax_id, species_tax_id, org_name, ref_id (94-100%)
3. **Genomic:** genome_size (63%)

### Medium Completeness (10-50%)
1. **Phenotypic:** gram_stain (26%), metabolism (20%), cell_shape (16%), sporulation (11%), motility (13%)
2. **Environmental:** isolation_source (30%)
3. **Quantitative:** optimum_tmp (9%), coding_genes (10%)

### Low Completeness (<10%)
1. **Pathways:** 9.3% ⚠️ **Critical for METPO**
2. **Growth parameters:** range_tmp (5%), optimum_ph (3%), growth_tmp (8%), doubling_h (0.7%)
3. **Salinity:** range_salinity (0.5%)
4. **Cell dimensions:** d1_lo, d1_up, d2_lo, d2_up (1-3%)
5. **Carbon substrates:** 2.7%

---

## METPO Coverage Implications

### Fields with Direct METPO Relevance

#### 1. Pathways (9.3% complete)
- **Status:** 15/103 values covered, 88 missing
- **Priority:** HIGH - core metabolic functions
- **Action:** Add missing degradation, oxidation, reduction pathways

#### 2. Metabolism (20.1% complete)
- **Values:** aerobic, anaerobic, facultative, microaerophilic, obligate aerobic, obligate anaerobic, strictly anaerobic
- **Overlap:** Similar to BacDive oxygen tolerance
- **Status:** Need to verify METPO coverage
- **Note:** Some redundancy with pathways field

#### 3. Gram Stain (25.7% complete)
- **Values:** positive, negative
- **BactoTraits overlap:** Yes (G_positive, G_negative in BactoTraits claims)
- **Status:** Should be covered

#### 4. Cell Shape (16.4% complete)
- **Values:** 19 distinct shapes
- **BactoTraits overlap:** Partial (6 categories in BactoTraits)
- **Mapping needed:** Madin → BactoTraits → METPO

#### 5. Sporulation (11.1% complete)
- **Values:** yes, no
- **BactoTraits overlap:** Yes (spore_forming, no_spore)
- **Status:** Should be covered

#### 6. Motility (13.2% complete)
- **Values:** yes, no, flagella, gliding, axial filament
- **BactoTraits overlap:** Partial (motile, non_motile)
- **Note:** Madin has more granular motility types

#### 7. Temperature Range (5.1% complete)
- **Values:** mesophilic, thermophilic, psychrophilic, etc.
- **Status:** Need to check METPO coverage for temperature preference

#### 8. Salinity Range (0.5% complete)
- **Values:** halophilic, halotolerant, non-halophilic, etc.
- **BacDive overlap:** Yes (halophily field in BacDive)
- **Status:** Should be covered via BacDive synonyms

### Fields Better Covered by Other Ontologies

#### 9. Isolation Source (30.2% complete)
- **Recommendation:** Map to ENVO (Environment Ontology)
- **Note:** 74 controlled vocabulary terms already aligned with ENVO structure

#### 10. Carbon Substrates (2.7% complete)
- **Recommendation:** Map to ChEBI (Chemical Entities of Biological Interest)
- **Note:** 3,978 unique values (likely compound names)

---

## Cross-Source Comparison

### Madin vs BacDive vs BactoTraits

| Trait | Madin Field | BacDive Field | BactoTraits Field | Coverage |
|-------|-------------|---------------|-------------------|----------|
| Oxygen preference | metabolism | oxygen tolerance | oxygen | All 3 sources |
| Salt preference | range_salinity | halophily | nacl (range) | All 3 sources |
| Cell shape | cell_shape | - | cell_shape | Madin + BactoTraits |
| Gram stain | gram_stain | - | gram_stain | Madin + BactoTraits |
| Motility | motility | - | motility | Madin + BactoTraits |
| Sporulation | sporulation | - | spore_formation | Madin + BactoTraits |
| Temperature range | range_tmp | - | temperature (range) | Madin + BactoTraits |
| pH | optimum_ph | - | ph (optimum/range) | Madin + BactoTraits |
| GC content | gc_content | - | gc_content | Madin + BactoTraits |
| Pathways | pathways | - | - | **Madin only** ⚠️ |

**Key Finding:** Pathways field is unique to Madin - this is why those 88 missing pathway values are critical to add to METPO.

---

## Recommendations

### Immediate Actions

1. **Verify METPO coverage for Madin categorical fields:**
   - metabolism (7 values)
   - range_tmp (7 values)
   - cell_shape (19 values)
   - motility (5 values)

2. **Cross-reference with BactoTraits:**
   - Map Madin cell_shape → BactoTraits cell_shape
   - Compare metabolism → oxygen preference terms
   - Align sporulation/motility terminology

3. **Add missing pathways (priority from issue #223):**
   - 88 pathway values not currently in METPO

### Medium-term Improvements

4. **Create mapping tables:**
   - Madin isolation_source → ENVO
   - Madin carbon_substrates → ChEBI
   - Madin cell_shape → BactoTraits cell_shape → METPO

5. **Document data source relationships:**
   - Which Madin fields overlap with BacDive?
   - Which are unique to Madin?
   - Which should use external ontologies (ENVO, ChEBI)?

### Questions for Clarification

- Should METPO cover temperature preference categories (mesophilic, thermophilic, etc.)?
- Should METPO have detailed motility types (flagella, gliding, axial filament)?
- Or should these be in separate, more specialized ontologies?
- What's the strategy for low-completeness fields (range_salinity at 0.5%)?

---

## MongoDB Queries Used

```javascript
// Count total documents
db.madin.countDocuments()

// Get all unique fields from sample
db.madin.aggregate([{$sample: {size: 100}}])

// Count unique values per field
db.madin.distinct('field_name').length

// Count NA vs non-NA
db.madin.countDocuments({field_name: 'NA'})
db.madin.countDocuments({field_name: {$ne: 'NA'}})

// Get all distinct values for categorical fields
db.madin.distinct('field_name').filter(v => v !== 'NA').sort()
```
