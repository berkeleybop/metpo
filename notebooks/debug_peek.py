#!/usr/bin/env python3
"""Debug the peek() failure."""

import chromadb
from chromadb.config import Settings
import traceback

try:
    client = chromadb.PersistentClient(
        path='embeddings_chroma',
        settings=Settings(anonymized_telemetry=False)
    )
    collection = client.get_collection('ols_embeddings')

    print("Test 1: What IDs does ChromaDB think it has?")
    # Query returns IDs successfully, so let's see what they look like
    dummy = [0.0] * 1536
    results = collection.query(query_embeddings=[dummy], n_results=10)
    print(f"Sample IDs from query():")
    for i, id in enumerate(results['ids'][0][:5]):
        print(f"  {i+1}. {id}")

    print("\nTest 2: Can we get() by these specific IDs?")
    # Try to retrieve by the IDs we just got from query
    first_id = results['ids'][0][0]
    print(f"Attempting to get ID: {first_id}")
    get_result = collection.get(ids=[first_id])
    print(f"✓ get() worked!")
    print(f"  Returned {len(get_result['ids'])} record(s)")

    print("\nTest 3: Can we get() multiple IDs?")
    test_ids = results['ids'][0][:3]
    print(f"Attempting to get {len(test_ids)} IDs...")
    get_multi = collection.get(ids=test_ids)
    print(f"✓ get() multiple worked!")
    print(f"  Returned {len(get_multi['ids'])} record(s)")

    print("\nTest 4: What happens with peek() with different limits?")
    for limit in [1, 5, 10]:
        try:
            print(f"  Trying peek(limit={limit})...")
            peek = collection.peek(limit=limit)
            print(f"    ✓ Worked! Got {len(peek['ids'])} records")
        except Exception as e:
            print(f"    ✗ Failed: {e}")

    print("\nTest 5: Check ChromaDB's internal SQLite for ID issues")
    import sqlite3
    conn = sqlite3.connect('embeddings_chroma/chroma.sqlite3')
    cursor = conn.cursor()

    # Check what tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables in chroma.sqlite3: {[t[0] for t in tables]}")

    # Check the embeddings table
    cursor.execute("SELECT COUNT(*) FROM embeddings")
    emb_count = cursor.fetchone()[0]
    print(f"Embeddings count: {emb_count:,}")

    # Sample some IDs from the database
    cursor.execute("SELECT id FROM embeddings LIMIT 5")
    db_ids = cursor.fetchall()
    print(f"Sample IDs from embeddings table:")
    for i, (id,) in enumerate(db_ids):
        print(f"  {i+1}. {id}")

    conn.close()

except Exception as e:
    print(f'\n✗✗✗ ERROR ✗✗✗')
    traceback.print_exc()
