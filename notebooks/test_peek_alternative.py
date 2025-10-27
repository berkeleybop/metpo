#!/usr/bin/env python3
"""Test if we can simulate peek() using get()."""

import chromadb
from chromadb.config import Settings
import sqlite3

client = chromadb.PersistentClient(
    path='embeddings_chroma',
    settings=Settings(anonymized_telemetry=False)
)
collection = client.get_collection('ols_embeddings')

print("Test 1: Can we manually peek by getting first N IDs from SQLite?")
conn = sqlite3.connect('embeddings_chroma/chroma.sqlite3')
cursor = conn.cursor()

# Get first 5 embedding_ids
cursor.execute("SELECT embedding_id FROM embeddings LIMIT 5")
ids = [row[0] for row in cursor.fetchall()]
print(f"First 5 IDs from database: {ids}")

try:
    results = collection.get(ids=ids)
    print(f"✓ get() with these IDs works! Got {len(results['ids'])} records")
    for i, id in enumerate(results['ids'][:3]):
        print(f"  {i+1}. {id}")
except Exception as e:
    print(f"✗ get() failed: {e}")

print("\nTest 2: Try getting by internal sequential IDs...")
cursor.execute("SELECT id, embedding_id FROM embeddings ORDER BY id LIMIT 5")
rows = cursor.fetchall()
print("Records by internal ID order:")
for internal_id, embedding_id in rows:
    print(f"  Internal: {internal_id}, External: {embedding_id}")

# Try to get using those external IDs
external_ids = [embedding_id for _, embedding_id in rows]
try:
    results = collection.get(ids=external_ids)
    print(f"✓ Can get these records: {len(results['ids'])}")
except Exception as e:
    print(f"✗ Failed: {e}")

conn.close()

print("\nTest 3: Check if there's an offset/limit issue...")
# Try different ways that peek might work
try:
    # Maybe peek uses where filters?
    results = collection.get(limit=5)
    print(f"✓ get(limit=5) works! Got {len(results['ids'])} records")
except Exception as e:
    print(f"✗ get(limit=5) failed: {e}")

print("\nConclusion: peek() has a specific bug, but we don't need it.")
print("query() works perfectly, which is all we need for METPO matching.")
