"""
Merge SPARQL query results with fetched API metadata.
"""

import csv
from pathlib import Path

import click


@click.command()
@click.option(
    "--sparql-results",
    "-s",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="SPARQL query results TSV",
)
@click.option(
    "--source-metadata",
    "-m",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Source metadata TSV from fetch-source-metadata",
)
@click.option(
    "--output-file",
    "-o",
    type=click.Path(path_type=Path),
    required=True,
    help="Output integrated TSV file",
)
def main(sparql_results: Path, source_metadata_file: Path, output_file: Path):
    """
    Merge SPARQL query results with fetched API metadata.

    Combines METPO definition source IRIs from SPARQL with their metadata
    (labels, definitions, synonyms) fetched from OLS/BioPortal APIs.
    """
    # Read source metadata
    source_metadata = {}
    with source_metadata_file.open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            source_iri = row["source_iri"]
            source_metadata[source_iri] = {
                "label": row.get("label", ""),
                "definition": row.get("definition", ""),
                "synonyms": row.get("synonyms", ""),
                "api_source": row.get("api_source", ""),
            }

    click.echo(f"Loaded metadata for {len(source_metadata)} sources")

    # Create output directory
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Read SPARQL results and merge
    with sparql_results.open() as f_in:
        with output_file.open("w", newline="") as f_out:
            reader = csv.DictReader(f_in, delimiter="\t")

            fieldnames = [
                "metpo_id",
                "metpo_label",
                "metpo_definition",
                "definition_source_iri",
                "source_label",
                "source_definition",
                "source_synonyms",
                "source_api",
            ]
            writer = csv.DictWriter(f_out, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()

            rows_written = 0
            not_found_count = 0

            for row in reader:
                metpo_id = row["?metpo_id"].strip('"')
                metpo_label = row["?label"].strip('"')
                metpo_def = row.get("?definition", "").strip('"')
                source_iri = row.get("?definition_source", "").strip("<>").strip('"')

                # Look up source metadata
                if source_iri in source_metadata:
                    meta = source_metadata[source_iri]
                    writer.writerow(
                        {
                            "metpo_id": metpo_id,
                            "metpo_label": metpo_label,
                            "metpo_definition": metpo_def,
                            "definition_source_iri": source_iri,
                            "source_label": meta["label"],
                            "source_definition": meta["definition"],
                            "source_synonyms": meta["synonyms"],
                            "source_api": meta["api_source"],
                        }
                    )
                    rows_written += 1
                else:
                    # Source not found in metadata
                    writer.writerow(
                        {
                            "metpo_id": metpo_id,
                            "metpo_label": metpo_label,
                            "metpo_definition": metpo_def,
                            "definition_source_iri": source_iri,
                            "source_label": "",
                            "source_definition": "",
                            "source_synonyms": "",
                            "source_api": "NOT_FOUND",
                        }
                    )
                    rows_written += 1
                    not_found_count += 1

    click.echo(f"✓ Created integrated output: {output_file}")
    click.echo(f"  Total rows: {rows_written}")
    if not_found_count > 0:
        click.echo(f"  ⚠ Sources not found in metadata: {not_found_count}")


if __name__ == "__main__":
    main()
