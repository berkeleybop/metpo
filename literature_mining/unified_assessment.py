#!/usr/bin/env python3
"""
Unified Literature Mining Assessment Tool

Integrates template quality, entity-relationship conversion, and grounding analysis
into a comprehensive pipeline health assessment. Provides goal-aligned reporting
following the raw→parsing→grounding→relationships pipeline.
"""

import yaml
import click
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import re

# Import individual assessors
from template_quality_assessor import assess_template_quality
# Entity-relationship assessment functionality (was in deleted entity_relationship_assessment.py)
def assess_extraction(extraction, template_schema=None):
    """Simple relationship assessment to replace deleted functionality."""
    extracted_object = extraction.get('extracted_object', {})
    named_entities = extraction.get('named_entities', [])
    
    # Count relationships (fields that contain lists or compound expressions)
    total_relationships = 0
    for field_name, field_value in extracted_object.items():
        if isinstance(field_value, list) and field_value:
            total_relationships += len(field_value)
        elif field_value and field_name not in ['pmid', 'source_text']:
            total_relationships += 1
    
    # Basic coverage calculation
    total_entities = len(named_entities)
    coverage_percent = (total_relationships / max(total_entities, 1)) * 100 if total_entities > 0 else 0
    
    return {
        'total_relationships': total_relationships,
        'total_entities': total_entities,
        'coverage_percent': coverage_percent
    }
# Grounding quality assessment functionality (was in deleted grounding_quality_assessor.py)
def analyze_grounding_quality(extraction):
    """Simple grounding analysis to replace deleted functionality."""
    named_entities = extraction.get('named_entities', [])
    
    total_entities = len(named_entities)
    grounded_entities = 0
    
    for entity in named_entities:
        if isinstance(entity, dict):
            entity_id = entity.get('id', '')
        else:
            entity_id = getattr(entity, 'id', '')
        
        # Count as grounded if it has a proper ontology ID (not AUTO:)
        if entity_id and not entity_id.startswith('AUTO:'):
            grounded_entities += 1
    
    return {
        'total_entities': total_entities,
        'grounded_entities': grounded_entities
    }

def analyze_raw_vs_structured(extraction):
    """Analyze raw completion vs structured extraction quality."""
    raw_output = extraction.get('raw_completion_output', '')
    extracted_object = extraction.get('extracted_object', {})
    
    # Count raw fields (lines with colons that aren't indented)
    raw_fields = len([line for line in raw_output.split('\n') 
                     if ':' in line and line.strip() and not line.startswith(' ')])
    
    # Count structured fields
    structured_fields = len([v for k, v in extracted_object.items() 
                           if k not in ['pmid', 'source_text', 'named_entities'] and v])
    
    return {
        'raw_fields': raw_fields,
        'structured_fields': structured_fields,
        'parsing_success_rate': (structured_fields / max(raw_fields, 1)) * 100
    }

def clean_entity_text(text):
    """Clean entity text for matching."""
    if not text:
        return ""
    # Remove common prefixes/suffixes that might not appear in source
    text = re.sub(r'^(strain\s+|isolate\s+)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+(sp\.?\s+nov\.?|gen\.?\s+nov\.?)$', '', text, flags=re.IGNORECASE)
    return text.strip()

def find_text_spans(source_text, entity_text, fuzzy=True):
    """Find all spans where entity text appears in source text."""
    spans = []
    if not entity_text or len(entity_text) < 3:
        return spans
    
    # Exact matches first
    for match in re.finditer(re.escape(entity_text), source_text, re.IGNORECASE):
        spans.append((match.start(), match.end()))
    
    if fuzzy and not spans:
        # Try partial matches for compound terms
        words = entity_text.split()
        if len(words) > 1:
            for word in words:
                if len(word) > 3:  # Skip short words
                    for match in re.finditer(re.escape(word), source_text, re.IGNORECASE):
                        spans.append((match.start(), match.end()))
    
    return spans

def analyze_text_coverage(extraction):
    """Analyze what percentage of source text is covered by extracted entities."""
    source_text = extraction.get('source_text', '')
    named_entities = extraction.get('named_entities', [])
    
    if not source_text:
        return {
            'text_coverage_percent': 0,
            'covered_characters': 0,
            'total_characters': 0,
            'entity_find_rate': 0,
            'entities_found_in_text': 0,
            'total_entities': len(named_entities)
        }
    
    total_chars = len(source_text)
    covered_chars = set()
    entities_found = 0
    
    # Analyze named entities
    for entity in named_entities:
        if isinstance(entity, dict):
            entity_text = entity.get('label', '') or entity.get('id', '')
        else:
            entity_text = str(entity)
        
        entity_text = clean_entity_text(entity_text)
        spans = find_text_spans(source_text, entity_text)
        
        if spans:
            entities_found += 1
            for start, end in spans:
                covered_chars.update(range(start, end))
    
    # Calculate metrics
    covered_char_count = len(covered_chars)
    coverage_percent = (covered_char_count / total_chars) * 100 if total_chars > 0 else 0
    entity_find_rate = (entities_found / len(named_entities)) * 100 if named_entities else 0
    
    return {
        'text_coverage_percent': coverage_percent,
        'covered_characters': covered_char_count,
        'total_characters': total_chars,
        'entity_find_rate': entity_find_rate,
        'entities_found_in_text': entities_found,
        'total_entities': len(named_entities)
    }

def detect_template_from_filename(filename):
    """Detect template type from extraction filename."""
    filename_lower = filename.lower()
    for template in ['biochemical', 'growth_conditions', 'morphology', 'chemical_utilization', 'taxa']:
        if template in filename_lower:
            return template
    return 'unknown'

def load_template_schema(template_name):
    """Load template schema for template-informed analysis."""
    template_path = Path(f"templates/{template_name}_populated.yaml")
    if not template_path.exists():
        template_path = Path(f"templates/{template_name}_template_base.yaml")
    
    if template_path.exists():
        try:
            with open(template_path) as f:
                return yaml.safe_load(f)
        except Exception:
            pass
    return None

def parse_extraction_file(extraction_file):
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

def calculate_pipeline_metrics(extractions, template_schema=None):
    """Calculate comprehensive pipeline metrics."""
    metrics = {
        'total_extractions': len(extractions),
        'raw_quality': {'field_completion': 0, 'entity_density': 0},
        'parsing_quality': {'extraction_success': 0, 'relationship_parsing': 0},
        'grounding_quality': {'grounding_rate': 0, 'auto_rate': 0},
        'relationship_quality': {'conversion_rate': 0, 'completeness': 0}
    }
    
    if not extractions:
        return metrics
    
    total_raw_fields = 0
    total_structured_fields = 0
    total_entities = 0
    total_grounded = 0
    total_relationships = 0
    total_entity_relationship_coverage = 0
    total_text_coverage = 0
    total_entity_find_rate = 0
    total_chars_analyzed = 0
    total_chars_covered = 0
    
    for extraction in extractions:
        # Raw quality analysis
        raw_output = extraction.get('raw_completion_output', '')
        raw_fields = len([line for line in raw_output.split('\n') 
                         if ':' in line and line.strip() and not line.startswith(' ')])
        total_raw_fields += raw_fields
        
        # Parsing quality analysis
        extracted_object = extraction.get('extracted_object', {})
        structured_fields = len([v for k, v in extracted_object.items() 
                               if k not in ['pmid', 'source_text', 'named_entities'] and v])
        total_structured_fields += structured_fields
        
        # Grounding analysis
        grounding_stats = analyze_grounding_quality(extraction)
        total_entities += grounding_stats['total_entities']
        total_grounded += grounding_stats['grounded_entities']
        
        # Text coverage analysis
        coverage_stats = analyze_text_coverage(extraction)
        total_text_coverage += coverage_stats['text_coverage_percent']
        total_entity_find_rate += coverage_stats['entity_find_rate']
        total_chars_analyzed += coverage_stats['total_characters']
        total_chars_covered += coverage_stats['covered_characters']
        
        # Relationship analysis
        if template_schema:
            rel_assessment = assess_extraction(extraction, template_schema)
            total_relationships += rel_assessment['total_relationships']
            if rel_assessment['total_entities'] > 0:
                total_entity_relationship_coverage += rel_assessment['coverage_percent']
    
    # Calculate averages
    if len(extractions) > 0:
        metrics['raw_quality']['field_completion'] = total_raw_fields / len(extractions)
        metrics['parsing_quality']['extraction_success'] = (total_structured_fields / max(total_raw_fields, 1)) * 100
        metrics['grounding_quality']['grounding_rate'] = (total_grounded / max(total_entities, 1)) * 100
        metrics['grounding_quality']['auto_rate'] = ((total_entities - total_grounded) / max(total_entities, 1)) * 100
        
        # Text coverage metrics
        metrics['text_coverage'] = {
            'average_coverage_percent': total_text_coverage / len(extractions),
            'average_entity_find_rate': total_entity_find_rate / len(extractions),
            'total_characters_analyzed': total_chars_analyzed,
            'total_characters_covered': total_chars_covered,
            'overall_coverage_percent': (total_chars_covered / max(total_chars_analyzed, 1)) * 100
        }
        
        metrics['relationship_quality']['conversion_rate'] = total_entity_relationship_coverage / len(extractions)
        metrics['relationship_quality']['avg_relationships'] = total_relationships / len(extractions)
    
    return metrics

def assess_template_specialization(extraction_files):
    """Analyze template overlap and specialization."""
    template_entities = defaultdict(set)
    template_fields = defaultdict(set)
    
    for file_path in extraction_files:
        template_name = detect_template_from_filename(file_path.name)
        extractions = parse_extraction_file(file_path)
        
        for extraction in extractions:
            extracted_object = extraction.get('extracted_object', {})
            named_entities = extraction.get('named_entities', [])
            
            # Collect entity types and field types
            for field_name, field_data in extracted_object.items():
                if field_name not in ['pmid', 'source_text', 'named_entities']:
                    template_fields[template_name].add(field_name)
            
            for entity in named_entities:
                if isinstance(entity, dict):
                    entity_label = entity.get('label', '')
                elif hasattr(entity, 'label'):
                    entity_label = entity.label
                else:
                    entity_label = str(entity)
                
                if entity_label:
                    template_entities[template_name].add(entity_label.lower())
    
    # Calculate overlap metrics
    overlap_analysis = {}
    template_names = list(template_entities.keys())
    
    for i, template1 in enumerate(template_names):
        for template2 in template_names[i+1:]:
            entities1 = template_entities[template1]
            entities2 = template_entities[template2]
            
            if entities1 and entities2:
                overlap = len(entities1.intersection(entities2))
                total_unique = len(entities1.union(entities2))
                overlap_rate = (overlap / total_unique * 100) if total_unique > 0 else 0
                
                overlap_analysis[f"{template1}_vs_{template2}"] = {
                    'shared_entities': overlap,
                    'total_unique': total_unique,
                    'overlap_rate': overlap_rate
                }
    
    return {
        'template_entities': {k: len(v) for k, v in template_entities.items()},
        'template_fields': {k: list(v) for k, v in template_fields.items()},
        'overlap_analysis': overlap_analysis
    }

@click.command()
@click.argument('extraction_path', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path),
              help='Output file for unified assessment (default: unified_assessment_TIMESTAMP.json)')
@click.option('--format', 'output_format', type=click.Choice(['json', 'text']), default='json',
              help='Output format: json or text (default: json)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--include-specialization', is_flag=True, 
              help='Include template specialization analysis (requires directory input)')
def main(extraction_path, output, output_format, verbose, include_specialization):
    """Comprehensive literature mining pipeline assessment.
    
    EXTRACTION_PATH can be a single extraction file or directory containing extraction files.
    Provides unified analysis across raw LLM quality, parsing quality, grounding quality,
    and relationship quality following the assessment roadmap.
    """
    
    # Collect extraction files
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
    
    # Set default output file
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = 'json' if output_format == 'json' else 'txt'
        output = Path(f"unified_assessment_{timestamp}.{suffix}")
    
    # Initialize assessment data
    assessment_data = {
        'timestamp': datetime.now().isoformat(),
        'extraction_files': [str(f) for f in extraction_files],
        'pipeline_summary': {},
        'template_assessments': [],
        'success_metrics': {}
    }
    
    click.echo("🔬 Unified Literature Mining Assessment")
    click.echo("=" * 50)
    click.echo(f"Processing {len(extraction_files)} file(s)")
    
    # Process each template/file
    template_metrics = {}
    all_extractions = []
    
    for extraction_file in sorted(extraction_files):
        template_name = detect_template_from_filename(extraction_file.name)
        template_schema = load_template_schema(template_name)
        
        if verbose:
            click.echo(f"\n📄 Processing: {extraction_file.name} ({template_name})")
        
        extractions = parse_extraction_file(extraction_file)
        all_extractions.extend(extractions)
        
        # Calculate template-specific metrics
        metrics = calculate_pipeline_metrics(extractions, template_schema)
        template_metrics[template_name] = metrics
        
        template_assessment = {
            'template_name': template_name,
            'file_name': extraction_file.name,
            'extraction_count': len(extractions),
            'metrics': metrics
        }
        
        assessment_data['template_assessments'].append(template_assessment)
        
        if verbose:
            click.echo(f"  📊 Extractions: {metrics['total_extractions']}")
            click.echo(f"  📝 Raw quality: {metrics['raw_quality']['field_completion']:.1f} fields/extraction")
            click.echo(f"  🔧 Parsing: {metrics['parsing_quality']['extraction_success']:.1f}% success rate")
            click.echo(f"  🏷️  Grounding: {metrics['grounding_quality']['grounding_rate']:.1f}% grounded")
            click.echo(f"  🔗 Relationships: {metrics['relationship_quality']['avg_relationships']:.1f}/extraction")
            click.echo(f"  📄 Text coverage: {metrics['text_coverage']['average_coverage_percent']:.1f}% chars covered")
            click.echo(f"  🔍 Entity matching: {metrics['text_coverage']['average_entity_find_rate']:.1f}% entities found in text")
    
    # Calculate overall pipeline metrics
    overall_metrics = calculate_pipeline_metrics(all_extractions)
    assessment_data['pipeline_summary'] = overall_metrics
    
    # Template specialization analysis
    if include_specialization and extraction_path.is_dir():
        specialization = assess_template_specialization(extraction_files)
        assessment_data['template_specialization'] = specialization
        
        if verbose:
            click.echo(f"\n🎯 Template Specialization Analysis")
            click.echo(f"Templates analyzed: {list(specialization['template_entities'].keys())}")
            for overlap_key, overlap_data in specialization['overlap_analysis'].items():
                click.echo(f"  {overlap_key}: {overlap_data['overlap_rate']:.1f}% overlap")
    
    # Success metrics evaluation
    success_metrics = {
        'raw_quality_target': overall_metrics['raw_quality']['field_completion'] >= 5,  # >5 fields/extraction
        'parsing_target': overall_metrics['parsing_quality']['extraction_success'] >= 80,  # >80% parsing
        'grounding_target': overall_metrics['grounding_quality']['grounding_rate'] >= 60,  # >60% grounding
        'relationship_target': overall_metrics['relationship_quality']['conversion_rate'] >= 80,  # >80% rel conversion
        'auto_entities_target': overall_metrics['grounding_quality']['auto_rate'] <= 20  # <20% AUTO
    }
    
    assessment_data['success_metrics'] = success_metrics
    targets_met = sum(success_metrics.values())
    
    # Display summary
    click.echo(f"\n📈 PIPELINE SUMMARY")
    click.echo(f"  Total extractions: {overall_metrics['total_extractions']}")
    click.echo(f"  Raw quality: {overall_metrics['raw_quality']['field_completion']:.1f} fields/extraction")
    click.echo(f"  Parsing success: {overall_metrics['parsing_quality']['extraction_success']:.1f}%")
    click.echo(f"  Grounding rate: {overall_metrics['grounding_quality']['grounding_rate']:.1f}%")
    click.echo(f"  Avg relationships: {overall_metrics['relationship_quality']['avg_relationships']:.1f}/extraction")
    click.echo(f"  Text coverage: {overall_metrics['text_coverage']['overall_coverage_percent']:.1f}% ({overall_metrics['text_coverage']['total_characters_covered']:,}/{overall_metrics['text_coverage']['total_characters_analyzed']:,} chars)")
    click.echo(f"  Entity matching: {overall_metrics['text_coverage']['average_entity_find_rate']:.1f}% entities found in source text")
    click.echo(f"  Success targets met: {targets_met}/5")
    
    # Save output
    try:
        with open(output, 'w') as f:
            if output_format == 'json':
                json.dump(assessment_data, f, indent=2, default=str)
            else:
                # Text format output
                f.write(f"Unified Literature Mining Assessment - {assessment_data['timestamp']}\n")
                f.write("=" * 60 + "\n\n")
                
                f.write("PIPELINE SUMMARY:\n")
                f.write(f"  Total extractions: {overall_metrics['total_extractions']}\n")
                f.write(f"  Raw quality: {overall_metrics['raw_quality']['field_completion']:.1f} fields/extraction\n")
                f.write(f"  Parsing success: {overall_metrics['parsing_quality']['extraction_success']:.1f}%\n")
                f.write(f"  Grounding rate: {overall_metrics['grounding_quality']['grounding_rate']:.1f}%\n")
                f.write(f"  Avg relationships: {overall_metrics['relationship_quality']['avg_relationships']:.1f}/extraction\n")
                f.write(f"  Success targets met: {targets_met}/5\n\n")
                
                f.write("TEMPLATE BREAKDOWN:\n")
                for template_assessment in assessment_data['template_assessments']:
                    metrics = template_assessment['metrics']
                    f.write(f"  {template_assessment['template_name']}: {metrics['total_extractions']} extractions\n")
                    f.write(f"    Relationships: {metrics['relationship_quality']['avg_relationships']:.1f}/extraction\n")
                    f.write(f"    Grounding: {metrics['grounding_quality']['grounding_rate']:.1f}%\n")
                
                if 'template_specialization' in assessment_data:
                    f.write("\nTEMPLATE SPECIALIZATION:\n")
                    for overlap_key, overlap_data in assessment_data['template_specialization']['overlap_analysis'].items():
                        f.write(f"  {overlap_key}: {overlap_data['overlap_rate']:.1f}% overlap\n")
        
        click.echo(f"\n💾 Unified assessment saved to: {output}")
        
    except Exception as e:
        click.echo(f"❌ Error saving output to {output}: {e}", err=True)
        raise click.Abort()

if __name__ == "__main__":
    main()