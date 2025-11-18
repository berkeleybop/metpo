#!/usr/bin/env python3
"""Convert chem_interaction_props.tsv to LinkML enumeration format."""

import re
from pathlib import Path
import click
import pandas as pd
import yaml


@click.command()
@click.option("--input-file", "-i", 
              default="literature_mining/chem_interaction_props.tsv",
              help="Input TSV file path")
@click.option("--output-file", "-o", 
              help="Output YAML file path (if not specified, prints to stdout)")
def convert_chem_props(input_file, output_file):
    """Convert chem_interaction_props.tsv to LinkML enumeration format."""
    
    # Read the TSV file
    df = pd.read_csv(input_file, sep="\t")

    # Build the data structure
    permissible_values = {}
    
    for _, row in df.iterrows():
        # Extract IRI and label
        iri = row["?chem_interaction_prop"]
        label = row["?label"].strip('"')
        
        # Convert label to enum key (replace spaces/special chars with underscores)
        enum_key = re.sub(r"[^a-zA-Z0-9_]", "_", label.lower())
        enum_key = re.sub(r"_+", "_", enum_key)  # collapse multiple underscores
        enum_key = enum_key.strip("_")  # remove leading/trailing underscores
        
        # Extract CURIE from IRI
        curie = iri.replace("<https://w3id.org/metpo/", "METPO:").replace(">", "")
        
        permissible_values[enum_key] = {
            "description": label,
            "meaning": curie
        }
    
    # Create the final structure
    data = {
        "enums": {
            "ChemicalInteractionPropertyEnum": {
                "permissible_values": permissible_values
            }
        }
    }
    
    # Output YAML
    yaml_output = yaml.dump(data, default_flow_style=False, sort_keys=False)
    
    if output_file:
        Path(output_file).write_text(yaml_output)
        click.echo(f"Written to {output_file}")
    else:
        click.echo(yaml_output)


if __name__ == "__main__":
    convert_chem_props()