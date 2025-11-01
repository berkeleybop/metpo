#!/usr/bin/env python
"""
Update .ontology_manifest.json with fetch/query status.

Usage:
    update-manifest --ontology D3O --status success --file non-ols/D3O.owl
    update-manifest --ontology D3O --robot-status failed --tsv notebooks/non-ols-terms/D3O.tsv
"""

import json
import os
from datetime import datetime
from pathlib import Path
import click


MANIFEST_PATH = Path(".ontology_manifest.json")


def load_manifest():
    """Load manifest or create if doesn't exist."""
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH) as f:
            return json.load(f)
    return {
        "_comment": "Tracking successful ontology fetches to avoid re-downloading",
        "ontologies": {}
    }


def save_manifest(manifest):
    """Save manifest with pretty formatting."""
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)


@click.command()
@click.option('--ontology', required=True, help='Ontology ID (e.g., D3O, OMP)')
@click.option('--status', type=click.Choice(['success', 'failed', 'empty']),
              help='Fetch status')
@click.option('--robot-status', type=click.Choice(['success', 'failed', 'empty', 'not_run']),
              help='ROBOT query status')
@click.option('--file', 'file_path', type=Path, help='Path to OWL/TTL file')
@click.option('--tsv', 'tsv_path', type=Path, help='Path to TSV output')
@click.option('--source', type=click.Choice(['bioportal', 'manual']), default='bioportal',
              help='Source of ontology')
@click.option('--term-count', type=int, help='Number of terms extracted')
def main(ontology: str, status: str, robot_status: str, file_path: Path,
         tsv_path: Path, source: str, term_count: int):
    """Update ontology manifest with fetch/query status."""
    manifest = load_manifest()

    # Get or create ontology entry
    ont_id = ontology.upper()
    if ont_id not in manifest['ontologies']:
        manifest['ontologies'][ont_id] = {}

    entry = manifest['ontologies'][ont_id]

    # Update fetch status
    if status:
        entry['status'] = status
        entry['fetched_at'] = datetime.now().isoformat()
        entry['source'] = source

    # Update file info
    if file_path and file_path.exists():
        entry['file_path'] = str(file_path)
        entry['file_size_bytes'] = file_path.stat().st_size
        if entry['file_size_bytes'] < 1000:  # < 1KB likely error
            entry['status'] = 'empty'

    # Update ROBOT query status
    if robot_status:
        entry['robot_query_status'] = robot_status

    # Update TSV info
    if tsv_path:
        entry['tsv_path'] = str(tsv_path)
        if tsv_path.exists():
            entry['tsv_size_bytes'] = tsv_path.stat().st_size
            if entry['tsv_size_bytes'] == 0:
                entry['robot_query_status'] = 'empty'
        else:
            entry['robot_query_status'] = 'failed'

    # Update term count
    if term_count is not None:
        entry['term_count'] = term_count

    save_manifest(manifest)
    click.echo(f"✓ Updated manifest for {ont_id}")


if __name__ == '__main__':
    main()
