#!/usr/bin/env python3
"""
Create BactoTraits Header Mapping Collection

This script creates a MongoDB collection that maps field names across three versions:
1. Provider's original (3-row header with category, units, field_name)
2. kg-microbe reformatted version
3. Current MongoDB field names (aggressively sanitized)

Usage:
    uv run create-bactotraits-field-mappings

Output:
    - MongoDB collection: bactotraits.field_mappings
    - JSON file: metadata/bactotraits_field_mappings.json
"""

import click
import json
from pathlib import Path
from pymongo import MongoClient


def sanitize_field_name(field_name):
    """
    Aggressively sanitize field names for MongoDB compatibility.

    Transformations:
    - Strip leading/trailing whitespace
    - Replace comparison operators: <= → _lte, >= → _gte, > → _gt, < → _lt
    - Replace periods with underscores
    - Replace hyphens with underscores
    - Replace internal spaces with underscores

    Examples:
        ' GC_42.65_57.0' → 'GC_42_65_57_0'
        'GC_<=42.65' → 'GC_lte_42_65'
        'non-motile' → 'non_motile'
        'NaO_>8' → 'NaO_gt_8'
    """
    sanitized = field_name.strip()

    # Replace comparison operators (order matters!)
    sanitized = sanitized.replace("<=", "_lte_")
    sanitized = sanitized.replace(">=", "_gte_")
    sanitized = sanitized.replace(">", "_gt_")
    sanitized = sanitized.replace("<", "_lt_")

    # Replace other problematic characters
    sanitized = sanitized.replace(".", "_")
    sanitized = sanitized.replace("-", "_")
    sanitized = sanitized.replace(" ", "_")

    # Clean up multiple consecutive underscores
    while "__" in sanitized:
        sanitized = sanitized.replace("__", "_")

    # Remove trailing underscores
    sanitized = sanitized.rstrip("_")

    return sanitized


def forward_fill_simple(row):
    """
    Simple forward-fill: empty values get filled with previous non-empty value.
    Leading empty values stay empty.
    """
    filled = []
    last_value = ""
    for value in row:
        if value.strip():
            last_value = value.strip()
        filled.append(last_value)
    return filled


def forward_fill_units(units_row, category_row):
    """
    Forward-fill units ONLY within same category groups.
    Reset when category changes.
    """
    filled = []
    last_unit = ""
    last_category = ""

    for unit, category in zip(units_row, category_row):
        # If category changed, reset the unit carry-forward
        if category != last_category:
            last_unit = ""
            last_category = category

        # Forward-fill within same category
        if unit.strip():
            last_unit = unit.strip()

        filled.append(last_unit)

    return filled


def read_provider_headers(provider_file):
    """Read the 3-row header structure from provider's CSV."""
    with open(provider_file, "r", encoding="ISO-8859-1") as f:
        # Read first 3 lines
        row1 = f.readline().strip().split(";")  # Category row
        row2 = f.readline().strip().split(";")  # Units row
        row3 = f.readline().strip().split(";")  # Field names row

    # Forward-fill category row
    category_filled = forward_fill_simple(row1)

    # Forward-fill units row (context-aware based on category)
    units_filled = forward_fill_units(row2, category_filled)

    # Field names preserved exactly
    fields = row3

    return category_filled, units_filled, fields


def read_kg_microbe_header(kg_microbe_file):
    """Read the single-row header from kg-microbe TSV."""
    if not kg_microbe_file.exists():
        print(f"Warning: kg-microbe file not found at {kg_microbe_file}")
        return None

    with open(kg_microbe_file, "r", encoding="utf-8") as f:
        header = f.readline().strip().split("\t")

    return header


def get_mongodb_fields_from_kg_microbe(kg_microbe_file):
    """
    Generate MongoDB field names by sanitizing kg-microbe header.
    This ensures they match what the import script will create.
    """
    if not kg_microbe_file.exists():
        print(f"Warning: kg-microbe file not found at {kg_microbe_file}")
        return None

    with open(kg_microbe_file, "r", encoding="utf-8") as f:
        header = f.readline().strip().split("\t")

    # Apply same sanitization as import script
    return [sanitize_field_name(field) for field in header]


def create_field_mappings(provider_file, kg_microbe_file):
    """Create comprehensive field mappings across all versions."""

    print("Reading provider headers (3 rows with forward-fill)...")
    category_row, units_row, fields_row = read_provider_headers(provider_file)

    print("Reading kg-microbe header...")
    kg_microbe_header = read_kg_microbe_header(kg_microbe_file)

    print("Generating sanitized MongoDB field names...")
    mongodb_fields = get_mongodb_fields_from_kg_microbe(kg_microbe_file)

    print(f"\nFound {len(fields_row)} provider fields")
    print(f"Found {len(kg_microbe_header) if kg_microbe_header else 0} kg-microbe fields")
    print(f"Generated {len(mongodb_fields) if mongodb_fields else 0} MongoDB fields")

    # Create mappings
    mappings = []

    # Handle the first two columns specially
    # Provider col 0: strain nÁ → removed in kg-microbe
    mappings.append({
        "position": 0,
        "provider": {
            "category": category_row[0] if len(category_row) > 0 else "",
            "units": units_row[0] if len(units_row) > 0 else "",
            "field_name": fields_row[0] if len(fields_row) > 0 else ""
        },
        "kg_microbe": "",
        "mongodb": "",
        "notes": "Row number column - removed in kg-microbe transformation"
    })

    # Provider col 1: Bacdive_ID → becomes col 0 in kg-microbe/MongoDB
    mappings.append({
        "position": 1,
        "provider": {
            "category": category_row[1] if len(category_row) > 1 else "",
            "units": units_row[1] if len(units_row) > 1 else "",
            "field_name": fields_row[1] if len(fields_row) > 1 else ""
        },
        "kg_microbe": kg_microbe_header[0] if kg_microbe_header and len(kg_microbe_header) > 0 else "",
        "mongodb": mongodb_fields[0] if mongodb_fields and len(mongodb_fields) > 0 else "",
        "notes": "Moved from provider position 2 to position 1"
    })

    # Special: ncbitaxon_id (new in kg-microbe at position 1)
    if kg_microbe_header and len(kg_microbe_header) > 1:
        mappings.append({
            "position": 2,
            "provider": {
                "category": "",
                "units": "",
                "field_name": ""
            },
            "kg_microbe": kg_microbe_header[1],
            "mongodb": mongodb_fields[1] if mongodb_fields and len(mongodb_fields) > 1 else "",
            "notes": "New column added by kg-microbe transformation (not in provider file)"
        })

    # Map remaining fields (provider 2+ → kg-microbe 2+ → mongodb 2+)
    for i in range(2, min(len(fields_row), 105)):
        provider_category = category_row[i] if i < len(category_row) else ""
        provider_units = units_row[i] if i < len(units_row) else ""
        provider_field = fields_row[i] if i < len(fields_row) else ""

        # kg-microbe and mongodb are at position i
        kg_field = kg_microbe_header[i] if kg_microbe_header and i < len(kg_microbe_header) else ""
        mongo_field = mongodb_fields[i] if mongodb_fields and i < len(mongodb_fields) else ""

        mapping = {
            "position": i + 1,
            "provider": {
                "category": provider_category,
                "units": provider_units,
                "field_name": provider_field
            },
            "kg_microbe": kg_field,
            "mongodb": mongo_field,
            "notes": ""
        }

        # Add notes about transformations applied
        notes = []
        if kg_field and kg_field.startswith(" "):
            notes.append("kg-microbe has leading whitespace")
        if kg_field and "-" in kg_field:
            notes.append("kg-microbe contains hyphen")
        if kg_field and ("." in kg_field):
            notes.append("kg-microbe contains period")
        if kg_field and ("<=" in kg_field or ">=" in kg_field or ">" in kg_field or "<" in kg_field):
            notes.append("kg-microbe contains comparison operator")

        # Note sanitization transformations
        if kg_field != mongo_field:
            notes.append("sanitized for MongoDB")

        mapping["notes"] = "; ".join(notes) if notes else ""

        mappings.append(mapping)

    return mappings


@click.command()
@click.option(
    "--provider-file",
    type=click.Path(exists=True, path_type=Path),
    default=Path("local/bactotraits/BactoTraits_databaseV2_Jun2022.csv"),
    help="Path to provider CSV file"
)
@click.option(
    "--kg-microbe-file",
    type=click.Path(exists=True, path_type=Path),
    default=Path("local/bactotraits/BactoTraits.tsv"),
    help="Path to kg-microbe TSV file"
)
@click.option(
    "--output-json",
    type=click.Path(path_type=Path),
    default=Path("metadata/bactotraits_field_mappings.json"),
    help="Path for output JSON file"
)
@click.option(
    "--db-name",
    default="bactotraits",
    help="MongoDB database name"
)
@click.option(
    "--collection-name",
    default="field_mappings",
    help="MongoDB collection name"
)
@click.option(
    "--mongo-uri",
    default="mongodb://localhost:27017/",
    help="MongoDB connection URI"
)
def main(provider_file, kg_microbe_file, output_json, db_name, collection_name, mongo_uri):
    """Create BactoTraits field mappings collection and JSON export."""
    print("=" * 80)
    print("BactoTraits Header Mapping Generator")
    print("=" * 80)
    print()

    # Create mappings
    mappings = create_field_mappings(provider_file, kg_microbe_file)

    # Save to JSON
    print(f"\nSaving mappings to {output_json}...")
    output_json.parent.mkdir(parents=True, exist_ok=True)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "total_fields": len(mappings),
                "description": "Mapping of BactoTraits field names across provider, kg-microbe, and MongoDB versions",
                "provider_file": provider_file.name,
                "kg_microbe_file": kg_microbe_file.name,
                "mongodb_collection": f"{db_name}.{collection_name}"
            },
            "mappings": mappings
        }, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved {len(mappings)} field mappings to JSON")

    # Load into MongoDB
    print("\nLoading mappings into MongoDB...")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    # Drop existing collection
    collection.drop()
    print(f"✓ Dropped existing {db_name}.{collection_name} collection")

    # Insert mappings
    if mappings:
        collection.insert_many(mappings)
        print(f"✓ Inserted {len(mappings)} documents into {db_name}.{collection_name}")

    # Create useful indexes
    collection.create_index("mongodb")
    collection.create_index("kg_microbe")
    collection.create_index("provider.field_name")
    collection.create_index("provider.category")
    print("✓ Created indexes")

    # Print summary statistics
    print("\n" + "=" * 80)
    print("Summary Statistics")
    print("=" * 80)

    total_fields = len(mappings)
    fields_with_categories = sum(1 for m in mappings
                                 if m.get("provider", {}).get("category")
                                 and m["provider"]["category"] not in ["", "NEW"])
    fields_with_units = sum(1 for m in mappings
                           if m.get("provider", {}).get("units")
                           and m["provider"]["units"] not in ["", "NEW"])
    fields_with_issues = sum(1 for m in mappings if m.get("notes"))

    print(f"Total fields: {total_fields}")
    print(f"Fields with categories: {fields_with_categories}")
    print(f"Fields with units: {fields_with_units}")
    print(f"Fields with issues: {fields_with_issues}")

    # Show examples of problematic fields
    print("\nExamples of fields with issues:")
    print("-" * 80)
    count = 0
    for m in mappings:
        if m.get("notes") and m.get("mongodb") not in ["REMOVED", ""]:
            print(f"  {m['mongodb']:30s} - {m['notes']}")
            count += 1
            if count >= 10:
                remaining = fields_with_issues - count
                if remaining > 0:
                    print(f"  ... and {remaining} more")
                break

    print("\n" + "=" * 80)
    print("Done!")
    print("=" * 80)
    print(f"\nQuery the collection with:")
    print(f"  mongosh {db_name} --eval 'db.{collection_name}.find().pretty()'")
    print(f"\nOr view the JSON file:")
    print(f"  cat {output_json}")
    print()


if __name__ == "__main__":
    main()
