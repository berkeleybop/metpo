"""Generate comprehensive field summary table for madin collection.

This script analyzes all fields in the madin collection and generates a summary
table with unique value counts, data types, and categorization.
"""

import csv
from collections import Counter
from pathlib import Path

import click
from pymongo import MongoClient
from rich.console import Console
from rich.table import Table


# Default output directory for madin analysis
def get_madin_output_dir() -> Path:
    """Get the default output directory for madin analysis."""
    return Path(__file__).parent.parent.parent.parent / "docs" / "madin_paths"

console = Console()


def detect_field_type(
    coll, field_name: str, sample_size: int = 1000
) -> tuple[str, dict]:
    """Detect field type and characteristics.

    Returns:
        Tuple of (field_type, metadata_dict)
    """
    # Get sample documents
    samples = list(
        coll.find(
            {field_name: {"$exists": True, "$nin": [None, "NA"]}}, {field_name: 1}
        ).limit(sample_size)
    )

    if not samples:
        return "no data", {}

    # Check data types
    types_seen = set()
    contains_comma = 0
    contains_underscore = 0
    all_numeric = True
    all_integer = True

    for doc in samples:
        value = doc.get(field_name)
        if value is None or value == "NA":
            continue

        types_seen.add(type(value).__name__)

        if isinstance(value, str):
            all_numeric = False
            all_integer = False
            if "," in value:
                contains_comma += 1
            if "_" in value:
                contains_underscore += 1
        elif isinstance(value, float):
            all_integer = False
        elif not isinstance(value, int):
            all_numeric = False
            all_integer = False

    metadata = {
        "types_seen": types_seen,
        "contains_comma_pct": (contains_comma / len(samples) * 100) if samples else 0,
        "contains_underscore_pct": (contains_underscore / len(samples) * 100)
        if samples
        else 0,
        "all_numeric": all_numeric,
        "all_integer": all_integer,
    }

    # Determine field type
    if all_integer:
        return "integer", metadata
    if all_numeric:
        return "float", metadata
    if "str" in types_seen:
        return "string", metadata
    return "mixed", metadata


def analyze_field(coll, field_name: str, total_docs: int) -> dict:
    """Comprehensive analysis of a single field.

    Returns:
        Dictionary with analysis results
    """
    # Count documents with field
    has_field = coll.count_documents(
        {field_name: {"$exists": True, "$nin": [None, "NA"]}}
    )

    # Get unique count
    unique_values = coll.distinct(field_name, {field_name: {"$nin": [None, "NA"]}})
    unique_count = len(unique_values)

    # Detect field type
    field_type, metadata = detect_field_type(coll, field_name)

    # Check if comma-separated list
    # Known list fields or if significant percentage have commas
    comma_count = coll.count_documents({field_name: {"$regex": ","}})
    known_list_fields = ["pathways", "carbon_substrates"]
    is_list = (field_name in known_list_fields and comma_count > 0) or (
        comma_count > 0 and metadata.get("contains_comma_pct", 0) > 5
    )

    unpacked_count = None
    if is_list:
        # Try to unpack and count unique values
        unpacked_counter = Counter()
        cursor = coll.find(
            {field_name: {"$exists": True, "$nin": [None, "NA"]}}, {field_name: 1}
        ).limit(10000)  # Limit for performance

        for doc in cursor:
            value_str = doc.get(field_name, "")
            if value_str and value_str != "NA":
                # Split on ", " (comma-space)
                individual_values = [v.strip() for v in value_str.split(", ")]
                unpacked_counter.update(individual_values)

        unpacked_count = len(unpacked_counter)

    # Categorize field
    category = categorize_field(
        field_name, unique_count, has_field, total_docs, field_type, is_list, metadata
    )

    return {
        "field_name": field_name,
        "unique_count": unique_count,
        "unpacked_count": unpacked_count,
        "has_field": has_field,
        "coverage_pct": (has_field / total_docs * 100) if total_docs > 0 else 0,
        "field_type": field_type,
        "is_list": is_list,
        "category": category,
        "metadata": metadata,
    }


# Field categorization constants
TAXONOMY_ID_FIELDS = {"tax_id", "species_tax_id"}
TAXONOMY_NAME_FIELDS = {
    "org_name", "species", "genus", "family", "order", "class", "phylum", "superkingdom"
}
LIST_FIELD_NOTES = {
    "carbon_substrates": "comma-space delimited, quoted compounds, underscore pairs",
    "pathways": "comma-space delimited, hierarchical underscores",
}


def _categorize_taxonomy_id(field_name: str) -> dict | None:
    """Categorize taxonomy identifier fields."""
    if field_name in TAXONOMY_ID_FIELDS:
        return {
            "data_type": "identifier",
            "subtype": "integer",
            "namespace": "NCBITaxon",
            "notes": "",
        }
    return None


def _categorize_ref_id(field_name: str) -> dict | None:
    """Categorize reference ID field."""
    if field_name == "ref_id":
        return {
            "data_type": "identifier",
            "subtype": "integer",
            "namespace": "internal",
            "notes": "foreign key to references collection",
        }
    return None


def _categorize_taxonomy_name(field_name: str) -> dict | None:
    """Categorize taxonomy name fields."""
    if field_name in TAXONOMY_NAME_FIELDS:
        return {
            "data_type": "identifier",
            "subtype": "text",
            "namespace": "",
            "notes": "taxonomic name",
        }
    return None


def _categorize_data_source(field_name: str) -> dict | None:
    """Categorize data source field."""
    if field_name == "data_source":
        return {
            "data_type": "identifier",
            "subtype": "text",
            "namespace": "",
            "notes": "source database name",
        }
    return None


def _categorize_list_field(field_name: str, is_list: bool) -> dict | None:
    """Categorize comma-separated list fields."""
    if is_list:
        notes = LIST_FIELD_NOTES.get(field_name, "comma-space delimited")
        return {"data_type": "list", "subtype": "", "namespace": "", "notes": notes}
    return None


def _categorize_isolation_source(field_name: str) -> dict | None:
    """Categorize isolation source field."""
    if field_name == "isolation_source":
        return {
            "data_type": "categorical",
            "subtype": "text",
            "namespace": "",
            "notes": "hierarchical underscores",
        }
    return None


def _categorize_numeric_field(
    field_name: str, field_type: str, unique_count: int
) -> dict | None:
    """Categorize numeric continuous fields."""
    if field_type not in ["integer", "float"]:
        return None

    # Gene count fields
    if field_name.endswith("_genes"):
        return {
            "data_type": "continuous",
            "subtype": "count",
            "namespace": "",
            "notes": "gene count",
        }

    # Dimension fields (d1_lo, d1_up, d2_lo, d2_up)
    if field_name.startswith(("d1_", "d2_")):
        return {
            "data_type": "continuous",
            "subtype": "float",
            "namespace": "",
            "notes": "cell dimension (μm)",
        }

    # Other numeric fields
    return {
        "data_type": "continuous",
        "subtype": field_type,
        "namespace": "",
        "notes": "",
    }


def categorize_field(
    field_name: str,
    unique_count: int,
    _has_field: int,
    _total_docs: int,
    field_type: str,
    is_list: bool,
    _metadata: dict,
) -> dict:
    """Categorize field based on characteristics.

    Returns dictionary with:
        - data_type: continuous, categorical, identifier, list
        - subtype: specific details
        - namespace: for identifiers (e.g., NCBITaxon)
        - notes: additional information
    """
    # Try each categorization strategy in order
    categorizers = [
        lambda: _categorize_taxonomy_id(field_name),
        lambda: _categorize_ref_id(field_name),
        lambda: _categorize_taxonomy_name(field_name),
        lambda: _categorize_data_source(field_name),
        lambda: _categorize_list_field(field_name, is_list),
        lambda: _categorize_isolation_source(field_name),
        lambda: (
            {"data_type": "categorical", "subtype": "text", "namespace": "", "notes": ""}
            if field_type == "string" and unique_count <= 30
            else None
        ),
        lambda: _categorize_numeric_field(field_name, field_type, unique_count),
    ]

    for categorizer in categorizers:
        result = categorizer()
        if result is not None:
            return result

    # Default
    return {"data_type": "text", "subtype": "", "namespace": "", "notes": ""}


def display_results_table(results: list[dict]) -> None:
    """Display field analysis results in a rich table."""
    console.print("\n[bold]Field Summary Table:[/bold]\n")

    table = Table(title="Madin Collection Fields")
    table.add_column("Field Name", style="cyan")
    table.add_column("Unique Values", style="green", justify="right")
    table.add_column("Unpacked", style="yellow", justify="right")
    table.add_column("Coverage %", style="blue", justify="right")
    table.add_column("Data Type", style="magenta")
    table.add_column("Subtype", style="white")
    table.add_column("Namespace", style="cyan")
    table.add_column("Notes", style="white", no_wrap=False)

    for result in results:
        unpacked_str = f"{result['unpacked_count']:,}" if result["unpacked_count"] else ""
        coverage_str = f"{result['coverage_pct']:.1f}%"
        category = result["category"]

        table.add_row(
            result["field_name"],
            f"{result['unique_count']:,}",
            unpacked_str,
            coverage_str,
            category.get("data_type", ""),
            category.get("subtype", ""),
            category.get("namespace", ""),
            category.get("notes", ""),
        )

    console.print(table)


def save_results_to_tsv(results: list[dict], output_path: Path) -> None:
    """Save field analysis results to TSV file."""
    with output_path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow([
            "Field Name", "Unique Values", "Unpacked Unique", "Coverage %",
            "Data Type", "Subtype", "Namespace", "Notes",
        ])

        for result in results:
            unpacked_str = str(result["unpacked_count"]) if result["unpacked_count"] else ""
            category = result["category"]
            writer.writerow([
                result["field_name"],
                result["unique_count"],
                unpacked_str,
                f"{result['coverage_pct']:.2f}",
                category.get("data_type", ""),
                category.get("subtype", ""),
                category.get("namespace", ""),
                category.get("notes", ""),
            ])

    console.print(f"\n[green]Table saved to {output_path}[/green]")


def print_summary_statistics(results: list[dict]) -> None:
    """Print summary statistics for field analysis."""
    console.print("\n[bold]Summary Statistics:[/bold]")
    console.print(f"  Total fields: {len(results)}")
    console.print(
        f"  Categorical fields: {sum(1 for r in results if r['category'].get('data_type') == 'categorical')}"
    )
    console.print(
        f"  Continuous fields: {sum(1 for r in results if r['category'].get('data_type') == 'continuous')}"
    )
    console.print(
        f"  Identifier fields: {sum(1 for r in results if r['category'].get('data_type') == 'identifier')}"
    )
    console.print(f"  List fields: {sum(1 for r in results if r['is_list'])}")


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
    "--collection",
    default="madin",
    help="Collection name",
    show_default=True,
)
@click.option(
    "--output-tsv",
    help="Output TSV file path",
    type=click.Path(),
)
def cli(mongo_uri: str, database: str, collection: str, output_tsv: str | None) -> None:
    """Generate field summary table for madin collection."""
    output_path = Path(output_tsv) if output_tsv else get_madin_output_dir() / "madin_field_summary.tsv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    client = MongoClient(mongo_uri)
    db = client[database]
    coll = db[collection]

    total_docs = coll.count_documents({})
    console.print(f"[bold]Total documents:[/bold] {total_docs:,}\n")
    console.print("[bold]Analyzing all fields...[/bold]\n")

    sample = coll.find_one()
    if not sample:
        console.print("[red]No documents found in collection[/red]")
        return

    field_names = [key for key in sample if key != "_id"]
    results = []
    for field_name in field_names:
        console.print(f"  Analyzing: {field_name}")
        results.append(analyze_field(coll, field_name, total_docs))

    results.sort(key=lambda x: x["unique_count"], reverse=True)

    display_results_table(results)
    save_results_to_tsv(results, output_path)
    print_summary_statistics(results)

    client.close()


if __name__ == "__main__":
    cli()
