"""Query and display madin references from MongoDB."""

import csv
from pathlib import Path

import click
from pymongo import MongoClient
from pymongo.collection import Collection
from rich.console import Console
from rich.table import Table

console = Console()


def lookup_specific_reference(ref_coll: Collection, madin_coll: Collection, ref_id: int) -> None:
    """Look up and display a specific reference."""
    refs = list(ref_coll.find({"ref_id": ref_id}))

    if not refs:
        console.print(f"[red]No reference found for ref_id: {ref_id}[/red]")
        return

    console.print(f"\n[bold]Reference {ref_id}:[/bold]")
    for ref in refs:
        console.print(f"  Type: {ref['ref_type']}")
        console.print(f"  Citation: {ref['reference']}\n")

    organisms = list(
        madin_coll.find({"ref_id": ref_id}, {"org_name": 1, "species": 1, "tax_id": 1}).limit(10)
    )

    if organisms:
        console.print("[bold]Organisms citing this reference (showing up to 10):[/bold]")
        for org in organisms:
            console.print(f"  - {org.get('org_name')} (tax_id: {org.get('tax_id')})")
    else:
        console.print("[yellow]No organisms found citing this reference[/yellow]")


def get_duplicate_ref_ids(ref_coll: Collection) -> list[dict]:
    """Find duplicate ref_ids in the references collection."""
    pipeline = [
        {"$group": {"_id": "$ref_id", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}},
    ]
    return list(ref_coll.aggregate(pipeline))


def get_top_cited_refs(madin_coll: Collection) -> list[dict]:
    """Get the most commonly cited references."""
    pipeline = [
        {"$match": {"ref_id": {"$exists": True, "$nin": [None, "NA"]}}},
        {"$group": {"_id": "$ref_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    return list(madin_coll.aggregate(pipeline))


def display_top_refs_table(top_refs: list[dict], ref_coll: Collection) -> None:
    """Display table of top cited references."""
    table = Table()
    table.add_column("Rank", style="cyan")
    table.add_column("ref_id", style="green")
    table.add_column("Citations", style="yellow")
    table.add_column("Reference", style="magenta", no_wrap=False)

    for i, item in enumerate(top_refs, 1):
        ref_id = item["_id"]
        ref_doc = ref_coll.find_one({"ref_id": ref_id})
        ref_text = "NOT FOUND"
        if ref_doc:
            ref_text = ref_doc["reference"][:80] + "..." if len(ref_doc["reference"]) > 80 else ref_doc["reference"]
        table.add_row(str(i), str(ref_id), f"{item['count']:,}", ref_text)

    console.print(table)


def save_top_refs_tsv(top_refs: list[dict], ref_coll: Collection, output_path: Path) -> None:
    """Save top cited references to TSV file."""
    with output_path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["rank", "ref_id", "citation_count", "reference_text"])

        for i, item in enumerate(top_refs, 1):
            ref_doc = ref_coll.find_one({"ref_id": item["_id"]})
            ref_text = ref_doc["reference"] if ref_doc else "NOT FOUND"
            writer.writerow([i, item["_id"], item["count"], ref_text])

    console.print(f"\n[green]Results saved to {output_path}[/green]")


def show_collection_statistics(ref_coll: Collection, madin_coll: Collection, output_tsv: str | None) -> None:
    """Show statistics about the reference collection."""
    total_refs = ref_coll.count_documents({})
    console.print("\n[bold]Reference Collection Statistics:[/bold]")
    console.print(f"  Total references: {total_refs:,}")

    duplicates = get_duplicate_ref_ids(ref_coll)
    if duplicates:
        console.print(f"  Duplicate ref_ids: {len(duplicates)}")
        console.print("\n[yellow]Duplicate ref_ids found:[/yellow]")
        for dup in duplicates[:10]:
            console.print(f"    ref_id {dup['_id']}: {dup['count']} entries")

    console.print("\n[bold]Most commonly cited references:[/bold]")
    top_refs = get_top_cited_refs(madin_coll)
    display_top_refs_table(top_refs, ref_coll)

    if output_tsv:
        save_top_refs_tsv(top_refs, ref_coll, Path(output_tsv))


@click.command()
@click.option("--mongo-uri", default="mongodb://localhost:27017", help="MongoDB connection URI", show_default=True)
@click.option("--database", default="madin", help="Database name", show_default=True)
@click.option("--ref-id", type=int, help="Specific ref_id to look up")
@click.option("--output-tsv", type=click.Path(), help="Optional: Save results to TSV file")
def cli(mongo_uri: str, database: str, ref_id: int | None, output_tsv: str | None) -> None:
    """Query madin references from MongoDB."""
    client = MongoClient(mongo_uri)
    db = client[database]
    ref_coll = db["references"]
    madin_coll = db["madin"]

    if ref_id:
        lookup_specific_reference(ref_coll, madin_coll, ref_id)
    else:
        show_collection_statistics(ref_coll, madin_coll, output_tsv)

    client.close()


if __name__ == "__main__":
    cli()
