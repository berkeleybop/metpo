# Fundamental Requirements for Literature Mining Templates

This document defines the core requirements and assessment criteria for OntoGPT template performance in the METPO literature mining pipeline.

## Primary Objective

**Extract maximum possible footprint of abstract content into structured CompoundExpressions.**

The only output of value from this workflow are the structured CompoundExpressions. All other extraction components (named_entities, raw_completion_outputs) serve as debugging checkpoints and quality indicators.

## Core Requirements

### 1. Maximum Abstract Coverage

**Coverage Assessment Metrics:**
- **Text.content**: Full abstract text being processed
- **original_spans**: Spans of text that map to extracted named_entities
- **raw_completion_outputs**: LLM's semicolon-separated entity lists

**Requirements:**
- Maximum number of raw_completion_output fields should be populated
- Each raw_completion_output should contain maximum number of semicolon-separated entities
- Coverage spans should encompass as much of the abstract text as possible

### 2. Raw Completion to Structured Extraction Pipeline

**Conversion Requirements:**
- All raw_completion_outputs MUST be represented as extracted_objects and named_entities
- **Exception**: CompoundExpressions cannot be represented as named_entities
- CompoundExpressions raw_completion_output MUST be reflected in extracted_objects
- No loss of information from raw LLM output to structured format

**Quality Indicators:**
- High entity count in raw_completion_outputs
- High conversion rate from raw → named_entities  
- High conversion rate from raw → CompoundExpressions in extracted_objects

### 3. Ontology Grounding Requirements

**Grounding Targets:**
- Maximum number of named_entities should be grounded to ontologies other than AUTO:
- Minimize AUTO: assignments (indicates failed grounding)
- Each template should use distinct, non-overlapping ontology coverage

**Template-Specific Ontology Targets:**
- **Chemical Utilization**: CHEBI (chemicals), METPO (interaction properties)
- **Growth Conditions**: ENVO (environments), PATO (qualities), METPO (conditions)
- **Biochemical**: EC (enzymes), CHEBI (metabolites), METPO (test results)
- **Morphology**: PATO (qualities), GO (cellular components), METPO (morphology)
- **Taxa**: NCBITaxon (organisms), METPO (strain relationships)

### 4. Template Specialization Requirements

**Disjoint Coverage Principle:**
- Ontologies and entities detected by each template should be as disjoint as possible
- Minimize cross-template overlap except for universal entities
- Each template should focus on its specific domain

**Universal Entity Exceptions:**
- **Strains**: All templates should extract strain identifiers
- **Taxa**: All templates should extract higher taxonomic classifications  
- **Strain-Taxa Relationships**: All templates should include CompoundExpressions linking strains to parent taxa
- **PMIDs**: All templates should capture literature source

### 5. CompoundExpression Structure Requirements

**Mandatory Attributes (exactly three, no others):**
- `subject`: Usually a Strain
- `predicate`: Usually an enumeration specific to template domain
- `object`: Preferably another class defined in template, sometimes string if necessary

**Prohibited:**
- Additional attributes in CompoundExpression classes beyond subject/predicate/object
- Information like `optimal_growth_temperature` should be captured as object values, not separate attributes

## Assessment Methodology

### Coverage Metrics

1. **Abstract Footprint Coverage**
   ```
   Coverage = (Total characters in original_spans) / (Total characters in Text.content)
   ```

2. **Raw Output Completeness**
   ```
   Completeness = (Populated raw_completion_outputs) / (Total template fields)
   ```

3. **Entity Density**
   ```
   Density = (Total semicolon-separated entities) / (Number of populated raw fields)
   ```

### Conversion Efficiency Metrics

1. **Named Entity Conversion Rate**
   ```
   Conversion = (Named entities extracted) / (Entities in raw_completion_outputs)
   ```

2. **CompoundExpression Conversion Rate**
   ```
   Conversion = (CompoundExpressions in extracted_objects) / (Relationship strings in raw outputs)
   ```

### Grounding Quality Metrics

1. **Ontology Grounding Rate**
   ```
   Grounding = (Non-AUTO entities) / (Total named entities)
   ```

2. **Template Specialization Score**
   ```
   Specialization = (Domain-specific ontology hits) / (Total grounded entities)
   ```

### Template Overlap Metrics

1. **Cross-Template Entity Overlap**
   ```
   Overlap = (Shared entities between templates) / (Total unique entities)
   ```
   - Target: <10% except for universal entities (strains, taxa, PMIDs)

## Quality Targets

### Minimum Acceptable Performance
- **Coverage**: >70% of abstract text captured in original_spans
- **Raw Completeness**: >80% of template fields populated
- **Entity Conversion**: >90% of raw entities converted to named_entities
- **CompoundExpression Conversion**: >80% of relationship strings converted to structured objects
- **Ontology Grounding**: >60% non-AUTO entities
- **Template Specialization**: >80% domain-appropriate ontology usage

### Excellent Performance
- **Coverage**: >85% of abstract text captured
- **Raw Completeness**: >95% of template fields populated  
- **Entity Conversion**: >95% conversion rate
- **CompoundExpression Conversion**: >90% relationship conversion
- **Ontology Grounding**: >80% non-AUTO entities
- **Template Specialization**: >90% domain-appropriate ontology usage

## Debugging Checkpoints

### When Performance is Low

1. **Check raw_completion_outputs**: Are they populated with rich, semicolon-separated content?
2. **Check named_entities**: Are raw entities being converted to structured format?
3. **Check original_spans**: Are entities being located in the source text?
4. **Check CompoundExpressions**: Are relationship strings being parsed into subject/predicate/object?
5. **Check ontology assignments**: Are entities being grounded to appropriate ontologies?

### Common Issues and Solutions

1. **Low Coverage**: Template may be too narrow, missing key abstract content types
2. **Poor Raw Output**: Template prompts may be unclear or too complex
3. **Low Conversion Rate**: OntoGPT parsing issues, template structure problems
4. **High AUTO Assignments**: Annotator configuration issues, missing ontology coverage
5. **High Template Overlap**: Templates not sufficiently specialized, need refinement

## Success Criteria

A template is successful when it:
1. **Maximizes abstract coverage** through comprehensive entity extraction
2. **Converts raw LLM output efficiently** into structured CompoundExpressions
3. **Grounds entities to appropriate ontologies** with minimal AUTO assignments
4. **Maintains domain specialization** with minimal cross-template overlap
5. **Produces valuable structured relationships** as CompoundExpressions

The ultimate measure of success is the quantity and quality of structured CompoundExpressions that can be used for downstream knowledge graph construction and analysis.