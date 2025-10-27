#!/usr/bin/env python3
"""Check consistency between what's in SQLite vs what query returns."""

import sqlite3

conn = sqlite3.connect('embeddings_chroma/chroma.sqlite3')
cursor = conn.cursor()

print("Checking ID formats in database...")

# Sample 100 random IDs to see the pattern
cursor.execute("""
    SELECT embedding_id, COUNT(*) as count
    FROM embeddings
    GROUP BY
        CASE
            WHEN embedding_id LIKE '%:%:%' THEN 'new_format'
            WHEN embedding_id LIKE '%:class:%' OR embedding_id LIKE '%:property:%' THEN 'partial_format'
            ELSE 'other'
        END
""")

print("\nID format distribution:")
for row in cursor.fetchall():
    print(f"  {row}")

# Check for our new format specifically
cursor.execute("""
    SELECT COUNT(*)
    FROM embeddings
    WHERE embedding_id LIKE '%:%:%http%'
""")
new_format_count = cursor.fetchone()[0]
print(f"\nRecords with new format (ontology:entityType:http...): {new_format_count:,}")

# Check total
cursor.execute("SELECT COUNT(*) FROM embeddings")
total = cursor.fetchone()[0]
print(f"Total records in database: {total:,}")

# Sample some records with the new format
print("\nSample records with NEW format:")
cursor.execute("""
    SELECT embedding_id
    FROM embeddings
    WHERE embedding_id LIKE '%:%:%http%'
    LIMIT 5
""")
for (eid,) in cursor.fetchall():
    print(f"  {eid}")

# Sample some records with weird format
print("\nSample records with WEIRD format:")
cursor.execute("""
    SELECT embedding_id
    FROM embeddings
    WHERE embedding_id NOT LIKE '%:%:%http%'
    LIMIT 10
""")
for (eid,) in cursor.fetchall():
    print(f"  {eid}")

conn.close()
