# METPO ID Ranges: Research and Provenance

**Date:** 2026-02-19
**Purpose:** Document the research behind METPO ID range analysis, including all sources consulted. Supplements `metpo_id_allocation_reference.md` (the definitive allocation record) with historical context and provenance.

---

## Sources Consulted

### Primary Sources (in this repo)

| Source | Path | What It Tells Us |
|--------|------|-----------------|
| **ID ranges OWL** | `src/ontology/metpo-idranges.owl` | Formal range allocations: Range 1 (0-999999) for ONTOLOGY-CREATOR, Range 2 (1000000-1999999) for ADDITIONAL EDITOR |
| **Current class sheet** | `src/templates/metpo_sheet.tsv` | 257 classes, METPO:1000059 to METPO:1004005 |
| **Current properties sheet** | `src/templates/metpo-properties.tsv` | 109 properties, METPO:2000001 to METPO:2000606 |
| **BioPortal entity extracts** | `metadata/ontology/historical_submissions/entity_extracts/metpo_submission_{2-10}_all_entities.tsv` | IDs used in each of 9 historical BioPortal submissions |
| **Historical OWL files** | `external/metpo_historical/metpo_submission_{2-10}.owl` | Actual OWL files for each submission |
| **Stability report** | `reports/METPO_Stability_Analysis_Comprehensive_Report.md` | Comprehensive analysis from Sep 2025 |
| **OLS submission metadata** | `metadata/ontology/ols-submission.csv` | OLS submission config (creator field, URIs) |
| **Custom Makefile** | `src/ontology/metpo.Makefile` | Google Sheets source URLs and gid values |
| **Existing allocation doc** | `docs/metpo_id_allocation_reference.md` | Prior ID allocation reference (dated 2026-02-13) |

### External Sources (Google Drive, accessed via MCP)

| Source | Google Drive ID | What It Tells Us |
|--------|----------------|-----------------|
| **METPO ancient history** (spreadsheet) | `1Oc-nfEkwkwIKdT2wMQNzK4iDiDWhC55ZIhsuJPZhves` | Retired vocabulary of ~280 terms using IDs 1000001-1000327, with linguistic role annotations (adjective, noun_plural, verb) |
| **metpo_sheet.tsv** (Google Drive copy) | `19T2jBfEuL19EkZijPSgYNrj5WBN1pcFD` | Live Google Sheets export; compared with git version |
| **Live Google Sheet** (canonical) | Sheet `1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU` | The upstream source that `metpo.Makefile` curls from |

### CLI Queries (run 2026-02-19)

```bash
# Current class ID range
cut -f1 src/templates/metpo_sheet.tsv | grep '^METPO:' | sed 's/METPO://' | sort -n
# Result: min=1000059, max=1004005, count=257

# Current property ID range
cut -f1 src/templates/metpo-properties.tsv | grep '^METPO:' | sed 's/METPO://' | sort -n
# Result: min=2000001, max=2000606, count=109

# ID gap analysis
cut -f1 src/templates/metpo_sheet.tsv | grep '^METPO:' | sed 's/METPO://' | sort -n | \
  awk '{a[NR]=$1} END{for(i=1;i<NR;i++){gap=a[i+1]-a[i]; if(gap>10) print a[i]" -> "a[i+1]" (gap="gap")"}}'

# Historical IRI patterns
grep 'w3id.org/metpo' metadata/ontology/historical_submissions/entity_extracts/metpo_submission_2_all_entities.tsv | head -3
# Result: <https://w3id.org/metpo/000001> "Temperature", etc.

grep 'w3id.org/metpo' metadata/ontology/historical_submissions/entity_extracts/metpo_submission_6_all_entities.tsv | head -3
# Result: <https://w3id.org/metpo/1000001> "acid-fast", etc.
```

---

## Three Eras of METPO Numbering

### Era 1: Original 6-digit (Submissions 2-3, March 2025)

- **Format**: `https://w3id.org/metpo/000001` to `000274`
- **Count**: 320 entities
- **Evidence**: `metadata/ontology/historical_submissions/entity_extracts/metpo_submission_2_all_entities.tsv`
- **Sample**: `000001` = "Temperature", `000002` = "Salinity", `000003` = "pH"
- **Status**: All IRIs **abandoned** — no migration path provided

### Era 2: Transition 7-digit (Submissions 4-5, March 2025)

- **Format**: `https://w3id.org/metpo/0000001` to `0000351`
- **Count**: ~350 METPO entities + 1,487 imported external terms
- **Evidence**: `metpo_submission_4_all_entities.tsv`, `metpo_submission_5_all_entities.tsv`
- **Notable**: Massive external ontology import (GO: 617, CHEBI: 221, RO: 134, PATO: 115, MicrO: 112 terms)
- **Status**: All IRIs **abandoned** — the 7-digit format was short-lived

### Era 3: Current 1000xxx/2000xxx (Submissions 6-10, April 2025+)

- **Format**: Classes in `1000xxx`, Properties in `2000xxx`
- **Evolution within Era 3**:

| Submission | Date | METPO Entities | Notes |
|------------|------|---------------|-------|
| 6 | 2025-04-25 | 860 | Initial Era 3, IDs 1000001-1000327 for literature-mining terms |
| 7 | 2025-06-25 | 810 | Minor cleanup |
| 8 | 2025-08-18 | 822 | Stable period |
| 9 | 2025-09-22 | 458 | **Major reduction** — retired most literature-mining terms |
| 10 | 2025-09-23 | 430 | Current state at last BioPortal submission |

**Current active (post-cleanup)**: 257 classes + 109 properties = 366 entities in robot templates. BioPortal submission 10 had 430 (includes OWL-generated entities beyond templates).

---

## The "Ancient History" Sheet: Retired IDs 1000001-1000327

**Source**: Google Drive spreadsheet `1Oc-nfEkwkwIKdT2wMQNzK4iDiDWhC55ZIhsuJPZhves` ("METPO ancient history")

This sheet documents ~280 terms that used IDs `METPO:1000001` through `METPO:1000327`. These were literature-mining-derived terms extracted from IJSEM papers using OntoGPT, given linguistic role annotations:

| ID | Former Label | Linguistic Roles |
|----|-------------|-----------------|
| 1000001 | acid-fast | adjective, noun_plural |
| 1000002 | acidophilic | adjective, noun_plural |
| 1000008 | aerobic | adjective, adverb, noun_plural |
| 1000016 | anaerobic | adjective, adverb, noun_plural |
| 1000060 | chemoautotrophic | adjective, adverb, noun_plural |
| 1000086 | denitrifying | adjective, verb |
| 1000127 | GC-rich/GC-poor | adjective |
| 1000143 | Gram-negative | adjective, noun_plural |
| 1000184 | methanogenic | adjective, verb |
| 1000232 | pH deltas | noun_plural |
| 1000259 | psychrophilic | adjective, noun_plural |
| 1000286 | sporulating | adjective, verb |
| 1000308 | thermophilic | adjective, noun_plural |
| 1000327 | zygospore-producing | adjective, noun_plural |

**Key finding**: The retirement of these terms during the submission 8 → 9 cleanup (Sep 2025) freed up many IDs. However, **these IDs should never be reused** because:
1. They existed in BioPortal submissions 6-8 with specific meanings
2. External systems may have cached or referenced them
3. The OBO Foundry principle of IRI persistence prohibits reassignment

### Which old IDs survived the cleanup?

A few old IDs were retained with **new** definitions in the current ontology:

| ID | Old Label (ancient) | Current Label (metpo_sheet.tsv) | Notes |
|----|---------------------|--------------------------------|-------|
| 1000059 | — | phenotype | Reused starting at sub 10 |
| 1000060 | chemoautotrophic | metabolism | **Label changed** |
| 1000127 | GC-rich/GC-poor | GC content | Similar concept, refined |
| 1000186 | — | material entity | New at sub 10 |
| 1000232 | pH deltas | pH delta | Same concept |
| 1000303 | — | temperature delta | Same concept |
| 1000304 | optimally-growing | temperature optimum | Related concept |
| 1000306 | temperature ranges | temperature range | Same concept |

Most IDs below 1000429 that appear in both the ancient sheet and current sheet retained roughly the same domain, even if labels evolved.

---

## Current ID Layout in Detail

### Classes (metpo_sheet.tsv)

```
1000059-1000060    Root concepts (phenotype, metabolism)
1000127            GC content
1000186-1000188    Top-level categories (material entity, quality)
1000232-1000335    Numerical phenotype parent classes
                   (pH/temp/NaCl optimum/range/delta)
1000429-1000487    Binned numerical categories (~60 classes)
                   GC bins, NaCl bins, pH bins, temp bins
1000525-1000536    Categorical phenotype parent classes
                   (microbe, chemical entity, phenotype subtypes)
1000601-1000631    Core categorical phenotypes
                   oxygen preference (12), halophily (8), trophic root
1000632-1000665    Trophic type subclasses (~25)
1000666-1000706    Cell shape (31) + gram stain (3) + motility (6)
1000720-1000731    Edge cases (fac. psychrophilic, nutrient adaptation)
1000800-1000806    Metabolic processes (7)
                   respiration, phosphorylation, electron transfer, etc.
1000844-1000846    Methanogenesis, acetogenesis, homoacetogenesis
1000870-1000890    Sporulation (3) + cell length bins (4) + cell width bins (4)
1001000-1001023    Observation classes (~20)
1001101-1001106    Biosafety levels (6)
1002003-1002006    Special metabolisms (cable bacteria, fermentation, syntrophy)
1003000-1003031    pH growth preference (10) + pigmentation (12)
1004000-1004005    Pathogenicity classes (5)
```

### Properties (metpo-properties.tsv)

```
2000001-2000051    Chemical interaction properties
                   (positive + negative pairs: ferments/does_not_ferment, etc.)
2000052-2000063    Observation object/data properties
2000071            has value (generic numeric data property)
2000101-2000103    has quality, has phenotype, capable of
2000200-2000232    Chemical conversion properties
                   (produces, transports, imports, exports, etc.)
2000239            has pH observation
2000301-2000303    Enzyme activity properties
2000501-2000518    Growth condition observation properties
2000601-2000606    Nitrogen cycle predicates (newest, from this branch)
```

**Note**: The existing `metpo_id_allocation_reference.md` (dated 2026-02-13) recorded highest property as METPO:2000518. The current `metpo-properties.tsv` on this branch goes up to **METPO:2000606** (nitrogen cycle predicates added recently).

---

## Formal ID Range Governance

### metpo-idranges.owl

```
Range 1: 0 to 999,999       → ONTOLOGY-CREATOR
Range 2: 1,000,000 to 1,999,999 → ADDITIONAL EDITOR
```

### Observations

1. **All current classes** (1000059-1004005) fall in Range 2 ("ADDITIONAL EDITOR")
2. **All current properties** (2000001-2000606) fall **outside both declared ranges** (2000000+)
3. **Range 1 IDs** (000001-000274 from Era 1) are burned but formally "ONTOLOGY-CREATOR"
4. **No Range 3** is declared for the 2000xxx property space

**Recommendation**: Add a Range 3 declaration for properties:
```
Datatype: idrange:3
    Annotations: allocatedto: "PROPERTIES"
    EquivalentTo: xsd:integer[>= 2000000 , <= 2999999]
```

---

## Safe Ranges for New Terms

### For new classes

The existing `metpo_id_allocation_reference.md` recommends starting new classes at **METPO:1005001+**. This remains valid:

| Range | Purpose | From |
|-------|---------|------|
| 1005001-1005010 | Nitrogen cycle process classes | allocation reference |
| 1005011-1005020 | Biochemical test phenotypes | allocation reference |
| 1005021-1005030 | Missing phenotypes (capnophilic, hemolytic) | allocation reference |
| 1005031-1005050 | Flagellum arrangement types | allocation reference |
| 1005051-1005999 | Reserved for future | allocation reference |

### For new properties

| Range | Purpose | From |
|-------|---------|------|
| 2000601-2000606 | Nitrogen cycle predicates (already allocated on this branch) | current properties sheet |
| 2000607-2000650 | Reserved for future predicates | allocation reference |
| 2000701-2000750 | Data properties | allocation reference |

### IDs to NEVER reuse

| ID Range | Reason | Evidence |
|----------|--------|---------|
| 000001-000274 | Era 1 (6-digit) | submission 2 entity extract |
| 0000001-0000351 | Era 2 (7-digit) | submission 4-5 entity extracts |
| 1000001-1000327 | Retired literature-mining terms | "METPO ancient history" Google Sheet |
| 1000001-1004005 | Any ID ever in metpo_sheet.tsv | current + historical sheets |
| 2000001-2000606 | Any ID ever in metpo-properties.tsv | current sheet |
| 9999999 | Test placeholder | submission 3-5 entity extracts |

### Verification command

```bash
# Check if an ID was ever used across all known sources
ID=1005001
for f in src/templates/*.tsv metadata/ontology/historical_submissions/entity_extracts/*.tsv; do
  grep -l "$ID" "$f" 2>/dev/null
done
```

---

## Google Sheets ↔ Git Synchronization

### How templates flow

```
Google Sheet (1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU)
  ↓ curl (via metpo.Makefile squeaky-clean + make targets)
src/templates/metpo_sheet.tsv, metpo-properties.tsv
  ↓ ROBOT template (via metpo.Makefile component target)
src/ontology/components/metpo_sheet.owl
  ↓ ODK build (sh run.sh make prepare_release)
metpo.owl, metpo.obo, metpo.json
  ↓ git commit + push + merge + tag
Tagged release on GitHub
  ↓ (consumed by downstream)
Knowledge-Graph-Hub/kg-microbe download.yaml
```

### Sheet gid values (from metpo.Makefile)

| gid | Sheet Name | Status |
|-----|-----------|--------|
| 121955004 | Cleaned definition sources (classes) | **Active** — used for metpo_sheet.tsv |
| 2094089867 | Properties | **Active** — used for metpo-properties.tsv |
| 907926993 | Synonyms | **Disabled** (commented out) |
| 1427185859 | Comprehensive classes | **Disabled** (commented out — "too comprehensive") |
| 355012485 | Minimal set of classes | **Superseded** by gid=121955004 |

### Sync status as of 2026-02-19

The Google Drive TSV (`19T2jBfEuL19EkZijPSgYNrj5WBN1pcFD`) was read via MCP and visually matches the git version of `src/templates/metpo_sheet.tsv`. Both contain the same 257 classes with identical structure.

**Important**: Any changes to robot template TSVs in git MUST be manually propagated back to the Google Sheet. The flow is one-directional (Sheets → git), so git-only changes will be overwritten on next `squeaky-clean` + rebuild.

---

*Last updated: 2026-02-19. All CLI queries, Google Drive reads, and BioPortal entity extract analyses performed on this date.*
