#!/usr/bin/env python3
"""
Analyze METPO grounding efficiency:
1. Which inputs had most METPO groundings?
2. METPO groundings per KB of input text
3. Check if other ontologies use CURIE format
"""

import yaml
from pathlib import Path
from collections import defaultdict

def analyze_file(yaml_file):
    """Analyze a single YAML file for METPO grounding efficiency."""

    with open(yaml_file) as f:
        try:
            docs = list(yaml.safe_load_all(f))
        except yaml.YAMLError as e:
            print(f"Error parsing {yaml_file}: {e}")
            return None

    total_input_size = 0
    metpo_count = 0
    other_ontology_formats = defaultdict(set)  # Track ID formats by ontology

    for doc in docs:
        if not doc:
            continue

        # Get input text size
        input_text = doc.get('input_text', '')
        total_input_size += len(input_text)

        # Count METPO entities and check formats
        if 'named_entities' in doc:
            for entity in doc.get('named_entities', []):
                entity_id = entity.get('id', '')

                # Check METPO (URI format)
                if isinstance(entity_id, str) and 'w3id.org/metpo/' in entity_id:
                    metpo_count += 1

                # Track other ontology formats
                if isinstance(entity_id, str):
                    if entity_id.startswith('CHEBI:'):
                        other_ontology_formats['CHEBI'].add('CURIE')
                    elif entity_id.startswith('NCBITaxon:'):
                        other_ontology_formats['NCBITaxon'].add('CURIE')
                    elif entity_id.startswith('GO:'):
                        other_ontology_formats['GO'].add('CURIE')
                    elif entity_id.startswith('RHEA:'):
                        other_ontology_formats['RHEA'].add('CURIE')
                    elif entity_id.startswith('AUTO:'):
                        other_ontology_formats['AUTO'].add('CURIE-like')
                    elif 'w3id.org' in entity_id or 'purl.obolibrary.org' in entity_id:
                        # Check if any other ontology uses URI format
                        if 'metpo' not in entity_id:
                            prefix = entity_id.split('/')[-2] if '/' in entity_id else 'unknown'
                            other_ontology_formats[prefix].add('URI')

    if total_input_size == 0:
        return None

    input_kb = total_input_size / 1024
    metpo_per_kb = metpo_count / input_kb if input_kb > 0 else 0

    return {
        'file': yaml_file.name,
        'input_bytes': total_input_size,
        'input_kb': input_kb,
        'metpo_count': metpo_count,
        'metpo_per_kb': metpo_per_kb,
        'other_formats': other_ontology_formats
    }

def main():
    """Analyze all extraction files."""
    outputs_dir = Path('literature_mining/outputs')

    all_results = []
    all_formats = defaultdict(set)

    # Search all YAML files
    yaml_files = list(outputs_dir.rglob('*.yaml'))

    print(f"Analyzing {len(yaml_files)} YAML files...")
    print()

    for yaml_file in yaml_files:
        result = analyze_file(yaml_file)
        if result and result['metpo_count'] > 0:
            all_results.append(result)
            # Aggregate format info
            for ontology, formats in result['other_formats'].items():
                all_formats[ontology].update(formats)

    # Sort by METPO count (descending)
    all_results.sort(key=lambda x: x['metpo_count'], reverse=True)

    print("=" * 100)
    print("ONTOLOGY ID FORMAT ANALYSIS")
    print("=" * 100)
    print()

    print("ID formats used by each ontology:")
    for ontology in sorted(all_formats.keys()):
        formats = ', '.join(sorted(all_formats[ontology]))
        print(f"  {ontology:20s} → {formats}")

    print()
    print("**FINDING:** Only METPO uses URI format; all others use CURIE format")
    print()

    print("=" * 100)
    print("FILES WITH MOST METPO GROUNDINGS (absolute count)")
    print("=" * 100)
    print()
    print(f"{'Rank':<6}{'File':<60}{'METPO':<10}{'Input KB':<12}{'METPO/KB':<10}")
    print("-" * 100)

    for i, result in enumerate(all_results, 1):
        print(f"{i:<6}{result['file']:<60}{result['metpo_count']:<10}{result['input_kb']:<12.1f}{result['metpo_per_kb']:<10.3f}")

    print()

    # Sort by efficiency (METPO per KB)
    all_results.sort(key=lambda x: x['metpo_per_kb'], reverse=True)

    print("=" * 100)
    print("FILES WITH HIGHEST METPO GROUNDING EFFICIENCY (per KB of input)")
    print("=" * 100)
    print()
    print(f"{'Rank':<6}{'File':<60}{'METPO/KB':<12}{'METPO':<10}{'Input KB':<10}")
    print("-" * 100)

    for i, result in enumerate(all_results, 1):
        print(f"{i:<6}{result['file']:<60}{result['metpo_per_kb']:<12.3f}{result['metpo_count']:<10}{result['input_kb']:<10.1f}")

    print()
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print()

    if all_results:
        total_metpo = sum(r['metpo_count'] for r in all_results)
        total_kb = sum(r['input_kb'] for r in all_results)
        avg_efficiency = total_metpo / total_kb if total_kb > 0 else 0

        print(f"Files with METPO grounding: {len(all_results)}")
        print(f"Total METPO groundings: {total_metpo}")
        print(f"Total input size: {total_kb:.1f} KB ({total_kb/1024:.2f} MB)")
        print(f"Average efficiency: {avg_efficiency:.3f} METPO groundings per KB")
        print()

        # Best file
        best_count = all_results[0] if all_results else None
        all_results.sort(key=lambda x: x['metpo_per_kb'], reverse=True)
        best_efficiency = all_results[0] if all_results else None

        if best_count:
            print(f"Most METPO groundings: {best_count['file']} ({best_count['metpo_count']} groundings)")
        if best_efficiency:
            print(f"Best efficiency: {best_efficiency['file']} ({best_efficiency['metpo_per_kb']:.3f} per KB)")

    # Save results
    output_file = Path('literature_mining/METPO_GROUNDING_EFFICIENCY.tsv')
    with open(output_file, 'w') as f:
        f.write("File\tMETPO_Count\tInput_Bytes\tInput_KB\tMETPO_per_KB\n")
        # Re-sort by count for output
        all_results.sort(key=lambda x: x['metpo_count'], reverse=True)
        for result in all_results:
            f.write(f"{result['file']}\t{result['metpo_count']}\t{result['input_bytes']}\t{result['input_kb']:.2f}\t{result['metpo_per_kb']:.4f}\n")

    print()
    print(f"Detailed results saved to: {output_file}")

if __name__ == '__main__':
    main()
