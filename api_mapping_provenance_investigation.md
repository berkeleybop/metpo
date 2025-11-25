# API Mapping Provenance Investigation

**Date**: 2025-11-20
**Investigation**: Where did Harshad Hegde's API mapping CSV files come from?

---

## Key Findings

### 1. CSV Files Found in Git History ✅

**Created by**: Harshad Hegde (hegdehb@gmail.com)
**Date**: March 4, 2024 at 22:08:45 (commit d64cf09)
**Removed**: March 5, 2024 at 10:56:11 (commit 5882144) - "remove source files from version control"
**Reason for removal**: Likely too large for git or licensing concerns

**15 CSV files total**:
1. kit_api_20A_meta.csv (24 tests)
2. kit_api_20E_meta.csv (27 tests)
3. kit_api_20NE_meta.csv
4. kit_api_20STR_meta.csv
5. kit_api_50CHas_meta.csv
6. kit_api_CAM_meta.csv
7. kit_api_ID32E_meta.csv
8. kit_api_ID32STA_meta.csv
9. kit_api_LIST_meta.csv
10. kit_api_NH_meta.csv
11. kit_api_STA_meta.csv
12. kit_api_coryne_meta.csv
13. kit_api_rID32A_meta.csv
14. kit_api_rID32STR_meta.csv
15. kit_api_zym_ec.csv (20 tests)

**Total unique analytes**: ~370 (combined in bacdive_mappings.tsv)

---

## CSV File Structure Analysis

### Columns (24 total):

1. **ID_kit_api_XXX_meta** - Row ID
2. **cupule** - Test well number
3. **cupule_Name_Kit** - Test abbreviation (as labeled on kit)
4. **name_bacdive** - BacDive internal name
5. **reaction_name** - Human-readable description
6. **external_Link** - URL to BRENDA or KEGG
7. **ID_microbiol** - Microbiological test ID
8. **substrate** - Chemical substrate name
9. **ID_CHEBI** - **CHEBI ID (just the number)**
10. **CAS** - CAS Registry Number
11. **kegg_comp** - KEGG Compound ID (just the ID part)
12. **brenda_ligand** - BRENDA ligand ID
13. **enzyme** - Enzyme name
14. **EC_number** - EC number
15-23. **tf_api_*** - Boolean flags linking to BacDive data types
24. **last_change** - **All dated 2016-03-22 14:45:XX**

### Key Observations:

1. **Last updated**: **2016-03-22** - This is 8 years old!
2. **External links present**: Direct URLs to BRENDA and KEGG
3. **Multiple ID systems**: CHEBI, CAS, KEGG, BRENDA, EC
4. **Well-structured**: Systematic mapping work, not ad-hoc

---

## Example Entry (API 20E - ONPG test):

```csv
ID,cupule,cupule_Name_Kit,name_bacdive,reaction_name,external_Link,ID_microbiol,substrate,ID_CHEBI,CAS,kegg_comp,brenda_ligand,enzyme,EC_number,...
1,1,ONPG,ONPG,beta-Galactosidase,http://www.brenda-enzymes.org/enzyme.php?ecno=3.2.1.23,ONPG_20E,o-nitrophenyl-beta-D-galactopyranosid,90144,0369-07-03,NULL,3699,beta-galactosidase,3.2.1.23,...
```

**Breakdown**:
- Test: ONPG (o-Nitrophenyl-β-D-galactopyranoside)
- Enzyme: β-galactosidase
- EC: 3.2.1.23
- CHEBI: 90144 (CHEBI:90144)
- Links to BRENDA for EC number details
- BRENDA ligand ID: 3699

---

## Where Did These Come From?

### Theory 1: BacDive Internal Database ⭐ **MOST LIKELY**

**Evidence**:
1. **BacDive API Test Finder exists**: https://bacdive.dsmz.de/api-test-finder
   - Shows 253 strain entries with API test results
   - Has columns for test analytes
   - Links to BRENDA and KEGG

2. **Column names suggest BacDive origin**:
   - `name_bacdive` - BacDive internal naming
   - `ID_microbiol` - Microbiological ID system
   - `tf_api_*` flags - Links to BacDive data structure

3. **Date (2016-03-22)** matches BacDive publication timeline:
   - "BacDive in 2019" paper mentions mobilizing 8,977 API test results
   - 2016 would be data preparation phase

4. **Harshad's affiliation**:
   - Works at Berkeley BBOP (Berkeley Bioinformatics Open-source Projects)
   - BBOP collaborates with database projects
   - Likely had access to BacDive backend data

**Hypothesis**: Harshad obtained these mappings **directly from BacDive/DSMZ**, possibly:
- Through collaboration/data sharing agreement
- Downloaded from BacDive API or internal database
- Received from BacDive team for kg-microbe project

---

### Theory 2: Manual Curation from Literature ❌ **UNLIKELY**

**Against this**:
- Too systematic (all entries dated same day in 2016)
- Consistent structure across 370 tests
- Would take months to curate manually
- Harshad added them in 2024, but "last_change" is 2016

---

### Theory 3: Scraped from BRENDA/KEGG ❌ **UNLIKELY**

**Against this**:
- BRENDA doesn't organize by API kits
- Would need to know API test → EC mappings already
- BacDive-specific fields (`name_bacdive`, `ID_microbiol`)

---

## Why Are API Mappings Not Public?

### bioMérieux's Position

**What IS public**:
- ✅ Test chemistry is published (ONPG is ONPG, ADH is arginine dihydrolase)
- ✅ Product catalogs show test names
- ✅ Package inserts explain reactions
- ✅ Academic papers discuss test interpretations

**What is NOT public**:
- ❌ Comprehensive database mapping all tests to ontology IDs
- ❌ APIWEB interpretation algorithms (proprietary)
- ❌ Full strain database with profiles (paid subscription)

**Why the secrecy?**
1. **Commercial product** - API strips are sold for profit
2. **APIWEB software is licensed** - requires credentials
3. **Intellectual property** - identification algorithms
4. **Quality control** - don't want incorrect DIY interpretations

**BUT**: The underlying chemistry is NOT secret:
- β-galactosidase test uses ONPG substrate (publicly known)
- EC numbers are public (Enzyme Commission)
- CHEBI IDs are public (EBI database)
- What's proprietary is the **integrated interpretation system**

---

## BacDive's Role

**BacDive mobilized API test data**:
- 8,977 API test results for 5,237 strains
- Made publicly searchable via API Test Finder
- Linked to BRENDA and KEGG

**This suggests**:
- BacDive negotiated with bioMérieux for data sharing
- Or: BacDive curated from published literature
- The mappings (substrate → CHEBI/EC) were created by **DSMZ team**, not bioMérieux

**Evidence**: The CSV files have BacDive-specific structure, not bioMérieux format

---

## How Harshad Got Them

### Most Probable Scenario:

1. **BacDive/DSMZ created the mappings** (dated 2016-03-22)
2. **Harshad accessed BacDive data** for kg-microbe project (March 2024)
3. **Either**:
   - Downloaded via BacDive API
   - Received directly from DSMZ team
   - Extracted from BacDive database dump

4. **Committed to kg-microbe** (March 4, 2024)
5. **Removed from git next day** (March 5, 2024) - likely because:
   - Files too large for git
   - Licensing concerns (should data be in public repo?)
   - Decided to keep as external dependency

6. **Generated `bacdive_mappings.tsv`** from CSV files (370 rows)
7. **CSV files remain referenced** by notebook but not in repo

---

## Questions to Ask Harshad

1. **Where did you get the kit_api_*_meta.csv files?**
   - From BacDive API?
   - From DSMZ directly?
   - From another source?

2. **Why were they removed from version control?**
   - Size concerns?
   - Licensing restrictions?
   - Data update strategy?

3. **Are these mappings considered public data?**
   - Can we use them freely?
   - Should they be cited?
   - Are they maintained/updated?

4. **Who created the mappings originally?**
   - DSMZ team?
   - Someone else?
   - What was the methodology?

5. **Where should the CSV files be stored now?**
   - External data repository?
   - Zenodo?
   - Keep in git with LFS?

6. **Are the 2016 mappings up-to-date?**
   - Have CHEBI IDs been deprecated?
   - Should we validate against current ontologies?

---

## Comparison: BacDive API Test Finder vs. Harshad's CSVs

### BacDive API Test Finder:
- **Purpose**: Search strain *results* (which strains are positive for which tests)
- **Entries**: 253 strains
- **Data**: +/- results for ~20 common tests per strain
- **Mappings**: Links to BRENDA/KEGG but not comprehensive

### Harshad's CSV Files:
- **Purpose**: Map test *analytes* to ontology IDs
- **Entries**: 370 unique tests across 15 kits
- **Data**: Substrate, enzyme, CHEBI, EC, KEGG, CAS, BRENDA IDs
- **Mappings**: Comprehensive for all API test chemistry

**Key difference**: BacDive Test Finder shows strain data, Harshad's CSVs map test metadata

---

## Why This Matters

### Data Quality Concerns:

1. **8 years old** (2016 mappings):
   - CHEBI IDs may be deprecated
   - EC numbers may be reclassified
   - New tests not included

2. **Unknown validation**:
   - Who checked these mappings?
   - What was the QC process?
   - Any errors corrected since 2016?

3. **Single source**:
   - If BacDive mappings have errors, we propagate them
   - No independent validation

### Opportunity:

If these are BacDive's official mappings:
- ✅ **Reliable** - created by database curators
- ✅ **Comprehensive** - covers all major API kits
- ✅ **Citable** - can attribute to DSMZ/BacDive
- ⚠️ **Need to validate** - check for deprecated IDs

---

## Recommendations

### Immediate Actions:

1. **Email Harshad** to ask about provenance
2. **Check BacDive documentation** for data sharing policy
3. **Contact DSMZ** to ask about API mapping availability
4. **Validate sample** of mappings against BRENDA/ChEBI

### If from BacDive:

1. **Cite properly**: "API test mappings obtained from BacDive (DSMZ)"
2. **Check for updates**: Are newer versions available?
3. **Validate IDs**: Run script to check for deprecated terms
4. **Consider publishing**: If we improve mappings, contribute back

### If NOT from BacDive:

1. **Document methodology**: How were mappings created?
2. **Validate thoroughly**: Can't trust unknown curation
3. **Consider recreating**: Manual curation from literature

---

## Total API System Coverage

### From bioMérieux Brochure:
- **16 different API kits listed**
- Each kit has 10-50 tests
- Estimated total: 300-500 unique analytes

### From Harshad's CSV Files:
- **15 CSV files** (covers most major kits)
- **~370 unique tests** after combining
- **Missing from brochure**: API 50CHac (not in CSV files)

### Coverage Assessment:
**~75-90% of API system covered** by Harshad's mappings

**Missing**:
- Rapid 20E (mentioned in brochure, no CSV)
- Some newer kits (if added after 2016)
- API 50CHac (brochure mentions, no CSV)

---

## Conclusion

**Most Likely Source**: BacDive/DSMZ internal database, created in 2016, accessed by Harshad in 2024

**Why mappings aren't publicly available elsewhere**:
- This IS the public source (via BacDive)
- bioMérieux doesn't provide it (commercial reasons)
- No one else has created comprehensive mappings
- **This is original database curation work by DSMZ**

**Next steps**:
1. Confirm with Harshad
2. Validate against current ontologies
3. Properly cite BacDive/DSMZ
4. Check for licensing restrictions
5. Update Issue #26 with findings

---

**Don't forget about helping Luke report the auto-prefix grounding failures!** 😊
