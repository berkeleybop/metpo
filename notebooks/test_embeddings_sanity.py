#!/usr/bin/env python3
"""Test if the embeddings in ChromaDB actually make semantic sense."""

import chromadb
from chromadb.config import Settings
import openai
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
openai.api_key = os.getenv("OPENAI_API_KEY")

client = chromadb.PersistentClient(
    path='embeddings_chroma',
    settings=Settings(anonymized_telemetry=False)
)
collection = client.get_collection('ols_embeddings')

# Test 1: Search for something very specific that SHOULD exist
print("Test 1: Search for 'bacterial cell shape' - should return cell shape terms")
response = openai.embeddings.create(
    model="text-embedding-3-small",
    input="bacterial cell shape"
)
query_emb = response.data[0].embedding

results = collection.query(
    query_embeddings=[query_emb],
    n_results=5,
    include=["documents", "metadatas", "distances"]
)

print("Top 5 results:")
for i in range(5):
    print(f"  {i+1}. [{results['metadatas'][0][i]['ontologyId']}] {results['documents'][0][i][:100]}")
    print(f"     Distance: {results['distances'][0][i]:.3f}")

# Test 2: Search for "temperature"
print("\n\nTest 2: Search for 'temperature growth' - should return temperature-related terms")
response2 = openai.embeddings.create(
    model="text-embedding-3-small",
    input="temperature growth"
)
query_emb2 = response2.data[0].embedding

results2 = collection.query(
    query_embeddings=[query_emb2],
    n_results=5,
    include=["documents", "metadatas", "distances"]
)

print("Top 5 results:")
for i in range(5):
    print(f"  {i+1}. [{results2['metadatas'][0][i]['ontologyId']}] {results2['documents'][0][i][:100]}")
    print(f"     Distance: {results2['distances'][0][i]:.3f}")

# Test 3: What's in the database - sample random records
print("\n\nTest 3: Sample 10 random records from database")
import sqlite3
conn = sqlite3.connect('embeddings_chroma/chroma.sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT embedding_id, segment_id FROM embeddings ORDER BY RANDOM() LIMIT 10")
for eid, seg in cursor.fetchall():
    print(f"  {eid} (segment: {seg})")
conn.close()
