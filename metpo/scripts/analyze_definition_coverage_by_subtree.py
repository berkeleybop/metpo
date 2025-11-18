#!/usr/bin/env python3
"""
Analyze definition coverage by parent class (subtree analysis).

Identifies near-terminal parents where most children have definitions,
helping with iterative definition strategy.
"""
import click
import csv
from collections import defaultdict
from pathlib import Path


def load_metpo_hierarchy(tsv_path: str) -> dict:
    """Load METPO terms with parent-child relationships."""
    terms = {}
    parent_to_children = defaultdict(list)

    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            term_id = row['ID']
            label = row['label']
            definition = row.get('description', '').strip()
            parents = row.get('parent classes (one strongly preferred)', '').strip()

            # Parse parents (pipe-separated)
            parent_list = [p.strip() for p in parents.split('|') if p.strip()]

            terms[term_id] = {
                'id': term_id,
                'label': label,
                'definition': definition,
                'has_definition': bool(definition),
                'parents': parent_list
            }

            # Build parent-child index
            for parent in parent_list:
                parent_to_children[parent].append(term_id)

    return terms, parent_to_children


def find_parent_id_by_label(terms: dict, parent_label: str) -> str:
    """Find term ID by label."""
    for term_id, term_data in terms.items():
        if term_data['label'] == parent_label:
            return term_id
    return None


def analyze_coverage(terms: dict, parent_to_children: dict) -> list:
    """Analyze definition coverage for each parent class."""
    results = []

    for parent_label, child_ids in parent_to_children.items():
        # Skip if no children
        if not child_ids:
            continue

        # Count children with definitions
        total_children = len(child_ids)
        children_with_defs = sum(1 for cid in child_ids if terms.get(cid, {}).get('has_definition'))
        coverage_pct = (children_with_defs / total_children) * 100 if total_children > 0 else 0

        # Find parent term ID
        parent_id = find_parent_id_by_label(terms, parent_label)
        parent_has_def = terms.get(parent_id, {}).get('has_definition', False) if parent_id else False

        # Identify stragglers (children without definitions)
        stragglers = [
            f"{terms[cid]['label']} ({cid})"
            for cid in child_ids
            if not terms.get(cid, {}).get('has_definition')
        ]

        # Get examples of defined children
        examples = [
            f"{terms[cid]['label']} ({cid})"
            for cid in child_ids
            if terms.get(cid, {}).get('has_definition')
        ][:5]  # Limit to 5 examples

        results.append({
            'parent_label': parent_label,
            'parent_id': parent_id or '',
            'parent_has_definition': parent_has_def,
            'total_children': total_children,
            'children_with_definitions': children_with_defs,
            'coverage_percent': round(coverage_pct, 1),
            'stragglers': ' | '.join(stragglers) if stragglers else '',
            'straggler_count': len(stragglers),
            'example_defined_children': ' | '.join(examples)
        })

    return results


@click.command()
@click.option(
    '--metpo-tsv',
    type=click.Path(exists=True),
    default='src/templates/metpo_sheet_improved.tsv',
    help='Path to METPO template TSV file'
)
@click.option(
    '--output',
    type=click.Path(),
    default='reports/definition_coverage_by_parent.tsv',
    help='Output TSV file path'
)
@click.option(
    '--min-children',
    type=int,
    default=2,
    help='Minimum number of children to include parent in analysis (default: 2)'
)
@click.option(
    '--sort-by',
    type=click.Choice(['coverage', 'stragglers', 'total']),
    default='coverage',
    help='Sort results by: coverage (desc), stragglers (asc), or total children (desc)'
)
def main(metpo_tsv: str, output: str, min_children: int, sort_by: str):
    """
    Analyze definition coverage by parent class.

    Identifies near-terminal parents where most children have definitions,
    helping prioritize iterative definition work.

    Example:
        uv run analyze-definition-coverage-by-subtree
        uv run analyze-definition-coverage-by-subtree --sort-by stragglers --min-children 5
    """
    click.echo(f"Loading METPO hierarchy from {metpo_tsv}...")
    terms, parent_to_children = load_metpo_hierarchy(metpo_tsv)

    click.echo(f"Analyzing definition coverage for {len(parent_to_children)} parent classes...")
    results = analyze_coverage(terms, parent_to_children)

    # Filter by minimum children
    results = [r for r in results if r['total_children'] >= min_children]

    # Sort results
    if sort_by == 'coverage':
        results.sort(key=lambda x: x['coverage_percent'], reverse=True)
    elif sort_by == 'stragglers':
        results.sort(key=lambda x: x['straggler_count'])
    else:  # total
        results.sort(key=lambda x: x['total_children'], reverse=True)

    # Write output
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'w', encoding='utf-8', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys(), delimiter='\t')
            writer.writeheader()
            writer.writerows(results)

    click.echo(f"\n✓ Analysis complete!")
    click.echo(f"  Output: {output}")
    click.echo(f"  Parents analyzed: {len(results)}")

    # Show summary statistics
    if results:
        high_coverage = [r for r in results if r['coverage_percent'] >= 80]
        medium_coverage = [r for r in results if 50 <= r['coverage_percent'] < 80]
        low_coverage = [r for r in results if r['coverage_percent'] < 50]

        click.echo(f"\nCoverage Summary:")
        click.echo(f"  High coverage (≥80%): {len(high_coverage)} parents")
        click.echo(f"  Medium coverage (50-79%): {len(medium_coverage)} parents")
        click.echo(f"  Low coverage (<50%): {len(low_coverage)} parents")

        # Show top candidates for pattern-based definition
        click.echo(f"\n🎯 Top candidates for pattern-based definition (high coverage, few stragglers):")
        candidates = [r for r in results if r['coverage_percent'] >= 70 and 1 <= r['straggler_count'] <= 5]
        for i, r in enumerate(candidates[:10], 1):
            click.echo(f"  {i}. {r['parent_label']} ({r['coverage_percent']}% coverage, {r['straggler_count']} stragglers)")


if __name__ == '__main__':
    main()
