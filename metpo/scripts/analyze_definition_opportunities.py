#!/usr/bin/env python3
"""
Analyze METPO terms to identify opportunities for adding or improving definitions
based on high-confidence SSSOM mapping matches.

This script:
1. Reads METPO terms from the template TSV
2. Reads SSSOM mappings to find high-confidence matches
3. Identifies terms with missing or minimal definitions
4. Extracts definitions from matched terms where available
5. Generates recommendations for definition improvements
"""
import csv
import click
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


def read_metpo_terms(template_path: Path) -> Dict[str, Dict]:
    """Read METPO terms from the ROBOT template TSV."""
    terms = {}

    with open(template_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            term_id = row.get('ID', '').strip()
            # Skip header rows and empty rows
            if not term_id or term_id == 'ID' or not term_id.startswith('METPO:'):
                continue

            terms[term_id] = {
                'id': term_id,
                'label': row.get('label', '').strip(),
                'definition': row.get('description', '').strip(),
                'parent_classes': row.get('parent classes (one strongly preferred)', '').strip(),
                'comment': row.get('comment', '').strip(),
            }

    return terms


def read_sssom_mappings(sssom_path: Path) -> Dict[str, List[Dict]]:
    """Read SSSOM mappings and organize by METPO term."""
    mappings = defaultdict(list)

    with open(sssom_path, 'r', encoding='utf-8') as f:
        # Skip comment lines
        lines = [line for line in f if not line.startswith('#')]

        reader = csv.DictReader(lines, delimiter='\t')
        for row in reader:
            subject_id = row.get('subject_id', '').strip()
            if not subject_id.startswith('METPO:'):
                continue

            mapping_info = {
                'subject_id': subject_id,
                'subject_label': row.get('subject_label', '').strip(),
                'predicate_id': row.get('predicate_id', '').strip(),
                'object_id': row.get('object_id', '').strip(),
                'object_label': row.get('object_label', '').strip(),
                'confidence': float(row.get('confidence', 0)),
                'similarity_score': float(row.get('similarity_score', 0)),
                'mapping_justification': row.get('mapping_justification', '').strip(),
                'object_source': row.get('object_source', '').strip(),
                'comment': row.get('comment', '').strip(),
            }

            mappings[subject_id].append(mapping_info)

    return mappings


def extract_definition_from_object_label(object_label: str) -> Tuple[str, str]:
    """
    Extract definition from object_label if it contains one.
    Format is often: 'label; definition'
    Returns (label, definition) tuple.
    """
    if ';' in object_label:
        parts = object_label.split(';', 1)
        return parts[0].strip(), parts[1].strip()
    return object_label.strip(), ''


def assess_definition_quality(definition: str) -> str:
    """Assess the quality/completeness of a definition."""
    if not definition:
        return 'missing'
    elif len(definition) < 30:
        return 'minimal'
    elif len(definition) < 100:
        return 'adequate'
    else:
        return 'comprehensive'


def check_genus_compatibility(parent_class: str, candidate_definition: str) -> bool:
    """
    Check if candidate definition is compatible with parent class (genus).
    Uses simple heuristic: definition should mention parent or related term.
    """
    if not parent_class or not candidate_definition:
        return False

    # Normalize for comparison
    parent_lower = parent_class.lower()
    definition_lower = candidate_definition.lower()

    # Check if parent class or its components appear in definition
    # Handle cases like "temperature phenotype" parent and "temperature" in definition
    parent_terms = parent_lower.split('|')[0].strip().split()  # Take first parent if multiple

    for term in parent_terms:
        if term in definition_lower:
            return True

    return False


def find_best_definition_candidates(mappings: List[Dict]) -> List[Dict]:
    """
    Find the best candidate definitions from mappings.
    Prioritize exactMatch and closeMatch with high confidence.
    """
    candidates = []

    for mapping in mappings:
        # Extract potential definition from object_label
        label, definition = extract_definition_from_object_label(mapping['object_label'])

        if not definition:
            continue

        # Prioritize by predicate type
        predicate = mapping['predicate_id']
        priority = 0
        if 'exactMatch' in predicate:
            priority = 3
        elif 'closeMatch' in predicate:
            priority = 2
        elif 'relatedMatch' in predicate:
            priority = 1

        candidates.append({
            'definition': definition,
            'source_label': label,
            'source_id': mapping['object_id'],
            'source': mapping['object_source'],
            'confidence': mapping['confidence'],
            'predicate': predicate,
            'priority': priority,
        })

    # Sort by priority (match type) then confidence
    candidates.sort(key=lambda x: (x['priority'], x['confidence']), reverse=True)

    return candidates


@click.command()
@click.option(
    '--template',
    '-t',
    type=click.Path(exists=True, path_type=Path),
    default='src/templates/metpo_sheet.tsv',
    help='Path to METPO ROBOT template TSV'
)
@click.option(
    '--mappings',
    '-m',
    type=click.Path(exists=True, path_type=Path),
    default='data/mappings/metpo_mappings_optimized.sssom.tsv',
    help='Path to SSSOM mappings file'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(path_type=Path),
    default='reports/definition_improvement_opportunities.tsv',
    help='Output TSV file for recommendations'
)
@click.option(
    '--min-confidence',
    type=float,
    default=0.7,
    help='Minimum confidence threshold for considering mappings'
)
@click.option(
    '--match-types',
    default='exactMatch,closeMatch',
    help='Comma-separated list of match types to consider'
)
@click.option(
    '--include-existing/--missing-only',
    default=False,
    help='Include terms with existing definitions (show all improvement opportunities)'
)
def main(
    template: Path,
    mappings: Path,
    output: Path,
    min_confidence: float,
    match_types: str,
    include_existing: bool
):
    """
    Analyze METPO terms to identify opportunities for adding or improving
    definitions based on high-confidence SSSOM mapping matches.
    """
    click.echo(f"Reading METPO terms from {template}...")
    terms = read_metpo_terms(template)
    click.echo(f"Found {len(terms)} METPO terms")

    click.echo(f"\nReading SSSOM mappings from {mappings}...")
    sssom_mappings = read_sssom_mappings(mappings)
    click.echo(f"Found mappings for {len(sssom_mappings)} terms")

    # Parse match types
    allowed_match_types = [mt.strip() for mt in match_types.split(',')]

    # Analyze each term
    recommendations = []

    for term_id, term_info in sorted(terms.items()):
        definition_quality = assess_definition_quality(term_info['definition'])

        # Only analyze terms with missing or minimal definitions (unless --include-existing)
        if not include_existing and definition_quality not in ['missing', 'minimal']:
            continue

        # Get mappings for this term
        term_mappings = sssom_mappings.get(term_id, [])

        # Filter by confidence and match type
        filtered_mappings = [
            m for m in term_mappings
            if m['confidence'] >= min_confidence
            and any(mt in m['predicate_id'] for mt in allowed_match_types)
        ]

        if not filtered_mappings:
            continue

        # Find best definition candidates
        candidates = find_best_definition_candidates(filtered_mappings)

        if not candidates:
            continue

        # Get top 3 candidates
        for i, candidate in enumerate(candidates[:3], 1):
            # Check genus compatibility with parent class
            genus_compatible = check_genus_compatibility(
                term_info['parent_classes'],
                candidate['definition']
            )

            recommendations.append({
                'metpo_id': term_id,
                'metpo_label': term_info['label'],
                'parent_classes': term_info['parent_classes'],
                'current_definition': term_info['definition'],
                'definition_quality': definition_quality,
                'rank': i,
                'candidate_definition': candidate['definition'],
                'genus_compatible': 'yes' if genus_compatible else 'no',
                'source_id': candidate['source_id'],
                'source_label': candidate['source_label'],
                'source_ontology': candidate['source'],
                'match_type': candidate['predicate'].split('#')[-1],
                'confidence': f"{candidate['confidence']:.4f}",
            })

    # Write output
    output.parent.mkdir(parents=True, exist_ok=True)

    if recommendations:
        fieldnames = [
            'metpo_id',
            'metpo_label',
            'parent_classes',
            'current_definition',
            'definition_quality',
            'rank',
            'candidate_definition',
            'genus_compatible',
            'source_id',
            'source_label',
            'source_ontology',
            'match_type',
            'confidence',
        ]

        with open(output, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            writer.writerows(recommendations)

        click.echo(f"\n✓ Generated {len(recommendations)} recommendations")
        click.echo(f"✓ Output written to {output}")

        # Summary statistics
        terms_with_recommendations = len(set(r['metpo_id'] for r in recommendations))
        missing_count = sum(1 for r in recommendations if r['definition_quality'] == 'missing' and r['rank'] == 1)
        minimal_count = sum(1 for r in recommendations if r['definition_quality'] == 'minimal' and r['rank'] == 1)

        click.echo(f"\nSummary:")
        click.echo(f"  Terms needing improvement: {terms_with_recommendations}")
        click.echo(f"  - Missing definitions: {missing_count}")
        click.echo(f"  - Minimal definitions: {minimal_count}")

        # Show a few examples
        click.echo(f"\nExample recommendations:")
        for rec in recommendations[:5]:
            click.echo(f"\n  {rec['metpo_id']} ({rec['metpo_label']})")
            click.echo(f"    Current: {rec['current_definition'] or '[MISSING]'}")
            click.echo(f"    Candidate: {rec['candidate_definition'][:100]}...")
            click.echo(f"    Source: {rec['source_ontology']} ({rec['match_type']}, conf={rec['confidence']})")
    else:
        click.echo("\n✓ No recommendations found with current criteria")
        click.echo(f"  Try lowering --min-confidence or adding more --match-types")


if __name__ == '__main__':
    main()
