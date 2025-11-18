"""
Extract all METPO entities from OntoGPT extraction YAML files.
Shows which METPO classes were successfully grounded.
"""

import re
from pathlib import Path

import click
import yaml


def extract_metpo_entities(yaml_file):
    """Extract METPO entities from a single YAML file."""
    metpo_entities = []

    with Path(yaml_file).open() as f:
        try:
            docs = list(yaml.safe_load_all(f))
        except yaml.YAMLError as e:
            click.echo(f"Error parsing {yaml_file}: {e}")
            return []

    for doc in docs:
        if not doc or "named_entities" not in doc:
            continue

        for entity in doc.get("named_entities", []):
            entity_id = entity.get("id", "")
            if isinstance(entity_id, str) and "w3id.org/metpo/" in entity_id:
                metpo_entities.append(
                    {
                        "id": entity_id,
                        "label": entity.get("label", "NO LABEL"),
                        "file": yaml_file.name,
                    }
                )

    return metpo_entities


@click.command()
@click.argument(
    "yaml_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    required=False,
)
@click.option(
    "-o",
    "--output",
    "output_file",
    type=click.Path(path_type=Path),
    help="Output TSV file for results",
)
@click.option("--recursive/--no-recursive", default=True, help="Search subdirectories recursively")
def main(yaml_dir, output_file, recursive):
    """Extract METPO entities from OntoGPT extraction YAML files.

    Shows which METPO classes were successfully grounded during extraction.

    YAML_DIR: Directory containing YAML files (default: literature_mining/outputs)
    """
    if not yaml_dir:
        yaml_dir = Path("literature_mining/outputs")

    all_metpo_entities = []
    files_with_metpo = []

    # Search all YAML files
    yaml_files = list(yaml_dir.rglob("*.yaml")) if recursive else list(yaml_dir.glob("*.yaml"))

    click.echo(f"Searching {len(yaml_files)} YAML files for METPO entities...")
    click.echo()

    for yaml_file in yaml_files:
        entities = extract_metpo_entities(yaml_file)
        if entities:
            all_metpo_entities.extend(entities)
            files_with_metpo.append((yaml_file, len(entities)))
            click.echo(f"✓ {yaml_file.name}: {len(entities)} METPO entities")

    click.echo()
    click.echo(f"Total files with METPO: {len(files_with_metpo)}")
    click.echo(f"Total METPO entities: {len(all_metpo_entities)}")
    click.echo()

    # Get unique METPO classes
    unique_classes = {}
    for entity in all_metpo_entities:
        # Extract numeric ID
        match = re.search(r"metpo/(\d+)", entity["id"])
        if match:
            metpo_id = match.group(1)
            if metpo_id not in unique_classes:
                unique_classes[metpo_id] = {"uri": entity["id"], "labels": set(), "count": 0}
            unique_classes[metpo_id]["labels"].add(entity["label"])
            unique_classes[metpo_id]["count"] += 1

    click.echo(f"Unique METPO classes: {len(unique_classes)}")
    click.echo()
    click.echo("=" * 80)
    click.echo("METPO CLASSES SUCCESSFULLY GROUNDED")
    click.echo("=" * 80)
    click.echo()

    for metpo_id in sorted(unique_classes.keys()):
        info = unique_classes[metpo_id]
        click.echo(f"METPO:{metpo_id}")
        click.echo(f"  URI: {info['uri']}")
        click.echo(f"  Occurrences: {info['count']}")
        click.echo("  Labels extracted:")
        for label in sorted(info["labels"]):
            click.echo(f"    - {label}")
        click.echo()

    # Save results
    if not output_file:
        output_file = Path("literature_mining/METPO_GROUNDED_CLASSES.tsv")
    with Path(output_file).open("w") as f:
        f.write("METPO_ID\tURI\tLabel\tOccurrences\tFiles\n")
        for metpo_id in sorted(unique_classes.keys()):
            info = unique_classes[metpo_id]
            files = {
                e["file"] for e in all_metpo_entities if re.search(f"metpo/{metpo_id}", e["id"])
            }
            label_str = "; ".join(sorted(info["labels"]))
            file_str = "; ".join(sorted(files))
            f.write(f"METPO:{metpo_id}\t{info['uri']}\t{label_str}\t{info['count']}\t{file_str}\n")

    click.echo(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()
