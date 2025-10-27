
import chromadb
from chromadb.config import Settings

# Connect to ChromaDB
client = chromadb.PersistentClient(
    path="./metpo_relevant_chroma",
    settings=Settings(anonymized_telemetry=False)
)

collection = client.get_collection(name="metpo_relevant_embeddings")
print(f"Collection loaded: {collection.count():,} embeddings")

# Filter by specific ontology (e.g., only OBA terms)
results_oba = collection.get(
    where={"ontologyId": "oba"},  # Filter condition
    include=["documents", "metadatas"]
)

print(f"\nFound {len(results_oba['ids'])} OBA terms:\n")
for i in range(len(results_oba['ids'])):
    iri = results_oba['ids'][i]
    metadata = results_oba['metadatas'][i]
    document = results_oba['documents'][i]
    
    print(f"iri: {iri}")
    print(f"metadata: {metadata}")
    print(f"document: {document[:150]}...\n")
