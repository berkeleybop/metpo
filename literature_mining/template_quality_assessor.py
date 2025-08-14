#!/usr/bin/env python3
"""
Template Quality Assessor for OntoGPT Templates.

This script analyzes OntoGPT template schemas to determine:
1. Coverage: Does every NamedEntity appear in at least one CompoundExpression?
2. Relationship density: Ratio of CompoundExpression fields to entity fields
3. Template focus: Are the templates structured for relationship extraction vs. entity extraction?
4. Consistency: Do all templates follow the same relationship extraction patterns?
"""

import yaml
import sys
from pathlib import Path
from collections import defaultdict

def load_template(template_path):
    """Load and parse a LinkML template YAML file."""
    with open(template_path, 'r') as f:
        return yaml.safe_load(f)

def analyze_template_structure(template_data, template_name):
    """Analyze the structure of a single template."""
    classes = template_data.get('classes', {})
    enums = template_data.get('enums', {})
    
    # Find the root extraction class (tree_root: true)
    root_class = None
    for class_name, class_def in classes.items():
        if class_def.get('tree_root'):
            root_class = class_name
            break
    
    if not root_class:
        return {
            'error': 'No tree_root class found',
            'template': template_name
        }
    
    # Analyze fields in the root class
    root_attributes = classes[root_class].get('attributes', {})
    
    # Categorize fields
    entity_fields = []
    relationship_fields = []
    string_fields = []
    other_fields = []
    
    for field_name, field_def in root_attributes.items():
        if field_name in ['pmid', 'source_text']:
            continue
            
        field_range = field_def.get('range', 'string')
        
        # Check if range refers to a NamedEntity class
        if field_range in classes:
            range_class = classes[field_range]
            if range_class.get('is_a') == 'NamedEntity':
                entity_fields.append((field_name, field_range))
            elif range_class.get('is_a') == 'CompoundExpression':
                relationship_fields.append((field_name, field_range))
            else:
                other_fields.append((field_name, field_range))
        elif field_range == 'string':
            string_fields.append((field_name, field_range))
        elif field_range in enums:
            other_fields.append((field_name, field_range))
        else:
            other_fields.append((field_name, field_range))
    
    # Find all NamedEntity classes
    named_entities = {}
    compound_expressions = {}
    
    for class_name, class_def in classes.items():
        if class_def.get('is_a') == 'NamedEntity':
            named_entities[class_name] = class_def
        elif class_def.get('is_a') == 'CompoundExpression':
            compound_expressions[class_name] = class_def
    
    # Check coverage: which NamedEntities appear in CompoundExpressions?
    entities_in_relationships = set()
    
    for rel_name, rel_class in compound_expressions.items():
        attributes = rel_class.get('attributes', {})
        for attr_name, attr_def in attributes.items():
            attr_range = attr_def.get('range')
            if attr_range in named_entities:
                entities_in_relationships.add(attr_range)
    
    # Calculate coverage
    all_entities = set(named_entities.keys())
    uncovered_entities = all_entities - entities_in_relationships
    coverage_percent = (len(entities_in_relationships) / len(all_entities) * 100) if all_entities else 0
    
    # Relationship density
    total_fields = len(entity_fields) + len(relationship_fields) + len(string_fields)
    relationship_density = (len(relationship_fields) / total_fields * 100) if total_fields > 0 else 0
    
    return {
        'template': template_name,
        'root_class': root_class,
        'entity_fields': entity_fields,
        'relationship_fields': relationship_fields,
        'string_fields': string_fields,
        'other_fields': other_fields,
        'named_entities': list(named_entities.keys()),
        'compound_expressions': list(compound_expressions.keys()),
        'entities_in_relationships': list(entities_in_relationships),
        'uncovered_entities': list(uncovered_entities),
        'coverage_percent': coverage_percent,
        'relationship_density': relationship_density,
        'total_entities': len(all_entities),
        'total_relationships': len(compound_expressions),
        'field_counts': {
            'entity': len(entity_fields),
            'relationship': len(relationship_fields),
            'string': len(string_fields),
            'other': len(other_fields)
        }
    }

def assess_template_quality(analysis):
    """Generate quality assessment based on analysis."""
    issues = []
    strengths = []
    
    # Coverage issues
    if analysis['coverage_percent'] < 100:
        issues.append(f"Incomplete entity coverage: {analysis['coverage_percent']:.1f}% ({len(analysis['uncovered_entities'])} entities not in relationships)")
        for entity in analysis['uncovered_entities']:
            issues.append(f"  - {entity} not used in any CompoundExpression")
    else:
        strengths.append("Full entity coverage: all NamedEntities appear in relationships")
    
    # Relationship density
    if analysis['relationship_density'] < 30:
        issues.append(f"Low relationship density: {analysis['relationship_density']:.1f}% (template focuses on entity extraction)")
    elif analysis['relationship_density'] > 50:
        strengths.append(f"Good relationship density: {analysis['relationship_density']:.1f}% (relationship-focused template)")
    
    # Template structure
    if analysis['total_relationships'] == 0:
        issues.append("No CompoundExpression classes defined - pure entity extraction template")
    elif analysis['total_relationships'] < analysis['total_entities'] / 2:
        issues.append(f"Few relationships ({analysis['total_relationships']}) relative to entities ({analysis['total_entities']})")
    
    # Field type balance
    if analysis['field_counts']['string'] > analysis['field_counts']['relationship']:
        issues.append("More string fields than relationship fields - consider structured extraction")
    
    return {
        'overall_score': max(0, 100 - len(issues) * 15),  # Rough scoring
        'issues': issues,
        'strengths': strengths
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python template_quality_assessor.py <template_file_or_directory>")
        print("Examples:")
        print("  python template_quality_assessor.py templates/biochemical_populated.yaml")
        print("  python template_quality_assessor.py templates/")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    
    if path.is_file():
        template_files = [path]
    elif path.is_dir():
        template_files = list(path.glob("*_populated.yaml"))
        if not template_files:
            template_files = list(path.glob("*_template_base.yaml"))
    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1)
    
    print("Template Quality Assessment")
    print("=" * 50)
    
    all_analyses = []
    
    for template_file in sorted(template_files):
        print(f"\n📋 Template: {template_file.name}")
        print("-" * 40)
        
        try:
            template_data = load_template(template_file)
            analysis = analyze_template_structure(template_data, template_file.stem)
            
            if 'error' in analysis:
                print(f"❌ Error: {analysis['error']}")
                continue
            
            quality = assess_template_quality(analysis)
            all_analyses.append((template_file.name, analysis, quality))
            
            # Display results
            print(f"Root class: {analysis['root_class']}")
            print(f"Entities: {analysis['total_entities']} | Relationships: {analysis['total_relationships']}")
            print(f"Coverage: {analysis['coverage_percent']:.1f}% | Relationship density: {analysis['relationship_density']:.1f}%")
            print(f"Quality score: {quality['overall_score']}/100")
            
            # Show field breakdown
            print(f"\nField types:")
            for field_type, count in analysis['field_counts'].items():
                print(f"  {field_type}: {count}")
            
            # Show issues
            if quality['issues']:
                print(f"\n⚠️  Issues:")
                for issue in quality['issues']:
                    print(f"  {issue}")
            
            # Show strengths
            if quality['strengths']:
                print(f"\n✅ Strengths:")
                for strength in quality['strengths']:
                    print(f"  {strength}")
                    
        except Exception as e:
            print(f"❌ Error analyzing {template_file.name}: {e}")
    
    # Summary across all templates
    if len(all_analyses) > 1:
        print(f"\n{'='*50}")
        print("SUMMARY ACROSS TEMPLATES")
        print("=" * 50)
        
        avg_coverage = sum(a[1]['coverage_percent'] for a in all_analyses) / len(all_analyses)
        avg_density = sum(a[1]['relationship_density'] for a in all_analyses) / len(all_analyses)
        avg_score = sum(a[2]['overall_score'] for a in all_analyses) / len(all_analyses)
        
        print(f"Average coverage: {avg_coverage:.1f}%")
        print(f"Average relationship density: {avg_density:.1f}%")
        print(f"Average quality score: {avg_score:.1f}/100")
        
        # Common issues
        all_issues = []
        for _, _, quality in all_analyses:
            all_issues.extend(quality['issues'])
        
        if all_issues:
            print(f"\nMost common issues:")
            issue_counts = defaultdict(int)
            for issue in all_issues:
                # Group similar issues
                if "coverage" in issue.lower():
                    issue_counts["Incomplete entity coverage"] += 1
                elif "density" in issue.lower():
                    issue_counts["Low relationship density"] += 1
                elif "string fields" in issue.lower():
                    issue_counts["Too many string fields"] += 1
            
            for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  {issue}: {count}/{len(all_analyses)} templates")

if __name__ == "__main__":
    main()