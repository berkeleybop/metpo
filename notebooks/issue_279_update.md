# Issue #279 Update: Cross-Computer Gitignored Files Comparison

**Date:** 2025-11-06
**Machines compared:** Ubuntu NUC (192.168.0.204) + MacBook (192.168.0.218)

---

## Executive Summary

Completed comprehensive cross-computer comparison. **The current state differs significantly from the original issue description**, but the analysis reveals important insights about machine specialization and dataset distribution.

**Key Findings:**
- ✅ .gitignore patterns working correctly on both machines
- ⚠️ **Machines appear specialized:** Ubuntu for N4L temperature research, Mac for KG-Microbe integration
- ⚠️ **N4L dataset:** Mac has 2.6x more files (10,470 vs 3,981) in different locations
- ⚠️ **Different datasets in `local/`:** Ubuntu has N4L temperature data, Mac has BactoTraits/Madin
- ⚠️ **Validation data:** Mac has 25x more ontology validation results

---

## Quick Comparison

| Metric | Ubuntu NUC | MacBook | Ratio |
|--------|-----------|---------|-------|
| **Gitignored files (excl. .venv)** | ~4,099 | 10,760 | 2.6x |
| **N4L files** | 3,981 (43MB) | 10,470 (574MB) | 2.6x |
| **N4L location** | `assets/` | `large/` | Different! |
| **Validation results** | 53M | 1.3G | 25x |
| **Robot test results** | ❌ Missing | 1.1G | N/A |
| **local/ size** | 1.6G | 930M | 0.6x |
| **Literature mining logs** | 4 logs (25M) | 47 logs (308M) | 12x |

---

## Major Discrepancies

### 1. N4L Phenotypic Ontology - Different Locations & Completeness

**Ubuntu:**
- Location: `assets/N4L_phenotypic_ontology_2016/`
- Files: 3,981
- Size: 43MB

**Mac:**
- Location: `large/N4L_phenotypic_ontology_2016/`
- Files: 10,470 (RDF/TTL/XML triples)
- Size: 574MB

**Issue:** Mac has more complete N4L dataset in different directory.

---

### 2. local/ Directory - Completely Different Contents

**Ubuntu focuses on N4L temperature modeling:**
```
n4l-tables.nq                               931MB
flattened_n4l_temperature_components.tsv    4.2MB
n4l-temperature.ttl                         3.3MB
categorized_temperature_range_*.tsv         3.5MB total
NCBI taxonomy (taxdmp/)                     ~480MB
noderanks.ttl                               177MB
```

**Mac focuses on KG-Microbe datasets:**
```
BactoTraits dataset                         15MB
Madin dataset                               88MB
MongoDB dumps (madin + bactotraits)         165MB
NCBI taxonomy (taxdmp/)                     ~490MB
noderanks.ttl                               178MB
```

**No overlap** except NCBI taxonomy!

---

### 3. Ontology Validation/Testing

**Ubuntu:**
- `ontologies/validation_results/` - 53M
- `ontologies/robot_test_results/` - ❌ **Does not exist**

**Mac:**
- `ontologies/validation_results/` - 1.3G (25x more!)
- `ontologies/robot_test_results/` - 1.1G

**Question:** Did Ubuntu intentionally clean up validation results?

---

### 4. Literature Mining Activity

**Ubuntu:** 4 logs from Oct 30, 2025 (25MB)
**Mac:** 47 logs, mostly from Oct 31, 2025 (308MB)

Mac has been running significantly more OntoGPT extractions.

---

## What Actually Matches

✅ **These are consistent across machines:**
- `.idea/` - IDE configuration
- `.env` - Environment variables
- `.litellm_cache/` - LLM cache
- `literature_mining/abstracts/` - ~796-784KB
- NCBI taxonomy data in `local/taxdmp/` (identical files)

✅ **No issues found:**
- No files tracked on one machine but ignored on another
- No contradictory .gitignore patterns
- Cache directories consistently ignored

---

## Questions for Discussion

1. **Is the machine specialization intentional?**
   - Ubuntu = N4L temperature research machine?
   - Mac = KG-Microbe integration + OntoGPT machine?

2. **Should both machines have all datasets?**
   - Option A: Sync everything (better consistency, more storage)
   - Option B: Keep specialized (document purposes clearly)

3. **N4L dataset location standardization:**
   - Should it be in `assets/` or `large/`?
   - Why the difference?

4. **Missing robot_test_results on Ubuntu:**
   - Was this cleaned up intentionally?
   - Does Ubuntu not need these?

5. **Much smaller validation_results on Ubuntu:**
   - Same question - intentional cleanup?

---

## Recommendations

### 1. Document Machine Purposes

Create `docs/DEVELOPMENT_MACHINES.md`:

```markdown
# Development Machines

## Ubuntu NUC (192.168.0.204)
**Primary use:** N4L temperature modeling and analysis
**Key datasets:**
- N4L tables and temperature data (local/)
- Partial N4L phenotypic ontology (assets/)
- NCBI taxonomy

## MacBook (192.168.0.218)
**Primary use:** KG-Microbe integration and OntoGPT extraction
**Key datasets:**
- Complete N4L phenotypic ontology (large/)
- BactoTraits and Madin datasets (local/)
- MongoDB dumps (local/mongodb_dumps/)
- NCBI taxonomy
- Extensive ontology validation results
```

### 2. Sync Critical Datasets (If Choosing "All Machines Have All Data")

**Copy to Ubuntu from Mac:**
```bash
# Complete N4L dataset
rsync -av --progress mac:/Users/MAM/Documents/gitrepos/metpo/large/N4L_phenotypic_ontology_2016/ assets/N4L_phenotypic_ontology_2016/

# KG-Microbe datasets
rsync -av mac:/Users/MAM/Documents/gitrepos/metpo/local/bactotraits/ local/bactotraits/
rsync -av mac:/Users/MAM/Documents/gitrepos/metpo/local/madin/ local/madin/
rsync -av mac:/Users/MAM/Documents/gitrepos/metpo/local/mongodb_dumps/ local/mongodb_dumps/
```

**Copy to Mac from Ubuntu:**
```bash
# N4L temperature analysis data
rsync -av ubuntu:/home/mark/gitrepos/metpo/local/n4l-*.{nq,csv,ttl} local/
rsync -av ubuntu:/home/mark/gitrepos/metpo/local/*temperature* local/
```

### 3. Standardize N4L Location

Pick one:
- Move Ubuntu's `assets/N4L_*` to `large/N4L_*`
- Move Mac's `large/N4L_*` to `assets/N4L_*`
- Update .gitignore patterns accordingly

---

## Files Generated

1. **Summary:** `notebooks/gitignore_comparison_summary.md` (this analysis)
2. **Detailed comparison:** `notebooks/gitignore_comparison_ubuntu_vs_mac.md` (earlier version)
3. **Raw data:**
   - `notebooks/mac_gitignored_analysis.txt`
   - `notebooks/ubuntu_gitignored_analysis.txt`

---

## Next Steps

- [ ] Decide on machine specialization strategy (Option A or B)
- [ ] Document machine purposes if keeping specialized
- [ ] Sync datasets if going with "all machines have all data"
- [ ] Standardize N4L dataset location
- [ ] Decide what to do about validation_results / robot_test_results size difference
- [ ] Consider syncing Google Sheets downloads (Mac has 3 extra TSVs)

---

**Analysis scripts available** in `/tmp/*_analyze_gitignored.sh` on both machines if you want to re-run.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
