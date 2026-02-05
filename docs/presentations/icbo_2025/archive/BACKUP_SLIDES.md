# METPO ICBO 2025 - Backup Slides

**For:** Questions, clarifications, and deep-dive technical content
**Date:** 2025-11-11

---

## Backup Slide 1: KG-Microbe Integration Statistics

### Three Primary Phenotype Data Sources

**Integrated into KG-Microbe knowledge graph:**

| Source | Nodes | Edges | Coverage |
|--------|-------|-------|----------|
| **BactoTraits** | 10,027 | 90,769 | Database curation |
| **Madin et al.** | 122,496 | 115,398 | Literature mining |
| **BacDive** | 196,169 | 1,656,668 | API integration |
| **TOTAL** | **~328K** | **~1.86M** | **All observation-based** |

**Key point:** All data from direct observations, NOT genome annotations
**Integration:** METPO provides semantic layer for cross-dataset queries

---

## Backup Slide 2: Low Exact Match Problem

### Why Embeddings Alone Are Insufficient

**From 3,019 total SSSOM mappings:**

```
Match Quality Distribution:
├── exactMatch:     42 terms (19.6%, avg similarity 1.0)  ← ONLY 2%!
├── closeMatch:     29 terms (13.6%, avg similarity 0.845)
├── relatedMatch:   28 terms (13.1%, avg similarity 0.693)
└── other/broad:   115 terms (53.7%, avg similarity 0.422) ← POOR QUALITY
```

**Problem:** 
- Only **19.6% exact matches** via embeddings
- **53.7% low-quality matches** (similarity < 0.5)
- Mean similarity: 0.6280 (median 0.6317)

**Solution:** METPO provides precise, pre-coordinated phenotype classes

---

## Backup Slide 3: The Import Problem - Multiple Hierarchies

### Why We Can't Just Import All Ontologies

**When attempting to import established ontologies:**

1. **Conflicting hierarchies**
   - GO says: `molecular_function ⊑ process`
   - CHEBI says: `molecular_function ⊑ role`
   - Result: **60 unsatisfiable classes** when importing MicrO

2. **Property punning violations**
   - 477 violations in MicrO alone
   - Breaks OWL 2 DL reasoners

3. **Database size explosion**
   - MicrO alone: 22,205 classes → 197MB semsql
   - UPHENO: 192,001 embeddings
   - CHEBI: 221,776 embeddings
   - Total tested: 778,496 embeddings (39 ontologies)

4. **No single hierarchy** for aerobe/anaerobe/facultative concepts
   - Needed for ML classification
   - Different environments require consistent modeling

**METPO approach:** 255 focused classes + 3,019 mappings for interoperability

---

## Backup Slide 4: Aerobe vs. Anaerobe - ML Requirements

### Why Hierarchy Matters for Machine Learning

**Problem:** Machine learning needs consistent parent-child relationships

**Example:** Oxygen tolerance phenotypes

```
METPO hierarchy (pre-coordinated):
oxygen preference
├── aerobic
│   ├── obligately aerobic
│   ├── facultatively aerobic
│   └── microaerophilic
└── anaerobic
    ├── obligately anaerobic
    ├── facultatively anaerobic  [also under aerobic]
    └── aerotolerant

```

**ML Requirements:**
1. **Clear partitions:** aerobic vs. anaerobic environments
2. **Qualifiers pre-composed:** "facultatively" built into class, not separate
3. **Single hierarchy:** No conflicting parent relationships
4. **Consistent:** Same modeling across all phenotype axes

**Question addressed:** Do we have qualifier classes?
**Answer:** No. All classes are fully pre-composed (e.g., "facultatively aerobic" is ONE class, not "facultative" + "aerobic")

---

## Backup Slide 5: Contrast with KG-Microbe Publication (Figure 3)

### Our Approach vs. Published KG-Microbe

**KG-Microbe Publication (Mungall et al.):**
- Focus: Knowledge graph construction
- Integration: BactoTraits, Madin, BacDive
- Ontology: Used existing ontologies as-is

**Our METPO Extension:**
1. **Semantic harmonization layer** on top of KG-Microbe
2. **Three sources integrated** with METPO mappings
3. **Cross-dataset queries enabled:** "all mesophiles" across BactoTraits/Madin/BacDive
4. **Quality-assessed mappings:** 182 excellent matches (≥0.75 similarity)
5. **Observation-based only:** No genome predictions

**Key difference:** We add the semantic layer that makes cross-dataset integration practical

---

## Backup Slide 6: Ontology Weaknesses - Beyond Revision Dates

### Gap in Ontology Landscape - Technical Problems

**MicrO (22,205 classes, last updated 2018):**
- ✗ **21% grounding rate** vs. METPO's 26% in fair comparison
- ✗ **60 unsatisfiable classes** when imported with METPO
- ✗ **477 OWL 2 DL violations** (property punning)
- ✗ **Cannot ground:** motile, non-motile, methylotroph, methanotroph
- ✗ **ROBOT report:** 7,130 violations (103 errors, 4,446 warnings)
- ✗ **Semsql build fails:** Cannot be auto-converted by OBO Foundry pipeline
- ✗ **Missing labels:** 62 imported terms lack labels

**MPO (via BioPortal, not in OLS):**
- ✗ **Strong embeddings but useless definitions**
  - Example: "Thermophilic; Thermophile" (just label repetition)
  - Only **2.8% definition coverage**
- ✗ **974 mappings found** but definitions don't follow genus-differentia
- ✗ **Not in OLS:** BioPortal only, complicates tooling

**PATO (general phenotypes):**
- ✓ High quality definitions BUT
- ✗ Too general: "a quality inhering in a bearer"
- ✗ Misses microbial-specific semantics

---

## Backup Slide 7: AI Usage in METPO Development

### Where and How AI Was Applied

**1. Literature Mining (OntoGPT)**
- **Tool:** GPT-4o via OntoGPT framework
- **Task:** Extract phenotypes from species descriptions
- **Example:** 19622650 (*Methylovirgula ligni*) → 12 phenotype extractions
- **Grounding:** To METPO ontology URIs via semantic similarity

**2. Definition Quality Assessment**
- **Tool:** Claude 3.5 Sonnet via CBORG (LBL's OpenAI API endpoint)
- **Task:** Evaluate definitions against Seppälä-Ruttenberg-Smith guidelines
- **Result:** Flagged low-quality definitions (e.g., MPO label repetition)
- **Workflow:** `docs/DEFINITION_ENRICHMENT_WORKFLOW.md`

**3. Definition Proposal (LLM-assisted)**
- **Tool:** Claude/GPT-4 for initial drafts
- **Human review:** All 255 definitions manually validated
- **Guidelines:** OBO Foundry genus-differentia principles
- **Key finding:** Only **15.6%** of matched foreign definitions properly follow guidelines

**NOT used for:**
- Ontology class hierarchy design (human-curated)
- Final definition text (human-approved)
- Mapping validation (embedding + human review)

---

## Backup Slide 8: Definition Enrichment Results

### Systematic Definition Quality Analysis

**Goal:** Find high-quality definitions for all 255 METPO terms

**Method:** OBO Foundry Seppälä-Ruttenberg-Smith guidelines
- Genus-differentia form: "A [parent class] that [differentiating property]"
- No circularity, no examples, no generalizations

**Results:**

| Analysis Phase | Result |
|----------------|--------|
| **Foreign ontology candidates** | 128/255 terms (50.2%) have matches |
| **Quality-filtered candidates** | 19 candidates, 7 excellent quality |
| **Following guidelines properly** | Only **15.6%** in METPO hierarchy context |
| **LLM-proposed definitions** | Generated for all 255 terms |
| **Human validation** | All definitions manually reviewed |

**Key Problems with Foreign Definitions:**
1. MPO: Label repetition ("Thermophilic; Thermophile")
2. MicrO: Too assay-focused ("grows at 37°C" vs. "mesophilic")
3. PATO: Too general ("a quality inhering in a bearer")

**METPO solution:** Custom definitions following OBO Foundry guidelines with microbial-specific semantics

---

## Backup Slide 9: Grounding Rate Context

### What "21% Grounding Rate" Actually Means

**Experiment Setup:**
- **Tool:** OntoGPT with GPT-4o
- **Input:** 2 ICBO example abstracts (species descriptions)
- **Task:** Extract phenotypes and ground to ontology
- **Comparison:** Same abstracts, same LLM, different ontology annotators

**Fair Comparison Results:**

| Ontology | Total Extractions | Successfully Grounded | Grounding Rate |
|----------|------------------|----------------------|----------------|
| **METPO** | 294 | 79 URIs | **26%** |
| **MicrO** | 297 | 63 URIs | **21%** |
| **OMP** | 38 | 33 URIs | **87%** (but only 38 extracted) |
| **PATO** | 22 | 11 URIs | **50%** (but only 22 extracted) |

**Context matters:**
- "21%" = Percentage of extracted phenotype mentions that could be mapped to MicrO URIs
- Lower rate despite MicrO having 22,205 classes vs. METPO's 255 classes
- **Critical gaps:** MicrO cannot ground: motile, non-motile, methylotroph, methanotroph

**Full details:** `literature_mining/MICRO_PROBLEMS_ANALYSIS.md`

---

## Backup Slide 10: Why MicrO Is Hard to Convert to Semsql

### Technical Barriers to Automation

**Semsql = SQL database format for OBO ontologies (OBO Foundry standard)**

**MicrO conversion problems:**

1. **Missing labels for imports**
   - 62 imported terms lack rdfs:label
   - Semsql requires labels for all entities
   - Source: ROBOT report `missing_label` violations

2. **Property punning violations**
   - 477 violations where same URI used as both ObjectProperty and AnnotationProperty
   - Violates OWL 2 DL semantics
   - Semsql generator assumes DL compliance

3. **Unsatisfiable classes**
   - 2 classes unsatisfiable in standalone MicrO
   - 60 classes become unsatisfiable with standard imports (GO, CHEBI, PATO)
   - Reasoner fails during semsql build

4. **OBO Foundry auto-build fails**
   ```bash
   sqlite:obo:micro  # Returns 0-byte file
   ```

**METPO:** 
- ✓ Zero ROBOT errors
- ✓ OWL 2 DL compliant
- ✓ Semsql builds automatically
- ✓ All imports compatible

---

## Backup Slide 11: ROBOT Report Issues

### What ROBOT Found Wrong with MicrO

**Command:** `robot report --input micro.owl --fail-on none`

**7,130 total violations:**

| Violation Type | Count | Impact |
|---------------|-------|--------|
| **missing_label** | 62 | Imported terms unusable without labels |
| **duplicate_label** | Multiple | `MICRO:0000206`/`0000207` same label |
| **property_punning** | 477 | OWL 2 DL non-compliant |
| **invalid_xref** | Many | Broken cross-references |
| **missing_definition** | Many | Only assay descriptions, not phenotypes |

**OWL 2 DL Profile Check:**
```bash
robot validate-profile --profile DL --input micro.owl
Result: FAIL - 477 punning violations
```

**Reasoning Test:**
```bash
robot reason --input micro.owl --reasoner ELK
Result: 2 unsatisfiable classes (60 when imported with METPO)
```

**METPO comparison:**
- ✓ 0 errors, 0 warnings from ROBOT
- ✓ OWL 2 DL compliant
- ✓ All classes satisfiable
- ✓ Clean imports

---

## Backup Slide 12: Integration vs. Other Approaches

### Our Semantic Integration Strategy

**Key term:** Integration (not just collection)

**Traditional approach:**
1. Collect data from sources
2. Store in separate silos
3. Manual cross-referencing

**METPO integration approach:**
1. **Semantic harmonization:** Common vocabulary via METPO classes
2. **SSSOM mappings:** 3,019 mappings to 35+ ontologies
3. **Cross-dataset queries:** "Find all mesophiles" works across all 3 sources
4. **Quality-assessed:** 182 excellent matches (≥0.75 similarity)
5. **Observation-based:** All from direct measurements, not predictions

**KG-Microbe + METPO:**
- **328K nodes, 1.86M edges** from integrated sources
- **255 METPO classes** provide semantic layer
- **Enables queries** that span BactoTraits/Madin/BacDive
- **Machine learning ready:** Consistent hierarchies for classification

---

## Backup Slide 13: Acknowledgments

### Funding and Collaborations

**Funding:**
- **DOE Systems Biology Knowledgebase (KBase)**
  - Award: DE-AC02-05CH11231
  - Program Manager: Chris Mungall
  - Program Manager Support: Nomi Harris
- **Lawrence Berkeley National Laboratory (LBNL)**
  - Environmental Genomics and Systems Biology Division
  
**Collaborations:**
- **KG-Microbe Team** (Chris Mungall, Marcin Joachimiak, et al.)
- **OBO Foundry Community** (ontology best practices)
- **NMDC Team** (data integration standards)

**Infrastructure:**
- **CBORG** (LBNL's OpenAI API endpoint for LLM access)
- **OntoGPT** (Chris Mungall, Berkeley Biosciences)
- **ROBOT** (OBO Foundry tool suite)

**Special Thanks:**
- Marcin Joachimiak (KG-Microbe, technical review)
- Chris Mungall (KBase, ontology guidance)
- Nomi Harris (program management)

---
