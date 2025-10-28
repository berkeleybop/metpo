# ChromaDB peek() Failure Issue

## Summary
ChromaDB `collection.peek()` fails with "Error finding id" after HNSW index rebuild, while `query()` and `get()` work correctly.

## Environment
- ChromaDB version: 1.2.1
- Python version: 3.11.10
- Platform: Ubuntu Linux (kernel 6.8.0-85-generic)
- Total records: 9,570,043 embeddings
- Vector dimensions: 1536 (text-embedding-3-small)
- Collection metadata: SQLite backend
- Memory: 62GB RAM total, migration peaked at ~54GB

## Reproduction Steps

### Initial Setup
1. Migrated 9,570,045 records from SQLite to ChromaDB using custom migration script
2. Migration completed successfully with 0 errors reported
3. HNSW index built during migration (consumed ~54GB RAM peak)
4. Index directory: `b3f185ec-a4d7-4d47-b309-9b4ac70cddf2/` (58GB total)
   - `data_level0.bin`: 57GB
   - `index_metadata.pickle`: 1.2GB
   - `link_lists.bin`: 78MB
   - `length.bin`: 37MB
   - `header.bin`: 100 bytes

### Trigger Condition
1. Deleted corrupted HNSW index directory
2. Let ChromaDB rebuild index on first access
3. Index rebuilt successfully (count() now works)
4. peek() fails consistently

## Observed Behavior

### What Works ✓
```python
collection.count()  # Returns: 9,570,043
collection.query(query_embeddings=[...], n_results=5)  # Works perfectly
collection.get(ids=['specific:id:here'])  # Works perfectly
collection.get(limit=5)  # Works perfectly
```

### What Fails ✗
```python
collection.peek(limit=1)   # Error: "Error finding id"
collection.peek(limit=5)   # Error: "Error finding id"
collection.peek(limit=10)  # Error: "Error finding id"
```

## Error Details

**Full error message:**
```
chromadb.errors.InternalError: Error executing plan: Internal error: Error finding id
```

**Stack trace:**
```python
File "chromadb/api/models/Collection.py", line 160, in peek
    self._client._peek(
File "chromadb/api/rust.py", line 348, in _peek
    return self._get(
File "chromadb/api/rust.py", line 381, in _get
    rust_response = self.bindings.get(
chromadb.errors.InternalError: Error executing plan: Internal error: Error finding id
```

## Investigation Results

### Database State
- SQLite `embeddings` table has 9,570,043 records
- All records have valid embedding_id values (external IDs)
- Internal ID sequence: 1 to 9,570,043
- Two malformed records were found and deleted (trailing spaces in IDs)
- Deletion did not resolve peek() failure

### ID System
ChromaDB uses two ID systems:
1. **External IDs** (user-provided): `ontology:entityType:iri` format
   - Example: `pride:class:http://www.ebi.ac.uk/efo/EFO_0802869`
   - These work in query() and get()
2. **Internal IDs** (database auto-increment): integers 1 to 9,570,043
   - These appear to be what peek() tries to use
   - Possibly a mapping issue between internal and external IDs

### Segments
Two segments exist:
1. Vector segment (HNSW): `b3f185ec-a4d7-4d47-b309-9b4ac70cddf2`
2. Metadata segment (SQLite): `a384aa7b-2af8-47f8-bd9b-2319d681fbe2`

## Hypotheses (Unconfirmed)

1. **Index rebuild created inconsistency**: When HNSW index was deleted and rebuilt, internal ID mappings may not have been properly reconstructed
2. **peek() implementation issue**: peek() may use a different code path than query()/get() that relies on metadata not properly restored during index rebuild
3. **Segment synchronization issue**: The vector segment and metadata segment may have inconsistent state after index rebuild

## Workarounds

For applications that only need vector similarity search:
- Use `query()` instead of `peek()` for exploration
- Use `get(limit=N)` to retrieve arbitrary records

## Questions Needing Answers

1. How is `peek()` supposed to work internally? Does it use internal IDs or external IDs?
2. What is the expected behavior when an HNSW index is deleted and rebuilt?
3. Should index rebuild fully reconstruct all internal metadata, or does it rely on SQLite state?
4. Is there a ChromaDB integrity check command that can verify index/metadata consistency?
5. What is the proper way to rebuild a corrupted HNSW index without losing data?

## Next Steps

- [ ] Check ChromaDB version
- [ ] Search ChromaDB issue tracker for similar issues
- [ ] Run ChromaDB's built-in diagnostic tools (if any exist)
- [ ] Create minimal reproducible example
- [ ] Report to ChromaDB project if this is a bug

## Related Files

Test scripts in `notebooks/`:
- `diagnose_chromadb.py` - Initial diagnostic
- `debug_peek.py` - ID system investigation
- `check_id_mapping.py` - Internal database structure
- `find_bad_records.py` - Malformed record detection
- `fix_bad_records.py` - Attempted fix
- `test_peek_alternative.py` - Workaround validation
