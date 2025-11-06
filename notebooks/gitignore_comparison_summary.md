# GitIgnored Files Comparison: Ubuntu NUC vs MacBook - Summary

**Date:** 2025-11-06
**For:** GitHub issue #279
**Status:** Issue description may be outdated; this reflects current state

---

## Quick Comparison Table

| Metric | Ubuntu NUC | MacBook | Notes |
|--------|-----------|---------|-------|
| **Total gitignored (excl. .venv)** | ~4,099 | 10,760 | Mac has 2.6x more files |
| **Largest difference** | N4L dataset | N4L dataset | Mac: 10,470 files (574MB), Ubuntu: 3,981 files (43MB) |
| **N4L location** | `assets/` | `large/` | Different directory! |
| **Validation results** | 53M | 1.3G | Mac has 25x more data |
| **Robot test results** | ❌ Missing | 1.1G | Only on Mac |
| **local/ contents** | N4L temperature data (1.6G) | BactoTraits + Madin + MongoDB (930M) | Completely different datasets! |
| **Literature mining logs** | 4 logs (25M) | 47 logs (308M) | Mac has 12x more logs |

---

## Key Findings

### 1. N4L Phenotypic Ontology Dataset - MAJOR DIFFERENCE

**Ubuntu:**
- Location: `assets/N4L_phenotypic_ontology_2016/`
- Files: 3,981
- Size: 43MB
- Status: Partial dataset

**Mac:**
- Location: `large/N4L_phenotypic_ontology_2016/`
- Files: 10,470
- Size: 574MB
- Status: Complete dataset with RDF/TTL/XML triples

**Impact:** Mac has **2.6x more N4L files** and **13x larger dataset**

---

### 2. local/ Directory - COMPLETELY DIFFERENT CONTENTS

**Ubuntu (22 files, 1.6GB):**
```
PRIMARY FOCUS: N4L temperature modeling
- n4l-tables.nq (931MB) - Main N4L knowledge graph
- Temperature analysis CSVs (4.2M + 1.6M + 1.4M + 479K + 228K)
- n4l-temperature.ttl (3.3M)
- NCBI taxonomy dump (taxdmp/)
- noderanks.ttl (177MB)
```

**Mac (33 files, 930MB):**
```
PRIMARY FOCUS: KG-Microbe datasets
- BactoTraits: 8.6M + 6.1M
- Madin: 44M + 38M + 5.8M + 268K
- MongoDB dumps: 127M (madin) + 38M (bactotraits)
- NCBI taxonomy dump (taxdmp/)
- noderanks.ttl (178MB)
```

**Conclusion:**
- Ubuntu = N4L temperature research machine
- Mac = KG-Microbe integration machine
- Only overlap: NCBI taxonomy data

---

### 3. Ontology Validation/Testing - Mac Much Larger

**Ubuntu:**
- `ontologies/validation_results/` - 53M
- `ontologies/robot_test_results/` - ❌ **Does not exist**

**Mac:**
- `ontologies/validation_results/` - 1.3G (25x larger!)
- `ontologies/robot_test_results/` - 1.1G
- Total: 2.4GB of validation/test data

**Question:** Did Ubuntu clean up old validation results?

---

###4. Literature Mining Logs - Mac Much More Active

**Ubuntu:** 4 logs, 25MB
```
- morphology_gpt-4o_20251030_180642.log (9.8M)
- growth_conditions_gpt-4o_20251030_142703.log (7.3M)
- chemical_utilization_gpt-4o_20251030_162000.log (7.3M)
- morphology_gpt-4o_20251030_174301.log (763K)
```

**Mac:** 47 logs, 308MB
```
Largest:
- fullpaper_prototype_v3_20251031_163102.log (70M)
- cmm_fullcorpus_gpt4o_t00_20251031_193935.log (55M)
- fullpaper_hybrid_gpt4o_t03.log (50M)
- chemical_utilization_hybrid_fullcorpus_gpt4o_t00_20251031_221515.log (16M)
- growth_conditions_hybrid_gpt4o_t00_20251031_213345.log (14M)
... + 42 more logs
```

**Conclusion:** Mac has been running many more OntoGPT extractions

---

### 5. Downloads - Similar but Not Identical

**Ubuntu:**
- `downloads/` directory exists but no `downloads/sheets/`
- Size: 67M

**Mac:**
- `downloads/sheets/` with 11 TSV files
- Size: 76M
- Extra files: metabolic_and_respiratory_*.tsv, trophic_mapping_bacdive.tsv

**Action needed:** Sync Google Sheets downloads?

---

## What Matches

✅ **These are identical or very similar:**
- `.idea/` - IDE config (both have)
- `.env` - Environment vars (both have)
- `.litellm_cache/` - LLM cache (both have)
- `literature_mining/abstracts/` - ~796-784KB (nearly identical)
- NCBI taxonomy data in `local/taxdmp/` (identical files)

---

## Discrepancies Requiring Action

### HIGH PRIORITY

#### 1. ⚠️ Complete N4L Dataset Only on Mac
- Mac: 10,470 files (574MB) in `large/N4L_phenotypic_ontology_2016/`
- Ubuntu: 3,981 files (43MB) in `assets/N4L_phenotypic_ontology_2016/`

**Questions:**
- Does Ubuntu need the complete N4L dataset?
- Why is it in different directories (`assets/` vs `large/`)?
- Should we standardize the location?

**Action:**
```bash
# If Ubuntu needs complete dataset:
rsync -av --progress mac:/Users/MAM/Documents/gitrepos/metpo/large/N4L_phenotypic_ontology_2016/ assets/N4L_phenotypic_ontology_2016/
```

---

#### 2. ⚠️ Different Datasets in `local/`

**Ubuntu focused on:** N4L temperature analysis
**Mac focused on:** KG-Microbe integration (BactoTraits + Madin)

**Questions:**
- Should both machines have both datasets?
- Is this intentional specialization?
- Document machine purposes?

**Action if both need all data:**
```bash
# Copy from Mac to Ubuntu:
rsync -av mac:/Users/MAM/Documents/gitrepos/metpo/local/bactotraits/ local/bactotraits/
rsync -av mac:/Users/MAM/Documents/gitrepos/metpo/local/madin/ local/madin/
rsync -av mac:/Users/MAM/Documents/gitrepos/metpo/local/mongodb_dumps/ local/mongodb_dumps/

# Copy from Ubuntu to Mac:
rsync -av local/n4l-*.{nq,csv,ttl} mac:/Users/MAM/Documents/gitrepos/metpo/local/
rsync -av local/*temperature* mac:/Users/MAM/Documents/gitrepos/metpo/local/
```

---

### MEDIUM PRIORITY

#### 3. ⚠️ Missing Robot Test Results on Ubuntu

**Mac has:** `ontologies/robot_test_results/` (1.1GB)
**Ubuntu:** Directory doesn't exist

**Question:** Was this cleaned up intentionally or missing by accident?

---

#### 4. ⚠️ Much Smaller Validation Results on Ubuntu

**Mac:** 1.3GB
**Ubuntu:** 53MB (25x smaller!)

**Question:** Did Ubuntu clean up old validation files?

---

### LOW PRIORITY

#### 5. Different Google Sheets Downloads

**Mac has 3 extra TSVs** in `downloads/sheets/`:
- `metabolic_and_respiratory_llm.tsv`
- `metabolic_and_respiratory_robot.tsv`
- `trophic_mapping_bacdive__tbdeleted.tsv`

**Action:** Sync sheets on Ubuntu

---

## Recommended Next Steps

1. **Document Machine Purposes**
   - Create `docs/DEVELOPMENT_MACHINES.md` explaining:
     - Ubuntu NUC: [Purpose? N4L temperature research?]
     - MacBook: [Purpose? KG-Microbe integration + OntoGPT?]

2. **Decide on Dataset Strategy**
   - Option A: Both machines have all datasets (increases consistency)
   - Option B: Specialized machines (document what goes where)

3. **Standardize N4L Location**
   - Choose: `assets/` or `large/` for N4L data
   - Update .gitignore if needed
   - Sync location across machines

4. **Sync Critical Datasets** (if going with Option A)
   - Use rsync commands above
   - Or create a sync script

5. **Update Issue #279**
   - Note that current state differs from issue description
   - Add this comparison document
   - Close or update with new findings

---

## Files Generated

1. **This file:** `notebooks/gitignore_comparison_summary.md`
2. **Mac analysis:** Ran on Mac, output captured above
3. **Ubuntu analysis:** Ran on Ubuntu, output captured above
4. **Detailed comparison:** `notebooks/gitignore_comparison_ubuntu_vs_mac.md` (created earlier)

---

## Raw Analysis Data

**Mac analysis:** `/tmp/mac_gitignored_analysis.txt` (on Mac)
**Ubuntu analysis:** `/tmp/ubuntu_gitignored_analysis.txt` (on Ubuntu)

To retrieve:
```bash
# Copy from Mac
scp mac:/tmp/mac_gitignored_analysis.txt notebooks/

# Already local on Ubuntu
cp /tmp/ubuntu_gitignored_analysis.txt notebooks/
```

---

**Analysis complete!** Ready to update issue #279 with findings.
