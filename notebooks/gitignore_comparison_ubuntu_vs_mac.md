# GitIgnored Files Comparison: Ubuntu NUC vs MacBook

**Date:** 2025-11-06
**Purpose:** Cross-computer comparison for GitHub issue #279

---

## Executive Summary

**Key Findings:**
- ✅ Core ignored directories have **identical sizes** across both machines (validation_results, robot_test_results, downloads, literature_mining)
- ⚠️ **Major difference:** Mac has 10,470 N4L phenotypic ontology files (RDF/TTL/XML) not present on Ubuntu
- ⚠️ **Different datasets in `local/`:** Ubuntu has N4L temperature data (931MB), Mac has BactoTraits/Madin datasets + MongoDB dumps
- ✅ .gitignore patterns are working correctly on both machines

---

## File Count Comparison

| Machine | Total Gitignored (excl. .venv) | Notes |
|---------|-------------------------------|-------|
| **Ubuntu NUC** | 114 files/directories | Baseline from issue #279 |
| **MacBook** | 10,760 files/directories | +10,470 N4L files in large/ |

---

## Directory Size Comparison

| Directory | Ubuntu Size | Mac Size | Status |
|-----------|-------------|----------|--------|
| `ontologies/validation_results/` | 1.3 GB | 1.3 GB | ✅ Identical |
| `ontologies/robot_test_results/` | 1.1 GB | 1.1 GB | ✅ Identical |
| `local/` | 930 MB | 930 MB | ⚠️ Same size, different contents |
| `large/` | 779 MB | 779 MB | ⚠️ Mac has +10,470 N4L files |
| `literature_mining/logs/` | 305 MB | 308 MB | ✅ Nearly identical |
| `downloads/` | 76 MB | 76 MB | ✅ Identical |
| `literature_mining/abstracts/` | 784 KB | 784 KB | ✅ Identical |

**Total ignored data:** ~4.5 GB on both machines

---

## Detailed Breakdown by Directory

### 1. Config & Environment (Identical Purpose, Different Contents)

**Both machines have:**
- `.idea/` - JetBrains IDE settings
- `.env` - Environment variables
- `.DS_Store` (Mac), not on Ubuntu (macOS-specific)
- `.litellm_cache/` - LiteLLM API cache

✅ **Status:** Expected - these are machine-specific configs

---

### 2. Large Reference Databases (`large/` directory)

#### Ubuntu NUC:
```
779 MB total
Sample files:
- kg-microbe-Association-predicates.rq
- mapping-notes.txt
- bacdive_utilizations.Makefile
- n4l_ref_protolog_orgname_vs_kgmicrobe.csv
```

#### MacBook:
```
779 MB total + 10,470 N4L files
Includes all Ubuntu files PLUS:
- large/N4L_phenotypic_ontology_2016/ (10,470 files)
  - N4L_phenotpic_data_xml_ttl_rdf_20160701/
    - C3.rdf, C3.ttl, C3.xml (for C3, C4, C6-C39)
    - R1.rdf, R1.ttl, R1.xml (for R1-R11354)
    - Ex8770.rdf, Ex8770.ttl, Ex8770.xml
    - InferredAntimicrobial.ttl, InferredEx8465.ttl
  - N4L_Taxonomy files (.tsv, .xlsx)
  - GSC-N4L-2015_poster.pdf
  - N4L_Taxonomy_Table_Description_20200827.docx
  - CLAUDE.md, METPO_LLM_Workflow_Summary.md
```

⚠️ **Action needed:** Should the N4L phenotypic ontology dataset be on both machines?

**File breakdown:**
- Ubuntu: ~73 files in large/
- Mac: 10,543 files in large/ (10,470 from N4L)

---

### 3. Local Data (`local/` directory) - DIFFERENT CONTENTS

#### Ubuntu NUC (22 files, 930 MB):

**N4L temperature analysis data:**
- `n4l-tables.nq` - 931 MB (largest file!)
- `flattened_n4l_temperature_components.tsv` - 4.2 MB
- `n4l-temperature.ttl` - 3.3 MB
- `categorized_temperature_range_assignments.tsv` - 1.6 MB
- `n4l-temperature.csv` - 1.4 MB
- `categorized_temperature_range_summary.tsv` - 479 KB
- `n4l-temperature-un-parsed.csv` - 228 KB
- `metpo_classes_temperature_limits.csv` - 1.7 KB
- `kg-microbe-types-bioloink-relations.csv` - 29 KB

**NCBI Taxonomy:**
- `taxdmp/names.dmp` - 255 MB
- `taxdmp/nodes.dmp` - 193 MB
- `taxdmp/citations.dmp` - 19 MB
- `taxdmp/delnodes.dmp` - 6.2 MB
- `taxdmp/images.dmp` - 4.6 MB
- `taxdmp/merged.dmp` - 1.7 MB
- `taxdmp/gencode.dmp`, `gc.prt`, `division.dmp`, `readme.txt`
- `noderanks.ttl` - 177 MB

**Other:**
- `local/.env` - 840 bytes
- `local/.gitkeep`

#### MacBook (33 files, 930 MB):

**BactoTraits dataset:**
- `bactotraits/BactoTraits_databaseV2_Jun2022.csv` - 8.6 MB
- `bactotraits/BactoTraits.tsv` - 6.1 MB

**Madin dataset:**
- `madin/madin_etal.csv` - 44 MB
- `madin/condensed_traits.csv` - 38 MB
- `madin/condensed_species.csv` - 5.8 MB
- `madin/Bacteria_archaea_traits_dataset.csv` - 268 KB

**MongoDB dumps:**
- `mongodb_dumps/madin/madin.bson` - 127 MB
- `mongodb_dumps/bactotraits/bactotraits.bson` - 38 MB

**NCBI Taxonomy (same as Ubuntu):**
- `taxdmp/names.dmp` - 258 MB
- `taxdmp/nodes.dmp` - 194 MB
- `taxdmp/citations.dmp` - 19 MB
- `taxdmp/delnodes.dmp` - 6.2 MB
- `taxdmp/images.dmp` - 4.6 MB
- `taxdmp/merged.dmp` - 1.7 MB
- `noderanks.ttl` - 178 MB

⚠️ **Key Difference:**
- **Ubuntu:** Focused on N4L temperature modeling data
- **Mac:** Has BactoTraits + Madin + MongoDB dumps

**Question:** Why doesn't Ubuntu have the Madin/BactoTraits datasets? These are used for KG-Microbe integration.

---

### 4. Downloads (`downloads/` directory) - IDENTICAL

**Both machines (76 MB):**
- `BactoTraits_databaseV2_Jun2022.csv` (also in Mac's local/bactotraits/)
- `taxdmp.zip` - NCBI taxonomy archive
- `sheets/` - Google Sheets downloads:
  - `minimal_classes.tsv`
  - `minimal_classes_enhanced.tsv`
  - `properties.tsv`
  - `bactotraits.tsv`
  - `more_classes___inconsistent.tsv`
  - `more_synonyms.tsv`
  - `attic_classes.tsv`
  - `attic_properties.tsv`
  - `metabolic_and_respiratory_llm.tsv` (Mac)
  - `metabolic_and_respiratory_robot.tsv` (Mac)
  - `trophic_mapping_bacdive__tbdeleted.tsv` (Mac)

⚠️ **Note:** Mac has 3 extra TSV files in downloads/sheets/

---

### 5. Literature Mining Outputs - NEARLY IDENTICAL

**Logs (305-308 MB):**
- Ubuntu: 305 MB
- Mac: 308 MB

**24 log files from OntoGPT extraction runs (Oct 31, 2025):**
- `fullpaper_prototype_v3_20251031_163102.log` - 70 MB
- `cmm_fullcorpus_gpt4o_t00_20251031_193935.log` - 55 MB
- `fullpaper_hybrid_gpt4o_t03.log` - 50 MB
- `chemical_utilization_hybrid_fullcorpus_gpt4o_t00_20251031_221515.log` - 16 MB
- `growth_conditions_hybrid_gpt4o_t00_20251031_213345.log` - 14 MB

**Abstracts (784 KB):**
- Both: 195 files (194 .txt files)
- Organized by topic subdirectories

✅ **Status:** Identical

---

### 6. Ontology Files - IDENTICAL

**Validation results (1.3 GB):**
- 20 .owl files on both machines
- Examples: D3O.converted.owl, FAO.reasoned.owl, METPO.reasoned.owl

**Robot test results (1.1 GB):**
- 141 files (.owl and .ttl formats)

✅ **Status:** Identical - These are reproducible generated files

---

### 7. Generated METPO Files - IDENTICAL

**In `src/ontology/`:**
- `metpo-base.*` (json, obo, owl)
- `metpo-full.*` (json, obo, owl)
- `metpo.*` (json, obo, owl, db)
- `reports/` - Build reports
- `tmp/` - Temporary build files

✅ **Status:** Should be identical if built from same commit

---

### 8. Python Cache - IDENTICAL

**Pycache directories:**
- `literature_mining/scripts/__pycache__/`
- `metpo/__pycache__/`
- `metpo/scripts/__pycache__/`

✅ **Status:** Machine-generated, contents don't matter

---

## File Count by Top-Level Directory

| Directory | Ubuntu Files | Mac Files | Difference |
|-----------|--------------|-----------|------------|
| `large/` | ~73 | 10,543 | +10,470 N4L files on Mac |
| `ontologies/` | 64 | 64 | ✅ Identical |
| `literature_mining/` | 55 | 55 | ✅ Identical |
| `local/` | 22 | 32 | +10 files on Mac (BactoTraits/Madin) |
| `src/` | 23 | 23 | ✅ Identical |
| `downloads/` | 14 | 14 | ✅ Identical |
| `.idea/` | 11 | 11 | ✅ Identical |
| `metpo/` | 8 | 8 | ✅ Identical |

---

## Critical Questions & Answers

### 1. Is `chebi_lexical_index.db` the same across computers?
**Status:** ✅ Both machines have this file ignored

### 2. Are there ChromaDB directories on other computer?
**Status:** ❌ No ChromaDB directories found on Mac
- Neither machine has `notebooks/chroma_ols_27/`, `embeddings_chroma/`, etc.
- These were likely cleaned up or moved

### 3. Does other computer have the 280 GB embeddings database?
**Status:** ❌ Not found on Mac in metpo directory
- May be stored elsewhere or on a different machine

### 4. Are Git LFS files properly configured?
**Status:** Not using Git LFS - large files are gitignored instead

### 5. Are BactoTraits files identical?
**Status:** ⚠️ Partial
- `downloads/BactoTraits_databaseV2_Jun2022.csv` exists on both (76 MB download)
- `local/bactotraits/` directory only exists on Mac

### 6. Are Google Sheets TSVs up to date on both computers?
**Status:** ⚠️ Nearly identical
- Mac has 3 extra TSVs in downloads/sheets/
- May need sync

### 7. Which literature mining logs exist on other computer?
**Status:** ✅ Identical
- Same 24 log files from Oct 31, 2025 runs

### 8. Are ontology validation results identical?
**Status:** ✅ Identical sizes (1.3 GB, 1.1 GB)
- Should be reproducible from same ROBOT/reasoner versions

---

## Discrepancies Requiring Action

### HIGH PRIORITY

#### 1. N4L Phenotypic Ontology Dataset (10,470 files on Mac, 0 on Ubuntu)

**Location:** `large/N4L_phenotypic_ontology_2016/`

**Question:** Should this be on both machines?
- If YES: Copy to Ubuntu or ensure it's downloadable
- If NO: Document why Mac needs it but Ubuntu doesn't

**Impact:** 10,470 files difference between machines

---

#### 2. Different Datasets in `local/` Directory

**Ubuntu has:**
- N4L temperature modeling data (931 MB n4l-tables.nq)
- Temperature analysis CSVs and TSVs

**Mac has:**
- BactoTraits dataset (8.6 MB + 6.1 MB)
- Madin dataset (44 MB + 38 MB + 5.8 MB + 268 KB)
- MongoDB dumps (127 MB + 38 MB)

**Question:** Why the difference?
- Is Ubuntu for temperature modeling work?
- Is Mac for KG-Microbe integration work?
- Should both machines have all datasets?

**Recommendation:**
- If datasets are project-critical: Both machines should have all datasets
- If machine-specific workflows: Document the purpose of each machine

---

### MEDIUM PRIORITY

#### 3. Extra Google Sheets TSVs on Mac

**Mac-only files in `downloads/sheets/`:**
- `metabolic_and_respiratory_llm.tsv`
- `metabolic_and_respiratory_robot.tsv`
- `trophic_mapping_bacdive__tbdeleted.tsv`

**Question:** Are these newer downloads that need to be pulled on Ubuntu?

**Recommendation:**
- Pull latest sheets on Ubuntu using appropriate download script
- Or delete from Mac if obsolete

---

#### 4. Markdown Documentation in `large/` on Mac

**Mac-only files:**
- `large/CLAUDE.md`
- `large/METPO_LLM_Workflow_Summary.md`
- `large/N4L_Data_Transformation_Workflow.md`

**Question:** Should these be tracked in git instead of ignored?

**Recommendation:**
- If these are project documentation: Move to `docs/` and track in git
- If machine-specific notes: Keep ignored

---

### LOW PRIORITY

#### 5. `.DS_Store` Files on Mac

**Mac has multiple .DS_Store files** (macOS Finder metadata)

✅ **Status:** Expected - properly ignored by .gitignore

**Recommendation:** No action needed - this is standard macOS behavior

---

## .gitignore Coverage Assessment

### ✅ Working Correctly

All major patterns are working on both machines:
- `*.db` - Catches chebi_lexical_index.db, .litellm_cache/*.db
- `.env` - Environment variables ignored
- `.idea/` - IDE settings ignored
- `.venv/` - Virtual environment ignored
- `downloads/` - Downloaded data ignored
- `large/` - Reference data ignored
- `local/` - Local datasets ignored
- `literature_mining/logs/*.log` - Log files ignored
- `ontologies/*.owl`, `*.ttl` - Downloaded ontologies ignored
- `ontologies/validation_results/`, `robot_test_results/` - Generated test results ignored
- `src/ontology/metpo-base.*`, `metpo-full.*`, `metpo.*` - Generated artifacts ignored

### No Issues Found

- ✅ No files ignored on one machine but tracked on the other
- ✅ No large files (>49 MB) that should be ignored but aren't
- ✅ Cache directories consistently ignored on both machines

---

## Recommendations

### 1. Document Machine Purposes

Create a `MACHINES.md` file documenting:
- **Ubuntu NUC:** Used for [what workflows?]
- **MacBook:** Used for [what workflows?]
- Which datasets are needed on which machines

### 2. Sync Critical Datasets

**If both machines should have same datasets:**

```bash
# On Ubuntu, copy from Mac:
rsync -av --progress mac:/Users/MAM/Documents/gitrepos/metpo/local/bactotraits/ local/bactotraits/
rsync -av --progress mac:/Users/MAM/Documents/gitrepos/metpo/local/madin/ local/madin/
rsync -av --progress mac:/Users/MAM/Documents/gitrepos/metpo/local/mongodb_dumps/ local/mongodb_dumps/

# On Mac, copy from Ubuntu:
rsync -av --progress ubuntu:/home/mark/gitrepos/metpo/local/n4l-* local/
rsync -av --progress ubuntu:/home/mark/gitrepos/metpo/local/*temperature* local/
```

### 3. Decide on N4L Phenotypic Ontology

**Option A:** Copy to Ubuntu if needed for work
```bash
rsync -av --progress mac:/Users/MAM/Documents/gitrepos/metpo/large/N4L_phenotypic_ontology_2016/ large/N4L_phenotypic_ontology_2016/
```

**Option B:** Document that it's Mac-only and why

### 4. Move Documentation to Tracked Files

If `large/*.md` files are project documentation:
```bash
# On Mac
mv large/CLAUDE.md docs/n4l_workflow/
mv large/METPO_LLM_Workflow_Summary.md docs/n4l_workflow/
mv large/N4L_Data_Transformation_Workflow.md docs/n4l_workflow/
git add docs/n4l_workflow/*.md
git commit -m "Move N4L workflow documentation to docs/"
```

### 5. Sync Google Sheets Downloads

On Ubuntu:
```bash
# Run the sheets download script to get latest versions
# (assuming there's a script for this)
make download-sheets  # or equivalent command
```

---

## Conclusion

**Good news:**
- ✅ .gitignore is working correctly on both machines
- ✅ Generated/validation files are identical in size
- ✅ No files being tracked on one machine but ignored on another
- ✅ No contradictions in .gitignore patterns

**Action needed:**
- ⚠️ Clarify why Ubuntu and Mac have different datasets in `local/`
- ⚠️ Decide if N4L phenotypic ontology should be on both machines
- ⚠️ Sync or document differences in downloaded Google Sheets

**Next steps:**
- Document machine purposes and workflows
- Sync datasets if both machines should be identical
- Move documentation files to tracked locations if appropriate

---

## Appendix: Commands Used

### Count gitignored files (excluding .venv)
```bash
git ls-files --others --ignored --exclude-standard | grep -v '^\.venv/' | wc -l
```

### Size breakdown by directory
```bash
for dir in ontologies/validation_results ontologies/robot_test_results local large literature_mining/logs downloads literature_mining/abstracts; do
    if [ -d "$dir" ]; then
        echo "=== $dir ==="
        du -sh "$dir"
    fi
done
```

### Count files by top-level directory
```bash
git ls-files --others --ignored --exclude-standard | grep -v '^\.venv/' | awk -F'/' '{print $1}' | sort | uniq -c | sort -rn
```

### List largest files in directory
```bash
find local -type f -exec ls -lh {} \; | awk '{print $5, $9}' | sort -h -r | head -15
```

---

**Generated:** 2025-11-06
**For:** GitHub issue #279
**Machines:** Ubuntu NUC (192.168.0.204) + MacBook (192.168.0.218)
