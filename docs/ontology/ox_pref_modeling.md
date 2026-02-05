# Report on Oxygen Preference Phenotype Modeling

**Author:** Mark Miller  
**Date:** August 2025

---

## 1. Data Provenance

### 1.1 Madin et al. dataset

- **Source:** Madin et al. (CSV file provided in supplementary materials).

- **Method:** Loaded into **MongoDB**, then used **Atlas Natural Language Query Generator** to produce aggregation pipeline.

- **Pipeline:**
  
  `[
    { $group: { _id: "$metabolism", count: { $sum: 1 } } },
    { $sort: { _id: 1 } }
  ]` 

- **Results (`madin.madin.metabolism.counts.csv`):**
  
  | _id                | count   |
  | ------------------ | ------- |
  | NA                 | 137,737 |
  | aerobic            | 12,062  |
  | anaerobic          | 7,232   |
  | facultative        | 8,567   |
  | microaerophilic    | 2,735   |
  | obligate aerobic   | 3,569   |
  | obligate anaerobic | 421     |
  | strictly anaerobic | 1       |

---

### 1.2 BacDive dataset

- **Source:** BacDive database, field `Physiology and metabolism.oxygen tolerance`.

- **Method:** Queried `oxygen tolerance` attribute in MongoDB; flattened arrays with `$unwind`.

- **Pipeline:**
  
  `[
    { $match: { "Physiology and metabolism.oxygen tolerance": { $exists: true } } },
    { $project: { oxygen_tolerance: "$Physiology and metabolism.oxygen tolerance.oxygen tolerance" } },
    { $unwind: { path: "$oxygen_tolerance" } },
    { $group: { _id: "$oxygen_tolerance", count: { $sum: 1 } } },
    { $sort: { count: -1 } }
  ]` 

- **Results (`bacdive.strains.oxtol.counts.csv`):**
  
  | _id                  | count  |
  | -------------------- | ------ |
  | aerobe               | 10,338 |
  | anaerobe             | 5,790  |
  | microaerophile       | 4,724  |
  | facultative anaerobe | 4,484  |
  | obligate aerobe      | 3,346  |
  | obligate anaerobe    | 224    |
  | facultative aerobe   | 106    |
  | aerotolerant         | 21     |
  | microaerotolerant    | 5      |

---

## 2. Using MongoDB Atlas AI for Natural Language Queries

- **Account setup:**
  
  - Go to [MongoDB Atlas](https://www.mongodb.com/atlas) and create a **free account**.
  
  - You can authenticate with a Google account.
  
  - Default project/cluster settings are sufficient for small-scale data exploration.

- **Compass integration:**
  
  - Download and install **MongoDB Compass** (GUI).
  
  - Connect Compass to your Atlas cluster using the connection string from Atlas.
  
  - In Compass, go to **Settings → Artificial Intelligence** and sign in with your Atlas account.

- **Using natural language queries:**
  
  - Once authenticated, you can enter English prompts in the Compass **Aggregation** tab.
  
  - Example:
    
    > *"tabulate the unique values of the metabolism field"*
  
  - The AI will generate the corresponding MongoDB aggregation pipeline, which you can run or modify.
  
  - Pipelines can be exported as JSON, saved to files, or executed directly on your Atlas data.

- **Limitations:**
  
  - Atlas AI tends to omit rows with `null` values when grouping.
  
  - Explicit `"NA"` values in CSVs (as in Madin) will appear in results.
  
  - The feature requires an active internet connection to Atlas; it is not available in offline/local-only Compass.

---

## 3. Ontological Modeling Goals

*(unchanged, as in earlier version)*

---

## 4. Phenotype Classes and Hierarchy

*(unchanged, with the 9 existing + 2 newly minted classes `1000611` and `1000612`)*

---

## 5. Source Term Coverage

*(all Madin and BacDive terms are accounted for, with synonyms explicitly marked)*

---

## 6. ROBOT Template Integration

- **Multi-template approach:** The oxygen phenotypes are now integrated into METPO's modular build system using multiple Google Sheets tabs.

- **Current templates:**
  - **Main classes**: `metpo_sheet.tsv` (gid=355012485) - includes the oxygen phenotypes in the minimal classes set
  - **Synonyms**: `metpo-synonyms.tsv` (gid=907926993) 
  - **Properties**: `metpo-properties.tsv` (gid=2094089867)

- **Build process:** Each template is downloaded separately and processed by ROBOT template, then merged into the final ontology via the `OTHER_SRC` variable in the ODK Makefile.

- **Coverage:** The 11 oxygen preference classes (9 existing + 2 new IDs 1000611, 1000612) are included in the minimal classes sheet, with synonyms moved to the dedicated synonyms sheet.

---

## 7. Next Steps

1. **✅ COMPLETED:** Merge new IDs into production ontology via modular template system.

2. **Build integration:** The multi-template approach (branch `182-break-the-metpo-robot-template-in-googel-sheets-into-multiple-templates-especially-for-mappings`) successfully separates:
   - Comprehensive classes sheet (gid=1427185859) - disabled as too comprehensive 
   - Minimal classes sheet (gid=355012485) - contains oxygen phenotypes
   - Synonyms sheet (gid=907926993) - contains BacDive/Madin mappings
   - Properties sheet (gid=2094089867) - annotation properties like IAO_0000115

3. **Review synonym scope** - now handled in dedicated synonyms template (decide if BacDive organism-type strings should be `exact` vs `related`).

4. **Publish update** to GitHub repo.

5. **Diagramming** oxygen preference hierarchy for team review.

6. **Future work:** 
   - Hybrid oxygen preferences (e.g., "anaerobe/facultative aerobe")
   - Additional phenotype domains can be added as separate template sheets
