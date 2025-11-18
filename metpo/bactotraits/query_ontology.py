#!/usr/bin/env python
"""
Query ontology with ROBOT.

Usage:
    query-ontology D3O --input external/ontologies/bioportal/D3O.owl --query sparql/extract_for_embeddings.rq --output data/pipeline/non-ols-terms/D3O.tsv

Exit codes:
    0: Success (terms extracted)
    1: Failure (any error or empty result)

Outputs term count to stdout on success for Make to capture.
"""

import sys
import csv
import subprocess
from datetime import datetime
from pathlib import Path
import click


LOG_PATH = Path(".robot_query.log")


def log_event(ontology_id: str, input_file: str, message: str, log_type: str = "QUERY_FAILED"):
    """Log query event."""
    timestamp = datetime.now().isoformat()
    with open(LOG_PATH, "a") as f:
        f.write(f"{timestamp} | {log_type} | {ontology_id} | {input_file} | {message}\n")


def count_tsv_terms(tsv_path: Path) -> int:
    """Count rows in TSV (excluding header)."""
    try:
        with open(tsv_path) as f:
            return sum(1 for _ in csv.reader(f, delimiter="\t")) - 1
    except Exception:
        return 0


@click.command()
@click.argument("ontology_id")
@click.option("--input", "input_file", type=Path, required=True, help="Input OWL/TTL file")
@click.option("--query", "query_file", type=Path, required=True, help="SPARQL query file")
@click.option("--output", "output_file", type=Path, required=True, help="Output TSV file")
def main(ontology_id: str, input_file: Path, query_file: Path, output_file: Path):
    """Query ontology with ROBOT."""

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Check input exists
    if not input_file.exists():
        click.echo(f"✗ Input file not found: {input_file}", err=True)
        log_event(ontology_id, str(input_file), "Input file not found")
        sys.exit(1)

    # Run ROBOT query
    click.echo(f"Querying {ontology_id} with ROBOT...")

    cmd = [
        "robot", "query",
        "--input", str(input_file),
        "--query", str(query_file),
        str(output_file)
    ]

    try:
        # Run ROBOT
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        # Log ROBOT stderr if present
        if result.stderr:
            log_event(ontology_id, str(input_file), result.stderr, "ROBOT_OUTPUT")

        # Check if output was created
        if not output_file.exists():
            click.echo(f"✗ ROBOT query failed for {ontology_id} (no output file created)", err=True)
            log_event(ontology_id, str(input_file), "No output file created")
            sys.exit(1)

        # Check if output has content
        term_count = count_tsv_terms(output_file)

        if term_count == 0:
            click.echo(f"✗ ROBOT query produced empty output for {ontology_id}", err=True)
            log_event(ontology_id, str(input_file), "Empty output", "QUERY_EMPTY")
            sys.exit(1)

        # Success - output term count for Make to capture
        click.echo(f"✓ Extracted {term_count} terms from {ontology_id}")
        click.echo(f"TERM_COUNT={term_count}")  # Make can parse this
        sys.exit(0)

    except subprocess.TimeoutExpired:
        click.echo(f"✗ ROBOT query timed out for {ontology_id}", err=True)
        log_event(ontology_id, str(input_file), "Query timeout")
        sys.exit(1)

    except Exception as e:
        click.echo(f"✗ ROBOT query failed for {ontology_id}: {e}", err=True)
        log_event(ontology_id, str(input_file), str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
