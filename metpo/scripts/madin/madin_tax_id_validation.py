"""Validate tax_id consistency with NCBI Taxonomy."""

import csv
from pathlib import Path
from typing import Any

import click
from pymongo import MongoClient
from pymongo.collection import Collection
from rich.console import Console
from rich.table import Table

console = Console()


def get_tax_id_type_counts(coll: Collection) -> list[dict]:
    """Get counts of different data types in tax_id field."""
    return list(coll.aggregate([
        {"$match": {"tax_id": {"$exists": True, "$ne": None}}},
        {"$group": {"_id": {"$type": "$tax_id"}, "count": {"$sum": 1}}},
    ]))


def get_anomaly_counts(coll: Collection) -> dict[str, int]:
    """Get counts of various tax_id anomalies."""
    return {
        "string_tax_ids": coll.count_documents({"tax_id": {"$type": "string"}}),
        "negative_tax_ids": coll.count_documents({"tax_id": {"$lt": 0}}),
        "zero_tax_ids": coll.count_documents({"tax_id": 0}),
        "large_tax_ids": coll.count_documents({"tax_id": {"$gt": 10000000}}),
    }


def print_anomaly_counts(counts: dict[str, int]) -> None:
    """Print tax_id anomaly counts."""
    console.print("\n[bold]Checking for anomalies across entire collection:[/bold]")
    console.print(f"  String tax_id values: {counts['string_tax_ids']:,}")
    console.print(f"  Negative tax_id values: {counts['negative_tax_ids']:,}")
    console.print(f"  Zero tax_id values: {counts['zero_tax_ids']:,}")
    console.print(f"  Tax_id > 10,000,000: {counts['large_tax_ids']:,}")


def compare_tax_ids(coll: Collection) -> tuple[int, int, list[dict]]:
    """Compare tax_id and species_tax_id fields."""
    both_fields = list(coll.find(
        {"tax_id": {"$exists": True, "$ne": None}, "species_tax_id": {"$exists": True, "$ne": None}},
        {"tax_id": 1, "species_tax_id": 1, "org_name": 1, "species": 1},
    ).limit(100))

    same_count = 0
    different_count = 0
    different_examples = []

    for doc in both_fields:
        if doc.get("tax_id") == doc.get("species_tax_id"):
            same_count += 1
        else:
            different_count += 1
            if len(different_examples) < 10:
                different_examples.append(doc)

    return same_count, different_count, different_examples


def display_different_examples(different_examples: list[dict]) -> None:
    """Display examples where tax_id differs from species_tax_id."""
    if not different_examples:
        return

    console.print("\n  Examples where they differ:")
    table = Table()
    table.add_column("Organism", style="cyan")
    table.add_column("Species", style="green")
    table.add_column("tax_id", style="yellow")
    table.add_column("species_tax_id", style="magenta")

    for doc in different_examples[:10]:
        table.add_row(
            str(doc.get("org_name", ""))[:40],
            str(doc.get("species", ""))[:40],
            str(doc.get("tax_id")),
            str(doc.get("species_tax_id")),
        )

    console.print(table)


def get_tax_id_range(coll: Collection) -> tuple[Any, Any]:
    """Get min and max tax_id values."""
    min_tax = list(coll.find({"tax_id": {"$type": "number"}}, {"tax_id": 1}).sort("tax_id", 1).limit(1))
    max_tax = list(coll.find({"tax_id": {"$type": "number"}}, {"tax_id": 1}).sort("tax_id", -1).limit(1))

    min_val = min_tax[0]["tax_id"] if min_tax else None
    max_val = max_tax[0]["tax_id"] if max_tax else None
    return min_val, max_val


def print_string_tax_id_samples(coll: Collection) -> None:
    """Print sample string tax_id values."""
    console.print("\n[bold]Checking for non-numeric tax_id values:[/bold]")

    string_samples = list(
        coll.find({"tax_id": {"$type": "string"}}, {"tax_id": 1, "org_name": 1}).limit(10)
    )

    if string_samples:
        console.print(f"  Found {len(string_samples)} string tax_id examples:")
        for doc in string_samples:
            console.print(f"    {doc.get('org_name')}: '{doc.get('tax_id')}'")
    else:
        console.print("  No string tax_id values found")


def save_analysis_tsv(
    output_path: Path,
    total_docs: int,
    has_tax_id: int,
    anomaly_counts: dict[str, int],
    has_species_tax_id: int,
    min_tax: Any,
    max_tax: Any,
) -> None:
    """Save analysis summary to TSV file."""
    with output_path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["metric", "value"])
        writer.writerow(["total_documents", total_docs])
        writer.writerow(["docs_with_tax_id", has_tax_id])
        writer.writerow(["tax_id_coverage_pct", f"{has_tax_id / total_docs * 100:.2f}" if total_docs > 0 else "0"])
        writer.writerow(["string_tax_ids", anomaly_counts["string_tax_ids"]])
        writer.writerow(["negative_tax_ids", anomaly_counts["negative_tax_ids"]])
        writer.writerow(["zero_tax_ids", anomaly_counts["zero_tax_ids"]])
        writer.writerow(["large_tax_ids_over_10M", anomaly_counts["large_tax_ids"]])
        writer.writerow(["docs_with_species_tax_id", has_species_tax_id])
        writer.writerow(["species_tax_id_coverage_pct", f"{has_species_tax_id / total_docs * 100:.2f}" if total_docs > 0 else "0"])
        if min_tax is not None:
            writer.writerow(["min_tax_id", min_tax])
        if max_tax is not None:
            writer.writerow(["max_tax_id", max_tax])

    console.print(f"\n[green]Analysis summary saved to {output_path}[/green]")


@click.command()
@click.option("--mongo-uri", default="mongodb://localhost:27017", help="MongoDB connection URI")
@click.option("--database", default="madin", help="Database name")
@click.option("--collection", default="madin", help="Collection name")
@click.option("--output-tsv", type=click.Path(), help="Optional: Save analysis summary to TSV file")
def cli(mongo_uri: str, database: str, collection: str, output_tsv: str | None) -> None:
    """Validate tax_id and species_tax_id field formats and consistency."""
    client = MongoClient(mongo_uri)
    db = client[database]
    coll = db[collection]

    total_docs = coll.count_documents({})
    console.print(f"[bold]Total documents:[/bold] {total_docs:,}\n")

    # Analyze tax_id field
    console.print("[bold]Analyzing tax_id field:[/bold]")
    has_tax_id = coll.count_documents({"tax_id": {"$exists": True, "$ne": None}})
    console.print(f"  Documents with tax_id: {has_tax_id:,} ({has_tax_id / total_docs * 100:.2f}%)")

    console.print("\n  Data types found in tax_id:")
    for item in get_tax_id_type_counts(coll):
        console.print(f"    {item['_id']}: {item['count']:,}")

    anomaly_counts = get_anomaly_counts(coll)
    print_anomaly_counts(anomaly_counts)

    # Analyze species_tax_id field
    console.print("\n[bold]Analyzing species_tax_id field:[/bold]")
    has_species_tax_id = coll.count_documents({"species_tax_id": {"$exists": True, "$ne": None}})
    console.print(f"  Documents with species_tax_id: {has_species_tax_id:,} ({has_species_tax_id / total_docs * 100:.2f}%)")

    # Compare tax_id and species_tax_id
    console.print("\n[bold]Comparing tax_id and species_tax_id:[/bold]")
    same_count, different_count, different_examples = compare_tax_ids(coll)
    console.print(f"  Documents where tax_id == species_tax_id: {same_count}")
    console.print(f"  Documents where tax_id != species_tax_id: {different_count}")
    display_different_examples(different_examples)

    # Tax_id value ranges
    console.print("\n[bold]Tax_id value ranges:[/bold]")
    min_tax, max_tax = get_tax_id_range(coll)
    if min_tax is not None:
        console.print(f"  Minimum tax_id: {min_tax}")
    if max_tax is not None:
        console.print(f"  Maximum tax_id: {max_tax}")

    print_string_tax_id_samples(coll)

    if output_tsv:
        save_analysis_tsv(Path(output_tsv), total_docs, has_tax_id, anomaly_counts, has_species_tax_id, min_tax, max_tax)

    client.close()


if __name__ == "__main__":
    cli()
