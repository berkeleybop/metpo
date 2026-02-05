# Report on Temperature Preference Phenotype Modeling  
**Author:** Mark Miller  
**Date:** August 2025  

---

## 1. Data Provenance

### 1.1 Madin et al. dataset
- Fields examined:  
  - `growth_tmp` (mostly “NA”, some integers)  
  - `optimum_tmp` (mostly “NA”, some numeric values)  
  - `range_tmp` (mostly “NA”, occasional categorical strings like *mesophilic*)  
- Interpretation:  
  - Madin reports **numeric growth/optimum temperatures**, with some **categorical labels**.  
  - *Mesophilic* appears as the most consistent categorical value in `range_tmp`.  

### 1.2 BacDive dataset
- Field: `Culture and growth conditions.culture temp` → numeric values (°C).  
- Keywords field: categorical descriptors such as:  
  - *mesophilic* (42,236)  
  - *thermophilic* (1,530)  
  - *psychrophilic* (1,190)  
  - *hyperthermophilic* (179)  

### 1.3 BactoTraits dataset
- Temperature traits expressed as **one-hot encoded bins**:  
  - **Optimum temperature** (`TO_<=10`, `TO_10_to_22`, …, `TO_>40`)  
  - **Range temperature** (`TR_<=10`, `TR_10_to_22`, …, `TR_>40`)  
  - **Delta (tolerance breadth)** (`Td_1_5`, `Td_5_10`, …, `Td_>30`)  
- Provides more **fine-grained, numeric binning** than BacDive or Madin categorical strings.  

---

## 2. Ontological Modeling Goals

- Establish a **temperature preference phenotype scaffold** in METPO parallel to the oxygen scaffold.  
- Ensure BacDive categorical keywords map cleanly.  
- Reserve space for BactoTraits fine-grained bins without collapsing them into broad categories.  
- Support both **categorical classes** (psychrophilic, mesophilic, thermophilic, hyperthermophilic, tolerant forms) and **numeric-derived classes** (optimum, range, delta bins).  

---

## 3. Phenotype Classes and Hierarchy

### 3.1 New parent class
- **`1000613` → temperature preference phenotype**  
  - Parent for all categorical and tolerance classes.  

### 3.2 Categorical preference classes
- `1000614` → psychrophilic  
- `1000615` → mesophilic  
- `1000616` → thermophilic  
- `1000617` → hyperthermophilic  

### 3.3 Tolerance classes
- `1000618` → psychrotolerant  
- `1000619` → thermotolerant  

---

## 4. Source Term Coverage

### 4.1 BacDive keywords
- *mesophilic* → ✅ `mesophilic` (1000615)  
- *thermophilic* → ✅ `thermophilic` (1000616)  
- *psychrophilic* → ✅ `psychrophilic` (1000614)  
- *hyperthermophilic* → ✅ `hyperthermophilic` (1000617)  

➡️ All BacDive temperature keywords map exactly to new METPO classes.  

### 4.2 Madin
- *mesophilic* observed in `range_tmp` → ✅ `mesophilic` (1000615).  
- Numeric optimum/range values will be useful for binning but don’t require new categorical classes.  

### 4.3 BactoTraits
- Provides structured bins (optimum, range, delta).  
- These do **not** yet exist in METPO — new classes will need to be minted under separate parents:  
  - *optimum temperature phenotype*  
  - *growth temperature range phenotype*  
  - *temperature tolerance breadth phenotype*  

---

## 5. ROBOT Template Output

- A template file `temperature_preference_categorical.tsv` was generated.  
- Includes parent + 6 subclasses with BacDive synonyms and one Madin synonym.  
- Follows the 2-row header layout used for oxygen phenotypes.  

---

## 6. Next Steps

1. **Create fine-grained classes** for BactoTraits bins (optimum, range, delta) under new parents.  
2. **Build mappings**:  
   - BacDive keyword → METPO categorical phenotype  
   - BactoTraits bin → METPO fine-grained phenotype  
3. **Annotate numeric values** from Madin and BacDive with properties (e.g., `hasOptimumTemperature`, `hasGrowthRangeTemperature`).  
4. Extend scaffold to hybrid cases if found (e.g., “psychrophile/mesophile”).  

---

✅ With this work, METPO now has a clear categorical temperature phenotype hierarchy, aligned with BacDive keywords and extendable to fine-grained BactoTraits bins.  
