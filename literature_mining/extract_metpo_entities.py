#!/usr/bin/env python3
"""
Extract all METPO entities from OntoGPT extraction YAML files.
Shows which METPO classes were successfully grounded.
"""

import yaml
import re
from pathlib import Path
from collections import defaultdict

def extract_metpo_entities(yaml_file):
    """Extract METPO entities from a single YAML file."""
    metpo_entities = []

    with open(yaml_file) as f:
        try:
            docs = list(yaml.safe_load_all(f))
        except yaml.YAMLError as e:
            print(f"Error parsing {yaml_file}: {e}")
            return []

    for doc in docs:
        if not doc or 'named_entities' not in doc:
            continue

        for entity in doc.get('named_entities', []):
            entity_id = entity.get('id', '')
            if isinstance(entity_id, str) and 'w3id.org/metpo/' in entity_id:
                metpo_entities.append({
                    'id': entity_id,
                    'label': entity.get('label', 'NO LABEL'),
                    'file': yaml_file.name
                })

    return metpo_entities

def main():
    """Extract METPO entities from all extraction files."""
    outputs_dir = Path('literature_mining/outputs')

    all_metpo_entities = []
    files_with_metpo = []

    # Search all YAML files
    yaml_files = list(outputs_dir.rglob('*.yaml'))

    print(f"Searching {len(yaml_files)} YAML files for METPO entities...")
    print()

    for yaml_file in yaml_files:
        entities = extract_metpo_entities(yaml_file)
        if entities:
            all_metpo_entities.extend(entities)
            files_with_metpo.append((yaml_file, len(entities)))
            print(f"✓ {yaml_file.name}: {len(entities)} METPO entities")

    print()
    print(f"Total files with METPO: {len(files_with_metpo)}")
    print(f"Total METPO entities: {len(all_metpo_entities)}")
    print()

    # Get unique METPO classes
    unique_classes = {}
    for entity in all_metpo_entities:
        # Extract numeric ID
        match = re.search(r'metpo/(\d+)', entity['id'])
        if match:
            metpo_id = match.group(1)
            if metpo_id not in unique_classes:
                unique_classes[metpo_id] = {
                    'uri': entity['id'],
                    'labels': set(),
                    'count': 0
                }
            unique_classes[metpo_id]['labels'].add(entity['label'])
            unique_classes[metpo_id]['count'] += 1

    print(f"Unique METPO classes: {len(unique_classes)}")
    print()
    print("=" * 80)
    print("METPO CLASSES SUCCESSFULLY GROUNDED")
    print("=" * 80)
    print()

    for metpo_id in sorted(unique_classes.keys()):
        info = unique_classes[metpo_id]
        print(f"METPO:{metpo_id}")
        print(f"  URI: {info['uri']}")
        print(f"  Occurrences: {info['count']}")
        print(f"  Labels extracted:")
        for label in sorted(info['labels']):
            print(f"    - {label}")
        print()

    # Save results
    output_file = Path('literature_mining/METPO_GROUNDED_CLASSES.tsv')
    with open(output_file, 'w') as f:
        f.write("METPO_ID\tURI\tLabel\tOccurrences\tFiles\n")
        for metpo_id in sorted(unique_classes.keys()):
            info = unique_classes[metpo_id]
            files = set(e['file'] for e in all_metpo_entities
                       if re.search(f'metpo/{metpo_id}', e['id']))
            label_str = "; ".join(sorted(info['labels']))
            file_str = "; ".join(sorted(files))
            f.write(f"METPO:{metpo_id}\t{info['uri']}\t{label_str}\t{info['count']}\t{file_str}\n")

    print(f"Results saved to: {output_file}")

if __name__ == '__main__':
    main()
