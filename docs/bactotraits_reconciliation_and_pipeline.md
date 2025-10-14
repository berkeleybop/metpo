# BactoTraits Data Pipeline and METPO Reconciliation

**Date:** 2025-10-14
**Purpose:** To provide a single, authoritative document explaining the BactoTraits data pipeline, from the original provider CSV to MongoDB, and to clarify the reconciliation status with the METPO ontology.

---

## 1. Executive Summary

This document consolidates the findings from multiple previous analyses. The key takeaway is:

**METPO's synonyms for BactoTraits are correct.** They accurately reflect the column headers in the original provider CSV file. The confusion in previous analyses stemmed from a transformation step that sanitizes field names during the import into MongoDB.

- **Coverage:** After accounting for the transformation, METPO's synonyms provide **69.5%** coverage for BactoTraits fields (73 out of 105).
- **Trait Field Coverage:** Excluding non-trait fields (like taxonomy and IDs), the coverage is **62.8%** (59 out of 94 trait fields).
- **Remaining Gaps:** There are 32 fields from BactoTraits that are legitimately not yet in METPO. These represent opportunities for expansion.

---

## 2. The BactoTraits Data Pipeline

The BactoTraits data moves through two main stages, each with its own format. Understanding this pipeline is crucial to understanding the reconciliation analysis.

### Stage 1: The Provider CSV File

- **File:** `BactoTraits_databaseV2_Jun2022.csv`
- **Source:** ORDaR (University of Lorraine)
- **Format:** Semicolon-delimited CSV with a 3-row header.
- **Field Names:** The **third row** of the header contains the column names. These names often include spaces, comparison operators (`<=`, `>`), and periods (`.`).
- **METPO Alignment:** METPO's synonyms for BactoTraits are correctly based on this original set of field names.

### Stage 2: The MongoDB Collection

- **Collection:** `bactotraits.bactotraits`
- **Transformation:** Before being imported into MongoDB, the field names from the CSV are **sanitized** to make them compatible with the database and easier to query.
- **Sanitization Rules:**
    1.  Leading/trailing whitespace is stripped.
    2.  Comparison operators are converted to text (e.g., `<=` becomes `_lte_`).
    3.  Periods and hyphens are replaced with underscores.
    4.  Spaces are replaced with underscores.

### Example Transformation

| Provider CSV Header | Sanitized MongoDB Field Name |
|---------------------|------------------------------|
| ` GC_42.65_57.0`    | `GC_42_65_57_0`              |
| `pHd_<=1`           | `pHd_lte_1`                  |
| `non-motile`        | `non_motile`                 |

This transformation is the source of the previously reported "mismatch." The mismatch is not with METPO's synonyms, but between the original source file and its database representation.

---

## 3. METPO Reconciliation and Gap Analysis

With the data pipeline clarified, here is the accurate state of METPO's coverage for BactoTraits.

### Successfully Mapped Fields (73/105)

METPO correctly provides synonyms for 73 of the original BactoTraits fields, including:
- **Temperature Bins:** `TO_10_to_22`, `TR_27_to_30`, etc.
- **pH Bins:** `pHO_0_to_6`, `pHR_4_to_6`, etc.
- **NaCl Bins:** `NaO_1_to_3`, `NaR_3_to_8`, etc.
- **GC Content Bins:** `GC_57.0_66.3`, etc.
- **Oxygen Preference:** `Ox_aerobic`, `Ox_anaerobic`, etc.
- **Morphology:** `G_positive`, `motile`, `S_rod`, etc.
- **Trophic Types:** `TT_autotroph`, `TT_heterotroph`, etc.

### Remaining Gaps: Fields to Add to METPO (32 fields)

These fields are present in BactoTraits but do not yet have a corresponding synonym or class in METPO.

#### High-Value Gaps (10 fields)
These have small, controlled vocabularies and are excellent candidates for new ontology classes.
- **Pigment Fields:** `Pigment_yellow`, `Pigment_pink`, `Pigment_white`, `Pigment_black`, `Pigment_green`, `Pigment_orange`, `Pigment_brown`, `Pigment_cream`, `Pigment_red`, `Pigment_carotenoid`.

#### Low-Value Gaps (22 fields)
These are mostly binary (0/1) fields representing specific trait bins.
- **Cell Size Bins:** `L_1_3_2`, `L_2_3`, `L_lte_1_3`, `L_gt_3`, `W_0_5_0_65`, `W_0_65_0_9`, `W_lte_0_5`, `W_gt_0_9`
- **Sporulation:** `spore`, `no_spore`
- **Trophic Type:** `TT_copiotroph_diazotroph`
- **And various boundary bins** for Temperature, NaCl, pH, and GC content.

### Excluded Fields (11 fields)
These fields are identifiers or taxonomic ranks and are correctly excluded from the trait ontology.
- `Bacdive_ID`, `ncbitaxon_id`, `Full_name`, `Species`, `Genus`, etc.

---

## 4. Conclusion and Action Plan

- **Conclusion:** The reconciliation status between BactoTraits and METPO is healthy. The perceived mismatch was due to a misunderstanding of the data pipeline.
- **Action Plan:**
    1.  Prioritize adding the 10 "High-Value Gap" pigment fields to METPO.
    2.  Systematically add the remaining 22 "Low-Value Gap" fields to complete coverage.
    3.  Consolidate and archive the outdated analysis documents that reported this issue incorrectly.
