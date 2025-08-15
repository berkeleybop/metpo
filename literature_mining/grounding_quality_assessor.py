#!/usr/bin/env python3
"""
Grounding Quality Assessor for OntoGPT Extractions.

This script analyzes the quality of ontology grounding in OntoGPT extractions:
1. Grounding success rate (ontology-grounded vs AUTO: entries)
2. Ontology coverage and distribution
3. Raw completion vs structured extraction conversion rate
4. Entity normalization quality
5. Cross-template grounding consistency
"""

import yaml
import click
import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
from urllib.parse import unquote

def parse_extraction_file(extraction_file):
    """Parse OntoGPT extraction YAML file into individual extractions."""
    with open(extraction_file, 'r') as f:
        content = f.read()
    
    # Split by document separator and parse each
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

def analyze_grounding_quality(extraction):
    """Analyze grounding quality for a single extraction."""
    # named_entities is at document level, not in extracted_object
    named_entities = extraction.get('named_entities', [])
    
    grounding_stats = {
        'total_entities': len(named_entities),
        'grounded_entities': 0,
        'auto_entities': 0,
        'ontology_distribution': defaultdict(int),
        'auto_patterns': defaultdict(int),
        'entity_types': defaultdict(int)
    }
    
    for entity in named_entities:
        # Handle both dictionary and object formats
        if isinstance(entity, dict):
            entity_dict = entity
        elif hasattr(entity, '__dict__'):
            entity_dict = vars(entity)
        else:
            # Try to access as attributes
            entity_dict = {
                'id': getattr(entity, 'id', ''),
                'label': getattr(entity, 'label', '')
            }
            
        entity_id = entity_dict.get('id', '')
        entity_label = entity_dict.get('label', '')
        
        if entity_id.startswith('AUTO:'):
            grounding_stats['auto_entities'] += 1
            # Analyze AUTO patterns
            auto_content = entity_id[5:]  # Remove 'AUTO:' prefix
            decoded_content = unquote(auto_content)
            grounding_stats['auto_patterns'][_classify_auto_pattern(decoded_content)] += 1
        else:
            grounding_stats['grounded_entities'] += 1
            # Extract ontology prefix
            if ':' in entity_id:
                ontology_prefix = entity_id.split(':')[0]
                grounding_stats['ontology_distribution'][ontology_prefix] += 1
        
        # Classify entity type based on label patterns
        entity_type = _classify_entity_type(entity_label)
        grounding_stats['entity_types'][entity_type] += 1
    
    return grounding_stats

def _classify_auto_pattern(auto_content):
    """Classify AUTO: patterns to understand what's not being grounded."""
    auto_content = auto_content.lower()
    
    if re.search(r'\b(strain|isolate)\b', auto_content):
        return 'strain_designation'
    elif re.search(r'\b\d+[tT]\b', auto_content):
        return 'type_strain'
    elif re.search(r'\b(atcc|dsm|jcm|ccug|nrrl|lmg|mccc|kctc|nbrc|cect)\b', auto_content):
        return 'culture_collection'
    elif re.search(r'\bc\d+:\d+', auto_content):
        return 'fatty_acid'
    elif re.search(r'\b(catalase|oxidase|urease|protease|lipase|amylase)\b', auto_content):
        return 'enzyme_activity'
    elif re.search(r'\b(positive|negative|activity)\b', auto_content):
        return 'test_result'
    else:
        return 'other'

def _classify_entity_type(label):
    """Classify entity type based on label patterns."""
    if not label:
        return 'unknown'
    
    label_lower = label.lower()
    
    # Taxonomic entities
    if any(tax_indicator in label_lower for tax_indicator in ['bacterium', 'bacteria', 'sp.', 'gen.', 'coccus', 'bacillus']):
        return 'taxon'
    
    # Strain designations
    if re.search(r'\b\d+[tT]\b', label) or any(cc in label for cc in ['ATCC', 'DSM', 'JCM']):
        return 'strain'
    
    # Chemical compounds
    if re.search(r'\bc\d+:\d+', label_lower) or 'acid' in label_lower:
        return 'chemical'
    
    # Enzyme activities
    if any(enzyme in label_lower for enzyme in ['catalase', 'oxidase', 'urease', 'protease', 'lipase']):
        return 'enzyme'
    
    # Locations/environments
    if any(loc in label_lower for loc in ['soil', 'water', 'marine', 'sediment']):
        return 'environment'
    
    return 'other'

def analyze_raw_vs_structured(extraction):
    """Compare raw completion output vs structured extraction."""
    raw_output = extraction.get('raw_completion_output', '')
    extracted_object = extraction.get('extracted_object', {})
    
    # Parse raw output fields
    raw_fields = {}
    for line in raw_output.split('\n'):
        line = line.strip()
        if ':' in line and not line.startswith(' '):
            field_name, content = line.split(':', 1)
            field_name = field_name.strip()
            content = content.strip()
            if content:
                raw_fields[field_name] = content
    
    # Count structured fields (excluding metadata)
    structured_fields = {k: v for k, v in extracted_object.items() 
                        if k not in ['pmid', 'source_text', 'named_entities'] and v}
    
    conversion_stats = {
        'raw_fields_with_content': len([f for f in raw_fields.values() if f]),
        'structured_fields_with_content': len(structured_fields),
        'raw_relationship_fields': len([f for f in raw_fields.keys() if 'relationship' in f.lower()]),
        'structured_relationship_fields': len([f for f in structured_fields.keys() if 'relationship' in f.lower()]),
        'conversion_rate': 0,
        'relationship_conversion_rate': 0
    }
    
    if conversion_stats['raw_fields_with_content'] > 0:
        conversion_stats['conversion_rate'] = (
            conversion_stats['structured_fields_with_content'] / 
            conversion_stats['raw_fields_with_content'] * 100
        )
    
    if conversion_stats['raw_relationship_fields'] > 0:
        conversion_stats['relationship_conversion_rate'] = (
            conversion_stats['structured_relationship_fields'] / 
            conversion_stats['raw_relationship_fields'] * 100
        )
    
    return conversion_stats

@click.command()
@click.argument('extraction_path', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path),
              help='Output file for grounding assessment (default: grounding_assessment_TIMESTAMP.json)')
@click.option('--format', 'output_format', type=click.Choice(['json', 'text']), default='text',
              help='Output format: json or text (default: text)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(extraction_path, output, output_format, verbose):
    """Assess grounding quality in OntoGPT extractions.
    
    EXTRACTION_PATH can be a single extraction file or directory containing extraction files.
    """
    
    if extraction_path.is_file():
        extraction_files = [extraction_path]
    elif extraction_path.is_dir():
        extraction_files = list(extraction_path.glob("*.yaml"))
        if not extraction_files:
            click.echo(f"No YAML files found in {extraction_path}", err=True)
            raise click.Abort()
    else:
        click.echo(f"Error: {extraction_path} is not a valid file or directory", err=True)
        raise click.Abort()
    
    # Set default output file if not provided
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = 'json' if output_format == 'json' else 'txt'
        output = Path(f"grounding_assessment_{timestamp}.{suffix}")
    
    # Prepare assessment data
    assessment_data = {
        'timestamp': datetime.now().isoformat(),
        'extraction_files': [str(f) for f in extraction_files],
        'file_assessments': [],
        'summary': {}
    }
    
    click.echo("Grounding Quality Assessment")
    click.echo("=" * 50)
    click.echo(f"Processing {len(extraction_files)} file(s)")
    
    total_grounding_stats = defaultdict(int)
    total_conversion_stats = defaultdict(float)
    total_extractions = 0
    
    for extraction_file in sorted(extraction_files):
        if verbose:
            click.echo(f"\n📄 Processing: {extraction_file.name}")
        
        extractions = parse_extraction_file(extraction_file)
        file_assessment = {
            'file_name': extraction_file.name,
            'extraction_count': len(extractions),
            'extractions': []
        }
        
        for extraction in extractions:
            grounding_stats = analyze_grounding_quality(extraction)
            conversion_stats = analyze_raw_vs_structured(extraction)
            
            extraction_assessment = {
                'pmid': extraction.get('extracted_object', {}).get('pmid', 'unknown'),
                'grounding': grounding_stats,
                'conversion': conversion_stats
            }
            
            file_assessment['extractions'].append(extraction_assessment)
            
            # Aggregate stats
            for key, value in grounding_stats.items():
                if isinstance(value, (int, float)):
                    total_grounding_stats[key] += value
                elif isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        total_grounding_stats[f"{key}_{subkey}"] += subvalue
            
            for key, value in conversion_stats.items():
                total_conversion_stats[key] += value
            
            total_extractions += 1
        
        assessment_data['file_assessments'].append(file_assessment)
        
        if verbose:
            file_grounding_rate = (
                sum(e['grounding']['grounded_entities'] for e in file_assessment['extractions']) /
                max(sum(e['grounding']['total_entities'] for e in file_assessment['extractions']), 1) * 100
            )
            click.echo(f"  Grounding rate: {file_grounding_rate:.1f}%")
    
    # Calculate summary statistics
    if total_extractions > 0:
        grounding_rate = (total_grounding_stats['grounded_entities'] / 
                         max(total_grounding_stats['total_entities'], 1) * 100)
        auto_rate = (total_grounding_stats['auto_entities'] / 
                    max(total_grounding_stats['total_entities'], 1) * 100)
        avg_conversion_rate = total_conversion_stats['conversion_rate'] / total_extractions
        avg_relationship_conversion = total_conversion_stats['relationship_conversion_rate'] / total_extractions
        
        click.echo(f"\nSUMMARY:")
        click.echo(f"  Total extractions: {total_extractions}")
        click.echo(f"  Total entities: {total_grounding_stats['total_entities']}")
        click.echo(f"  Grounding rate: {grounding_rate:.1f}%")
        click.echo(f"  AUTO entities: {auto_rate:.1f}%")
        click.echo(f"  Field conversion rate: {avg_conversion_rate:.1f}%")
        click.echo(f"  Relationship conversion rate: {avg_relationship_conversion:.1f}%")
        
        # Show top ontologies
        ontology_counts = {}
        auto_pattern_counts = {}
        entity_type_counts = {}
        
        for file_assessment in assessment_data['file_assessments']:
            for extraction in file_assessment['extractions']:
                grounding = extraction['grounding']
                for ont, count in grounding['ontology_distribution'].items():
                    ontology_counts[ont] = ontology_counts.get(ont, 0) + count
                for pattern, count in grounding['auto_patterns'].items():
                    auto_pattern_counts[pattern] = auto_pattern_counts.get(pattern, 0) + count
                for etype, count in grounding['entity_types'].items():
                    entity_type_counts[etype] = entity_type_counts.get(etype, 0) + count
        
        if ontology_counts:
            click.echo(f"\nTop ontologies:")
            for ont, count in sorted(ontology_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                click.echo(f"  {ont}: {count} entities")
        
        if auto_pattern_counts:
            click.echo(f"\nAUTO patterns:")
            for pattern, count in sorted(auto_pattern_counts.items(), key=lambda x: x[1], reverse=True):
                click.echo(f"  {pattern}: {count} entities")
        
        # Store summary for JSON
        assessment_data['summary'] = {
            'total_extractions': total_extractions,
            'total_entities': total_grounding_stats['total_entities'],
            'grounding_rate': grounding_rate,
            'auto_rate': auto_rate,
            'field_conversion_rate': avg_conversion_rate,
            'relationship_conversion_rate': avg_relationship_conversion,
            'top_ontologies': ontology_counts,
            'auto_patterns': auto_pattern_counts,
            'entity_types': entity_type_counts
        }
    
    # Save output
    try:
        with open(output, 'w') as f:
            if output_format == 'json':
                json.dump(assessment_data, f, indent=2, default=str)
            else:
                # Save text output
                f.write(f"Grounding Quality Assessment - {assessment_data['timestamp']}\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Source files: {len(assessment_data['extraction_files'])} file(s)\n")
                for file_path in assessment_data['extraction_files']:
                    f.write(f"  - {file_path}\n")
                f.write("\n")
                
                if 'summary' in assessment_data:
                    f.write("Overall Summary:\n")
                    f.write(f"  Total extractions: {assessment_data['summary']['total_extractions']}\n")
                    f.write(f"  Total entities: {assessment_data['summary']['total_entities']}\n")
                    f.write(f"  Grounding rate: {assessment_data['summary']['grounding_rate']:.1f}%\n")
                    f.write(f"  AUTO entities: {assessment_data['summary']['auto_rate']:.1f}%\n")
                    f.write(f"  Field conversion: {assessment_data['summary']['field_conversion_rate']:.1f}%\n")
                    f.write(f"  Relationship conversion: {assessment_data['summary']['relationship_conversion_rate']:.1f}%\n")
                    
                    f.write("\nTop Ontologies:\n")
                    for ont, count in sorted(assessment_data['summary']['top_ontologies'].items(), 
                                           key=lambda x: x[1], reverse=True)[:5]:
                        f.write(f"  {ont}: {count}\n")
                    
                    f.write("\nAUTO Patterns:\n")
                    for pattern, count in sorted(assessment_data['summary']['auto_patterns'].items(), 
                                               key=lambda x: x[1], reverse=True):
                        f.write(f"  {pattern}: {count}\n")
        
        click.echo(f"\n💾 Grounding assessment saved to: {output}")
        
    except Exception as e:
        click.echo(f"❌ Error saving output to {output}: {e}", err=True)
        raise click.Abort()

if __name__ == "__main__":
    main()