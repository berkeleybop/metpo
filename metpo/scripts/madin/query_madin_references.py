"""Query and display madin references from MongoDB."""

import csv
from pathlib import Path

import click
from pymongo import MongoClient
from rich.console import Console
from rich.table import Table

console = Console()


@click.command()
@click.option(
    "--mongo-uri",
    default="mongodb://localhost:27017",
    help="MongoDB connection URI",
    show_default=True,
)
@click.option(
    "--database",
    default="madin",
    help="Database name",
    show_default=True,
)
@click.option(
    "--ref-id",
    type=int,
    help="Specific ref_id to look up",
)
@click.option(
    "--output-tsv",
    type=click.Path(),
    help="Optional: Save results to TSV file",
)
def cli(
    mongo_uri: str, database: str, ref_id: int | None, output_tsv: str | None
) -> None:
    """Query madin references from MongoDB."""
    client = MongoClient(mongo_uri)
    db = client[database]
    ref_coll = db["references"]
    madin_coll = db["madin"]

    if ref_id:
        # Look up specific reference
        refs = list(ref_coll.find({"ref_id": ref_id}))

        if not refs:
            console.print(f"[red]No reference found for ref_id: {ref_id}[/red]")
            return

        console.print(f"\n[bold]Reference {ref_id}:[/bold]")
        for ref in refs:
            console.print(f"  Type: {ref['ref_type']}")
            console.print(f"  Citation: {ref['reference']}\n")

        # Find organisms that cite this reference
        organisms = list(
            madin_coll.find(
                {"ref_id": ref_id}, {"org_name": 1, "species": 1, "tax_id": 1}
            ).limit(10)
        )

        if organisms:
            console.print(
                "[bold]Organisms citing this reference (showing up to 10):[/bold]"
            )
            for org in organisms:
                console.print(
                    f"  - {org.get('org_name')} (tax_id: {org.get('tax_id')})"
                )
        else:
            console.print("[yellow]No organisms found citing this reference[/yellow]")

    else:
        # Show statistics
        total_refs = ref_coll.count_documents({})
        console.print("\n[bold]Reference Collection Statistics:[/bold]")
        console.print(f"  Total references: {total_refs:,}")

        # Find duplicates
        duplicate_pipeline = [
            {"$group": {"_id": "$ref_id", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}},
        ]
        duplicates = list(ref_coll.aggregate(duplicate_pipeline))

        if duplicates:
            console.print(f"  Duplicate ref_ids: {len(duplicates)}")
            console.print("\n[yellow]Duplicate ref_ids found:[/yellow]")
            for dup in duplicates[:10]:
                console.print(f"    ref_id {dup['_id']}: {dup['count']} entries")

        # Show sample of most commonly cited references
        console.print("\n[bold]Most commonly cited references:[/bold]")

        # Aggregate ref_id usage from madin collection
        pipeline = [
            {"$match": {"ref_id": {"$exists": True, "$nin": [None, "NA"]}}},
            {"$group": {"_id": "$ref_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10},
        ]

        top_refs = list(madin_coll.aggregate(pipeline))

        table = Table()
        table.add_column("Rank", style="cyan")
        table.add_column("ref_id", style="green")
        table.add_column("Citations", style="yellow")
        table.add_column("Reference", style="magenta", no_wrap=False)

        for i, item in enumerate(top_refs, 1):
            ref_id = item["_id"]
            count = item["count"]

            # Look up reference text
            ref_doc = ref_coll.find_one({"ref_id": ref_id})
            ref_text = "NOT FOUND"
            if ref_doc:
                ref_text = (
                    ref_doc["reference"][:80] + "..."
                    if len(ref_doc["reference"]) > 80
                    else ref_doc["reference"]
                )

            table.add_row(str(i), str(ref_id), f"{count:,}", ref_text)

        console.print(table)

        # Save to TSV if requested
        if output_tsv:
            output_path = Path(output_tsv)
            with open(output_path, "w", newline="") as f:
                writer = csv.writer(f, delimiter="\t")
                writer.writerow(["rank", "ref_id", "citation_count", "reference_text"])

                for i, item in enumerate(top_refs, 1):
                    ref_id_val = item["_id"]
                    count = item["count"]
                    ref_doc = ref_coll.find_one({"ref_id": ref_id_val})
                    ref_text = "NOT FOUND"
                    if ref_doc:
                        ref_text = ref_doc["reference"]
                    writer.writerow([i, ref_id_val, count, ref_text])

            console.print(f"\n[green]Results saved to {output_path}[/green]")

    client.close()


if __name__ == "__main__":
    cli()
