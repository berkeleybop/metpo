#!/usr/bin/env python
"""
Scan external/ontologies/ directories and update manifest with current state.

Usage:
    scan-manifest
"""

import json
import csv
from datetime import datetime
from pathlib import Path
import click


MANIFEST_PATH = Path(".ontology_manifest.json")
NON_OLS_DIR = Path("non-ols")
TSV_DIR = Path("notebooks/non-ols-terms")


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


def count_tsv_terms(tsv_path: Path) -> int:
    """Count rows in TSV (excluding header)."""
    try:
        with open(tsv_path) as f:
            return sum(1 for _ in csv.reader(f, delimiter='\t')) - 1
    except Exception:
        return 0


@click.command()
@click.option('--verbose', is_flag=True, help='Show detailed output')
def main(verbose: bool):
    """Scan directories and update manifest with current state."""
    manifest = load_manifest()

    click.echo("Scanning external/ontologies/ directories...")

    # Scan OWL and TTL files
    files_found = 0
    for ext in ['*.owl', '*.ttl']:
        for file_path in NON_OLS_DIR.glob(ext):
            files_found += 1
            # Extract ontology ID from filename
            ont_id = file_path.stem.upper()

            # Handle versioned files (e.g., meo.v.1.0.ttl -> MEO)
            if '.' in ont_id and ont_id.split('.')[0]:
                ont_id = ont_id.split('.')[0]

            # Skip some obvious non-ontology files
            if ont_id in ['PATO', 'N4L_MERGED']:
                # These might be manually added, keep them
                pass

            if ont_id not in manifest['ontologies']:
                manifest['ontologies'][ont_id] = {}

            entry = manifest['ontologies'][ont_id]

            # Update file info
            file_size = file_path.stat().st_size
            entry['file_path'] = str(file_path)
            entry['file_size_bytes'] = file_size
            entry['source'] = 'manual' if ont_id in ['PATO', 'N4L_MERGED'] else 'bioportal'

            # Determine status based on file size
            if file_size < 1000:
                entry['status'] = 'empty'
            else:
                entry['status'] = 'success'

            # Check for corresponding TSV
            tsv_path = TSV_DIR / f"{ont_id}.tsv"
            if tsv_path.exists():
                entry['tsv_path'] = str(tsv_path)
                entry['tsv_size_bytes'] = tsv_path.stat().st_size
                term_count = count_tsv_terms(tsv_path)
                entry['term_count'] = term_count

                if term_count == 0:
                    entry['robot_query_status'] = 'empty'
                else:
                    entry['robot_query_status'] = 'success'
            else:
                entry['robot_query_status'] = 'not_run'

            # Update timestamp only if not already set
            if 'fetched_at' not in entry:
                entry['fetched_at'] = datetime.fromtimestamp(
                    file_path.stat().st_mtime
                ).isoformat()

            if verbose:
                click.echo(f"  {ont_id}: {entry['status']} "
                          f"({file_size:,} bytes, "
                          f"robot: {entry.get('robot_query_status', 'unknown')})")

    save_manifest(manifest)

    click.echo(f"\n✓ Scanned {files_found} files")
    click.echo(f"✓ Manifest updated: {MANIFEST_PATH}")

    # Summary
    statuses = {}
    robot_statuses = {}
    for ont_data in manifest['ontologies'].values():
        status = ont_data.get('status', 'unknown')
        statuses[status] = statuses.get(status, 0) + 1

        robot_status = ont_data.get('robot_query_status', 'not_run')
        robot_statuses[robot_status] = robot_statuses.get(robot_status, 0) + 1

    click.echo("\nFetch Status Summary:")
    for status, count in sorted(statuses.items()):
        click.echo(f"  {status}: {count}")

    click.echo("\nROBOT Query Status Summary:")
    for status, count in sorted(robot_statuses.items()):
        click.echo(f"  {status}: {count}")


if __name__ == '__main__':
    main()
