#!/usr/bin/env python3
"""Check ChromaDB health and known issues."""

import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(
    path='embeddings_chroma',
    settings=Settings(anonymized_telemetry=False)
)

print("1. Client heartbeat:")
try:
    heartbeat = client.heartbeat()
    print(f"  {heartbeat}")
except Exception as e:
    print(f"  Error: {e}")

print("\n2. System version:")
version = client.get_version()
print(f"  {version}")

print("\n3. List all collections:")
collections = client.list_collections()
for col in collections:
    print(f"  - {col.name}: {col.count():,} items")

print("\n4. Check if peek() implementation changed in 1.2.1:")
print("  GitHub: https://github.com/chroma-core/chroma")
print("  Search for: 'peek' 'Error finding id' in issues")
print("  Release notes: https://github.com/chroma-core/chroma/releases/tag/1.2.1")

print("\n5. What does peek() documentation say?")
collection = client.get_collection('ols_embeddings')
if collection.peek.__doc__:
    print(f"  {collection.peek.__doc__}")
else:
    print("  No docstring available")

print("\n6. Inspect peek() signature:")
import inspect
sig = inspect.signature(collection.peek)
print(f"  peek{sig}")
