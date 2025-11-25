"""Verify that madin tax_ids are valid NCBI Taxonomy IDs by checking a sample."""

import csv
import time
from pathlib import Path
from typing import Any

import click
import requests
from pymongo import MongoClient
from pymongo.collection import Collection
from rich.console import Console
from rich.table import Table

console = Console()


def check_ncbi_taxid(tax_id: int) -> tuple[bool, str]:
    """Check if a tax_id exists in NCBI Taxonomy."""
    try:
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {"db": "taxonomy", "id": tax_id, "retmode": "xml"}
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200 and "<ScientificName>" in response.text:
            start = response.text.find("<ScientificName>") + len("<ScientificName>")
            end = response.text.find("</ScientificName>", start)
            return True, response.text[start:end]
        return False, "NOT FOUND"
    except Exception as e:
        return False, f"ERROR: {e}"


def compare_names(org_name: str, ncbi_name: str) -> tuple[str, float]:
    """Compare organism names and return match symbol and score."""
    madin_norm = org_name.lower().strip()
    ncbi_norm = ncbi_name.lower().strip()

    if madin_norm == ncbi_norm:
        return "✓", 1.0
    if madin_norm in ncbi_norm or ncbi_norm in madin_norm:
        return "~", 0.5
    return "✗", 0.0


def get_random_samples(coll: Collection, sample_size: int) -> list[dict]:
    """Get random sample of documents with tax_ids."""
    pipeline = [
        {"$match": {"tax_id": {"$exists": True, "$ne": None}}},
        {"$sample": {"size": sample_size}},
    ]
    return list(coll.aggregate(pipeline))


def build_validation_table() -> Table:
    """Create the validation results table."""
    table = Table(title="NCBI Taxonomy Validation")
    table.add_column("Madin tax_id", style="cyan")
    table.add_column("Madin org_name", style="green", no_wrap=False)
    table.add_column("NCBI Valid?", style="yellow")
    table.add_column("NCBI ScientificName", style="magenta", no_wrap=False)
    table.add_column("Match?", style="white")
    return table


def validate_samples(samples: list[dict]) -> tuple[Table, int, float, list[dict[str, Any]]]:
    """Validate samples against NCBI and build results."""
    table = build_validation_table()
    valid_count = 0
    name_match_score = 0.0
    results = []

    for i, doc in enumerate(samples):
        tax_id = doc.get("tax_id")
        org_name = doc.get("org_name", "")

        is_valid, ncbi_name = check_ncbi_taxid(tax_id)
        if is_valid:
            valid_count += 1

        names_match = "?"
        match_type = "unknown"
        if is_valid and ncbi_name != "NOT FOUND":
            names_match, score = compare_names(org_name, ncbi_name)
            name_match_score += score
            match_type = (
                "exact" if names_match == "✓" else ("partial" if names_match == "~" else "no")
            )

        table.add_row(
            str(tax_id),
            org_name[:40],
            "✓" if is_valid else "✗",
            ncbi_name[:40] if ncbi_name else "N/A",
            names_match,
        )

        results.append(
            {
                "tax_id": tax_id,
                "org_name": org_name,
                "is_valid": is_valid,
                "ncbi_name": ncbi_name,
                "match_type": match_type,
            }
        )

        if i < len(samples) - 1:
            time.sleep(0.4)

    return table, valid_count, name_match_score, results


def print_summary(samples: list, valid_count: int, name_match_score: float) -> None:
    """Print validation summary."""
    console.print("\n[bold]Summary:[/bold]")
    console.print(f"  Samples checked: {len(samples)}")
    console.print(
        f"  Valid NCBI tax_ids: {valid_count}/{len(samples)} ({valid_count / len(samples) * 100:.1f}%)"
    )
    console.print(
        f"  Name matches: {name_match_score}/{len(samples)} ({name_match_score / len(samples) * 100:.1f}%)"
    )

    if valid_count == len(samples):
        console.print("\n[green]✓ All sampled tax_ids are valid NCBI Taxonomy IDs![/green]")
    else:
        console.print(f"\n[red]✗ {len(samples) - valid_count} tax_ids not found in NCBI[/red]")


def save_results_tsv(results: list[dict[str, Any]], output_path: Path) -> None:
    """Save validation results to TSV file."""
    with output_path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(
            ["madin_tax_id", "madin_org_name", "ncbi_valid", "ncbi_scientific_name", "names_match"]
        )
        for r in results:
            writer.writerow(
                [
                    r["tax_id"],
                    r["org_name"],
                    "yes" if r["is_valid"] else "no",
                    r["ncbi_name"],
                    r["match_type"],
                ]
            )
    console.print(f"\n[green]Results saved to {output_path}[/green]")


@click.command()
@click.option("--mongo-uri", default="mongodb://localhost:27017", help="MongoDB connection URI")
@click.option("--database", default="madin", help="Database name")
@click.option("--collection", default="madin", help="Collection name")
@click.option("--sample-size", default=20, help="Number of random tax_ids to verify")
@click.option("--output-tsv", type=click.Path(), help="Optional: Save results to TSV file")
def cli(
    mongo_uri: str, database: str, collection: str, sample_size: int, output_tsv: str | None
) -> None:
    """Verify random sample of tax_ids against NCBI Taxonomy API."""
    client = MongoClient(mongo_uri)
    db = client[database]
    coll = db[collection]

    console.print(
        f"[bold]Verifying {sample_size} random tax_ids against NCBI Taxonomy API[/bold]\n"
    )
    console.print("[yellow]Note: This will make API calls to NCBI (rate-limited)[/yellow]\n")

    samples = get_random_samples(coll, sample_size)
    table, valid_count, name_match_score, results = validate_samples(samples)

    console.print(table)
    print_summary(samples, valid_count, name_match_score)

    if output_tsv:
        save_results_tsv(results, Path(output_tsv))

    client.close()


if __name__ == "__main__":
    cli()
