#!/usr/bin/env python3
"""Fix the 2 malformed records."""

import sqlite3
import chromadb
from chromadb.config import Settings

print("Step 1: Verify the bad records exist...")
conn = sqlite3.connect('embeddings_chroma/chroma.sqlite3')
cursor = conn.cursor()

cursor.execute("""
    SELECT id, embedding_id
    FROM embeddings
    WHERE (LENGTH(embedding_id) - LENGTH(REPLACE(embedding_id, ':', ''))) < 2
    OR embedding_id LIKE '% %'
    OR embedding_id LIKE '%  %'
""")

bad_records = cursor.fetchall()
print(f"Found {len(bad_records)} bad records:")
for internal_id, embedding_id in bad_records:
    print(f"  ID {internal_id}: '{embedding_id}'")

if len(bad_records) == 0:
    print("No bad records found!")
    conn.close()
    exit(0)

print("\nStep 2: Delete these records from ChromaDB...")
conn.close()

# Use ChromaDB API to delete
client = chromadb.PersistentClient(
    path='embeddings_chroma',
    settings=Settings(anonymized_telemetry=False)
)
collection = client.get_collection('ols_embeddings')

# Get the embedding_ids to delete
ids_to_delete = [emb_id for _, emb_id in bad_records]
print(f"Deleting IDs: {ids_to_delete}")

collection.delete(ids=ids_to_delete)
print(f"✓ Deleted {len(ids_to_delete)} bad records")

print("\nStep 3: Verify deletion...")
new_count = collection.count()
print(f"New count: {new_count:,}")
print(f"Expected: 9,570,043")

print("\nStep 4: Test peek() now...")
try:
    peek = collection.peek(limit=5)
    print(f"✓ peek() works! Got {len(peek['ids'])} records")
except Exception as e:
    print(f"✗ peek() still fails: {e}")
