# Microbial Phenotype Datasets — Background & Access Guide

This brief reviews three widely used microbial trait resources, with emphasis on **what they contain**, **how to get the data** (file/API/dumps), **schemas/data dictionaries**, and **academic publications**.

---

## 1) Madin et al. — *A synthesis of bacterial and archaeal phenotypic trait data*

**What it is.** A scripted, reproducible merge of 26 sources into a unified trait dataset for bacteria and archaea (≈14 phenotypic traits, 5 quantitative genomic traits, 4 environmental characteristics; ~170k strain‑level and ~15k species‑aggregated records).  
- Paper: *Scientific Data* (Nature Research), 2020 — “A synthesis of bacterial and archaeal phenotypic trait data”.  
  - https://www.nature.com/articles/s41597-020-0497-4
- Project landing: https://jmadinlab.github.io/datasets/madin-2020

**Where to get the data/code.**
- **GitHub (primary, with full R workflow & data folder):** https://github.com/jmadin/bacteria_archaea_traits

**Formats.**
- CSV/TSV (within the repo’s `data/`); R scripts to rebuild merged tables. No REST API.

**Schema / data dictionary.**
- Conversion tables & corrections: `data/conversion_tables/`, `data_corrections/`  
- The R pipeline documents field structure and consolidation logic.

**Suggested citation.**
- Madin, J.S. *et al.* (2020) *Sci. Data* 7, 170. DOI via article page above.

**Notes for use.**
- Designed for reproducibility; straightforward to align traits to ontology-backed slots (e.g., PATO/OMP/MCO) in downstream pipelines.

---

## 2) BacDive — The Bacterial Diversity Metadatabase (DSMZ)

**What it is.** The largest curated strain‑linked knowledge base for bacteria/archaea, with taxonomy, morphology/physiology, growth conditions, isolation/environment, sequences, and more. Actively curated; multiple NAR updates.

**Where to get data.**
- **Web portal (browse & export CSV):** https://bacdive.dsmz.de/  → *Download selection* tool for ad‑hoc CSVs.
- **Official REST API (JSON; registration required):** https://api.bacdive.dsmz.de/
  - Endpoints & docs: IDs, culture collection numbers, taxonomy, 16S, genomes, etc.
  - Sections/fields overview: https://api.bacdive.dsmz.de/strain_fields_information (≈234 main fields in 10 sections).
- **Client libraries/examples:**
  - Python package: https://pypi.org/project/bacdive/
  - R client and examples: https://api.bacdive.dsmz.de/client_examples

**Formats.**
- JSON (API), CSV (portal exports), human‑readable HTML views.

**Schema / data dictionary.**
- API documentation lists endpoints and field structure; “strain fields information” enumerates sections/fields and serves as a de‑facto data dictionary.

**Key publications.**
- Reimer, L.C. *et al.* (2022) “BacDive in 2022: the knowledge base for standardized bacterial and archaeal data.” *Nucleic Acids Research* (REST service and large‑scale retrieval emphasized).  
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC8728306/
- BacDive help/overview: https://bacdive.dsmz.de/help/

**Notes for use.**
- Use the API for systematic pulls at scale; CSV export suits quick subsets. Normalize free‑text fields (e.g., media names, conditions) to ontologies where possible.

---

## 3) BactoTraits — “A functional trait database to evaluate how natural and man‑induced changes influence the assembly of bacterial communities”

**What it is.** A bacterial functional‑traits table assembled primarily from **BacDive** (~19,455 strains). Traits include oxygen preference, cell size/shape, motility, growth pH/temperature (optimum/range), GC content, trophic type, etc.

**Where to get data.**
- **Institutional repository (ORDaR, Univ. Lorraine):** DOI landing with files (e.g., `BactoTraits_databaseV2_Jun2022.csv`, `ReadMe_BactoTraits.txt`).  
  - https://ordar.otelo.univ-lorraine.fr/record?id=10.24396%2FORDAR-53

**Formats.**
- Single CSV + README (no REST API).

**Schema / data dictionary.**
- README on the ORDaR record documents column meanings; the paper’s Supplementary Info explains variable definitions/units.

**Key publication.**
- Cébron, A. *et al.* (2021) *Ecological Indicators* — BactoTraits paper (see repository landing page for DOI and citation).

**Notes for use.**
- Because BactoTraits is derived largely from BacDive, crosswalk BacDive identifiers when enriching/verifying traits; observe license (ORDaR release lists CC BY‑NC‑SA).

---

## Quick comparison

| Resource | Coverage & freshness | Access method(s) | Formats | “Schema” support |
|---|---|---|---|---|
| **Madin et al.** | Frozen, reproducible 2020 synthesis; rebuildable from scripts | GitHub repo (code + data) | CSV/TSV + R scripts | Conversion tables + pipeline define field structure |
| **BacDive** | Continuously curated; broadest strain coverage | Web portal (CSV export) + **REST API** (JSON) + client libs | JSON (API), CSV, HTML | API docs + “strain fields information” serve as a data dictionary |
| **BactoTraits** | Static CSV release (v2, 2022) | Institutional repository (DOI landing) | CSV + README | README + paper/SI describe columns/units |

---

## Practical tips

- At scale, prefer **BacDive API** for current breadth; cache JSON and normalize to your schema (e.g., LinkML with PATO/OMP/MCO terms).  
- For **reproducible baselines**, fork/replicate **Madin et al.** (pin commits/tags).  
- For **quick analyses**, start with **BactoTraits** CSV (clear field names), then map to ontology‑backed slots for integration with other sources.
