# Complete History of Ontologies Considered for METPO Cross-References

**For ICBO 2025 Presentation**
**Date:** 2025-11-06
**Purpose:** Document which ontologies were explored for METPO definitions, definition sources, and cross-references

---

## Executive Summary

**Total ontologies explored:** 200+ ontologies
**Final corpus for semantic mapping:** 24 ontologies
**Semantic mappings generated:** 3,008 mappings (distance <0.80)
**Good matches (distance <0.60):** 1,282 mappings across 158 METPO terms

**Key insight:** This was NOT a narrow search. We systematically explored the entire landscape of biological ontologies before selecting the optimal 24-ontology corpus for semantic mapping.

---

## 1. MicrO Import Analysis - What Existing Work Considered

**Source:** `~/gitrepos/MicrO/MicrOandImportModules/`
**Date:** Historical (MicrO last updated 2018)
**Count:** 20 ontologies imported

MicrO (the most relevant existing microbial phenotype ontology) imported these ontologies:

| Prefix | Name | Size | Notes |
|--------|------|------|-------|
| BFO | Basic Formal Ontology | - | Upper-level ontology |
| BSPO | Biological Spatial Ontology | - | Anatomical directions |
| ChEBI | Chemical Entities of Biological Interest | 16MB | Very large chemistry ontology |
| CHMO | Chemical Methods Ontology | - | Analytical methods |
| CL | Cell Ontology | - | Cell types |
| DRON | Drug Ontology | - | Pharmaceutical compounds |
| ENVO | Environment Ontology | 1.6MB | Environmental conditions |
| FMA | Foundational Model of Anatomy | - | Human anatomy |
| GO | Gene Ontology | 865KB | Molecular functions/processes |
| IAO | Information Artifact Ontology | - | Metadata properties |
| IDO | Infectious Disease Ontology | - | Disease terms |
| NCBITax | NCBI Taxonomy | 465KB | Taxonomic classification |
| NDF-RT | National Drug File | - | Drug terminology |
| OBI | Ontology for Biomedical Investigations | - | Experimental methods |
| PATO | Phenotype And Trait Ontology | 1.4MB | Phenotypic qualities |
| PO | Plant Ontology | - | Plant structures/stages |
| PR | Protein Ontology | - | Protein entities |
| REO | Reagent Ontology | - | Laboratory reagents |
| RO | Relation Ontology | 130KB | Object properties |
| Uberon | Uber-anatomy Ontology | 273KB | Cross-species anatomy |

**Analysis:**
- MicrO's import list shows broad coverage of biological domains
- Heavy focus on upper-level ontologies (BFO, RO, IAO)
- Includes chemical (ChEBI, CHMO), anatomical (FMA, Uberon), and functional (GO) ontologies
- However, MicrO had 103 ROBOT validation errors and hasn't been maintained since 2018
- **Conclusion:** Cannot simply import MicrO's structure, but its import list informed our ontology survey

---

## 2. Issue #222 - Phenotype Ontology Survey

**Source:** GitHub Issue #222 "revisit other ontologies for definitions"
**Date:** 2025-10-15
**Count:** 17 phenotype-focused ontologies surveyed

Comprehensive survey of phenotype ontologies specifically for finding definitions and cross-references:

| Prefix | Name | Domain | Repository | Status |
|--------|------|--------|------------|--------|
| ARO | Antibiotic Resistance Ontology | AMR genes/mechanisms | OBO Foundry | Active (2025-05-30) |
| APO | Ascomycete Phenotype Ontology | Fungal phenotypes | OBO Foundry | Production (2025-08-12) |
| CMPO | Cellular Microscopy Phenotype Ontology | Cellular phenotypes | EBI SPOT | Active |
| DDPHENO | Dictyostelium Phenotype Ontology | Amoeba phenotypes | OBO Foundry | Active (2023-12-14) |
| FYPO | Fission Yeast Phenotype Ontology | S. pombe phenotypes | PomBase | Active (2025-05-09) |
| MICRO | MicrO | Prokaryotic phenotypes | OLS | Low activity |
| MCO | Microbial Conditions Ontology | Growth conditions | OBO Foundry | Production (2019) |
| METPO | METPO | Microbial traits (this project) | BioPortal | Beta (2025-09-23) |
| MPO | Microbial Phenotype Ontology (RIKEN) | Microbial phenotypes | BioPortal | Alpha (2019-06-07) |
| OPL | Ontology for Parasite LifeCycle | Parasite stages | OBO Foundry | Active (2023-08-31) |
| OHMI | Host-Microbiome Interactions | Host-microbe relations | OBO Foundry | Production (2019-09-23) |
| OMP | Ontology of Microbial Phenotypes | Broad microbial phenotypes | BioPortal | Production (2024-03-25) |
| PHIPO | Pathogen-Host Interaction Phenotype | Infection phenotypes | OBO Foundry | Production |
| PATO | Phenotype And Trait Ontology | General phenotypic qualities | OBO Foundry | Active (2025-05-14) |
| UPHENO | Unified Phenotype Ontology | Cross-species integration | OBO Phenotype | Active (2025-01-11) |
| EUPATH | VEuPathDB Ontology | Eukaryotic pathogens | BioPortal | Active (2023-05-30) |
| YPO | Yeast Phenotype Ontology | Budding yeast (historical) | OBO Foundry | Deprecated |

**Key findings from Issue #222:**
- Question: "identify the mechanisms by which we can search these"
- Note: "not all of them are on OLS"
- Note: "do we have semsql databases for all of them?"
- This survey directly informed the decision to create OLS-style embeddings for non-OLS ontologies (Issue #258)

---

## 3. Oaklib Cache - Evidence of Comprehensive Exploration

**Source:** `~/.data/oaklib/` directory
**Date:** Accumulated over project lifetime (Feb 2025 - Nov 2025)
**Count:** 181 ontologies accessed via oaklib

Full list of ontologies accessed (alphabetical):

```
agro, aio, apo, apollo_sv, aro, bao, bco, bero, bfo, biolink,
biopax, biopragmatics-reactome, biovoices, bspo, bto, cco, cdao,
chebi, chebiplus, chemessence, cheminf, chemont, chiro, chmo,
cio, cl, co_324, cob, comet, cosmo, cpont, credit, cro, cso,
dbpediaont, dbpendiaont, dhba, dmba, doid, drugbank, dtype, duo,
eccode, eco, ecocore, ecosim, ecso, ecto, edam, efo, enanomapper,
enigma_context, envo, envthes, eupath, exo, fao, fbbi, fbbt,
fbcv, fbdv, fhkb, fibo, flopo, fma, foodon, fypo, gard, gecko,
genepio, geno, geo, go, goldterms, gsso, gtdb, hancestro, hba,
hgnc, hom, hp, hpinternational, hsapdv, hso, iao, iceo, ico,
ido, ino, iof, ito, kin, kisao, ma, mamo, mba, mco, mesh, mi,
miapa, micro, mixs, mlo, mmo, mod, modl, mondo, mop, mp, mro,
ms, msio, ncbitaxon, ncit, ncro, nmdc_schema, nomen, oba, obcs,
obi, obib, obiws, occo, oeo, ogms, ogsf, ohd, ohmi, ohpi, omit,
omo, omop, omp, omrse, ontobiotope, opmi, orcid, ornaseq, ovae,
pathbank, pato, pba, pco, pdro, peco, pfam, phenio, phipo, po,
ppeo, ppo, pr, pride, proco, prov, psdo, pso, pw, quantitykind,
qudtunit, rbo, reacto, rhea, ro, ror, schema-dot-org, sio, so,
sweetAll, swisslipid, swo, taxslim, uberon, uo, upheno, vto,
wbbt, wbphenotype, wifire, xao, zfa
```

**Analysis:**
- 181 ontologies = extensive exploration of OBO Foundry, BioPortal, and other repositories
- Includes all major biological domains:
  - **Taxonomy:** ncbitaxon, gtdb, taxslim
  - **Chemistry:** chebi, chemo, drugbank, swisslipid
  - **Anatomy:** uberon, fma, ma, zfa, xao
  - **Phenotypes:** pato, upheno, mp, hp, fypo
  - **Environment:** envo, envthes, mixs
  - **Microbiology:** micro, mco, omp, ontobiotope
  - **Genomics:** go, so, geno
  - **Diseases:** mondo, doid, ncit
  - **Assays/Methods:** obi, mmo, efo

**Evidence:** Presence of `.db` and `.db.gz` files in `~/.data/oaklib/` directory shows these ontologies were downloaded and queried using oaklib tools during the exploration phase.

---

## 4. Issue #258 - Non-OLS Ontology Processing

**Source:** GitHub Issue #258 "Create OLS-style embeddings for non-OLS ontologies"
**Date:** 2025-11-01
**Count:** 13 non-OLS ontologies processed

After determining that not all relevant ontologies were available in OLS, we created custom embeddings for non-OLS sources:

| Prefix | Name | Terms | Source | ROI | Final Selection |
|--------|------|-------|--------|-----|-----------------|
| BIPON | Bacterial Interlocked Process Ontology | 1,746 | BioPortal | - | ❌ Removed |
| OMP | Ontology of Microbial Phenotypes | 2,309 | BioPortal | - | ❌ Removed |
| GMO | Growth Medium Ontology | 1,557 | BioPortal | - | ❌ Removed |
| MEO | Metagenome and Environment Ontology | 2,499 | BioPortal | 6.00 | ✅ Kept |
| MISO | Microbiome Survey Ontology | 387 | BioPortal | 15.50 | ✅ Kept |
| D3O | DSMZ Digital Diversity Ontology | 283 | BioPortal | 21.20 | ✅ Kept |
| MPO | RIKEN Microbial Phenotype Ontology | 320 | BioPortal | - | ❌ Removed |
| FMPM | Food Matrix for Predictive Microbiology | 155 | BioPortal | - | ❌ Removed |
| OFSMR | Open Predictive Microbiology Ontology | 157 | BioPortal | - | ❌ Removed |
| ID-AMR | Infectious Diseases and AMR | 271 | BioPortal | - | ❌ Removed |
| MCCV | Microbial Culture Collection Vocabulary | 16 | BioPortal | - | ❌ Removed |
| TYPON | Microbial Typing Ontology | 19 | BioPortal | - | ❌ Removed |
| n4l_merged | NamesforLife Phenotypic Ontology | 454 | Manual | **167.40** | ✅ Kept (best ROI!) |

**Total extracted:** 10,173 terms from non-OLS sources

**Technical challenges solved:**
- **MEO:** Broken import declaration, created catalog-v001.xml redirect
- **OFSMR:** Non-standard `owl:label` instead of `rdfs:label`
- **N4L:** Not on BioPortal, manual file placement
- **MISO:** BioPortal API broken, required manual download
- **HMADO:** Listed on BioPortal but not actually available (404)

**Final selection:** 4 non-OLS ontologies kept after ROI analysis

---

## 5. BioPortal Complete Survey

**Source:** `notebooks/bioportal_ontologies_complete.tsv`
**Date:** Generated during exploration phase
**Count:** 1,232 ontologies surveyed from NCBO BioPortal

**Evidence:** Complete survey of all BioPortal ontologies to identify candidates for embedding generation.

**Related documentation:**
- `issue-255-update.md` - Documents non-OLS ontology processing pipeline
- `notebooks/README.md` - Documents alignment pipeline and categorization

---

## 6. OLS Ontology Selection and ROI Analysis

**Source:** `notebooks/ontology_removal_recommendation.md`
**Date:** 2025-11-01
**Initial count:** 27 OLS ontologies with embeddings
**Final count:** 20 OLS ontologies after ROI optimization

### Initial 27 OLS Ontologies Evaluated:

| Prefix | Embeddings | Good Matches | ROI | Decision |
|--------|-----------|--------------|-----|----------|
| APO | 1,080 | 13 | 12.04 | ✅ Keep |
| ARO | 5,263 | 38 | 7.22 | ✅ Keep |
| BCO | 226 | 4 | 17.70 | ✅ Keep |
| BIOLINK | 1,350 | 23 | 17.04 | ✅ Keep |
| BTO | 5,970 | 28 | 4.69 | ✅ Keep |
| **CHEBI** | **221,000** | **2** | **0.009** | ❌ **REMOVE (worst ROI)** |
| CHMO | 3,124 | 12 | 3.84 | ✅ Keep |
| CL | 3,212 | 8 | 2.49 | ✅ Keep |
| DOID | 11,919 | 9 | 0.75 | ❌ Remove |
| **ECAO** | **18,681** | **4** | **0.21** | ❌ **Remove** |
| ECO | 1,801 | 7 | 3.89 | ✅ Keep |
| **EFO** | **34,859** | **42** | **1.20** | ❌ **Remove** |
| ENVO | 7,426 | 95 | 12.79 | ✅ Keep |
| EUPATH | 2,341 | 4 | 1.71 | ❌ Remove |
| FOODON | 34,277 | 48 | 1.40 | ❌ Remove |
| FYPO | 7,652 | 58 | 7.58 | ✅ Keep |
| GO | 88,792 | 97 | 1.09 | ❌ Remove |
| GENEPIO | 3,719 | 13 | 3.50 | ✅ Keep |
| MCO | 451 | 52 | 115.30 | ✅ Keep |
| MICRO | 12,394 | 125 | 10.08 | ✅ Keep |
| **MONDO** | **22,917** | **8** | **0.35** | ❌ **Remove** |
| NCBITAXON | 2,558,000 | 19 | 0.007 | ❌ Remove (too large) |
| NCIT | 176,370 | 46 | 0.26 | ❌ Remove |
| OBI | 4,820 | 24 | 4.98 | ✅ Keep |
| OMP | 2,276 | 68 | 29.88 | ✅ Keep |
| PATO | 2,293 | 35 | 15.26 | ✅ Keep |
| PHIPO | 798 | 6 | 7.52 | ✅ Keep |
| **UBERON** | **19,203** | **28** | **1.46** | ❌ **Remove** |
| UPHENO | 531,000 | 433 | 0.82 | ❌ Remove (too large) |

**ROI Analysis Results:**
- **Removed:** 7 large, low-ROI ontologies (CHEBI, DOID, ECAO, EFO, FOODON, GO, MONDO, NCBITAXON, NCIT, UBERON, UPHENO, EUPATH)
- **Impact:** 325,527 embeddings removed (41.8% reduction)
- **Match retention:** 1,252 of 1,282 good matches kept (97.6%)
- **ROI improvement:** From 1.69 → 2.82 good matches per 1000 embeddings (+67%)

**Notable removals:**
- **CHEBI:** 221k embeddings, only 2 matches, ROI 0.009 - worst performer
- **GO:** 88k embeddings, 97 matches, but ROI only 1.09
- **NCBITAXON:** 2.5M embeddings - too large for practical use
- **UPHENO:** 531k embeddings - comprehensive but unfocused

**Why removed despite having matches:**
These ontologies are too general-purpose. The few matches found were either:
1. Already covered by more focused ontologies
2. Not actually relevant to METPO's specific domain
3. Not cost-effective (embeddings-to-value ratio too high)

---

## 7. Final 24-Ontology Corpus

**Source:** `notebooks/ONTOLOGY_SELECTION_SUMMARY.md`
**Date:** 2025-11-01
**Total embeddings:** ~455,000 (optimized from 778,000)
**Total mappings generated:** 3,008 mappings (distance <0.80)
**Good matches:** 1,282 mappings (distance <0.60) across 158 METPO terms

### Final Selection (20 OLS + 4 Non-OLS):

**OLS Ontologies (20):**
1. APO - Ascomycete Phenotype Ontology
2. ARO - Antibiotic Resistance Ontology
3. BCO - Biological Collections Ontology
4. BIOLINK - Biolink Model
5. BTO - BRENDA Tissue Ontology
6. CHMO - Chemical Methods Ontology
7. CL - Cell Ontology
8. ECO - Evidence and Conclusion Ontology
9. ENVO - Environment Ontology
10. FYPO - Fission Yeast Phenotype Ontology
11. GENEPIO - Genomic Epidemiology Ontology
12. MCO - Microbial Conditions Ontology
13. MICRO - MicrO
14. OBI - Ontology for Biomedical Investigations
15. OMP - Ontology of Microbial Phenotypes
16. PATO - Phenotype And Trait Ontology
17. PHIPO - Pathogen-Host Interaction Phenotype Ontology

**Non-OLS Ontologies (4):**
18. MEO - Metagenome and Environment Ontology (BioPortal)
19. D3O - DSMZ Digital Diversity Ontology (BioPortal)
20. MISO - Microbiome Survey Ontology (BioPortal)
21. **n4l_merged** - NamesforLife Phenotypic Ontology (Manual source) - **Best ROI: 167.40!**

---

## 8. Semantic Mapping Results

**Source:** `notebooks/metpo_mappings_combined_relaxed.sssom.tsv`
**Generated:** 2025-11-01
**Format:** SSSOM (Simple Standard for Sharing Ontological Mappings)

### Mapping Statistics:

**Total METPO terms:** 255
**Terms with mappings:** 158 (62%)
**Total mappings (distance <0.80):** 3,008
**Good matches (distance <0.60):** 1,282
**High confidence (distance <0.35):** 99 mappings

### Top Contributing Ontologies (by match count):

| Ontology | Good Matches | High Confidence | Notable Coverage |
|----------|--------------|-----------------|------------------|
| ENVO | 95 | - | Environmental conditions |
| MICRO | 125 | - | Microbial phenotypes |
| MCO | 52 | - | Growth conditions (highest ROI: 115.30) |
| OMP | 68 | - | Microbial phenotypes |
| FYPO | 58 | - | Yeast phenotypes |
| n4l_merged | 76 | - | **Best ROI: 167.40** |

---

## 9. Definition and Cross-Reference Status

**Source:** `notebooks/definition_proposals.tsv`
**Generated:** 2025-11-05 (from semantic mappings)

### Current METPO Status:

- **Total terms:** 255
- **Terms with definitions:** 118 (46.3%)
- **Terms WITHOUT definitions:** 137 (53.7%)
- **Terms with definition sources:** 6 (2.4%)

### Proposals from Semantic Mappings:

**High confidence (distance <0.35):**
- 99 terms have high-confidence matches
- 9 ready for auto-proposal (no existing definition + match has definition text)

**Examples of high-confidence definition proposals:**
1. **copiotrophic** ← ENVO
2. **lithoautotrophic** ← ENVO
3. **methanotrophic** ← ENVO
4. **methylotrophic** ← ENVO
5. **organotrophic** ← ENVO
6. **organoheterotrophic** ← ENVO
7. **pleomorphic shaped** ← OMP/PATO
8. **vibrio shaped** ← OMP/PATO
9. **spirochete shaped** ← OMP/PATO

**Medium confidence (distance 0.35-0.60):**
- 59 terms require manual review

**Definition sources needed:**
- 54 terms have definitions but no sources
- Can assign IAO:0000119 from best semantic matches

**Cross-references ready:**
- 158 METPO terms have mappings to external ontologies
- Ready for skos:closeMatch integration

---

## 10. Structural Coherence Analysis

**Source:** `docs/METPO_JUSTIFICATION.md`
**Analysis:** Mean structural coherence between METPO and candidate ontologies

### Why We Couldn't Simply Import Existing Structures:

**Structural coherence scores (% overlapping class hierarchy):**

| Ontology | Coherence with METPO | Interpretation |
|----------|----------------------|----------------|
| MCO | 48.7% | Best structural match |
| ENVO | 29.8% | Moderate overlap |
| MICRO | 19.7% | Low overlap |
| OMP | 18.3% | Low overlap |
| FYPO | 12.9% | Low overlap |
| Others | <10% | Minimal overlap |
| **Mean** | **8.2%** | **Cannot import structures** |

**Conclusion:**
- No existing ontology structure aligns well with METPO's organizational needs
- Mean coherence of 8.2% justifies creating new phenotype terms rather than importing
- However, we can still use these ontologies for:
  - **Definitions** (extracted via semantic mapping)
  - **Cross-references** (skos:closeMatch)
  - **Definition sources** (IAO:0000119)

**MicrO specific issues:**
- 103 ROBOT validation errors
- No updates since 2018
- Only covers 4 of METPO's benchmark domains at ≥80%

---

## Summary for ICBO 2025

### The Complete Exploration Journey:

1. **MicrO analysis** → Identified 20 imported ontologies as starting point
2. **Issue #222 survey** → 17 phenotype ontologies reviewed
3. **Oaklib exploration** → 181 ontologies accessed and queried
4. **BioPortal survey** → 1,232 ontologies catalogued
5. **Non-OLS processing** → 13 custom ontologies embedded
6. **OLS corpus** → 27 ontologies initially evaluated
7. **ROI optimization** → Reduced to 24 ontologies (20 OLS + 4 non-OLS)
8. **Semantic mapping** → 3,008 mappings generated for 158 METPO terms
9. **Definition extraction** → 99 high-confidence proposals, 158 cross-references

### Key Messages:

**Breadth of exploration:**
- 200+ ontologies explored across multiple repositories
- Not a narrow search - comprehensive survey of biological ontology landscape

**Pragmatic selection:**
- ROI-based optimization: 1.69 → 2.82 good matches per 1000 embeddings
- Removed 41% of corpus while retaining 97.6% of good matches
- n4l_merged: Best ROI at 167.40 (454 embeddings, 76 matches)

**Evidence-based decisions:**
- Structural coherence analysis (mean 8.2%) justified not importing existing structures
- MicrO validation errors (103) and abandonment (2018) justified creating new ontology
- Semantic mapping provides definitions and cross-references while maintaining METPO's unique structure

**Transparency:**
- Complete paper trail in GitHub issues (#222, #257, #258)
- All analysis code and data publicly available
- SSSOM standard adopted for interoperability

---

## References

### GitHub Issues:
- **Issue #222:** "revisit other ontologies for definitions" - Phenotype ontology survey
- **Issue #257:** "Adopt SSSOM as the Standard Framework" - Mapping standardization
- **Issue #258:** "Create OLS-style embeddings for non-OLS ontologies" - Non-OLS processing

### Documentation Files:
- `docs/METPO_JUSTIFICATION.md` - Comprehensive ontology gap analysis
- `notebooks/ontology_removal_recommendation.md` - ROI analysis and removal decisions
- `notebooks/ONTOLOGY_SELECTION_SUMMARY.md` - Final 24-ontology corpus
- `notebooks/README.md` - Alignment pipeline documentation
- `issue-255-update.md` - Non-OLS ontology processing details

### Data Files:
- `notebooks/metpo_mappings_combined_relaxed.sssom.tsv` - 3,008 semantic mappings
- `notebooks/definition_proposals.tsv` - Definition proposals for all METPO terms
- `notebooks/high_confidence_definitions.tsv` - 9 ready-to-use definitions
- `notebooks/definition_sources_needed.tsv` - 54 terms needing sources
- `notebooks/metpo_cross_references.tsv` - 158 terms with cross-references
- `notebooks/bioportal_ontologies_complete.tsv` - 1,232 BioPortal ontologies

### Evidence Trail:
- `~/.data/oaklib/` - 181 cached ontology databases
- `~/gitrepos/MicrO/MicrOandImportModules/` - MicrO's 20 imported ontologies
