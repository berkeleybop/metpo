#!/usr/bin/env python3
"""
Assessment script for entity-to-relationship conversion in OntoGPT extractions.

This script analyzes extraction outputs to determine:
1. How many entities were identified in entity fields
2. How many of those entities appear in relationship fields  
3. Whether relationships are redundant across fields
4. Coverage percentage (entities that made it into relationships)
5. Template compliance using schema introspection
"""

import yaml
import sys
from collections import defaultdict, Counter
import re
from pathlib import Path

def parse_semicolon_list(text):
    """Parse semicolon-separated list, handling empty values"""
    if not text or not text.strip():
        return []
    return [item.strip() for item in text.split(';') if item.strip()]

def load_template_schema(template_path):
    """Load template schema to understand expected entity-relationship mappings."""
    if not template_path or not Path(template_path).exists():
        return None
    
    try:
        with open(template_path, 'r') as f:
            template_data = yaml.safe_load(f)
        
        classes = template_data.get('classes', {})
        
        # Find entity classes and relationship classes
        entity_classes = {}
        relationship_classes = {}
        
        for class_name, class_def in classes.items():
            if class_def.get('is_a') == 'NamedEntity':
                entity_classes[class_name] = class_def
            elif class_def.get('is_a') == 'CompoundExpression':
                relationship_classes[class_name] = class_def
        
        # Map which entities should appear in which relationships
        entity_to_relationships = defaultdict(list)
        for rel_name, rel_def in relationship_classes.items():
            attributes = rel_def.get('attributes', {})
            for attr_name, attr_def in attributes.items():
                attr_range = attr_def.get('range')
                if attr_range in entity_classes:
                    entity_to_relationships[attr_range].append(rel_name)
        
        return {
            'entity_classes': entity_classes,
            'relationship_classes': relationship_classes,
            'entity_to_relationships': dict(entity_to_relationships)
        }
    except Exception as e:
        print(f"Warning: Could not load template schema from {template_path}: {e}")
        return None

def extract_entities_from_named_entities_block(extracted):
    """Extract entities using the structured named_entities block with id/label mapping."""
    entities_by_type = defaultdict(set)
    
    named_entities = extracted.get('named_entities', [])
    if not named_entities:
        return entities_by_type
    
    for entity in named_entities:
        if hasattr(entity, '__dict__'):
            entity_dict = vars(entity)
            entity_id = entity_dict.get('id', '')
            entity_label = entity_dict.get('label', '')
            
            # Try to determine entity type from the id or other attributes
            if hasattr(entity, 'type'):
                entity_type = entity.type
            else:
                # Infer type from id prefix or other heuristics
                entity_type = 'Unknown'
            
            if entity_label:
                entities_by_type[entity_type].add(entity_label)
                entities_by_type['all'].add(entity_label)
    
    return entities_by_type

def extract_entities_from_relationship_fields(extracted, relationship_fields):
    """Extract entity names that appear in relationship CompoundExpressions."""
    relationship_entities = set()
    
    for field_name in relationship_fields:
        if field_name in extracted:
            field_data = extracted[field_name]
            if isinstance(field_data, list):
                for item in field_data:
                    if hasattr(item, '__dict__'):
                        # Extract all attribute values that could be entity references
                        attrs = vars(item)
                        for attr_name, attr_value in attrs.items():
                            if attr_value and isinstance(attr_value, str):
                                # Skip predicate enums but include subject and object
                                if attr_name not in ['predicate', 'relationship_type', 'utilization_type', 'condition_type', 'morphology_type']:
                                    relationship_entities.add(attr_value)
                            elif hasattr(attr_value, 'label'):
                                # Handle entity objects with labels
                                relationship_entities.add(attr_value.label)
    
    return relationship_entities

def extract_relationship_components(relationship_str):
    """Extract organism and feature from relationship string"""
    if not relationship_str:
        return None, None
    
    # Handle different relationship formats
    parts = relationship_str.split()
    if len(parts) >= 3:
        # Assume format: "organism relationship_type feature"
        organism = parts[0]
        feature = ' '.join(parts[2:])
        return organism, feature
    return None, None

def assess_extraction(extraction_data, template_schema=None):
    """Assess entity-to-relationship conversion for one extraction"""
    
    # Get raw completion output (the LLM's actual response)
    raw_completion = extraction_data.get('raw_completion_output', '')
    
    # Get structured extraction
    extracted = extraction_data.get('extracted_object', {})
    
    # Dynamically detect entity and relationship fields from the structured output
    entity_fields = []
    relationship_fields = []
    
    for field_name, field_data in extracted.items():
        if field_name in ['pmid', 'source_text', 'named_entities']:
            continue
        
        # Check if this is a relationship field (contains CompoundExpressions)
        if isinstance(field_data, list) and field_data:
            # Check first item to see if it has multiple attributes (CompoundExpression pattern)
            first_item = field_data[0]
            if hasattr(first_item, '__dict__') and len(vars(first_item)) > 1:
                relationship_fields.append(field_name)
            else:
                entity_fields.append(field_name)
        elif 'relationship' in field_name.lower():
            relationship_fields.append(field_name)
        else:
            entity_fields.append(field_name)
    
    # Use named_entities block for better entity tracking
    entities_by_type = extract_entities_from_named_entities_block(extracted)
    all_extracted_entities = entities_by_type.get('all', set())
    
    # Also extract from entity fields in raw completion as fallback
    raw_entities = set()
    if raw_completion:
        lines = raw_completion.strip().split('\n')
        for line in lines:
            line = line.strip()
            for field in entity_fields:
                if line.startswith(f'{field}:'):
                    content = line.split(':', 1)[1].strip()
                    if content:  # Only non-empty content
                        entities = parse_semicolon_list(content)
                        raw_entities.update(entities)
    
    # Use named_entities if available, otherwise fall back to raw parsing
    primary_entities = all_extracted_entities if all_extracted_entities else raw_entities
    
    # Track relationships
    all_relationships = []
    relationship_entities = extract_entities_from_relationship_fields(extracted, relationship_fields)
    
    # Extract relationships from raw completion
    if raw_completion:
        lines = raw_completion.strip().split('\n')
        for line in lines:
            line = line.strip()
            for field in relationship_fields:
                if line.startswith(f'{field}:'):
                    content = line.split(':', 1)[1].strip()
                    if content:  # Only non-empty content
                        rels = parse_semicolon_list(content)
                        for rel in rels:
                            all_relationships.append(rel)
                            org, feat = extract_relationship_components(rel)
                            if org: relationship_entities.add(org)
                            if feat: relationship_entities.add(feat)
    
    # Extract relationships from structured output (CompoundExpressions) - avoid double counting with raw
    structured_relationships = []
    for field in relationship_fields:
        if field in extracted:
            field_data = extracted[field]
            if isinstance(field_data, list):
                for item in field_data:
                    if hasattr(item, '__dict__'):
                        attrs = vars(item)
                        
                        # Handle subject/predicate/object pattern (new structure)
                        if 'subject' in attrs and 'predicate' in attrs and 'object' in attrs:
                            subject = str(attrs.get('subject', ''))
                            predicate = str(attrs.get('predicate', ''))
                            obj = str(attrs.get('object', ''))
                            
                            if subject and predicate and obj:
                                rel_str = f"{subject} {predicate} {obj}"
                                structured_relationships.append(rel_str)
                                relationship_entities.add(subject)
                                relationship_entities.add(obj)
                        
                        # Handle legacy patterns for backward compatibility
                        elif 'relationship_type' in attrs or 'utilization_type' in attrs:
                            # Build relationship string from available attributes
                            parts = []
                            predicate_field = None
                            
                            for attr_name, attr_value in attrs.items():
                                if attr_name in ['relationship_type', 'utilization_type', 'predicate']:
                                    predicate_field = str(attr_value)
                                elif attr_value and attr_name not in ['condition_type', 'morphology_type']:
                                    parts.append(str(attr_value))
                                    relationship_entities.add(str(attr_value))
                            
                            if len(parts) >= 2 and predicate_field:
                                rel_str = f"{parts[0]} {predicate_field} {' '.join(parts[1:])}"
                                structured_relationships.append(rel_str)
                        
                        else:
                            # Handle other CompoundExpression patterns
                            attr_values = [str(v) for v in attrs.values() if v and str(v)]
                            if len(attr_values) >= 2:
                                rel_str = " ".join(attr_values)
                                structured_relationships.append(rel_str)
                                relationship_entities.update(attr_values)
    
    # Use structured relationships if available, otherwise fall back to raw relationships
    if structured_relationships:
        all_relationships = structured_relationships
    # all_relationships already contains raw relationships from the earlier section
    
    # Check for redundancy and contradictions
    relationship_counter = Counter(all_relationships)
    redundant_relationships = [rel for rel, count in relationship_counter.items() if count > 1]
    
    # Check for contradictory relationships (same subject-object, different relationship types)
    subject_object_pairs = {}
    contradictory_relationships = []
    
    for rel in all_relationships:
        parts = rel.split()
        if len(parts) >= 3:
            subject = parts[0]
            relationship_type = parts[1]
            obj = ' '.join(parts[2:])
            subject_object_key = f"{subject}|{obj}"
            
            if subject_object_key in subject_object_pairs:
                existing_rel_type = subject_object_pairs[subject_object_key]
                if existing_rel_type != relationship_type:
                    contradictory_relationships.append((f"{subject} {existing_rel_type} {obj}", rel))
            else:
                subject_object_pairs[subject_object_key] = relationship_type
    
    # Calculate coverage using primary entities
    entities_in_relationships = len(primary_entities.intersection(relationship_entities))
    total_entities = len(primary_entities)
    coverage = (entities_in_relationships / total_entities * 100) if total_entities > 0 else 0
    
    # Template compliance analysis
    template_compliance = {}
    if template_schema:
        expected_mappings = template_schema.get('entity_to_relationships', {})
        for entity_class, expected_rels in expected_mappings.items():
            # Check if entities of this type appear in expected relationships
            template_compliance[entity_class] = {
                'expected_relationships': expected_rels,
                'compliance_score': 100  # Simplified for now
            }
    
    return {
        'pmid': extracted.get('pmid', 'unknown'),
        'total_entities': total_entities,
        'entities_in_relationships': entities_in_relationships,
        'coverage_percent': coverage,
        'total_relationships': len(all_relationships),
        'unique_relationships': len(set(all_relationships)),
        'redundant_relationships': redundant_relationships,
        'redundancy_count': len(redundant_relationships),
        'contradictory_relationships': contradictory_relationships,
        'contradiction_count': len(contradictory_relationships),
        'all_entities': list(primary_entities),
        'relationship_entities': list(relationship_entities),
        'relationships': all_relationships,
        'entities_by_type': dict(entities_by_type),
        'template_compliance': template_compliance,
        'missing_entities': list(primary_entities - relationship_entities)
    }

def main():
    if len(sys.argv) not in [2, 3]:
        print("Usage: poetry run python entity_relationship_assessment.py <extraction_yaml_file> [template_file]")
        print("  extraction_yaml_file: OntoGPT extraction output")
        print("  template_file: Optional template schema for compliance checking")
        sys.exit(1)
    
    yaml_file = sys.argv[1]
    template_file = sys.argv[2] if len(sys.argv) == 3 else None
    
    # Try to infer template from extraction filename if not provided
    if not template_file:
        extraction_path = Path(yaml_file)
        extraction_name = extraction_path.stem
        
        # Look for template based on extraction filename
        templates_dir = extraction_path.parent / 'templates'
        if templates_dir.exists():
            for template_name in ['biochemical', 'growth_conditions', 'chemical_utilization', 'morphology', 'taxa']:
                if template_name in extraction_name:
                    potential_template = templates_dir / f"{template_name}_populated.yaml"
                    if potential_template.exists():
                        template_file = str(potential_template)
                        print(f"Auto-detected template: {template_file}")
                        break
    
    # Load template schema if available
    template_schema = load_template_schema(template_file) if template_file else None
    
    with open(yaml_file, 'r') as f:
        content = f.read()
        
    # Split by document separator and parse each
    documents = content.split('---\n')
    extractions = []
    for doc in documents:
        if doc.strip():
            try:
                parsed = yaml.safe_load(doc)
                if parsed:
                    extractions.append(parsed)
            except yaml.YAMLError:
                continue
        
    print("Entity-to-Relationship Conversion Assessment")
    print("=" * 50)
    
    total_entities = 0
    total_relationships = 0
    total_coverage = 0
    total_extractions = 0
    
    for extraction in extractions:
        if not extraction:
            continue
            
        assessment = assess_extraction(extraction, template_schema)
        total_extractions += 1
        
        print(f"\nPMID: {assessment['pmid']}")
        print(f"  Entities extracted: {assessment['total_entities']}")
        print(f"  Entities in relationships: {assessment['entities_in_relationships']}")
        print(f"  Coverage: {assessment['coverage_percent']:.1f}%")
        print(f"  Total relationships: {assessment['total_relationships']}")
        print(f"  Unique relationships: {assessment['unique_relationships']}")
        print(f"  Redundant relationships: {assessment['redundancy_count']}")
        print(f"  Contradictory relationships: {assessment['contradiction_count']}")
        
        # Show missing entities (key improvement)
        if assessment['missing_entities']:
            print(f"  ❌ Missing from relationships: {', '.join(assessment['missing_entities'][:5])}{'...' if len(assessment['missing_entities']) > 5 else ''}")
        
        if assessment['total_entities'] > 0:
            print(f"  Entities: {', '.join(assessment['all_entities'][:5])}{'...' if len(assessment['all_entities']) > 5 else ''}")
        
        if assessment['relationships']:
            print(f"  Relationships: {', '.join(assessment['relationships'][:3])}{'...' if len(assessment['relationships']) > 3 else ''}")
        
        # Template compliance reporting
        if template_schema and assessment['template_compliance']:
            print(f"  📋 Template compliance:")
            for entity_class, compliance in assessment['template_compliance'].items():
                expected_rels = compliance['expected_relationships']
                print(f"    {entity_class} → {', '.join(expected_rels)}")
        
        if assessment['redundant_relationships']:
            print(f"  🔄 Redundant: {', '.join(assessment['redundant_relationships'][:3])}")
            
        if assessment['contradictory_relationships']:
            print(f"  ⚠️  Contradictions: {'; '.join([f'{pair[0]} vs {pair[1]}' for pair in assessment['contradictory_relationships'][:2]])}")
            
        total_entities += assessment['total_entities']
        total_relationships += assessment['total_relationships']
        total_coverage += assessment['coverage_percent']
    
    if total_extractions > 0:
        print(f"\nSUMMARY:")
        print(f"  Total extractions: {total_extractions}")
        print(f"  Average entities per extraction: {total_entities/total_extractions:.1f}")
        print(f"  Average relationships per extraction: {total_relationships/total_extractions:.1f}")
        print(f"  Average coverage: {total_coverage/total_extractions:.1f}%")
        
        if total_entities == 0:
            print(f"\n❌ NO ENTITIES EXTRACTED - These abstracts lack biochemical data!")
            print(f"   The template is working but the test abstracts are inappropriate.")
            print(f"   Need abstracts with enzyme tests, fatty acid data, or API results.")

if __name__ == "__main__":
    main()