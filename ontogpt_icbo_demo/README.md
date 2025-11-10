# OntoGPT ICBO 2025 Demonstration

**Purpose**: Demonstrate METPO's strengths and weaknesses for grounding literature mining extractions in preparation for ICBO 2025 talk.

## Test Design

This demonstration uses OntoGPT to extract structured information from IJSEM abstracts, showing:
1. **What METPO can ground** - phenotypes within its domain
2. **What METPO cannot ground** - gaps in coverage or terminology mismatches
3. **How METPO properties work** - chemical interaction predicates (METPO:2000xxx)

### Two Extraction Scenarios

#### 1. Phenotype Extraction (`strain_phenotype_icbo.yaml`)

**Goal**: Extract strain-phenotype relationships as RDF triples

**Template design**:
- Subject: Strain (AUTO: identifier)
- Predicate: `has_phenotype`
- Object: Phenotype (METPO class)

**Expected METPO groundings** (based on handoff analysis):
- ✅ Cell shape: rod-shaped, coccus-shaped
- ✅ Gram staining: Gram-positive, Gram-negative
- ✅ Motility: motile, non-motile
- ✅ Oxygen: aerobic, anaerobic, facultative
- ✅ Temperature: mesophilic, thermophilic, psychrophilic
- ✅ pH: acidophilic, alkaliphilic, neutrophilic
- ✅ Salinity: halophilic

**Expected gaps** (potential weaknesses):
- ❓ "Gram-stain-negative" vs "Gram-negative" synonym mismatch
- ❓ Specific pigmentation colors (METPO has classes but may miss synonyms)
- ❓ Complex morphological descriptions
- ❓ Numeric ranges (temperature, pH, salinity values)

**Input abstracts**:
- `28879838` - Agarilytica: rod, Gram-negative, motile, aerobic, halophilic, yellow pigment
- `37170873` - Halomonas: rod, Gram-negative, motile, halophilic, alkaliphilic
- `19622650` - Methylovirgula: rod, Gram-negative, non-motile, aerobic, acidophilic, mesophilic

#### 2. Chemical Utilization Extraction (`chemical_utilization_icbo.yaml`)

**Goal**: Extract strain-chemical relationships using METPO object properties

**Template design**:
- Subject: Strain
- Predicate: METPO property (e.g., `METPO:2000006` = uses_as_carbon_source)
- Object: Chemical compound (ChEBI)

**Expected METPO property uses**:
- ✅ `uses_for_growth` (METPO:2000012)
- ✅ `uses_as_carbon_source` (METPO:2000006)
- ✅ `oxidizes` (METPO:2000016)
- ✅ `degrades` (METPO:2000007)
- ✅ `requires_for_growth` (METPO:2000018)

**Expected ChEBI groundings**:
- ✅ methanol, ethanol, pyruvate, malate
- ✅ formaldehyde, acetaldehyde
- ❓ lanthanides (La³⁺, Y³⁺) - may be outside ChEBI's microbiology coverage

**Input abstracts**:
- `19622650` - Methylovirgula: methanol, ethanol, pyruvate, malate utilization
- `27573017` - M. extorquens AM1: ethanol, methanol, formaldehyde, acetaldehyde, lanthanide-dependent metabolism

## Running the Tests

### Prerequisites

```bash
# Ensure OntoGPT is installed
uv run ontogpt --version

# Ensure OpenAI API key is set
echo $OPENAI_API_KEY
echo $OPENAI_API_BASE
```

### Quick Start

```bash
# Run all extractions with default settings
make

# Run phenotype extractions only
make phenotypes

# Run chemical utilization extractions only
make chemicals

# Analyze METPO grounding in outputs
make analyze

# Clean up outputs
make clean
```

### Custom Settings

```bash
# Use a different model
make MODEL=gpt-4o-mini

# Adjust temperature
make TEMPERATURE=0.5

# Run specific extraction
make outputs/28879838-phenotype.yaml
```

## Expected Output Files

```
outputs/
├── 28879838-phenotype.yaml      # Agarilytica phenotypes
├── 37170873-phenotype.yaml      # Halomonas phenotypes
├── 19622650-phenotype.yaml      # Methylovirgula phenotypes
├── 19622650-chemical.yaml       # Methylovirgula chemical utilization
└── 27573017-chemical.yaml       # M. extorquens chemical utilization
```

## Analysis Strategy

### 1. Automated Analysis

```bash
make analyze
```

Counts:
- METPO URIs found (`w3id.org/metpo/`)
- AUTO terms (failed groundings)
- ChEBI groundings

### 2. Manual Analysis

For each output file, examine:

**Phenotype extraction**:
```bash
# Find METPO groundings
grep "w3id.org/metpo/" outputs/*-phenotype.yaml

# Find failed groundings
grep "AUTO:" outputs/*-phenotype.yaml

# Extract unique METPO classes
grep -oh "w3id.org/metpo/[0-9]*" outputs/*-phenotype.yaml | sort -u
```

**Chemical utilization**:
```bash
# Find METPO properties used
grep "METPO:2000" outputs/*-chemical.yaml

# Find ChEBI groundings
grep "CHEBI:" outputs/*-chemical.yaml

# Check predicate distribution
grep "predicate:" outputs/*-chemical.yaml | sort | uniq -c
```

### 3. Quality Assessment

**Success criteria**:
- ✅ Major phenotypes grounded (rod-shaped, Gram-negative, aerobic, mesophilic)
- ✅ METPO properties correctly selected for chemical interactions
- ✅ Consistent strain identifiers across relationships

**Document failures**:
- ❌ Synonym mismatches (e.g., "Gram-stain-negative" → AUTO:)
- ❌ Missing METPO classes for described phenotypes
- ❌ Incorrect predicate selection
- ❌ ChEBI grounding failures

## Version Control Strategy

### Commit Frequency

**Option 1: Milestone commits** (recommended for ICBO demo)
- Initial setup: templates, Makefile, README, inputs
- First extraction run: all outputs with default settings
- Template refinement: after analyzing first results
- Final extraction: optimized templates
- Analysis documentation: findings and interpretation

**Option 2: Incremental commits**
- Each extraction run (tag with model + temperature)
- Each template modification
- Each analysis script or finding

### Commit Message Format

```
ontogpt_icbo: <action> - <description>

Examples:
- ontogpt_icbo: initial setup - templates, inputs, Makefile
- ontogpt_icbo: extraction run - gpt-4o temp=0.0 default settings
- ontogpt_icbo: analysis - METPO grounding results documented
- ontogpt_icbo: template fix - add Gram-stain-negative synonym prompt
```

### What to Commit

**Always commit**:
- ✅ Templates (`templates/*.yaml`)
- ✅ Input abstracts (`inputs/*.txt`)
- ✅ Makefile
- ✅ README and documentation
- ✅ Analysis scripts and results
- ✅ Key output files showing strengths/weaknesses

**Optionally commit** (depending on size/importance):
- ⚠️ All extraction outputs (can be large)
- ⚠️ Intermediate experiments

**Never commit**:
- ❌ API keys or credentials
- ❌ Temporary files
- ❌ Cache directories

### Branching Strategy

Since this is for ICBO 2025 talk prep:
- Main branch: `main` or current working branch
- Optional: `icbo-2025-ontogpt-demo` feature branch
- Tag final results: `icbo-2025-demo-v1`

## Test Expectations

### Hypothesis

**METPO should perform well for**:
1. Core morphological phenotypes (shape, Gram stain, motility)
2. Basic growth requirements (oxygen, temperature, pH, salinity)
3. Chemical interaction predicates (has comprehensive METPO:2000xxx properties)

**METPO may struggle with**:
1. Synonym variations ("Gram-stain-negative" vs "Gram-negative")
2. Numeric values (specific temperatures, pH values, salinity percentages)
3. Complex descriptions requiring inference
4. Edge cases outside curated databases (BacDive, BactoTraits, Madin)

### Comparison to Previous Results

From `SESSION_HANDOFF_2025-11-06.md`:
- Previous morphology extraction: 22 METPO URIs (gpt-4o, Oct 30)
- Previous growth conditions: 20 METPO URIs (gpt-4o, Oct 30)
- **Key learning**: Must search for URI format `w3id.org/metpo/` not CURIE `METPO:`

### Success Metrics

**Quantitative**:
- METPO grounding rate: >50% for in-domain phenotypes
- Synonym match rate: track AUTO: terms for synonym analysis
- Predicate accuracy: correct METPO properties selected (manual review)

**Qualitative**:
- Can demonstrate both strengths and weaknesses
- Results are reproducible
- Findings inform ICBO talk narrative

## ICBO Talk Integration

### Key Messages

1. **METPO works when configured correctly**
   - Show successful groundings from this demo
   - 8 classes grounded in previous work, expect similar here

2. **Template design is critical**
   - Must include METPO annotators
   - Must use correct ontology references

3. **Synonym coverage matters**
   - Show "Gram-stain-negative" → AUTO: example
   - Opportunity to add synonyms to METPO

4. **Structured data alignment remains strongest use case**
   - 269 synonyms curated from BacDive, BactoTraits, Madin
   - Literature mining complements but doesn't replace structured data

### Slide Examples

**Success slide**:
- Show phenotype extraction with METPO groundings
- Highlight: rod-shaped → METPO:1000681, aerobic → METPO:1000602

**Challenge slide**:
- Show synonym mismatch: "Gram-stain-negative" → AUTO:
- Show missing class: specific pigment color

**Solution slide**:
- Adding synonyms to METPO
- Hybrid approach: combine structured + literature mining

## Files in This Directory

```
ontogpt_icbo_demo/
├── README.md                          # This file
├── Makefile                           # Automation
├── inputs/                            # Input abstracts
│   ├── 19622650-abstract.txt         # Methylovirgula (phenotype + chemical)
│   ├── 27573017-abstract.txt         # M. extorquens (chemical)
│   ├── 28879838-abstract.txt         # Agarilytica (phenotype)
│   └── 37170873-abstract.txt         # Halomonas (phenotype)
├── outputs/                           # Extraction results (created by make)
├── templates/                         # OntoGPT templates
│   ├── strain_phenotype_icbo.yaml    # Phenotype extraction
│   └── chemical_utilization_icbo.yaml # Chemical utilization
└── metpo_phenotype_classes.rq        # SPARQL query for METPO classes
```

## Next Steps

1. Run initial extractions: `make`
2. Analyze results: `make analyze`
3. Document findings in new file: `RESULTS.md`
4. Identify synonym gaps and template improvements
5. Optionally re-run with refined templates
6. Create slide examples for ICBO talk

## References

- Session handoff: `../literature_mining/SESSION_HANDOFF_2025-11-06.md`
- Previous templates: `../literature_mining/templates/`
- METPO ontology: `../src/ontology/metpo.owl`
- METPO template sheet: `../src/templates/metpo_sheet.tsv`
