"""
Download ontology from BioPortal with robust error handling.

Usage:
    download-ontology D3O --output external/ontologies/bioportal/D3O.owl

Exit codes:
    0: Success (file downloaded and valid)
    1: Failure (any error)
"""

import os
import sys
from datetime import UTC, datetime
from pathlib import Path

import click
import requests

LOG_PATH = Path(".ontology_fetch.log")
MIN_FILE_SIZE = 1000  # Bytes - anything smaller is likely an error response


def log_failure(ontology_id: str, file_size: int, message: str):
    """Log fetch failure."""
    timestamp = datetime.now(UTC).isoformat()
    with Path(LOG_PATH).open("a") as f:
        f.write(f"{timestamp} | FETCH_FAILED | {ontology_id} | {file_size} bytes | {message}\n")


@click.command()
@click.argument("ontology_id")
@click.option("--output", type=Path, required=True, help="Output file path")
def main(ontology_id: str, output: Path):
    """Download ontology from BioPortal."""
    api_key = os.getenv("BIOPORTAL_API_KEY")

    if not api_key:
        click.echo("✗ BIOPORTAL_API_KEY environment variable not set", err=True)
        sys.exit(1)

    # Ensure output directory exists
    output.parent.mkdir(parents=True, exist_ok=True)

    # Download
    url = f"https://data.bioontology.org/ontologies/{ontology_id}/download"
    click.echo(f"Downloading BioPortal ontology {ontology_id}...")

    try:
        response = requests.get(url, params={"apikey": api_key}, timeout=300)
        response.raise_for_status()

        # Write to file
        output.write_bytes(response.content)
        file_size = output.stat().st_size

        # Check if successful
        if file_size < MIN_FILE_SIZE:
            click.echo(
                f"✗ Failed to download {ontology_id} (empty or error response: {file_size} bytes)",
                err=True,
            )
            log_failure(ontology_id, file_size, "File too small")
            output.unlink(missing_ok=True)
            sys.exit(1)

        # Success
        click.echo(f"✓ Successfully downloaded {ontology_id} ({file_size:,} bytes)")
        sys.exit(0)

    except requests.exceptions.RequestException as e:
        click.echo(f"✗ Failed to download {ontology_id}: {e}", err=True)
        log_failure(ontology_id, 0, str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
