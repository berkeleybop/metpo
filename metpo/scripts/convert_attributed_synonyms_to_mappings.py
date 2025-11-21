#!/usr/bin/env python3
"""
Convert attributed synonyms from METPO templates to mapping instances.

Reads metpo_sheet.tsv and metpo-properties.tsv and extracts attributed synonyms,
converting them to the new Mapping instance format.
"""
import click
import csv
import re
from pathlib import Path
from typing import List, Dict, Tuple


def parse_synonym_tuples(tuples_str: str) -> List[Tuple[str, str]]:
    """Parse synonym tuples like 'oboInOwl:hasRelatedSynonym \"value\"'."""
    if not tuples_str or tuples_str.strip() == "":
        return []

    # Pattern: property_name 'value' or property_name "value"
    pattern = r"(\w+:\w+)\s+['\"]([^'\"]+)['\"]"
    matches = re.findall(pattern, tuples_str)
    return [(prop, val) for prop, val in matches]


def extract_class_synonyms(template_path: Path) -> List[Dict]:
    """Extract attributed synonyms from metpo_sheet.tsv."""
    mappings = []
    mapping_id = 1

    with open(template_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            metpo_id = row.get('ID', '').strip()
            label = row.get('label', '').strip()

            # Skip header rows and empty IDs
            if not metpo_id or metpo_id == 'ID' or not metpo_id.startswith('METPO:'):
                continue

            # Convert METPO: to metpo: for ROBOT template compatibility
            metpo_id = metpo_id.replace('METPO:', 'metpo:')

            # BacDive synonyms
            bacdive_syn = row.get('bacdive keyword synonym', '').strip()
            bacdive_source = row.get('Bacdive synonym source', '').strip()
            if bacdive_syn and bacdive_source:
                # Extract field name from source URL or use generic
                path = extract_path_from_source(bacdive_source, 'bacdive')
                mappings.append({
                    'id': f'metpo-map:{mapping_id}',
                    'label': f'{bacdive_syn} (BacDive)',
                    'metpo_id': metpo_id,
                    'dataset': 'metpo:BacDiveDataset',
                    'path': path,
                    'value': bacdive_syn,
                    'note': ''
                })
                mapping_id += 1

            # BactoTraits synonyms
            bactotraits_syn = row.get('bactotraits related synonym', '').strip()
            bactotraits_source = row.get('Bactotraits synonym source', '').strip()
            if bactotraits_syn and bactotraits_source:
                path = extract_path_from_source(bactotraits_source, 'bactotraits')
                mappings.append({
                    'id': f'metpo-map:{mapping_id}',
                    'label': f'{bactotraits_syn} (BactoTraits)',
                    'metpo_id': metpo_id,
                    'dataset': 'metpo:BactoTraitsDataset',
                    'path': path,
                    'value': bactotraits_syn,
                    'note': ''
                })
                mapping_id += 1

            # Madin synonyms
            madin_syn = row.get('madin synonym or field', '').strip()
            madin_source = row.get('Madin synonym source', '').strip()
            if madin_syn and madin_source:
                path = extract_path_from_source(madin_source, 'madin')
                # Madin column might have multiple synonyms separated by |
                for syn in madin_syn.split('|'):
                    syn = syn.strip()
                    if syn:
                        mappings.append({
                            'id': f'metpo-map:{mapping_id}',
                            'label': f'{syn} (Madin)',
                            'metpo_id': metpo_id,
                            'dataset': 'metpo:MadinDataset',
                            'path': path,
                            'value': syn,
                            'note': ''
                        })
                        mapping_id += 1

    return mappings, mapping_id


def extract_property_synonyms(template_path: Path, start_id: int) -> List[Dict]:
    """Extract attributed synonyms from metpo-properties.tsv."""
    mappings = []
    mapping_id = start_id

    with open(template_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            metpo_id = row.get('ID', '').strip()
            label = row.get('label', '').strip()

            # Skip header rows and empty IDs
            if not metpo_id or metpo_id == 'ID' or not metpo_id.startswith('METPO:'):
                continue

            # Convert METPO: to metpo: for ROBOT template compatibility
            metpo_id = metpo_id.replace('METPO:', 'metpo:')

            # Parse synonym tuples
            tuples_str = row.get('synonym property and value TUPLES', '').strip()
            source = row.get('synonym source', '').strip()

            if tuples_str and source:
                synonym_tuples = parse_synonym_tuples(tuples_str)

                # Determine dataset from source
                dataset = determine_dataset(source)
                path = extract_path_from_source(source, dataset.split(':')[1].replace('Dataset', '').lower())

                for prop, value in synonym_tuples:
                    mappings.append({
                        'id': f'metpo-map:{mapping_id}',
                        'label': f'{value} ({dataset.split(":")[1].replace("Dataset", "")})',
                        'metpo_id': metpo_id,
                        'dataset': dataset,
                        'path': path,
                        'value': value,
                        'note': f'Property: {prop}'
                    })
                    mapping_id += 1

    return mappings


def extract_path_from_source(source: str, dataset_type: str) -> str:
    """Extract or infer the path/field name from the source URL."""
    if not source:
        return ""

    # Try to extract meaningful path info from URL
    if 'bacdive.dsmz.de' in source.lower():
        # Generic BacDive path - could be refined
        return "keywords"
    elif 'github.com/jmadin/bacteria_archaea_traits' in source.lower():
        # Madin dataset - use generic
        return "trait_field"
    elif 'ordar.otelo.univ-lorraine.fr' in source.lower() or 'BactoTraits' in source:
        # BactoTraits - the source might have the field name after the URL
        return "trait_category"

    return "field"


def determine_dataset(source: str) -> str:
    """Determine which dataset based on source URL."""
    source_lower = source.lower()

    if 'bacdive.dsmz.de' in source_lower:
        return 'metpo:BacDiveDataset'
    elif 'github.com/jmadin/bacteria_archaea_traits' in source_lower:
        return 'metpo:MadinDataset'
    elif 'ordar.otelo.univ-lorraine.fr' in source_lower or 'bactotraits' in source_lower:
        return 'metpo:BactoTraitsDataset'

    return 'metpo:UnknownDataset'


@click.command()
@click.option('--classes-template', '-c',
              type=click.Path(exists=True),
              default='src/templates/metpo_sheet.tsv',
              help='Path to metpo_sheet.tsv')
@click.option('--properties-template', '-p',
              type=click.Path(exists=True),
              default='src/templates/metpo-properties.tsv',
              help='Path to metpo-properties.tsv')
@click.option('--output', '-o',
              type=click.Path(),
              default='metpo-mappings-template.tsv',
              help='Output TSV file for mappings')
def main(classes_template: str, properties_template: str, output: str):
    """
    Convert attributed synonyms from METPO templates to Mapping instances.

    Reads attributed synonyms from metpo_sheet.tsv and metpo-properties.tsv
    and converts them to the new Mapping instance format compatible with
    ROBOT template.
    """
    click.echo("Extracting class synonyms...")
    class_mappings, next_id = extract_class_synonyms(Path(classes_template))
    click.echo(f"  Found {len(class_mappings)} class synonym mappings")

    click.echo("Extracting property synonyms...")
    property_mappings = extract_property_synonyms(Path(properties_template), next_id)
    click.echo(f"  Found {len(property_mappings)} property synonym mappings")

    all_mappings = class_mappings + property_mappings

    # Write output TSV
    click.echo(f"Writing {len(all_mappings)} mappings to {output}...")
    with open(output, 'w', newline='', encoding='utf-8') as f:
        # Write header rows
        f.write('ID\tTYPE\tlabel\tMETPO_ID\tDATASET\tPATH\tVALUE\tNOTE\n')
        f.write('ID\tTYPE\tLABEL\tI prov:entity\tI prov:wasDerivedFrom\t'
                'A skos:notation\tA schema:value\tA skos:note\n')

        # Write data rows
        writer = csv.DictWriter(f,
                                fieldnames=['id', 'label', 'metpo_id', 'dataset',
                                           'path', 'value', 'note'],
                                delimiter='\t')

        for mapping in all_mappings:
            f.write(f'{mapping["id"]}\tmetpo:Mapping\t"{mapping["label"]}"\t'
                   f'{mapping["metpo_id"]}\t{mapping["dataset"]}\t'
                   f'{mapping["path"]}\t"{mapping["value"]}"\t"{mapping["note"]}"\n')

    click.echo(f"Done! Generated {len(all_mappings)} total mappings.")
    click.echo(f"\nNext steps:")
    click.echo(f"  1. Review {output}")
    click.echo(f"  2. Run: make -f Makefile.metpo-mappings metpo-mappings")
    click.echo(f"  3. Verify metpo-mappings.ttl")


if __name__ == '__main__':
    main()
