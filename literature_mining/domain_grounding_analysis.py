#!/usr/bin/env python3
"""
Domain-Specific Grounding Quality Analysis

Analyzes ontology grounding quality with focus on domain-specific patterns:
- Fatty acids → CHEBI mapping quality
- Enzyme activities → EC/GO coverage  
- Growth conditions → controlled vocabulary usage
- Bacterial taxa → NCBITaxon coverage
- Template-specific grounding performance patterns
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

def detect_template_from_filename(filename):
    """Detect template type from extraction filename."""
    filename_lower = filename.lower()
    for template in ['biochemical', 'growth_conditions', 'morphology', 'chemical_utilization', 'taxa']:
        if template in filename_lower:
            return template
    return 'unknown'

def classify_entity_by_content(entity_label, entity_id):
    """Classify entity by its content and expected domain."""
    if not entity_label:
        return 'unknown'
    
    label_lower = entity_label.lower()
    
    # Fatty acids
    if re.search(r'\\bc\\d+:\\d+', label_lower) or 'fatty acid' in label_lower or \
       any(fa in label_lower for fa in ['iso-c', 'anteiso-c', 'methyl', 'hydroxyl']):
        expected_ontology = 'CHEBI'
        actual_ontology = entity_id.split(':')[0] if ':' in entity_id else 'AUTO'
        return {
            'domain': 'fatty_acid',
            'expected_ontology': expected_ontology,
            'actual_ontology': actual_ontology,
            'correct_grounding': actual_ontology == expected_ontology
        }
    
    # Enzyme activities  
    if any(enzyme in label_lower for enzyme in ['catalase', 'oxidase', 'urease', 'protease', 
                                               'lipase', 'amylase', 'gelatinase', 'phosphatase']):
        expected_ontology = 'GO'  # Gene Ontology for molecular functions
        actual_ontology = entity_id.split(':')[0] if ':' in entity_id else 'AUTO'
        return {
            'domain': 'enzyme_activity',
            'expected_ontology': expected_ontology,
            'actual_ontology': actual_ontology,
            'correct_grounding': actual_ontology in ['GO', 'EC']  # EC numbers also acceptable
        }
    
    # Bacterial taxa
    if any(tax_indicator in label_lower for tax_indicator in ['bacterium', 'bacteria', 'sp.', 
                                                              'coccus', 'bacillus', 'streptococcus']):
        expected_ontology = 'NCBITaxon'
        actual_ontology = entity_id.split(':')[0] if ':' in entity_id else 'AUTO'
        return {
            'domain': 'bacterial_taxon',
            'expected_ontology': expected_ontology,
            'actual_ontology': actual_ontology,
            'correct_grounding': actual_ontology == expected_ontology
        }
    
    # Growth conditions - environmental terms
    if any(env in label_lower for env in ['temperature', 'ph', 'nacl', 'salt', 'oxygen', 
                                         'aerobic', 'anaerobic', 'atmosphere']):
        expected_ontology = 'ENVO'  # Environmental Ontology
        actual_ontology = entity_id.split(':')[0] if ':' in entity_id else 'AUTO'
        return {
            'domain': 'growth_condition',
            'expected_ontology': expected_ontology,
            'actual_ontology': actual_ontology,
            'correct_grounding': actual_ontology in ['ENVO', 'PATO']  # PATO for qualities also acceptable
        }
    
    # Chemical compounds (general)
    if any(chem in label_lower for chem in ['glucose', 'acetate', 'sulfate', 'nitrate', 
                                           'phosphate', 'carbonate']):
        expected_ontology = 'CHEBI'
        actual_ontology = entity_id.split(':')[0] if ':' in entity_id else 'AUTO'
        return {
            'domain': 'chemical_compound',
            'expected_ontology': expected_ontology,
            'actual_ontology': actual_ontology,
            'correct_grounding': actual_ontology == expected_ontology
        }
    
    # Cell morphology terms
    if any(morph in label_lower for morph in ['rod', 'coccus', 'spiral', 'filament', 
                                             'gram-positive', 'gram-negative', 'motile']):
        expected_ontology = 'METPO'  # METPO has morphology terms
        # Handle both standard URIs and METPO URIs
        if entity_id.startswith('<https://w3id.org/metpo/'):
            actual_ontology = 'METPO'
        elif ':' in entity_id:
            actual_ontology = entity_id.split(':')[0]
        else:
            actual_ontology = 'AUTO'
        return {
            'domain': 'cell_morphology',
            'expected_ontology': expected_ontology,
            'actual_ontology': actual_ontology,
            'correct_grounding': actual_ontology in ['METPO', 'PATO', 'GO']  # METPO, PATO, or GO are acceptable
        }
    
    # Strains (should typically remain AUTO)
    if re.search(r'\\b\\d+[tT]\\b', label_lower) or \
       any(cc in label_lower for cc in ['atcc', 'dsm', 'jcm', 'strain', 'isolate']):
        return {
            'domain': 'strain_designation',
            'expected_ontology': 'AUTO',
            'actual_ontology': entity_id.split(':')[0] if ':' in entity_id else 'AUTO',
            'correct_grounding': True  # AUTO is correct for strain designations
        }
    
    # Default classification
    return {
        'domain': 'other',
        'expected_ontology': 'unknown',
        'actual_ontology': entity_id.split(':')[0] if ':' in entity_id else 'AUTO',
        'correct_grounding': None
    }

def analyze_domain_grounding(extractions, template_name):
    """Analyze domain-specific grounding patterns for a template."""
    domain_stats = defaultdict(lambda: {
        'total': 0,
        'correctly_grounded': 0,
        'incorrectly_grounded': 0,
        'auto_entities': 0,
        'ontology_distribution': defaultdict(int),
        'examples': {'correct': [], 'incorrect': [], 'auto': []}
    })
    
    for extraction in extractions:
        named_entities = extraction.get('named_entities', [])
        
        for entity in named_entities:
            # Handle both dictionary and object formats
            if isinstance(entity, dict):
                entity_id = entity.get('id', '')
                entity_label = entity.get('label', '')
            elif hasattr(entity, '__dict__'):
                entity_dict = vars(entity)
                entity_id = entity_dict.get('id', '')
                entity_label = entity_dict.get('label', '')
            else:
                entity_id = getattr(entity, 'id', '')
                entity_label = getattr(entity, 'label', '')
            
            # Classify entity by domain
            classification = classify_entity_by_content(entity_label, entity_id)
            domain = classification['domain']
            
            domain_stats[domain]['total'] += 1
            domain_stats[domain]['ontology_distribution'][classification['actual_ontology']] += 1
            
            # Track grounding correctness
            if classification['correct_grounding'] is True:
                domain_stats[domain]['correctly_grounded'] += 1
                if len(domain_stats[domain]['examples']['correct']) < 3:
                    domain_stats[domain]['examples']['correct'].append({
                        'label': entity_label,
                        'id': entity_id,
                        'expected': classification['expected_ontology'],
                        'actual': classification['actual_ontology']
                    })
            elif classification['correct_grounding'] is False:
                domain_stats[domain]['incorrectly_grounded'] += 1
                if len(domain_stats[domain]['examples']['incorrect']) < 3:
                    domain_stats[domain]['examples']['incorrect'].append({
                        'label': entity_label,
                        'id': entity_id,
                        'expected': classification['expected_ontology'],
                        'actual': classification['actual_ontology']
                    })
            
            if entity_id.startswith('AUTO:'):
                domain_stats[domain]['auto_entities'] += 1
                if len(domain_stats[domain]['examples']['auto']) < 3:
                    domain_stats[domain]['examples']['auto'].append({
                        'label': entity_label,
                        'id': entity_id
                    })
    
    return dict(domain_stats)

def calculate_domain_metrics(domain_stats):
    """Calculate domain-specific grounding metrics."""
    metrics = {}
    
    for domain, stats in domain_stats.items():
        if stats['total'] > 0:
            correct_rate = (stats['correctly_grounded'] / stats['total']) * 100
            auto_rate = (stats['auto_entities'] / stats['total']) * 100
            
            # Identify problematic grounding patterns
            problematic_ontologies = []
            for ont, count in stats['ontology_distribution'].items():
                if ont.startswith('<') or ont in ['AUTO'] and domain not in ['strain_designation']:
                    if count / stats['total'] > 0.1:  # >10% problematic
                        problematic_ontologies.append(ont)
            
            metrics[domain] = {
                'total_entities': stats['total'],
                'correct_grounding_rate': correct_rate,
                'auto_rate': auto_rate,
                'ontology_distribution': dict(stats['ontology_distribution']),
                'problematic_ontologies': problematic_ontologies,
                'examples': stats['examples']
            }
    
    return metrics

@click.command()
@click.argument('extraction_path', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path),
              help='Output file for domain grounding assessment (default: domain_grounding_TIMESTAMP.json)')
@click.option('--format', 'output_format', type=click.Choice(['json', 'text']), default='json',
              help='Output format: json or text (default: json)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--template-filter', type=str,
              help='Only analyze files matching template name (biochemical, growth_conditions, etc.)')
def main(extraction_path, output, output_format, verbose, template_filter):
    """Domain-specific grounding quality analysis for OntoGPT extractions.
    
    EXTRACTION_PATH can be a single extraction file or directory containing extraction files.
    Analyzes grounding patterns by domain (fatty acids, enzymes, taxa, etc.) and provides
    recommendations for improving ontology mapping quality.
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
    
    # Filter by template if specified
    if template_filter:
        extraction_files = [f for f in extraction_files if template_filter.lower() in f.name.lower()]
        if not extraction_files:
            click.echo(f"No files found matching template filter: {template_filter}", err=True)
            raise click.Abort()
    
    # Set default output file
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = 'json' if output_format == 'json' else 'txt'
        output = Path(f"domain_grounding_{timestamp}.{suffix}")
    
    click.echo("🔬 Domain-Specific Grounding Analysis")
    click.echo("=" * 50)
    click.echo(f"Processing {len(extraction_files)} file(s)")
    
    # Initialize assessment data
    assessment_data = {
        'timestamp': datetime.now().isoformat(),
        'extraction_files': [str(f) for f in extraction_files],
        'template_assessments': [],
        'summary': {}
    }
    
    # Process each template
    all_domain_stats = defaultdict(lambda: defaultdict(int))
    
    for extraction_file in sorted(extraction_files):
        template_name = detect_template_from_filename(extraction_file.name)
        
        if verbose:
            click.echo(f"\\n📄 Processing: {extraction_file.name} ({template_name})")
        
        extractions = parse_extraction_file(extraction_file)
        domain_stats = analyze_domain_grounding(extractions, template_name)
        domain_metrics = calculate_domain_metrics(domain_stats)
        
        template_assessment = {
            'template_name': template_name,
            'file_name': extraction_file.name,
            'extraction_count': len(extractions),
            'domain_metrics': domain_metrics
        }
        
        assessment_data['template_assessments'].append(template_assessment)
        
        # Aggregate for summary
        for domain, metrics in domain_metrics.items():
            all_domain_stats[domain]['total'] += metrics['total_entities']
            all_domain_stats[domain]['correct'] += metrics['total_entities'] * metrics['correct_grounding_rate'] / 100
        
        if verbose:
            click.echo(f"  Domains found: {list(domain_metrics.keys())}")
            for domain, metrics in domain_metrics.items():
                if metrics['total_entities'] > 0:
                    click.echo(f"    {domain}: {metrics['correct_grounding_rate']:.1f}% correct ({metrics['total_entities']} entities)")
    
    # Calculate summary metrics
    summary_metrics = {}
    for domain, stats in all_domain_stats.items():
        if stats['total'] > 0:
            summary_metrics[domain] = {
                'total_entities': stats['total'],
                'overall_correct_rate': (stats['correct'] / stats['total']) * 100
            }
    
    assessment_data['summary'] = summary_metrics
    
    # Display summary
    click.echo(f"\\n📊 DOMAIN SUMMARY")
    for domain, metrics in sorted(summary_metrics.items(), key=lambda x: x[1]['total_entities'], reverse=True):
        click.echo(f"  {domain}: {metrics['overall_correct_rate']:.1f}% correct ({metrics['total_entities']} entities)")
    
    # Save output
    try:
        with open(output, 'w') as f:
            if output_format == 'json':
                json.dump(assessment_data, f, indent=2, default=str)
            else:
                # Text format output
                f.write(f"Domain-Specific Grounding Analysis - {assessment_data['timestamp']}\\n")
                f.write("=" * 60 + "\\n\\n")
                
                f.write("SUMMARY BY DOMAIN:\\n")
                for domain, metrics in sorted(summary_metrics.items(), key=lambda x: x[1]['total_entities'], reverse=True):
                    f.write(f"  {domain}: {metrics['overall_correct_rate']:.1f}% correct ({metrics['total_entities']} entities)\\n")
                
                f.write("\\nTEMPLATE BREAKDOWN:\\n")
                for template_assessment in assessment_data['template_assessments']:
                    f.write(f"\\n{template_assessment['template_name']} ({template_assessment['file_name']}):\\n")
                    for domain, metrics in template_assessment['domain_metrics'].items():
                        f.write(f"  {domain}: {metrics['correct_grounding_rate']:.1f}% correct, {metrics['auto_rate']:.1f}% AUTO\\n")
                        if metrics['problematic_ontologies']:
                            f.write(f"    Problematic: {', '.join(metrics['problematic_ontologies'])}\\n")
        
        click.echo(f"\\n💾 Domain grounding analysis saved to: {output}")
        
    except Exception as e:
        click.echo(f"❌ Error saving output to {output}: {e}", err=True)
        raise click.Abort()

if __name__ == "__main__":
    main()