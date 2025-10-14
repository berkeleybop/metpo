# BactoTraits ↔ METPO Reconciliation Action Plan

**Generated**: 2025-10-13
**Based on**: reports/bactotraits-metpo-set-diff.yaml

## Executive Summary

**Total Issues**: 61 items requiring action
- **14 METPO synonym errors** (high priority - incorrect forms)
- **38 missing BactoTraits trait fields** (medium priority - legitimate fields not in METPO)
- **9 documentation tasks** (ongoing)

**Coverage Impact**:
- Current: 50/105 exact matches (47.6%)
- After fixing errors: 64/105 matches (61.0%)
- After adding high-value missing: 77/105 matches (73.3%)

---

## PRIORITY 1: Fix METPO Orphaned Synonyms (14 items)

These synonyms exist in METPO but don't match actual BactoTraits data. They need correction.

### P1.1: Fix Comparison Operators (7 fields)

**Issue**: METPO uses `<` but BactoTraits uses `<=`

**File**: `src/ontology/metpo.owl`

**Find and replace**:

| Current METPO Synonym | Correct BactoTraits Form | METPO ID | Search Pattern |
|----------------------|--------------------------|----------|----------------|
| `GC_<42.65` | `GC_<=42.65` | METPO:1000429 | `<oboInOwl:hasRelatedSynonym.*GC_&lt;42\.65` |
| `NaO_<1` | `NaO_<=1` | METPO:1000469 | `<oboInOwl:hasRelatedSynonym.*NaO_&lt;1` |
| `NaR_<1` | `NaR_<=1` | METPO:1000465 | `<oboInOwl:hasRelatedSynonym.*NaR_&lt;1` |
| `Nad_<1` | `Nad_<=1` | METPO:1000479 | `<oboInOwl:hasRelatedSynonym.*Nad_&lt;1` |
| `TO_<10` | `TO_<=10` | METPO:1000441 | `<oboInOwl:hasRelatedSynonym.*TO_&lt;10` |
| `TR_<10` | `TR_<=10` | METPO:1000448 | `<oboInOwl:hasRelatedSynonym.*TR_&lt;10` |
| `pHd_<1` | `pHd_<=1` | METPO:1000473 | `<oboInOwl:hasRelatedSynonym.*pHd_&lt;1` |

**XML encoding note**: In OWL files, `<` is encoded as `&lt;` and `<=` should be `&lt;=`

**Verification command**:
```bash
uv run python src/scripts/bactotraits_metpo_set_difference.py --format yaml --output reports/bactotraits-metpo-set-diff.yaml
```

### P1.2: Fix Shape Field Case (6 fields)

**Issue**: METPO uses lowercase `s_` but BactoTraits uses uppercase `S_` (some with leading space)

**File**: `src/ontology/metpo.owl`

| Current METPO Synonym | Correct BactoTraits Form | METPO ID | Notes |
|----------------------|--------------------------|----------|-------|
| `s_curved_spiral` | `S_curved_spiral` | METPO:1000675 | Also appears as ` S_curved_spiral` (with space) |
| `s_filament` | `S_filament` | METPO:1000674 | Also appears as ` S_filament` |
| `s_ovoid` | `S_ovoid` | METPO:1000677 | Also appears as ` S_ovoid` |
| `s_rod` | `S_rod` | METPO:1000681 | Also appears as ` S_rod` |
| `s_sphere` | `S_sphere` | METPO:1000683 | Also appears as ` S_sphere` |
| `s_star_dumbbell_pleomorphic` | `S_star_dumbbell_pleomorphic` | METPO:1000685 | No leading space variant |

**Decision needed**: Should we add both forms (`S_rod` AND ` S_rod`) as synonyms, or pick one canonical form?

**Recommendation**: Add both forms since both appear in actual BactoTraits data. Leading whitespace is preserved in provider and kg-microbe versions.

### P1.3: Fix Whitespace Issues (1 field)

**Issue**: METPO has space after hyphen

**File**: `src/ontology/metpo.owl`

| Current METPO Synonym | Correct BactoTraits Form | METPO ID |
|----------------------|--------------------------|----------|
| `non- motile` | `non-motile` | METPO:1000702 |

**Note**: MongoDB sanitized form is `non_motile` but kg-microbe preserves the hyphen.

---

## PRIORITY 2: Add Missing BactoTraits Fields to METPO (38 trait fields)

These legitimate BactoTraits trait fields have no METPO representation.

### P2.1: High-Value Missing Fields (13 fields with 2-20 unique values)

These fields have small controlled vocabularies and are good ontology candidates.

#### P2.1.1: Pigment Color Fields (9 fields)

**Data quality**: 2-3 unique values each (mostly binary: 0, 1, sometimes 0.5 for mixed)

| Field | Unique Values | Record Count | Non-empty |
|-------|--------------|--------------|-----------|
| `Pigment_yellow` | 3 | 101 | 39 (24 = 1, 14 = 0.5, 1 = 0.333) |
| `Pigment_pink` | 3 | 101 | 13 (5 = 1, 7 = 0.5, 1 = 0.333) |
| `Pigment_white` | 3 | 101 | 12 (2 = 1, 9 = 0.5, 1 = 0.334) |
| `Pigment_black` | 3 | 101 | 8 (2 = 1, 4 = 0.5, 2 = 0.333) |
| `Pigment_green` | 3 | 101 | 3 (1 = 1, 1 = 0.5, 1 = 0.334) |
| `Pigment_orange` | 2 | 101 | 18 (10 = 1, 8 = 0.5) |
| `Pigment_brown` | 2 | 101 | 19 (9 = 1, 10 = 0.5) |
| `Pigment_cream` | 2 | 101 | 11 (6 = 1, 5 = 0.5) |
| `Pigment_red` | 2 | 101 | 10 (4 = 1, 6 = 0.5) |

**Proposed METPO structure**:
- Parent class: `METPO:1000XXX` "pigment color"
- Children: 9 color classes (black, brown, carotenoid, cream, green, orange, pink, red, white, yellow)
- Add BactoTraits synonyms: `Pigment_black`, `Pigment_brown`, etc.
- Data type: Categorical
- Values: Binary or fractional (for mixed/uncertain observations)

#### P2.1.2: Temperature Range Boundary Fields (2 fields)

| Field | Unique Values | Description | MongoDB Form |
|-------|--------------|-------------|--------------|
| `TR_<=10` | 7 | Temperature range ≤10°C | `TR_lte_10` |
| `TR_>40` | 7 | Temperature range >40°C | `TR_gt_40` |

**Proposed METPO structure**:
- Add to existing temperature range hierarchy (METPO:1000449-1000454)
- `METPO:1000447` "temperature range very low" → add synonym `TR_<=10`
- `METPO:1000454` "temperature range high" → add synonym `TR_>40`

#### P2.1.3: NaCl Range Boundary Fields (2 fields)

| Field | Unique Values | Description | MongoDB Form |
|-------|--------------|-------------|--------------|
| `NaR_<=1` | 5 | NaCl range ≤1% | `NaR_lte_1` |
| `NaR_>8` | 5 | NaCl range >8% | `NaR_gt_8` |

**Proposed METPO structure**:
- Add to existing NaCl range hierarchy (METPO:1000466-1000472)
- Create `METPO:1000XXX` "NaCl optimum very low" → add synonym `NaR_<=1`
- Create `METPO:1000XXX` "NaCl optimum very high" → add synonym `NaR_>8`

### P2.2: Low-Value Missing Fields (25 fields with 1 unique value)

These are mostly binary traits (0/1 only). Less urgent but still legitimate.

#### P2.2.1: GC Content Boundary Fields (2 fields)

| Field | Description | MongoDB Form |
|-------|-------------|--------------|
| `GC_<=42.65` | GC content ≤42.65% | `GC_lte_42_65` |
| `GC_>66.3` | GC content >66.3% | `GC_gt_66_3` |

**Proposed action**: Add to existing GC hierarchy (METPO:1000429-1000432)

#### P2.2.2: Cell Length Bins (4 fields)

| Field | Description | MongoDB Form |
|-------|-------------|--------------|
| `L_<=1.3` | Length ≤1.3 µm | `L_lte_1_3` |
| ` L_1.3_2` | Length 1.3-2 µm | `L_1_3_2` |
| `L_2_3` | Length 2-3 µm | `L_2_3` |
| `L_>3` | Length >3 µm | `L_gt_3` |

**Proposed action**: Create cell length hierarchy under morphology

#### P2.2.3: Cell Width Bins (4 fields)

| Field | Description | MongoDB Form |
|-------|-------------|--------------|
| `W_<=0.5` | Width ≤0.5 µm | `W_lte_0_5` |
| ` W_0.5_0.65` | Width 0.5-0.65 µm | `W_0_5_0_65` |
| `W_0.65_0.9` | Width 0.65-0.9 µm | `W_0_65_0_9` |
| `W_>0.9` | Width >0.9 µm | `W_gt_0_9` |

**Proposed action**: Create cell width hierarchy under morphology

#### P2.2.4: NaCl Boundary Fields (4 fields)

| Field | Description | MongoDB Form |
|-------|-------------|--------------|
| `NaO_<=1` | NaCl optimum ≤1% | `NaO_lte_1` |
| `NaO_>8` | NaCl optimum >8% | `NaO_gt_8` |
| `Nad_<=1` | NaCl delta ≤1% | `Nad_lte_1` |
| `Nad_>8` | NaCl delta >8% | `Nad_gt_8` |

**Proposed action**: Add to existing NaCl hierarchies

#### P2.2.5: Temperature Boundary Fields (3 fields)

| Field | Description | MongoDB Form |
|-------|-------------|--------------|
| `TO_<=10` | Temperature optimum ≤10°C | `TO_lte_10` |
| `TO_>40` | Temperature optimum >40°C | `TO_gt_40` |
| `Td_>30` | Temperature delta >30°C | `Td_gt_30` |

**Proposed action**: Add to existing temperature hierarchies

#### P2.2.6: pH Boundary Fields (1 field)

| Field | Description | MongoDB Form |
|-------|-------------|--------------|
| `pHd_<=1` | pH delta ≤1 | `pHd_lte_1` |

**Proposed action**: Add to existing pH delta hierarchy (METPO:1000473-1000478)

#### P2.2.7: Shape Fields (2 fields)

| Field | Description | MongoDB Form |
|-------|-------------|--------------|
| `S_curved_spiral` | Curved/spiral shape | `S_curved_spiral` |
| `S_star_dumbbell_pleomorphic` | Star/dumbbell/pleomorphic shape | `S_star_dumbbell_pleomorphic` |

**Note**: These appear in kg-microbe with leading space: ` S_curved_spiral`

**Proposed action**: Add to existing shape hierarchy (METPO:1000674-1000685)

#### P2.2.8: Sporulation Fields (2 fields)

| Field | Description | MongoDB Form |
|-------|-------------|--------------|
| `spore` | Spore formation | `spore` |
| `no_spore` | No spore formation | `no_spore` |

**Proposed action**: Add to sporulation hierarchy

#### P2.2.9: Motility Fields (1 field)

| Field | Description | MongoDB Form |
|-------|-------------|--------------|
| `non-motile` | Non-motile | `non_motile` |

**Note**: Already mapped to METPO:1000702 "motile" but as inverse. May need separate class.

#### P2.2.10: Trophic Type Fields (1 field)

| Field | Description | MongoDB Form |
|-------|-------------|--------------|
| `TT_copiotroph_diazotroph` | Copiotroph/diazotroph | `TT_copiotroph_diazotroph` |

**Proposed action**: Add to trophic type hierarchy

#### P2.2.11: Pigment Type (1 field)

| Field | Description | MongoDB Form |
|-------|-------------|--------------|
| `Pigment_carotenoid` | Carotenoid pigment | `Pigment_carotenoid` |

**Proposed action**: Add alongside pigment color fields

---

## PRIORITY 3: Documentation and Validation

### P3.1: Field Mapping Documentation

**File**: `docs/bactotraits_field_mappings.md`

**Contents**:
- Three-way mapping table: provider → kg-microbe → MongoDB
- Sanitization rules explanation
- Examples of each transformation type
- Notes on encoding (ISO-8859-1 → UTF-8)

### P3.2: Coverage Analysis Documentation

**File**: `docs/bactotraits_metpo_coverage_analysis.md`

**Contents**:
- Current coverage statistics (57/94 trait fields = 60.6%)
- Projected coverage after fixes
- Breakdown by category (temperature, pH, NaCl, morphology, etc.)
- Recommendations for priority additions

### P3.3: Validation Scripts

**Task**: Ensure all reconciliation scripts work with sanitized names

**Files to verify**:
- `src/scripts/bactotraits_metpo_set_difference.py` ✓ (already updated)
- `src/scripts/reconcile_bactotraits_coverage.py` ✓ (already updated)
- Any SPARQL queries that reference BactoTraits synonyms

---

## Implementation Checklist

### Phase 1: Critical Fixes (1-2 days)

- [ ] **P1.1**: Fix 7 comparison operator errors in metpo.owl
- [ ] **P1.2**: Fix 6 shape field case errors in metpo.owl
- [ ] **P1.3**: Fix 1 whitespace error in metpo.owl
- [ ] **Validation**: Run set difference script, verify 0 orphaned synonyms
- [ ] **Validation**: Run coverage script, verify 64/105 matches

### Phase 2: High-Value Additions (3-5 days)

- [ ] **P2.1.1**: Add 9 pigment color fields to metpo.owl
- [ ] **P2.1.2**: Add 2 temperature range boundary fields to metpo.owl
- [ ] **P2.1.3**: Add 2 NaCl range boundary fields to metpo.owl
- [ ] **Validation**: Run coverage script, verify 77/105 matches

### Phase 3: Low-Value Additions (1 week)

- [ ] **P2.2.1**: Add GC content boundary fields
- [ ] **P2.2.2**: Add cell length bin fields
- [ ] **P2.2.3**: Add cell width bin fields
- [ ] **P2.2.4**: Add NaCl boundary fields
- [ ] **P2.2.5**: Add temperature boundary fields
- [ ] **P2.2.6**: Add pH boundary fields
- [ ] **P2.2.7**: Add remaining shape fields
- [ ] **P2.2.8**: Add sporulation fields
- [ ] **P2.2.9**: Review motility field mapping
- [ ] **P2.2.10**: Add remaining trophic type fields
- [ ] **P2.2.11**: Add pigment type field
- [ ] **Validation**: Run coverage script, verify 95/105 matches

### Phase 4: Documentation (ongoing)

- [ ] **P3.1**: Create field mapping documentation
- [ ] **P3.2**: Create coverage analysis documentation
- [ ] **P3.3**: Validate all reconciliation scripts

---

## Excluded from Coverage

These 10 fields are not trait fields and should not be added to METPO:

| Field | Unique Values | Reason for Exclusion |
|-------|--------------|----------------------|
| `culture collection codes` | 19,439 | Identifier, not trait |
| `Bacdive_ID` | 19,455 | Identifier |
| `ncbitaxon_id` | 9,933 | Taxonomic reference |
| `Full_name` | 11,355 | Taxonomic name |
| `Species` | 6,525 | Taxonomic rank |
| `Genus` | 2,394 | Taxonomic rank |
| `Family` | 708 | Taxonomic rank |
| `Order` | 471 | Taxonomic rank |
| `Class` | 363 | Taxonomic rank |
| `Phylum` | 323 | Taxonomic rank |

**Final trait coverage goal**: 95/94 = 101% (some fields map to multiple METPO classes)

---

## Notes

1. **Leading whitespace in shape fields**: The provider and kg-microbe versions preserve leading spaces on some shape field values (` S_rod`, ` S_sphere`, etc.). Decision needed on whether to add both forms as synonyms.

2. **Comparison operator encoding**: OWL files use XML entities (`&lt;` for `<`, `&gt;` for `>`). Use `&lt;=` for `<=`.

3. **MongoDB sanitization**: Remember that MongoDB field names differ from kg-microbe names:
   - `GC_<=42.65` (kg-microbe) → `GC_lte_42_65` (MongoDB)
   - `non-motile` (kg-microbe) → `non_motile` (MongoDB)

4. **METPO synonym attribution**: All synonyms should have:
   - `oboInOwl:hasRelatedSynonym` property
   - BactoTraits source annotation: `https://ordar.otelo.univ-lorraine.fr/files/ORDAR-53/BactoTraits_databaseV2_Jun2022.csv`

5. **Testing**: After each phase, regenerate both reconciliation reports:
   ```bash
   make reconcile-bactotraits
   uv run python src/scripts/bactotraits_metpo_set_difference.py --format yaml --output reports/bactotraits-metpo-set-diff.yaml
   ```
