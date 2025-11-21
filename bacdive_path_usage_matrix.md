# BacDive Knowledge Path Usage Matrix

**Date**: 2025-11-20
**Purpose**: Definitive reference for which BacDive paths are used in KG-Microbe and how they're represented

---

## Summary Statistics

| Category | Count | Details |
|----------|-------|---------|
| **Total BacDive chemistry/enzyme paths** | 24 | 31 Physiology fields minus 7 non-chemistry fields |
| **Currently used in KG-M** | 10 | Producing edges in output |
| **Extracted but NOT used** | 3 | Variables exist but no edges created |
| **Not extracted at all** | 0 | All relevant fields are extracted |
| **Using METPO CURIEs** | 6 | Proper ontology representation |
| **Using ad-hoc prefixes** | 3 | `assay:`, `strain:`, etc. |
| **Using standard ontology (EC, CHEBI)** | 4 | Non-METPO but still semantic |

---

## Complete Path Usage Matrix

### Legend
- ✅ **Used & Semantic**: Processed with METPO/EC/CHEBI identifiers
- ⚠️ **Used but Ad-hoc**: Processed but uses non-semantic prefixes
- ❌ **Extracted but Unused**: Variable exists but no edges created
- 🔍 **Partially Used**: Some aspects processed, others ignored

| # | BacDive Path | Used in KG-M? | Representation Type | Prefix/Namespace | Edge Count | Code Location | METPO Term(s) | Notes |
|---|--------------|---------------|---------------------|------------------|------------|---------------|---------------|-------|
| **1** | `General.keywords` | ✅ Used | **METPO CURIEs** | `METPO:` | ~120K | Lines 979-984 | Multiple (METPO:1000602, 1000603, 1000615, etc.) | Keyword-based phenotype mapping |
| **2** | `Physiology and metabolism.metabolite utilization` | 🔍 Partial | **Standard ontology (CHEBI)** | `CHEBI:` | 393K | Lines 1425-1501 | None (uses CHEBI directly) | ✅ Positive results only; ❌ Negatives ignored; ❌ Utilization type ignored |
| **3** | `Physiology and metabolism.metabolite production` | 🔍 Partial | **Standard ontology (CHEBI)** | `CHEBI:` | 12.5K | Lines 1503-1567 | None (uses CHEBI directly) | ✅ Yes results only; ❌ No results ignored |
| **4** | `Physiology and metabolism.enzymes` | 🔍 Partial | **Standard ontology (EC)** | `EC:` | 186K | Lines 1080-1134 | None (uses EC numbers directly) | ✅ Positive activity only; ❌ Negatives ignored; ❌ No substrate links |
| **5-20** | `Physiology and metabolism.API [20A\|20E\|20NE\|20STR\|50CHac\|50CHas\|CAM\|ID32E\|ID32STA\|LIST\|NH\|STA\|coryne\|rID32A\|rID32STR\|zym]` (16 systems) | ⚠️ Used | **⚠️ Ad-hoc prefix** | `assay:` | 522K | Lines 1610-1655 | None | ⚠️ Non-semantic prefix like `assay:API_20E_ONPG`; ❌ Negatives ignored; ❌ No EC/CHEBI links |
| **21** | `Physiology and metabolism.antibiotic resistance` | ✅ Used | **Standard ontology (CHEBI)** | `CHEBI:` | 10K | Lines 1700-1720 | None (uses CHEBI directly) | ✅ Well-handled with resistance predicates |
| **22** | `Physiology and metabolism.halophily` | 🔍 Partial | **METPO CURIEs** | `METPO:` | 127 | Via keywords + METPO tree | METPO:1000620-1000629 (halophily classes) | ⚠️ Only keyword-based (159 strains); ❌ Path-based NOT enabled (9,687 strains ignored!) |
| **23** | `Physiology and metabolism.oxygen tolerance.oxygen tolerance` | ✅ Used | **METPO CURIEs** | `METPO:` | ~15K | Lines 1568-1573 | METPO:1000601 (parent), 1000602 (aerobic), 1000603 (anaerobic), etc. | ✅ Path-based METPO extraction working |
| **24** | `Physiology and metabolism.spore formation.spore formation` | ✅ Used | **METPO CURIEs** | `METPO:` | ~1.5K | Lines 1575-1580 | METPO:1000870 (sporulation parent) | ✅ Path-based METPO extraction working |
| **25** | `Physiology and metabolism.nutrition type.type` | ✅ Used | **METPO CURIEs** | `METPO:` | Unknown | Lines 1582-1587 | METPO:1000631 (trophic type parent) | ✅ Path-based METPO extraction working |
| **26** | `Physiology and metabolism.metabolite tests` | ❌ **UNUSED** | N/A - Not processed | N/A | **0** | Extracted line 872, passed line 1083, **NEVER USED** | Could use CHEBI (IDs present) | ❌ **MAJOR GAP**: Has CHEBI + test results but completely ignored! |
| **27** | `Physiology and metabolism.compound production` | ❌ **UNUSED** | N/A - Not processed | N/A | **0** | Extracted line 901, passed line 1090, **NEVER USED** | Could create METPO production terms or use NER→CHEBI | ❌ **MAJOR GAP**: Similar to metabolite production but ignored |
| **28** | `Physiology and metabolism.fatty acid profile` | ❌ **UNUSED** | N/A - Not processed | N/A | **0** | Extracted line 904, passed line 1091, **NEVER USED** | Could use CHEBI (needs FA notation mapping) | ❌ **MAJOR GAP**: Taxonomically valuable but ignored |

---

## Breakdown by Representation Type

### ✅ Using METPO CURIEs (6 paths)

| Path | METPO Terms | Edge Count | Status |
|------|-------------|------------|--------|
| General.keywords | Multiple (60+ terms) | ~120K | ✅ Working well |
| oxygen tolerance | METPO:1000601-1000608 | ~15K | ✅ Working well |
| spore formation | METPO:1000870+ | ~1.5K | ✅ Working well |
| nutrition type | METPO:1000631+ | Unknown | ✅ Working well |
| halophily (keywords) | METPO:1000620-1000629 | 127 | ⚠️ Only keywords, not path-based |
| *(cell shape)* | METPO:1000666+ | Unknown | ✅ From Morphology section |
| *(gram stain)* | METPO:1000697+ | Unknown | ✅ From Morphology section |
| *(motility)* | METPO:1000701+ | Unknown | ✅ From Morphology section |

**Total METPO edges**: ~140K+ (primarily from keywords + oxygen/spore/nutrition paths)

**Mechanism**: Two approaches:
1. **Keyword matching**: `General.keywords` → METPO mappings via normalization
2. **Path-based extraction**: METPO tree nodes specify BacDive JSON paths → extract values → match to METPO child terms

---

### ✅ Using Standard Ontology Identifiers (4 paths)

| Path | Ontology | Prefix | Edge Count | Predicate | Status |
|------|----------|--------|------------|-----------|--------|
| metabolite utilization | CHEBI | `CHEBI:` | 393K | `biolink:consumes` | 🔍 Only positive |
| metabolite production | CHEBI | `CHEBI:` | 12.5K | `biolink:produces` | 🔍 Only positive |
| enzymes | EC Enzyme | `EC:` | 186K | `biolink:capable_of` | 🔍 Only positive |
| antibiotic resistance | CHEBI | `CHEBI:` | 10K | `biolink:associated_with_resistance_to` | ✅ Good |

**Total standard ontology edges**: ~600K+

**Why not METPO?**: These use established ontologies (CHEBI for chemicals, EC for enzymes) which are appropriate. METPO focuses on phenotypes and capabilities, not chemical identity.

---

### ⚠️ Using Ad-Hoc Prefixes (3 contexts)

| Path/Context | Ad-hoc Prefix | Node Count | Edge Count | Why Ad-hoc? | Should Use Instead |
|--------------|---------------|------------|------------|-------------|-------------------|
| API test results | `assay:` | 511 | 522K | No EC/CHEBI mapping | **EC numbers + CHEBI substrates** |
| Strain identifiers | `strain:` | 172K | N/A | BacDive strain IDs | ✅ Acceptable (local identifiers) |
| Culture media | `medium:` | 1,571 | N/A | No standard medium ontology | ⚠️ Debatable (could use OBI terms) |
| Isolation sources | `isolation_source:` | 353 | N/A | Free-text environmental terms | ⚠️ Could use ENVO terms |

**Most problematic**: `assay:` prefix for API tests
- Example: `assay:API_20E_ONPG`
- Should be: `NCBITaxon:X → biolink:capable_of → EC:3.2.1.23` + `EC:3.2.1.23 → biolink:consumes → CHEBI:75055`

---

### ❌ Extracted But Not Used (3 paths)

| Path | Has Ontology IDs? | Structure | Why Unused? | Priority to Fix |
|------|------------------|-----------|-------------|-----------------|
| metabolite tests | ✅ CHEBI IDs present | `{Chebi-ID, metabolite, "citrate test": "+/-", ...}` | Dead code - extracted but processing never implemented | **HIGHEST** |
| compound production | ❌ Free text | `{compound: "indole", excreted: "yes/no"}` | Dead code - extracted but processing never implemented | **HIGH** |
| fatty acid profile | ⚠️ Needs mapping | `{fatty acid: "16:0", percentage: 25.3}` | Dead code - extracted but processing never implemented | **MEDIUM** |

**Impact**: Unknown edge count potential (need MongoDB queries)

**Why this happened**: Variables are passed to `_build_keyword_map_from_record()` but that function only uses data for METPO tree path extraction, not general processing.

---

## METPO vs. Non-METPO Decision Matrix

### When BacDive Data Uses METPO

| Data Type | Uses METPO? | Example | Rationale |
|-----------|-------------|---------|-----------|
| **Categorical phenotypes** | ✅ Yes | "aerobic", "halophilic", "mesophilic" | METPO's core purpose: phenotype classification |
| **Metabolic capabilities** | ✅ Yes | "phototrophic", "chemoheterotrophic" | METPO models trophic types |
| **Structural phenotypes** | ✅ Yes | "spore-forming", "motile", "gram-positive" | METPO includes morphology |
| **Process participation** | ⚠️ Sometimes | "fermentation", "respiration" | METPO has high-level process classes |

### When BacDive Data Uses Other Ontologies

| Data Type | Uses Instead | Example | Rationale |
|-----------|--------------|---------|-----------|
| **Chemical identity** | CHEBI | D-glucose (CHEBI:17634) | CHEBI is THE chemical ontology |
| **Enzyme identity** | EC numbers | β-galactosidase (EC:3.2.1.23) | EC is THE enzyme classification |
| **Taxonomic identity** | NCBITaxon | *E. coli* (NCBITaxon:562) | NCBITaxon is standard for organisms |
| **Chemical-specific capabilities** | ❌ **Nothing** (gap) | "ferments D-glucose" | ⚠️ Should use METPO process + CHEBI chemical in separate edges |

### When BacDive Data Uses Ad-Hoc Prefixes (PROBLEMS!)

| Data Type | Currently Uses | Should Use | Why It's Wrong |
|-----------|----------------|------------|----------------|
| **API test results** | `assay:API_20E_ONPG` | `EC:3.2.1.23` + `CHEBI:75055` | Non-semantic, no enzyme or substrate info |
| **Strain IDs** | `strain:12345` | ✅ OK (local IDs) | Actually acceptable for strain identifiers |
| **Media** | `medium:Marine_Broth` | Debatable (OBI?) | Could be improved but low priority |
| **Isolation** | `isolation_source:soil` | ENVO terms | Could use environmental ontology |

---

## Path-Based vs. Keyword-Based METPO Extraction

### Keyword-Based (from General.keywords)

**Mechanism**:
```python
# Line 979-984
keywords = general_info.get(KEYWORDS, "")
nodes_from_keywords = {
    key: keyword_map[key.lower().replace(" ", "_").replace("-", "_")]
    for key in keywords
    if key.lower().replace(" ", "_").replace("-", "_") in keyword_map
}
```

**Characteristics**:
- ✅ Simple categorical labels
- ✅ Broad coverage (~159 halophily keywords)
- ❌ No experimental evidence
- ⚠️ Normalization mismatch bug (spaces/hyphens)

**Examples**: "halophilic", "mesophilic", "aerobe", "spore-forming"

---

### Path-Based (from METPO tree JSON paths)

**Mechanism**:
```python
# Lines 252-313, 1568-1608
def _process_phenotype_by_metpo_parent(self, record, parent_iri, ...):
    parent_node = self.bacdive_metpo_tree.get(parent_iri)
    for json_path in parent_node.bacdive_json_paths:
        extracted_values = self._extract_value_from_json_path(record, json_path)
        # Match extracted values to METPO child terms
```

**METPO sheet specifies paths**:
```tsv
METPO:1000601  oxygen preference  ...  Physiology and metabolism.oxygen tolerance.oxygen tolerance
METPO:1000870  sporulation       ...  Physiology and metabolism.spore formation.spore formation
METPO:1000631  trophic type      ...  Physiology and metabolism.nutrition type.type
```

**Characteristics**:
- ✅ Experimental evidence with references
- ✅ Structured data
- ✅ Multiple observations per strain
- ❌ More complex extraction
- ❌ Lower coverage (only strains with experimental data)

**Currently enabled for**:
1. oxygen tolerance (METPO:1000601)
2. spore formation (METPO:1000870)
3. nutrition type (METPO:1000631)
4. cell shape (METPO:1000666)
5. gram stain (METPO:1000697)
6. motility (METPO:1000701)

**Should be enabled but ISN'T**:
- halophily (METPO:1000629) - 9,687 strains with data vs. 159 with keywords!

---

## Coverage Summary Table

| Representation Type | Paths Using It | Total Edges | Nodes Created | METPO Alignment |
|---------------------|----------------|-------------|---------------|-----------------|
| **METPO CURIEs** | 6 main + 3 morphology | ~140K | 61 METPO nodes | ✅ Perfect |
| **Standard Ontology (EC, CHEBI)** | 4 | ~600K | 1,088 CHEBI + 112 EC | ✅ Appropriate |
| **Ad-hoc prefixes** | 3 | 522K | 511 assay + 1,571 medium + 353 isolation | ❌ Should use semantic IDs |
| **Not used** | 3 | **0** | **0** | ❌ Missing opportunities |

**Total edges in BacDive transform**: 1,656,668
**METPO-related edges**: ~140K (8.4% of total)
**Ad-hoc prefix edges**: ~522K (31.5% of total) ← **Major problem!**

---

## Recommendations by Priority

### Priority 1: Eliminate Ad-Hoc Assay Prefix (HIGHEST IMPACT)

**Current**: `assay:API_20E_ONPG` (511 nodes, 522K edges)
**Replace with**: `EC:3.2.1.23` + `CHEBI:75055`
**Impact**: Remove 31.5% of non-semantic edges
**Effort**: Medium (need API → EC/CHEBI mapping file)

### Priority 2: Implement Metabolite Tests (EASY WIN)

**Current**: Completely unused
**Add**: CHEBI-based edges like metabolite utilization
**Impact**: Potentially thousands of new edges with +/- results
**Effort**: Low (1-2 days, has CHEBI IDs already)

### Priority 3: Capture Negative Results (HIGH VALUE)

**Current**: Only positive results (+, yes) captured
**Add**: Edge properties for negative results (-, no)
**Impact**: Double training data across 4 fields (~1M more edges)
**Effort**: Low (add edge property columns)

### Priority 4: Enable Halophily Path Extraction

**Current**: 127 keyword-based edges
**Add**: Path-based extraction from 9,687 strains
**Impact**: 60x more halophily data with experimental evidence
**Effort**: Medium (add path processing call)

---

## Related Documentation

- Complete audit: `metpo/bacdive_complete_chemistry_audit.md`
- Chemical/enzyme analysis: `metpo/bacdive_chemical_enzyme_gap_analysis.md`
- Coverage analysis: `metpo/bacdive_metpo_coverage_analysis.md`
- Issue #22: BacDive Ingestion Lifecycle
- Issue #25: Chemical-Enzyme Interactions Gap Analysis

---

## Quick Reference: BacDive → KG-M Representation Decision Tree

```
BacDive Data Type?
│
├─ Categorical phenotype? → Use METPO (e.g., "aerobic" → METPO:1000602)
│
├─ Chemical compound? → Use CHEBI (e.g., "D-glucose" → CHEBI:17634)
│
├─ Enzyme activity? → Use EC number (e.g., "catalase" → EC:1.11.1.6)
│
├─ Organism? → Use NCBITaxon (e.g., "E. coli" → NCBITaxon:562)
│
├─ Chemical-specific capability? → Use METPO process + CHEBI in separate edges
│  Example: ferments glucose = NCBITaxon:X → capable_of → METPO:1002005 (Fermentation)
│                              + NCBITaxon:X → consumes → CHEBI:17634 (D-glucose)
│
└─ Unknown/unmapped? → ❌ DON'T use ad-hoc prefix! Either:
   1. Find appropriate ontology term
   2. Create METPO term if it's a phenotype
   3. Use NER to map to existing ontology
   4. Leave unprocessed until proper mapping exists
```
