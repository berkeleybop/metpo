"""
Thoroughly search extraction YAML files for METPO terms.
Parse YAML properly to find METPO IDs in nested structures.
"""

import json
from pathlib import Path

import click
import yaml


def find_metpo_in_obj(obj, path=""):
    """Recursively search for METPO terms in nested data structures."""
    metpo_terms = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            new_path = f"{path}.{key}" if path else key
            metpo_terms.extend(find_metpo_in_obj(value, new_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_path = f"{path}[{i}]"
            metpo_terms.extend(find_metpo_in_obj(item, new_path))
    elif isinstance(obj, str) and obj.startswith("METPO:"):
        metpo_terms.append((path, obj))

    return metpo_terms

def analyze_yaml_file(yaml_path):
    """Parse YAML file and find all METPO terms."""
    click.echo(f"\n{'='*80}")
    click.echo(f"Analyzing: {yaml_path.name}")
    click.echo(f"{'='*80}")

    with Path(yaml_path).open() as f:
        try:
            docs = list(yaml.safe_load_all(f))
        except yaml.YAMLError as e:
            click.echo(f"ERROR parsing YAML: {e}")
            return None

    click.echo(f"Number of documents in file: {len(docs)}")

    all_metpo_terms = []
    auto_terms = []

    for i, doc in enumerate(docs):
        if not doc:
            continue

        # Find METPO terms in entire document
        metpo_in_doc = find_metpo_in_obj(doc)
        all_metpo_terms.extend([(i, path, term) for path, term in metpo_in_doc])

        # Also find AUTO terms for comparison
        auto_in_doc = [(path, term) for path, term in find_metpo_in_obj(doc)
                       if isinstance(term, str) and term.startswith("AUTO:")]
        auto_terms.extend([(i, path, term) for path, term in auto_in_doc])

        # Show extracted_object structure for first few docs
        if i < 3 and "extracted_object" in doc:
            click.echo(f"\nDocument {i} extracted_object structure:")
            click.echo(json.dumps(doc["extracted_object"], indent=2)[:500])

    click.echo(f"\n{'='*80}")
    click.echo(f"RESULTS FOR {yaml_path.name}")
    click.echo(f"{'='*80}")
    click.echo(f"Total METPO terms found: {len(all_metpo_terms)}")
    click.echo(f"Total AUTO terms found: {len(auto_terms)}")

    if all_metpo_terms:
        click.echo("\n✓ METPO TERMS FOUND:")
        # Show first 20
        for doc_idx, path, term in all_metpo_terms[:20]:
            click.echo(f"  Doc {doc_idx}: {path} = {term}")
        if len(all_metpo_terms) > 20:
            click.echo(f"  ... and {len(all_metpo_terms) - 20} more")
    else:
        click.echo("\n✗ NO METPO TERMS FOUND")
        click.echo("\nAUTO terms (first 10):")
        for doc_idx, path, term in auto_terms[:10]:
            click.echo(f"  Doc {doc_idx}: {path} = {term}")

    return {
        "file": yaml_path.name,
        "metpo_count": len(all_metpo_terms),
        "auto_count": len(auto_terms),
        "metpo_terms": all_metpo_terms,
        "auto_terms": auto_terms
    }

@click.command()
@click.argument("yaml_dir", type=click.Path(exists=True, file_okay=False, path_type=Path),
                default=None, required=False)
@click.option("--pattern", default="*_fullcorpus_gpt4o_t00_20251031*.yaml",
              help="File pattern to match")
def main(yaml_dir, pattern):
    """Thoroughly search extraction YAML files for METPO terms.

    Parses YAML properly to find METPO IDs in nested structures.

    YAML_DIR: Directory containing YAML files (default: ./outputs)
    """
    if not yaml_dir:
        yaml_dir = Path(__file__).parent / "outputs"

    # Production files from pattern filter
    production_files = sorted(yaml_dir.glob(pattern))

    click.echo(f"Searching {len(production_files)} production YAML files for METPO terms...")
    click.echo("Using proper YAML parsing to find nested METPO IDs")

    results = []
    for yaml_file in production_files:
        result = analyze_yaml_file(yaml_file)
        results.append(result)

    # Summary
    click.echo(f"\n{'='*80}")
    click.echo("OVERALL SUMMARY")
    click.echo(f"{'='*80}")

    total_metpo = sum(r["metpo_count"] for r in results)
    total_auto = sum(r["auto_count"] for r in results)

    click.echo(f"\nTotal METPO terms across all files: {total_metpo}")
    click.echo(f"Total AUTO terms across all files: {total_auto}")

    if total_metpo > 0:
        click.echo("\n✓ SUCCESS! Found METPO terms in extraction files!")
        click.echo("\nFiles with METPO terms:")
        for r in results:
            if r["metpo_count"] > 0:
                click.echo(f"  {r['file']}: {r['metpo_count']} METPO terms")
    else:
        click.echo("\n✗ No METPO terms found in any production files")
        click.echo("\nThis suggests:")
        click.echo("  1. Templates may not have METPO annotators configured")
        click.echo("  2. METPO path in templates may be incorrect")
        click.echo("  3. Genuine grounding failures")

if __name__ == "__main__":
    main()
