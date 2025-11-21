# BacDive Chemical and Enzyme Activity: Gap Analysis and METPO Strategy

**Date**: 2025-11-20
**Focus**: Representing microbe-chemical-enzyme interactions without ad-hoc prefixes

---

## Executive Summary

**Current Problem**: BacDive contains rich assay data showing microbe-chemical-enzyme interactions, but KG-Microbe currently:
1. Uses **ad-hoc `assay:` prefix** for assay results (511 assay nodes, 522,416 `biolink:assesses` edges)
2. Only captures **positive results** (`+` signs) from API tests
3. **Ignores negative results** (`-` signs) which are equally valuable for machine learning
4. Doesn't capture **all chemical-microbe interactions** from metabolite tests

**Opportunity**: BacDive has structured fields for:
- **metabolite utilization** (with +/- activity, utilization type)
- **metabolite production** (yes/no)
- **API test batteries** (15+ different test types with +/- results)
- **enzymes** (EC numbers with activity data)

**Goal**: Represent microbe-chemical-enzyme interactions using **METPO CURIEs** and **standard biolink predicates**, avoiding ad-hoc prefixes.

---

## Current State Analysis

### Predicates Used Across KG-Microbe Sources

| Predicate | BacDive | Madin | BactoTraits | Notes |
|-----------|---------|-------|-------------|-------|
| `biolink:has_phenotype` | 123,867 | 44,081 | 90,768 | **Universal** - all 3 sources |
| `biolink:consumes` | 393,508 | 36,817 | 0 | **Chemical substrate utilization** |
| `biolink:capable_of` | 186,197 | 7,493 | 0 | **Metabolic capabilities** |
| `biolink:produces` | 12,523 | 0 | 0 | **Chemical product generation** |
| `biolink:assesses` | 522,416 | 0 | 0 | **Assay-to-organism** (⚠️ ad-hoc prefix) |
| `biolink:occurs_in` | 53,338 | 0 | 0 | **Chemical-to-assay** |
| `biolink:associated_with_sensitivity_to` | 12,518 | 0 | 0 | **Antibiotic sensitivity** |
| `biolink:associated_with_resistance_to` | 10,297 | 0 | 0 | **Antibiotic resistance** |
| `biolink:location_of` | 169,130 | 26,649 | 0 | **Isolation sources** |
| `biolink:subclass_of` | 172,761 | 0 | 0 | **Taxonomy hierarchy** |

**Best Practice Established**: `biolink:consumes` is used by both BacDive and Madin for chemical substrate utilization (430K+ edges total)

---

## BacDive Data Sources for Chemical/Enzyme Interactions

### 1. Metabolite Utilization

**Path**: `Physiology and metabolism.metabolite utilization`

**Structure**:
```json
[
  {
    "@ref": 12345,
    "Chebi-ID": 15824,
    "metabolite": "D-fructose",
    "utilization activity": "+",
    "kind of utilization tested": "fermentation"
  },
  {
    "@ref": 12346,
    "Chebi-ID": 17634,
    "metabolite": "D-glucose",
    "utilization activity": "-",
    "kind of utilization tested": "respiration"
  }
]
```

**Current Handling** (`bacdive.py:1425-1501`):
- ✅ **Captured**: Positive activity (`+`) with CHEBI ID
- ✅ **Predicate**: `biolink:consumes` (line 1494)
- ✅ **Relation**: `RO:0000057` (has_participant)
- ❌ **Ignored**: Negative activity (`-`)
- ❌ **Ignored**: `kind of utilization tested` (fermentation, respiration, etc.)
- ❌ **Ignored**: Metabolites without CHEBI IDs (commented out, lines 1432-1442)

**Coverage**: Currently creates edges for ~393,000 positive utilization cases

---

### 2. Metabolite Production

**Path**: `Physiology and metabolism.metabolite production`

**Structure**:
```json
[
  {
    "@ref": 12347,
    "Chebi-ID": 16761,
    "metabolite": "indole",
    "production": "yes"
  },
  {
    "@ref": 12348,
    "metabolite": "acetoin",
    "production": "no"
  }
]
```

**Current Handling** (`bacdive.py:1503-1567`):
- ✅ **Captured**: Production = "yes" with CHEBI ID
- ✅ **Predicate**: `biolink:produces` (line 1544)
- ✅ **Relation**: `RO:0002233` (has_output)
- ❌ **Ignored**: Production = "no"
- ❌ **Ignored**: Metabolites without CHEBI IDs (commented out, lines 1517-1522)

**Coverage**: Currently creates edges for ~12,500 production cases

---

### 3. API Test Batteries

**Paths**: `Physiology and metabolism.API [20A|20E|20NE|20STR|50CHac|50CHas|CAM|ID32E|ID32STA|LIST|NH|STA|coryne|rID32A|rID32STR|zym]`

**Structure**: Variable nested dicts and lists with test results

**Example** (API 20E):
```json
{
  "@ref": 12349,
  "ONPG": "+",
  "ADH": "-",
  "LDC": "+",
  "ODC": "-",
  "CIT": "+",
  "H2S": "-"
}
```

**Current Handling** (`bacdive.py:1610-1655`):
- ✅ **Captured**: Positive results (`+`) only
- ⚠️ **Uses ad-hoc prefix**: `assay:API_20E_ONPG` (line 1632)
- ⚠️ **Category**: `biolink:PhenotypicQuality` (line 1633) - should be more specific
- ⚠️ **Predicate**: `biolink:assesses` from assay to organism (line 1646)
- ⚠️ **Relation**: `RO:0000053` (bearer_of) - not standard for capabilities
- ❌ **Ignored**: Negative results (`-`)
- ❌ **No chemical links**: Tests like "ONPG", "ADH" are enzyme/substrate abbreviations but not linked to CHEBI

**Coverage**: 522,416 `biolink:assesses` edges, all using ad-hoc `assay:` prefix

---

### 4. Enzymes

**Path**: `Physiology and metabolism.enzymes`

**Structure**:
```json
[
  {
    "@ref": 12350,
    "enzyme": "catalase",
    "EC-number": "1.11.1.6",
    "activity": "+"
  }
]
```

**Current Handling** (`bacdive.py:1080-1134`):
- ✅ **Captured**: Enzymes with EC numbers
- ✅ **Creates EC nodes**: `EC:1.11.1.6`
- ✅ **Predicate**: `biolink:capable_of` (enzyme activity capability)
- ❌ **Ignored**: Negative activity (`-`)
- ❌ **No substrate links**: EC numbers not linked to substrates/products from ChEBI

**Coverage**: 112 EC nodes, ~186,000 `biolink:capable_of` edges

---

## Gap Summary

| Data Type | BacDive Path | Currently Captured | Currently Ignored | Edge Count |
|-----------|--------------|-------------------|-------------------|------------|
| Metabolite utilization | `metabolite utilization` | Positive + CHEBI | Negative, no CHEBI, utilization type | ~393K |
| Metabolite production | `metabolite production` | Yes + CHEBI | No, no CHEBI | ~12K |
| API tests | `API *` | Positive only | Negative, chemical/enzyme context | ~522K |
| Enzymes | `enzymes` | EC numbers + positive | Negative, substrate/product links | ~186K |

**Key Gaps**:
1. **No negative results** - ML models need both positive and negative examples
2. **Ad-hoc `assay:` prefix** - should use METPO or chemical/enzyme identifiers
3. **Missing utilization type context** - fermentation vs. respiration distinction lost
4. **No substrate-enzyme-product triads** - disconnected data silos

---

## Proposed Solution: METPO + Biolink Patterns

### Design Principles

1. **Use METPO CURIEs** for metabolic capabilities/processes
2. **Use standard biolink predicates** (already established in KG-M)
3. **Capture polarity** via edge properties or negated predicates
4. **Single edges** for simple assertions (microbe-chemical)
5. **Edge properties** for context (test type, method, conditions)
6. **No ad-hoc prefixes** - only METPO, CHEBI, EC, NCBITaxon

---

### Pattern 1: Metabolite Utilization with Polarity

**For positive utilization** (`activity: "+"`) - **EXISTING PATTERN, KEEP IT**:
```
NCBITaxon:12345  →  biolink:consumes  →  CHEBI:15824 (D-fructose)
  relation: RO:0000057 (has_participant)
  primary_knowledge_source: bacdive:12345
  [NEW] utilization_type: "fermentation"  # from "kind of utilization tested"
  [NEW] evidence: "+"
```

**For negative utilization** (`activity: "-"`) - **NEW PATTERN**:

**Option A: Use negated predicate** (not standard in Biolink yet):
```
NCBITaxon:12345  →  biolink:does_not_consume  →  CHEBI:17634 (D-glucose)
```
❌ Problem: `biolink:does_not_consume` doesn't exist

**Option B: Use qualifier/edge property** ✅ **RECOMMENDED**:
```
NCBITaxon:12345  →  biolink:consumes  →  CHEBI:17634 (D-glucose)
  relation: RO:0000057
  primary_knowledge_source: bacdive:12346
  utilization_type: "respiration"
  evidence: "-"
  qualified_predicate: "does_not_consume"  # Biolink Association qualifier
```

**Option C: Use METPO capability classes** (if they exist):
```
NCBITaxon:12345  →  biolink:capable_of  →  METPO:XXXXXX (fermentation of D-fructose)
NCBITaxon:12345  →  biolink:lacks_capability_for  →  METPO:YYYYYY (respiration of D-glucose)
```
❌ Problem: Would need thousands of METPO terms (one per chemical × process combination)

**Recommendation**: **Option B** - Use edge properties to indicate polarity

---

### Pattern 2: Replace Ad-Hoc Assay Nodes with Capability Assertions

**Current pattern** (using ad-hoc prefix):
```
assay:API_20E_ONPG  →  biolink:assesses  →  NCBITaxon:12345
```
❌ Problems:
- Ad-hoc `assay:` prefix
- No semantic meaning for "API_20E_ONPG"
- No chemical or enzyme linkage

**Proposed pattern** (chemical-centric):

**Step 1**: Map API test abbreviations to enzymes/chemicals:
- `ONPG` → enzyme: β-galactosidase (EC:3.2.1.23), substrate: CHEBI:75055 (ONPG)
- `ADH` → enzyme: arginine dihydrolase (EC:3.5.3.6), substrate: CHEBI:16467 (arginine)
- `LDC` → enzyme: lysine decarboxylase (EC:4.1.1.18), substrate: CHEBI:18019 (lysine)

**Step 2**: Create edges using standard identifiers:
```
# Positive result: organism has enzyme activity
NCBITaxon:12345  →  biolink:capable_of  →  EC:3.2.1.23 (β-galactosidase)
  relation: RO:0002215 (capable_of)
  primary_knowledge_source: bacdive:12349
  assay_type: "API 20E"
  evidence: "+"

# Link enzyme to substrate
EC:3.2.1.23  →  biolink:consumes  →  CHEBI:75055 (ONPG)
  relation: RO:0000057

# Negative result: organism lacks enzyme activity
NCBITaxon:12345  →  biolink:capable_of  →  EC:3.5.3.6 (arginine dihydrolase)
  relation: RO:0002215
  primary_knowledge_source: bacdive:12349
  assay_type: "API 20E"
  evidence: "-"
  qualified_predicate: "lacks_capability_for"
```

---

### Pattern 3: Substrate-Enzyme-Product Triads

**For metabolite tests where enzyme is known**:

```
# Organism has enzyme activity
NCBITaxon:12345  →  biolink:capable_of  →  EC:1.11.1.6 (catalase)
  primary_knowledge_source: bacdive:12350
  evidence: "+"

# Enzyme acts on substrate
EC:1.11.1.6  →  biolink:consumes  →  CHEBI:16240 (hydrogen peroxide)

# Enzyme produces product
EC:1.11.1.6  →  biolink:produces  →  CHEBI:15379 (dioxygen)
EC:1.11.1.6  →  biolink:produces  →  CHEBI:15377 (water)
```

**Benefit**: Creates knowledge graph paths:
```
Organism → capable_of → Enzyme → consumes → Substrate
                      ↘ produces → Product
```

---

## Edge Property Standardization

### Current Edge Properties in KG-M

From `nodes.tsv` and `edges.tsv` column structure:
```
subject | predicate | object | relation | primary_knowledge_source
```

**Additional properties used** (need to verify if standard):
- None currently - just the 5 columns above

### Proposed Edge Properties for Assay Data

Following [Biolink Association qualifiers](https://biolink.github.io/biolink-model/docs/qualified_predicate.html):

| Property | Values | Example | Used For |
|----------|--------|---------|----------|
| `qualified_predicate` | String (predicate name) | "does_not_consume", "lacks_capability_for" | Negation |
| `evidence` | "+", "-", "yes", "no" | "+", "-" | Raw assay result |
| `assay_type` | String | "API 20E", "fermentation", "respiration" | Experimental method |
| `utilization_type` | String | "fermentation", "respiration", "assimilation" | Metabolic mode |

**Implementation**: Would require updating KGX node/edge headers to support additional columns beyond the current 5.

**Alternative**: Encode in JSON within existing columns (less preferred, harder to query)

---

## METPO Metabolic Capability Classes

### Existing METPO Terms

**High-level processes**:
- METPO:1002005 (Fermentation)
- METPO:1000800 (respiration)
- METPO:1000803 (Oxidative phosphorylation)
- METPO:1000804 (Substrate-level phosphorylation)
- METPO:1000844 (Methanogenesis)
- METPO:1000845 (Acetogenesis)

**Trophic types**:
- METPO:1000631 (trophic type)
  - METPO:1000632 (autotrophic)
  - METPO:1000633 (chemoheterotrophic)
  - METPO:1000634 (chemoorganoheterotrophic)
  - etc.

**Problem**: These are high-level process classes, not chemical-specific capabilities

**Not practical to create**: METPO:XXXXXX (fermentation of D-fructose), METPO:YYYYYY (respiration of D-glucose), etc. for every chemical

**Solution**: Use METPO for process type + CHEBI for chemical identity in separate edges

---

## Implementation Recommendations

### Priority 1: Capture Negative Results (HIGH VALUE, LOW EFFORT)

**Current code ignores negatives**:
```python
# bacdive.py:1446
if (
    METABOLITE_CHEBI_KEY in metabolite
    and metabolite.get(UTILIZATION_ACTIVITY) == PLUS_SIGN  # ← Only "+"
):
```

**Proposed change**:
```python
if METABOLITE_CHEBI_KEY in metabolite:
    activity = metabolite.get(UTILIZATION_ACTIVITY)  # Get "+", "-", or other
    if activity in ["+", "-"]:  # Accept both positive and negative
        # Create edge with evidence property
        edge_writer.writerow([
            organism,
            NCBI_TO_METABOLITE_UTILIZATION_EDGE,
            chebi_key,
            HAS_PARTICIPANT,
            BACDIVE_PREFIX + key,
            # Add evidence column (requires header update)
        ])
```

**Impact**: Double the training data for ML models (positive + negative examples)

**Estimated new edges**: ~393,000 more (matching current positive edges)

---

### Priority 2: Replace Ad-Hoc Assay Prefix with EC Numbers (MEDIUM EFFORT)

**Challenge**: Need mapping file `API_abbreviation → (EC_number, CHEBI_substrate)`

**Example mapping needed**:
```yaml
API_20E:
  ONPG:
    enzyme: EC:3.2.1.23
    substrate: CHEBI:75055
    name: "β-galactosidase activity (ONPG hydrolysis)"
  ADH:
    enzyme: EC:3.5.3.6
    substrate: CHEBI:16467
    name: "arginine dihydrolase activity"
  # ... 40+ more tests across 15+ API systems
```

**Current code** (`bacdive.py:1620-1655`):
```python
meta_assay = {
    f"{assay_name_norm}:{k}"
    for entry in values
    if isinstance(entry, dict)
    for k, v in entry.items()
    if v == PLUS_SIGN  # ← Only captures "+"
}

# Creates nodes like: assay:API_20E_ONPG
```

**Proposed replacement**:
```python
# Load API -> (EC, CHEBI) mapping
api_mapping = load_api_enzyme_substrate_mapping()

for entry in values:
    if isinstance(entry, dict):
        for test_abbrev, result in entry.items():
            if result in ["+", "-"] and test_abbrev in api_mapping:
                ec_number = api_mapping[test_abbrev]["enzyme"]
                substrate = api_mapping[test_abbrev]["substrate"]

                # Create EC node
                node_writer.writerow([ec_number, "biolink:MolecularActivity", ...])

                # Create organism -> capable_of -> EC edge
                edge_writer.writerow([
                    organism,
                    "biolink:capable_of",
                    ec_number,
                    "RO:0002215",  # capable_of
                    BACDIVE_PREFIX + key,
                    # evidence=result  (need column for this)
                ])

                if substrate:
                    # Create EC -> consumes -> CHEBI edge
                    edge_writer.writerow([
                        ec_number,
                        "biolink:consumes",
                        substrate,
                        "RO:0000057",
                        BACDIVE_PREFIX + key
                    ])
```

**Impact**:
- Remove 511 ad-hoc `assay:` nodes
- Add proper EC and CHEBI nodes
- Create substrate-enzyme-organism paths

**Estimated effort**:
- Medium - requires creating mapping file (could use literature + bioinformatics databases)
- Could start with subset (API 20E, API zym) and expand

---

### Priority 3: Capture Utilization Type Context (LOW EFFORT)

**Current**: `kind of utilization tested` field ignored

**Proposed**: Add as edge property or link to METPO process class

**Option A**: Edge property (simpler):
```python
# Add utilization_type column to edges
utilization_type = metabolite.get("kind of utilization tested", "")
edge_writer.writerow([
    organism, predicate, chebi_key, relation, provenance,
    # utilization_type  # New column
])
```

**Option B**: Link to METPO class (more semantic):
```python
if utilization_type == "fermentation":
    metpo_process = "METPO:1002005"  # Fermentation
elif utilization_type == "respiration":
    metpo_process = "METPO:1000800"  # respiration

if metpo_process:
    # Create additional edge: organism -> capable_of -> METPO process
    edge_writer.writerow([
        organism,
        "biolink:capable_of",
        metpo_process,
        "RO:0002215",
        provenance
    ])
```

**Recommendation**: Start with **Option A** (edge property), migrate to **Option B** after validating utility

---

### Priority 4: Handle Metabolites Without CHEBI IDs (MEDIUM EFFORT)

**Current**: Commented out code suggests this was attempted (lines 1432-1442, 1517-1522)

**Challenge**: Many metabolites lack CHEBI IDs in BacDive

**Options**:

**Option A**: Use OntoGPT/OAK NER to map metabolite names → CHEBI (like Madin transform does)
```python
from oaklib import get_adapter
chebi_adapter = get_adapter("sqlite:obo:chebi")

metabolite_name = metabolite.get("metabolite")
chebi_id = chebi_adapter.get_id_by_label(metabolite_name)
```

**Option B**: Create custom namespace for unmapped metabolites (discouraged - creates ad-hoc prefix!)

**Option C**: Skip them (current approach)

**Recommendation**: **Option A** - use NER mapping like Madin transform

**Estimated impact**: Could add thousands more metabolite edges for BacDive entries lacking CHEBI annotations

---

## Summary of Recommendations

| Priority | Action | Effort | Impact | METPO? | Ad-hoc prefix? |
|----------|--------|--------|--------|--------|----------------|
| **1** | Capture negative results | Low | +393K edges | ✅ No new terms needed | ✅ No |
| **2** | Replace assay nodes with EC numbers | Medium | Remove 511 ad-hoc nodes, add semantic links | ✅ No new terms needed | ✅ Removes `assay:` |
| **3** | Add utilization type context | Low | Richer semantics | ⚠️ Could use existing | ✅ No |
| **4** | Map metabolites without CHEBI | Medium | +1000s edges | ✅ No new terms needed | ✅ No |

**All recommendations avoid ad-hoc prefixes and use existing METPO/CHEBI/EC identifiers** ✅

---

## Edge Property Schema Proposal

**Current KGX schema** (5 columns):
```
subject | predicate | object | relation | primary_knowledge_source
```

**Proposed extended schema** (8 columns):
```
subject | predicate | object | relation | primary_knowledge_source | qualified_predicate | evidence | assay_type
```

**New columns**:
- `qualified_predicate`: String (for negation context)
- `evidence`: String (raw assay result: "+", "-", "yes", "no")
- `assay_type`: String (experimental method: "API 20E", "fermentation test", etc.)

**Alternative**: Use KGX edge property bags (JSON in additional columns) - need to check KGX spec

---

## Next Steps

### Immediate Actions (This Week)
1. ✅ Document current state and gaps (this file)
2. ⏭️ Create mapping file: `API_test_abbreviations_to_EC_CHEBI.yaml`
3. ⏭️ Prototype Priority 1: Modify metabolite utilization code to capture negatives

### Short-Term Actions (Next 2 Weeks)
4. ⏭️ Implement Priority 2: Replace `assay:` prefix with EC numbers
5. ⏭️ Test extended edge schema with additional properties
6. ⏭️ Regenerate BacDive transform and validate edge counts

### Medium-Term Actions (Next Month)
7. ⏭️ Implement Priority 3: Add utilization type context
8. ⏭️ Implement Priority 4: NER for metabolites without CHEBI
9. ⏭️ Document Biolink Association qualifier patterns for KG-M
10. ⏭️ Create coverage analysis: how many more microbe-chemical edges?

---

## Related Issues and Discussions

**Slack discussions** (need to search):
- Topics: enzyme activity representation, chemical interactions, assay data modeling
- Channels: #kg-microbe-ldrd, #metpo, #culturebot (check recent threads)

**GitHub Issues**:
- Issue #22: BacDive Ingestion Lifecycle Documentation

**Related Files**:
- Transform: `kg-microbe/kg_microbe/transform_utils/bacdive/bacdive.py`
- Config: `kg-microbe/kg_microbe/transform_utils/custom_curies.yaml`
- METPO: `metpo/src/templates/metpo_sheet.tsv`
- Output: `kg-microbe/data/transformed/bacdive/edges.tsv`

---

## Appendix: BacDive Metabolic Data Fields

**Complete list** from genson schema:

```
Physiology and metabolism:
  - API 20A, API 20E, API 20NE, API 20STR
  - API 50CHac, API 50CHas, API CAM
  - API ID32E, API ID32STA, API LIST
  - API NH, API STA, API coryne
  - API rID32A, API rID32STR, API zym
  - antibiogram
  - antibiotic resistance
  - compound production
  - enzymes  ← EC numbers
  - fatty acid profile
  - halophily
  - metabolite production  ← CHEBI + yes/no
  - metabolite tests
  - metabolite utilization  ← CHEBI + +/- + type
  - murein
  - nutrition type
  - observation
  - oxygen tolerance
  - spore formation
  - tolerance
```

**Fields currently processed**: metabolite utilization, metabolite production, enzymes, API tests, antibiotic resistance

**Fields not yet processed**: compound production, metabolite tests, fatty acid profile, tolerance (non-antibiotic)

**Opportunity**: Even more data to integrate in future iterations
