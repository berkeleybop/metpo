# MetaTraits-to-METPO Mapping Specification

**Date:** 2026-02-13
**Branch:** issue-341-curie-join-sssom
**Related issues:** #341 (MetaTraits CURIE-join mapping), #344 (SSSOM migration)

---

## 1. Goal

Express ALL MetaTraits trait assertions as KGX edges using METPO and Biolink predicates,
with METPO objects or objects from high-quality encyclopedic ontologies (CHEBI, GO, OMP, etc.).

Companion implementation guide with runnable commands and concrete KGX examples:
`docs/metatraits_kgx_encoding_examples.md`
External-repo implementation handoff guide:
`docs/metatraits_external_repo_handoff.md`

**Design constraints:**
- One canonical edge per fact (no multiple ways of saying the same thing)
- Easy for humans to make new assertions in the future
- Easy to query from kg-microbe with minimal query patterns
- Efficient for ML (clean signal, no redundant representations)
- No blank nodes (KGX-incompatible) -- use data properties directly on organisms

---

## 2. MetaTraits Data Access Methods

MetaTraits (metatraits.embl.de) exposes trait data through 5 methods.
The trait `name` string (e.g., "fermentation: D-glucose") is the universal join key.
Two methods also return ontology CURIEs directly.

### 2.1 REST API

- **URL:** `GET /api/v1/traits/taxonomy/{taxid}?databases=...`
- **Query by:** NCBI taxon ID (only method that accepts taxon ID)
- **Response fields:** `{database, feature, record_link, tax_id, unit, value}`
- **CURIEs:** No
- **Strengths:** Per-observation provenance, database attribution, tax_id in response
- **Weaknesses:** No ontology CURIEs

Known databases for D. radiodurans (taxid 1299):
BacDive-AI:proGenomes3, BacDive:2025-07-29, Genome statistics:proGenomes3,
GenomeSPOT:proGenomes3, MICROPHERRET:proGenomes3, Traitar:proGenomes3

### 2.2 Taxonomy Download

- **URL:** `GET /taxonomy/download?query={species_name}&rank=species`
- **Query by:** Species name only (does NOT accept taxon IDs)
- **Response fields:** `{name, is_ai, num_observations, unique_databases, majority_label, percentages, ontologies}`
- **CURIEs:** Yes -- `ontologies` array contains GO, CHEBI, OMP, SNOMED CURIEs
- **Strengths:** CURIEs per trait, is_ai flag (experimental vs predicted)
- **Weaknesses:** Name-based query only, no taxon ID

### 2.3 Record Download

- **URL:** `GET /record/download?query={GCA_accession}`
- **Query by:** GCA genome accession
- **Response fields:** Same as taxonomy download
- **CURIEs:** Yes
- **Strengths:** Per-genome, has CURIEs
- **Weaknesses:** All AI predictions, GCA-based query only

### 2.4 Web Page Scraping (summaryData JSON embedded in HTML)

- **Taxonomy URL:** `GET /taxonomy?query={species_name}&rank=species`
- **Record URL:** `GET /record?query={GCA_accession}`
- **Data:** `var summaryData = {...}` JSON blob embedded in HTML `<script>` tag
- **Fields per trait:** `{name, display_name, is_ai, is_discrete, link, majority_label, num_observations, percentages, unique_databases, histogram_counts, labels}`
- **CURIEs:** No
- **Strengths:** Category grouping (tab -> category -> trait), `is_discrete` flag, histogram data
- **Note:** Name-based query only; does NOT accept taxon IDs

### 2.5 Traits Page Scraping (global trait catalog)

- **URL:** `GET /traits`
- **Existing script:** `fetch-metatraits` (metpo/scripts/fetch_metatraits.py)
- **Output:** `data/mappings/metatraits_cards.tsv` (2,860 rows)
- **Fields:** `{card_id, name, type, ontology_curies, ontology_urls, description}`
- **CURIEs:** Yes -- this is the ONLY source that publishes ontology CURIEs per trait definition
- **Scope:** Global (all traits, not per-organism)

### 2.6 Comparison Matrix

| Criterion                  | REST API | Tax Download | Record DL | Web Page | /traits |
|----------------------------|----------|-------------|-----------|----------|---------|
| Query by taxon ID          | Yes      | No          | No        | No       | N/A     |
| Query by species name      | No       | Yes         | No        | Yes      | N/A     |
| Query by GCA accession     | No       | No          | Yes       | Yes      | N/A     |
| CURIEs in response         | No       | Yes         | Yes       | No       | Yes     |
| is_ai flag                 | Via DB   | Yes         | Yes       | Yes      | N/A     |
| Per-observation provenance | Yes      | No          | No        | No       | N/A     |
| Category grouping          | No       | No          | No        | Yes      | No      |
| Scope                      | Per-org  | Per-species | Per-genome| Per-org  | Global  |

### 2.7 Internal Flask Endpoints (discovered via JavaScript analysis)

The MetaTraits Flask app exposes additional internal endpoints:
- `/search_autocomplete` -- GET with query, taxonomy params
- `/update_databases` -- POST with JSON {"databases": [...]}
- `/observations` -- session-bound, requires Flask session state from page load
- `/genome-search/download-file/`, `/genome-search/check-progress/`, `/genome-search/display-results/`

The `/observations` endpoint powers the DataTable on taxonomy/record pages but requires
cookies from a prior page load and returns non-JSON without proper session state.
The `?include_ontologies=true` parameter is silently ignored by the REST API.

---

## 3. MetaTraits Trait Format Taxonomy

MetaTraits reports ~2,860 distinct traits. These fall into 4 categories, each with a
different mapping strategy to KGX edges.

### 3.1 Composed Boolean Traits (~2,600 types)

Format: `"base: substrate"` with value `true`/`false`

Examples: `fermentation: D-glucose`, `enzyme activity: catalase (EC1.11.1.6)`,
`growth: acetate`, `hydrolysis: gelatin`, `produces: hydrogen sulfide`

**KGX mapping:** Use METPO object property as predicate, foreign CURIE (CHEBI, GO MF) as object.

```
# value=true: use positive predicate
NCBITaxon:1299 -> METPO:2000011 (ferments) -> CHEBI:4167 (D-glucose)

# value=false: use negative predicate
NCBITaxon:1299 -> METPO:2000037 (does not ferment) -> CHEBI:4167 (D-glucose)
```

For enzyme activities, use native MetaTraits enzyme object CURIEs first
(typically `EC:*`), and avoid generic SNOMED:424017009 placeholders:
```
NCBITaxon:1299 -> METPO:2000302 (shows activity of) -> EC:1.11.1.6
NCBITaxon:1299 -> METPO:2000303 (does not show activity of) -> EC:1.11.1.6
```

Optional later normalization: map EC to GO MF via ec2go for interoperability.
Operational ingestion should preserve native MetaTraits object CURIEs first
(e.g., `EC:*`) and treat EC->GO as a derived view, not a required transform.
This is not required for initial operational ingest.

**Coverage:** 27 of 31 MetaTraits composed bases have existing METPO predicates.
3 new predicate pairs needed (see Section 5).

### 3.2 Uncomposed Boolean Traits (~38 types)

Format: standalone trait name with value `true`/`false`

Examples: `aerotolerant`, `gram positive`, `sporulation`, `presence of motility`

**KGX mapping:** Use `biolink:has_phenotype` as predicate, METPO phenotype class as object.

```
# value=true
NCBITaxon:1299 -> biolink:has_phenotype -> METPO:1000609 (aerotolerant)

# Traits where true/false map to distinct classes:
# "sporulation" value=true
NCBITaxon:1299 -> biolink:has_phenotype -> METPO:1000871 (spore forming)
# "sporulation" value=false
NCBITaxon:1299 -> biolink:has_phenotype -> METPO:1000872 (non-spore forming)
```

Note: Use `biolink:has_phenotype` (not METPO:2000102) since KGX is a Biolink-native format.
Map `METPO:2000102 skos:exactMatch biolink:has_phenotype` in SSSOM (issue #344).

**Standalone metabolic processes** (nitrogen fixation, nitrification, fermentation-boolean,
denitrification pathway) use `capable of`:
```
NCBITaxon:1299 -> METPO:2000103 (capable of) -> GO:0009399 (nitrogen fixation)
NCBITaxon:1299 -> METPO:2000103 (capable of) -> METPO:1005001 (nitrification)
NCBITaxon:1299 -> METPO:2000103 (capable of) -> GO:0019333 (denitrification)
NCBITaxon:1299 -> METPO:2000103 (capable of) -> METPO:1002005 (Fermentation)
```

### 3.3 Uncomposed Factor Traits (~4 types)

Format: trait name with categorical text value

Examples: `cell shape` -> "coccus-shaped", `oxygen preference` -> "aerobic",
`biosafety level` -> "level 1", `temperature preference` -> "mesophilic"

**KGX mapping:** Use `biolink:has_phenotype` with the specific METPO value class.

```
NCBITaxon:1299 -> biolink:has_phenotype -> METPO:1000668 (coccus shaped)
NCBITaxon:1299 -> biolink:has_phenotype -> METPO:1000602 (aerobic)
NCBITaxon:1299 -> biolink:has_phenotype -> METPO:1001102 (biosafety level 1)
NCBITaxon:1299 -> biolink:has_phenotype -> METPO:1000615 (mesophilic)
```

MetaTraits factor values -> METPO classes:
- Cell shape values: mapped via BacDive synonyms already in metpo_sheet.tsv (31 shape classes)
- Oxygen preference: 12 classes (METPO:1000601-1000612)
- Biosafety level: 5 classes (METPO:1001102-1001106)
- Temperature preference: 7+ classes (METPO:1000614-1000721)
- Flagellum arrangement: NEEDS new classes (see Section 5)

### 3.4 Uncomposed Numeric Traits (~14 types)

Format: trait name with decimal value and unit

Examples: `temperature growth` -> 32.3 Celsius, `pH minimum` -> 5.4,
`genome size` -> 3283189 bp, `GC percentage` -> 66.6 %

**KGX mapping:** Use NEW data properties directly on the organism (no blank nodes).
Optionally ALSO emit a binned phenotype class edge.

```
# Raw numeric value (new data property)
NCBITaxon:1299 -> METPO:2000701 (has growth temperature value) -> "32.3"^^xsd:decimal

# Binned categorical class (existing bin class)
NCBITaxon:1299 -> biolink:has_phenotype -> METPO:1000445 (temperature optimum mid3)
```

These are NOT redundant -- the data property carries the exact measurement,
the phenotype class carries the categorical classification. Different consumers want different things.

MetaTraits units: %, % NaCl (w/v), % w/v NaCl, Celsius, boolean, bp, factor, genes, pH

---

## 4. METPO's Built-in Mapping Infrastructure

METPO already embeds external data source mappings through qualified synonyms in ROBOT templates.
This is the primary mechanism for resolving MetaTraits trait names to METPO entities.
NO external mapping file (SSSOM, translation_table.yaml, custom_curies.yaml) is needed
for the MetaTraits-to-METPO operational mapping.

### 4.1 Property Synonyms (metpo-properties.tsv)

Each property row has:
- **`synonym property and value TUPLES`**: e.g., `oboInOwl:hasRelatedSynonym 'fermentation'`
- **`synonym source`**: e.g., `https://bacdive.dsmz.de/`
- **`assay outcome`**: `+` or `-` (routes to positive or negative predicate)

Resolution logic:
1. Parse MetaTraits trait name: `"fermentation: D-glucose"` -> base=`"fermentation"`, substrate=`"D-glucose"`
2. Look up base in synonym column: `'fermentation'` matches METPO:2000011 (outcome=+) and METPO:2000037 (outcome=-)
3. If MetaTraits value=true, use METPO:2000011; if value=false, use METPO:2000037
4. Substrate `"D-glucose"` -> CHEBI CURIE from MetaTraits `ontologies` field or metatraits_cards.tsv

### 4.2 Class Synonyms (metpo_sheet.tsv)

Each class row has database-specific synonym columns:
- **`madin synonym or field`** + **`Madin synonym source`**
- **`bacdive keyword synonym`** + **`Bacdive synonym source`**
- **`bactotraits related synonym`** + **`Bactotraits synonym source`**
- **`confirmed exact synonym`**
- **`biolink close match`** (skos:closeMatch for Biolink equivalents)
- **`definition source`** (IAO:0000119 -- carries cross-references to OMP, MICRO, SNOMED, etc.)

MetaTraits trait names are overwhelmingly the same strings as BacDive synonyms since
MetaTraits aggregates BacDive data. To make the mapping explicit, add a MetaTraits synonym
column or extend the existing synonym source to include `https://metatraits.embl.de/`.

### 4.3 Cross-Ontology Mappings

Currently stored as `definition source` annotations (IAO:0000119). This conflates
provenance ("where I got the definition") with semantic mapping ("this term is equivalent to").
Issue #344 tracks migrating these to proper SSSOM with `skos:exactMatch` / `skos:closeMatch`.

---

## 5. New METPO Terms Needed

### 5.1 New Object Properties (3 pairs = 6 properties)

These are biochemically distinct from existing predicates (confirmed via research):

| Proposed ID | Label | Neg. ID | Neg. Label | MetaTraits base | Substrates |
|-------------|-------|---------|------------|-----------------|------------|
| METPO:2000601 | denitrifies | METPO:2000602 | does not denitrify | denitrification | nitrate, nitrite, nitrous oxide |
| METPO:2000603 | ammonifies | METPO:2000604 | does not ammonify | ammonification | nitrate, nitrite |
| METPO:2000605 | oxidizes in darkness | METPO:2000606 | does not oxidize in darkness | oxidation in darkness | hydrogen, iron, sulfide, sulfur compounds |

**Why these are NOT synonyms of existing predicates:**

- **Denitrification** (GO:0019333): NO3->NO2->NO->N2O->N2 (removes nitrogen as gas).
  NOT the same as `reduces` (METPO:2000017). A microbe can reduce nitrate via DNRA
  (producing NH4+) or assimilatory reduction (into biomass) without denitrifying.
  Denitrification requires four specific enzymes: Nar/Nap, NirS/NirK, Nor, Nos.

- **Ammonification/DNRA** (GO:0071941 too broad): NO3->NO2->NH4+ (retains nitrogen).
  NOT the same as `reduces`. The end product (ammonium vs nitrite vs N2) matters ecologically.
  DNRA and denitrification are competing pathways with opposite ecosystem effects.

- **Oxidation in darkness**: Chemolithotrophic oxidation without light.
  Distinct from `oxidizes` (METPO:2000016) because it specifies the metabolic context.

**Cell color** does NOT need a new predicate -- use `biolink:has_phenotype` -> existing
METPO pigmentation classes (METPO:1003022-1003031).

### 5.2 New Data Properties (~17 properties)

These replace the observation-class pattern that creates blank nodes.
Domain: microbe. Range: xsd:decimal.

| Proposed ID | Label | Unit | MetaTraits feature |
|-------------|-------|------|--------------------|
| METPO:2000701 | has growth temperature value | Celsius | temperature growth |
| METPO:2000702 | has minimum temperature value | Celsius | temperature minimum |
| METPO:2000703 | has maximum temperature value | Celsius | temperature maximum |
| METPO:2000704 | has growth pH value | pH | pH growth |
| METPO:2000705 | has minimum pH value | pH | pH minimum |
| METPO:2000706 | has maximum pH value | pH | pH maximum |
| METPO:2000707 | has growth salinity value | % NaCl w/v | salinity growth |
| METPO:2000708 | has minimum salinity value | % NaCl w/v | salinity minimum |
| METPO:2000709 | has maximum salinity value | % NaCl w/v | salinity maximum |
| METPO:2000711 | has genome size value | bp | genome size |
| METPO:2000712 | has estimated genome size value | bp | estimated genome size |
| METPO:2000713 | has gene count value | genes | gene count |
| METPO:2000714 | has estimated gene count value | genes | estimated gene count |
| METPO:2000715 | has GC percentage value | % | GC percentage |
| METPO:2000716 | has coding density value | % | coding density |
| METPO:2000721 | has cell length value | µm | cell length |
| METPO:2000722 | has cell width value | µm | cell width |

### 5.3 New Phenotype Classes (17 classes)

| Proposed ID | Label | Parent | MetaTraits trait | External mapping |
|-------------|-------|--------|------------------|-----------------|
| METPO:1005001 | nitrification | biological process | nitrification | OMIT:0027217 (bad mapping); sub-steps: GO:0019329 + GO:0019332 |
| METPO:1005011 | indole test positive | phenotype | indole test (true) | MICRO:0000430 |
| METPO:1005012 | indole test negative | phenotype | indole test (false) | |
| METPO:1005013 | methyl red test positive | phenotype | methyl red test (true) | SNOMED:5894006 |
| METPO:1005014 | methyl red test negative | phenotype | methyl red test (false) | |
| METPO:1005015 | Voges-Proskauer test positive | phenotype | voges-proskauer test (true) | SNOMED:66592006 |
| METPO:1005016 | Voges-Proskauer test negative | phenotype | voges-proskauer test (false) | |
| METPO:1005021 | capnophilic | oxygen preference | capnophilic | SNOMED:413748004 |
| METPO:1005022 | hemolytic | phenotype | presence of hemolysis (true) | OMP:0005117 |
| METPO:1005023 | non-hemolytic | phenotype | presence of hemolysis (false) | |
| METPO:1005031 | peritrichous flagellation | flagellated | flagellum arrangement | OMP:0000078 children |
| METPO:1005032 | polar flagellation | flagellated | flagellum arrangement | |
| METPO:1005033 | amphitrichous flagellation | flagellated | flagellum arrangement | |
| METPO:1005034 | lophotrichous flagellation | flagellated | flagellum arrangement | |
| METPO:1005035 | monotrichous flagellation | flagellated | flagellum arrangement | |
| METPO:1005036 | lateral flagellation | flagellated | flagellum arrangement | |
| METPO:1005037 | subpolar flagellation | flagellated | flagellum arrangement | |

---

## 6. Nitrogen Cycle Biochemistry Reference

This section documents why the nitrogen cycle predicates are distinct.
Marcin suggested some might be synonyms of existing terms -- this is incorrect.

```
Nitrogen cycle overview:

N2 (atmosphere)
  |
  | nitrogen fixation (GO:0009399) -- N2 -> NH3 via nitrogenase
  v
NH4+ (ammonium)
  |
  | nitrification step 1: ammonia oxidation (GO:0019329) -- NH3 -> NO2-
  v
NO2- (nitrite)
  |
  | nitrification step 2: nitrite oxidation (GO:0019332) -- NO2- -> NO3-
  v
NO3- (nitrate)
  |
  +---> denitrification (GO:0019333) -- NO3- -> NO2- -> NO -> N2O -> N2
  |     (removes nitrogen from ecosystem as gas)
  |
  +---> ammonification/DNRA -- NO3- -> NO2- -> NH4+
  |     (retains nitrogen in ecosystem)
  |
  +---> assimilatory nitrate reduction (GO:0042128) -- NO3- -> NH4+ -> biomass
  |     (incorporates nitrogen into cell material)
  |
  +---> generic nitrate reduction -- NO3- -> NO2- (may stop here)
        (MetaTraits "reduction: nitrate" -- mapped to obsolete GO:0055114)
```

Key distinctions:
- Denitrification: complete pathway to N2 gas, requires 4 specific enzymes
- Ammonification (DNRA): produces NH4+, uses Nrf enzyme system
- Assimilatory reduction: anabolic, into biomass
- Generic reduction: can be any of the above; MetaTraits mapping to GO:0055114 is obsolete

Capnophilic: NOT a metabolic process. Growth phenotype (CO2-requiring), analogous to
aerotolerant, microaerophilic, halophilic. No GO term exists. Use `has_phenotype`.

---

## 7. Existing METPO Bin Boundaries

METPO defines 84 numeric bin classes. These are used for categorical phenotype assertions
alongside the raw data property values.

### Temperature (Celsius)

**Optimum (7 bins):** <=10, 10-22, 22-27, 27-30, 30-34, 34-40, >=40
- METPO:1000441 through METPO:1000447

**Range (7 bins):** <=10, 10-22, 22-27, 27-30, 30-34, 34-40, >=40
- METPO:1000448 through METPO:1000454

**Delta (5 bins):** 1-5, 5-10, 10-20, 20-30, >=30
- METPO:1000483 through METPO:1000487

### pH

**Optimum (4 bins):** 0-6, 6-7, 7-8, 8-14
- METPO:1000455 through METPO:1000458

**Range (6 bins):** 0-4, 4-6, 6-7, 7-8, 8-10, 10-14
- METPO:1000459 through METPO:1000464

**Delta (6 bins):** <=1, 1-2, 2-3, 3-4, 4-5, 5-9
- METPO:1000473 through METPO:1000478

### NaCl (% w/v)

**Optimum (4 bins):** <=1, 1-3, 3-8, >=8
- METPO:1000465 through METPO:1000468

**Range (4 bins):** <=1, 1-3, 3-8, >=8
- METPO:1000469 through METPO:1000472

**Delta (4 bins):** <=1, 1-3, 3-8, >=8
- METPO:1000479 through METPO:1000482

### GC Content (%)

**4 bins:** <=42.65, 42.65-57, 57-66.3, >=66.3
- METPO:1000429 through METPO:1000432

### Cell Dimensions (um)

**Cell length (4 bins):** <=1.3, 1.3-2, 2-3, >=3
- METPO:1000883 through METPO:1000886

**Cell width (4 bins):** <=0.5, 0.5-0.65, 0.65-0.9, >=0.9
- METPO:1000887 through METPO:1000890

### Bins Still Needed

Genome size, gene count, and coding density need bin boundaries.
Derive from MetaTraits data distribution (future work).

---

## 8. METPO ID Allocation Reference

### 8.1 ID Range Policy (from metpo-idranges.owl)

- **Range 1:** 0 to 999,999 (ONTOLOGY-CREATOR)
- **Range 2:** 1,000,000 to 1,999,999 (ADDITIONAL EDITOR)

In practice, classes use 1xxxxxx and properties use 2xxxxxx.

### 8.2 Historically Allocated IDs

**1,228 unique METPO IDs** have ever been allocated across:
- `src/templates/metpo_sheet.tsv` (current class template)
- `src/templates/metpo-properties.tsv` (current property template)
- `metadata/ontology/historical_submissions/entity_extracts/metpo_submission_*_all_entities.tsv` (9 historical BioPortal submission extracts)

**Highest allocated IDs:**
- Classes: METPO:1004005 (in metpo_sheet.tsv)
- Properties: METPO:2000518 (in metpo-properties.tsv)
- Historical: METPO:2000103 (submission 10, dated 2025-09-23)
- Test placeholder: METPO:9999999 (submissions 3-5, ignore)

### 8.3 Historical Submissions Summary

| Submission | Unique IDs | Highest Real ID | Date |
|------------|-----------|-----------------|------|
| 2 | 274 | METPO:000274 | Early (malformed IDs with leading zeros) |
| 3 | 300 | METPO:1021 + 9999999 placeholder | Early |
| 4 | 296 | same | Early |
| 5 | 298 | same | Early |
| 6 | 536 | METPO:2000007 | Expanded |
| 7 | 524 | METPO:2000051 | Expanded |
| 8 | 536 | METPO:2000102 | Nearly current |
| 9 | 296 | METPO:2000103 | Current |
| 10 | 265 | METPO:2000103 | 2025-09-23 |

### 8.4 Current ID Block Usage (with topical groupings)

**Class IDs (METPO:1xxxxxx):**

| Block | Range | Topic | Status |
|-------|-------|-------|--------|
| 1000059-1000060 | 1000059-1000060 | Root classes (phenotype, metabolism) | In use |
| 1000127 | 1000127 | GC content | In use |
| 1000155 | 1000155 | Hemolysis (historical only, not in current release) | Historical |
| 1000186-1000188 | 1000186-1000188 | Upper-level (material entity, quality) | In use |
| 1000232 | 1000232 | pH delta | In use |
| 1000303-1000335 | 1000303-1000335 | Numeric phenotype parents (temp/pH/NaCl optimum/range/delta) | In use |
| 1000429-1000487 | 1000429-1000487 | Numeric bin classes (GC, temperature, pH, NaCl) | In use |
| 1000525-1000537 | 1000525-1000537 | Entity classes (microbe, chemical entity, enzyme) + numeric phenotype parents | In use |
| 1000601-1000631 | 1000601-1000631 | Oxygen preference + trophic type | In use |
| 1000632-1000665 | 1000632-1000665 | Trophic type subclasses | In use |
| 1000666-1000706 | 1000666-1000706 | Cell shape + motility classes | In use |
| 1000720-1000731 | 1000720-1000731 | Additional preferences (psychrophilic variants, nutrient adaptation) | In use |
| 1000800-1000806 | 1000800-1000806 | Metabolic process classes (respiration, phosphorylation) | In use |
| 1000844-1000846 | 1000844-1000846 | Specialized metabolism (methanogenesis, acetogenesis) | In use |
| 1000870-1000890 | 1000870-1000890 | Sporulation + cell dimension bins | In use |
| 1001000-1001023 | 1001000-1001023 | Observation classes (DO NOT USE -- leads to blank nodes) | In use but deprecated for KGX |
| 1001101-1001106 | 1001101-1001106 | Biosafety level | In use |
| 1002003-1002006 | 1002003-1002006 | Cable bacteria, fermentation, syntrophy | In use |
| 1003000-1003031 | 1003000-1003031 | pH preference + pigmentation | In use |
| 1004000-1004005 | 1004000-1004005 | Pathogenicity + growth medium | In use |

**Property IDs (METPO:2xxxxxx):**

| Block | Range | Topic | Status |
|-------|-------|-------|--------|
| 2000001-2000051 | 2000001-2000051 | Chemical interaction properties (+/-) | In use |
| 2000052-2000063 | 2000052-2000063 | Observation properties + data props (blank-node pattern) | In use but deprecated for KGX |
| 2000071 | 2000071 | has value (generic numeric data property) | In use |
| 2000101-2000103 | 2000101-2000103 | has quality, has phenotype, capable of | In use |
| 2000200-2000232 | 2000200-2000232 | Chemical conversion properties (+/-) | In use |
| 2000239 | 2000239 | has pH observation | In use but deprecated for KGX |
| 2000301-2000303 | 2000301-2000303 | Enzyme activity properties | In use |
| 2000501-2000518 | 2000501-2000518 | pH/NaCl/oxygen observation properties + growth medium | In use (observation ones deprecated for KGX) |

### 8.5 Safe ID Ranges for New Allocations

| Range | Available IDs | Proposed use |
|-------|--------------|-------------|
| METPO:1005001-1005050 | 50 | New classes (nitrogen processes, biochemical tests, phenotypes, flagellum) |
| METPO:1005051-1005999 | 949 | Future class expansions |
| METPO:2000601-2000610 | 10 | New nitrogen cycle object properties |
| METPO:2000701-2000730 | 30 | New data properties (temperature, pH, salinity, genome, cell) |
| METPO:2000731-2000999 | 269 | Future property expansions |

**DO NOT reuse any ID <= METPO:2000518 or <= METPO:1004005.**
**DO NOT use METPO:9999999 (historical test placeholder).**
**DO NOT use any ID found in the historical submission entity extracts.**

---

## 9. "One Way to Say It" Principle

### 9.1 Avoid Redundant Edge Patterns

For `"fermentation: D-glucose"` value=true, emit ONLY:
```
NCBITaxon:1299 -> METPO:2000011 (ferments) -> CHEBI:4167 (D-glucose)
```
Do NOT also emit:
```
NCBITaxon:1299 -> METPO:2000103 (capable of) -> GO:0006113 (fermentation)
```
The METPO predicate `ferments` already encodes the process semantics.
The GO process CURIE is a mapping target (for SSSOM), not a second edge.

The standalone boolean `"fermentation"` (uncomposed) DOES get its own edge:
```
NCBITaxon:1299 -> METPO:2000103 (capable of) -> METPO:1002005 (Fermentation)
```
This is a DIFFERENT assertion (general capability) from the substrate-specific one.

### 9.2 Predicate Selection Rules

1. **Composed trait with METPO predicate available:** Use METPO predicate -> CHEBI/GO object
2. **Uncomposed boolean phenotype:** Use `biolink:has_phenotype` -> METPO class
3. **Standalone metabolic capability:** Use `METPO:2000103 (capable of)` -> GO/METPO process
4. **Enzyme activity:** Use `METPO:2000302 (shows activity of)` -> GO molecular function
5. **Numeric measurement:** Use METPO data property -> xsd:decimal literal
6. **Categorical factor:** Use `biolink:has_phenotype` -> METPO value class

### 9.3 METPO:2000102 vs biolink:has_phenotype

These are equivalent. Use `biolink:has_phenotype` in KGX edges (Biolink-native format).
Map them in SSSOM (issue #344): `METPO:2000102 skos:exactMatch biolink:has_phenotype`.

---

## 10. MetaTraits CURIE Quality Issues

MetaTraits' own ontology mappings have several known issues that our pipeline must handle:

- **Enzyme activities:** Often mapped to generic SNOMED:424017009 regardless of enzyme. Prefer native EC CURIEs first; optional GO MF normalization can be layered later.
- **EC number format:** MetaTraits uses `EC3.2.1.4` (no colon). Standard CURIE is `EC:3.2.1.4`.
- **BRENDA URLs:** Malformed ecno parameter (e.g., `ecno=.2.1.4` -- first digit missing).
- **Nitrification:** Mapped to OMIT:0027217 (a miRNA ontology term -- wrong ontology entirely).
- **Ammonification:** Mapped to GO:0071941 (nitrogen cycle metabolic process -- too broad).
- **Reduction:** Mapped to GO:0055114 (now obsolete in GO).
- **~40% of composed traits** in metatraits_cards.tsv have only the process GO CURIE but are missing the substrate CHEBI CURIE.

---

## 11. Implementation Checklist

- [ ] Create GitHub issue for new METPO terms
- [ ] Create branch from main
- [ ] Add 6 new object properties to metpo-properties.tsv (denitrifies, ammonifies, oxidizes in darkness + negatives)
- [ ] Add ~17 new data properties to metpo-properties.tsv
- [ ] Add ~18 new classes to metpo_sheet.tsv
- [ ] Add MetaTraits synonym annotations to all relevant existing + new terms
- [ ] Write coverage validation script (reads metatraits_cards.tsv, verifies every trait resolves to METPO predicate + object)
- [ ] Build ontology and run tests
- [ ] Define bin boundaries for genome size, gene count, coding density
- [ ] Update curie_join_metatraits.py to use the new term resolution logic
- [ ] Fix SSSOM to pass sssom validate (or remove in favor of template-embedded mappings)
