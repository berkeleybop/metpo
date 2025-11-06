# OLS Embeddings Vector Search - Problem Analysis

## Context

Using EBI OLS embeddings database (~288GB SQLite) documented at:
https://cthoyt.com/2025/08/04/ontology-text-embeddings.html

These embeddings power the "Similar classes/Similar entities" feature on OLS4:
https://www.ebi.ac.uk/ols4/ontologies/envo/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FENVO_00000428

## Requirements

**Immediate need:**
- Search 250 METPO terms against 27 ontologies (768K vectors currently migrated)

**Long-term goal:**
- General semantic search tool for all projects
- Search against all ~200 ontologies from OLS (~9.57M vectors)

## Scale Reality Check

**Full database:**
- Size: 288GB SQLite
- Vectors: 9.57 million embeddings
- Ontologies: 273
- Dimension: 1536 (text-embedding-3-small)

**Current subset (27 ontologies):**
- Vectors: 768K (8% of total)
- Observed RAM usage with Qdrant: 62GB
- Status: Crashes during index load

**Projected full dataset:**
- Estimated RAM needed: 750GB+ for HNSW index
- Conclusion: Will never work locally with HNSW-based vector DBs

## The Fundamental Problem

HNSW (Hierarchical Navigable Small World) indexes used by ChromaDB and Qdrant:
- Optimize for sub-second query speed
- Trade-off: Load entire index into RAM
- Designed for production servers with 128GB+ RAM
- Not suitable for local machines with large datasets

**Pattern observed:**
- Migration works (sequential writes, no index loaded)
- Querying fails (loads entire HNSW index, memory explosion)

## Three Paths Forward

### Option 1: Brute-Force Numpy (Recommended for immediate need)

**Approach:**
- Load vectors directly from SQLite into numpy arrays
- Compute cosine similarity using vectorized operations
- No approximate search, exact results

**Pros:**
- Memory efficient: ~5GB RAM for 768K vectors
- No migration needed
- Predictable performance
- Will actually work

**Cons:**
- Slower per query: 5-10 seconds each
- Total time for 250 queries: 20-40 minutes
- Not scalable to 9.57M vectors (would take hours per query)

**Best for:**
- One-time METPO reconciliation
- Queries against subset of ontologies

### Option 2: Faiss with Quantization

**Approach:**
- Use Facebook's Faiss library
- Product Quantization (PQ) or IVF+PQ indexes
- 4-8x memory compression

**Pros:**
- More memory efficient than HNSW
- Faster than brute-force
- Still approximate nearest neighbor

**Cons:**
- Another 4-hour migration
- Risk: might still exceed available RAM
- More complex to set up and tune

**Best for:**
- Medium-scale (1-2M vectors)
- If you need recurring queries

### Option 3: Cloud Vector Database

**Approach:**
- Qdrant Cloud or Pinecone
- Instance with 128GB+ RAM
- Upload full 288GB dataset

**Pros:**
- Handles full 9.57M vector dataset
- Fast queries (<100ms)
- Supports long-term use case across all projects

**Cons:**
- Cost: ~$200-500/month
- Upload time: hours to days for 288GB
- Network dependency

**Best for:**
- Long-term general semantic search tool
- All 200+ ontologies
- Multiple projects/users

## Recommendation

**For immediate METPO reconciliation:**
Use Option 1 (brute-force numpy). It's the fastest path to results that will actually work.

**For long-term vision (all ontologies, all projects):**
Either invest in cloud infrastructure (Option 3) or rethink the approach:
- Do you need all 9.57M vectors searchable simultaneously?
- Or can you search subsets by ontology/domain?
- Could you use OLS4 API directly for some use cases?

## Next Steps

1. Decide: One-time analysis or recurring tool?
2. If one-time: Write numpy brute-force script
3. If recurring: Evaluate cloud costs vs. alternatives
