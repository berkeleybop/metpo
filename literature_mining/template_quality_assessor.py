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
import click
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

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

@click.command()
@click.argument('template_path', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), 
              help='Output file for assessment results (default: assessment_results_TIMESTAMP.json)')
@click.option('--format', 'output_format', type=click.Choice(['json', 'text']), default='text',
              help='Output format: json or text (default: text)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(template_path, output, output_format, verbose):
    """Assess template quality for OntoGPT templates.
    
    TEMPLATE_PATH can be a single template file or directory containing templates.
    """
    
    if template_path.is_file():
        template_files = [template_path]
    elif template_path.is_dir():
        template_files = list(template_path.glob("*_populated.yaml"))
        if not template_files:
            template_files = list(template_path.glob("*_template_base.yaml"))
    else:
        click.echo(f"Error: {template_path} is not a valid file or directory", err=True)
        raise click.Abort()
    
    if not template_files:
        click.echo(f"No template files found in {template_path}", err=True)
        raise click.Abort()
    
    # Set default output file if not provided
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = 'json' if output_format == 'json' else 'txt'
        output = Path(f"template_assessment_{timestamp}.{suffix}")
    
    click.echo("Template Quality Assessment")
    click.echo("=" * 50)
    
    all_analyses = []
    assessment_data = {
        'timestamp': datetime.now().isoformat(),
        'templates': [],
        'summary': {}
    }
    
    for template_file in sorted(template_files):
        click.echo(f"\n📋 Template: {template_file.name}")
        click.echo("-" * 40)
        
        try:
            template_data = load_template(template_file)
            analysis = analyze_template_structure(template_data, template_file.stem)
            
            if 'error' in analysis:
                click.echo(f"❌ Error: {analysis['error']}", err=True)
                continue
            
            quality = assess_template_quality(analysis)
            all_analyses.append((template_file.name, analysis, quality))
            
            # Store data for JSON output
            template_result = {
                'template_name': template_file.name,
                'analysis': analysis,
                'quality': quality
            }
            assessment_data['templates'].append(template_result)
            
            # Display results
            click.echo(f"Root class: {analysis['root_class']}")
            click.echo(f"Entities: {analysis['total_entities']} | Relationships: {analysis['total_relationships']}")
            click.echo(f"Coverage: {analysis['coverage_percent']:.1f}% | Relationship density: {analysis['relationship_density']:.1f}%")
            click.echo(f"Quality score: {quality['overall_score']}/100")
            
            # Show field breakdown
            if verbose:
                click.echo(f"\nField types:")
                for field_type, count in analysis['field_counts'].items():
                    click.echo(f"  {field_type}: {count}")
            
            # Show issues
            if quality['issues']:
                click.echo(f"\n⚠️  Issues:")
                for issue in quality['issues']:
                    click.echo(f"  {issue}")
            
            # Show strengths
            if quality['strengths']:
                click.echo(f"\n✅ Strengths:")
                for strength in quality['strengths']:
                    click.echo(f"  {strength}")
                    
        except Exception as e:
            click.echo(f"❌ Error analyzing {template_file.name}: {e}", err=True)
    
    # Summary across all templates
    if len(all_analyses) > 1:
        click.echo(f"\n{'='*50}")
        click.echo("SUMMARY ACROSS TEMPLATES")
        click.echo("=" * 50)
        
        avg_coverage = sum(a[1]['coverage_percent'] for a in all_analyses) / len(all_analyses)
        avg_density = sum(a[1]['relationship_density'] for a in all_analyses) / len(all_analyses)
        avg_score = sum(a[2]['overall_score'] for a in all_analyses) / len(all_analyses)
        
        summary_text = [
            f"Average coverage: {avg_coverage:.1f}%",
            f"Average relationship density: {avg_density:.1f}%",
            f"Average quality score: {avg_score:.1f}/100"
        ]
        
        for line in summary_text:
            click.echo(line)
        
        # Store summary for JSON
        assessment_data['summary'] = {
            'total_templates': len(all_analyses),
            'average_coverage': avg_coverage,
            'average_density': avg_density,
            'average_score': avg_score
        }
        
        # Common issues
        all_issues = []
        for _, _, quality in all_analyses:
            all_issues.extend(quality['issues'])
        
        if all_issues:
            click.echo(f"\nMost common issues:")
            issue_counts = defaultdict(int)
            for issue in all_issues:
                # Group similar issues
                if "coverage" in issue.lower():
                    issue_counts["Incomplete entity coverage"] += 1
                elif "density" in issue.lower():
                    issue_counts["Low relationship density"] += 1
                elif "string fields" in issue.lower():
                    issue_counts["Too many string fields"] += 1
            
            common_issues = []
            for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
                issue_text = f"  {issue}: {count}/{len(all_analyses)} templates"
                click.echo(issue_text)
                common_issues.append({'issue': issue, 'count': count, 'total': len(all_analyses)})
            
            assessment_data['summary']['common_issues'] = common_issues
    
    # Save output
    try:
        with open(output, 'w') as f:
            if output_format == 'json':
                json.dump(assessment_data, f, indent=2, default=str)
            else:
                # Save text output (simplified version for logs)
                f.write(f"Template Quality Assessment - {assessment_data['timestamp']}\n")
                f.write("=" * 50 + "\n\n")
                
                for template_data in assessment_data['templates']:
                    analysis = template_data['analysis']
                    quality = template_data['quality']
                    f.write(f"Template: {template_data['template_name']}\n")
                    f.write(f"Coverage: {analysis['coverage_percent']:.1f}% | ")
                    f.write(f"Density: {analysis['relationship_density']:.1f}% | ")
                    f.write(f"Score: {quality['overall_score']}/100\n")
                    if quality['issues']:
                        f.write(f"Issues: {'; '.join(quality['issues'][:2])}\n")
                    f.write("\n")
                
                if 'summary' in assessment_data:
                    f.write(f"Summary:\n")
                    f.write(f"Average coverage: {assessment_data['summary']['average_coverage']:.1f}%\n")
                    f.write(f"Average density: {assessment_data['summary']['average_density']:.1f}%\n")
                    f.write(f"Average score: {assessment_data['summary']['average_score']:.1f}/100\n")
        
        click.echo(f"\n💾 Assessment saved to: {output}")
        
    except Exception as e:
        click.echo(f"❌ Error saving output to {output}: {e}", err=True)
        raise click.Abort()

if __name__ == "__main__":
    main()