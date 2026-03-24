# MetaTraits API Data, MongoDB Collections, and Anthea's Download Work

**Created:** 2026-02-19

---

## Anthea's Current Work

Anthea Guo is downloading the full MetaTraits dataset by querying the API for every NCBI taxonomy ID known to KG-Microbe. Her pipeline:

- **Source:** `https://metatraits.embl.de/api/v1/traits/taxonomy/{tax_id}` (all databases)
- **Method:** Python producer-consumer pipeline streaming API responses to Google Drive
- **Storage:** Google Drive shared folder `CultureBot_collaboration → MetaTraits` ([link](https://drive.google.com/drive/folders/0AK9VwyLqCr3kUk9PVA))
- **Progress (as of 2026-02-16):** 33,900 / 2,693,506 taxa (1.3%), 3.35 GB, ~768 hours ETA
- **File naming:** `{tax_id}__all.json` (one file per taxon)

Anthea has **not started** the KGX transform step. She is still in the download phase.

### Decided approach for KGX transform

Per issues [#340](https://github.com/berkeleybop/metpo/issues/340) and [#339](https://github.com/berkeleybop/metpo/issues/339), the team decided against using the SSSOM label-matching approach (PR #332) for operational MetaTraits assertion instantiation. Instead, the KGX transform should use **deterministic METPO template mechanisms**: qualified synonyms, property synonym tuples, and assay outcome routing from the METPO sheets directly.

Key points from the decision:
- MetaTraits cards already publish GO (2,530 cards) and CHEBI (2,372 cards) CURIEs — these go directly into KG-Microbe as objects
- METPO predicates (ferments, does_not_ferment, etc.) provide the relational vocabulary for KG-Microbe edges
- The SSSOM label-matching approach only covered 12% of cards (362/2,860) and lost substrate specificity
- SSSOM is kept alive only for long-run curated cross-ontology publication (issue #344), not for operational transform

Marcin pointed Anthea to `src/templates/metpo_sheet.tsv` on 2026-02-18, which is consistent with this direction.

---

## MetaTraits API Response Shape (raw observations)

Each API call returns a JSON array of flat observation records:

```json
[
  {
    "database": "BacDive-AI:SPIREv1",
    "feature": "acidophilic",
    "record_link": "https://spire.embl.de/genome/spire_mag_00405155",
    "tax_id": 2923425,
    "unit": "boolean",
    "value": "false"
  },
  {
    "database": "BacDive:2025-07-29",
    "feature": "cell shape",
    "record_link": "http://bacdive.dsmz.de/strain/3852",
    "tax_id": 1299,
    "unit": "factor",
    "value": "coccus-shaped"
  }
]
```

**Keys:** `database`, `feature`, `record_link`, `tax_id`, `unit`, `value`

Each record is one observation from one strain/genome in one source database. A single taxon can have thousands of records (E. coli taxon 562 returns 31,831 records from BacDive alone).

### Verified by direct API calls

We curled the API for taxon 1299 (463 records) and taxon 2923425 (957 records) and confirmed the 6-key structure. Anthea's downloaded file `2923425__all.json` has the same shape.

---

## MongoDB `metatraits` Database — Existing Collections

Our local MongoDB (`localhost:27017`, database `metatraits`) has 10 collections loaded from the MetaTraits **bulk JSON downloads** (from `https://metatraits.embl.de/traits`). These are a **different data product** from the API — they are pre-aggregated summaries, not raw per-observation records.

### Summary collections (by taxonomy)

| Collection | Docs | Taxonomy | Rank |
|-----------|------|----------|------|
| `ncbi_species_summary` | 54,654 | NCBI | species |
| `ncbi_genus_summary` | 4,906 | NCBI | genus |
| `ncbi_family_summary` | 1,022 | NCBI | family |
| `gtdb_species_summary` | 65,349 | GTDB | species |
| `gtdb_genus_summary` | 18,440 | GTDB | genus |
| `gtdb_family_summary` | 4,511 | GTDB | family |

**Document shape (summary):**

```json
{
  "tax_name": "Streptococcus sanguinis",
  "summaries": [
    {
      "name": "cell shape",
      "is_discrete": true,
      "num_observations": 29,
      "unique_databases": 4,
      "majority_label": "coccus-shaped: (100%)",
      "percentages": { "coccus-shaped": 100 }
    }
  ]
}
```

**Keys per summary:** `name`, `is_discrete`, `num_observations`, `unique_databases`, `majority_label`, `percentages`

These summaries correspond to the "trait cards" on the MetaTraits website. The `name` field here matches the `feature` field in the raw API data, but everything else differs.

### Per-genome collections

| Collection | Docs | Description |
|-----------|------|-------------|
| `genome_records` | 1 | Full per-genome record (GCA_000008565.1, 130 traits embedded) |
| `genome_traits` | 130 | Individual trait records for that genome (flattened from genome_records) |

**Document shape (genome_traits):**

```json
{
  "name": "electron acceptor: fumarate",
  "is_ai": true,
  "num_observations": 1,
  "unique_databases": 1,
  "majority_label": "false: (100%)",
  "percentages": { "false": 100 },
  "ontologies": ["CHEBI:17654", "CHEBI:29806"],
  "genome_accession": "GCA_000008565.1"
}
```

This is also a summary format. The existing demo script `metpo/scripts/demo_metatraits_mongo_to_kgx.py` reads from this collection.

### Taxonomy mapping collections

| Collection | Docs | Description |
|-----------|------|-------------|
| `ncbi2gtdb` | 92,711 | NCBI → GTDB taxon ID mapping |
| `gtdb2ncbi` | 92,823 | GTDB → NCBI taxon ID mapping |

---

## Comparison: Summary Data vs. Raw API Data

| Aspect | Summary (in MongoDB now) | Raw API (what Anthea downloads) |
|--------|--------------------------|--------------------------------|
| **Source** | Bulk JSON downloads from `metatraits.embl.de/traits` | Per-taxon API calls to `/api/v1/traits/taxonomy/{id}` |
| **Grain** | One entry per trait per taxon/genome | One record per observation per strain |
| **Provenance** | Aggregated across databases | Per-database, per-strain `record_link` |
| **Values** | `majority_label` + `percentages` | Raw `value` + `unit` |
| **Ontologies** | Embedded `ontologies` array | Not present |
| **Taxonomy key** | `tax_name` (string) | `tax_id` (integer) |
| **Volume** | Compact (e.g., 182 summaries for S. sanguinis) | Large (e.g., 463 records for S. sanguinis) |

### Verified side-by-side: taxon 1299 (Streptococcus sanguinis)

- **API** (`/api/v1/traits/taxonomy/1299`): 463 flat records, 51 unique features (BacDive only), keys: `database`, `feature`, `record_link`, `tax_id`, `unit`, `value`
- **MongoDB** (`ncbi_species_summary`, `tax_name: "Streptococcus sanguinis"`): 182 trait summaries across all databases, keys: `name`, `is_discrete`, `num_observations`, `unique_databases`, `majority_label`, `percentages`

### `api_taxonomy_traits` collection (raw API format)

We created this collection by curling the MetaTraits API directly for two taxon IDs. Each document wraps one API response:

```json
{
  "tax_id": 1299,
  "record_count": 463,
  "records": [
    {
      "database": "BacDive:2025-07-29",
      "feature": "cell shape",
      "record_link": "http://bacdive.dsmz.de/strain/3852",
      "tax_id": 1299,
      "unit": "factor",
      "value": "coccus-shaped"
    }
  ]
}
```

| tax_id | Records | Source |
|--------|---------|-------|
| 2876789 | 4 | API curl 2026-02-19 |
| 2859893 | 6 | API curl 2026-02-19 |
| 3123319 | 6 | API curl 2026-02-19 |
| 1299 | 463 | API curl 2026-02-19 |
| 2923425 | 957 | API curl 2026-02-19 |

All documents sourced from direct API calls. The three small taxa (2876789, 2859893, 3123319) were identified by scanning Anthea's Google Drive downloads via rclone for files in the 1 KB range, then fetched directly from the API.

### Anthea's download statistics (as of 2026-02-19)

Via `rclone lsl` of her Google Drive folder (`0AK9VwyLqCr3kUk9PVA`):

- **11,781 files**, 9.45 GB total over ~10 days (Feb 9–19)
- **Throughput:** ~48 files/hour average, bursty (3,315 files on Feb 19 alone)
- **File size distribution:**

| Range | Files | Notes |
|-------|------:|-------|
| <1 KB | 1,047 | Likely empty/minimal API responses |
| 1–10 KB | 1,647 | Small taxa (few traits) |
| 10–100 KB | 7,107 | Typical taxa (60% of files) |
| 100 KB–1 MB | 1,429 | Moderately annotated taxa |
| 1–10 MB | 441 | Heavily annotated taxa |
| >10 MB | 110 | Very large (includes one 1.69 GB file) |

- **Median file size:** 28 KB
- **Smallest non-zero:** 163 bytes
- Some older files have `.json.gz` extension but may not actually be compressed (per Anthea's Slack note)

---

## Relevant Scripts

| Script | Reads from | Purpose |
|--------|-----------|---------|
| `metpo/scripts/demo_metatraits_mongo_to_kgx.py` | `genome_traits` (summary format) | Demo KGX transform using per-genome summary data |
| `metpo/scripts/resolve_metatraits_in_sheets.py` | METPO Google Sheets | Deterministic mapper: MetaTraits card names → METPO predicates/objects via synonym tuples |
| `metpo/scripts/create_metatraits_mappings.py` | (on `metatraits` branch) | Creates SSSOM mapping file (deprecated for operational use per #340) |

---

*Updated: 2026-02-19*
