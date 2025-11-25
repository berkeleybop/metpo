"""Shared utilities for madin analysis scripts."""

import csv
from collections import Counter
from pathlib import Path
from typing import Any

from pymongo.collection import Collection
from rich.console import Console
from rich.table import Table

console = Console()


def get_sample_values(
    coll: Collection,
    field: str,
    limit: int = 20,
) -> tuple[list[tuple[str, Any]], list[tuple[str, Any]]]:
    """Get sample values and categorize by comma presence.

    Args:
        coll: MongoDB collection
        field: Field name to analyze
        limit: Maximum number of samples

    Returns:
        Tuple of (single_value_examples, comma_examples)
    """
    samples = list(
        coll.find(
            {field: {"$exists": True, "$nin": [None, "NA"]}},
            {field: 1, "org_name": 1},
        ).limit(limit)
    )

    single_examples: list[tuple[str, Any]] = []
    comma_examples: list[tuple[str, Any]] = []

    for doc in samples:
        value = doc.get(field)
        org_name = doc.get("org_name", "")

        if isinstance(value, str):
            if "," in value:
                if len(comma_examples) < 5:
                    comma_examples.append((org_name, value))
            elif len(single_examples) < 10:
                single_examples.append((org_name, value))

    return single_examples, comma_examples


def count_field_values(coll: Collection, field: str) -> Counter:
    """Count occurrences of each field value.

    Args:
        coll: MongoDB collection
        field: Field name to count

    Returns:
        Counter with value frequencies
    """
    counter: Counter = Counter()
    cursor = coll.find(
        {field: {"$exists": True, "$nin": [None, "NA"]}},
        {field: 1},
    )
    for doc in cursor:
        value = doc.get(field, "")
        if value and value != "NA":
            counter[value] += 1
    return counter


def unpack_comma_separated(coll: Collection, field: str) -> Counter:
    """Unpack comma-separated values and count individual items.

    Args:
        coll: MongoDB collection
        field: Field name to unpack

    Returns:
        Counter with individual value frequencies
    """
    counter: Counter = Counter()
    cursor = coll.find(
        {field: {"$exists": True, "$nin": [None, "NA"]}},
        {field: 1},
    )
    for doc in cursor:
        value_str = doc.get(field, "")
        if value_str and value_str != "NA":
            # Split on ", " first, then try ","
            individual = [s.strip() for s in value_str.split(", ")]
            if len(individual) == 1 and "," in value_str:
                individual = [s.strip() for s in value_str.split(",")]
            counter.update(individual)
    return counter


def display_value_table(
    counter: Counter,
    total: int,
    value_column: str = "Value",
) -> None:
    """Display a table of values sorted by frequency.

    Args:
        counter: Counter with value frequencies
        total: Total count for percentage calculation
        value_column: Name for the value column
    """
    table = Table()
    table.add_column("Rank", style="cyan")
    table.add_column(value_column, style="green", no_wrap=False)
    table.add_column("Count", style="yellow")
    table.add_column("% of Total", style="magenta")

    for i, (value, count) in enumerate(counter.most_common(), 1):
        percentage = (count / total * 100) if total > 0 else 0
        table.add_row(str(i), str(value), f"{count:,}", f"{percentage:.2f}%")

    console.print(table)


def save_counter_to_tsv(
    counter: Counter,
    total: int,
    output_path: Path,
    columns: tuple[str, str, str] = ("value", "count", "percentage"),
) -> None:
    """Save counter results to TSV file.

    Args:
        counter: Counter with value frequencies
        total: Total count for percentage calculation
        output_path: Output file path
        columns: Column names for the TSV
    """
    with output_path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(columns)
        for value, count in counter.most_common():
            percentage = (count / total * 100) if total > 0 else 0
            writer.writerow([value, count, f"{percentage:.2f}"])

    console.print(f"\n[green]Results saved to {output_path}[/green]")
    console.print(f"  Total unique values: {len(counter)}")
    console.print(f"  Total mentions: {sum(counter.values()):,}")


def print_field_stats(
    coll: Collection,
    field: str,
    total_docs: int,
) -> int:
    """Print basic statistics for a field.

    Args:
        coll: MongoDB collection
        field: Field name
        total_docs: Total document count

    Returns:
        Count of documents with non-NA values
    """
    has_field = coll.count_documents({field: {"$exists": True, "$nin": [None, "NA"]}})
    console.print(f"[bold]Analyzing {field} field:[/bold]")
    console.print(
        f"  Documents with {field} (non-NA): {has_field:,} ({has_field / total_docs * 100:.2f}%)"
    )
    return has_field


def print_sample_analysis(
    single_examples: list[tuple[str, Any]],
    comma_examples: list[tuple[str, Any]],
    field: str,
) -> None:
    """Print sample analysis results.

    Args:
        single_examples: Examples without commas
        comma_examples: Examples with commas
        field: Field name for display
    """
    console.print("\n  Sample analysis (first 20):")
    console.print(f"    Single values: {len(single_examples)}")
    console.print(f"    Contains commas: {len(comma_examples)}")

    if single_examples:
        console.print("\n  Examples of single values:")
        for org, value in single_examples[:10]:
            console.print(f"    {org[:40]}: {value}")

    if comma_examples:
        console.print("\n  Examples with commas (potential lists):")
        for org, value in comma_examples:
            console.print(f"    {org[:40]}: {value}")


def analyze_naming_patterns(unique_values: list[str]) -> None:
    """Analyze and print naming pattern statistics.

    Args:
        unique_values: List of unique values to analyze
    """
    console.print("\n[bold]Analyzing naming patterns:[/bold]")
    underscore_count = sum(1 for v in unique_values if "_" in str(v))
    hyphen_count = sum(1 for v in unique_values if "-" in str(v))
    console.print(f"  Values with underscores: {underscore_count}/{len(unique_values)}")
    console.print(f"  Values with hyphens: {hyphen_count}/{len(unique_values)}")
