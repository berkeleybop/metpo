# OntoGPT Template Analysis for METPO

## Issues Found

### 1. Growth Conditions Template (`growth_conditions_template_base.yaml`)

**CRITICAL ISSUES:**

#### Incorrect Annotator Paths:
- **Line 180**: `sqlite:intermediates/db/metpo.db` - WRONG path
- **Line 188**: `sqlite:intermediates/db/metpo.db` - WRONG path  
- **Line 196**: `sqlite:intermediates/db/metpo.db` - WRONG path
- **Line 204**: `sqlite:intermediates/db/metpo.db` - WRONG path
- **Line 212**: `sqlite:intermediates/db/metpo.db` - WRONG path

**Should be**: `sqlite:@src/ontology/metpo.db` or better yet, since METPO might be an OWL file, it should be handled differently.

**PROBLEM**: The path `sqlite:intermediates/db/metpo.db` is a relative path that won't work correctly. According to the user, METPO should be referenced from `@src/ontology/`

#### Signal-to-Noise Concerns:

**Too many fields** (11 top-level attributes):
- pmid
- study_taxa
- strains  
- culture_media
- temperature_conditions
- ph_conditions
- oxygen_requirements
- salt_tolerance
- atmospheric_requirements
- strain_relationships
- growth_condition_relationships
- culture_medium_relationships

This might overwhelm the LLM. Compare to ontogpt examples:
- `environmental_sample.yaml`: 6 attributes
- `gocam.yaml`: 7 attributes

**Redundancy**: The template asks for conditions twice:
1. First as lists (temperature_conditions, ph_conditions, etc.)
2. Then as relationships (growth_condition_relationships)

This is inefficient - the LLM will extract the same information twice.

**RECOMMENDATION**: Either extract conditions as simple lists OR as relationships, not both. The relationship approach is better for structured data.

#### Prompts Are Too Long:
- strain prompt (lines 41-42): 5 sentences
- culture_media prompt (51-55): 4 sentences
- temperature_conditions prompt (62-67): 6 sentences

**Compare to ontogpt examples** which use very concise prompts:
```yaml
# From environmental_sample.yaml
prompt: semicolon-separated list of sites at which the study was conducted. Give specific place names. if you cannot find a specific place name leave the field as empty.
```

vs metpo's verbose prompts that give examples, normalization instructions, conversion instructions, etc.

**Signal-to-noise impact**: Longer prompts increase token usage and can confuse the LLM.

#### growth_condition_relationships Prompt is Problematic:

Lines 138-140:
```yaml
prompt: >-
  For each growth condition found in temperature_conditions, ph_conditions, oxygen_requirements, salt_tolerance, and atmospheric_requirements fields above, extract structured relationships linking specific organisms to those growth parameters...
```

This tells the LLM to look at "fields above" which creates circular dependencies and is confusing.

### 2. Chemical Utilization Template (`bacdive_utilization_template.yaml`)

**ISSUES:**

#### Annotator Problems:

**Line 123**: 
```yaml
annotators: mco.db, MicrO-2025-03-20-merged.db, mpo_v0.74.en_only.db, n4l_merged.db, omp.db
```

**PROBLEMS**:
- These are `.db` files without `sqlite:` prefix - unclear if this works
- Paths are not absolute or using `@src/ontology/`
- Uses multiple phenotype databases instead of just METPO
- According to user: "only METPO should be used for anything related to microbial traits, phenotypes and types of chemical utilization"

**Should be**: Just METPO for phenotypes

**Lines 97, 103**: Uses `sqlite:obo:foodon` and `sqlite:obo:swisslipid`
- `foodon` is in registry ✓
- `swisslipid` is in registry ✓

**Lines 107, 111**: Uses `sqlite:obo:ncbitaxon` 
- NOT in registry explicitly, but `sqlite:obo:` prefix usually works for standard OBO ontologies

#### Too Many Entity Types:

The template has **9 different entity types**:
- ChemicalCompound
- Enzyme
- Lipid
- Organism
- Species
- Strain
- TypeStrain
- MicrobialPhenotype

Plus **6 relationship types**. This is very complex.

**Compare to ontogpt examples**:
- `gocam.yaml`: 5 entity types
- `environmental_sample.yaml`: 5 entity types

#### Massive Enums:

RelationshipTypeEnum has **59 permissible values** (lines 202-304). This is excessive and will:
1. Take up huge prompt space
2. Confuse the LLM
3. Reduce extraction quality

**RECOMMENDATION**: Simplify to ~10-15 core relationship types.

### 3. Microbial Phenotype Relations Template (`large/microbial_phenotype_relations_template.yaml`)

**ISSUES:**

**Line 77**: 
```yaml
annotators: MicrO-for-metpo.owl
```

**PROBLEM**: This references an OWL file directly without `sqlite:` or proper path prefix. Should be:
- `sqlite:@src/ontology/metpo.db` OR
- If using OWL directly, needs proper path handling

#### Relationship Type as String:

Lines 90, 103, 115, 127:
```yaml
relationship_type:
  description: the type of relationship (e.g., "utilizes", "produces", "requires", "is sensitive to", "is resistant to")
  range: string
```

**PROBLEM**: Using `string` instead of enum means:
1. No standardization
2. Cannot ground to METPO relationship types
3. Will get inconsistent extractions ("uses" vs "utilizes" vs "consumes")

**RECOMMENDATION**: Use enums like the chemical utilization template.

#### No Isolation Source Extraction:

None of the three templates extract:
- Isolation source
- Geographic location
- Sample type
- Environmental origin

This might be valuable metadata for the database.

## Comparison with OntoGPT Examples

### Good Practices from OntoGPT:

1. **Concise prompts** - environmental_sample uses very brief prompts
2. **Clear separation** - entities vs relationships 
3. **Limited attributes** - usually 5-7 per template
4. **Proper annotators** - Uses standard formats:
   - `sqlite:obo:envo`
   - `bioportal:gaz`
   - `gilda:`

### What METPO Templates Do Well:

1. **Detailed descriptions** - Good documentation
2. **CompoundExpression** - Proper use of LinkML patterns for relationships
3. **Type safety** - Using enums for relationship types (except microbial_phenotype_relations)

## Recommendations

### For Growth Conditions Template:

1. **Fix METPO path**: Change `sqlite:intermediates/db/metpo.db` to `sqlite:@src/ontology/metpo.db`
2. **Reduce redundancy**: Remove the simple list fields (temperature_conditions, ph_conditions, etc.) and only keep the relationship fields
3. **Shorten prompts**: Use 1-2 sentence prompts maximum
4. **Remove circular dependency**: Don't reference "fields above" in prompts
5. **Reduce attributes**: Target 6-8 total attributes

### For Chemical Utilization Template:

1. **Use only METPO for phenotypes**: Change line 123 to use only METPO
2. **Add sqlite: prefix** and proper paths to all annotators
3. **Reduce enum size**: Cut RelationshipTypeEnum to 15-20 core values
4. **Consider splitting**: May want separate templates for chemical utilization vs phenotypes

### For Microbial Phenotype Relations:

1. **Fix METPO path**: Use proper annotator format with sqlite: and path
2. **Replace string with enum**: For all relationship_type fields
3. **Add relationship types**: Define proper enums

### General:

1. **Add isolation source extraction**: Consider adding this to at least one template
2. **Verify NCBITaxon**: Check if `sqlite:obo:ncbitaxon` actually works or if it needs to be in registry
3. **Test with real data**: Run on sample abstracts to verify signal-to-noise is good
4. **Document AUTO extractions**: Set up tracking for entities that can't be grounded to METPO

## Correct Annotator Formats

Based on ontogpt examples and registry:

**Standard OBO ontologies** (from semantic-sql):
```yaml
annotators: sqlite:obo:chebi, sqlite:obo:foodon
```

**Local METPO** (recommended):
```yaml
annotators: sqlite:@src/ontology/metpo.db
```

**Bioportal** (if needed):
```yaml  
annotators: bioportal:ncit
```

**Multiple annotators**:
```yaml
annotators: sqlite:obo:chebi, sqlite:@src/ontology/metpo.db
```
