#!/usr/bin/env python3
"""Find all malformed records."""

import sqlite3

conn = sqlite3.connect('embeddings_chroma/chroma.sqlite3')
cursor = conn.cursor()

print("Finding ALL records that don't match the expected format...")

# Get all records that don't match ontology:entityType:iri pattern
cursor.execute("""
    SELECT id, embedding_id
    FROM embeddings
    WHERE embedding_id NOT LIKE '%:%:%'
    OR embedding_id NOT LIKE '%:class:%'
    AND embedding_id NOT LIKE '%:property:%'
    AND embedding_id NOT LIKE '%:individual:%'
    ORDER BY id
""")

bad_records = cursor.fetchall()
print(f"\nFound {len(bad_records)} potentially malformed records:")
for internal_id, embedding_id in bad_records[:20]:  # Show first 20
    print(f"  Internal ID: {internal_id}, Embedding ID: '{embedding_id}'")

if len(bad_records) > 20:
    print(f"  ... and {len(bad_records) - 20} more")

print("\n\nChecking if these are the issue with peek()...")
print("If peek() randomly samples and hits one of these, it might fail.")

# Better query - find records that DON'T have proper 3-part colon-separated format
cursor.execute("""
    SELECT id, embedding_id
    FROM embeddings
    WHERE (LENGTH(embedding_id) - LENGTH(REPLACE(embedding_id, ':', ''))) < 2
    OR embedding_id LIKE '% %'
    OR embedding_id LIKE '%  %'
""")

definitely_bad = cursor.fetchall()
print(f"\nDefinitely malformed records (< 2 colons or has spaces): {len(definitely_bad)}")
for internal_id, embedding_id in definitely_bad:
    print(f"  {internal_id}: '{embedding_id}'")

conn.close()
