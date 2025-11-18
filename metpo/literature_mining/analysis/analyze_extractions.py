"""Analyze OntoGPT extraction results to compare template performance."""

from collections import defaultdict
from pathlib import Path

import click
import yaml


def count_entities_and_grounding(yaml_file):
    """Count entities and grounding quality in a YAML extraction file."""
    with Path(yaml_file).open() as f:
        data = yaml.safe_load_all(f)

        stats = {
            "total_extractions": 0,
            "total_entities": 0,
            "grounded_entities": 0,
            "auto_entities": 0,
            "none_entities": 0,
            "total_relations": 0,
            "namespace_counts": defaultdict(int)
        }

        for doc in data:
            if not doc or "extracted_object" not in doc:
                continue

            stats["total_extractions"] += 1
            extracted = doc["extracted_object"]

            # Count named entities
            if "named_entities" in doc:
                for entity in doc["named_entities"]:
                    if not entity or "id" not in entity:
                        continue

                    entity_id = entity["id"]

                    # Skip "none" entities
                    if "none" in str(entity_id).lower():
                        stats["none_entities"] += 1
                        continue

                    stats["total_entities"] += 1

                    # Check namespace
                    if ":" in str(entity_id):
                        namespace = entity_id.split(":")[0]
                        stats["namespace_counts"][namespace] += 1

                        if namespace != "AUTO":
                            stats["grounded_entities"] += 1
                        else:
                            stats["auto_entities"] += 1

            # Count relationships/triples
            for key, value in extracted.items():
                if "relationship" in key.lower() and isinstance(value, list):
                    for rel in value:
                        if isinstance(rel, dict) and "subject" in rel:
                            # Skip "none" relationships
                            subject = str(rel.get("subject", ""))
                            if "none" not in subject.lower():
                                stats["total_relations"] += 1

        return stats

@click.command()
@click.argument("yaml_dir", type=click.Path(exists=True, file_okay=False, path_type=Path),
                default=None, required=False)
def main(yaml_dir):
    """Analyze OntoGPT extraction results by template.

    YAML_DIR: Directory containing YAML files (default: literature_mining/outputs)
    """
    if not yaml_dir:
        yaml_dir = Path("/Users/MAM/Documents/gitrepos/metpo/literature_mining/outputs")

    click.echo("=" * 80)
    click.echo("CMM Abstract Extraction Analysis")
    click.echo("=" * 80)
    click.echo()

    results = {}

    for yaml_file in sorted(yaml_dir.glob("*.yaml")):
        template_name = yaml_file.stem.rsplit("_", 2)[0]  # Remove timestamp
        stats = count_entities_and_grounding(yaml_file)
        results[template_name] = stats

        click.echo(f"Template: {template_name}")
        click.echo(f"  File: {yaml_file.name}")
        click.echo(f"  Extractions: {stats['total_extractions']}")
        click.echo(f"  Total entities (non-'none'): {stats['total_entities']}")
        click.echo(f"  Grounded entities (non-AUTO): {stats['grounded_entities']}")
        click.echo(f"  AUTO entities: {stats['auto_entities']}")
        click.echo(f"  'none' entities: {stats['none_entities']}")
        click.echo(f"  Total relations: {stats['total_relations']}")
        click.echo(f"  Avg entities per abstract: {stats['total_entities']/max(stats['total_extractions'], 1):.1f}")
        click.echo(f"  Avg relations per abstract: {stats['total_relations']/max(stats['total_extractions'], 1):.1f}")
        click.echo(f"  Grounding rate: {100*stats['grounded_entities']/max(stats['total_entities'], 1):.1f}%")
        click.echo(f"  Namespaces used: {dict(stats['namespace_counts'])}")
        click.echo()

    click.echo("=" * 80)
    click.echo("SUMMARY - Ranked by Total Entities + Relations")
    click.echo("=" * 80)
    click.echo()

    ranked = sorted(results.items(),
                   key=lambda x: x[1]["total_entities"] + x[1]["total_relations"],
                   reverse=True)

    for template_name, stats in ranked:
        total_extracted = stats["total_entities"] + stats["total_relations"]
        click.echo(f"{template_name:30} | Entities: {stats['total_entities']:4} | Relations: {stats['total_relations']:4} | Total: {total_extracted:4} | Grounded: {stats['grounded_entities']:4} ({100*stats['grounded_entities']/max(stats['total_entities'], 1):5.1f}%)")

if __name__ == "__main__":
    main()
