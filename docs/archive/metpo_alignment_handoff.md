# METPO Alignment / Ontology Retrieval Pipeline Handoff

*(This is a condensed handoff-ready summary of the prior session. It emphasizes completeness while removing filler and repetition.)* fileciteturn2file1

---

## 1. High-level Goal

We’re trying to align METPO (a microbial phenotype ontology) with existing public ontologies in order to:

1. Find good cross-references for METPO classes.
2. Build a high-signal lookup service for phenotype terms.
3. Refine METPO using structural agreement across ontologies (e.g. shared parent/child/sibling structure).

This is **not** naive string matching. We’re doing embedding-based nearest-neighbor search across ontology term text.


## 2. Source Data

- We have a SQLite DB (`embeddings.db`) with precomputed text embeddings for many ontologies from EBI OLS4 and BioPortal.
  - Columns include: `ontologyId`, `entityType`, `iri`, `document`, `embeddings` (JSON-serialized vector).
  - Ontology sizes range from hundreds to millions of terms.

- We also have ~250 METPO terms. Each row includes:
  - `metpo_id`
  - `metpo_label`
  - `metpo_parents`
  - definition / description text

These METPO terms are the queries we want to align to external ontologies.


## 3. Overall Retrieval Pipeline

We’re building a retrieval/assessment workflow in 3 phases:

1. **Subset migration**  
   Extract selected ontology records from SQLite and load them into a local ChromaDB vector store.

2. **Semantic querying**  
   For each METPO term, embed the term text and retrieve nearest neighbors from that ChromaDB subset.

3. **Assessment / ranking**  
   Score match quality by distance, ontology coverage, structural consistency, etc., and use that to decide which ontologies are “good alignment partners” for METPO.

We’re intentionally *not* dumping every ontology at once. We’re creating focused subsets to improve signal and interpretability.


## 4. Code / Tooling Built So Far

### 4.1 `migrate_oba_only.py`
**Purpose:** Prototype migration of a *single* ontology (“OBA” / Ontology of Biological Attributes) from SQLite into ChromaDB.

**What it does:**
- Connects to `embeddings.db`.
- Runs `SELECT ... WHERE ontologyId = 'oba'`.
- Extracts `embeddings` (tolerates different JSON formats like a raw list or `{"embedding": [...]}`).
- Creates (or opens) a persistent ChromaDB collection at a given path (e.g. `./oba_chroma`, collection name `oba_embeddings`).
- Inserts rows in batches. If batch insert fails, it retries individual rows.
- Logs failures and prints summary stats.

**Result from the actual run:**
- Migrated 73,148 OBA records.
- 0 failures.
- Stored in `./oba_chroma` under collection `oba_embeddings`.

This validated the full ETL path: SQLite → cleaned vectors → ChromaDB.


### 4.2 Generalized migrator: `migrate_filtered.py`
This is the generalized, production version of the migration step.

**Key features:**
- Uses `click` for CLI.
- Arguments:
  - `--db-path` (default like `~/embeddings.db`)
  - `--chroma-path` (output directory for a persistent ChromaDB client)
  - `--collection-name` (name of the collection to create/use)
  - `--include <ONT_ID>` (repeatable)
  - `--exclude <ONT_ID>` (repeatable)
  - `--batch-size`
- Enforces mutual exclusivity: you can **either** `--include` a whitelist of ontologyIds, **or** `--exclude` a blocklist. Not both.

**Behavior:**
- Dynamically builds the SQL `WHERE` clause:
  - With `--include a --include b`: `ontologyId IN (?, ?)`
  - With `--exclude x --exclude y`: `ontologyId NOT IN (?, ?)`
  - With neither: migrates *all* ontologies.
- Streams rows in batches from SQLite.
- Inserts to a persistent ChromaDB collection (`chromadb.PersistentClient(path=chroma_path)`).
- Writes an error log alongside the ChromaDB directory (e.g. `oba_chroma_migration_errors.log`).
- Prints record counts as it goes so you know scale before/after.

**Example commands already discussed / planned:**
```bash
# Only OBA into its own store
uv run python migrate_filtered.py   --include oba   --chroma-path ./oba_chroma   --collection-name oba_embeddings

# OBA + PATO + ENVO + etc. into one shared store
uv run python migrate_filtered.py   --include oba   --include pato   --include envo   --include mco   --include omp   --chroma-path ./metpo_relevant_chroma   --collection-name metpo_relevant_embeddings

# Everything EXCEPT huge/irrelevant ontologies
uv run python migrate_filtered.py   --exclude ncbitaxon   --exclude slm   --exclude dron   --chroma-path ./filtered_chroma   --collection-name filtered_embeddings

# ncbitaxon only (BIG ~2.65M rows, used as a control later)
uv run python migrate_filtered.py   --include ncbitaxon   --chroma-path ./ncbitaxon_chroma   --collection-name ncbitaxon_embeddings   --db-path ~/embeddings.db
```

### 4.3 Query script: `query_metpo_terms.py`
**Purpose:** Given a ChromaDB subset, retrieve nearest ontology terms for each METPO term and write a scored table.

**Behavior:**
- Loads METPO terms from `../src/templates/metpo_sheet.tsv`.
- Connects to ChromaDB persistent client at `--chroma-path`.
- Opens a specified ChromaDB collection using `--collection-name` (this flag was added so we’re not hardcoding `ols_embeddings`).
- For each METPO term:
  - Builds a query string (label, definition, maybe parents).
  - Embeds that query using OpenAI embeddings.
  - Runs a similarity search on the ChromaDB collection for top N (default 5).
  - Records:
    - METPO ID / label / parents
    - Query text used
    - Matched ontology record ID (derived from `ontologyId`, `entityType`, `iri`)
    - Matched ontology text (`document`)
    - Distance score
    - Rank
- Writes a CSV named by `--output`.

**Example (already run against OBA-only index):**
```bash
uv run python query_metpo_terms.py   --chroma-path ./oba_chroma   --collection-name oba_embeddings   --output ./oba_matches.csv
```

**Observed runtime stats from that run:**
- METPO terms processed: ~250
- Queries succeeded: 250
- Total match rows written: 1250 (= 250 * top5)
- Distance range: ~0.0 (best) up to ~1.46 (worst)
- Duration: ~1.3 minutes for 250 embedding calls
- 0 runtime errors

**Note on renaming collections:**
- ChromaDB doesn’t support “rename collection”.
- Workaround (discussed but not executed here): read from old collection, create a new one with the new desired name, reinsert docs, then delete old.
- For now we just pass `--collection-name` explicitly and keep using `oba_embeddings`, etc.


## 5. Empirical Results So Far (OBA-only test)

We migrated only the OBA ontology (≈73K concepts) and queried it with all METPO terms, producing `oba_matches.csv`. Compared to a previous “all ontologies in one giant index” approach, quality improved a lot.

### Positives:
- Matches are biologically relevant:
  - “diplococcus shaped” → returns cell-shape / morphology concepts, not random human disease terms.
  - “temperature optimum” → returns temperature/physiology traits.
  - “phenotype”, “metabolism”, “material entity” → map to plausible biological attribute classes.
- This is a big improvement over earlier attempts where noisy ontologies caused absurd matches (like “vaginal neoplasia” for a bacterial morphology class).

### Gaps / issues:
- Some METPO concepts (like “GC content”) matched unrelated biomedical ratio/quantification terms (e.g. “CHGB/SCG2 protein level ratio”), which are numerically similar but semantically off. Distances ~1.0–1.1.
- Certain METPO terms had effectively no good hits.

### Quick distance quality breakdown (rough bins):
- ~32.6% of matches are “good or excellent” (distance < 0.9).
- ~44.2% are “fair” (0.9–1.1).
- ~23.1% are “poor” (>= 1.1).

Interpretation:
- Restricting to a single, relevant ontology drastically improves precision.
- OBA alone still doesn’t cover all microbial phenotype concepts; we’ll need other ontologies.


## 6. Ontology Selection Strategy

We don’t want to index everything at once because:
- Giant ontologies add noise.
- Some ontologies are off-domain (e.g. mammal-only, clinical drug catalogs).
- Taxonomy ontologies match species names that *look* phenotype-y (“thermophilicus”) but are not actual phenotype classes.

Instead we’re ranking ontologies into 3 buckets:
1. **Very appealing**
2. **Not appealing**
3. **In between**

We use size, domain relevance (microbial phenotype, growth conditions, environment), and expert judgment (microbial focus first; clinical mammal phenotypes later).

### 6.1 `categorize_ontologies.py`
This script:
- Reads `ontology_catalog.csv`, which lists all ontologyIds, names, descriptions, and record counts.
- Heuristically scores and buckets each ontology.
- Prints a human-readable summary and also writes CSVs:
  - `ontologies_very_appealing.csv`
  - `ontologies_in_between.csv`
  - `ontologies_not_appealing.csv`

#### Initial buckets before manual refinement:

**Very Appealing (microbial/phenotype/environment-focused, moderate size):**
- `omp`  (Ontology of Microbial Phenotypes)
- `mco`  (Microbial Conditions Ontology)
- `micro` (Prokaryotic Phenotypic and Metabolic Characters)
- `pato` (Phenotype And Trait Ontology)
- `envo` (Environment Ontology)
- `fypo` (Fission Yeast Phenotype Ontology)
- `apo`  (Ascomycete Phenotype Ontology)
- `phipo` (Pathogen Host Interaction Phenotype Ontology)
- `eco`  (Evidence & Conclusion Ontology)
- `peco` (Plant Experimental Conditions Ontology)

Together these sum to ~68,936 terms.
These ontologies express microbial traits, growth conditions, environments, host-pathogen interactions, etc.

**Not Appealing (huge and/or off-target):**
- Extremely large taxonomies and clinical/chemical ontologies:
  - `ncbitaxon` (~2.65M rows; pure taxonomy, very noisy for phenotype use),
  - `slm` (~1M),
  - `dron` (~756K; drug ontology),
  - `gaz` (~678K; gazetteer of places),
  - `chebi` (~221K; chemicals).
- Also a bunch of large mammal-centric or human-clinical ontologies (e.g. HP, MP, UBERON, NCIT, SNOMED, etc.).
Total here is ~8.7M records across ~80+ ontologies. These inflate search space and tend to return irrelevant matches.

**In Between:**
- Everything else not clearly “very appealing” or “not appealing”.
- `oba` (Ontology of Biological Attributes) initially landed here because it’s broad biological attributes (~73K terms) rather than microbe-only.

BUT: empirical evidence shows OBA is *extremely* valuable for our mapping. So OBA should likely be promoted to “Very Appealing.”

#### Refinement rules after expert feedback:
We started adjusting the heuristics to account for domain nuance:

- Keep bacterial phenotype ontologies highest priority.
- Deprioritize purely fungal phenotypes unless we explicitly care about fungi.
- Keep ENVO, PECO, and other environment / growth condition ontologies, because culturing conditions and habitat descriptions are critical.
- Keep cross-species phenotype bridges like uPheno.
- Keep FLOPO (plant phenotype) because it produced surprisingly good alignments to some METPO terms.
- Keep FAO in “in-between.”
- Consider ARO (antibiotic resistance ontology), OHMI, CMPO, biolink, PCO, etc. as valuable.
- Push FYPO down slightly in priority because we’re emphasizing bacteria first (but don’t drop it entirely).
- Explicitly *add* OBA to “very appealing” because of strong retrieval quality.
- Explicitly *lower* gigantic, noisy clinical/human/fly/mouse ontologies, and most of NCBITaxon, to “not appealing.”
- Keep NCBITaxon mostly for a sanity-check experiment (see below), not as a core alignment ontology.

We are moving toward a numeric “relevance score” rather than a fixed allowlist, so we can iterate without editing code every time.


## 7. Planned Experiments / Next Steps

### 7.1 NCBITaxon-only baseline
**Why:** NCBITaxon is huge (~2.65M rows) and will probably return tons of string-similarity hits based on species/strain names that *look* phenotype-y (“thermophilus”, etc.) but are not curated phenotype classes.

**Plan:**
```bash
uv run python migrate_filtered.py   --include ncbitaxon   --chroma-path ./ncbitaxon_chroma   --collection-name ncbitaxon_embeddings   --db-path ~/embeddings.db

uv run python query_metpo_terms.py   --chroma-path ./ncbitaxon_chroma   --collection-name ncbitaxon_embeddings   --output ./ncbitaxon_matches.csv
```

**Goal:** Produce a “negative control” dataset:
- Expect extremely *high recall* (many hits for many METPO terms),
- but *low precision* (matches are usually taxa names, not phenotype classes).
- This helps quantify the noise floor.


### 7.2 Phenotype-core subset
**Why:** We want a best-effort phenotype+environment “core index” for real mapping.

**Plan:**
1. Create a ChromaDB collection from a handpicked set of relevant ontologies:
   - e.g. `oba`, `pato`, `mco`, `omp`, `envo`, maybe `micro`, `peco`, `fypo`, etc.
2. Query all METPO terms against that combined index.
3. Write results to CSV.

Commands:
```bash
uv run python migrate_filtered.py   --include oba   --include pato   --include mco   --include omp   --include envo   --chroma-path ./metpo_relevant_chroma   --collection-name metpo_relevant_embeddings

uv run python query_metpo_terms.py   --chroma-path ./metpo_relevant_chroma   --collection-name metpo_relevant_embeddings   --output ./metpo_relevant_matches.csv
```

**Goal:** Measure coverage lift vs OBA-only (Do we now cover METPO concepts that OBA alone missed? Do distances improve?)


### 7.3 Alignment quality metrics
After we generate match CSVs for:
- OBA-only
- Phenotype-core subset
- NCBITaxon-only

…we’ll compute ontology alignment metrics to rank ontology usefulness:

1. **Sibling Coherence Check**  
   For METPO class X mapping to ontology class Y:  
   - Do X’s siblings also map near Y’s siblings?  
   - Stable sibling blocks suggest meaningful structural correspondence.

2. **Parent-Child Consistency**  
   If METPO children under parent P all map into the same branch of ontology Q, Q is structurally aligned with METPO in that region.  
   That’s a strong signal that Q could be used for cross-references or even to propose restructurings.

3. **Ontology Coverage Score**  
   For each candidate ontology/set:
   - What % of METPO terms get a “good” match (distance < ~0.7–0.8)?
   - How many have *no* good matches?

4. **Match Locality / Clustering**  
   Are the matches for related METPO terms clustered into a coherent subgraph/branch of the ontology, or scattered randomly?
   (Coherent clusters = more trustworthy.)

5. **Reciprocal Best Match**  
   If METPO:X → Ontology:Y is a top hit, does Ontology:Y → METPO:X also come back as top (or near-top)?  
   Reciprocal top matches are strong candidates for asserting cross-ontology equivalence or close mapping.

6. **Distance Distribution by Ontology Type**  
   Compare median/mean distances for phenotype ontologies (OMP, MCO, PATO, etc.) vs. taxonomic, chemical, or clinical ontologies.
   - Expect phenotype ontologies to have lower (better) distances.
   - This gives an evidence-based ranking of ontology usefulness.

7. **Semantic Type Filtering via `entityType`**  
   We should down-rank matches where the external record is:
   - an individual instance,
   - a specific strain record,
   - pure evidence statement nodes,
   unless we explicitly *want* those.
   We mainly care about “class-like” terms that could map to METPO classes.

**Endgame of these metrics:**
- Produce a ranked shortlist of “best alignment ontologies” for METPO.
- Use that to:
  - propose xrefs,
  - suggest METPO refinements (merge/split/rename),
  - drive a curator-facing lookup tool (“type a trait, get candidate ontology terms + scores + structural evidence”).

---

## 8. TL;DR for the Next Agent

1. We now have working tooling to:
   - Export arbitrary ontology subsets from `embeddings.db` → persistent ChromaDB (`migrate_filtered.py`).
   - Query a chosen ChromaDB collection with all METPO terms and write a scored CSV (`query_metpo_terms.py`).
   - Bucket/scoring ontologies by domain relevance and size to decide what to include next (`categorize_ontologies.py`).

2. We validated this on OBA-only (~73K terms):
   - ~33% strong matches (<0.9 distance),
   - ~44% okay (0.9–1.1),
   - ~23% weak (>=1.1).
   - Matches are biologically sensible instead of random clinical nonsense.  
   - OBA is clearly valuable, but can’t cover everything alone.

3. Next steps already laid out:
   - Generate `ncbitaxon_only` results as a noisy baseline (high recall / low precision).
   - Build a “phenotype core” index (OBA + PATO + MCO + OMP + ENVO + etc.), re-run queries, and compare coverage.
   - Implement and compute structural/consistency metrics (sibling/parent coherence, reciprocal best match, ontology coverage %,
     distance distribution by ontology type, etc.) to rank ontology usefulness for METPO alignment.

That is the full current state.
This document is meant to be dropped into another LLM session so it can continue the work without re-reading the entire raw transcript.

---

## Related Documentation

- **[METPO Justification](../ontology/METPO_JUSTIFICATION.md)** - Why METPO was created instead of using existing ontologies
- **[Grounding Analysis](../../literature_mining/docs/ontogpt/GROUNDING_ANALYSIS.md)** - Critical discovery about URI vs CURIE format that corrected initial 0% grounding claim
- **[Extraction Results](../../literature_mining/docs/ontogpt/EXTRACTION_RESULTS.md)** - Summary of OntoGPT extraction performance with different templates

---
