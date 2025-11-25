"""Regenerate curator_proposed_definitions.tsv from undergraduate source files"""

import csv
from pathlib import Path

import click

# Curator info mapping
CURATOR_INFO = {
    "curator4_all_terms.tsv": {"number": 4, "name": "Anthea Guo", "github": "crocodile27"},
    "curator5_all_terms_v3.tsv": {
        "number": 5,
        "name": "Jed Dongjin Kim-Ozaeta",
        "github": "jedkim-ozaeta",
    },
    "curator6_all_terms.tsv": {"number": 6, "name": "Luke Wang", "github": "lukewangCS121"},
}

@click.command()
@click.option(
    "--curator-dir",
    type=click.Path(exists=True, path_type=Path),
    default="data/undergraduate_definitions",
    help="Directory containing curator TSV files",
)
@click.option(
    "--output-file",
    "-o",
    type=click.Path(path_type=Path),
    default="data/undergraduate_definitions/curator_proposed_definitions.tsv",
    help="Output consolidated TSV file",
)
def main(curator_dir: Path, output_file: Path):
    """
    Regenerate consolidated curator definitions from individual curator files.

    Combines curator4_all_terms.tsv, curator5_all_terms_v3.tsv, and
    curator6_all_terms.tsv into a single integrated file with proper attributions.
    """
    # Collect all rows
    all_rows = []

    for filename, info in CURATOR_INFO.items():
        filepath = curator_dir / filename

        if not filepath.exists():
            click.echo(f"Warning: {filepath} not found")
            continue

    with Path(filepath).open() as f:
        lines = f.readlines()

    # Skip header rows (both say "ID")
    # Data starts at line 3 (index 2)
    header = lines[0].strip().split("\t")

    reader = csv.DictReader(lines[2:], delimiter="\t", fieldnames=header)

    for row in reader:
        metpo_id = row.get("ID", "").strip()
        if not metpo_id or not metpo_id.startswith("METPO:"):
            continue

        # Create output row with original data exactly as provided
        # Handle None values from row.get()
        def safe_get(d, key, default=""):
            val = d.get(key, default)
            return val.strip() if val else default

        output_row = {
            "metpo_id": metpo_id,
            "label": safe_get(row, "label"),
            "curator_number": info["number"],
            "curator_name": info["name"],
            "github_handle": info["github"],
            "proposed_definition": safe_get(row, "description"),
            "definition_source": safe_get(row, "definition source"),
            "has_definition_source": "Yes" if safe_get(row, "definition source") else "No",
            "subclass_of_label": safe_get(row, "parent class"),
            "subclass_of_id": safe_get(row, "parent classes (one strongly preferred)"),
            "reasoning": safe_get(row, "comment"),
            "quantitative_values": safe_get(row, "quantitative_values"),
        }

            all_rows.append(output_row)

    # Sort by metpo_id
    all_rows.sort(key=lambda x: x["metpo_id"])

    # Create output directory
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write to output file
    fieldnames = [
        "metpo_id",
        "label",
        "curator_number",
        "curator_name",
        "github_handle",
        "proposed_definition",
        "definition_source",
        "has_definition_source",
        "subclass_of_label",
        "subclass_of_id",
        "reasoning",
        "quantitative_values",
    ]

    with Path(output_file).open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(all_rows)

    click.echo(f"✓ Regenerated {output_file}")
    click.echo(f"  Total rows: {len(all_rows)}")
    click.echo(f"  Unique terms: {len({r['metpo_id'] for r in all_rows})}")


if __name__ == "__main__":
    main()
