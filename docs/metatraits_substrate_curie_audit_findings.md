# MetaTraits Substrate CURIE Audit: Verified Findings

**Date:** 2026-02-19
**Audit script:** `metpo/scripts/audit_metatraits_substrate_curies.py`
**Audit output:** `data/mappings/metatraits_substrate_curie_audit.tsv` (1,157 rows)
**Audit summary:** `data/mappings/metatraits_substrate_curie_audit_report.md`

---

## Background

MetaTraits (metatraits.embl.de) publishes 2,860 trait cards. Of the 2,779 composed
cards (format "base_category: substrate"), many carry CHEBI CURIEs in their
`ontology_curies` field. These CURIEs have never been label-verified against the
authoritative CHEBI ontology. During work on KG-Microbe compound mappings, we
discovered that "Casamino acids" was mapped to CHEBI:78020 (heptacosanoate, a C27
fatty acid) via an LLM-hallucinated mapping upstream. This prompted a systematic
audit of all MetaTraits substrate CURIEs.

## Methodology

1. Parsed `metatraits_cards.tsv` (scraped from metatraits.embl.de by `fetch-metatraits`)
2. Extracted unique substrate labels from composed cards (split on ": ")
3. Collected all CHEBI-prefixed CURIEs from the `ontology_curies` field
4. Looked up authoritative labels for 679 unique CHEBI CURIEs via OAK (`sqlite:obo:chebi`)
5. Cross-referenced against 710 KG-Microbe compound mappings (`compound_mappings_strict_hydrate.tsv`)
6. Compared labels, flagged mismatches, and classified each substrate

### Verification

All CHEBI label claims were verified via two independent sources:
- OAK local SQLite (semsql/CHEBI)
- CHEBI website (ebi.ac.uk/chebi/searchId.do)

Both sources agree on all 8 disputed CURIEs. The `fetch-metatraits` scraper was
confirmed to be a pure pass-through (regex extraction from HTML, zero transformation
of CURIEs), so all CURIE errors originate upstream of our pipeline.

## Audit Status Summary

| Status | Count | Description |
|--------|-------|-------------|
| `verified` | 491 | MetaTraits CHEBI exists and OAK label matches substrate |
| `no_curie` | 434 | Neither MetaTraits nor KG-Microbe has a CHEBI mapping |
| `mismatch` | 231 | MetaTraits CHEBI exists but OAK label does NOT match substrate |
| `no_curie_kgm_available` | 1 | No MetaTraits CHEBI, but KG-Microbe has a mapping |

### Mismatch Breakdown

The 231 mismatches decompose into distinct failure modes:

| Failure mode | Count | Severity |
|-------------|-------|----------|
| "electron donor" category leak (CHEBI:15022) | 66 | High |
| "electron acceptor" category leak (CHEBI:17654) | 19 | High |
| "nutrient" category leak (CHEBI:33284) | 2 | High |
| No OAK label found | 2 | Medium |
| Genuine synonym/charge-state mismatch | ~142 | Low-Medium |

Of the ~142 "genuine" mismatches, most are benign synonym differences (e.g.,
"adipate" vs "adipate(2-)"), but some are wrong-compound errors (see below).

---

## Verified Examples by Category

### 1. `verified` -- Correct mapping confirmed

**(-)-quinic acid / CHEBI:17521**

| Field | Value |
|-------|-------|
| substrate_label | `(-)-quinic acid` |
| card_count | 7 |
| example_cards | `aerobic-catabolization-quinic-acid`, `assimilation-quinic-acid`, `carbon-source-quinic-acid` |
| metatraits_chebi_id | `CHEBI:17521` |
| chebi_label_from_oak | `(-)-quinic acid` |
| label_match | `exact` |

**Evidence:** All 7 cards in `metatraits_cards.tsv` include CHEBI:17521 in
`ontology_curies`. OAK returns label "(-)-quinic acid". CHEBI website confirms.
Exact string match.

**ammonium chloride / CHEBI:31206 (both sources agree)**

| Field | Value |
|-------|-------|
| substrate_label | `ammonium chloride` |
| card_count | 3 |
| metatraits_chebi_id | `CHEBI:31206` |
| chebi_label_from_oak | `ammonium chloride` |
| kgm_chebi_id | `CHEBI:31206` |
| kgm_chebi_label | `ammonium chloride` |
| kgm_matches_metatraits | `yes` |

MetaTraits and KG-Microbe independently assign the same CHEBI CURIE, and OAK
confirms the label. Maximum confidence.

---

### 2. `mismatch` -- Category leak (CHEBI:15022 = "electron donor")

**acetate (23 cards)**

| Field | Value |
|-------|-------|
| substrate_label | `acetate` |
| card_count | 23 |
| metatraits_chebi_id | `CHEBI:15022` |
| chebi_label_from_oak | `electron donor` |
| label_match | `mismatch` |
| audit_status | `mismatch` |

**Evidence:** In `metatraits_cards.tsv`, the card `electron-donor-acetate` (line 1127)
has `ontology_curies = CHEBI:15022; CHEBI:30089`. CHEBI:15022 is the base-category
concept "electron donor" (confirmed via OAK and CHEBI website). CHEBI:30089 is the
correct compound "acetate" (also confirmed). The audit reports CHEBI:15022 because
it sorts first alphabetically ("15022" < "30089").

**Important nuance:** The correct CURIE (CHEBI:30089) IS present in the data alongside
the role CURIE. The problem is that MetaTraits mixes role CURIEs and compound CURIEs
in the same `ontology_curies` field with no way to distinguish them. Naive consumers
that take the first or only CHEBI CURIE will get the role instead of the compound.

This pattern affects **66 substrates** where CHEBI:15022 appears (electron donor),
**19 substrates** where CHEBI:17654 appears (electron acceptor), and **2 substrates**
where CHEBI:33284 appears (nutrient).

**dimethyl sulfoxide (electron acceptor leak with KGM disagreement)**

| Field | Value |
|-------|-------|
| substrate_label | `dimethyl sulfoxide` |
| card_count | 3 |
| metatraits_chebi_id | `CHEBI:17654` |
| chebi_label_from_oak | `electron acceptor` |
| kgm_chebi_id | `CHEBI:28262` |
| kgm_chebi_label | `dimethyl sulfoxide` |
| kgm_matches_metatraits | `no` |

MetaTraits provides the role CURIE; KG-Microbe correctly provides the compound CURIE.

---

### 3. `mismatch` -- Wrong compound (data-entry errors in MetaTraits)

**acetic acid / CHEBI:16411 = "indole-3-acetic acid"**

| Field | Value |
|-------|-------|
| substrate_label | `acetic acid` |
| card_count | 11 |
| metatraits_chebi_id | `CHEBI:16411` |
| chebi_label_from_oak | `indole-3-acetic acid` |
| kgm_chebi_id | `CHEBI:15366` |
| kgm_chebi_label | `acetic acid` |
| kgm_matches_metatraits | `no` |

**Evidence:** All 11 "acetic acid" cards use CHEBI:16411. OAK and CHEBI website both
confirm CHEBI:16411 = "indole-3-acetic acid" (a plant hormone / auxin). KG-Microbe
correctly maps to CHEBI:15366 = "acetic acid". MetaTraits also has a separate card
`hydrolysis: 1h-indol-3-ylacetic acid` (line 1805) that uses CHEBI:16411 -- this is
where that CURIE actually belongs.

**Likely cause:** Copy-paste error or CURIE collision during MetaTraits' initial curation.

**D-gluconate / CHEBI:8391 = "Prenalterol" (digit-drop typo)**

| Field | Value |
|-------|-------|
| substrate_label | `D-gluconate` |
| card_count | 8 |
| metatraits_chebi_id | `CHEBI:8391` |
| chebi_label_from_oak | `Prenalterol` |
| Correct CURIE | `CHEBI:18391` (D-gluconate) |

**Evidence:** OAK and CHEBI website confirm CHEBI:8391 = Prenalterol (a beta-1
adrenergic agonist cardiac drug). OAK `basic_search('D-gluconate')` returns exactly
one hit: CHEBI:18391. The error is a dropped leading digit: **1**8391 -> 8391.

**inuline / CHEBI:2759 = "Anthranoyllycoctonine" (wrong compound class)**

| Field | Value |
|-------|-------|
| substrate_label | `inuline` |
| card_count | 1 (fermentation-inuline, line 1524) |
| metatraits_chebi_id | `CHEBI:2759` |
| chebi_label_from_oak | `Anthranoyllycoctonine` |
| Correct CURIE | `CHEBI:15443` (inulin) |

**Evidence:** OAK and CHEBI website confirm CHEBI:2759 = Anthranoyllycoctonine, a
toxic diterpene alkaloid from monkshood (Aconitum). Inulin is a fructan
polysaccharide prebiotic fiber -- a completely different compound class.

---

### 4. `mismatch` -- Both sources wrong (casamino acids)

**casamino acids: MetaTraits has CHEBI:15022, KG-Microbe has CHEBI:78020**

| Field | Value |
|-------|-------|
| substrate_label | `casamino acids` |
| card_count | 11 |
| metatraits_chebi_id | `CHEBI:15022` |
| chebi_label_from_oak | `electron donor` |
| kgm_chebi_id | `CHEBI:78020` |
| kgm_chebi_label | `heptacosanoate` |
| kgm_matches_metatraits | `no` |

**Evidence (MetaTraits):** 11 cards with "casamino acids" in name. Only
`electron-donor-casamino-acids` (line 1144) has a CHEBI: `CHEBI:15022` (the category
leak). No MetaTraits card has a CHEBI CURIE for "casamino acids" as a chemical substance.

**Evidence (KG-Microbe):** `compound_mappings_strict_hydrate.tsv` maps "Casamino acids"
to CHEBI:78020 (heptacosanoate, a C27 fatty acid) across 57 rows / 56 DSMZ media.
CHEBI website confirms CHEBI:78020 = heptacosanoate with formula C27H53O2.

**Upstream origin:** The error is hardcoded in `CultureBotAI/MicroMediaParam` at
`src/mapping/microbio_products.py` lines 73-78. The dictionary was created in commit
`f02b23c1` (2025-10-29 04:28 UTC) and deployed 17 minutes later via commit `690ef209`
(2025-10-29 04:45 UTC) in `apply_microbio_products.py`. Both commits were LLM
co-authored. The code comment says `confidence="medium"` and notes it's a
"Complex mixture, no single ChEBI ID perfectly represents it." KG-Microbe downloads
these mappings via `download.yaml` (lines 258-271). This is NOT a known issue in
either repository.

Casamino acids is an acid hydrolysate of casein (a complex amino acid mixture). Neither
"electron donor" nor "heptacosanoate" is remotely correct.

---

### 5. `no_curie_kgm_available` -- KG-Microbe has a valid mapping

**niacin (sole instance)**

| Field | Value |
|-------|-------|
| substrate_label | `niacin` |
| card_count | 1 (`produces-niacin`, line 2458) |
| metatraits_chebi_id | (none) |
| kgm_chebi_id | `CHEBI:15940` |
| kgm_chebi_label | `nicotinic acid` |

**Evidence:** `produces-niacin` has `ontology_curies = GO:0009058` only -- no CHEBI.
KG-Microbe maps `Niacin -> CHEBI:15940 -> nicotinic acid`. OAK and CHEBI website
confirm CHEBI:15940 = nicotinic acid. Niacin IS nicotinic acid (vitamin B3) -- the
KGM mapping is correct despite the label string mismatch.

This is the only substrate in this category because most unmapped MetaTraits substrates
are also absent from KG-Microbe's growth media compound list.

---

### 6. `no_curie` -- No mapping from any source

**Top unmapped substrates by card count:**

| Substrate | Cards | Notes |
|-----------|-------|-------|
| casein hydrolysate | 9 | Complex mixture, no single CHEBI |
| 2-oxogluconate | 8 | Should have a CHEBI mapping |
| 1 % sodium lactate | 7 | Concentration prefix complicates matching |
| 3-O-methyl alpha-D-glucopyranoside | 5 | Should have a CHEBI mapping |
| esculin ferric citrate | 5 | Reagent mixture |
| peptone | 5 | Complex mixture, no single CHEBI |
| (+)-D-galactose | 4 | Should be CHEBI:28061, stereochemistry prefix may have prevented match |

434 substrates have no CHEBI CURIE from any source. Many are complex mixtures
(peptone, tryptone, yeast extract, casein hydrolysate) that don't map cleanly to a
single CHEBI entity. Others (2-oxogluconate, (+)-D-galactose) should have
straightforward mappings and represent curation gaps.

---

## Error Attribution

### Errors in MetaTraits (metatraits.embl.de, EMBL)

The `fetch-metatraits` scraper is a pure pass-through: it extracts CURIEs verbatim
from `<a class="btn btn-cta">` button text on the MetaTraits HTML page with zero
transformation. All CURIE errors below originate in MetaTraits' own data.

| Substrate | Wrong CURIE | Wrong label | Likely correct CURIE | Error type |
|-----------|-------------|-------------|---------------------|------------|
| acetic acid | CHEBI:16411 | indole-3-acetic acid | CHEBI:15366 | Wrong compound |
| D-gluconate | CHEBI:8391 | Prenalterol | CHEBI:18391 | Digit-drop typo |
| inuline | CHEBI:2759 | Anthranoyllycoctonine | CHEBI:15443 | Wrong compound |
| 66 substrates | CHEBI:15022 | electron donor | (varies) | Role/compound conflation |
| 19 substrates | CHEBI:17654 | electron acceptor | (varies) | Role/compound conflation |
| 2 substrates | CHEBI:33284 | nutrient | (varies) | Role/compound conflation |

### Error in KG-Microbe / MicroMediaParam (CultureBotAI/MicroMediaParam)

| Substrate | Wrong CURIE | Wrong label | Source file | Commit |
|-----------|-------------|-------------|-------------|--------|
| casamino acids | CHEBI:78020 | heptacosanoate | `src/mapping/microbio_products.py:73-78` | `f02b23c1` / `690ef209` (2025-10-29) |
| casein hydrolysate | CHEBI:78020 | heptacosanoate | `src/mapping/microbio_products.py:209` | `f02b23c1` / `690ef209` (2025-10-29) |

KG-Microbe downloads these mappings via `download.yaml`. 57 rows across 56 DSMZ
media are affected. Not a known issue in either repo.

### Limitation in METPO (this repo)

The card parser (shared between `resolve_metatraits_in_sheets.py` and this audit
script) treats ALL CHEBI-prefixed CURIEs as substrate CURIEs. When a card like
`electron-donor-acetate` has both CHEBI:15022 (role) and CHEBI:30089 (compound),
the parser cannot distinguish them. The audit's "take first sorted CHEBI" logic
can report the role CURIE instead of the compound CURIE.

---

## Recommended Actions

1. **File issue on MetaTraits/EMBL** for the three wrong-compound CURIEs (acetic acid,
   D-gluconate, inuline) and the role/compound conflation pattern
2. **File issue on CultureBotAI/MicroMediaParam** for the casamino acids / CHEBI:78020
   hardcoded mapping, with downstream issue on Knowledge-Graph-Hub/kg-microbe
3. **Improve METPO parser** to filter known role CURIEs (CHEBI:15022, CHEBI:17654,
   CHEBI:33284) or use URL patterns to distinguish OLS role links from direct CHEBI
   compound links
4. **Re-scrape MetaTraits** (`uv run fetch-metatraits -o /tmp/fresh_cards.tsv`) to
   confirm errors are still present before filing complaints
5. **Review the ~142 genuine synonym mismatches** against CHEBI synonym lists to
   determine how many are truly benign vs. additional wrong-compound errors

## Related Files

- [`data/mappings/metatraits_substrate_curie_audit.tsv`](../data/mappings/metatraits_substrate_curie_audit.tsv) -- full audit TSV
- [`data/mappings/metatraits_substrate_curie_audit_report.md`](../data/mappings/metatraits_substrate_curie_audit_report.md) -- auto-generated summary
- [`docs/casamino_acids_curie_mapping_case_study.md`](casamino_acids_curie_mapping_case_study.md) -- CHEBI:78020 error case study
- [`docs/linkml_embedding_and_validation_tools.md`](linkml_embedding_and_validation_tools.md) -- OAK/linkml-store tooling research
- [`data/mappings/metatraits_in_sheet_resolution.tsv`](../data/mappings/metatraits_in_sheet_resolution.tsv) -- in-sheet resolution table
- [`data/mappings/metatraits_external_curie_coverage.tsv`](../data/mappings/metatraits_external_curie_coverage.tsv) -- external CURIE coverage
