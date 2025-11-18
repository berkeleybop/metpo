"""
Filtered METPO grounding analysis - analyze only production-quality extractions.
Excludes experimental/superseded runs to show realistic, representative results.
"""

from collections import Counter
from pathlib import Path

import click

from metpo.literature_mining.analysis.analyze_metpo_grounding import (
    extract_entities_from_yaml,
    find_auto_terms_with_context,
    find_metpo_successes_with_context,
)

# Define production-quality file patterns
PRODUCTION_PATTERNS = {
    "fullcorpus_strict": [
        # Strict: Only Oct 31 fullcorpus runs with gpt4o temp=0.0
        "*_fullcorpus_gpt4o_t00_20251031*.yaml"
    ],
    "fullcorpus_and_hybrid": [
        # Includes fullcorpus + hybrid template runs from Oct 31
        "*_fullcorpus_gpt4o_t00_20251031*.yaml",
        "*_hybrid_gpt4o_t00_20251031*.yaml",
    ],
    "all_oct31_production": [
        # All Oct 31 production files (excluding archive/, test, prototype)
        "*_gpt4o_t00_20251031*.yaml",
        "*_fullcorpus_*_20251031*.yaml",
        "*_hybrid_*_20251031*.yaml",
        "cmm_fullcorpus_*.yaml",
    ],
}

EXCLUDE_PATTERNS = ["archive/", "*_test_*", "*_prototype_*", "*_v2_*", "*_v3_*", "*_v4_*"]


def filter_yaml_files(dir_path: Path, pattern_set: str = "fullcorpus_strict") -> list[Path]:
    """Filter YAML files based on production quality criteria."""
    patterns = PRODUCTION_PATTERNS.get(pattern_set, PRODUCTION_PATTERNS["fullcorpus_strict"])

    all_files = []
    for pattern in patterns:
        all_files.extend(dir_path.glob(pattern))

    # Remove duplicates
    all_files = list(set(all_files))

    # Filter out excluded patterns
    filtered_files = []
    for f in all_files:
        exclude = False
        for exclude_pattern in EXCLUDE_PATTERNS:
            if exclude_pattern in str(f):
                exclude = True
                break
        if not exclude:
            filtered_files.append(f)

    return sorted(filtered_files)


def analyze_directory_filtered(dir_path: Path, pattern_set: str = "fullcorpus_strict") -> dict:
    """Analyze only production-quality YAML files."""
    results = {
        "summary": Counter(),
        "auto_examples": [],
        "metpo_examples": [],
        "files_analyzed": [],
        "template_annotators": {},
        "pattern_set": pattern_set,
    }

    yaml_files = filter_yaml_files(dir_path, pattern_set)

    click.echo(f"Pattern set: {pattern_set}")
    click.echo(f"Found {len(yaml_files)} production-quality YAML files in {dir_path}")
    click.echo("\nFiles included:")
    for f in yaml_files:
        click.echo(f"  - {f.name}")
    click.echo()

    for yaml_file in yaml_files:
        if yaml_file.stat().st_size == 0:
            continue

        click.echo(f"Analyzing {yaml_file.name}...")
        results["files_analyzed"].append(yaml_file.name)

        # Count all entity types
        entities = extract_entities_from_yaml(yaml_file)
        for prefix, ids in entities.items():
            results["summary"][prefix] += len(ids)

        # Collect examples
        if entities.get("AUTO"):
            auto_ex = find_auto_terms_with_context(yaml_file, limit=5)
            results["auto_examples"].extend(auto_ex)

        if entities.get("METPO"):
            metpo_ex = find_metpo_successes_with_context(yaml_file, limit=5)
            results["metpo_examples"].extend(metpo_ex)

    return results


@click.command()
@click.argument(
    "yaml_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    required=False,
)
@click.option(
    "--pattern-set",
    type=click.Choice(list(PRODUCTION_PATTERNS.keys())),
    default="fullcorpus_strict",
    show_default=True,
    help="File pattern set to use for filtering",
)
@click.option(
    "-o",
    "--output",
    "output_file",
    type=click.Path(path_type=Path),
    help="Output file for detailed results",
)
def main(yaml_dir, pattern_set, output_file):
    """Filtered METPO grounding analysis - production-quality extractions only.

    Excludes experimental/superseded runs to show realistic, representative results.

    YAML_DIR: Directory containing OntoGPT YAML output files (default: ./outputs)
    """
    if not yaml_dir:
        yaml_dir = Path(__file__).parent / "outputs"

    click.echo("=" * 80)
    click.echo("METPO GROUNDING ANALYSIS - PRODUCTION QUALITY ONLY")
    click.echo("For ICBO 2025 - Representative Results")
    click.echo("=" * 80)
    click.echo()

    results = analyze_directory_filtered(yaml_dir, pattern_set)

    click.echo("\n" + "=" * 80)
    click.echo("PRODUCTION FILE SUMMARY")
    click.echo("=" * 80)
    click.echo(f"\nPattern set: {pattern_set}")
    click.echo(f"Files analyzed: {len(results['files_analyzed'])}")
    for fname in results["files_analyzed"]:
        click.echo(f"  - {fname}")

    click.echo("\n" + "=" * 80)
    click.echo("ENTITY STATISTICS")
    click.echo("=" * 80)
    click.echo("\nEntity type counts:")
    for prefix, count in sorted(results["summary"].items(), key=lambda x: -x[1]):
        click.echo(f"  {prefix:15s}: {count:6d}")

    # Calculate grounding rate
    metpo_count = results["summary"].get("METPO", 0)
    auto_count = results["summary"].get("AUTO", 0)
    total_phenotype = metpo_count + auto_count

    if total_phenotype > 0:
        grounding_rate = (metpo_count / total_phenotype) * 100
        click.echo(
            f"\nPhenotype grounding rate: {grounding_rate:.1f}% ({metpo_count}/{total_phenotype})"
        )
        click.echo(f"AUTO term rate: {100 - grounding_rate:.1f}% ({auto_count}/{total_phenotype})")
    else:
        click.echo("\nNo METPO or AUTO terms found")

    # Count total extractions
    total_extractions = 0
    for fname in results["files_analyzed"]:
        fpath = yaml_dir / fname
        with Path(fpath).open() as f:
            total_extractions += f.read().count("input_text:")

    click.echo(f"\nTotal paper extractions: {total_extractions}")

    # Show examples
    click.echo("\n" + "=" * 80)
    click.echo("EXAMPLES: SUCCESSFUL METPO GROUNDING")
    click.echo("=" * 80)
    click.echo(
        f"\nFound {len(results['metpo_examples'])} examples where METPO successfully grounded terms\n"
    )

    for i, example in enumerate(results["metpo_examples"][:10], 1):
        click.echo(f"\n{i}. File: {example['file']}")
        click.echo(f"   Template: {example.get('template_name', 'unknown')}")
        if example.get("pmid"):
            click.echo(f"   PMID: {example['pmid']}")
        if example.get("doi"):
            click.echo(f"   DOI: {example['doi']}")
        click.echo(f"   METPO terms: {', '.join('METPO:' + t for t in example['metpo_terms'])}")
        if example["context"] != "No context":
            click.echo(f"   Context: {example['context'][:150]}...")

    click.echo("\n" + "=" * 80)
    click.echo("EXAMPLES: AUTO: TERMS INDICATING METPO GAPS")
    click.echo("=" * 80)
    click.echo(f"\nFound {len(results['auto_examples'])} examples with AUTO: terms\n")

    for i, example in enumerate(results["auto_examples"][:20], 1):
        click.echo(f"\n{i}. Extraction: {example['file']}")
        click.echo(f"   Template: {example.get('template_name', 'unknown')}")
        if example.get("pmid"):
            click.echo(f"   PMID: {example['pmid']}")
        if example.get("doi"):
            click.echo(f"   DOI: {example['doi']}")
        if example.get("title"):
            click.echo(f"   Paper title: {example['title'][:80]}...")
        click.echo(f"   AUTO terms: {', '.join(example['auto_terms'])}")
        if example["context"] != "No context":
            click.echo(f"   Context: {example['context'][:150]}...")

    click.echo("\n" + "=" * 80)
    click.echo("INTERPRETATION FOR ICBO TALK")
    click.echo("=" * 80)
    click.echo(f"""
This analysis uses ONLY production-quality extractions ({pattern_set}):
- Late October 2025 runs (mature templates)
- Full corpus or hybrid optimized templates
- GPT-4o with temperature 0.0 (deterministic)
- Excludes experimental/superseded runs

Key findings:
1. Grounding rate: {grounding_rate:.1f}% shows realistic free-text mining performance
2. AUTO: terms reveal systematic gaps - candidates for METPO expansion
3. Contrast with structured DB alignment (54-60% coverage) shows METPO optimized for
   semi-structured data integration, not free-text mining
4. Total corpus: {total_extractions} paper extractions across {len(results["files_analyzed"])} extraction runs

Recommendation: Report these numbers for ICBO - honest, representative, reproducible.
""")

    # Save results
    if not output_file:
        output_file = Path(__file__).parent / f"metpo_grounding_production_{pattern_set}.txt"
    with Path(output_file).open("w") as f:
        f.write("METPO Grounding Analysis - Production Quality\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Pattern set: {pattern_set}\n")
        f.write(f"Files analyzed: {len(results['files_analyzed'])}\n\n")
        for fname in results["files_analyzed"]:
            f.write(f"  {fname}\n")

        f.write(f"\nTotal extractions: {total_extractions}\n")
        f.write("\nEntity counts:\n")
        for prefix, count in sorted(results["summary"].items(), key=lambda x: -x[1]):
            f.write(f"  {prefix}: {count}\n")

        if total_phenotype > 0:
            f.write(f"\nGrounding rate: {grounding_rate:.1f}%\n")
            f.write(f"AUTO rate: {100 - grounding_rate:.1f}%\n")

        f.write("\n\nAUTO: TERM EXAMPLES (METPO GAPS):\n" + "=" * 80 + "\n")
        for example in results["auto_examples"][:30]:
            f.write(f"\nFile: {example['file']}\n")
            f.write(f"Template: {example.get('template_name', 'unknown')}\n")
            if example.get("pmid"):
                f.write(f"PMID: {example['pmid']}\n")
            if example.get("doi"):
                f.write(f"DOI: {example['doi']}\n")
            f.write(f"AUTO terms: {example['auto_terms']}\n")
            if example["context"] != "No context":
                f.write(f"Context: {example['context'][:200]}\n")
            f.write("-" * 80 + "\n")

    click.echo(f"\nDetailed results saved to: {output_file}")


if __name__ == "__main__":
    main()
