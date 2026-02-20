# Collaborator GitHub Orgs, Repos, and Usernames

**Date:** 2026-02-19
**Purpose:** Comprehensive map of GitHub orgs, repos, and people involved in the METPO/KG-Microbe/CultureBot ecosystem. Supplements `METPO_CONTRIBUTORS.md` (core team) with full landscape.

**Sources:**
- `~/gitrepos/external-metadata-awareness/repo_data/CultureBotAI/_SUMMARY.json` (scraped Sep 2025)
- `~/gitrepos/external-metadata-awareness/repo_data/contextualizer-ai/_SUMMARY.json`
- `~/Desktop/markdown/mark-marcin-repos.md` (updated 2026-02-09)
- `~/Desktop/markdown/ai-llm-landscape-deep-dive-2026-02-12.md`
- `gh search repos --owner CultureBotAI` (live query 2026-02-19)
- `gh search repos --owner realmarcin` (live query 2026-02-19)
- `gh api users/crocodile27` (live query 2026-02-19)

---

## People

### Core Team

| Name | GitHub | LBL Email | Role |
|------|--------|-----------|------|
| Mark Andrew Miller | `turbomam` | MAM@lbl.gov | METPO primary maintainer, validation, standards |
| Marcin P. Joachimiak | `realmarcin` | mjoachimiak@lbl.gov | CultureBot/KG-Microbe PI, kg-microbe-projects, MicroGrowLink |
| Chris Mungall | `cmungall` | — | BBOP PI, strategic direction |
| Sujay Patil | `sujaypatil96` | spatil@lbl.gov | BacDive/BactoTraits ingest, pipeline maintenance |

### Undergraduates

| Name | GitHub | School | METPO Curator ID | Focus |
|------|--------|--------|-----------------|-------|
| Anthea Guo | `crocodile27` (also `antheaguobi` inactive) | UC Berkeley | Curator 4 | MetaTraits/METPO mappings, KG-Microbe transforms (PRs #425, #452), KG-Microbe-search |
| Luke Wang | `lukewangCS121` | UC Berkeley | Curator 6 | AUTO term catalog, METPO literature mining |
| Jed Dongjin Kim-Ozaeta | `jedkim-ozaeta` | UC Berkeley | Curator 5 | BugSigDB analysis, metpo-kgm-studio, KG-Microbe-search |
| Ilyas Abdolcader | `Ilyas-Abdolcader` | CCSF | — | BugSigDB experiments, CultureBot tasks |
| Noel Jubil Sason | `NoelSason` | UC Berkeley | — | BugSigDB study/experiment parsing |
| Varrun Prakash | `vman-lang` | UT Knoxville | — | Just started (Jan 2026) |

### External Collaborators

| Name | Affiliation | GitHub | Role |
|------|-------------|--------|------|
| Adam Deutschbauer | LBNL (co-PI) | — | Wet lab validation |
| Tomas Kliegr | VSE Prague | — | Symbolic rule mining (Masa et al. CSBJ 2025) |
| Petr Masa | VSE Prague | — | Symbolic rule mining (first author) |
| Brook Santangelo | CU Anschutz | `bsantan` | KG mechanistic inference |

---

## GitHub Organizations

### CultureBotAI (main hub for joint work)

**Members:** cmungall, crocodile27, jedkim-ozaeta, kliegr, petrmasa, realmarcin, sujaypatil96, turbomam

| Repo | Description | Key Contributors | Last Updated |
|------|-------------|-----------------|-------------|
| **CultureMech** | Microbial culture media KG (10K+ recipes, LinkML schema) | realmarcin | 2026-02-19 |
| **CommunityMech** | Microbial community mechanisms KB (LinkML) | realmarcin | 2026-02-19 |
| **MicroGrowLink** | Microbial growth prediction | realmarcin (634 commits) | 2026-02-17 |
| **MicroGrowAgents** | Agentic AI for cultivation, concentration predictions, HT experiment design | realmarcin | 2026-02-14 |
| **CultureBotHT** | Growth curve data download/organization | realmarcin | 2026-02-14 |
| **KG-Microbe-search** | BugSigDB analysis, search functionality | realmarcin, crocodile27, jedkim-ozaeta | 2026-02-02 |
| **kg-microbe-projects** | ML projects, DeepWalk embeddings, KOGUT model, ULTRA eval | realmarcin (545 commits), bsantan | 2026-02-02 |
| **auto-term-catalog** | OntoGPT AUTO term extraction | lukewangCS121, realmarcin | 2026-01-15 |
| **CMM-AI** | Critical minerals metabolism KGX transforms | realmarcin | 2026-01-07 |
| **PFASCommunityAgents** | PFAS microbial community agents | realmarcin | 2026-01-07 |
| **MicroMediaParam** | Chemical/media parameter mappings | realmarcin | 2025-12-22 |
| **kg-ai-prep** | KG preparation for AI model training | realmarcin | 2025-12-21 |
| **PFAS-AI** | PFAS analysis | realmarcin | 2025-12-03 |
| **MicroGrowLinkService** | MicroGrowLink service layer | realmarcin | 2025-11-02 |
| **microbe-rules** | Microbial rule sets | realmarcin | 2025-11-06 |
| **MATE-LLM** | LLM work | realmarcin | 2025-09-24 |
| **eggnogtable** | eggNOG table processing | realmarcin | 2025-09-24 |
| **eggnog_runner** | eggNOG runner | realmarcin | 2025-09-24 |
| **CultureBotAI.github.io** | Project website | realmarcin | 2026-02-10 |
| **.github** | Org profile | realmarcin | 2026-02-10 |
| **assay-metadata** | Assay metadata | realmarcin | — |

#### KG-Microbe-search branches (undergraduate work)

- `main` — realmarcin
- `jed_bugsigdb` — jedkim-ozaeta
- `Ilyas_bugsigdb_exp` — Ilyas-Abdolcader
- `noel_trait_tsv` — NoelSason

### contextualizer-ai (Marcin's MCP servers)

All repos owned by `realmarcin`:

| Repo | Description |
|------|-------------|
| artl-mcp | Art-related MCP server |
| fitness-mcp | Mutant pool fitness data MCP |
| biosample-enricher | BioSample enrichment |
| crawl-first | Web crawling |
| env-embeddings | Environmental embeddings |
| gene-function-review | Gene function review |
| gold-tools | GOLD database tools |
| landuse-mcp | Land use MCP |
| mcp_literature_eval | Literature evaluation MCP |
| metabolome-mcp | Metabolome MCP |
| ncbi-tools | NCBI tools |
| ols-mcp | OLS (Ontology Lookup Service) MCP |
| to-duckdb | DuckDB conversion |
| weather-mcp | Weather MCP |

### Knowledge-Graph-Hub

| Repo | Description | Key Contributors |
|------|-------------|-----------------|
| **kg-microbe** | Core microbial KG (1.3M nodes, 4M edges). Modular construction with Biolink model. | realmarcin, crocodile27 (PRs #425, #452), sujaypatil96, turbomam |

**Note on MetaTraits in kg-microbe:** As of 2026-02-19, there is NO metatraits code in kg-microbe and no metatraits-related issues. MetaTraits integration has not landed there yet.

### berkeleybop

| Repo | Description | Key Contributors |
|------|-------------|-----------------|
| **metpo** | Microbial Traits and Phenotypes Ontology (257 classes, 109 properties) | realmarcin, turbomam, undergrads |
| **metpo-kgm-studio** | Ontology visualization, definition generation, curator assignments | crocodile27, jedkim-ozaeta, realmarcin, sujaypatil96 |
| **group-meetings** | Weekly meeting coordination (GitHub Issues) | all |

### Marcin's personal repos (realmarcin)

| Repo | Description | Updated |
|------|-------------|---------|
| **repo-research-writer** | AI manuscript generation from repos | 2026-02-11 |
| **linkml-coral** | LinkML schema for CORAL | 2026-02-11 |
| **CORAL-LinkML** | CORAL-LinkML | 2025-09-12 |
| **fitness-mcp** | Mutant pool fitness data (also in contextualizer-ai) | 2025-09-17 |
| MAK, MAK_projects | Massive Associative K-biclustering | 2022 |
| MicrobeEnvironmentGraphLearn | Microbe-environment graph learning | 2020 |

### Adjacent orgs/repos

| Org / Repo | Focus | Who |
|-----------|-------|-----|
| chemkg/chemrof | Chemical mixtures/media schema (PR #48) | Marcin |
| turbomam/cmm-ai-automation | CMM data curation, Google Sheets integration | Mark |
| turbomam/issues | Mark's personal issue tracker | Mark |
| turbomam/agscrap | Agentic scratchpad | Mark |
| lukewangCS121/auto-term-catalog | Luke's personal fork | Luke |
| bacteria-archaea-traits/bacteria-archaea-traits | BactoTraits source data | reference |
| monarch-initiative/ontogpt | Literature mining tool | reference |

---

## Anthea's Work — What We Know

Anthea (`crocodile27`) is the key undergraduate for MetaTraits/KGX work:

1. **metpo curation**: Term editor for ~20+ METPO classes (cell shapes, trophic types, pH preferences)
2. **kg-microbe transforms**: PRs #425, #452 in Knowledge-Graph-Hub/kg-microbe
3. **KG-Microbe-search**: Active contributor (BugSigDB analysis with Jed)
4. **MetaTraits mapping**: Listed as focused on "MetaTraits/metpo mappings"

**What we DON'T see:**
- No personal repo for MetaTraits API fetching or KGX transforms
- No commits to CultureBotAI repos besides KG-Microbe-search
- The MetaTraits → KGX pipeline work may be in kg-microbe branches or local/uncommitted

**GCP connection** (from Desktop notes): CultureBot uses GCP project `culturebot-476200`. Anthea may be using this for MetaTraits data storage.

---

## Slack Channels (berkeleybop workspace)

| Channel | Purpose |
|---------|---------|
| #kg-microbe-ldrd | Primary KG-Microbe LDRD coordination |
| #culturebot | METPO curation, student coordination |
| #metpo | Dedicated METPO discussions |
| #kg-microbe-ml | ML applications |
| #ber-cmm | Critical minerals project |
| #ai-tools | AI tooling |

---

## Key Google Drive Documents

- **METPO Robot Templates source**: Google Sheet `1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU`
  - gid=121955004 → metpo_sheet.tsv
  - gid=2094089867 → metpo-properties.tsv
- **METPO ancient history**: `1Oc-nfEkwkwIKdT2wMQNzK4iDiDWhC55ZIhsuJPZhves` (retired IDs with linguistic synonyms)
- **Newish METPO screenshots**: `1etnGZ8k2xvOVCw5sn03dYXR81p0YH5VnMux3C-6mYR8`
- **CultureBotAI presentation** (QMM Group Meeting 2026-02-09): 33 slides, ML models, wet lab validation

---

*Last updated: 2026-02-19. All GitHub queries and Google Drive reads performed on this date.*
