# Literature Mining Assessment Roadmap

## Project Context
OntoGPT-based literature mining pipeline for bacterial characteristics extraction using specialized templates. Focus on maximizing extraction quality, minimizing redundancy, and optimizing template specialization.

## Current Status

### ✅ Completed Work
1. **Enhanced Assessment Tools**
   - `template_quality_assessor.py` - Template structure analysis with click CLI and file output
   - `entity_relationship_assessment.py` - Entity-to-relationship conversion analysis with bulk processing
   - `grounding_quality_assessor.py` - Ontology grounding quality analysis
   - All assessors save timestamped output files (JSON/text formats)

2. **Fixed Infrastructure Issues**
   - OntoGPT cache path bug resolved (absolute paths: `$(PWD)/cache/ontogpt-cache.db`)
   - Makefile targets updated with proper cache configuration
   - Debug extraction target with maximum verbosity (`LITELLM_LOG=DEBUG`)

3. **Assessment Results**
   - **Templates**: 100% entity coverage, 38.6% relationship density, 94/100 quality score
   - **Grounding**: 33.5% grounding rate, 526 entities, NCBITaxon (117), CHEBI (43) leading
   - **Critical Issue**: 0% relationship extraction despite good LLM output (S/P/O parsing broken)

## Core Goals (Priority Order)

### 1. Raw LLM Quality
- **Maximize populated raw_completion_output fields**
- **Maximize semicolon-separated entities per field**
- Metrics: Field completion rate, entity density per field

### 2. Parsing Quality  
- **Maximize extracted_objects creation**
- **Fix S/P/O CompoundExpression parsing** (CRITICAL BLOCKER)
- Metrics: Structured extraction success rate, relationship parsing rate

### 3. Grounding Quality
- **Maximize grounded extracted_objects**
- **Ensure reasonable annotators for each entity type**
- Metrics: Grounding rate by domain, annotator coverage, cross-template consistency

### 4. Relationship Quality
- **Maximize extracted_objects in relationship CompoundExpressions**
- Metrics: Entity-to-relationship conversion rate, relationship completeness

### 5. Template Specialization (NEW)
- **Minimize extraction duplication** (except strains, taxa, pmids, relations)
- **Maximize template sensitivity** (catch all relevant info)
- **Maximize template specificity** (avoid off-topic extractions)
- Metrics: Cross-template overlap, sensitivity/specificity scores

## Critical Issues Identified

### 🚨 S/P/O Relationship Parsing Issue
**Problem**: OntoGPT can't parse semicolon-separated relationships into CompoundExpressions
- LLM generates: `fatty_acid_relationships: AZM34c11T predominant_fatty_acid iso-C16:0; NBRC 106114T predominant_fatty_acid iso-C16:0`
- Expected structure:
  ```yaml
  fatty_acid_relationships:
    - subject: AZM34c11T
      predicate: predominant_fatty_acid
      object: iso-C16:0
  ```
- Current result: Relationships missing from extracted_object entirely

**Root Cause**: OntoGPT's S/P/O parsing expects different input format than semicolon-separated strings

**Impact**: 0% relationship extraction across all templates despite good LLM output

## Implementation Roadmap

### Phase 1: Fix Critical Blockers
1. **Fix S/P/O CompoundExpression Parsing**
   - Investigate OntoGPT's relationship parsing expectations
   - Either modify template prompts or find alternative approach
   - Validate fix with test extractions

### Phase 2: Unified Assessment System
2. **Create Unified Assessment Script**
   - Template-informed extraction analysis
   - All pipeline health metrics in one tool
   - Integration with existing assessors
   - Goal-aligned reporting (raw→parsing→grounding→relationships)

### Phase 3: Template Specialization Analysis
3. **Template Overlap Detection**
   - Cross-template entity type analysis
   - Quantify extraction redundancy
   - Identify template-exclusive vs shared fields

4. **Sensitivity/Specificity Analysis**
   - Template focus drift detection
   - Off-topic extraction measurement
   - Cross-template entity gap analysis

### Phase 4: Enhanced Quality Metrics
5. **Domain-Specific Grounding Analysis**
   - Fatty acids → CHEBI mapping quality
   - Enzyme activities → EC/GO coverage
   - Growth conditions → controlled vocabulary usage

6. **Cross-Template Consistency Analysis**
   - Same entities grounded identically across templates
   - Template-specific grounding performance patterns

## Deterministic vs Thematic Tasks

### Deterministic Solutions (Can Automate)
- Template overlap quantification
- Field completion rate analysis  
- Grounding success rate calculation
- Cross-template entity comparison
- Off-topic extraction detection (based on field names)

### Thematic Tasks (Need Human Guidance)
- Biochemical vs morphological boundary definition
- Edge case classification (e.g., cell wall composition)
- Template consolidation strategy
- Priority order for overlapping extractions

## File Structure
```
literature_mining/
├── assessments/           # Timestamped assessment outputs
├── templates/            # Base and populated templates
├── outputs/             # Extraction results
├── cache/              # OntoGPT cache (fixed paths)
├── logs/               # Extraction logs
├── template_quality_assessor.py
├── entity_relationship_assessment.py  
├── grounding_quality_assessor.py
├── Makefile            # Updated with cache fixes
└── ASSESSMENT_ROADMAP.md # This file
```

## Key Commands
```bash
# Template assessment
make assess-templates

# Extraction assessment  
make assess-all-outputs

# Grounding analysis
poetry run python grounding_quality_assessor.py outputs/ --verbose

# Debug extraction
make debug-extraction TEMPLATE=biochemical INPUT_DIR=test-biochemical-rich

# Full pipeline with assessment
make timestamped-extraction TEMPLATE=biochemical INPUT_DIR=test-biochemical-rich
```

## Next Session Recovery
If restarting Claude:
1. Read this roadmap file
2. Current priority: Fix S/P/O relationship parsing issue
3. Key insight: LLM generates good relationships, OntoGPT fails to parse them
4. All assessment tools working, need unified script next
5. Template specialization analysis needed for efficiency optimization

## Success Metrics Dashboard (Target)
- **Raw Quality**: >90% field completion, >5 entities/field
- **Parsing Quality**: >90% structured extraction, >80% relationship parsing  
- **Grounding Quality**: >60% grounding rate, <20% AUTO entities
- **Relationship Quality**: >90% entity→relationship conversion
- **Template Specialization**: <10% cross-template overlap (non-core fields)