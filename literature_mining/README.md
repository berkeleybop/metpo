# Literature Mining and Fact Extraction System

A comprehensive OntoGPT-based pipeline for extracting structured bacterial characteristics from scientific literature, with specialized templates for growth conditions, chemical utilization, morphology, biochemical properties, and taxonomic information.

## Quick Start

### Prerequisites
- UV package manager (replaces Poetry)
- Access to PubMed abstracts via `artl-cli`
- OntoGPT with LLM API access (OpenAI, Anthropic Claude, etc.)

### Basic Usage

```bash
# Setup environment
uv sync --extra dev

# Create directory structure
make setup

# Build templates with METPO predicates
make build-templates

# Run quick test (10 abstracts)
make quick-test TEMPLATE=growth_conditions

# Full extraction pipeline
make extract-all SOURCE=ijsem TEMPLATE=growth_conditions N_ABSTRACTS=50

# Assessment and analysis
make assess-templates
make unified-assessment
make domain-grounding-analysis
```

## System Architecture

### Data Sources and ID Management

**Primary ID Sources:**
- **Names for Life (N4L)**: 23,535 references, 18,636 with valid PMIDs
- **BacDive database**: Strains with Pubmed links
- **EuropePMC**: IJSEM articles collection

**Abstract Fetching:** Uses `artl-cli get-abstract-from-pubmed-id` for reliable PubMed access.

### Template System

**Five Specialized Templates** (focused approach beats comprehensive):

1. **Taxa Template** (`taxa_template.yaml`)
   - PMID + taxonomic information only
   - 100% field specificity, 92.8% exclusivity

2. **Growth Conditions Template** (`growth_conditions_template.yaml`)  
   - Media, temperature, pH, oxygen, salt, chemical requirements
   - Normalized units: "25-30°C", "pH 6.8-7.0", "up to 4% NaCl"
   - 100% field specificity, 93.9% exclusivity

3. **Chemical Utilization Template** (`chemical_utilization_template.yaml`)
   - 60+ METPO predicates dynamically injected via SPARQL
   - ChEBI grounding for chemical compounds
   - Examples: `uses_as_carbon_source`, `ferments`, `hydrolyzes`
   - 100% field specificity, 98.0% exclusivity

4. **Morphology Template** (`morphology_template.yaml`)
   - Cell shape, Gram staining, motility, spore formation
   - METPO/PATO grounding for morphological terms
   - 87.5% field specificity, 91.1% exclusivity

5. **Biochemical Template** (`biochemical_template.yaml`)
   - Enzyme activities, fatty acid profiles, API test results
   - 100% field specificity, 93.1% exclusivity

### Directory Structure

```
literature_mining/
├── inputs/           # PMID sources and reference data
├── intermediates/    # Generated TSV, YAML, DB files
├── templates/        # Base and populated templates
├── abstracts/        # Fetched abstracts (preserved)
├── outputs/          # Final extractions (preserved)
├── assessments/      # Analysis results
├── cache/           # LLM response cache
├── logs/            # Processing logs
└── sparql/          # SPARQL queries for METPO integration
```

## Assessment and Quality Control

### Assessment Tools

**Three Core Assessment Scripts:**

1. **Template Quality Assessment** (no extractions needed)
   ```bash
   make assess-templates
   # Uses: template_quality_assessor.py
   # Assesses: Template structure, coverage, relationship density
   ```

2. **Unified Pipeline Assessment** (comprehensive analysis)
   ```bash
   make unified-assessment
   # Uses: unified_assessment.py
   # Assesses: Raw LLM → parsing → grounding → relationships
   ```

3. **Domain-Specific Grounding Analysis** (ontology focus)
   ```bash
   make domain-grounding-analysis  
   # Uses: domain_grounding_analysis.py
   # Assesses: Fatty acids→CHEBI, enzymes→GO, taxa→NCBITaxon
   ```

### Success Metrics Dashboard

**Quality Targets:**
- **Raw Quality**: >90% field completion, >5 entities/field
- **Parsing Quality**: >90% structured extraction, >80% relationship parsing
- **Grounding Quality**: >60% grounding rate, <20% AUTO entities
- **Relationship Quality**: >90% entity→relationship conversion  
- **Template Specialization**: <10% cross-template overlap (non-core fields)

**Current Performance** (Templates are production-ready):
- Template specialization scores: 83.9-99.0/100
- Minimal cross-template overlap (primarily universal identifiers)
- High field specificity (87.5-100% on-topic extraction)

## Key Workflows

### Parameterized Extraction

```bash
# Single template extraction
make extract-all SOURCE=ijsem TEMPLATE=growth_conditions N_ABSTRACTS=25

# Multiple template pipeline
make run-all-templates

# Timestamped extraction with assessment
make timestamped-extraction TEMPLATE=biochemical INPUT_DIR=test-biochemical-rich
```

### Development and Testing

```bash
# Validate template schemas
make validate-templates

# Quick test (preserves existing abstracts)
make quick-test TEMPLATE=taxa

# Debug with maximum verbosity
make debug-extraction TEMPLATE=morphology INPUT_DIR=test-morphology-rich

# Template specialization analysis
uv run python unified_assessment.py outputs/ --include-specialization
```

### Cleanup and Maintenance

```bash
# Preserve abstracts and outputs, clean generated files
make clean

# Remove assessment files only
make clean-assessments

# Pipeline status check
make status
```

## Integration with Databases

### Literature vs Database Complementarity

**Literature Extraction Advantages:**
- Novel organisms before database curation
- Experimental context and optimization studies  
- Strain-specific characteristics
- Recent research and cultivation innovations

**BacDive Database Advantages:**
- Precise quantitative data with exact ranges
- Standardized API biochemical panels
- Proven growth media formulations
- Chemical database integration (ChEBI IDs)

**Recommended Integration Strategy:**
1. **BacDive baseline**: Standardized growth parameters and metabolic patterns
2. **Literature supplementation**: Novel conditions and strain-specific requirements
3. **Cross-validation**: Compare literature claims against database standards  
4. **Predictive modeling**: Use combined data for growth media recommendation

### Growth Media Prediction Pipeline

**Feature Engineering Sources:**
- API biochemical profiles (BacDive) → metabolic fingerprints
- Chemical utilization patterns (Literature + METPO) → substrate preferences  
- Environmental parameters (Both) → optimal conditions
- Phylogenetic proximity (Both) → evolutionary context

## Model Configuration

**OntoGPT Model Options:**
```bash
# Default (OpenAI GPT-4)
uv run ontogpt extract -t template.yaml -i abstracts -o output.yaml

# Anthropic Claude
uv run ontogpt extract -m claude-3-5-sonnet-latest -t template.yaml -i abstracts -o output.yaml

# With environment variables
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

**Optimization Settings:**
- `-p 0.1`: Low temperature for consistent results
- `--show-prompt`: Debug LLM prompts and responses
- `--cache-db cache.db`: Persistent caching for development

## Template Design Principles

### Successful Design Patterns

1. **Small and Focused**: Targeted templates outperform comprehensive ones
2. **Normalization at Extraction**: LLM handles unit conversion during extraction
3. **Essential Fields**: PMID + Taxa ensure traceability and linkage  
4. **Ontology Grounding**: Critical for data integration across sources
5. **Dynamic METPO Integration**: SPARQL-populated enums for up-to-date predicates

### Template Coverage Assessment

| Requirement | Literature Templates | BacDive Coverage |
|-------------|---------------------|------------------|
| Organism identification | ✅ | ✅ |
| Phylogenetic context | ✅ | ✅ |
| Growth media | ✅ (qualitative) | ✅ (quantitative) |
| Environmental parameters | ✅ (ranges) | ✅ (precise) |
| Chemical utilization | ✅ (METPO predicates) | ✅ (API panels) |
| Metabolic capabilities | ✅ (contextual) | ✅ (standardized) |

## Infrastructure Features

### Makefile Design

**Key Features:**
- **Parameterized targets**: Single template handles all extraction types
- **Proper dependencies**: Order-only prerequisites with `|`
- **Aggressive cleanup tiers**: Preserve expensive abstracts and cache
- **Self-documenting**: `make help` with examples
- **Status monitoring**: `make status` shows pipeline state

### UV Migration Benefits

**Performance Improvements:**
- Faster dependency resolution (1ms vs previous Poetry slowness)
- Efficient package caching and installation
- Better virtual environment management
- Compatible with all existing workflows

**Migration Complete:**
- All `poetry run` commands → `uv run`
- Dependencies updated to latest compatible versions
- Makefile fully migrated and tested

## Common Use Cases

### Bacterial Characterization Research
Extract comprehensive phenotypic profiles for novel species descriptions and comparative studies.

### Growth Media Optimization  
Combine literature extraction with BacDive data for intelligent media formulation recommendations.

### Phylogenetic Analysis Support
Extract 16S rRNA similarities and taxonomic relationships for phylogenetic studies.

### Metabolic Network Reconstruction
Gather substrate utilization patterns and enzyme activities for systems biology applications.

### Ecological Studies
Extract environmental preferences and isolation sources for habitat modeling.

## Next Steps

**For New Users:**
1. Run `make quick-test` to verify system functionality
2. Try different templates with your abstracts of interest
3. Use assessment tools to evaluate extraction quality
4. Integrate with your analysis workflows

**For Developers:**
1. Review `DEVELOPMENT_NOTES.md` for detailed implementation insights  
2. Examine template specialization results and optimization opportunities
3. Consider domain-specific template extensions
4. Explore integration with additional databases and ontologies

The literature mining pipeline provides mature, production-ready tools for bacterial literature analysis with excellent template specialization and comprehensive quality assessment capabilities.