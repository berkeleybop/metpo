"""Analyze match quality by distance for each ontology.

This tool analyzes SSSOM mapping files to assess the quality of matches
for non-OLS ontologies based on distance metrics.
"""

import click
import pandas as pd

from metpo.cli_common import distance_threshold_option


@click.command()
@click.argument("sssom_file", type=click.Path(exists=True, dir_okay=False, path_type=str))
@distance_threshold_option(default=0.35, help_text="Distance threshold for high-quality matches")
def main(sssom_file, distance_threshold):
    """Analyze match quality by distance for each non-OLS ontology.

    Reads an SSSOM file and generates a quality assessment report
    showing match statistics and recommendations for each ontology.

    Example:
        uv run analyze-match-quality mappings.sssom.tsv
    """
    df = pd.read_csv(sssom_file, sep="\t", comment="#")

    # Extract distance from comment field
    df["distance"] = df["comment"].str.extract(r"distance: ([\d.]+)").astype(float)

    # Focus on non-OLS ontologies
    non_ols = [
        "d3o",
        "meo",
        "miso",
        "gmo",
        "id-amr",
        "n4l_merged",
        "omp",
        "bipon",
        "mccv",
        "typon",
        "fmpm",
        "ofsmr",
        "mpo",
    ]

    click.echo(
        f"{'Ontology':<15} {'Matches':<10} {'Best':<10} {'Median':<10} {'Worst':<10} {'Avg':<10} {'<{distance_threshold}':<8} {'Assessment'}"
    )
    click.echo("-" * 110)

    for ont in sorted(non_ols):
        ont_df = df[df["object_source"] == ont]

        if len(ont_df) == 0:
            click.echo(
                f"{ont:<15} {'0':<10} {'-':<10} {'-':<10} {'-':<10} {'-':<10} {'0':<8} REMOVE - no matches"
            )
            continue

        distances = ont_df["distance"].sort_values()
        best = distances.iloc[0]
        median = distances.median()
        worst = distances.iloc[-1]
        avg = distances.mean()
        high_quality = len(ont_df[ont_df["distance"] < distance_threshold])

        # Assessment
        if avg < 0.35:
            assessment = "EXCELLENT - keep"
        elif avg < 0.50 and high_quality >= 3:
            assessment = "GOOD - keep"
        elif avg < 0.60 and high_quality >= 1:
            assessment = "FAIR - review"
        else:
            assessment = "POOR - likely remove"

        click.echo(
            f"{ont:<15} {len(ont_df):<10} {best:<10.4f} {median:<10.4f} {worst:<10.4f} {avg:<10.4f} {high_quality:<8} {assessment}"
        )


if __name__ == "__main__":
    main()
