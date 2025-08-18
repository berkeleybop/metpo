#!/usr/bin/env python3
"""
METPO Literature Mining Assessor

Two-phase assessment tool with clear CLI entrypoints:
1. Template analysis (design quality in isolation)
2. Extraction analysis (real-world performance)

Integrates with:
- semsql ontology registry for annotator validation
- OntoGPT extraction data model understanding
- Template pattern detection and cross-template optimization
"""

import yaml
import json
import requests
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple, Optional
import click
from collections import defaultdict, Counter
from datetime import datetime
import re

class MetpoAssessor:
    def __init__(self):
        self.semsql_registry = self._load_semsql_registry()
        self.universal_entities = {'pmid', 'source_text'}
        
    def _load_semsql_registry(self) -> Dict[str, Any]:
        """Load semsql ontology registry for annotator validation."""
        url = "https://raw.githubusercontent.com/INCATools/semantic-sql/refs/heads/main/src/semsql/builder/registry/ontologies.yaml"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return yaml.safe_load(response.text)
        except Exception as e:
            click.echo(f"Warning: Could not load semsql registry: {e}", err=True)
            return {}
    
    def _get_available_annotators(self) -> Set[str]:
        """Extract available annotator prefixes from semsql registry."""
        annotators = set()
        if 'ontologies' in self.semsql_registry:
            for ont_info in self.semsql_registry['ontologies']:
                if isinstance(ont_info, dict) and 'id' in ont_info:
                    annotators.add(f"sqlite:obo:{ont_info['id']}")
        return annotators

    # ===== PHASE 1: TEMPLATE ANALYSIS =====
    
    def analyze_template(self, template_path: Path) -> Dict[str, Any]:
        """Analyze template design quality in isolation."""
        with open(template_path, 'r') as f:
            template = yaml.safe_load(f)
        
        result = {
            'template_path': str(template_path),
            'template_name': template_path.stem,
            'analysis_timestamp': datetime.now().isoformat(),
            'compliance': {},
            'quality_metrics': {},
            'issues': [],
            'recommendations': [],
            'patterns': {}
        }
        
        classes = template.get('classes', {})
        
        # Core compliance checks
        result['compliance'] = {
            'tree_root_found': self._check_tree_root(classes),
            'compound_expressions': self._analyze_compound_expressions(classes),
            'semicolon_requests': self._check_semicolon_requests(classes),
            'multivalued_fields': self._check_multivalued_fields(classes),
            'annotator_quality': self._check_annotators(classes)
        }
        
        # Quality pattern detection
        result['patterns'] = self._detect_template_patterns(classes)
        
        # Generate issues and recommendations
        self._generate_template_recommendations(result)
        
        return result
    
    def _check_tree_root(self, classes: Dict) -> Dict[str, Any]:
        """Check tree root class structure."""
        tree_root = None
        for class_name, class_def in classes.items():
            if class_def.get('tree_root'):
                tree_root = class_def
                break
        
        if not tree_root:
            return {'found': False}
        
        attributes = tree_root.get('attributes', {})
        return {
            'found': True,
            'attribute_count': len(attributes),
            'attributes': list(attributes.keys())
        }
    
    def _analyze_compound_expressions(self, classes: Dict) -> Dict[str, Any]:
        """Analyze CompoundExpression classes for compliance."""
        compound_expressions = {}
        for class_name, class_def in classes.items():
            if class_def.get('is_a') == 'CompoundExpression':
                compound_expressions[class_name] = class_def
        
        compliant_count = 0
        issues = []
        
        for ce_name, ce_def in compound_expressions.items():
            attrs = set(ce_def.get('attributes', {}).keys())
            expected = {'subject', 'predicate', 'object'}
            
            if attrs == expected:
                compliant_count += 1
            else:
                issues.append(f"{ce_name}: {attrs} != {expected}")
        
        return {
            'total_count': len(compound_expressions),
            'compliant_count': compliant_count,
            'compliance_rate': (compliant_count / max(len(compound_expressions), 1)) * 100,
            'issues': issues[:3]  # Limit output
        }
    
    def _check_semicolon_requests(self, classes: Dict) -> Dict[str, Any]:
        """Check if fields properly request semicolon-separated lists."""
        tree_root = self._find_tree_root(classes)
        if not tree_root:
            return {'total_fields': 0, 'semicolon_fields': 0, 'rate': 0}
        
        total_fields = 0
        semicolon_fields = 0
        
        for attr_name, attr_def in tree_root.get('attributes', {}).items():
            if attr_name in self.universal_entities:
                continue
            
            total_fields += 1
            description = attr_def.get('description', '').lower()
            
            if 'semicolon' in description:
                semicolon_fields += 1
        
        return {
            'total_fields': total_fields,
            'semicolon_fields': semicolon_fields,
            'rate': (semicolon_fields / max(total_fields, 1)) * 100
        }
    
    def _check_multivalued_fields(self, classes: Dict) -> Dict[str, Any]:
        """Check multivalued field usage."""
        tree_root = self._find_tree_root(classes)
        if not tree_root:
            return {'total_fields': 0, 'multivalued_fields': 0, 'rate': 0}
        
        total_fields = 0
        multivalued_fields = 0
        
        for attr_name, attr_def in tree_root.get('attributes', {}).items():
            if attr_name in self.universal_entities:
                continue
            
            total_fields += 1
            if attr_def.get('multivalued'):
                multivalued_fields += 1
        
        return {
            'total_fields': total_fields,
            'multivalued_fields': multivalued_fields,
            'rate': (multivalued_fields / max(total_fields, 1)) * 100
        }
    
    def _check_annotators(self, classes: Dict) -> Dict[str, Any]:
        """Check NamedEntity annotator specifications."""
        available_annotators = self._get_available_annotators()
        
        named_entities = {}
        for class_name, class_def in classes.items():
            if class_def.get('is_a') == 'NamedEntity':
                named_entities[class_name] = class_def
        
        total_entities = len(named_entities)
        well_annotated = 0
        annotator_issues = []
        
        for entity_name, entity_def in named_entities.items():
            annotators_str = entity_def.get('annotations', {}).get('annotators', '')
            
            if not annotators_str:
                annotator_issues.append(f"{entity_name}: No annotators")
                continue
            
            annotators = [a.strip() for a in annotators_str.split(',')]
            valid_annotators = []
            
            for annotator in annotators:
                if annotator.startswith('sqlite:obo:'):
                    if annotator in available_annotators:
                        valid_annotators.append(annotator)
                elif annotator in ['metpo.db']:  # Special cases
                    valid_annotators.append(annotator)
            
            if len(valid_annotators) >= 2:
                well_annotated += 1
            elif len(valid_annotators) == 1:
                annotator_issues.append(f"{entity_name}: Only 1 annotator")
            else:
                annotator_issues.append(f"{entity_name}: No valid annotators")
        
        return {
            'total_entities': total_entities,
            'well_annotated': well_annotated,
            'rate': (well_annotated / max(total_entities, 1)) * 100,
            'issues': annotator_issues[:3]
        }
    
    def _detect_template_patterns(self, classes: Dict) -> Dict[str, Any]:
        """Detect good/bad patterns in template design."""
        patterns = {
            'good_practices': [],
            'anti_patterns': [],
            'entity_types': [],
            'predicate_types': []
        }
        
        # Detect entity types and annotation patterns
        for class_name, class_def in classes.items():
            if class_def.get('is_a') == 'NamedEntity':
                annotators = class_def.get('annotations', {}).get('annotators', '')
                patterns['entity_types'].append({
                    'name': class_name,
                    'annotators': annotators,
                    'description': class_def.get('description', '')[:100]
                })
        
        # Detect predicate enumeration patterns
        enums = classes.get('enums', {})
        for enum_name, enum_def in enums.items():
            if 'Type' in enum_name or 'Enum' in enum_name:
                values = enum_def.get('permissible_values', {})
                patterns['predicate_types'].append({
                    'name': enum_name,
                    'value_count': len(values),
                    'sample_values': list(values.keys())[:5]
                })
        
        return patterns
    
    def _generate_template_recommendations(self, result: Dict):
        """Generate actionable recommendations for template improvement."""
        compliance = result['compliance']
        
        # CompoundExpression compliance
        ce_rate = compliance['compound_expressions']['compliance_rate']
        if ce_rate < 100:
            result['issues'].append(f"CompoundExpression compliance: {ce_rate:.1f}%")
            result['recommendations'].append("Fix CompoundExpression structure to use exactly subject/predicate/object")
        
        # Semicolon request compliance
        semi_rate = compliance['semicolon_requests']['rate']
        if semi_rate < 80:
            result['issues'].append(f"Semicolon requests: {semi_rate:.1f}%")
            result['recommendations'].append("Add 'semicolon-separated list' to field descriptions")
        
        # Multivalued field compliance
        mv_rate = compliance['multivalued_fields']['rate']
        if mv_rate < 70:
            result['issues'].append(f"Multivalued fields: {mv_rate:.1f}%")
            result['recommendations'].append("Mark most fields as multivalued: true")
        
        # Annotator compliance
        ann_rate = compliance['annotator_quality']['rate']
        if ann_rate < 80:
            result['issues'].append(f"Well-annotated entities: {ann_rate:.1f}%")
            result['recommendations'].append("Add multiple comma-separated annotators to NamedEntity classes")

    # ===== PHASE 2: EXTRACTION ANALYSIS =====
    
    def analyze_extraction(self, extraction_path: Path) -> Dict[str, Any]:
        """Analyze extraction output performance."""
        with open(extraction_path, 'r') as f:
            docs = list(yaml.safe_load_all(f))
            
            if not docs:
                return self._empty_extraction_result(extraction_path)
            
            # Find ALL documents with extracted_object
            extractions = []
            for doc in docs:
                if isinstance(doc, dict) and 'extracted_object' in doc:
                    extractions.append(doc)
            
            if not extractions:
                return self._empty_extraction_result(extraction_path)
        
        result = {
            'extraction_path': str(extraction_path),
            'template_name': self._extract_template_name(extraction_path),
            'analysis_timestamp': datetime.now().isoformat(),
            'abstracts_processed': len(extractions),
            'success_metrics': {},
            'performance': {},
            'issues': [],
            'strengths': []
        }
        
        # Aggregate metrics across all extractions
        total_ce_count = 0
        successful_extractions = 0
        all_entities = []
        all_extracted_objects = []
        
        for extraction in extractions:
            extracted_obj = extraction.get('extracted_object', {})
            ce_count = self._count_compound_expressions(extracted_obj)
            total_ce_count += ce_count
            if ce_count > 0:
                successful_extractions += 1
            
            # Collect all named entities for grounding analysis
            named_entities = extraction.get('named_entities', [])
            all_entities.extend(named_entities)
            
            # Collect extracted objects for CompoundExpression analysis
            all_extracted_objects.append(extracted_obj)
        
        # Core success metrics
        result['success_metrics']['compound_expressions'] = total_ce_count
        result['success_metrics']['successful_extractions'] = successful_extractions
        result['success_metrics']['primary_success'] = successful_extractions > 0
        
        # Aggregate CompoundExpression analysis across all extractions
        ce_analysis = {'total_compound_expressions': 0, 'grounded_subjects': 0, 'grounded_predicates': 0, 'metpo_predicates': 0}
        for extracted_obj in all_extracted_objects:
            obj_analysis = self._analyze_compound_expression_grounding(extracted_obj)
            ce_analysis['total_compound_expressions'] += obj_analysis['total_compound_expressions']
            ce_analysis['grounded_subjects'] += obj_analysis['grounded_subjects']
            ce_analysis['grounded_predicates'] += obj_analysis['grounded_predicates']
            ce_analysis['metpo_predicates'] += obj_analysis['metpo_predicates']
        
        # Calculate final rates
        total_ces = ce_analysis['total_compound_expressions']
        ce_analysis['subject_grounding_rate'] = round((ce_analysis['grounded_subjects'] / max(total_ces, 1)) * 100, 1)
        ce_analysis['predicate_grounding_rate'] = round((ce_analysis['grounded_predicates'] / max(total_ces, 1)) * 100, 1)
        ce_analysis['metpo_predicate_usage'] = round((ce_analysis['metpo_predicates'] / max(total_ces, 1)) * 100, 1)

        # Performance analysis using aggregated data
        result['performance'] = {
            'raw_output': self._analyze_raw_output(extractions[0].get('raw_completion_output', '') if extractions else ''),
            'grounding': self._analyze_grounding(all_entities),
            'compound_expression_grounding': ce_analysis,
            'coverage': self._analyze_coverage(extractions[0] if extractions else {})
        }
        
        # Generate insights
        self._generate_extraction_insights(result)
        
        return result
    
    def _empty_extraction_result(self, extraction_path: Path) -> Dict[str, Any]:
        """Return empty result for failed extractions."""
        return {
            'extraction_path': str(extraction_path),
            'template_name': self._extract_template_name(extraction_path),
            'analysis_timestamp': datetime.now().isoformat(),
            'success_metrics': {'compound_expressions': 0, 'primary_success': False},
            'performance': {
                'raw_output': {'populated_fields': 0, 'total_entities': 0},
                'grounding': {'total': 0, 'grounded': 0, 'rate': 0},
                'coverage': {'span_rate': 0}
            },
            'issues': ['Failed to parse extraction file'],
            'strengths': []
        }
    
    def _extract_template_name(self, extraction_path: Path) -> str:
        """Extract template name from extraction filename."""
        stem = extraction_path.stem
        parts = stem.split('_')
        if len(parts) >= 3:
            return '_'.join(parts[:-2])  # Remove timestamp
        return parts[0]
    
    def _count_compound_expressions(self, extracted_object: Dict) -> int:
        """Count valid CompoundExpressions."""
        count = 0
        for key, value in extracted_object.items():
            if key in self.universal_entities:
                continue
            
            if isinstance(value, list):
                for item in value:
                    if self._is_compound_expression(item):
                        count += 1
            elif self._is_compound_expression(value):
                count += 1
        
        return count
    
    def _is_compound_expression(self, item: Any) -> bool:
        """Check if item is valid CompoundExpression."""
        if not isinstance(item, dict):
            return False
        required = {'subject', 'predicate', 'object'}
        return all(key in item and item[key] for key in required)
    
    def _analyze_raw_output(self, raw_output: str) -> Dict[str, Any]:
        """Analyze raw LLM completion quality."""
        if not raw_output:
            return {'populated_fields': 0, 'total_entities': 0, 'quality': 'empty'}
        
        lines = raw_output.strip().split('\\n')
        populated_fields = 0
        total_entities = 0
        
        for line in lines:
            if ':' in line and not line.startswith(' '):
                field_value = ':'.join(line.split(':')[1:]).strip()
                if field_value:
                    populated_fields += 1
                    entities = [e.strip() for e in field_value.split(';') if e.strip()]
                    total_entities += len(entities)
        
        quality = 'excellent' if total_entities > 20 else 'good' if total_entities > 10 else 'poor'
        
        return {
            'populated_fields': populated_fields,
            'total_entities': total_entities,
            'avg_entities_per_field': total_entities / max(populated_fields, 1),
            'quality': quality
        }
    
    def _analyze_grounding(self, named_entities: List[Dict]) -> Dict[str, Any]:
        """Analyze entity grounding quality with enhanced metrics."""
        total = len(named_entities)
        auto = sum(1 for e in named_entities if e.get('id', '').startswith('AUTO:'))
        grounded = total - auto
        
        # Ontology usage analysis
        ontologies = {}
        entity_duplicates = {}
        
        for entity in named_entities:
            entity_id = entity.get('id', '')
            entity_label = entity.get('label', '')
            
            # Track ontology usage
            if ':' in entity_id and not entity_id.startswith('AUTO:'):
                ontology = entity_id.split(':')[0]
                ontologies[ontology] = ontologies.get(ontology, 0) + 1
            
            # Track entity duplication
            if entity_id:
                entity_duplicates[entity_id] = entity_duplicates.get(entity_id, 0) + 1
        
        # Find most duplicated entities (excluding expected NCBI taxonomy)
        duplicated_entities = {k: v for k, v in entity_duplicates.items() 
                             if v > 1 and not k.startswith('NCBITaxon:')}
        
        # Calculate auto vs grounded ratio
        auto_vs_grounded_ratio = auto / max(grounded, 1) if grounded > 0 else float('inf')
        
        return {
            'total': total,
            'grounded': grounded,
            'auto': auto,
            'rate': (grounded / max(total, 1)) * 100,
            'auto_vs_grounded_ratio': round(auto_vs_grounded_ratio, 2),
            'ontologies_used': ontologies,
            'ontology_diversity': len(ontologies),
            'duplicated_entities': duplicated_entities,
            'excessive_duplication': len(duplicated_entities) > 5
        }
    
    def _analyze_compound_expression_grounding(self, extracted_obj: Dict) -> Dict[str, Any]:
        """Analyze grounding quality specifically for CompoundExpression objects."""
        total_ces = 0
        grounded_subjects = 0
        grounded_predicates = 0
        metpo_predicates = 0
        
        # Check all fields that might contain CompoundExpressions
        for field_name, field_value in extracted_obj.items():
            if isinstance(field_value, list):
                for item in field_value:
                    if isinstance(item, dict) and all(k in item for k in ['subject', 'predicate', 'object']):
                        total_ces += 1
                        
                        # Check subject grounding
                        subject = item.get('subject', '')
                        if isinstance(subject, str) and ':' in subject and not subject.startswith('AUTO:'):
                            grounded_subjects += 1
                        
                        # Check predicate grounding
                        predicate = item.get('predicate', '')
                        if isinstance(predicate, str):
                            if ':' in predicate and not predicate.startswith('AUTO:'):
                                grounded_predicates += 1
                            if 'METPO:' in str(predicate) or predicate in ['uses_as_carbon_source', 'degrades', 'ferments']:
                                metpo_predicates += 1
        
        return {
            'total_compound_expressions': total_ces,
            'grounded_subjects': grounded_subjects,
            'grounded_predicates': grounded_predicates,
            'metpo_predicates': metpo_predicates,
            'subject_grounding_rate': round((grounded_subjects / max(total_ces, 1)) * 100, 1),
            'predicate_grounding_rate': round((grounded_predicates / max(total_ces, 1)) * 100, 1),
            'metpo_predicate_usage': round((metpo_predicates / max(total_ces, 1)) * 100, 1)
        }
    
    def _analyze_coverage(self, extraction: Dict) -> Dict[str, Any]:
        """Analyze text coverage."""
        named_entities = extraction.get('named_entities', [])
        entities_with_spans = sum(1 for e in named_entities if e.get('original_spans'))
        
        return {
            'entities_with_spans': entities_with_spans,
            'total_entities': len(named_entities),
            'span_rate': (entities_with_spans / max(len(named_entities), 1)) * 100
        }
    
    def _generate_extraction_insights(self, result: Dict):
        """Generate insights for extraction performance."""
        performance = result['performance']
        success = result['success_metrics']
        
        # Primary success assessment
        if success['compound_expressions'] == 0:
            result['issues'].append("CRITICAL: No CompoundExpressions extracted")
        elif success['compound_expressions'] > 10:
            result['strengths'].append(f"Excellent relationship extraction: {success['compound_expressions']} CEs")
        
        # Raw output quality
        raw_quality = performance['raw_output']['quality']
        if raw_quality == 'poor':
            result['issues'].append("Poor raw LLM output quality")
        elif raw_quality == 'excellent':
            result['strengths'].append("Excellent raw LLM output richness")
        
        # Grounding quality
        grounding_rate = performance['grounding']['rate']
        if grounding_rate < 60:
            result['issues'].append(f"Low grounding rate: {grounding_rate:.1f}%")
        elif grounding_rate > 80:
            result['strengths'].append(f"Excellent grounding rate: {grounding_rate:.1f}%")

    # ===== UTILITY METHODS =====
    
    def _find_tree_root(self, classes: Dict) -> Optional[Dict]:
        """Find tree root class."""
        for class_name, class_def in classes.items():
            if class_def.get('tree_root'):
                return class_def
        return None
    
    def cross_template_analysis(self, template_results: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns across multiple templates for optimization."""
        if len(template_results) < 2:
            return {'message': 'Need multiple templates for cross-analysis'}
        
        # Collect patterns
        all_patterns = defaultdict(list)
        for result in template_results:
            template_name = result['template_name']
            patterns = result.get('patterns', {})
            
            # Collect entity types and annotators
            for entity in patterns.get('entity_types', []):
                all_patterns['entities'].append({
                    'template': template_name,
                    'name': entity['name'],
                    'annotators': entity['annotators']
                })
        
        # Find best practices to propagate
        best_practices = []
        annotator_patterns = defaultdict(set)
        
        for entity_info in all_patterns['entities']:
            annotators = entity_info['annotators']
            if annotators and len(annotators.split(',')) >= 2:
                annotator_patterns[entity_info['name']].add(annotators)
        
        return {
            'cross_template_patterns': dict(all_patterns),
            'best_practices': best_practices,
            'recommendations': [
                "Standardize annotator patterns across similar entity types",
                "Propagate successful CompoundExpression patterns",
                "Harmonize field description patterns"
            ]
        }

# ===== CLI INTERFACE =====

@click.group()
def cli():
    """METPO Literature Mining Assessment Tool"""
    pass

@cli.command()
@click.argument('templates_dir', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Output file')
@click.option('--pattern', default='*_base.yaml', help='Template file pattern')
def analyze_templates(templates_dir, output, pattern):
    """Phase 1: Analyze template design quality in isolation."""
    assessor = MetpoAssessor()
    template_files = list(templates_dir.glob(pattern))
    
    if not template_files:
        click.echo(f"No templates found with pattern {pattern}")
        return
    
    click.echo(f"Analyzing {len(template_files)} templates...")
    
    results = []
    for template_file in template_files:
        click.echo(f"  {template_file.name}")
        result = assessor.analyze_template(template_file)
        results.append(result)
    
    # Cross-template analysis
    cross_analysis = assessor.cross_template_analysis(results)
    
    # Generate report
    report = generate_template_report(results, cross_analysis)
    
    if output:
        output.write_text(report)
        click.echo(f"Template analysis written to {output}")
    else:
        click.echo("\\n" + report)

@cli.command()
@click.argument('extractions_dir', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Output file')
@click.option('--pattern', default='*.yaml', help='Extraction file pattern')
def analyze_extractions(extractions_dir, output, pattern):
    """Phase 2: Analyze extraction output performance."""
    assessor = MetpoAssessor()
    extraction_files = list(extractions_dir.glob(pattern))
    
    if not extraction_files:
        click.echo(f"No extractions found with pattern {pattern}")
        return
    
    click.echo(f"Analyzing {len(extraction_files)} extractions...")
    
    results = []
    for extraction_file in extraction_files:
        click.echo(f"  {extraction_file.name}")
        result = assessor.analyze_extraction(extraction_file)
        results.append(result)
    
    # Generate report
    report = generate_extraction_report(results)
    
    if output:
        output.write_text(report)
        click.echo(f"Extraction analysis written to {output}")
    else:
        click.echo("\\n" + report)

def generate_template_report(results: List[Dict], cross_analysis: Dict) -> str:
    """Generate template analysis report in YAML format."""
    report = {
        'generated': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'summary': {
            'templates_analyzed': len(results)
        },
        'templates': {}
    }
    
    # Individual template results
    for result in results:
        name = result['template_name']
        compliance = result['compliance']
        
        report['templates'][name] = {
            'compliance_metrics': {
                'compound_expression_compliance': round(compliance['compound_expressions']['compliance_rate'], 1),
                'semicolon_requests': round(compliance['semicolon_requests']['rate'], 1),
                'multivalued_fields': round(compliance['multivalued_fields']['rate'], 1),
                'well_annotated_entities': round(compliance['annotator_quality']['rate'], 1)
            },
            'issues': result['issues'],
            'recommendations': result['recommendations']
        }
    
    return yaml.dump(report, default_flow_style=False, sort_keys=False)

def generate_extraction_report(results: List[Dict]) -> str:
    """Generate extraction performance report in YAML format."""
    total = len(results)
    successful = sum(1 for r in results if r['success_metrics']['primary_success'])
    total_ces = sum(r['success_metrics']['compound_expressions'] for r in results)
    
    report = {
        'generated': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'summary': {
            'extractions_analyzed': total,
            'successful_extractions': successful,
            'success_rate': round(successful/max(total,1)*100, 1),
            'total_compound_expressions': total_ces,
            'average_ces_per_extraction': round(total_ces/max(total,1), 1)
        },
        'templates': {}
    }
    
    # Group by template
    by_template = defaultdict(list)
    for result in results:
        template_name = result['template_name']
        by_template[template_name].append(result)
    
    for template_name, template_results in by_template.items():
        successful_count = sum(1 for r in template_results if r['success_metrics']['primary_success'])
        total_count = len(template_results)
        ces = sum(r['success_metrics']['compound_expressions'] for r in template_results)
        abstracts_processed = sum(r.get('abstracts_processed', 1) for r in template_results)
        
        # Aggregate grounding metrics
        avg_grounding = sum(r['performance']['grounding']['rate'] for r in template_results) / len(template_results)
        avg_auto_vs_grounded = sum(r['performance']['grounding']['auto_vs_grounded_ratio'] for r in template_results) / len(template_results)
        
        # Aggregate CompoundExpression metrics
        avg_subject_grounding = sum(r['performance']['compound_expression_grounding']['subject_grounding_rate'] for r in template_results) / len(template_results)
        avg_predicate_grounding = sum(r['performance']['compound_expression_grounding']['predicate_grounding_rate'] for r in template_results) / len(template_results)
        avg_metpo_usage = sum(r['performance']['compound_expression_grounding']['metpo_predicate_usage'] for r in template_results) / len(template_results)
        
        # Aggregate ontology usage
        all_ontologies = {}
        all_duplicates = {}
        for r in template_results:
            grounding = r['performance']['grounding']
            for ont, count in grounding.get('ontologies_used', {}).items():
                all_ontologies[ont] = all_ontologies.get(ont, 0) + count
            for ent, count in grounding.get('duplicated_entities', {}).items():
                all_duplicates[ent] = all_duplicates.get(ent, 0) + count
        
        report['templates'][template_name] = {
            'abstracts_processed': abstracts_processed,
            'success_rate': f"{successful_count}/{total_count}",
            'success_percentage': round(successful_count/total_count*100, 1),
            'compound_expressions': ces,
            'average_ces': round(ces/total_count, 1),
            'grounding_metrics': {
                'overall_grounding_rate': round(avg_grounding, 1),
                'auto_vs_grounded_ratio': round(avg_auto_vs_grounded, 2),
                'subject_grounding_rate': round(avg_subject_grounding, 1),
                'predicate_grounding_rate': round(avg_predicate_grounding, 1),
                'metpo_predicate_usage': round(avg_metpo_usage, 1)
            },
            'ontology_usage': all_ontologies,
            'problematic_duplicates': {k: v for k, v in all_duplicates.items() if v > 2}
        }
    
    return yaml.dump(report, default_flow_style=False, sort_keys=False)

if __name__ == '__main__':
    cli()