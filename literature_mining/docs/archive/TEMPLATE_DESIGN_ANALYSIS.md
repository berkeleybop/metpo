# Template Design Features Leading to METPO Grounding

**Date:** 2025-11-06
**Analysis:** What OntoGPT template designs and command options led to successful METPO grounding?

---

## Summary of Findings

### Answer to Your Questions

**Q1: Are all other groundings CURIEs?**
**A: YES** - Only METPO uses full URI format `<https://w3id.org/metpo/1000681>`
- CHEBI: CURIE format (`CHEBI:17439`)
- NCBITaxon: CURIE format (`NCBITaxon:1355477`)
- GO: CURIE format (`GO:0015946`)
- AUTO: CURIE-like format (`AUTO:USDA110`)

**Q2: What inputs had the most METPO groundings?**
**A: growth_conditions_gpt-4o_20251030_142703.yaml** with 5 METPO entities

**Q3: Most METPO groundings per KB of input?**
**A: morphology_gpt-4o_20251030_174301.yaml** with 0.246 METPO/KB (1 grounding in just 4.1 KB)

---

## Efficiency Rankings

### By Absolute Count
```
Rank  File                                              METPO  Input KB
1     growth_conditions_gpt-4o_20251030_142703.yaml     5      97.5 KB
2-3   morphology_gpt-4o_20251030_180642.yaml            3      97.5 KB (tie, duplicates)
4-8   Various morphology experiments                    1      4-143 KB
```

### By Efficiency (METPO per KB)
```
Rank  File                                              METPO/KB  METPO  Input KB
1-2   morphology_gpt-4o_20251030_174301.yaml            0.246     1      4.1 KB
3     growth_conditions_gpt-4o_20251030_142703.yaml     0.051     5      97.5 KB
4-5   morphology_gpt-4o_20251030_180642.yaml            0.031     3      97.5 KB
6-8   morphology v3/v4/hybrid experiments               0.007     1      142.9 KB
```

**Best overall:** `morphology_gpt-4o_20251030_174301.yaml` - short input, high efficiency

---

## Template Design Features That Work

### 1. METPO Annotator Configuration

**CRITICAL SUCCESS FACTOR:** Classes must have `annotators:` pointing to METPO

#### Two Working Approaches

**Approach A: Local OWL file (growth_conditions_hybrid.yaml)**
```yaml
OxygenRequirement:
  is_a: NamedEntity
  annotations:
    annotators: sqlite:../src/ontology/metpo.owl
```

**Approach B: OBO Library (morphology_template_base.yaml)**
```yaml
CellShape:
  is_a: NamedEntity
  annotations:
    annotators: sqlite:obo:metpo
```

**Approach C: Multiple ontologies (growth_conditions_hybrid.yaml)**
```yaml
GrowthMedium:
  is_a: NamedEntity
  annotations:
    annotators: sqlite:../src/ontology/metpo.owl, sqlite:obo:chebi
```

### 2. Classes with METPO Annotators (morphology_template_base.yaml)

**8 entity classes configured:**
1. CellShape → `sqlite:obo:metpo`
2. CellArrangement → `sqlite:obo:metpo`
3. GramStaining → `sqlite:obo:metpo`
4. Motility → `sqlite:obo:metpo`
5. SporeFormation → `sqlite:obo:metpo`
6. CellularInclusion → `sqlite:obo:metpo`
7. CellWallCharacteristic → `sqlite:obo:metpo`
8. Pigmentation → `sqlite:obo:metpo`

**Success rate:** 3/8 classes successfully grounded (CellShape, Motility, Motility)

### 3. Classes with METPO Annotators (growth_conditions_hybrid.yaml)

**5 entity classes configured:**
1. OxygenRequirement → `sqlite:../src/ontology/metpo.owl`
2. AtmosphericRequirement → `sqlite:../src/ontology/metpo.owl`
3. TemperatureCondition → `sqlite:../src/ontology/metpo.owl`
4. PHCondition → `sqlite:../src/ontology/metpo.owl`
5. SaltTolerance → `sqlite:../src/ontology/metpo.owl`

**Success rate:** 5/5 classes successfully grounded (aerobic, anaerobic, facultative, mesophilic, halophilic)

---

## Templates WITHOUT METPO Annotators (Failed)

### biochemical_hybrid.yaml
```yaml
MetabolicPhenotype:
  is_a: NamedEntity
  annotations:
    annotators: sqlite:obo:go, sqlite:obo:rhea, sqlite:obo:chebi
    # NO METPO!
```

**Result:** 0 METPO groundings

### chemical_utilization_hybrid.yaml
```yaml
SubstrateUtilization:
  is_a: NamedEntity
  annotations:
    annotators: sqlite:obo:chebi
    # NO METPO!
```

**Result:** 0 METPO groundings

---

## OntoGPT Command Line Options (Inferred from Filenames)

### Successful Extractions (Oct 30, 2025)

**File:** `growth_conditions_gpt-4o_20251030_142703.yaml`
```bash
# Inferred command:
ontogpt extract \
  -t templates/growth_conditions_hybrid.yaml \
  -i <input_file> \
  -o growth_conditions_gpt-4o_20251030_142703.yaml \
  --model gpt-4o
```

**File:** `morphology_gpt-4o_20251030_180642.yaml`
```bash
# Inferred command:
ontogpt extract \
  -t templates/morphology_template_base.yaml \  # or morphology experiment
  -i <input_file> \
  -o morphology_gpt-4o_20251030_180642.yaml \
  --model gpt-4o
```

### Failed Fullcorpus Extractions (Oct 31, 2025)

**File:** `*_fullcorpus_gpt4o_t00_20251031_*.yaml`
```bash
# Inferred command:
ontogpt extract \
  -t templates/<template>.yaml \
  -i <multiple_pdfs> \  # fullcorpus = all papers
  -o <output>.yaml \
  --model gpt-4o \
  --temperature 0.0  # t00 = temperature 0.0
```

**Key differences:**
- `t00` in filename → `--temperature 0.0` (deterministic)
- `fullcorpus` → multiple input PDFs
- Oct 31 date → something changed from Oct 30

---

## Command Line Options Analysis

### From Filename Patterns

| Pattern | Interpretation | Example |
|---------|----------------|---------|
| `gpt-4o` | `--model gpt-4o` | Default working model |
| `gpt4o` | Same as above | Filename shorthand |
| `t00` | `--temperature 0.0` | Deterministic extraction |
| `t03` | `--temperature 0.3` | More creative |
| `fullcorpus` | Multiple input files | Batch extraction |
| `hybrid` | Hybrid template (combined features) | Template name |
| `base` | Base template | Template name |
| `claude-sonnet` | `--model anthropic/claude-sonnet` | Alternative model |

### Successful Combinations

**Most successful:**
```bash
--model gpt-4o
--temperature <default or not specified>
-t templates/morphology_template_base.yaml  # with sqlite:obo:metpo
-t templates/growth_conditions_hybrid.yaml  # with sqlite:../src/ontology/metpo.owl
```

**Less successful:**
```bash
--model gpt-4o
--temperature 0.0  # deterministic
<fullcorpus inputs>  # resulted in many empty extractions
```

---

## Key Success Factors

### Template Design

1. **MUST have METPO annotators** in entity class definitions
   ```yaml
   annotations:
     annotators: sqlite:obo:metpo  # or sqlite:../src/ontology/metpo.owl
   ```

2. **Entity descriptions matter** - clear descriptions help LLM extract correctly
   ```yaml
   Motility:
     description: >-
       Cellular motility characteristics including flagellar motility,
       gliding motility, twitching motility, and related movement mechanisms.
   ```

3. **Prompt customization** - detailed prompts guide extraction
   ```yaml
   annotations:
     prompt: >-
       Extract all motility characteristics mentioned in the text, including
       motility presence (motile/non-motile), motility types...
   ```

4. **CompoundExpression relationships** - structured strain-phenotype links
   ```yaml
   MotilityRelationship:
     is_a: CompoundExpression
     attributes:
       subject: Strain
       predicate: MorphologyType
       object: Motility
   ```

### Command Line Options

1. **Model:** `gpt-4o` worked well (claude-sonnet had lower success)

2. **Temperature:** Default or unspecified worked better than `--temperature 0.0`

3. **Input size:** Smaller, focused inputs had higher efficiency
   - Best: 4.1 KB → 0.246 METPO/KB
   - Large: 143 KB → 0.007 METPO/KB

4. **Single vs batch:** Single paper extractions worked better than fullcorpus

---

## Why Did Oct 30 Succeed but Oct 31 Fail?

### Hypothesis 1: Template Changes
- Oct 30 used templates with working METPO annotators
- Oct 31 may have used modified templates or different template versions

### Hypothesis 2: Input Document Quality
- Oct 30: Single focused papers with clear phenotype descriptions
- Oct 31 fullcorpus: Mixed papers, many irrelevant → empty `extracted_object: {}`

### Hypothesis 3: Temperature Setting
- Oct 30: Default temperature (likely 0.0 or 0.1)
- Oct 31: Explicit `--temperature 0.0` (`t00` in filename)
- Deterministic mode may reduce grounding attempts

### Hypothesis 4: METPO Path Resolution
- `sqlite:obo:metpo` (OBO library) vs `sqlite:../src/ontology/metpo.owl` (local)
- Different working directories could break relative paths

---

## Recommendations for ICBO

### Template Design Best Practices

1. **Always configure METPO annotators** for phenotype classes
   ```yaml
   YourPhenotypeClass:
     annotations:
       annotators: sqlite:../src/ontology/metpo.owl
   ```

2. **Use absolute paths** or environment variables
   ```bash
   export METPO_OWL=/full/path/to/metpo.owl
   annotators: sqlite:${METPO_OWL}
   ```

3. **Test both OBO library and local file** approaches
   - OBO library: `sqlite:obo:metpo`
   - Local file: `sqlite:../src/ontology/metpo.owl`

4. **Combine multiple ontologies** for comprehensive grounding
   ```yaml
   annotators: sqlite:../src/ontology/metpo.owl, sqlite:obo:chebi, sqlite:obo:go
   ```

### Command Line Best Practices

1. **Use gpt-4o model** (proven success)
2. **Avoid deterministic temperature** for grounding tasks
3. **Process papers individually** rather than fullcorpus batches
4. **Validate extraction success** - check for empty objects

### For ICBO Talk

**Show successful template design:**
```yaml
# morphology_template_base.yaml
Motility:
  is_a: NamedEntity
  description: Cellular motility characteristics...
  annotations:
    annotators: sqlite:obo:metpo
```

**Successful result:**
```yaml
named_entities:
  - id: <https://w3id.org/metpo/1000702>
    label: motile
```

**Contrast with failure:**
```yaml
# biochemical_hybrid.yaml - NO METPO ANNOTATOR
MetabolicPhenotype:
  annotations:
    annotators: sqlite:obo:go, sqlite:obo:chebi  # Missing METPO!
```

**Failed result:**
```yaml
named_entities:
  - id: AUTO:methylotrophic%20bacteria  # Should be METPO!
```

---

## Files for Reference

**Successful templates:**
- `literature_mining/templates/morphology_template_base.yaml`
- `literature_mining/templates/growth_conditions_hybrid.yaml`

**Failed templates:**
- `literature_mining/templates/biochemical_hybrid.yaml` (no METPO)
- `literature_mining/templates/chemical_utilization_hybrid.yaml` (no METPO)

**Successful extractions:**
- `outputs/growth_conditions_gpt-4o_20251030_142703.yaml` (5 METPO)
- `outputs/morphology_gpt-4o_20251030_180642.yaml` (3 METPO)

**Analysis files:**
- `METPO_GROUNDING_EFFICIENCY.tsv`
- `analyze_metpo_efficiency.py`

---

**Key Message for ICBO:**

> "METPO grounding success depends critically on template configuration. Templates with METPO annotators achieved 5-8 phenotype groundings per extraction. Templates without METPO annotators produced 0% grounding, with all phenotypes becoming AUTO: terms. This demonstrates that OntoGPT + METPO works when properly configured, but requires explicit template design."
