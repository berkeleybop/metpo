#!/usr/bin/env python3
"""Check ChromaDB internal state and diagnostics."""

import chromadb
from chromadb.config import Settings

print(f"ChromaDB version: {chromadb.__version__}")

client = chromadb.PersistentClient(
    path='embeddings_chroma',
    settings=Settings(anonymized_telemetry=False)
)

print("\n1. Client info:")
print(f"  Type: {type(client)}")
print(f"  Client class: {client.__class__.__name__}")

collection = client.get_collection('ols_embeddings')
print("\n2. Collection info:")
print(f"  Name: {collection.name}")
print(f"  Metadata: {collection.metadata}")
print(f"  Count: {collection.count():,}")

# Check if there are any admin/diagnostic methods
print("\n3. Available collection methods:")
methods = [m for m in dir(collection) if not m.startswith('_')]
print(f"  {', '.join(sorted(methods))}")

print("\n4. Available client methods:")
client_methods = [m for m in dir(client) if not m.startswith('_')]
print(f"  {', '.join(sorted(client_methods))}")

# Try to get collection details
print("\n5. Collection internals (if accessible):")
if hasattr(collection, '_client'):
    print(f"  Has _client: {type(collection._client)}")
if hasattr(collection, 'id'):
    print(f"  Collection ID: {collection.id}")
