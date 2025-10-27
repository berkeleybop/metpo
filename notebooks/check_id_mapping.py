#!/usr/bin/env python3
"""Check ChromaDB's internal ID mapping."""

import sqlite3

conn = sqlite3.connect('embeddings_chroma/chroma.sqlite3')
cursor = conn.cursor()

print("Checking embeddings table structure...")
cursor.execute("PRAGMA table_info(embeddings)")
columns = cursor.fetchall()
print("Columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

print("\nSample records from embeddings table:")
cursor.execute("SELECT id, segment_id, embedding_id FROM embeddings LIMIT 5")
for row in cursor.fetchall():
    print(f"  Internal ID: {row[0]}, Segment: {row[1]}, Embedding ID: {row[2]}")

print("\nChecking if embedding_id matches our external IDs...")
cursor.execute("SELECT embedding_id FROM embeddings LIMIT 5")
embedding_ids = cursor.fetchall()
print("Sample embedding_ids:")
for i, (eid,) in enumerate(embedding_ids):
    print(f"  {i+1}. {eid}")

print("\nChecking segments table...")
cursor.execute("SELECT * FROM segments LIMIT 3")
segments = cursor.fetchall()
print(f"Segments table has {len(segments)} entries (showing first 3):")
cursor.execute("PRAGMA table_info(segments)")
seg_cols = [col[1] for col in cursor.fetchall()]
print(f"  Columns: {seg_cols}")
for seg in segments:
    print(f"  {seg}")

conn.close()
