# MetaTraits-to-METPO Mapping Pipeline

## Problem

[MetaTraits](https://metatraits.embl.de/) is an EMBL database that unifies microbial
trait data across 2.2M genomes from two categories of sources:

- **Observed/curated data**: BacDive (culture-based assay results), BV-BRC, JGI/GOLD
  (genome metadata with curated phenotypes)
- **Genomic predictions**: BacDive-AI, GenomeSPOT, SPIRE (computational phenotype
  inference from genome sequences)

MetaTraits publishes 2,860 traits, each annotated with ontology CURIEs (GO, CHEBI,
OMP, MICRO, etc.). The trait definitions themselves are source-agnostic — "fermentation:
glucose" means the same thing whether it was observed in a culture assay or predicted
from a genome. The distinction between observed and predicted is carried at the
**per-organism assertion level**, not the trait definition level.

The goal is to express MetaTraits knowledge as KG-Microbe triples:

```
NCBITaxon:562  --[METPO:2000011 ferments]-->  CHEBI:17234 (glucose)
```

A previous approach (PR #332, Marcin's `create_metatraits_mappings.py` on the
`metatraits` branch) used fuzzy label matching to produce 420 SSSOM mappings, but
introduced semantic errors (e.g., "obligate aerobic" mapped to "obligately anaerobic")
and lost substrate specificity for all 308 composed traits.

## Approach

This pipeline uses **deterministic CURIE-based joining** (no fuzzy matching, no
embeddings) in three phases:

### Phase 1: Base trait CURIE join

Base traits (e.g., "fermentation", "cell shape", "thermophilic") are joined to METPO
classes by intersecting the ontology CURIEs that MetaTraits associates with each trait
against the CURIEs in METPO's `definition source` column (`metpo_sheet.tsv`).

Five hyper-generic GO CURIEs are excluded from the primary join to avoid noisy fan-out
(GO:0008152 metabolism, GO:0009058 biosynthetic process, etc.). They're used as fallbacks
at lower confidence only if no specific match is found.

### Phase 2: Composed trait two-part model

Composed traits (e.g., "fermentation: glucose") are decomposed into:
- **Process**: the non-CHEBI CURIEs (typically a GO term like GO:0006113 fermentation)
- **Substrate**: the CHEBI CURIE (e.g., CHEBI:17234 glucose)

The process CURIEs are joined to METPO classes the same way as Phase 1. The CHEBI
substrate is preserved in the SSSOM `comment` column.

### Phase 3: METPO property resolution

This is the key step for KG-Microbe edge generation. METPO's `metpo-properties.tsv`
defines ~50 object properties with synonyms that match MetaTraits base category names:

| MetaTraits category | METPO property (+) | METPO property (-) |
|--------------------|--------------------|-------------------|
| fermentation | `METPO:2000011` ferments | `METPO:2000037` does not ferment |
| assimilation | `METPO:2000002` assimilates | `METPO:2000027` does not assimilate |
| carbon source | `METPO:2000006` uses as carbon source | `METPO:2000031` does not use as... |
| hydrolysis | `METPO:2000013` hydrolyzes | `METPO:2000039` does not hydrolyze |
| ... | ... | ... |

The synonym column (`oboInOwl:hasRelatedSynonym 'fermentation'`) and assay outcome
column (`+`/`-`) are used to build the lookup. This resolves 25 of 31 MetaTraits
composed categories to METPO predicates.

**Six categories are currently unresolved** (no matching METPO property synonym):
ammonification, cell color, denitrification, enzyme activity, oxidation in darkness,
utilizes. These need new METPO properties or synonym additions.

## Files

| File | Description |
|------|-------------|
| `metatraits_cards.tsv` | 2,860 traits scraped from metatraits.embl.de/traits (input) |
| `metatraits_metpo_curie_join.sssom.tsv` | 250 SSSOM mappings: MetaTraits terms to METPO classes |
| `metatraits_kgx_edge_templates.tsv` | 2,557 rows: METPO predicate + CHEBI object per composed trait |
| `metatraits_metpo_curie_join_report.md` | Detailed results with property resolution table |

### metatraits_cards.tsv

Scraped by Marcin's `fetch_metatraits.py` (on the `metatraits` branch) from the
MetaTraits website. The website is the only source that publishes ontology CURIEs
per trait; the API and bulk downloads do not include them. (The filename uses "cards"
because Marcin's scraper parses Bootstrap `<div class="card">` HTML elements;
MetaTraits itself calls these "traits".)

Columns: `card_id`, `name`, `type`, `ontology_curies`, `ontology_urls`, `description`

- 81 base traits, 2,779 composed traits
- 826 unique CURIEs dominated by GO (2,530 references) and CHEBI (2,372)
- Types: boolean (2,825), factor (9), measurement units (um, Celsius, %, etc.)

This file captures **trait definitions only**, not per-organism assertions. It does not
indicate which organisms have which traits, nor whether a trait was observed or predicted.

### metatraits_metpo_curie_join.sssom.tsv

Standard SSSOM format. The `comment` column preserves substrate information for
composed traits, e.g.:

```
Process CURIE: GO:0009060 | Substrate: cellobiose (CHEBI:17057)
```

### metatraits_kgx_edge_templates.tsv

**This is NOT a standard KGX artifact.** It's a lookup table mapping each composed
MetaTraits trait to its resolved METPO predicate and CHEBI object. It does NOT contain
subjects (organisms) — those come from querying MetaTraits per-organism data.

To generate actual KG-Microbe edges, a script should:
1. Query MetaTraits for per-organism trait assertions (e.g., "genome X has trait
   fermentation: glucose with positive result")
2. Look up the METPO predicate from this table (or embed the logic directly)
3. Emit: `organism_curie → METPO:2000011 → CHEBI:17234`
4. For negative results, use the `negative_predicate_id` column instead
5. Set `knowledge_level` and `agent_type` based on the **source database**:
   - Observed data (BacDive, BV-BRC, GOLD): `knowledge_assertion` / `manual_agent`
   - Predictions (BacDive-AI, GenomeSPOT, SPIRE): `prediction` / `automated_agent`

The MetaTraits API exposes which database each per-organism assertion comes from
(via the `?databases=` parameter), so observed vs. predicted can be resolved at
edge generation time.

The `cmm-ai-automation` repo provides the reference implementation for KGX edge
generation — scripts there query MongoDB/APIs and emit `KGXEdge` objects directly
without an intermediate template file.

## Regenerating

```bash
make data/mappings/metatraits_metpo_curie_join.sssom.tsv
```

Or directly:

```bash
uv run curie-join-metatraits \
  -m data/mappings/metatraits_cards.tsv \
  -t src/templates/metpo_sheet.tsv \
  -p src/templates/metpo-properties.tsv \
  -o data/mappings/metatraits_metpo_curie_join.sssom.tsv \
  -k data/mappings/metatraits_kgx_edge_templates.tsv \
  -r data/mappings/metatraits_metpo_curie_join_report.md
```

## Results summary

| Metric | Value |
|--------|------:|
| SSSOM mappings | 250 (zero semantic errors) |
| KGX edge templates | 2,557 |
| Categories resolved to METPO predicates | 25 / 31 |
| Composed traits with CHEBI objects | 2,163 / 2,557 |
| Semantic errors | 0 |

## Known issues

- **METPO:2000045** (`is not required for growth`) is incorrectly marked `+` in
  `metpo-properties.tsv` — should be `-`. See issue #342.
- **Six unresolved categories**: ammonification, cell color, denitrification, enzyme
  activity, oxidation in darkness, utilizes.
- **394 composed traits lack CHEBI objects** — their substrates (e.g., "chemoheterotrophy",
  "casamino acids") don't have CHEBI CURIEs in the MetaTraits data.
- **OMP:0005009 fan-out**: `acidophilic` maps to 5 METPO terms via a shared OMP CURIE
  that covers all pH-related phenotypes.

## Relationship to other mapping files

| File | Source | Approach |
|------|--------|----------|
| `metatraits_metpo_curie_join.sssom.tsv` | This pipeline | Deterministic CURIE join |
| `metpo_mappings_combined_relaxed.sssom.tsv` | Alignment pipeline | ChromaDB semantic + OLS embeddings |
| `metpo_mappings_optimized.sssom.tsv` | Alignment pipeline | Optimized semantic matches |
| (on `metatraits` branch) `metatraits_metpo_kgmicrobe.sssom.tsv` | Marcin's script | Fuzzy label matching |

## Observed vs. predicted data

MetaTraits integrates both culture-based observations and computational predictions,
but this distinction is **not captured in the trait definitions** — it exists only in the
per-organism assertion data. When generating KG-Microbe edges, the source database
determines the appropriate KGX provenance metadata:

| Source type | Databases | `knowledge_level` | `agent_type` |
|------------|-----------|-------------------|-------------|
| Observed/curated | BacDive, BV-BRC, JGI/GOLD, JGI/IMG | `knowledge_assertion` | `manual_agent` |
| Predicted | BacDive-AI, GenomeSPOT, SPIRE, proGenomes | `prediction` | `automated_agent` |

The current edge template file hardcodes `knowledge_assertion` / `manual_agent` for
all rows. This is a placeholder — the actual values must be set per-assertion at edge
generation time based on which MetaTraits database the assertion came from.

## Next steps

1. **Generate actual KG-Microbe edges**: Write a script (following `cmm-ai-automation`
   patterns) that queries MetaTraits per-organism data and emits KGX edges using the
   METPO predicate resolution logic built here. Must handle observed vs. predicted
   provenance correctly.
2. **Fix METPO:2000045** assay outcome (issue #342).
3. **Add METPO properties** for the 6 unresolved categories.
4. **Improve CHEBI coverage** for the 394 substrates without CURIEs.

## Related issues

- #341 — This work
- #342 — METPO:2000045 assay outcome bug
- #340 — Strategic question: CURIE join vs label matching
- #332 — Marcin's label matching PR
- #333-#336 — Quality issues in PR #332
