"""
Merge SPARQL query results with fetched API metadata.

Takes SPARQL output with METPO terms and their definition sources,
and joins with fetched metadata from OLS/BioPortal APIs.
"""

import csv
from pathlib import Path

import click


@click.command()
@click.option(
    "--sparql-output",
    "-s",
    required=True,
    type=click.Path(exists=True),
    help="SPARQL output TSV with METPO terms and definition sources",
)
@click.option(
    "--metadata",
    "-m",
    required=True,
    type=click.Path(exists=True),
    help="Source metadata TSV from fetch-source-metadata",
)
@click.option(
    "--output",
    "-o",
    required=True,
    type=click.Path(),
    help="Output TSV with merged data",
)
def main(sparql_output: str, metadata: str, output: str):
    """Merge SPARQL query results with fetched API metadata."""
    # Read source metadata
    source_metadata = {}
    with Path(metadata).open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            source_iri = row["source_iri"]
            source_metadata[source_iri] = {
                "label": row.get("label", ""),
                "definition": row.get("definition", ""),
                "synonyms": row.get("synonyms", ""),
                "api_source": row.get("api_source", ""),
            }

    click.echo(f"Loaded {len(source_metadata)} source metadata entries")

    # Read SPARQL results and merge
    row_count = 0
    with Path(sparql_output).open() as f_in:
        with Path(output).open("w", newline="") as f_out:
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

                row_count += 1

    click.echo(f"✓ Created merged output: {output}")
    click.echo(f"  Total rows: {row_count}")


if __name__ == "__main__":
    main()
