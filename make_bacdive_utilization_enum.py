import pandas as pd
import yaml
import click
from typing import Dict, Any
from pathlib import Path


# Click CLI
@click.command()
@click.argument('tsv_file', type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('-o', '--output', 'output_file', type=click.Path(dir_okay=False, path_type=Path),
              help='Output YAML file path. If not specified, will use input filename with .yaml extension')
@click.option('--enum-name', default='OrganismChemicalRelationship',
              help='Name for the LinkML enumeration (default: OrganismChemicalRelationship)')
@click.option('--id-prefix', default='https://example.org/metpo-relationships',
              help='Base ID/URI for the LinkML schema (default: https://example.org/metpo-relationships)')
@click.option('--default-prefix', default='metpo',
              help='Default prefix for the schema (default: metpo)')
@click.option('--stats/--no-stats', default=True,
              help='Print summary statistics (default: True)')
@click.option('--preview/--no-preview', default=True,
              help='Show preview of generated YAML (default: True)')
def convert_tsv_to_linkml(tsv_file: Path, output_file: Path, enum_name: str,
                          id_prefix: str, default_prefix: str, stats: bool, preview: bool):
    """
    Convert a robot template TSV with two header rows into a LinkML enumeration.

    TSV_FILE: Path to the input TSV file with robot template format
    """

    # Determine output file if not specified
    if not output_file:
        output_file = tsv_file.with_suffix('.yaml')

    click.echo(f"Converting {tsv_file} to LinkML enumeration...")

    # Print stats if requested
    if stats:
        print_summary_stats(tsv_file)
        click.echo()

    # Convert to LinkML
    try:
        linkml_yaml = convert_tsv_to_linkml_enum(
            str(tsv_file),
            str(output_file),
            enum_name=enum_name,
            id_prefix=id_prefix,
            default_prefix=default_prefix
        )

        click.echo(f"✅ LinkML enumeration written to {output_file}")

        # Show preview if requested
        if preview:
            click.echo("\n=== Preview (first 30 lines) ===")
            preview_lines = linkml_yaml.split('\n')[:30]
            click.echo('\n'.join(preview_lines))
            if len(linkml_yaml.split('\n')) > 30:
                click.echo('...')

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


def convert_tsv_to_linkml_enum(tsv_file: str, output_file: str = None,
                               enum_name: str = 'OrganismChemicalRelationship',
                               id_prefix: str = 'https://example.org/metpo-relationships',
                               default_prefix: str = 'metpo') -> str:
    """
    Convert a robot template TSV with two header rows into a LinkML enumeration.

    Args:
        tsv_file: Path to the TSV file
        output_file: Optional output file path for the YAML

    Returns:
        LinkML YAML as string
    """

    # Read the TSV file, skipping the first header row
    df = pd.read_csv(tsv_file, sep='\t', skiprows=[1])

    # Filter for ObjectProperty rows that represent organism-chemical relationships
    object_properties = df[df['TYPE'] == 'owl:ObjectProperty'].copy()

    # Create the LinkML enumeration structure
    linkml_enum = {
        'id': id_prefix,
        'name': id_prefix.split('/')[-1] if '/' in id_prefix else id_prefix,
        'title': f'{enum_name} Enumeration',
        'description': 'Enumeration of relationships between organisms and chemicals derived from BacDive metabolic utilization data',
        'prefixes': {
            'linkml': 'https://w3id.org/linkml/',
            default_prefix: 'http://example.com/'
        },
        'default_prefix': default_prefix,
        'enums': {
            enum_name: {
                'description': 'Types of relationships between organisms and chemicals',
                'permissible_values': {}
            }
        }
    }

    # Process each relationship
    for _, row in object_properties.iterrows():
        # Extract the ID number from the full URI
        id_uri = row['ID']
        id_num = id_uri.split('/')[-1]

        # Create a code-friendly key from the label
        label = str(row['LABEL'])
        # Convert label to snake_case for the key
        key = label.lower().replace(' ', '_').replace('-', '_')

        # Create the permissible value entry
        pv_entry = {
            # 'text': label,
            'meaning': id_uri
        }

        # # Add description if we have bacdive key info
        # if pd.notna(row['bacdive key']) and row['bacdive key']:
        #     bacdive_key = row['bacdive key']
        #     description_parts = [f"Relationship type: {bacdive_key}"]
        #
        #     # Add count if available
        #     if pd.notna(row['bacdive count']) and str(row['bacdive count']).isdigit():
        #         count = int(row['bacdive count'])
        #         description_parts.append(f"BacDive occurrences: {count:,}")
        #
        #     # Add notes if available
        #     if pd.notna(row['notes']) and row['notes']:
        #         description_parts.append(f"Notes: {row['notes']}")
        #
        #     pv_entry['description'] = '; '.join(description_parts)

        # Add to permissible values
        linkml_enum['enums'][enum_name]['permissible_values'][key] = pv_entry

    # Convert to YAML
    yaml_output = yaml.dump(linkml_enum, default_flow_style=False, sort_keys=False, allow_unicode=True)

    # Clean up the YAML formatting
    yaml_output = yaml_output.replace("'", "")  # Remove unnecessary quotes

    # Write to file if specified
    if output_file:
        with open(output_file, 'w') as f:
            f.write(yaml_output)

    return yaml_output


def print_summary_stats(tsv_file: str):
    """Print summary statistics about the TSV data."""
    df = pd.read_csv(tsv_file, sep='\t', skiprows=[1])

    print("=== TSV File Summary ===")
    print(f"Total rows: {len(df)}")
    print(f"ObjectProperty rows: {len(df[df['TYPE'] == 'owl:ObjectProperty'])}")
    print(f"Class rows: {len(df[df['TYPE'] == 'owl:Class'])}")

    # Count positive vs negative relationships
    obj_props = df[df['TYPE'] == 'owl:ObjectProperty']
    positive_rels = obj_props[~obj_props['LABEL'].str.contains('does not', na=False)]
    negative_rels = obj_props[obj_props['LABEL'].str.contains('does not', na=False)]

    print(f"Positive relationships: {len(positive_rels)}")
    print(f"Negative relationships: {len(negative_rels)}")

    # Show total BacDive counts
    total_count = obj_props['bacdive count'].sum(skipna=True)
    print(f"Total BacDive occurrences: {total_count:,.0f}")


# Example usage and CLI entry point
if __name__ == "__main__":
    convert_tsv_to_linkml()
