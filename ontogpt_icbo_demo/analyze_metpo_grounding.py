#!/usr/bin/env python3
"""Analyze METPO grounding in OntoGPT extraction outputs."""

import yaml
from pathlib import Path
from collections import defaultdict

def count_metpo_classes(yaml_file):
    """Count METPO URI groundings for classes (phenotypes)."""
    with open(yaml_file) as f:
        data = yaml.safe_load(f)
    
    metpo_count = 0
    auto_count = 0
    
    for entity in data.get('named_entities', []):
        entity_id = entity.get('id', '')
        if 'w3id.org/metpo' in str(entity_id):
            metpo_count += 1
        elif str(entity_id).startswith('AUTO:'):
            auto_count += 1
    
    return metpo_count, auto_count

def count_metpo_predicates(yaml_file):
    """Count METPO predicate usage in chemical utilizations."""
    with open(yaml_file) as f:
        data = yaml.safe_load(f)
    
    predicate_counts = defaultdict(int)
    
    extracted = data.get('extracted_object', {})
    utilizations = extracted.get('chemical_utilizations', [])
    
    if isinstance(utilizations, list):
        for util in utilizations:
            if isinstance(util, dict):
                pred = util.get('predicate', '')
                if pred:
                    predicate_counts[pred] += 1
    
    return dict(predicate_counts), len(utilizations)

def main():
    outputs_dir = Path('outputs')
    
    print("=== METPO Grounding Analysis ===\n")
    
    print("Phenotype Extractions (METPO class groundings):")
    for yaml_file in sorted(outputs_dir.glob('*-phenotype.yaml')):
        metpo, auto = count_metpo_classes(yaml_file)
        total = metpo + auto
        percent = (metpo / total * 100) if total > 0 else 0
        print(f"  {yaml_file.name}:")
        print(f"    METPO URIs: {metpo:3d} / {total:3d} ({percent:5.1f}%)")
        print(f"    AUTO terms: {auto:3d}")
    
    print("\nChemical Utilization Extractions (METPO predicate usage):")
    for yaml_file in sorted(outputs_dir.glob('*-chemical.yaml')):
        predicates, total_utils = count_metpo_predicates(yaml_file)
        print(f"  {yaml_file.name}:")
        print(f"    Total utilizations: {total_utils}")
        print(f"    METPO predicates used: {len(predicates)}")
        if predicates:
            print(f"    Top predicates:")
            for pred, count in sorted(predicates.items(), key=lambda x: -x[1])[:5]:
                print(f"      - {pred}: {count}")

if __name__ == '__main__':
    main()
