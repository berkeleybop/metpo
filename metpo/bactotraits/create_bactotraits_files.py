#!/usr/bin/env python3
"""
Create BactoTraits Files Collection

Simple collection documenting the two BactoTraits files with euphemisms.

Usage:
    uv run python src/scripts/create_bactotraits_files.py
"""

import click
from pymongo import MongoClient

@click.command()
@click.option("--host", default="localhost", help="MongoDB host.")
@click.option("--port", default=27017, type=int, help="MongoDB port.")
@click.option("--db-name", default="bactotraits", help="MongoDB database name.")
@click.option("--collection-name", default="files", help="MongoDB collection name.")
def main(host, port, db_name, collection_name):
    """Create simple files collection."""

    files = [
        {
            "euphemism": "provider",
            "file_name": "BactoTraits_databaseV2_Jun2022.csv",
            "comments": "Original 3-row header CSV from ORDaR; semicolon-delimited; ISO-8859-1 encoding; contains periods and spaces in field names"
        },
        {
            "euphemism": "kg_microbe",
            "file_name": "BactoTraits.tsv",
            "comments": "Processed single-row header TSV; tab-delimited; UTF-8 encoding; periods and spaces still present in field names"
        }
    ]

    # Connect to MongoDB
    client = MongoClient(host, port)
    db = client[db_name]
    collection = db[collection_name]

    # Drop and recreate
    collection.drop()
    collection.insert_many(files)
    collection.create_index("euphemism", unique=True)

    print("Created bactotraits.files collection with 2 documents:")
    for f in files:
        print(f"  {f['euphemism']:12s} → {f['file_name']}")
    print()
    print("Query with:")
    print("  mongosh bactotraits --eval 'db.files.find().pretty()'")

if __name__ == "__main__":
    main()