# METPO ID Allocation Reference

**Date:** 2026-02-13
**Purpose:** Prevent ID reuse when adding new terms. This is the definitive record of
all METPO IDs ever allocated, including historical BioPortal submissions.

---

## ID Range Policy (metpo-idranges.owl)

```
Range 1: 0 to 999,999       (ONTOLOGY-CREATOR)
Range 2: 1,000,000 to 1,999,999  (ADDITIONAL EDITOR)
```

In practice: **1xxxxxx = classes**, **2xxxxxx = properties**.

---

## Sources of Historical ID Allocations

1. `src/templates/metpo_sheet.tsv` -- current class definitions (257 unique IDs)
2. `src/templates/metpo-properties.tsv` -- current property definitions (97+ unique IDs)
3. `metadata/ontology/historical_submissions/entity_extracts/metpo_submission_*_all_entities.tsv` -- 9 historical BioPortal submission extracts
4. `external/metpo_historical/metpo_submission_*.owl` -- 9 historical OWL files

**Total unique IDs ever allocated: 1,228**

---

## Highest Allocated IDs

| Source | Highest Class ID | Highest Property ID |
|--------|-----------------|-------------------|
| metpo_sheet.tsv (current) | METPO:1004005 | METPO:2000071 (referenced) |
| metpo-properties.tsv (current) | -- | METPO:2000518 |
| submission 10 (2025-09-23) | -- | METPO:2000103 |
| submissions 3-5 | METPO:9999999 (TEST -- ignore) | -- |

**Absolute highest real IDs: METPO:1004005 (class), METPO:2000518 (property)**

---

## Class ID Blocks (METPO:1xxxxxx)

| Block | IDs | Topic | Count |
|-------|-----|-------|-------|
| 1000059-1000060 | 1000059, 1000060 | Root: phenotype, metabolism | 2 |
| 1000127 | 1000127 | GC content | 1 |
| 1000155 | 1000155 | Hemolysis (historical only, NOT in current release) | 1 |
| 1000186-1000188 | 1000186-1000188 | Upper-level: material entity, quality | 3 |
| 1000232 | 1000232 | pH delta | 1 |
| 1000303-1000335 | ~15 IDs | Numeric phenotype parents (optimum/range/delta for temp/pH/NaCl) | ~15 |
| 1000429-1000487 | ~40 IDs | Numeric bin classes (GC 4, temp opt 7, temp range 7, pH opt 4, pH range 6, NaCl opt 4, NaCl range 4, pH delta 6, NaCl delta 4, temp delta 5) | ~51 |
| 1000525-1000537 | ~10 IDs | Entity classes (microbe, chemical entity, enzyme, observation) + parents | ~10 |
| 1000601-1000631 | ~20 IDs | Oxygen preference (12) + biological process + trophic root | ~20 |
| 1000632-1000665 | ~25 IDs | Trophic type subclasses | ~25 |
| 1000666-1000706 | ~35 IDs | Cell shape (31) + motility (6) | ~37 |
| 1000720-1000731 | ~8 IDs | Psychro variants, hyperthermophilic, nutrient adaptation | ~8 |
| 1000800-1000806 | 7 IDs | Metabolic processes: respiration, phosphorylation, electron transfer | 7 |
| 1000844-1000846 | 3 IDs | Methanogenesis, acetogenesis, homoacetogenesis | 3 |
| 1000870-1000890 | ~15 IDs | Sporulation (3) + cell length bins (4) + cell width bins (4) | ~11 |
| 1001000-1001023 | ~20 IDs | Observation classes (temp/pH/NaCl/O2 observations) | ~20 |
| 1001101-1001106 | 6 IDs | Biosafety levels 1-5 + parent | 6 |
| 1002003-1002006 | 4 IDs | Cable bacteria metabolism, fermentation, syntrophy | 4 |
| 1003000-1003031 | ~20 IDs | pH preference (10) + pigmentation (12) | ~22 |
| 1004000-1004005 | ~5 IDs | Pathogenicity (4) + growth medium (1) | 5 |

### Gaps in Class IDs

| Gap Range | Size | Notes |
|-----------|------|-------|
| 1000061-1000126 | 66 | Between root classes and GC content |
| 1000128-1000154 | 27 | |
| 1000156-1000185 | 30 | |
| 1000189-1000231 | 43 | |
| 1000336-1000428 | 93 | |
| 1000488-1000524 | 37 | |
| 1000538-1000600 | 63 | |
| 1000707-1000719 | 13 | Between motility and psychro variants |
| 1000732-1000799 | 68 | Between nutrient adaptation and metabolic processes |
| 1000807-1000843 | 37 | |
| 1000847-1000869 | 23 | |
| 1000891-1000999 | 109 | |
| 1001024-1001100 | 77 | After observation classes |
| 1001107-1001999 | 893 | Large gap |
| 1002007-1002999 | 993 | Large gap |
| 1003032-1003999 | 968 | Large gap |
| **1004006-1999999** | **995,994** | **Primary expansion space** |

---

## Property ID Blocks (METPO:2xxxxxx)

| Block | IDs | Topic | Count |
|-------|-----|-------|-------|
| 2000001-2000051 | ~51 IDs | Chemical interaction properties (positive + negative pairs for 20 bases + parent + aerobic/anaerobic variants) | ~51 |
| 2000052-2000063 | ~10 IDs | Observation object properties + data properties (blank-node pattern, deprecated for KGX) | ~10 |
| 2000071 | 1 ID | has value (generic numeric data property) | 1 |
| 2000101-2000103 | 3 IDs | has quality, has phenotype, capable of | 3 |
| 2000200-2000232 | ~20 IDs | Chemical conversion: produces, transports, imports, exports, accumulates, sequesters, compartmentalizes, disproportionates + negatives | ~20 |
| 2000239 | 1 ID | has pH observation | 1 |
| 2000301-2000303 | 3 IDs | Enzyme activity: analyzed, shows activity, does not show activity | 3 |
| 2000501-2000518 | ~15 IDs | pH/NaCl/O2 observation properties + grows in / does not grow in | ~15 |

### Gaps in Property IDs

| Gap Range | Size | Notes |
|-----------|------|-------|
| 2000064-2000070 | 7 | |
| 2000072-2000100 | 29 | |
| 2000104-2000199 | 96 | |
| 2000233-2000238 | 6 | |
| 2000240-2000300 | 61 | |
| 2000304-2000500 | 197 | |
| **2000519-2000600** | **82** | Available |
| **2000601+** | **unlimited** | Primary expansion space for properties |

---

## Safe Ranges for New Term Allocation

### New Classes

| Proposed Range | Purpose | Count needed |
|----------------|---------|-------------|
| METPO:1005001-1005010 | Nitrogen cycle process classes | ~1 (nitrification) |
| METPO:1005011-1005020 | Biochemical test phenotypes (indole/MR/VP +/-) | ~6 |
| METPO:1005021-1005030 | Missing phenotypes (capnophilic, hemolytic) | ~3 |
| METPO:1005031-1005050 | Flagellum arrangement types | ~7 |
| METPO:1005051-1005999 | Reserved for future | 949 |

### New Object Properties

| Proposed Range | Purpose | Count needed |
|----------------|---------|-------------|
| METPO:2000601-2000606 | Nitrogen cycle predicates (3 positive + 3 negative) | 6 |
| METPO:2000607-2000650 | Reserved for future predicates | 44 |

### New Data Properties

| Proposed Range | Purpose | Count needed |
|----------------|---------|-------------|
| METPO:2000701-2000709 | Temperature/pH/salinity values (growth/min/max x 3) | 9 |
| METPO:2000711-2000716 | Genome metrics (size, est size, genes, est genes, GC%, coding density) | 6 |
| METPO:2000721-2000722 | Cell dimensions (length, width) | 2 |
| METPO:2000723-2000750 | Reserved for future data properties | 28 |

---

## IDs to NEVER Reuse

- Any ID in `metpo_sheet.tsv` or `metpo-properties.tsv`
- Any ID in `metadata/ontology/historical_submissions/entity_extracts/*.tsv`
- METPO:9999999 (test placeholder from submissions 3-5)
- IDs with leading zeros from submission 2 (METPO:000001-000274)
- Any ID <= METPO:1004005 (classes) or <= METPO:2000518 (properties)

When in doubt, run:
```bash
# Check if an ID was ever used
for f in src/templates/*.tsv metadata/ontology/historical_submissions/entity_extracts/*.tsv; do
  grep -l "1005001" "$f"
done
```
