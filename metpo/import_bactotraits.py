"""Import BactoTraits data into MongoDB."""
import click
import csv
from pathlib import Path
from pymongo import MongoClient
from tqdm import tqdm


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
    sanitized = sanitized.replace('<=', '_lte_')
    sanitized = sanitized.replace('>=', '_gte_')
    sanitized = sanitized.replace('>', '_gt_')
    sanitized = sanitized.replace('<', '_lt_')

    # Replace other problematic characters
    sanitized = sanitized.replace('.', '_')
    sanitized = sanitized.replace('-', '_')
    sanitized = sanitized.replace(' ', '_')

    # Clean up multiple consecutive underscores
    while '__' in sanitized:
        sanitized = sanitized.replace('__', '_')

    # Remove trailing underscores
    sanitized = sanitized.rstrip('_')

    return sanitized


@click.command()
@click.option(
    "--input-file", "-i",
    type=click.Path(exists=True, path_type=Path),
    default=Path("/Users/MAM/Documents/gitrepos/kg-microbe/kg_microbe/transform_utils/bactotraits/tmp/BactoTraits.tsv"),
    help="Path to kg-microbe BactoTraits.tsv file"
)
@click.option(
    "--database", "-d",
    default="bactotraits",
    help="MongoDB database name"
)
@click.option(
    "--collection", "-c",
    default="bactotraits",
    help="MongoDB collection name"
)
@click.option(
    "--drop/--no-drop",
    default=True,
    help="Drop existing collection before import"
)
@click.option(
    "--mongo-uri",
    default="mongodb://localhost:27017/",
    help="MongoDB connection URI"
)
def import_bactotraits(input_file, database, collection, drop, mongo_uri):
    """
    Import BactoTraits TSV data into MongoDB.

    The script:
    1. Reads the kg-microbe BactoTraits.tsv file
    2. Aggressively sanitizes field names for MongoDB compatibility
    3. Imports into MongoDB with proper field types
    4. Creates indexes for common queries

    Field name transformations:
    - Strip leading/trailing whitespace
    - Comparison operators: <= → _lte, >= → _gte, > → _gt, < → _lt
    - Periods → underscores
    - Hyphens → underscores
    - Spaces → underscores

    Examples:
        ' GC_42.65_57.0' → 'GC_42_65_57_0'
        'GC_<=42.65' → 'GC_lte_42_65'
        'non-motile' → 'non_motile'

    Usage:
        uv run import-bactotraits
        uv run import-bactotraits --input-file /path/to/BactoTraits.tsv --no-drop
    """
    click.echo("=" * 80)
    click.echo("BactoTraits MongoDB Import")
    click.echo("=" * 80)
    click.echo()

    # Validate input file
    if not input_file.exists():
        click.echo(f"❌ Error: Input file not found: {input_file}", err=True)
        click.echo()
        click.echo("Expected location:")
        click.echo("  /Users/MAM/Documents/gitrepos/kg-microbe/kg_microbe/transform_utils/bactotraits/tmp/BactoTraits.tsv")
        click.echo()
        click.echo("Or use --input-file to specify a different location")
        raise click.Abort()

    click.echo(f"Input file:  {input_file}")
    click.echo(f"Database:    {database}")
    click.echo(f"Collection:  {collection}")
    click.echo(f"Drop first:  {drop}")
    click.echo()

    # Connect to MongoDB
    click.echo("Connecting to MongoDB...")
    client = MongoClient(mongo_uri)
    db = client[database]
    coll = db[collection]

    # Drop collection if requested
    if drop:
        click.echo(f"Dropping existing collection '{collection}'...")
        coll.drop()
        click.echo("✓ Collection dropped")

    # Read and process TSV file
    click.echo(f"\nReading {input_file.name}...")

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')

        # Read header and sanitize field names
        header = next(reader)

        # Aggressively sanitize field names for MongoDB
        sanitized_header = [sanitize_field_name(field) for field in header]

        click.echo(f"✓ Read header with {len(sanitized_header)} fields")

        # Show field name transformations
        transformations = [(orig, san) for orig, san in zip(header, sanitized_header) if orig != san]
        if transformations:
            click.echo(f"\n{len(transformations)} field names sanitized:")
            for orig, san in transformations[:10]:
                click.echo(f"  '{orig}' → '{san}'")
            if len(transformations) > 10:
                click.echo(f"  ... and {len(transformations) - 10} more")

        # Count rows
        click.echo("\nCounting rows...")
        row_count = sum(1 for _ in f)
        f.seek(0)
        next(reader)  # Skip header again

        # Import data
        click.echo(f"\nImporting {row_count} documents...")

        documents = []
        batch_size = 1000

        for row in tqdm(reader, total=row_count, desc="Processing"):
            # Create document from row
            doc = {}
            for field_name, value in zip(sanitized_header, row):
                # Convert empty strings to empty (preserve for field_mappings compatibility)
                # Convert numeric-like strings appropriately
                if value == '':
                    doc[field_name] = ''
                elif value in ('0', '1'):
                    # Binary trait values - store as integers
                    doc[field_name] = int(value)
                else:
                    # Keep as string (includes fractional values like "0.5", "0.333...")
                    doc[field_name] = value

            documents.append(doc)

            # Insert in batches
            if len(documents) >= batch_size:
                coll.insert_many(documents)
                documents = []

        # Insert remaining documents
        if documents:
            coll.insert_many(documents)

    click.echo(f"\n✓ Imported {row_count} documents")

    # Create indexes
    click.echo("\nCreating indexes...")
    coll.create_index('Bacdive_ID')
    coll.create_index('ncbitaxon_id')
    coll.create_index([('Kingdom', 1), ('Phylum', 1), ('Class', 1)])
    click.echo("✓ Created indexes on Bacdive_ID, ncbitaxon_id, and taxonomy fields")

    # Verify import
    count = coll.count_documents({})
    click.echo(f"\n✓ Verification: {count} documents in collection")

    # Show sample document
    click.echo("\nSample document:")
    sample = coll.find_one({}, {'_id': 0})
    if sample:
        # Show first 10 fields
        for i, (key, value) in enumerate(list(sample.items())[:10]):
            click.echo(f"  {key}: {repr(value)[:50]}")
        if len(sample) > 10:
            click.echo(f"  ... and {len(sample) - 10} more fields")

    click.echo()
    click.echo("=" * 80)
    click.echo("Import complete!")
    click.echo("=" * 80)
    click.echo()
    click.echo("Query examples:")
    click.echo(f"  mongosh {database} --eval 'db.{collection}.findOne()'")
    click.echo(f"  mongosh {database} --eval 'db.{collection}.countDocuments({{}})'")
    click.echo()


if __name__ == "__main__":
    import_bactotraits()
