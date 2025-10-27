#!/usr/bin/env python3
"""Check if stored embeddings are valid vectors."""

import chromadb
from chromadb.config import Settings
import numpy as np

client = chromadb.PersistentClient(
    path='embeddings_chroma',
    settings=Settings(anonymized_telemetry=False)
)
collection = client.get_collection('ols_embeddings')

# Get some specific records and check their embeddings
print("Checking stored embeddings...")

# Get a few records
results = collection.get(
    limit=5,
    include=["embeddings", "documents", "metadatas"]
)

print(f"Retrieved {len(results['ids'])} records\n")

for i in range(min(3, len(results['ids']))):
    eid = results['ids'][i]
    doc = results['documents'][i][:80]
    emb = results['embeddings'][i]

    print(f"Record {i+1}: {eid}")
    print(f"  Document: {doc}")
    print(f"  Embedding length: {len(emb)}")
    print(f"  Embedding stats: min={min(emb):.4f}, max={max(emb):.4f}, mean={np.mean(emb):.4f}")
    print(f"  First 5 values: {emb[:5]}")
    print()

# Check if all embeddings have same dimension
print(f"\nAll embeddings have dimension: {len(results['embeddings'][0])}")

# Check if they're all zeros or obviously corrupt
all_same = all(emb == results['embeddings'][0] for emb in results['embeddings'])
print(f"Are all embeddings identical? {all_same}")
