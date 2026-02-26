# Document and Data Inventory for ICBO 2025 METPO Talk

**Date:** 2025-11-06
**Purpose:** Comprehensive inventory of documents, databases, and resources for ICBO 2025 presentation

---

## Executive Summary

✅ **MongoDB Remote Access:** Successfully configured (2025-11-06)
✅ **Trait Databases:** All three major databases found and accessible (BacDive, BactoTraits, Madin)
✅ **EuropePMC/IJSEM:** 13,925 bacterial species descriptions + 417k text-mined annotations 🌟
✅ **All Reference Papers:** Found and organized (BactoTraits, Madin, BacDive, SEPGFW)
✅ **SSH Documentation:** Complete and tested
✅ **CMM/Lanthanide Papers:** 40+ PDFs organized by project
✅ **ChromaDB/Qdrant:** Fully documented (2025-11-06)
✅ **Storage Infrastructure:** Fully documented (2025-11-06)
✅ **LLM Provider Funding:** Fully documented (2025-11-06)

🎉 **ALL DOCUMENTATION COMPLETE!**

---

## 1. MongoDB Databases (MacBook - 192.168.0.218:27017)

### Bacterial Trait Databases

| Database | Size | Records | Collections | Status |
|----------|------|---------|-------------|--------|
| **bacdive** | 462.52 MiB | 99,392 strains | `strains`, `strains_api`, `strains_old` | ✅ Ready |
| **bactotraits** | 6.57 MiB | 19,455 strains | `bactotraits`, `field_mappings`, `files` | ✅ Ready |
| **madin** | 19.44 MiB | 172,324 records | `madin`, `files` | ✅ Ready |

**Key Finding:** BactoTraits has exactly 19,455 strains - matching the number cited in the Cébron et al. 2021 paper!

### Literature and Metadata Databases

#### EuropePMC Database - IJSEM Articles & Text Mining ⭐

**Database:** `europepmc`
**Size:** 90.49 MiB
**Total Records:** 431,789
**Status:** ✅ **HIGHLY VALUABLE FOR METPO DEFINITIONS**

**Collections:**

| Collection | Records | Purpose |
|------------|---------|---------|
| **ijsem_articles** | 13,925 | Full IJSEM bacterial species descriptions |
| **organism_annotations** | 417,862 | Text-mined organism mentions with ontology tags |
| **annotation_state** | ? | Processing metadata |
| **ijsem_state** | ? | IJSEM processing metadata |

**What is IJSEM?**
- International Journal of Systematic and Evolutionary Microbiology
- Gold standard for bacterial species descriptions
- Contains standardized phenotypic trait descriptions
- Each article describes morphology, physiology, growth conditions, etc.

**Why This is Critical for METPO:**

1. **Standardized Trait Descriptions:** IJSEM articles follow a structured format with sections for:
   - Cell morphology (shape, size, motility, Gram stain)
   - Colony characteristics
   - Growth conditions (temperature, pH, salinity ranges and optima)
   - Oxygen requirements
   - Substrate utilization
   - Biochemical characteristics

2. **Definition Sources:** Can cite IJSEM articles as authoritative sources for METPO term definitions

3. **Ontology Annotations:** 417,862 text-mined annotations with OBO ontology tags (OBI, etc.)

4. **Cross-references:** Articles have PMIDs and DOIs for citation

**Sample Article Structure:**
```javascript
{
  doi: "10.1099/ijsem.0.006848",
  pmid: "40658455",
  title: "From cantaloupe to cattle: Pseudomonas alabamensis sp. nov..."
  // Plus abstract, full text sections, organism annotations
}
```

**Sample Organism Annotation:**
```javascript
{
  exact: "assays",
  prefix: "LOPAT reactions; pathogenicity",
  postfix: "on cantaloupe, watermelon",
  section: "Abstract",
  tags: [{
    name: "assay",
    uri: "http://purl.obolibrary.org/obo/OBI_0000070"
  }],
  type: "Experimental Methods"
}
```

**Example Queries for METPO Definition Work:**

```javascript
// Connect
use europepmc

// Find articles about mesophilic bacteria
db.organism_annotations.find({
  exact: /mesophil/i
}).limit(10)

// Find articles describing temperature ranges
db.organism_annotations.find({
  $or: [
    { exact: /temperature/ },
    { prefix: /temperature/ },
    { postfix: /temperature/ }
  ]
}).limit(10)

// Find articles with specific ontology terms
db.organism_annotations.find({
  "tags.uri": { $regex: "OBI_" }
}).limit(10)

// Get all IJSEM articles
db.ijsem_articles.find().limit(5)

// Search for specific trait mentions
db.organism_annotations.find({
  $text: { $search: "halophilic alkaliphilic thermophilic" }
})
```

**Value Proposition:**
- 13,925 bacterial species descriptions = 13,925 potential sources for trait definitions
- Text mining already done (417k annotations)
- Ontology mappings already extracted
- Can search by organism name, trait keyword, or ontology term

---

#### Other Metadata Databases

| Database | Size | Purpose |
|----------|------|---------|
| **ncbi_metadata** | 11.20 GiB | NCBI bacterial metadata (older) |
| **ncbi_metadata_20250919** | 24.85 GiB | NCBI bacterial metadata (Sept 2025 update) |
| **gold_metadata_biosample_centric_20250915** | 204.18 MiB | GOLD project metadata |
| **nmdc_20250919** | 179.34 MiB | NMDC microbiome data |

### MongoDB Access

**From Ubuntu NUC:**
```bash
# Connect to Mac's MongoDB
mongosh "mongodb://192.168.0.218:27017"

# Specific database
mongosh "mongodb://192.168.0.218:27017/bacdive"
mongosh "mongodb://192.168.0.218:27017/bactotraits"
mongosh "mongodb://192.168.0.218:27017/madin"
```

**Documentation:** `/home/mark/MONGODB_REMOTE_ACCESS_SETUP.md`

---

## 2. PDF Documents Found

### ✅ BactoTraits Paper (FOUND)

**Location:** `/home/mark/gitrepos/metpo/mongodb/1-s2.0-S1470160X21007123-main.pdf`
**Size:** 3.2 MB
**Citation:** Cébron et al. (2021) Ecological Indicators 130:108047
**Content:** Complete BactoTraits paper with:
- 19 bacterial functional traits
- 19,455 bacterial strains
- Application to soil contamination
- Fuzzy correspondence analysis
- Functional groups (mesophiles, competitors, colonizers, stress-tolerants, stress-sensitives)

**Key for ICBO:** This paper provides the framework for comparing METPO's approach to BactoTraits

### ✅ CMM/Lanthanide Papers (FOUND)

**Location:** `/home/mark/gitrepos/metpo/literature_mining/CMM-AI/publications/`

Recent papers (last 3 months):
- `fmicb-13-921635.pdf` - Frontiers in Microbiology on REE
- `fmicb-14-1258452.pdf` - Frontiers in Microbiology
- `Machine_Learning_Approaches_to_Predicting_Lanthani.pdf`
- `Machine_learning-led_semi-automated_medium_optimiz.pdf`
- `doi_10_1073-pnas_1600558113.pdf` - PNAS lanthanide paper
- `doi_10_1038-nature16174.pdf` - Nature lanthanide paper
- `doi_10_1038-nchembio_1947.pdf` - Nature Chemical Biology
- Multiple PMID papers on REE biorecovery

**Total:** ~40 PDFs in CMM-AI/publications directory

### ✅ PFAS Papers (FOUND)

**Location:** `/home/mark/gitrepos/metpo/literature_mining/PFAS-AI/publications/`

Recent papers on PFAS biodegradation (last 3 months):
- 15 PDFs on PFAS-degrading microbes
- Environmental science and toxicology journals

### ✅ ICBO Preparation (FOUND)

**Location:** `../ICBO_PREP.md`
**Size:** Comprehensive guide
**Content:**
- CMM project context and budget details
- Talk narrative and slide structure
- ROBOT validation evidence showing METPO has 0 errors vs. 65-155 errors in "core" ontologies
- Definition status: 118/255 terms have definitions (46.3%)
- Mapping analysis: 3,008 semantic mappings across 24 ontologies
- Functional group analysis

### ✅ Madin et al. Paper (FOUND - Downloaded 2025-11-06)

**Location:** `/home/mark/gitrepos/metpo/docs/icbo_2025_prep/madin_et_al_2020_trait_synthesis.pdf`
**Size:** 3.0 MB
**Citation:** Madin et al. (2020) Scientific Data 7:170
**DOI:** 10.1038/s41597-020-0497-4
**Title:** "A synthesis of bacterial and archaeal phenotypic trait data"
**Content:**
- Aggregated dataset of 23 phenotypic, genomic and environmental characteristics
- 14,884 species-aggregated records
- Methods for trait aggregation and standardization
- Complements the 172,324 records in your MongoDB madin database

**Key for ICBO:** Source paper for one of your three main trait databases, provides methodological framework for trait data integration

### ✅ BacDive Database Paper (FOUND - Downloaded 2025-11-06)

**Location:** `/home/mark/gitrepos/metpo/docs/icbo_2025_prep/bacdive_reimer_et_al_2022.pdf`
**Size:** 4.2 MB
**Citation:** Reimer et al. (2022) Nucleic Acids Research 50:D741-D746
**DOI:** 10.1093/nar/gkab961
**Title:** "BacDive in 2022: the knowledge base for standardized bacterial and archaeal data"
**Content:**
- Comprehensive description of BacDive database structure and curation process
- Data standards and quality control procedures
- API documentation
- Coverage statistics (99,000+ strains as of 2022)
- Ontology mappings and semantic integration

**Key for ICBO:** Authoritative source for BacDive trait definitions, data model, and standardization approach

### ✅ SEPGFW Definition Guide (FOUND - Downloaded 2025-11-06)

**Location:** `/home/mark/gitrepos/metpo/docs/icbo_2025_prep/sepgfw_definition_guide.pdf`
**Size:** 884 KB
**Source:** https://philpapers.org/archive/SEPGFW.pdf
**Title:** "Good For What?" (philosophical framework for definitions)
**Purpose:** Guide for writing OBO-compliant, philosophically rigorous definitions
**Content:** Principles for creating good ontological definitions based on philosophical analysis

**Key for ICBO:** Framework for ensuring METPO definitions meet OBO Foundry standards and are philosophically sound

---

## 3. Documentation Created/Found

### ✅ SSH Setup Guide

**Location:** `/home/mark/SSH_SETUP_GUIDE.md`
**Created:** 2025-11-06
**Status:** Complete and tested
**Content:**
- Passwordless SSH between Ubuntu NUC (192.168.0.204) and MacBook (192.168.0.218)
- SSH config with aliases ("mac" and "ubuntu")
- Key locations and security notes
- Troubleshooting guide

### ✅ MongoDB Remote Access Guide

**Location:** `/home/mark/MONGODB_REMOTE_ACCESS_SETUP.md`
**Created:** 2025-11-06 (today)
**Status:** Complete and tested
**Content:**
- Step-by-step setup for remote MongoDB access
- Connection strings and examples
- Security considerations
- Troubleshooting guide
- Quick reference card

### ✅ API/LLM Cost Guide

**Location:** `/home/mark/gitrepos/spending-money-on-apis/README.md`
**Status:** Found but incomplete (appears to be template/example)
**Content:** Guide on using uv with paid APIs

### ⚠️ Storage/Device Documentation (MISSING)

**Expected:** Markdown file documenting storage devices discussion
**Evidence:** Bash history shows commands for:
- `lsblk`, `mount`, `findmnt`, `gio mount`
- `recoll` installation and configuration
- `/satadata` mount point usage
- Identifying local, localnet, and remote storage

**Status:** Discussion happened but not documented
**Recommendation:** Create document based on bash history

---

## 4. METPO Repository Status

**Location:** `/home/mark/gitrepos/metpo/`

### Key Files for ICBO

| File | Purpose | Status |
|------|---------|--------|
| `../ICBO_PREP.md` | Main preparation document | ✅ Complete |
| `docs/icbo_validation_evidence.md` | ROBOT validation analysis | ✅ Complete |
| `docs/icbo_cmm_details.md` | CMM project details | ✅ Complete |
| `docs/icbo_analysis_notes.md` | Technical analysis | ✅ Complete |
| `notebooks/definition_proposals.tsv` | 256 term analysis | ✅ Ready |
| `notebooks/high_confidence_definitions.tsv` | 9 ready-to-use definitions | ✅ Ready |
| `notebooks/definition_sources_needed.tsv` | 54 terms needing sources | 📝 Action needed |
| `notebooks/metpo_cross_references.tsv` | 158 terms with mappings | ✅ Ready |
| `mongodb/1-s2.0-S1470160X21007123-main.pdf` | BactoTraits paper | ✅ Found |
| `mongodb/bactotraits_migration_ready.tsv` | Migration data | ✅ Ready |

### METPO Alignment with Trait Databases

**Coverage Analysis Available:**
- `docs/bacdive_keywords_analysis.md`
- `docs/metpo_madin_pathway_coverage.md`
- `docs/kg_microbe_bacdive_implementation_analysis.md`
- `docs/bacdive_oxygen_tolerance_analysis.md`
- `docs/madin_field_analysis.md`

---

## 5. Priority Actions for ICBO Talk

### High Priority - Definition Work

1. **Mine EuropePMC/IJSEM for trait definitions** ⭐ **NEW - HIGHEST PRIORITY** (2-3 hours)
   - 13,925 IJSEM bacterial species descriptions
   - 417,862 text-mined organism annotations with ontology tags
   - Query for METPO terms: mesophilic, thermophilic, halophilic, etc.
   - Extract standardized trait descriptions from species descriptions
   - Use PMID/DOI as authoritative definition sources
   - **This is gold for OBO-compliant definitions!**

2. **Add definition sources** (1-2 hours)
   - 54 terms have definitions but no sources
   - File: `notebooks/definition_sources_needed.tsv`
   - Can now use IJSEM articles (PMID) as authoritative sources

3. **Add high-confidence definitions** (30 minutes)
   - 9 terms ready for auto-proposal
   - File: `notebooks/high_confidence_definitions.tsv`
   - Terms: copiotrophic, lithoautotrophic, methanotrophic, methylotrophic, etc.

4. **Query other MongoDB databases for examples** (1-2 hours)
   - Use BacDive, BactoTraits, Madin databases
   - Extract field descriptions that align with METPO terms
   - Cross-reference with IJSEM definitions

### Medium Priority - Missing Documents

4. **Fetch Madin et al. paper** (5 minutes)
   ```bash
   cd ~/gitrepos/metpo/literature_mining/CMM-AI/publications/
   wget "https://www.nature.com/articles/s41597-020-0497-4.pdf" -O madin_et_al_2020.pdf
   ```

5. **Fetch SEPGFW.pdf** (5 minutes)
   ```bash
   wget "https://philpapers.org/archive/SEPGFW.pdf"
   ```

6. **Fetch BacDive database paper** (10 minutes)
   - Search for primary BacDive citation
   - Download and save to metpo/literature_mining/

### Low Priority - Documentation

7. **Document storage device setup** (30 minutes)
   - Create markdown based on bash history
   - Document recoll configuration
   - List all storage locations (local, NAS, cloud)

8. **Update LLM cost comparison** (1 hour)
   - Document OpenAI, Anthropic, Gemini costs
   - Your current funding sources
   - Cost-effective strategies

---

## 6. MongoDB Query Examples for METPO Definitions

### EuropePMC - IJSEM Articles (PRIMARY SOURCE) ⭐

```javascript
use europepmc

// Get an IJSEM article with full metadata
db.ijsem_articles.findOne()

// Search for articles about specific phenotypes
db.organism_annotations.find({
  exact: /thermophilic/i
}).limit(10)

// Find temperature-related descriptions
db.organism_annotations.find({
  $or: [
    { exact: /temperature/i },
    { prefix: /growth.*temperature/i },
    { postfix: /°C/i }
  ]
}).limit(10)

// Search for pH-related descriptions
db.organism_annotations.find({
  exact: /pH/i
}).limit(10)

// Find ontology-tagged annotations
db.organism_annotations.find({
  "tags.uri": { $exists: true }
}, {
  exact: 1,
  prefix: 1,
  postfix: 1,
  "tags.name": 1,
  "tags.uri": 1
}).limit(10)

// Get all articles for a specific organism
db.organism_annotations.find({
  exact: /Pseudomonas/i
}).limit(10)

// Find morphology descriptions
db.organism_annotations.find({
  $or: [
    { exact: /rod-shaped/i },
    { exact: /spherical/i },
    { exact: /coccoid/i },
    { exact: /filament/i }
  ]
}).limit(10)
```

### BacDive Field Descriptions

```javascript
use bacdive

// Get unique field names with descriptions
db.strains.findOne()

// Example: Temperature data
db.strains.find(
  { "morphology_physiology.temperature_range": { $exists: true } }
).limit(5)

// Example: pH tolerance
db.strains.find(
  { "morphology_physiology.pH_range": { $exists: true } }
).limit(5)

// Example: Oxygen requirements
db.strains.find(
  { "morphology_physiology.oxygen_tolerance": { $exists: true } }
).limit(5)
```

### BactoTraits Field Mappings

```javascript
use bactotraits

// Get field mappings
db.field_mappings.find()

// Get example strain with multiple traits
db.bactotraits.findOne()

// Count strains by trait
db.bactotraits.aggregate([
  { $group: { _id: "$oxygen_preference", count: { $sum: 1 } } }
])
```

### Madin Trait Descriptions

```javascript
use madin

// Get example record
db.madin.findOne()

// Find specific traits
db.madin.find({ trait_name: /temperature/ }).limit(5)
db.madin.find({ trait_name: /pH/ }).limit(5)
db.madin.find({ trait_name: /salinity/ }).limit(5)
```

---

## 7. System Configuration

### Computers

| Computer | IP | MongoDB | SSH Alias | Status |
|----------|-----|---------|-----------|--------|
| Ubuntu NUC | 192.168.0.204 | Client only | `mac` (to MacBook) | ✅ Active |
| MacBook M74 | 192.168.0.218 | Server + Client | `ubuntu` (to NUC) | ✅ Active |

### SSH Keys

- **Ubuntu → Mac:** `~/.ssh/id_ed25519_to_mac`
- **Mac → Ubuntu:** `~/.ssh/id_ed25519_to_ubuntu`
- **Status:** Passwordless, tested, working

### MongoDB Access

- **Mac MongoDB:** Port 27017, listening on 127.0.0.1 + 192.168.0.218
- **Security:** No authentication (local network only)
- **Access:** From Ubuntu: `mongosh "mongodb://192.168.0.218:27017"`

---

## 8. Undergraduate Assistants' Work

**From `../ICBO_PREP.md`:**
- Marcin has 3 undergraduate assistants
- Working on LLM-assisted approaches for METPO definitions
- Trying to satisfy OBO Foundry principles
- **Status:** Not yet at actionable stage

**Implication:** You'll need to proceed with definition work independently for now

---

## 9. KG-Microbe Status

**From `../ICBO_PREP.md`:**
- Uses METPO CURIEs
- Powers CMM project (KG-CMREE extension)
- BioRxiv paper: https://www.biorxiv.org/content/10.1101/2025.02.24.639989v1
- **Action:** Review this paper to understand how Marcin uses METPO for non-CMM tasks

---

## 10. ChromaDB with Ontology Embeddings ✅ FOUND & DOCUMENTED

**Status:** FINALIZED (Oct 31, 2025) - ChromaDB is official vector database

**Location:** `/home/mark/gitrepos/metpo/notebooks/chroma_ols20_nonols4/`

**Current Configuration:**
- **24 ontologies** (20 OLS + 4 non-OLS)
- **452,942 embeddings** (reduced from 778,496 - 41.8% reduction)
- **Size:** 648 MB
- **Vector dimensions:** 1536 (OpenAI text-embedding-3-small)

**Key Achievements:**
- **97.6% match retention** despite 41.8% corpus reduction
- **ROI improved +67%** (1.69 → 2.82 good matches per 1000 embeddings)
- **3,008 semantic mappings** generated across 24 ontologies
- **328 high-confidence mappings** (distance <0.35) ready for auto-integration

**Qdrant Status:** Evaluated but abandoned due to memory issues (required 62GB+ RAM for 8% of data)

**Top Performers:**
- n4l_merged: ROI 167.40 (Names for Life microbial phenotypes) - STAR PERFORMER
- micro: ROI 34.63 (Microbial ecology ontology)
- d3o: ROI 21.20 (DSMZ 3D structures - has GC content!)

**Biggest Removal:** CHEBI (221K embeddings, 28% of original corpus) - only 2 good matches, ROI 0.009

**Full Documentation:** `docs/icbo_2025_prep/CHROMADB_QDRANT_STATUS.md`

**Related Docs:**
- `docs/chromadb_audit_report.md` - Database integrity verification
- `docs/ONTOLOGY_SELECTION_SUMMARY.md` - Ontology selection rationale
- `docs/ontology_removal_recommendation.md` - ROI analysis details
- `docs/vector_search_analysis.md` - Qdrant vs ChromaDB comparison

**Already Generated for ICBO:**
- High-confidence definitions: 9 terms ready (`notebooks/high_confidence_definitions.tsv`)
- Definition sources needed: 54 terms (`notebooks/definition_sources_needed.tsv`)
- Cross-references: 158 terms (`notebooks/metpo_cross_references.tsv`)

---

## 11. Recommended Workflow for Next 24 Hours

### Morning (2-3 hours)
1. ✅ MongoDB access (DONE!)
2. Query BacDive/BactoTraits/Madin for field descriptions
3. Cross-reference with METPO terms needing definitions
4. Draft 10-20 new definitions

### Afternoon (2-3 hours)
5. Add definition sources to 54 terms
6. Add 9 high-confidence definitions
7. Fetch missing PDFs (Madin, SEPGFW)
8. Review BioRxiv KG-Microbe paper

### Evening (1-2 hours)
9. Update `../ICBO_PREP.md` with progress
10. Prepare queries for tomorrow's definition work
11. Review slide narrative with new examples

---

## 12. Quick Commands Reference

### MongoDB from Ubuntu

```bash
# List all databases
mongosh "mongodb://192.168.0.218:27017" --eval "show dbs"

# Connect to EuropePMC (IJSEM articles)
mongosh "mongodb://192.168.0.218:27017/europepmc"

# Connect to BacDive
mongosh "mongodb://192.168.0.218:27017/bacdive"

# Quick query - count IJSEM articles
mongosh "mongodb://192.168.0.218:27017/europepmc" --eval "db.ijsem_articles.countDocuments({})"

# Quick query - count organism annotations
mongosh "mongodb://192.168.0.218:27017/europepmc" --eval "db.organism_annotations.countDocuments({})"

# Quick query - BacDive strains
mongosh "mongodb://192.168.0.218:27017/bacdive" --eval "db.strains.countDocuments({})"
```

### Copy Files from Mac

```bash
# Copy a database export
scp mac:/path/to/file.json ~/Downloads/

# Copy multiple PDFs
rsync -av mac:~/Documents/papers/ ~/Documents/papers_from_mac/
```

### METPO Repo

```bash
cd ~/gitrepos/metpo

# Check definition status
head -20 notebooks/definition_sources_needed.tsv

# View high-confidence proposals
head -20 notebooks/high_confidence_definitions.tsv
```

---

## 13. Optional Next Steps

All critical documentation is complete! Optional improvements:

1. **Recoll configuration:** Set up indexing for PDFs and ontology files
   - Index paths: `~/gitrepos/`, `/satadata/literature/`, `~/Dropbox/`
   - File types: `.pdf`, `.owl`, `.ttl`, `.md`, `.py`
   - Would enable fast searching for papers and ontologies

2. **Storage reorganization:** Move data to underutilized SATA SSD
   - ChromaDB databases → `/satadata/chromadb/`
   - PDF collections → `/satadata/literature/`
   - MongoDB exports → `/satadata/mongodb_exports/`
   - Free up home directory space (currently 74% full)

---

## Appendix A: File Locations Quick Reference

```
# Documentation (home directory)
~/SSH_SETUP_GUIDE.md
~/MONGODB_REMOTE_ACCESS_SETUP.md
~/STORAGE_INFRASTRUCTURE.md
~/LLM_PROVIDER_FUNDING_GUIDE.md  # ⭐ NEW

# METPO repo - ICBO 2025 prep
~/gitrepos/metpo/docs/ICBO_PREP.md
~/gitrepos/metpo/docs/icbo_2025_prep/DOCUMENT_INVENTORY_ICBO_2025.md (this file)
~/gitrepos/metpo/docs/icbo_2025_prep/CHROMADB_QDRANT_STATUS.md
~/gitrepos/metpo/docs/icbo_2025_prep/madin_et_al_2020_trait_synthesis.pdf
~/gitrepos/metpo/docs/icbo_2025_prep/bacdive_reimer_et_al_2022.pdf
~/gitrepos/metpo/docs/icbo_2025_prep/sepgfw_definition_guide.pdf

# METPO repo - Papers and data
~/gitrepos/metpo/mongodb/1-s2.0-S1470160X21007123-main.pdf (BactoTraits)
~/gitrepos/metpo/notebooks/*.tsv (definition proposals, cross-refs)
~/gitrepos/metpo/literature_mining/CMM-AI/publications/*.pdf

# ChromaDB (production)
~/gitrepos/metpo/notebooks/chroma_ols20_nonols4/  # 24 ontologies, 453K embeddings

# MongoDB (MacBook)
mongodb://192.168.0.218:27017/europepmc  # ⭐ IJSEM articles - PRIMARY SOURCE
mongodb://192.168.0.218:27017/bacdive
mongodb://192.168.0.218:27017/bactotraits
mongodb://192.168.0.218:27017/madin
```

---

**Last Updated:** 2025-11-06
**Status:** READY FOR ICBO PREPARATION WORK
**Next Action:** Query MongoDB trait databases for METPO definition material

