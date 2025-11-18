"""
NER Coverage Visualization Tool

Analyzes and visualizes named entity recognition coverage from OntoGPT output.
Creates HTML visualization showing text spans and coverage metrics.
"""

import re
from collections import Counter
from pathlib import Path

import click
import yaml


def load_ontogpt_output(yaml_file: str) -> dict:
    """Load OntoGPT output YAML file."""
    with Path(yaml_file).open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def extract_text_and_entities(data: dict) -> tuple[str, list[dict]]:
    """Extract input text and named entities from OntoGPT output."""
    text = data.get("input_text", "")
    entities = data.get("named_entities", [])
    return text, entities


def get_entity_type_colors() -> dict[str, str]:
    """Define color scheme for different entity types."""
    return {
        "chemical": "#FF6B6B",  # Red
        "enzyme": "#4ECDC4",  # Teal
        "lipid": "#45B7D1",  # Blue
        "organism": "#96CEB4",  # Green
        "species": "#FECA57",  # Yellow
        "strain": "#FF9FF3",  # Pink
        "type_strain": "#E74C3C",  # Dark Red (type strains)
        "phenotype": "#54A0FF",  # Light Blue
        "chebi": "#FF6B6B",  # Red (chemicals)
        "ncbitaxon": "#96CEB4",  # Green (organisms)
        "micro": "#54A0FF",  # Light Blue (phenotypes)
        "auto": "#DDA0DD",  # Plum (auto-generated)
        "default": "#E0E0E0",  # Light Gray
    }


def categorize_entity(entity_id: str, label: str) -> str:
    """Categorize entity based on ID prefix or label content."""
    if entity_id.startswith("CHEBI:"):
        return "chemical"
    if entity_id.startswith("NCBITaxon:"):
        return "organism"
    if entity_id.startswith("MICRO:"):
        return "phenotype"
    if entity_id.startswith("AUTO:"):
        # Try to categorize AUTO entities by content
        label_lower = label.lower()
        if any(term in label_lower for term in ["ase", "enzyme", "activity"]):
            return "enzyme"
        if any(term in label_lower for term in ["fatty", "lipid", "acid", "c16", "c18"]):
            return "lipid"
        if re.match(r"^[A-Z]+\d+[A-Z]*T$", label):  # Type strain pattern like MD5T
            return "type_strain"
        if re.match(r"^[A-Z]+\d+[A-Z]*$", label):  # Strain pattern like MD5
            return "strain"
        if "sp." in label or len(label.split()) >= 2:  # Species pattern
            return "species"
        return "auto"
    return "default"


def calculate_coverage_metrics(text: str, entities: list[dict]) -> dict:
    """Calculate coverage metrics for the NER results."""
    text_length = len(text)
    covered_chars = set()

    # Track covered character positions
    for entity in entities:
        spans = entity.get("original_spans", [])
        for span in spans:
            if isinstance(span, str) and ":" in span:
                start, end = map(int, span.split(":"))
                # Fix OntoGPT span issue - add 1 to end coordinate to include last character
                end = end + 1
                covered_chars.update(range(start, end))

    coverage_percentage = len(covered_chars) / text_length * 100 if text_length > 0 else 0

    # Entity type distribution
    entity_types = [categorize_entity(e.get("id", ""), e.get("label", "")) for e in entities]
    type_counts = Counter(entity_types)

    # Total spans
    total_spans = sum(len(e.get("original_spans", [])) for e in entities)

    return {
        "text_length": text_length,
        "covered_characters": len(covered_chars),
        "coverage_percentage": round(coverage_percentage, 2),
        "total_entities": len(entities),
        "total_spans": total_spans,
        "entity_density": round(len(entities) / text_length * 1000, 2),  # entities per 1000 chars
        "type_distribution": dict(type_counts),
    }


def create_html_visualization(text: str, entities: list[dict], metrics: dict) -> str:
    """Create HTML visualization of NER coverage."""
    colors = get_entity_type_colors()

    # Create spans with entity information
    spans = []
    for entity in entities:
        entity_id = entity.get("id", "")
        label = entity.get("label", "")
        entity_type = categorize_entity(entity_id, label)
        color = colors.get(entity_type, colors["default"])

        for span in entity.get("original_spans", []):
            if isinstance(span, str) and ":" in span:
                start, end = map(int, span.split(":"))
                # Fix OntoGPT span issue - add 1 to end coordinate to include last character
                end = end + 1
                spans.append(
                    {
                        "start": start,
                        "end": end,
                        "label": label,
                        "id": entity_id,
                        "type": entity_type,
                        "color": color,
                    }
                )

    # Sort spans by start position
    spans.sort(key=lambda x: x["start"])

    # Build highlighted HTML
    html_parts = []
    last_pos = 0

    for span in spans:
        # Add unhighlighted text before this span
        if span["start"] > last_pos:
            html_parts.append(text[last_pos : span["start"]])

        # Add highlighted span
        span_text = text[span["start"] : span["end"]]
        tooltip = f"{span['type']}: {span['label']} ({span['id']})"
        html_parts.append(
            f'<span class="entity {span["type"]}" style="background-color: {span["color"]}; '
            f'padding: 1px 2px; margin: 1px; border-radius: 2px;" title="{tooltip}">'
            f"{span_text}</span>"
        )

        last_pos = max(last_pos, span["end"])

    # Add remaining unhighlighted text
    if last_pos < len(text):
        html_parts.append(text[last_pos:])

    highlighted_text = "".join(html_parts)

    # Create metrics table
    metrics_html = f"""
    <div class="metrics">
        <h3>Coverage Metrics</h3>
        <table>
            <tr><td>Text Length:</td><td>{metrics["text_length"]} characters</td></tr>
            <tr><td>Covered Characters:</td><td>{metrics["covered_characters"]}</td></tr>
            <tr><td>Coverage Percentage:</td><td>{metrics["coverage_percentage"]}%</td></tr>
            <tr><td>Total Entities:</td><td>{metrics["total_entities"]}</td></tr>
            <tr><td>Total Spans:</td><td>{metrics["total_spans"]}</td></tr>
            <tr><td>Entity Density:</td><td>{metrics["entity_density"]} per 1000 chars</td></tr>
        </table>

        <h4>Entity Type Distribution</h4>
        <table>
    """

    for entity_type, count in sorted(metrics["type_distribution"].items()):
        color = colors.get(entity_type, colors["default"])
        metrics_html += f'<tr><td><span style="background-color: {color}; padding: 2px 8px; border-radius: 2px;">{entity_type}</span></td><td>{count}</td></tr>'

    metrics_html += "</table></div>"

    # Complete HTML document
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NER Coverage Visualization</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .text-content {{
                background: #f9f9f9;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
                white-space: pre-wrap;
                font-family: 'Courier New', monospace;
            }}
            .metrics {{
                background: #fff;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin: 20px 0;
            }}
            table {{ border-collapse: collapse; width: 100%; }}
            td {{ padding: 8px; border-bottom: 1px solid #eee; }}
            .entity {{ cursor: help; }}
            h1, h2, h3 {{ color: #333; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Named Entity Recognition Coverage Analysis</h1>

            {metrics_html}

            <h2>Highlighted Text</h2>
            <div class="text-content">
{highlighted_text}
            </div>
        </div>
    </body>
    </html>
    """

    return html


@click.command()
@click.argument("input_file", type=click.Path(exists=True, readable=True))
@click.option(
    "-o",
    "--output",
    "output_file",
    default="ner_visualization.html",
    help="Output HTML file",
    show_default=True,
)
@click.option("--quiet", "-q", is_flag=True, help="Suppress output messages")
@click.option("--stats-only", is_flag=True, help="Only print statistics, do not generate HTML")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["html", "json"], case_sensitive=False),
    default="html",
    help="Output format",
    show_default=True,
)
def main(input_file, output_file, quiet, stats_only, output_format):
    """Visualize NER coverage from OntoGPT output.

    INPUT_FILE: OntoGPT output YAML file to analyze
    """
    if not quiet:
        click.echo(f"Loading OntoGPT output from {input_file}")

    # Load data
    try:
        data = load_ontogpt_output(input_file)
    except Exception as e:
        click.echo(f"Error loading file: {e}", err=True)
        raise click.Abort from e

    # Extract text and entities
    text, entities = extract_text_and_entities(data)
    if not quiet:
        click.echo(f"Found {len(entities)} entities in {len(text)} characters of text")

    # Calculate metrics
    metrics = calculate_coverage_metrics(text, entities)
    if not quiet:
        click.echo(f"Coverage: {metrics['coverage_percentage']}% of text")

    # Print statistics
    if not quiet or stats_only:
        click.echo("\nCoverage Summary:")
        for key, value in metrics.items():
            if key != "type_distribution":
                click.echo(f"  {key}: {value}")

        click.echo("\nEntity Types:")
        for entity_type, count in sorted(metrics["type_distribution"].items()):
            click.echo(f"  {entity_type}: {count}")

    # Generate output
    if not stats_only:
        if output_format.lower() == "html":
            html = create_html_visualization(text, entities, metrics)
            try:
                with Path(output_file).open("w", encoding="utf-8") as f:
                    f.write(html)
                if not quiet:
                    click.echo(f"\nVisualization saved to {output_file}")
            except Exception as e:
                click.echo(f"Error writing output file: {e}", err=True)
                raise click.Abort from e

        elif output_format.lower() == "json":
            import json

            output_data = {"metrics": metrics, "entities": entities, "text_length": len(text)}
            try:
                with Path(output_file).open("w", encoding="utf-8") as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                if not quiet:
                    click.echo(f"\nJSON data saved to {output_file}")
            except Exception as e:
                click.echo(f"Error writing JSON file: {e}", err=True)
                raise click.Abort from e


if __name__ == "__main__":
    main()
