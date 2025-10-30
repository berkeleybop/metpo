# Abstract Fetching Report for CMM/PFAS Literature Mining

**Date:** 2025-10-29
**Project:** METPO Literature Mining (Critical Minerals & PFAS)
**Tool Used:** artl-mcp 0.34.0
**Method:** Europe PMC API via `get_europepmc_paper_by_id`

---

## Objective

Retrieve abstracts for 36 unique papers about critical mineral microbes (CMM) and PFAS biodegradation for OntoGPT knowledge extraction. Papers were identified from two sources:
- CMM-AI/publications (critical minerals, rare earth elements)
- PFAS-AI/publications (PFAS biodegradation)

## Initial Dataset

**Source:** `literature_mining/publication_ids.tsv`

| Category | Count |
|----------|-------|
| Papers with PMIDs | 19 unique (21 rows including duplicates) |
| Papers with DOIs only (PMID = "Not Found") | 17 |
| **Total unique papers** | **36** |

**Note:** The PMID-based abstracts were previously fetched and stored in `cmm_pfas_abstracts/`.

## Method Used

### Tool: artl-mcp's `get_europepmc_paper_by_id`

Based on recommendation from artl-mcp maintainer, we used:

```python
from artl_mcp.tools import get_europepmc_paper_by_id

# Fetch paper metadata with abstract
paper = get_europepmc_paper_by_id("10.1038/nature16174")

# Extract fields
abstract = paper["abstractText"]
title = paper["title"]
pmid = paper.get("pmid")  # May be None for some DOIs
```

**Why this method:**
- ✅ Works with DOIs directly (no PMID mapping required)
- ✅ Returns full abstract in `abstractText` field
- ✅ Returns comprehensive metadata (authors, journal, publication date)
- ✅ No email required (unlike DOIFetcher tools)
- ✅ Can discover missing PMIDs for DOI-only papers

### Implementation

Created script: `literature_mining/scripts/fetch_doi_abstracts.py`

**Key features:**
1. Reads `publication_ids.tsv` and filters for `pmid == "Not Found"`
2. Fetches abstract from Europe PMC API for each DOI
3. Saves abstracts as individual text files:
   - If PMID discovered: `{PMID}-abstract.txt`
   - If no PMID: `doi_{sanitized_doi}-abstract.txt`
4. Reports discovered PMIDs for updating the source list

---

## Results

### ✅ Successful Retrievals: 10 out of 17 (59%)

| DOI | Status | PMID | Notes |
|-----|--------|------|-------|
| `10.1038/nature16174` | ✅ Retrieved | 26738593 | PMID discovered! |
| `10.1016/j.chemosphere.2014.01.072` | ✅ Retrieved | 24556541 | PMID discovered! |
| `10.1016/j.funbio.2025.101586` | ✅ Retrieved | 40441795 | PMID discovered! |
| `10.1016/j.jhazmat.2023.133217` | ✅ Retrieved | 38101019 | PMID discovered! |
| `10.1016/j.jhazmat.2024.136426` | ✅ Retrieved | 39531816 | PMID discovered! |
| `10.1016/j.scitotenv.2024.172996` | ✅ Retrieved | 38719042 | PMID discovered! |
| `10.1016/j.scitotenv.2024.176801` | ✅ Retrieved | 39389130 | PMID discovered! |
| `10.1021/acs.est.5c06771` | ✅ Retrieved | 41090692 | PMID discovered! |
| `10.1101/2023.08.22.554321` | ✅ Retrieved | None | bioRxiv preprint |
| `10.1101/2025.09.19.677392` | ✅ Retrieved | None | bioRxiv preprint |

**Bonus Discovery:** 8 papers had PMIDs in Europe PMC that were missing from our original dataset!

### ❌ Failed Retrievals: 7 out of 17 (41%)

**Papers NOT available in Europe PMC:**

#### 1. `10.1016/j.seppur.2025.131701`
- **Journal:** Separation and Purification Technology (Elsevier)
- **Year:** 2025 (very recent)
- **Possible reasons:** Too recent, not yet indexed, or Elsevier access restrictions

#### 2. `10.1038/nchembio.1947`
- **Journal:** Nature Chemical Biology
- **Publisher:** Nature/Springer
- **Possible reasons:** Behind paywall, Nature journals sometimes have PMC delays

#### 3. `10.1101/2023.09.15.557123`
- **Source:** bioRxiv preprint
- **Possible reasons:** Not all bioRxiv papers are indexed in PMC; may never have been submitted for peer review

#### 4. `10.48550/arXiv.2309.12345`
- **Source:** arXiv preprint
- **Possible reasons:** **Europe PMC does not index arXiv papers** (arXiv is physics/CS focused, PMC is biomedical)

#### 5. `10.1007/s11756-024-01654-0`
- **Publisher:** Springer
- **Year:** 2024
- **Possible reasons:** Recent publication, Springer indexing delay, or access restrictions

#### 6. `10.1134/S0003683817050027`
- **Journal:** Applied Biochemistry and Microbiology (Russian journal)
- **Publisher:** Pleiades Publishing/Springer
- **Year:** 2017
- **Possible reasons:** Regional journal, may not be fully indexed in PMC

#### 7. `10.3390/su151814000`
- **Journal:** Sustainability (MDPI)
- **Publisher:** MDPI
- **Possible reasons:** Some MDPI journals have incomplete PMC coverage

---

## Overall Statistics

### Complete Project Status

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total unique papers** | 36 | 100% |
| **Abstracts retrieved** | 29 | 81% |
| **Abstracts missing** | 7 | 19% |

**Breakdown by method:**
- PMIDs from original dataset: 19 papers (all retrieved)
- DOIs via Europe PMC: 10 papers (59% success rate)
- Failed retrievals: 7 papers (41% of DOI-only papers)

---

## Questions for artl-mcp Maintainer

### 1. Alternative Methods for Missing Papers

For the 7 papers not available in Europe PMC, are there other artl-mcp tools we should try?

**Specifically:**

**a) arXiv paper (`10.48550/arXiv.2309.12345`):**
- Does artl-mcp have arXiv integration?
- Should we use a different approach for arXiv preprints?

**b) Nature journals (`10.1038/nchembio.1947`):**
- Any alternative APIs for Nature/Springer content?
- Would `get_doi_metadata` help, or does it also lack abstracts?

**c) Recent Elsevier papers (`10.1016/j.seppur.2025.131701`):**
- Are there Elsevier-specific tools in artl-mcp?
- Any way to handle very recent publications not yet in PMC?

**d) Regional/MDPI journals:**
- Best practices for journals with incomplete PMC indexing?
- Alternative sources like Unpaywall, Semantic Scholar, or publisher APIs?

### 2. Improving Success Rate

**Current approach:**
```python
paper = get_europepmc_paper_by_id(doi)
abstract = paper.get("abstractText")
```

**Questions:**
- Should we add retries or error handling for intermittent API issues?
- Are there rate limits we should be aware of when processing batches?
- Any recommended timeout or backoff strategies?

### 3. Abstract Quality

**Observed:** Some abstracts contain HTML tags (e.g., `<h4>Background</h4>`, `<i>Pseudomonas</i>`)

**Questions:**
- Is this expected from Europe PMC?
- Should we strip HTML tags, or do they provide useful structure?
- Best practices for cleaning abstracts for NLP processing (OntoGPT)?

### 4. PMID Discovery Feature

**Observed:** Europe PMC discovered PMIDs for 8 papers we thought were DOI-only!

**Questions:**
- Is there a way to batch-check DOIs for PMID associations before fetching?
- Could this help us update our source dataset more efficiently?
- Any tools in artl-mcp specifically for DOI→PMID mapping?

---

## Use Case Context

### Downstream Processing: OntoGPT Extraction

These abstracts will be processed with OntoGPT to extract:
- Microbial species and taxonomic information
- Chemical compounds (critical minerals, PFAS compounds)
- Metabolic capabilities and biochemical reactions
- Growth conditions and environmental parameters

**Requirements:**
- Plain text abstracts (or consistently formatted HTML)
- High coverage (ideally >90% of papers)
- Metadata for provenance (DOI, PMID, authors, journal)

### Why artl-mcp?

We chose artl-mcp because:
1. ✅ Single tool for multiple ID types (DOI, PMID, PMCID)
2. ✅ Returns full abstracts (unlike some metadata-only APIs)
3. ✅ No email/API key required (unlike some publisher APIs)
4. ✅ Integrated with our existing workflow (Python-based)
5. ✅ MCP integration for potential AI agent workflows

---

## Technical Details

### Environment
- **Python:** 3.11.12
- **artl-mcp:** 0.34.0
- **Project:** metpo (Microbial Ecophysiological Trait and Phenotype Ontology)
- **Package manager:** uv

### Files Created
- `literature_mining/scripts/fetch_doi_abstracts.py` - Main fetching script
- `literature_mining/abstracts/*.txt` - Retrieved abstracts
- `literature_mining/publication_ids.tsv` - Source dataset

### Script Usage
```bash
# Fetch all DOI-only abstracts
uv run literature_mining/scripts/fetch_doi_abstracts.py

# Dry run to preview
uv run literature_mining/scripts/fetch_doi_abstracts.py --dry-run

# Custom paths
uv run literature_mining/scripts/fetch_doi_abstracts.py \
  --input publication_ids.tsv \
  --output-dir abstracts/
```

---

## Recommendations Requested

Based on our experience, we would appreciate guidance on:

1. **Alternative data sources** for the 7 missing papers
2. **Best practices** for handling HTML in abstracts
3. **Rate limiting** and batch processing strategies
4. **Error handling** patterns for production use
5. **Future features** in artl-mcp that might help (e.g., batch DOI→PMID lookup, arXiv support)

---

## Acknowledgments

Thank you to the artl-mcp maintainer for the excellent `get_europepmc_paper_by_id` tool and clear documentation. The 59% success rate on DOI-only papers (with 8 bonus PMIDs discovered) significantly exceeded our expectations!

The integration was straightforward, and the tool worked exactly as documented. We look forward to any suggestions for improving coverage on the remaining 19% of papers.

---

**Report prepared by:** Mark A. Miller (METPO maintainer)
**Contact:** mam@lbl.gov
**Repository:** https://github.com/berkeleybop/metpo
