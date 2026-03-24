# MetaTraits Mapping Branch Status

**Date:** 2026-02-23
**Branch:** `metatraits-entity-additions`
**Base:** `main`
**Release status:** Not yet merged, not yet uploaded to Google Sheets, not yet included in a METPO release.

---

## Summary

The `metatraits-entity-additions` branch adds 24 new METPO classes, 26 new data properties, 2 new template columns, and MetaTraits synonym annotations to existing terms. Combined with the resolver script, this brings MetaTraits-to-METPO coverage to **97%** (2801 of 2860 trait cards resolve to a METPO entity or external CURIE).

A working demo script emits KGX nodes and edges from local MongoDB MetaTraits records using the official `kgx` Python library. This is the code that someone like Anthea (or anyone implementing MetaTraits ingestion in kg-microbe) would build on.

---

## What changed in the templates

### New columns in metpo_sheet.tsv (classes)

| Column | ROBOT header | Purpose |
|--------|-------------|---------|
| `metatraits synonym` | `A oboInOwl:hasRelatedSynonym SPLIT=\|` | MetaTraits-specific synonym strings (e.g., "salinity preference", "cell color") |
| `MetaTraits synonym source` | `>AI IAO:0000119` | Source annotation (`https://metatraits.embl.de/`) |

### New class rows (24 entities, METPO:1005001-1005040)

| ID range | Count | Category | Labels |
|----------|-------|----------|--------|
| 1005001 | 1 | process | nitrification |
| 1005010-1005018 | 9 | biochemical tests | indole test, methyl red test, Voges-Proskauer test (each with parent, positive, negative) |
| 1005021 | 1 | oxygen preference | capnophilic |
| 1005025-1005027 | 3 | phenotype | hemolysis (parent), hemolytic, non-hemolytic |
| 1005031-1005037 | 7 | flagellum arrangement | peritrichous, polar, amphitrichous, lophotrichous, monotrichous, lateral, subpolar |
| 1005038 | 1 | process | denitrification |
| 1005039 | 1 | process | nitrogen fixation |
| 1005040 | 1 | ecology | generalist |

### New data property rows (26 entities, METPO:2000701-2000734)

| ID range | Count | Category |
|----------|-------|----------|
| 2000701-2000703 | 3 | Temperature (growth/min/max) |
| 2000704-2000706 | 3 | pH (growth/min/max) |
| 2000707-2000709 | 3 | Salinity (growth/min/max) |
| 2000711-2000712 | 2 | Genome size (actual/estimated) |
| 2000713-2000714 | 2 | Gene count (actual/estimated) |
| 2000715-2000716 | 2 | GC percentage, coding density |
| 2000721-2000726 | 6 | Cell length/width (value/min/max) |
| 2000730 | 1 | Ecology metric parent (`has ecology metric value`) |
| 2000731-2000734 | 4 | Ecology metrics (generalism score, habitat count, pangenome openness, nucleotide diversity) |

### Modified existing rows

- **METPO:2000015** (`uses in other way`) and **METPO:2000041** (`does not use in other way`): added `oboInOwl:hasRelatedSynonym 'utilizes'` with source `https://metatraits.embl.de/`
- Many existing classes gained values in the new `metatraits synonym` column

### Row/column counts

| File | main | Branch | Delta |
|------|------|--------|-------|
| metpo_sheet.tsv | 258 lines | 283 lines | +25 (24 new entities + header change) |
| metpo-properties.tsv | 113 lines | 139 lines | +26 new data properties |

---

## Where the updated files live

The template files exist in multiple locations. Understanding which copy is authoritative matters because the ontology build downloads from Google Sheets and can overwrite local edits.

### 1. Git working copy (authoritative for this branch)

These are the files that contain all new rows and columns:

- `src/templates/metpo_sheet.tsv` (283 lines)
- `src/templates/metpo-properties.tsv` (139 lines)

GitHub URLs on the branch:
- https://github.com/microbiomedata/metpo/blob/metatraits-entity-additions/src/templates/metpo_sheet.tsv
- https://github.com/microbiomedata/metpo/blob/metatraits-entity-additions/src/templates/metpo-properties.tsv

### 2. Drafts directory (stash copies, protection against Google Sheets overwrite)

Saved copies that survive `squeaky-clean` + re-download from Google Sheets:

- `src/templates/drafts/metpo_sheet.tsv`
- `src/templates/drafts/metpo-properties.tsv`

These are created and restored via Makefile targets in `src/ontology/metpo.Makefile`:

```bash
# Save before squeaky-clean
cd src/ontology
sh run.sh make save-drafts

# After squeaky-clean re-downloads from Google Sheets, restore local edits
sh run.sh make install-drafts

# Diff Google Sheets version vs saved drafts
sh run.sh make diff-drafts
```

GitHub URL for the Makefile with these targets:
- https://github.com/microbiomedata/metpo/blob/metatraits-entity-additions/src/ontology/metpo.Makefile

### 3. Google Sheets (NOT YET UPDATED)

The Google Sheets source is the upstream that the ODK build downloads from during `squeaky-clean`:

- **Sheet ID:** `1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU`
- **Classes tab (gid=121955004):** does NOT yet have the new `metatraits synonym` / `MetaTraits synonym source` columns or the 24 new class rows
- **Properties tab (gid=2094089867):** does NOT yet have the 26 new data property rows

Download URLs (these currently return the OLD versions without our changes):
- Classes: `https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv&gid=121955004`
- Properties: `https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv&gid=2094089867`

### 4. METPO release artifacts (NOT YET UPDATED)

The release files (`metpo.owl`, `metpo.obo`, `metpo.json`) on `main` do not include any of the new entities. A release requires:

1. Merge `metatraits-entity-additions` to `main`
2. Upload updated TSVs to Google Sheets (or bypass Sheets and build from git)
3. Run `cd src/ontology && sh run.sh make prepare_release`
4. Tag and publish

---

## What still needs to happen before release

- [ ] Upload new columns and rows to Google Sheets (or decide to build from git-committed TSVs only)
- [ ] Merge branch to `main`
- [ ] Run ontology build and tests
- [ ] Tag a release

---

## Generated mapping artifacts

The branch also includes scripts and generated files that resolve MetaTraits trait names to METPO entities:

| File | Purpose |
|------|---------|
| `data/mappings/metatraits_cards.tsv` | All 2860 MetaTraits trait card definitions (scraped from metatraits.embl.de/traits) |
| `data/mappings/metatraits_in_sheet_resolution.tsv` | Deterministic lookup table: trait name -> METPO predicate, object, mapping kind |
| `data/mappings/metatraits_in_sheet_resolution_report.md` | Coverage report (97% resolved) |

Regenerate with:

```bash
make metatraits-helper-files
```

---

## Code examples for KGX emission

Three resources exist for someone implementing MetaTraits-to-KGX ingestion (e.g., in kg-microbe or KG-Microbe-search):

### 1. Working demo script

**File:** `metpo/scripts/demo_metatraits_mongo_to_kgx.py`
**CLI alias:** `demo-metatraits-mongo-to-kgx`
**Makefile target:** `make demo-metatraits-mongo`

Reads from local MongoDB `metatraits.genome_traits`, resolves traits through the resolution table, and emits KGX nodes/edges using `kgx.sink.TsvSink` and `kgx.sink.JsonlSink`.

```bash
# Run the demo (requires local MongoDB with metatraits database)
make demo-metatraits-mongo
# Writes:
#   data/mappings/demo_metatraits_mongo_kgx_nodes.tsv
#   data/mappings/demo_metatraits_mongo_kgx_edges.tsv
```

Key functions to study:

- `load_resolution_table()` — reads the TSV lookup table
- `map_record_to_edge()` — applies predicate selection rules (composed vs uncomposed, positive vs negative)
- `choose_object_curie()` — picks CHEBI for composed traits, METPO for base traits
- `write_kgx()` — emits via official KGX sink classes (not ad hoc TSV writers)

GitHub URL:
- https://github.com/microbiomedata/metpo/blob/metatraits-entity-additions/metpo/scripts/demo_metatraits_mongo_to_kgx.py

### 2. Operational runbook with worked examples

**File:** `docs/metatraits_kgx_encoding_examples.md`

Six worked KGX edge examples covering every trait category:

| Example | Trait | Predicate | Object |
|---------|-------|-----------|--------|
| A. Composed positive | `fermentation: D-glucose` (true) | `METPO:2000011` (ferments) | `CHEBI:4167` |
| B. Composed negative | `fermentation: D-glucose` (false) | `METPO:2000037` (does not ferment) | `CHEBI:4167` |
| C. Nitrogen-cycle | `denitrification: nitrate` (true) | `METPO:2000601` (denitrifies) | `CHEBI:<nitrate>` |
| D. Uncomposed boolean | `gram positive` (true) | `biolink:has_phenotype` | `METPO:1000698` |
| E. Standalone process | `nitrogen fixation` (true) | `METPO:2000103` (capable of) | `GO:0009399` |
| F. Enzyme activity | `enzyme activity: catalase` (true) | `METPO:2000302` (shows activity of) | `EC:1.11.1.6` |

Also includes an implementation skeleton with `kgx.sink.TsvSink` and predicate selection rules.

GitHub URL:
- https://github.com/microbiomedata/metpo/blob/metatraits-entity-additions/docs/metatraits_kgx_encoding_examples.md

### 3. Full mapping specification

**File:** `docs/metatraits_to_metpo_mapping_specification.md`

Comprehensive spec covering:
- All 5 MetaTraits data access methods (REST API, taxonomy download, record download, web scraping, /traits catalog) with a comparison matrix
- The 4 trait format categories (composed boolean, uncomposed boolean, uncomposed factor, uncomposed numeric) with KGX mapping rules for each
- METPO's built-in mapping infrastructure (property synonyms, class synonyms, cross-ontology mappings)
- The "one way to say it" principle and anti-patterns to avoid
- ID allocation reference and safe ranges for new terms

GitHub URL:
- https://github.com/microbiomedata/metpo/blob/metatraits-entity-additions/docs/metatraits_to_metpo_mapping_specification.md

### 4. Resolver script (generates the lookup table)

**File:** `metpo/scripts/resolve_metatraits_in_sheets.py`
**CLI alias:** `resolve-metatraits-in-sheets`

Reads the MetaTraits card catalog and the METPO template sheets, then deterministically resolves each trait name to a METPO predicate and object. This is the script that produces the 97% coverage number.

GitHub URL:
- https://github.com/microbiomedata/metpo/blob/metatraits-entity-additions/metpo/scripts/resolve_metatraits_in_sheets.py

---

## Predicate selection rules (quick reference)

| Trait type | Predicate | Object | Example |
|-----------|-----------|--------|---------|
| Composed boolean (value=true) | METPO positive predicate (e.g., `METPO:2000011` ferments) | CHEBI/EC CURIE | `NCBITaxon:562 METPO:2000011 CHEBI:4167` |
| Composed boolean (value=false) | METPO negative predicate (e.g., `METPO:2000037` does not ferment) | CHEBI/EC CURIE | `NCBITaxon:562 METPO:2000037 CHEBI:4167` |
| Uncomposed boolean phenotype | `biolink:has_phenotype` | METPO class | `NCBITaxon:562 biolink:has_phenotype METPO:1000698` |
| Standalone process capability | `METPO:2000103` (capable of) | GO/METPO process | `NCBITaxon:562 METPO:2000103 GO:0009399` |
| Enzyme activity | `METPO:2000302` / `METPO:2000303` | EC number | `NCBITaxon:562 METPO:2000302 EC:1.11.1.6` |
| Numeric measurement | METPO data property (e.g., `METPO:2000701`) | `xsd:decimal` literal | `NCBITaxon:562 METPO:2000701 "32.3"` |
| Categorical factor | `biolink:has_phenotype` | METPO value class | `NCBITaxon:562 biolink:has_phenotype METPO:1000668` |

---

## Commit history on this branch (since 2026-02-13)

```
346d66d0 2026-02-20 Add format-aware label/synonym matching and new METPO entities for 97% KGX coverage
ad445406 2026-02-20 Add leading space to class template ID headers
5ca4a809 2026-02-20 Restore leading space on properties template ID headers
4555028c 2026-02-20 Address Copilot review: fix typos, mojibake, Makefile prereqs, and audit logic
0de1f3ad 2026-02-20 Add 21 new classes and 17 data properties for MetaTraits KGX encoding
9b511401 2026-02-20 Add CURIE audit script, build artifacts, and research docs
64192ec9 2026-02-19 Add MetaTraits synonym columns and draft template workflow
31237280 2026-02-13 Standardize SSSOM object_id normalization and curie_map-based parsing (#352)
4bf2de67 2026-02-13 Initial in-sheet MetaTraits resolver and predicate expansions (#349)
59c58e05 2026-02-13 Fix METPO:2000045 assay outcome: + -> - (#342) (#347)
a5ec7035 2026-02-13 Add MetaTraits mapping spec and ID allocation reference (#345) (#346)
```
