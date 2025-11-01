#!/usr/bin/env python3
"""Analyze OntoGPT extraction results to compare template performance."""

import yaml
import sys
from pathlib import Path
from collections import defaultdict

def count_entities_and_grounding(yaml_file):
    """Count entities and grounding quality in a YAML extraction file."""
    with open(yaml_file) as f:
        data = yaml.safe_load_all(f)

        stats = {
            'total_extractions': 0,
            'total_entities': 0,
            'grounded_entities': 0,
            'auto_entities': 0,
            'none_entities': 0,
            'total_relations': 0,
            'namespace_counts': defaultdict(int)
        }

        for doc in data:
            if not doc or 'extracted_object' not in doc:
                continue

            stats['total_extractions'] += 1
            extracted = doc['extracted_object']

            # Count named entities
            if 'named_entities' in doc:
                for entity in doc['named_entities']:
                    if not entity or 'id' not in entity:
                        continue

                    entity_id = entity['id']

                    # Skip "none" entities
                    if 'none' in str(entity_id).lower():
                        stats['none_entities'] += 1
                        continue

                    stats['total_entities'] += 1

                    # Check namespace
                    if ':' in str(entity_id):
                        namespace = entity_id.split(':')[0]
                        stats['namespace_counts'][namespace] += 1

                        if namespace != 'AUTO':
                            stats['grounded_entities'] += 1
                        else:
                            stats['auto_entities'] += 1

            # Count relationships/triples
            for key, value in extracted.items():
                if 'relationship' in key.lower() and isinstance(value, list):
                    for rel in value:
                        if isinstance(rel, dict) and 'subject' in rel:
                            # Skip "none" relationships
                            subject = str(rel.get('subject', ''))
                            if 'none' not in subject.lower():
                                stats['total_relations'] += 1

        return stats

def main():
    outputs_dir = Path('/Users/MAM/Documents/gitrepos/metpo/literature_mining/outputs')

    print("=" * 80)
    print("CMM Abstract Extraction Analysis")
    print("=" * 80)
    print()

    results = {}

    for yaml_file in sorted(outputs_dir.glob('*.yaml')):
        template_name = yaml_file.stem.rsplit('_', 2)[0]  # Remove timestamp
        stats = count_entities_and_grounding(yaml_file)
        results[template_name] = stats

        print(f"Template: {template_name}")
        print(f"  File: {yaml_file.name}")
        print(f"  Extractions: {stats['total_extractions']}")
        print(f"  Total entities (non-'none'): {stats['total_entities']}")
        print(f"  Grounded entities (non-AUTO): {stats['grounded_entities']}")
        print(f"  AUTO entities: {stats['auto_entities']}")
        print(f"  'none' entities: {stats['none_entities']}")
        print(f"  Total relations: {stats['total_relations']}")
        print(f"  Avg entities per abstract: {stats['total_entities']/max(stats['total_extractions'], 1):.1f}")
        print(f"  Avg relations per abstract: {stats['total_relations']/max(stats['total_extractions'], 1):.1f}")
        print(f"  Grounding rate: {100*stats['grounded_entities']/max(stats['total_entities'], 1):.1f}%")
        print(f"  Namespaces used: {dict(stats['namespace_counts'])}")
        print()

    print("=" * 80)
    print("SUMMARY - Ranked by Total Entities + Relations")
    print("=" * 80)
    print()

    ranked = sorted(results.items(),
                   key=lambda x: x[1]['total_entities'] + x[1]['total_relations'],
                   reverse=True)

    for template_name, stats in ranked:
        total_extracted = stats['total_entities'] + stats['total_relations']
        print(f"{template_name:30} | Entities: {stats['total_entities']:4} | Relations: {stats['total_relations']:4} | Total: {total_extracted:4} | Grounded: {stats['grounded_entities']:4} ({100*stats['grounded_entities']/max(stats['total_entities'], 1):5.1f}%)")

if __name__ == '__main__':
    main()
