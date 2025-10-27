#!/usr/bin/env python3
"""Diagnose ChromaDB connection and index issues."""

import chromadb
from chromadb.config import Settings
import traceback

try:
    print("Step 1: Creating client...")
    client = chromadb.PersistentClient(
        path='embeddings_chroma',
        settings=Settings(anonymized_telemetry=False)
    )
    print('✓ Client OK')

    print("\nStep 2: Getting collection...")
    collection = client.get_collection('ols_embeddings')
    print('✓ Collection OK')

    print(f'\nStep 3: Attempting count...')
    count = collection.count()
    print(f'✓ Count OK: {count:,}')

    print(f'\nStep 4: Attempting peek...')
    try:
        peek = collection.peek(limit=1)
        print(f'✓ Peek OK')
        print(f"  Sample ID: {peek['ids'][0]}")
    except Exception as e:
        print(f'✗ Peek failed: {e}')
        print(f'  (Continuing to test query...)')

    print(f'\nStep 5: Attempting simple query...')
    # Create a dummy embedding vector (1536 dimensions, all zeros)
    dummy_embedding = [0.0] * 1536
    results = collection.query(
        query_embeddings=[dummy_embedding],
        n_results=5
    )
    print(f'✓ Query OK')
    print(f"  Returned {len(results['ids'][0])} results")
    for i, result_id in enumerate(results['ids'][0][:3]):
        print(f"  Result {i+1}: {result_id}")

    print(f'\nStep 6: Testing query with different embedding...')
    # Create a different embedding (all 0.1s)
    dummy_embedding2 = [0.1] * 1536
    results2 = collection.query(
        query_embeddings=[dummy_embedding2],
        n_results=5,
        include=["documents", "metadatas", "distances"]
    )
    print(f'✓ Query OK')
    print(f"  Distance to first result: {results2['distances'][0][0]:.4f}")
    print(f"  Metadata: {results2['metadatas'][0][0]}")
    print(f"  Document preview: {results2['documents'][0][0][:100]}...")

    print("\n✓✓✓ All tests passed! ChromaDB query is working.")

except Exception as e:
    print(f'\n✗✗✗ ERROR OCCURRED ✗✗✗\n')
    print(f'Error type: {type(e).__name__}')
    print(f'Error message: {str(e)}')
    print(f'\nFull stack trace:')
    traceback.print_exc()
