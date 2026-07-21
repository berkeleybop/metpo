"""Assess which external ontologies best align with METPO labels via search APIs.

For each METPO label in the input TSV, this queries the OLS4 and BioPortal
search APIs, records every returned class, scores each match against the METPO
label with Levenshtein similarity, and ranks the external ontologies by how many
high-quality matches they produce. It is a discovery pass: no filtering beyond
dropping METPO's own self-matches.

This CLI replaces the retired ``notebooks/assess_ontology_by_api_search.ipynb``.

Outputs (written into ``--output-dir``):

- ``phase1_raw_results.tsv``: every match with its similarity score
- ``phase1_high_quality_matches.tsv``: matches at or above ``--hq-threshold``
- ``phase1_ontology_rankings.tsv``: ontologies ranked by high-quality match count
- ``phase1_summary_stats.json``: run-level summary statistics

BioPortal queries need a ``BIOPORTAL_API_KEY`` (read from the environment or a
local ``.env``). Without it, use ``--skip-bioportal`` to query OLS only.
"""

import json
import os
import time
from pathlib import Path

import click
import Levenshtein
import pandas as pd
import requests
from dotenv import load_dotenv

OLS_SEARCH_URL = "https://www.ebi.ac.uk/ols4/api/search"
BIOPORTAL_SEARCH_URL = "https://data.bioontology.org/search"
REQUEST_TIMEOUT = 10


def search_ols(label: str, rows: int) -> list[dict[str, str | None]]:
    """Return OLS4 search hits for ``label`` as label/iri/ontology/definition dicts."""
    params: dict[str, str | int] = {"q": label, "type": "class", "rows": rows}
    try:
        response = requests.get(OLS_SEARCH_URL, params=params, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        click.echo(f"  OLS error for '{label}': {exc}", err=True)
        return []
    if response.status_code != 200:
        return []
    try:
        docs = response.json().get("response", {}).get("docs", [])
    except ValueError as exc:
        click.echo(f"  OLS non-JSON response for '{label}': {exc}", err=True)
        return []
    return [
        {
            "label": doc.get("label"),
            "iri": doc.get("iri"),
            "ontology": doc.get("ontology_name"),
            "definition": doc.get("description", [""])[0] if doc.get("description") else "",
        }
        for doc in docs
    ]


def search_bioportal(label: str, api_key: str | None, pagesize: int) -> list[dict[str, str | None]]:
    """Return BioPortal search hits for ``label`` as label/iri/ontology/definition dicts."""
    params: dict[str, str | int] = {"q": label, "pagesize": pagesize}
    headers = {"Authorization": f"apikey token={api_key}"} if api_key else {}
    try:
        response = requests.get(
            BIOPORTAL_SEARCH_URL, params=params, headers=headers, timeout=REQUEST_TIMEOUT
        )
    except requests.RequestException as exc:
        click.echo(f"  BioPortal error for '{label}': {exc}", err=True)
        return []
    if response.status_code != 200:
        return []
    try:
        collection = response.json().get("collection", [])
    except ValueError as exc:
        click.echo(f"  BioPortal non-JSON response for '{label}': {exc}", err=True)
        return []
    results: list[dict[str, str | None]] = []
    for item in collection:
        ontology_url = item.get("links", {}).get("ontology", "")
        definition = item.get("definition", "")
        if isinstance(definition, list):
            definition = definition[0] if definition else ""
        results.append(
            {
                "label": item.get("prefLabel"),
                "iri": item.get("@id"),
                "ontology": ontology_url.split("/")[-1] if ontology_url else "unknown",
                "definition": definition,
            }
        )
    return results


def calculate_similarity(metpo_label: str, match_label: object) -> tuple[int | None, float | None]:
    """Return (Levenshtein distance, ratio) between two labels, or (None, None) if unlabeled."""
    if match_label is None or pd.isna(match_label):
        return None, None
    left = str(metpo_label).lower()
    right = str(match_label).lower()
    return Levenshtein.distance(left, right), Levenshtein.ratio(left, right)


def _resolve_api_key() -> str | None:
    """Load a BioPortal API key from the environment or a local .env, if present."""
    load_dotenv()
    return os.getenv("BIOPORTAL_API_KEY")


@click.command()
@click.option(
    "--input",
    "-i",
    "input_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default="data/metpo_terms/metpo_all_labels.tsv",
    show_default=True,
    help="TSV of METPO labels (two columns: metpo_id, metpo_label; no header).",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False, path_type=Path),
    default="data/ontology_assessments",
    show_default=True,
    help="Directory for the phase1 output files (created if missing).",
)
@click.option(
    "--rows",
    type=int,
    default=75,
    show_default=True,
    help="Results requested per query from each of OLS and BioPortal.",
)
@click.option(
    "--rate-limit",
    type=float,
    default=1.0,
    show_default=True,
    help="Seconds to sleep between API calls.",
)
@click.option(
    "--hq-threshold",
    type=float,
    default=0.5,
    show_default=True,
    help="Minimum Levenshtein similarity ratio for a high-quality match.",
)
@click.option(
    "--skip-bioportal",
    is_flag=True,
    help="Query only OLS4 (no BioPortal API key required).",
)
def main(
    input_file: Path,
    output_dir: Path,
    rows: int,
    rate_limit: float,
    hq_threshold: float,
    skip_bioportal: bool,
) -> None:
    """Query OLS4/BioPortal for each METPO label and rank aligning ontologies."""
    api_key = None if skip_bioportal else _resolve_api_key()
    if not skip_bioportal and not api_key:
        click.echo(
            "BIOPORTAL_API_KEY not set; BioPortal queries will return nothing. "
            "Pass --skip-bioportal to query OLS only.",
            err=True,
        )

    metpo_df = pd.read_csv(input_file, sep="\t", names=["metpo_id", "metpo_label"])
    click.echo(f"Loaded {len(metpo_df)} METPO labels from {input_file}")

    all_results: list[dict[str, object]] = []
    for position, (_, row) in enumerate(metpo_df.iterrows(), start=1):
        metpo_id = row["metpo_id"]
        metpo_label = row["metpo_label"]
        click.echo(f"[{position}/{len(metpo_df)}] {metpo_label}")

        hits = [("OLS", hit) for hit in search_ols(metpo_label, rows)]
        time.sleep(rate_limit)
        if not skip_bioportal:
            hits += [("BioPortal", hit) for hit in search_bioportal(metpo_label, api_key, rows)]
            time.sleep(rate_limit)

        for source, hit in hits:
            all_results.append(
                {
                    "metpo_id": metpo_id,
                    "metpo_label": metpo_label,
                    "source": source,
                    "match_label": hit["label"],
                    "match_iri": hit["iri"],
                    "match_ontology": hit["ontology"],
                    "match_definition": hit["definition"],
                }
            )

    if not all_results:
        raise click.ClickException("No search results returned; nothing to write.")

    results_df = pd.DataFrame(all_results)

    # Drop METPO's own classes so we measure alignment with external ontologies only.
    before = len(results_df)
    results_df = results_df[
        ~results_df["match_iri"].str.contains("metpo", case=False, na=False)
    ].reset_index(drop=True)
    click.echo(f"Removed {before - len(results_df)} METPO self-matches ({len(results_df)} remain)")

    scores = results_df.apply(
        lambda r: calculate_similarity(r["metpo_label"], r["match_label"]), axis=1
    )
    results_df["levenshtein_distance"] = [score[0] for score in scores]
    results_df["similarity_ratio"] = [score[1] for score in scores]

    output_dir.mkdir(parents=True, exist_ok=True)
    raw_output = output_dir / "phase1_raw_results.tsv"
    results_df.to_csv(raw_output, sep="\t", index=False)

    high_quality = results_df[results_df["similarity_ratio"] >= hq_threshold]
    hq_output = output_dir / "phase1_high_quality_matches.tsv"
    high_quality.to_csv(hq_output, sep="\t", index=False)

    hq_counts = high_quality["match_ontology"].value_counts()
    avg_similarity = results_df.groupby("match_ontology")["similarity_ratio"].mean()
    total_matches = results_df["match_ontology"].value_counts()
    rankings = pd.DataFrame(
        {"ontology": hq_counts.index, "high_quality_matches": hq_counts.to_numpy()}
    )
    rankings["avg_similarity"] = rankings["ontology"].map(avg_similarity)
    rankings["total_matches"] = rankings["ontology"].map(total_matches)
    rankings = rankings.sort_values("high_quality_matches", ascending=False)
    rankings_output = output_dir / "phase1_ontology_rankings.tsv"
    rankings.to_csv(rankings_output, sep="\t", index=False)

    summary = {
        "input_file": str(input_file),
        "total_metpo_terms": len(metpo_df),
        "total_results": len(results_df),
        "high_quality_results": len(high_quality),
        "high_quality_threshold": hq_threshold,
        "unique_ontologies": int(results_df["match_ontology"].nunique()),
        "avg_similarity": float(results_df["similarity_ratio"].mean()),
        "median_similarity": float(results_df["similarity_ratio"].median()),
        "top_10_ontologies": rankings.head(10).to_dict("records"),
    }
    summary_output = output_dir / "phase1_summary_stats.json"
    with summary_output.open("w") as handle:
        json.dump(summary, handle, indent=2)

    click.echo(
        f"\nWrote {raw_output}, {hq_output}, {rankings_output}, {summary_output}\n"
        f"High-quality matches (>= {hq_threshold}): {len(high_quality)}/{len(results_df)}; "
        f"{results_df['match_ontology'].nunique()} unique ontologies"
    )


if __name__ == "__main__":
    main()
