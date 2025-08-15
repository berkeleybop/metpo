#!/usr/bin/env python3
"""
Template Specialization Analysis Tool

Analyzes template overlap, sensitivity, and specificity to optimize
template boundaries and minimize redundant extractions while maximizing
coverage of domain-specific content.

Phase 3 implementation from ASSESSMENT_ROADMAP.md
"""

import yaml
import click
import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Set, Tuple

def parse_extraction_file(extraction_file: Path) -> List[dict]:
    """Parse OntoGPT extraction YAML file into individual extractions."""
    with open(extraction_file, 'r') as f:
        content = f.read()
    
    documents = content.split('---\n')
    extractions = []
    for doc in documents:
        if doc.strip():
            try:
                parsed = yaml.safe_load(doc)
                if parsed and 'extracted_object' in parsed:
                    extractions.append(parsed)
            except yaml.YAMLError:
                continue
    return extractions

def detect_template_from_filename(filename: str) -> str:
    """Detect template type from extraction filename."""
    filename_lower = filename.lower()
    for template in ['biochemical', 'growth_conditions', 'morphology', 'chemical_utilization', 'taxa']:
        if template in filename_lower:
            return template
    return 'unknown'

def extract_entities_by_field(extraction: dict) -> Dict[str, Set[str]]:
    """Extract all entities from an extraction, organized by field."""
    extracted_object = extraction.get('extracted_object', {})
    entities_by_field = defaultdict(set)
    
    for field, value in extracted_object.items():
        if field in ['pmid', 'input_text']:
            continue
            
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    # Clean entity ID for comparison
                    clean_id = item.replace('AUTO:', '').replace('%20', ' ').replace('%28', '(').replace('%29', ')')
                    entities_by_field[field].add(clean_id)
                elif isinstance(item, dict) and 'subject' in item:
                    # Handle relationship objects
                    for rel_field in ['subject', 'object']:
                        if rel_field in item:
                            rel_value = str(item[rel_field])
                            clean_id = rel_value.replace('AUTO:', '').replace('%20', ' ')
                            entities_by_field[field].add(clean_id)
        elif isinstance(value, str):
            clean_id = value.replace('AUTO:', '').replace('%20', ' ')
            entities_by_field[field].add(clean_id)
    
    return entities_by_field

def analyze_template_overlap(template_data: Dict[str, List[dict]]) -> Dict[str, dict]:
    """Analyze entity overlap between templates."""
    # Collect all entities by template
    template_entities = {}
    template_fields = {}
    
    for template_name, extractions in template_data.items():
        all_entities = set()
        all_fields = set()
        
        for extraction in extractions:
            entities_by_field = extract_entities_by_field(extraction)
            for field, entities in entities_by_field.items():
                all_entities.update(entities)
                all_fields.add(field)
        
        template_entities[template_name] = all_entities
        template_fields[template_name] = all_fields
    
    # Calculate pairwise overlaps
    overlap_analysis = {}
    template_names = list(template_entities.keys())
    
    for i, template1 in enumerate(template_names):
        for template2 in template_names[i+1:]:
            entities1 = template_entities[template1]
            entities2 = template_entities[template2]
            
            shared_entities = entities1.intersection(entities2)
            total_unique = len(entities1.union(entities2))
            overlap_rate = (len(shared_entities) / total_unique * 100) if total_unique > 0 else 0
            
            overlap_analysis[f"{template1}_vs_{template2}"] = {
                'shared_entities': len(shared_entities),
                'total_unique': total_unique,
                'overlap_rate': overlap_rate,
                'shared_examples': list(shared_entities)[:5],  # First 5 examples
                'template1_exclusive': len(entities1 - entities2),
                'template2_exclusive': len(entities2 - entities1)
            }
    
    return {
        'template_entities': {k: len(v) for k, v in template_entities.items()},
        'template_fields': {k: list(v) for k, v in template_fields.items()},
        'overlap_analysis': overlap_analysis
    }

def analyze_field_specificity(template_data: Dict[str, List[dict]]) -> Dict[str, dict]:
    """Analyze which fields are specific to each template vs shared."""
    
    # Collect field usage across templates
    field_usage = defaultdict(set)  # field -> set of templates using it
    field_entity_counts = defaultdict(lambda: defaultdict(int))  # field -> template -> count
    
    for template_name, extractions in template_data.items():
        template_fields = set()
        
        for extraction in extractions:
            entities_by_field = extract_entities_by_field(extraction)
            for field, entities in entities_by_field.items():
                field_usage[field].add(template_name)
                field_entity_counts[field][template_name] += len(entities)
                template_fields.add(field)
    
    # Categorize fields
    exclusive_fields = {}  # template -> list of exclusive fields
    shared_fields = []     # fields used by multiple templates
    
    for template_name in template_data.keys():
        exclusive_fields[template_name] = []
    
    for field, templates_using in field_usage.items():
        if len(templates_using) == 1:
            template = list(templates_using)[0]
            exclusive_fields[template].append(field)
        else:
            shared_fields.append({
                'field': field,
                'templates': list(templates_using),
                'usage_counts': dict(field_entity_counts[field])
            })
    
    return {
        'exclusive_fields': exclusive_fields,
        'shared_fields': shared_fields,
        'field_usage_matrix': {field: list(templates) for field, templates in field_usage.items()}
    }

def detect_off_topic_extractions(template_data: Dict[str, List[dict]]) -> Dict[str, dict]:
    """Detect potential off-topic extractions based on field names and content."""
    
    # Define expected field patterns for each template
    expected_patterns = {
        'biochemical': ['enzyme', 'metabolic', 'biochemical', 'fatty_acid', 'api_test'],
        'morphology': ['cell_shape', 'cell_arrangement', 'gram', 'motility', 'spore', 'morphology'],
        'growth_conditions': ['temperature', 'ph', 'oxygen', 'salt', 'atmospheric', 'culture', 'growth'],
        'chemical_utilization': ['chemical', 'utilization', 'substrate', 'carbon', 'nitrogen'],
        'taxa': ['taxa', 'strain', 'species', 'genus', 'taxonomic']
    }
    
    off_topic_analysis = {}
    
    for template_name, extractions in template_data.items():
        expected = expected_patterns.get(template_name, [])
        
        # Collect all fields used by this template
        all_fields = set()
        for extraction in extractions:
            entities_by_field = extract_entities_by_field(extraction)
            all_fields.update(entities_by_field.keys())
        
        # Identify potentially off-topic fields
        on_topic_fields = []
        off_topic_fields = []
        
        for field in all_fields:
            field_lower = field.lower()
            is_on_topic = any(pattern in field_lower for pattern in expected)
            
            # Special handling for universal fields
            if any(universal in field_lower for universal in ['strain', 'taxa', 'pmid', 'relationship']):
                is_on_topic = True
            
            if is_on_topic:
                on_topic_fields.append(field)
            else:
                off_topic_fields.append(field)
        
        off_topic_analysis[template_name] = {
            'on_topic_fields': on_topic_fields,
            'off_topic_fields': off_topic_fields,
            'specificity_score': len(on_topic_fields) / len(all_fields) * 100 if all_fields else 0,
            'total_fields': len(all_fields)
        }
    
    return off_topic_analysis

def calculate_specialization_scores(overlap_analysis: dict, specificity_analysis: dict) -> Dict[str, dict]:
    """Calculate overall specialization scores for each template."""
    
    scores = {}
    
    for template in specificity_analysis.keys():
        # Specificity score (0-100): how focused the template is on its domain
        specificity_score = specificity_analysis[template]['specificity_score']
        
        # Calculate average overlap with other templates
        overlaps = []
        for comparison, data in overlap_analysis['overlap_analysis'].items():
            if template in comparison:
                overlaps.append(data['overlap_rate'])
        
        avg_overlap = sum(overlaps) / len(overlaps) if overlaps else 0
        
        # Exclusivity score (0-100): 100 - average overlap
        exclusivity_score = 100 - avg_overlap
        
        # Overall specialization score
        specialization_score = (specificity_score + exclusivity_score) / 2
        
        scores[template] = {
            'specificity_score': specificity_score,
            'exclusivity_score': exclusivity_score,
            'specialization_score': specialization_score,
            'avg_overlap_rate': avg_overlap,
            'entity_count': overlap_analysis['template_entities'].get(template, 0)
        }
    
    return scores

@click.command()
@click.argument('extraction_path', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path),
              help='Output file for specialization analysis (default: template_specialization_TIMESTAMP.json)')
@click.option('--format', 'output_format', type=click.Choice(['json', 'text']), default='json',
              help='Output format: json or text (default: json)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(extraction_path, output, output_format, verbose):
    """Template specialization analysis for OntoGPT extractions.
    
    Analyzes template overlap, sensitivity, and specificity to optimize
    template boundaries and minimize redundant extractions.
    
    EXTRACTION_PATH can be a directory containing extraction files.
    """
    
    if not extraction_path.is_dir():
        click.echo(f"Error: {extraction_path} must be a directory containing extraction files", err=True)
        raise click.Abort()
    
    extraction_files = list(extraction_path.glob("*.yaml"))
    if not extraction_files:
        click.echo(f"No YAML files found in {extraction_path}", err=True)
        raise click.Abort()
    
    # Set default output file
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = 'json' if output_format == 'json' else 'txt'
        output = Path(f"template_specialization_{timestamp}.{suffix}")
    
    click.echo("🎯 Template Specialization Analysis")
    click.echo("=" * 50)
    click.echo(f"Processing {len(extraction_files)} file(s)")
    
    # Organize extractions by template
    template_data = defaultdict(list)
    
    for extraction_file in extraction_files:
        template_name = detect_template_from_filename(extraction_file.name)
        if template_name != 'unknown':  # Skip test files
            extractions = parse_extraction_file(extraction_file)
            template_data[template_name].extend(extractions)
            if verbose:
                click.echo(f"  📄 {extraction_file.name}: {len(extractions)} extractions ({template_name})")
    
    if not template_data:
        click.echo("No valid template extractions found", err=True)
        raise click.Abort()
    
    # Perform analyses
    click.echo("\n🔍 Analyzing template overlap...")
    overlap_analysis = analyze_template_overlap(template_data)
    
    click.echo("📊 Analyzing field specificity...")
    specificity_analysis = detect_off_topic_extractions(template_data)
    
    click.echo("📈 Analyzing field usage patterns...")
    field_analysis = analyze_field_specificity(template_data)
    
    click.echo("🎯 Calculating specialization scores...")
    specialization_scores = calculate_specialization_scores(overlap_analysis, specificity_analysis)
    
    # Create comprehensive analysis report
    analysis_data = {
        'timestamp': datetime.now().isoformat(),
        'extraction_files': [str(f) for f in extraction_files],
        'template_data_summary': {template: len(extractions) for template, extractions in template_data.items()},
        'overlap_analysis': overlap_analysis,
        'specificity_analysis': specificity_analysis,
        'field_analysis': field_analysis,
        'specialization_scores': specialization_scores,
        'recommendations': generate_recommendations(overlap_analysis, specificity_analysis, specialization_scores)
    }
    
    # Display summary
    if verbose:
        click.echo(f"\n📊 SPECIALIZATION SUMMARY")
        for template, scores in sorted(specialization_scores.items(), key=lambda x: x[1]['specialization_score'], reverse=True):
            click.echo(f"  {template}:")
            click.echo(f"    Specialization Score: {scores['specialization_score']:.1f}/100")
            click.echo(f"    Specificity: {scores['specificity_score']:.1f}% | Exclusivity: {scores['exclusivity_score']:.1f}%")
            click.echo(f"    Average Overlap: {scores['avg_overlap_rate']:.1f}% | Entities: {scores['entity_count']}")
    
    # Save output
    try:
        with open(output, 'w') as f:
            if output_format == 'json':
                json.dump(analysis_data, f, indent=2, default=str)
            else:
                write_text_report(f, analysis_data)
        
        click.echo(f"\n💾 Template specialization analysis saved to: {output}")
        
    except Exception as e:
        click.echo(f"❌ Error saving output to {output}: {e}", err=True)
        raise click.Abort()

def generate_recommendations(overlap_analysis: dict, specificity_analysis: dict, specialization_scores: dict) -> List[str]:
    """Generate actionable recommendations for template optimization."""
    
    recommendations = []
    
    # High overlap recommendations
    for comparison, data in overlap_analysis['overlap_analysis'].items():
        if data['overlap_rate'] > 15:  # >15% overlap is concerning
            recommendations.append(f"HIGH OVERLAP: {comparison} shows {data['overlap_rate']:.1f}% overlap ({data['shared_entities']} shared entities). Consider consolidating or clarifying boundaries.")
    
    # Low specificity recommendations
    for template, data in specificity_analysis.items():
        if data['specificity_score'] < 70:  # <70% on-topic is concerning
            recommendations.append(f"LOW SPECIFICITY: {template} template shows {data['specificity_score']:.1f}% specificity. Review off-topic fields: {', '.join(data['off_topic_fields'][:3])}")
    
    # Overall recommendations
    recommendations.append("RECOMMENDED ACTIONS:")
    recommendations.append("1. Review high-overlap template pairs for boundary clarification")
    recommendations.append("2. Consider field consolidation for shared non-core fields")
    recommendations.append("3. Add template-specific validation to prevent off-topic extractions")
    recommendations.append("4. Maintain strain/taxa/pmid sharing as these are universal identifiers")
    
    return recommendations

def write_text_report(f, analysis_data):
    """Write human-readable text report."""
    f.write(f"Template Specialization Analysis - {analysis_data['timestamp']}\n")
    f.write("=" * 60 + "\n\n")
    
    f.write("SPECIALIZATION SCORES:\n")
    for template, scores in sorted(analysis_data['specialization_scores'].items(), 
                                 key=lambda x: x[1]['specialization_score'], reverse=True):
        f.write(f"  {template}: {scores['specialization_score']:.1f}/100\n")
        f.write(f"    Specificity: {scores['specificity_score']:.1f}% | Exclusivity: {scores['exclusivity_score']:.1f}%\n")
        f.write(f"    Entities: {scores['entity_count']} | Avg Overlap: {scores['avg_overlap_rate']:.1f}%\n\n")
    
    f.write("HIGH OVERLAP PAIRS:\n")
    for comparison, data in analysis_data['overlap_analysis']['overlap_analysis'].items():
        if data['overlap_rate'] > 10:
            f.write(f"  {comparison}: {data['overlap_rate']:.1f}% ({data['shared_entities']} shared)\n")
    
    f.write("\nRECOMMENDATIONS:\n")
    for rec in analysis_data['recommendations']:
        f.write(f"  {rec}\n")

if __name__ == "__main__":
    main()