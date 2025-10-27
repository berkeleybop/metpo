# METPO Undergraduate Engagement Plan

## Executive Summary

This plan provides a structured approach for Berkeley undergraduate students to contribute to METPO (Microbial Environmental and Trait Phenotype Ontology) development, focusing on high-quality class definitions and ontology alignment. The work supports METPO's submission to EBI OLS and presentation at ICBO 2025.

**Core Principle**: Follow the scientific method - change one thing at a time, document the result, and iterate.

## Goals

1. Create OBO Foundry-compliant definitions for METPO classes
2. Align METPO with related ontologies (OMP, PATO, MCO, ENVO) using SKOS mappings
3. Engage students with varied interests (software engineering, ML, knowledge management, microbiology)
4. Build sustainable workflows for ontology quality assurance
5. Prepare METPO for EBI OLS submission and ICBO 2025 presentation

## Background: Related Ontologies

### Ontology of Microbial Phenotypes (OMP)
- **Scope**: 1,880+ terms describing microbial phenotypes (morphology, growth, metabolism)
- **Structure**: Built on BFO and PATO foundations
- **Access**: OBO Foundry, BioPortal, SourceForge
- **Key feature**: Logical definitions supporting computational analysis
- **Overlap with METPO**: High - both describe microbial phenotypes

### Phenotype and Trait Ontology (PATO)
- **Scope**: Quality attributes that can be assigned to entities
- **Role**: Foundation ontology used by OMP and should inform METPO
- **Usage**: Describes qualities like "thermophilic" as distinct from entities like "thermophile"

### Microbial Conditions Ontology (MCO)
- **Scope**: Standardized vocabulary for microbial growth conditions
- **Focus**: Experimental conditions (temperature, pH, media, oxygen)
- **Origin**: E. coli K-12 gene regulation experiments at RegulonDB
- **Overlap with METPO**: Culture and growth conditions

### Environment Ontology (ENVO)
- **Scope**: Environmental terms including microbial habitats
- **Role**: Contextualizes where microbes live and what conditions they tolerate

## Semantic Similarity Strategy

**Key Innovation**: Use embedding-based semantic similarity to find related ontology terms beyond simple label matching.

**Two-Tier Approach**:

### Tier 1: OLS4 Embedding-Based Similarity (Preferred)
- **How it works**: OLS4 has projected all indexed ontology classes into embedding space
- **Advantage**: Finds semantically similar terms even with different labels (e.g., "thermophilic" finds "heat-loving" or "high-temperature growth")
- **Access**: Via OLS4 web interface (manual or browser automation)
- **Ontologies**: ENVO, PATO, and most OBO Foundry ontologies
- **Limitation**: Doesn't include OMP or MCO

### Tier 2: Custom Embeddings for BioPortal-Only Ontologies
- **Why needed**: OMP and MCO are only in BioPortal, not OLS4
- **Solution**: Build custom embedding index using:
  - Pre-trained biomedical models (BioSentVec, PubMedBERT) - free
  - OpenAI embeddings API - ~$0.01 for all target ontologies, best quality
  - ChromaDB or FAISS for fast similarity search
- **Process**: Download ontology from BioPortal → embed terms → query with METPO terms

**Combined Workflow**:
1. For PATO/ENVO terms: Use OLS4 embedding similarity (Tier 1)
2. For OMP/MCO terms: Use custom embeddings (Tier 2)
3. For all: Validate semantic alignment (entity vs quality distinction)

## Critical Issue: Entity vs Quality Distinction

**Problem**: Fuzzy label matching (and even embedding similarity) can conflate ontologically distinct concepts.

**Example**:
- METPO "thermophilic" (PATO:quality / BFO:realizable entity)
- vs OMP "thermophile" (PATO:material entity / BFO:organism)

These terms are semantically similar in embeddings space (high cosine similarity) but ontologically distinct!

**Solution**: Always validate semantic type after finding similar terms:
1. Search OLS/BioPortal for similar labels (or use embeddings)
2. Retrieve class definitions and parent classes
3. Check if term represents quality (PATO) vs entity (material)
4. Only create SKOS mapping if semantic types align
5. If mismatch, document the related-but-distinct term in notes

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────┐
│ 1. INVENTORY: Generate list of METPO classes needing work  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│ 2. SEARCH: Query OLS/BioPortal APIs for label matches      │
│    - Fuzzy search for similar terms                         │
│    - Prioritize: OMP > PATO > MCO > ENVO                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│ 3. VALIDATE: Check semantic alignment                       │
│    - Retrieve term definitions and parent classes            │
│    - Verify entity vs quality distinction                   │
│    - Check if term is phenotype-oriented                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
              ┌───────┴────────┐
              │                │
       ┌──────▼─────┐   ┌─────▼──────┐
       │ MATCH FOUND│   │ NO MATCH   │
       └──────┬─────┘   └─────┬──────┘
              │                │
┌─────────────▼────────┐  ┌────▼──────────────────────────────┐
│ 4a. MAP: Add SKOS    │  │ 4b. DEFINE: Write Aristotelian    │
│     - exactMatch     │  │     definition                      │
│     - closeMatch     │  │     - "An A is a B that C"         │
│     - broadMatch     │  │     - Use IAO_0000115              │
│     - narrowMatch    │  │     - Cite sources (IAO_0000119)   │
└─────────────┬────────┘  └────┬──────────────────────────────┘
              │                │
              └────────┬───────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│ 5. DOCUMENT: Record decision in metpo-kgm-studio            │
│    - Prompt used                                             │
│    - Response/decision                                       │
│    - Source citations                                        │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│ 6. UPDATE: Modify METPO ROBOT template                      │
│    - Add definition or mapping                               │
│    - Update one row at a time                                │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│ 7. BUILD & VALIDATE: Run ROBOT and check output             │
│    - robot template --template metpo.tsv                     │
│    - robot reason --reasoner ELK                             │
│    - Check for errors                                        │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│ 8. REVIEW: Git workflow                                     │
│    - Create branch                                           │
│    - Commit one logical change                               │
│    - PR with clear description                               │
└──────────────────────────────────────────────────────────────┘
```

## Detailed Task Descriptions

### Task 1: Generate Inventory

**Goal**: Identify METPO classes that need definitions or ontology alignment.

**Tools**:
- ROBOT query
- Python/pandas for analysis
- OAK (Ontology Access Kit)

**Process**:
```bash
# Find classes without definitions
robot query --input metpo.owl \
  --query queries/missing-definitions.rq \
  --output results/classes-need-definitions.tsv

# Find classes without mappings to OMP/PATO
oak -i metpo.owl relationships --predicates skos:exactMatch,skos:closeMatch \
  > results/existing-mappings.txt
```

**Output**: TSV with columns:
- class_id
- class_label
- has_definition (boolean)
- has_omp_mapping (boolean)
- has_pato_mapping (boolean)
- has_mco_mapping (boolean)
- priority (high/medium/low)

**Student roles**:
- **Software Engineering**: Write ROBOT query scripts
- **Data Science**: Analyze gaps and prioritize
- **Microbiology**: Validate priority rankings based on importance

### Task 2: Search OLS/BioPortal APIs

**Goal**: Find existing ontology terms that match or closely relate to METPO labels.

**APIs**:

**OLS4 API** (https://www.ebi.ac.uk/ols4/api/)
- Endpoint: `/api/search?q={query}&ontology={ontology}&exact=false`
- Returns: label, definition, IRI, ontology, type
- **NEW: Semantic Similarity via Embeddings**
  - OLS4 has projected ontology classes into embedding space
  - Each OLS4 class page shows "Similar classes" and "Similar entities"
  - Example: https://www.ebi.ac.uk/ols4/ontologies/envo/classes/[encoded-IRI]
  - **Advantage**: Finds semantically similar terms even with different labels
  - **Limitation**: Only works for ontologies available in OLS4

**BioPortal API** (https://data.bioontology.org/documentation)
- Endpoint: `/search?q={query}&ontologies={OMP,PATO,MCO,ENVO}&require_exact_match=false`
- Parameters:
  - `require_definitions=true` (only return terms with definitions)
  - `also_search_properties=false`
  - `include=prefLabel,definition,properties,parents`
- **Note**: No native embedding-based similarity API
- **Workaround**: Use external embeddings (see Task 2b below)

**Coverage Differences**:
- **OLS4**: ENVO, PATO, many OBO Foundry ontologies
- **BioPortal**: OMP, MCO, plus many ontologies NOT in OLS4
- **Strategy**: Search both, use embedding-based similarity when available

**Search Strategy**:
1. Search for exact label match first (both APIs)
2. If in OLS4: Use "Similar classes" feature for semantic matches
3. If only in BioPortal: Use fuzzy string search + external embeddings
4. Prioritize ontologies: OMP > PATO > MCO > ENVO
5. Retrieve top 10 results for manual review

**Python Example**:
```python
import requests

def search_ols(label, ontology=None):
    """Search OLS4 for term by label"""
    base_url = "https://www.ebi.ac.uk/ols4/api/search"
    params = {
        "q": label,
        "exact": "false",
        "rows": 10
    }
    if ontology:
        params["ontology"] = ontology

    response = requests.get(base_url, params=params)
    return response.json()

def search_bioportal(label, ontologies=["OMP", "PATO", "MCO", "ENVO"],
                     api_key="YOUR_KEY"):
    """Search BioPortal for term by label"""
    base_url = "https://data.bioontology.org/search"
    params = {
        "q": label,
        "ontologies": ",".join(ontologies),
        "require_exact_match": "false",
        "require_definitions": "true",
        "include": "prefLabel,definition,properties,parents"
    }
    headers = {"Authorization": f"apikey token={api_key}"}

    response = requests.get(base_url, params=params, headers=headers)
    return response.json()

# Usage
results_ols = search_ols("thermophilic", ontology="PATO")
results_bp = search_bioportal("thermophilic")
```

**Output**: TSV with columns:
- metpo_label
- match_label
- match_iri
- match_ontology
- match_definition
- similarity_score (manual 1-5 rating)
- notes

**Student roles**:
- **Software Engineering**: Build API clients, batch processing
- **Machine Learning**: Implement semantic similarity scoring beyond simple fuzzy matching
- **Knowledge Management**: Design data capture schema

### Task 2b: Semantic Similarity for BioPortal-Only Ontologies

**Goal**: Implement embedding-based semantic similarity for ontologies not available in OLS4 (e.g., OMP, MCO).

**Problem**: OLS4's "Similar classes" feature only works for ontologies indexed in OLS4. Several important ontologies (OMP, MCO) are only in BioPortal.

**Solution**: Build custom embedding-based similarity using pre-trained biomedical models or OpenAI embeddings.

**Approach 1: Pre-trained Biomedical Embeddings**

Use models trained on biomedical text:
- **BioWordVec**: Subword embeddings trained on PubMed + MIMIC-III
- **BioSentVec**: Sentence-level embeddings for biomedical text
- **PubMedBERT**: BERT model pre-trained on PubMed abstracts

**Workflow**:
```python
# 1. Download ontology terms from BioPortal
# 2. Generate embeddings for all term labels + definitions
# 3. Index embeddings in vector database (FAISS, ChromaDB)
# 4. Query with METPO term to find nearest neighbors

from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load biomedical embedding model
model = SentenceTransformer('pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb')

def embed_ontology_terms(bioportal_terms):
    """
    Generate embeddings for BioPortal terms

    Args:
        bioportal_terms: List of dicts with 'label', 'definition', 'iri'

    Returns:
        Dict mapping IRI to embedding vector
    """
    embeddings = {}

    for term in bioportal_terms:
        # Combine label and definition for richer semantic representation
        text = f"{term['label']}. {term['definition']}"
        embedding = model.encode(text)
        embeddings[term['iri']] = {
            'vector': embedding,
            'label': term['label'],
            'definition': term['definition'],
            'ontology': term['ontology']
        }

    return embeddings

def find_similar_terms(metpo_label, metpo_definition, ontology_embeddings, top_k=10):
    """
    Find most semantically similar terms using cosine similarity

    Args:
        metpo_label: METPO term label
        metpo_definition: METPO term definition (if exists)
        ontology_embeddings: Dict from embed_ontology_terms
        top_k: Number of results to return

    Returns:
        List of (iri, label, similarity_score) tuples
    """
    # Generate query embedding
    query_text = f"{metpo_label}. {metpo_definition}" if metpo_definition else metpo_label
    query_embedding = model.encode(query_text)

    # Calculate similarities
    results = []
    for iri, data in ontology_embeddings.items():
        similarity = cosine_similarity(
            query_embedding.reshape(1, -1),
            data['vector'].reshape(1, -1)
        )[0][0]

        results.append({
            'iri': iri,
            'label': data['label'],
            'definition': data['definition'],
            'ontology': data['ontology'],
            'similarity': float(similarity)
        })

    # Sort by similarity (descending)
    results.sort(key=lambda x: x['similarity'], reverse=True)

    return results[:top_k]

# Example usage
omp_terms = fetch_bioportal_ontology('OMP')  # Fetch all OMP terms
omp_embeddings = embed_ontology_terms(omp_terms)

# Find terms similar to "thermophilic"
similar = find_similar_terms(
    metpo_label="thermophilic",
    metpo_definition="A quality of an organism that exhibits optimal growth at high temperatures",
    ontology_embeddings=omp_embeddings,
    top_k=10
)

for result in similar:
    print(f"{result['similarity']:.3f} | {result['label']} ({result['iri']})")
    print(f"       {result['definition'][:100]}...")
    print()
```

**Approach 2: OpenAI Embeddings API**

Use commercial API for state-of-the-art embeddings:
```python
import openai
import numpy as np

# Requires API key: export OPENAI_API_KEY="sk-..."
client = openai.OpenAI()

def get_openai_embedding(text, model="text-embedding-3-small"):
    """
    Get embedding from OpenAI API

    Args:
        text: Text to embed
        model: Model name (text-embedding-3-small or text-embedding-3-large)

    Returns:
        Embedding vector (numpy array)
    """
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return np.array(response.data[0].embedding)

def batch_embed_ontology(terms, model="text-embedding-3-small", batch_size=100):
    """
    Batch embed ontology terms (more efficient, reduces API calls)

    Args:
        terms: List of term dicts
        model: OpenAI model name
        batch_size: Terms per API call (max 2048)

    Returns:
        Dict mapping IRI to embedding
    """
    embeddings = {}

    # Prepare texts
    texts = []
    iris = []
    for term in terms:
        text = f"{term['label']}. {term['definition']}"
        texts.append(text)
        iris.append(term['iri'])

    # Batch API calls
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_iris = iris[i:i+batch_size]

        response = client.embeddings.create(
            input=batch_texts,
            model=model
        )

        for j, embedding_data in enumerate(response.data):
            iri = batch_iris[j]
            embeddings[iri] = {
                'vector': np.array(embedding_data.embedding),
                'label': terms[i+j]['label'],
                'definition': terms[i+j]['definition'],
                'ontology': terms[i+j]['ontology']
            }

    return embeddings

# Cost estimation for text-embedding-3-small:
# - $0.02 / 1M tokens
# - Average ontology term ~100 tokens (label + definition)
# - OMP ~1,880 terms = ~188,000 tokens = $0.004 (less than half a cent)
```

**Approach 3: Vector Database for Scale**

For production use with multiple ontologies:
```python
import chromadb
from chromadb.config import Settings

# Initialize ChromaDB (local vector database)
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./metpo_ontology_embeddings"
))

# Create collection
collection = client.create_collection(
    name="bioportal_ontologies",
    metadata={"description": "Embeddings for OMP, MCO, and other BioPortal ontologies"}
)

def index_ontology_in_chromadb(collection, terms, embedding_function):
    """
    Add ontology terms to ChromaDB collection

    Args:
        collection: ChromaDB collection
        terms: List of term dicts
        embedding_function: Function to generate embeddings
    """
    documents = []
    metadatas = []
    ids = []

    for term in terms:
        text = f"{term['label']}. {term['definition']}"
        documents.append(text)

        metadatas.append({
            'iri': term['iri'],
            'label': term['label'],
            'ontology': term['ontology'],
            'definition': term['definition']
        })

        # Use IRI as unique ID
        ids.append(term['iri'])

    # ChromaDB handles embedding generation automatically
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

def search_chromadb(collection, metpo_label, metpo_definition=None, top_k=10):
    """
    Search ChromaDB for similar terms
    """
    query_text = f"{metpo_label}. {metpo_definition}" if metpo_definition else metpo_label

    results = collection.query(
        query_texts=[query_text],
        n_results=top_k
    )

    return results

# Usage
omp_terms = fetch_bioportal_ontology('OMP')
index_ontology_in_chromadb(collection, omp_terms, model.encode)

# Search
results = search_chromadb(collection, "thermophilic", top_k=10)
```

**Recommended Strategy**:

1. **For exploration/prototyping**: Use BioSentVec or PubMedBERT (free, good quality)
2. **For production**: Use OpenAI embeddings (cost ~$0.01 for all target ontologies, best quality)
3. **For scale**: Index in ChromaDB or FAISS (enables fast nearest-neighbor search)

**Student Deliverables**:
- Python module for embedding-based search
- Pre-computed embeddings for OMP and MCO (cached in repo)
- Jupyter notebook comparing embedding models
- Integration with main search tool

**Student roles**:
- **Machine Learning**: Lead - select models, tune parameters, evaluate quality
- **Software Engineering**: Build indexing pipeline, integrate with search tool
- **Knowledge Management**: Validate that semantic similarity aligns with ontological similarity

### Task 3: Validate Semantic Alignment

**Goal**: Ensure matched terms represent the same ontological type (quality vs entity).

**Critical Checks**:

1. **Entity Type Check**
   - Retrieve parent classes using OLS/BioPortal
   - METPO phenotypes should map to PATO qualities or BFO realizable entities
   - Reject mappings to material entities (organisms, substances)

2. **Definition Analysis**
   - Read definition text
   - Check for quality language ("having property X", "characterized by Y")
   - vs entity language ("organism that...", "bacterium with...")

3. **Use Case Validation**
   - Would this mapping make sense in kg-microbe extraction?
   - Does it support the phenotype-centric use case?

**Python Example**:
```python
def get_term_parents(term_iri, ontology):
    """Get parent classes from OLS"""
    # URL encode the IRI
    encoded_iri = requests.utils.quote(term_iri, safe='')
    url = f"https://www.ebi.ac.uk/ols4/api/ontologies/{ontology}/terms/{encoded_iri}/parents"
    response = requests.get(url)
    return response.json()

def is_quality_term(term_iri, ontology):
    """Check if term is a quality (PATO) vs entity"""
    parents = get_term_parents(term_iri, ontology)

    quality_indicators = [
        "PATO_0000001",  # quality
        "BFO_0000020",   # specifically dependent continuant
        "BFO_0000017"    # realizable entity
    ]

    entity_indicators = [
        "BFO_0000040",   # material entity
        "NCBITaxon_1",   # organism
    ]

    # Check if any parent matches quality indicators
    # vs entity indicators
    # Return boolean + confidence score
```

**Decision Matrix**:

| METPO Type | Match Type | Parent Classes | Decision |
|------------|-----------|----------------|----------|
| Phenotype | Quality | PATO, BFO:realizable | ✅ CREATE MAPPING |
| Phenotype | Entity | BFO:material, NCBITaxon | ❌ REJECT - Document as related |
| Phenotype | Quality | Unknown ontology | ⚠️  REVIEW - Check definition text |
| Phenotype | Process | BFO:process | ⚠️  REVIEW - May be acceptable |

**Output**: Updated TSV with additional columns:
- match_type (quality/entity/process/unknown)
- parent_classes (list)
- semantic_alignment (aligned/misaligned/uncertain)
- decision (map/reject/review)
- rationale (text explanation)

**Student roles**:
- **Microbiology**: Review uncertain cases, validate biological meaning
- **Knowledge Management**: Apply ontology design patterns, check BFO alignment
- **Software Engineering**: Automate parent class retrieval and type checking

### Task 4a: Create SKOS Mappings

**Goal**: Link METPO classes to existing ontology terms using appropriate SKOS predicates.

**SKOS Mapping Types**:

| Predicate | Use When | Example |
|-----------|----------|---------|
| `skos:exactMatch` | Terms are interchangeable, same meaning in all contexts | METPO "Gram-negative" → PATO "Gram-negative" |
| `skos:closeMatch` | Terms are highly similar but may differ in subtle ways | METPO "thermophilic" → OMP "thermophilic organism phenotype" |
| `skos:broadMatch` | METPO term is more specific than matched term | METPO "extreme thermophile" → PATO "thermophilic" |
| `skos:narrowMatch` | METPO term is more general than matched term | METPO "motile" → OMP "flagellar motility" |
| `skos:relatedMatch` | Terms are related but not hierarchically | METPO "halophilic" → ENVO "hypersaline environment" |

**ROBOT Template Format**:

The mappings go in dedicated columns in the ROBOT template:

```tsv
ID	Label	skos:exactMatch	skos:closeMatch	SPLIT=|
METPO:0000001	thermophilic	PATO:0002078
METPO:0000002	halophilic		OMP:0005507|PATO:0001627
```

**Quality Standards**:
- Always include mapping source annotation: `IAO:0000119 "Mapped via OLS search 2025-10-24"`
- Document confidence level in notes column
- Never guess - if uncertain, leave for review

**Student Workflow**:
1. Open METPO ROBOT template (TSV)
2. Find row for target class
3. Add mapping IRI to appropriate SKOS column
4. Add source annotation to notes
5. Save and commit (one class at a time)

**Student roles**:
- **Knowledge Management**: Lead - understand SKOS semantics, make mapping decisions
- **Microbiology**: Validate biological equivalence
- **All**: Can execute once decision is made

### Task 4b: Write Aristotelian Definitions

**Goal**: Create OBO Foundry-compliant textual definitions for classes without suitable mappings.

**Aristotelian Form**: "An A is a B that C"
- A = term being defined (genus)
- B = parent class
- C = differentia (what makes it distinct)

**OBO Foundry Requirements** (FP-006):

1. **Use IAO_0000115 for definitions**
   ```
   IAO:0000115 "A quality of an organism that..."
   ```

2. **Include definition source (IAO_0000119)**
   ```
   IAO:0000119 "Based on BacDive keyword analysis and BactoTraits data"
   ```

3. **Follow patterns**:
   - Quality: "A quality inhering in a bearer by virtue of..."
   - Disposition: "A disposition to..."
   - Role: "A role that is realized when..."

**Examples**:

**Good**:
```
thermophilic
Definition: "A quality of an organism that exhibits optimal growth at temperatures between 45°C and 80°C."
Source: "BacDive culture temperature data analysis"
```

**Bad** (circular):
```
thermophilic
Definition: "Being thermophilic" ❌
```

**Bad** (empty):
```
thermophilic
Definition: "Related to temperature" ❌
```

**Bad** (wrong form):
```
thermophilic
Definition: "Organisms that grow at high temperatures" ❌
(This defines "thermophile" not "thermophilic")
```

**Process**:
1. Research the concept:
   - Check BacDive documentation
   - Review BactoTraits papers
   - Search literature if needed
2. Identify parent class (usually PATO quality)
3. Write differentia (what distinguishes it)
4. Format in Aristotelian form
5. Add citations

**ROBOT Template Format**:
```tsv
ID	Label	IAO:0000115	IAO:0000119
METPO:0000001	thermophilic	A quality of an organism that exhibits optimal growth at temperatures between 45°C and 80°C.	BacDive culture temperature data analysis (2025-10-24)
```

**Student roles**:
- **Microbiology**: Lead - understand biological concepts, find authoritative sources
- **Knowledge Management**: Review for ontology design pattern compliance
- **All**: Can draft definitions once trained

### Task 5: Document in metpo-kgm-studio

**Goal**: Create transparent record of all ontology development decisions.

**What to Document**:
- Query/prompt used to search for terms
- Search results (top matches)
- Reasoning for mapping decision or definition choice
- Source citations
- Date and author

**metpo-kgm-studio Format**:

Each decision gets a markdown file:
```
metpo-kgm-studio/
├── mapping-decisions/
│   ├── 2025-10-24-thermophilic-mapping.md
│   ├── 2025-10-24-halophilic-definition.md
└── queries/
    ├── ols-thermophilic-search.json
    └── bioportal-halophilic-search.json
```

**Template**:
```markdown
# [METPO Class Label] - [Mapping/Definition Decision]

**Date**: 2025-10-24
**Author**: @username
**METPO ID**: METPO:0000001
**METPO Label**: thermophilic

## Search Process

### Query
- Search term: "thermophilic"
- APIs: OLS4, BioPortal
- Ontologies: OMP, PATO, MCO
- Date: 2025-10-24

### Results
1. PATO:0002078 "thermophilic"
   - Definition: "A quality inhering in an organism by virtue of the
     organism's disposition to thrive at relatively high temperatures,
     between 45 and 122 degrees Celsius."
   - Parents: PATO:0000146 (temperature)
   - Ontology: PATO

2. OMP:0005508 "thermophilic organism phenotype"
   - Definition: "A phenotype of being thermophilic"
   - Parents: OMP:0000001
   - Ontology: OMP

### Validation
- PATO:0002078 is a PATO quality ✓
- Definition uses "quality inhering in" pattern ✓
- Semantic type: quality (not entity) ✓
- Temperature range matches BacDive validation (45-80°C) ✓

## Decision

**MAPPING**: skos:exactMatch to PATO:0002078

**Rationale**:
- Exact semantic alignment (quality)
- Definition matches our BacDive validation
- PATO is foundational ontology for qualities
- Temperature range is consistent

**Alternative considered**: OMP:0005508
- Rejected because: Circular definition, less precise

## Implementation

```tsv
ID	Label	skos:exactMatch	IAO:0000119
METPO:0000001	thermophilic	PATO:0002078	Mapped via OLS search on 2025-10-24
```

## Sources
- PATO via OLS4: https://www.ebi.ac.uk/ols4/ontologies/pato/classes?iri=...
- BacDive temperature validation: docs/bacdive_culture_temp_analysis.md
```

**Student roles**:
- **All**: Everyone documents their own work
- **Knowledge Management**: Review documentation for completeness
- **Software Engineering**: Build templates and automation

### Task 6: Update METPO ROBOT Template

**Goal**: Make atomic changes to METPO source files.

**Critical Rule**: ONE CLASS PER COMMIT

**Process**:
1. Open ROBOT template TSV in text editor
2. Find row for target class (by ID or label)
3. Make ONE of:
   - Add definition to IAO:0000115 column
   - Add mapping to skos:exactMatch (or closeMatch, etc.) column
   - Add source to IAO:0000119 column
4. Save file
5. Proceed to Task 7 (validate)

**Git Workflow**:
```bash
# Create branch
git checkout -b add-thermophilic-mapping

# Make change (edit one row)
nano src/templates/metpo.tsv

# Stage
git add src/templates/metpo.tsv

# Commit with descriptive message
git commit -m "Add PATO mapping for thermophilic (METPO:0000001)

- Maps to PATO:0002078 (thermophilic quality)
- Source: OLS search validated against BacDive data
- Decision documented in metpo-kgm-studio/mapping-decisions/2025-10-24-thermophilic-mapping.md"

# DO NOT PUSH YET - validate first (Task 7)
```

**Student roles**:
- **All**: Can edit TSV once trained on git workflow
- **Software Engineering**: Help with git issues, review PRs

### Task 7: Build & Validate

**Goal**: Ensure changes don't break METPO ontology.

**ROBOT Build Process**:
```bash
# 1. Convert template to OWL
make build

# This runs:
# robot template --template src/templates/metpo.tsv \
#   --input-iri http://purl.obolibrary.org/obo/bfo.owl \
#   --output metpo.owl

# 2. Run reasoner to check consistency
robot reason --input metpo.owl \
  --reasoner ELK \
  --output metpo-reasoned.owl

# 3. Validate against OBO standards
robot report --input metpo.owl \
  --output reports/metpo-validation.txt \
  --fail-on ERROR
```

**What to Check**:
1. **Build succeeds without errors**
   - No template syntax errors
   - All IRIs are valid
   - No duplicate IDs

2. **Reasoner succeeds**
   - No unsatisfiable classes
   - No inconsistencies

3. **Validation passes**
   - No missing labels
   - No missing definitions (if required)
   - IRIs follow OBO format

**If Errors Occur**:
1. Read error message carefully
2. Fix the specific issue
3. Amend the commit: `git commit --amend`
4. Rebuild and validate again
5. Repeat until clean

**Success Criteria**:
```
✓ Template conversion: SUCCESS
✓ Reasoner: No inconsistencies
✓ Validation: 0 errors
```

**Now Safe to Push**:
```bash
git push -u origin add-thermophilic-mapping
```

**Student roles**:
- **Software Engineering**: Lead - debug build errors, maintain CI
- **All**: Must learn to run validation before pushing

### Task 8: Review & Merge

**Goal**: Peer review and integrate changes into main branch.

**Pull Request Template**:
```markdown
## Summary
Add PATO mapping for thermophilic class (METPO:0000001)

## Changes
- Added skos:exactMatch to PATO:0002078
- Added source annotation citing OLS search

## Decision Documentation
See: metpo-kgm-studio/mapping-decisions/2025-10-24-thermophilic-mapping.md

## Validation
- ✅ ROBOT build passes
- ✅ Reasoner check passes
- ✅ OBO validation passes

## Checklist
- [x] One logical change only
- [x] Decision documented in metpo-kgm-studio
- [x] Source citation included
- [x] Build validation passes
- [x] Follows OBO Foundry principles
```

**Review Checklist**:

**For Mappings**:
- [ ] SKOS predicate is appropriate (exact vs close vs broad)
- [ ] Semantic alignment validated (quality vs entity)
- [ ] Target ontology term has definition
- [ ] Source citation included
- [ ] Decision documented

**For Definitions**:
- [ ] Follows Aristotelian form "An A is a B that C"
- [ ] Not circular ("thermophilic means being thermophilic")
- [ ] Not empty or vague
- [ ] Cites authoritative source
- [ ] Uses appropriate OBO relations

**For Both**:
- [ ] Single class changed (atomic commit)
- [ ] ROBOT build passes
- [ ] No merge conflicts

**Student roles**:
- **Knowledge Management**: Review semantic correctness
- **Microbiology**: Review biological accuracy
- **Software Engineering**: Review technical correctness (git, ROBOT, syntax)
- **All**: Learn from reviewing others' work

## Student Engagement by Interest Area

### Software Engineering Students

**Primary Tasks**:
1. Build API clients for OLS4 and BioPortal
2. Automate term search and retrieval
3. Create batch processing scripts
4. Maintain CI/CD for ROBOT builds
5. Debug ontology build errors
6. Develop web UI for non-technical students

**Skills Developed**:
- REST API integration
- Python programming
- Git workflow
- Shell scripting
- Ontology tooling (ROBOT, OAK)

**Example Projects**:
- **OLS/BioPortal Search Tool**: CLI that searches both APIs, ranks results, retrieves parent classes
- **METPO QA Dashboard**: Web UI showing classes needing definitions/mappings with search interface
- **Automated Validation**: GitHub Action that runs ROBOT checks on every PR

**Deliverables**:
- Python package for ontology search
- CI/CD pipeline configuration
- Documentation for other students

### Machine Learning Students

**Primary Tasks**:
1. Semantic similarity scoring beyond fuzzy string matching
2. Term clustering to find groups needing similar definitions
3. Definition quality assessment
4. Automated mapping suggestion (with human review)
5. BacDive data analysis for term validation

**Skills Developed**:
- NLP (embeddings, similarity metrics)
- Classification models
- Feature engineering from ontology metadata
- Data mining

**Example Projects**:
- **Semantic Similarity Scorer**: Use BERT embeddings to score METPO-to-OMP label matches beyond string similarity
- **Definition Quality Checker**: Model trained on good vs bad definitions to flag issues
- **Cluster Analysis**: Group METPO classes by semantic similarity to find patterns

**Deliverables**:
- Similarity scoring module integrated into search tool
- Analysis reports on METPO coverage gaps
- Quality metrics dashboard

### Knowledge Management Students

**Primary Tasks**:
1. Lead SKOS mapping decisions
2. Review definitions for OBO compliance
3. Design documentation standards
4. Maintain metpo-kgm-studio records
5. Cross-ontology pattern analysis
6. Train other students on ontology principles

**Skills Developed**:
- Ontology design patterns
- OBO Foundry principles
- SKOS vocabulary
- Information architecture
- Scientific documentation

**Example Projects**:
- **Mapping Decision Framework**: Formalize criteria for exact vs close vs broad matches
- **Definition Pattern Library**: Catalog reusable patterns for METPO classes
- **Quality Guidelines**: Write comprehensive style guide for METPO contributions

**Deliverables**:
- METPO contribution guidelines document
- Decision pattern library
- Training materials for new students

### Microbiology Students

**Primary Tasks**:
1. Validate biological accuracy of definitions
2. Research microbial phenotypes in literature
3. Review uncertain semantic alignments
4. Prioritize classes by biological importance
5. Connect METPO to experimental use cases
6. Provide domain expertise on ambiguous terms

**Skills Developed**:
- Literature research
- Phenotype characterization
- Data curation
- Scientific writing
- Ontology application to real data

**Example Projects**:
- **Phenotype Literature Review**: For top 50 priority classes, find authoritative definitions from textbooks/papers
- **Use Case Validation**: Check if METPO terms align with actual BacDive/BactoTraits data usage in kg-microbe
- **Priority Ranking**: Order classes by biological significance for ICBO presentation

**Deliverables**:
- Annotated bibliography for METPO domains
- Use case documentation
- Biological validation reports

## Tools & Resources

### Required Tools

**Ontology Tools**:
- **ROBOT**: Ontology manipulation (template, merge, reason, validate)
  - Install: https://robot.obolibrary.org/
- **OAK** (Ontology Access Kit): Query and analysis
  - Install: `pip install oaklib`
- **Protégé**: Visual ontology editor (optional, for exploration)

**Programming**:
- **Python 3.9+**: API clients, data analysis
- **pandas**: Data manipulation
- **requests**: HTTP API calls
- **rdflib**: RDF/OWL parsing if needed

**Version Control**:
- **Git**: Required for all students
- **GitHub**: Pull requests, issues, project boards

**APIs**:
- **OLS4 API**: https://www.ebi.ac.uk/ols4/api/
- **BioPortal API**: https://data.bioontology.org/documentation
  - Requires free API key: https://bioportal.bioontology.org/accounts/new

### Learning Resources

**OBO Foundry Principles**:
- FP-006 Textual Definitions: http://obofoundry.org/principles/fp-006-textual-definitions.html
- FP-007 Relations Reuse: http://obofoundry.org/principles/fp-007-relations.html
- FP-012 Naming Conventions: http://obofoundry.org/principles/fp-012-naming-conventions.html

**Ontology Tutorials**:
- OBO Academy: https://oboacademy.github.io/obook/
- ROBOT Tutorial: https://robot.obolibrary.org/tutorial
- OAK Tutorial: https://incatools.github.io/ontology-access-kit/

**Related Ontologies**:
- OMP (Ontology of Microbial Phenotypes): https://bioportal.bioontology.org/ontologies/OMP
- PATO (Phenotype and Trait Ontology): https://www.ebi.ac.uk/ols4/ontologies/pato
- MCO (Microbial Conditions Ontology): https://bioportal.bioontology.org/ontologies/MCO
- ENVO (Environment Ontology): https://www.ebi.ac.uk/ols4/ontologies/envo

**BacDive Analysis**:
- See docs/ directory in this repository:
  - `bacdive_keywords_inventory.tsv`
  - `bacdive_keywords_key_findings.md`
  - `bacdive_culture_temp_analysis.md`
  - `kg_microbe_bacdive_implementation_analysis.md`

## Quality Assurance

### Definition Quality Checklist

**Format**:
- [ ] Follows Aristotelian form: "An A is a B that C"
- [ ] Uses IAO:0000115 annotation
- [ ] Includes source (IAO:0000119)
- [ ] No circular definitions
- [ ] Not vague or empty

**Content**:
- [ ] Scientifically accurate (verified by microbiology student)
- [ ] Uses appropriate ontology design pattern
- [ ] References authoritative sources
- [ ] Appropriate level of specificity

**Integration**:
- [ ] Consistent with related METPO terms
- [ ] Aligned with parent class definition
- [ ] Uses standard OBO relations

### Mapping Quality Checklist

**Search**:
- [ ] Searched both OLS and BioPortal
- [ ] Checked top 10 results
- [ ] Documented search process

**Validation**:
- [ ] Retrieved parent classes
- [ ] Verified semantic type (quality vs entity)
- [ ] Checked definition compatibility
- [ ] Confirmed not deprecated/obsolete

**SKOS Selection**:
- [ ] Correct predicate (exact vs close vs broad)
- [ ] Target has definition
- [ ] Source citation included
- [ ] Rationale documented

**Review**:
- [ ] Approved by knowledge management student
- [ ] Approved by microbiology student (if domain-specific)

## Project Management

### Sprint Structure (2-week cycles)

**Week 1 - Individual Work**:
- Day 1-2: Generate inventory, assign classes to students
- Day 3-8: Students work independently on search/define/map tasks
- Day 9-10: Document decisions, prepare PRs

**Week 2 - Review & Integration**:
- Day 1-3: Peer review PRs
- Day 4-5: Address feedback, iterate
- Day 6-7: Merge approved changes
- Day 8-9: Build complete METPO, run validation
- Day 10: Sprint retrospective, plan next sprint

### Weekly Meetings

**Monday (1 hour)** - Status & Planning:
- Review last week's progress
- Discuss blockers
- Assign new classes
- Technical Q&A

**Thursday (1 hour)** - Review Session:
- Peer review 3-5 PRs as group
- Discuss difficult cases
- Share lessons learned
- Knowledge management training

**Friday (30 min, optional)** - Office Hours:
- One-on-one help with students
- Debug technical issues
- Career mentoring

### Communication Channels

**Slack/Discord**:
- #general: Announcements, general discussion
- #technical: Git issues, ROBOT errors, API problems
- #ontology-questions: Semantic alignment, definition help
- #biology: Domain expertise, literature help
- #random: Team building

**GitHub**:
- Issues: Track individual classes needing work
- Projects: Sprint board with columns:
  - Backlog
  - In Progress
  - Review
  - Done
- Discussions: Design decisions, policy questions

### Progress Tracking

**Metrics to Track**:
- Classes with definitions: X / total
- Classes with mappings: X / total
- PRs opened this sprint: X
- PRs merged this sprint: X
- Contributors active this sprint: X

**Visualization**:
- GitHub Project board
- Weekly progress chart
- Coverage heat map (which domains well-covered vs gaps)

## Timeline to ICBO 2025

Assuming 6-month timeline (November 2025 - April 2026):

**Phase 1 (Month 1-2): Foundation**
- Set up infrastructure (APIs, tools, CI)
- Train all students on workflow
- Complete first 50 classes (high priority)
- Establish documentation patterns

**Phase 2 (Month 3-4): Scale**
- Process 200 classes total
- Students work independently
- Refine quality processes
- Build automation tools

**Phase 3 (Month 5): Polish**
- Complete 400+ classes
- Address all validation errors
- Write ICBO abstract
- Prepare submission to EBI OLS

**Phase 4 (Month 6): Publication**
- Submit to EBI OLS (April target)
- Finalize ICBO presentation
- Write documentation for external users
- Celebrate!

**Milestones**:
- Month 1: First 50 classes complete, all students trained
- Month 2: API tools functional, process documented
- Month 3: 200 classes complete, submit ICBO abstract
- Month 4: 400 classes complete, validation clean
- Month 5: EBI OLS submission ready
- Month 6: ICBO presentation delivered

## Success Criteria

**Quantitative**:
- ≥80% of METPO classes have OBO-compliant definitions
- ≥60% of METPO classes have SKOS mappings to related ontologies
- 100% of commits follow one-class-per-commit rule
- 100% of merged PRs pass ROBOT validation
- ≥90% of decisions documented in metpo-kgm-studio

**Qualitative**:
- METPO accepted by EBI OLS
- Positive feedback from ICBO reviewers
- Students can articulate OBO Foundry principles
- Students feel confident contributing to ontologies
- Sustainable workflow for future METPO maintenance

## Risks & Mitigations

### Risk: Students focus on quantity over quality

**Mitigation**:
- Emphasize "change one thing, document, iterate"
- Reject PRs that skip documentation or validation
- Celebrate good work examples in meetings
- Make quality visible in metrics

### Risk: Confusion between entity and quality terms

**Mitigation**:
- Clear training on BFO upper level ontology
- Mandatory validation step in workflow
- Knowledge management student review required
- Document common mistakes and how to avoid

### Risk: Students overwhelmed by ontology complexity

**Mitigation**:
- Start with simple, clear-cut classes
- Pair students (experienced + new)
- Office hours for one-on-one help
- Build abstraction layers (tools hide complexity)

### Risk: API rate limits or downtime

**Mitigation**:
- Cache API responses locally
- Respect rate limits in scripts
- Use both OLS and BioPortal (redundancy)
- Local ontology files as backup

### Risk: Git conflicts and merge issues

**Mitigation**:
- One class per commit rule (reduces conflicts)
- Merge frequently (don't let PRs sit)
- Software engineering students help others
- Clear git training at start

### Risk: Loss of momentum or engagement

**Mitigation**:
- Regular progress celebration
- Connect to bigger picture (kg-microbe, ICBO)
- Varied tasks matching interests
- Recognize individual contributions publicly

## Appendix A: Detailed API Examples

### Example 1: Search OLS for Term

```python
import requests
import pandas as pd

def search_ols_comprehensive(label, ontologies=["omp", "pato", "mco", "envo"]):
    """
    Search OLS4 for terms matching label across multiple ontologies
    """
    results = []

    base_url = "https://www.ebi.ac.uk/ols4/api/search"

    for ontology in ontologies:
        params = {
            "q": label,
            "ontology": ontology,
            "exact": "false",
            "rows": 5,
            "start": 0
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        if "response" in data and "docs" in data["response"]:
            for doc in data["response"]["docs"]:
                results.append({
                    "query": label,
                    "match_label": doc.get("label"),
                    "match_iri": doc.get("iri"),
                    "match_ontology": doc.get("ontology_name"),
                    "match_type": doc.get("type"),
                    "match_definition": doc.get("description", [""])[0] if "description" in doc else "",
                    "score": doc.get("score", 0)
                })

    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)

    return pd.DataFrame(results)

# Usage
df = search_ols_comprehensive("thermophilic")
print(df.to_string())
```

### Example 1b: Use OLS4 Embedding-Based Similarity

**Note**: OLS4's semantic similarity feature uses embeddings to find related terms even when labels differ. This is accessible through the web interface but requires web scraping or browser automation to access programmatically (no direct API endpoint yet).

```python
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup

def get_ols_similar_classes(term_iri, ontology, top_k=10):
    """
    Retrieve similar classes from OLS4 web interface

    Note: This scrapes the web UI since there's no direct API for embeddings.
    OLS4 may add an official API endpoint in the future.

    Args:
        term_iri: Full IRI of the term (e.g., "http://purl.obolibrary.org/obo/PATO_0002078")
        ontology: Ontology code (lowercase, e.g., "pato")
        top_k: Number of similar terms to retrieve

    Returns:
        List of similar terms with labels and IRIs
    """
    # URL encode the IRI for OLS4 URL
    encoded_iri = quote(term_iri, safe='')
    url = f"https://www.ebi.ac.uk/ols4/ontologies/{ontology}/classes/{encoded_iri}"

    # Note: This requires JavaScript rendering
    # In production, use Selenium or Playwright for full rendering
    response = requests.get(url)

    # This is a placeholder - actual implementation would need
    # JavaScript rendering to access the "Similar classes" widget
    # which is loaded dynamically

    print(f"Visit {url} to see similar classes in the web interface")
    print("Embedding-based similar classes are shown in the 'Similar classes' tab")

    return url

# Usage
term_iri = "http://purl.obolibrary.org/obo/PATO_0002078"  # thermophilic
url = get_ols_similar_classes(term_iri, "pato")
print(f"\nView similar terms at: {url}")

# Alternative: Use web interface directly
# Students can manually check similar classes and record findings
```

**Recommended Workflow for OLS4 Similar Classes**:

Since there's no direct API endpoint yet:

1. **Manual exploration** (quick, good for small batches):
   - Search OLS4 for METPO term
   - Click on best match
   - Navigate to "Similar classes" or "Similar entities" tab
   - Record top 5-10 similar terms manually

2. **Browser automation** (scalable, for larger batches):
   - Use Playwright or Selenium to render JavaScript
   - Extract similar terms programmatically
   - Cache results

```python
# Example with Playwright (requires: pip install playwright)
from playwright.sync_api import sync_playwright

def get_similar_classes_playwright(term_iri, ontology):
    """
    Use Playwright to get similar classes from OLS4 web UI
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Navigate to term page
        encoded_iri = quote(term_iri, safe='')
        url = f"https://www.ebi.ac.uk/ols4/ontologies/{ontology}/classes/{encoded_iri}"
        page.goto(url)

        # Wait for similar classes to load
        page.wait_for_selector('[data-testid="similar-classes"]', timeout=10000)

        # Extract similar terms
        # (Actual selectors depend on OLS4's HTML structure)
        similar_terms = page.query_selector_all('.similar-class-item')

        results = []
        for term_elem in similar_terms[:10]:
            label = term_elem.query_selector('.label').inner_text()
            iri = term_elem.query_selector('a').get_attribute('href')
            results.append({'label': label, 'iri': iri})

        browser.close()
        return results

# Note: Actual implementation depends on OLS4's HTML structure
# Check the page source to find correct selectors
```

3. **Request API feature** (long-term):
   - Contact OLS4 team to request embedding similarity API endpoint
   - This would enable programmatic access without scraping
   - Feature request: https://github.com/EBISPOT/ols4 (if public repo exists)
```

### Example 2: Get Parent Classes

```python
def get_parent_hierarchy(term_iri, ontology):
    """
    Get full parent hierarchy for a term
    """
    from urllib.parse import quote

    encoded_iri = quote(term_iri, safe='')
    url = f"https://www.ebi.ac.uk/ols4/api/ontologies/{ontology}/terms/{encoded_iri}/hierarchicalParents"

    response = requests.get(url)
    data = response.json()

    parents = []
    if "_embedded" in data and "terms" in data["_embedded"]:
        for term in data["_embedded"]["terms"]:
            parents.append({
                "iri": term.get("iri"),
                "label": term.get("label"),
                "ontology": term.get("ontology_name")
            })

    return parents

# Usage
parents = get_parent_hierarchy("http://purl.obolibrary.org/obo/PATO_0002078", "pato")
for p in parents:
    print(f"{p['label']} ({p['iri']})")
```

### Example 3: Batch Processing

```python
def process_metpo_classes(input_tsv, output_tsv):
    """
    Batch process METPO classes: search OLS/BioPortal for each
    """
    df = pd.read_csv(input_tsv, sep="\t")

    results = []

    for idx, row in df.iterrows():
        metpo_id = row["class_id"]
        metpo_label = row["class_label"]

        print(f"Processing {metpo_label}...")

        # Search OLS
        ols_results = search_ols_comprehensive(metpo_label)

        # Take top result from each ontology
        for ontology in ["OMP", "PATO", "MCO", "ENVO"]:
            ontology_results = ols_results[ols_results["match_ontology"] == ontology]
            if not ontology_results.empty:
                top = ontology_results.iloc[0]
                results.append({
                    "metpo_id": metpo_id,
                    "metpo_label": metpo_label,
                    "match_label": top["match_label"],
                    "match_iri": top["match_iri"],
                    "match_ontology": top["match_ontology"],
                    "match_definition": top["match_definition"],
                    "score": top["score"]
                })

        # Rate limiting
        time.sleep(0.5)

    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_tsv, sep="\t", index=False)
    print(f"Saved {len(results)} matches to {output_tsv}")

# Usage
process_metpo_classes("metpo_needs_mapping.tsv", "metpo_search_results.tsv")
```

## Appendix B: ROBOT Template Cheat Sheet

### Basic Template Structure

```tsv
ID	Label	IAO:0000115	IAO:0000119	skos:exactMatch	skos:closeMatch	Parent
METPO:0000001	thermophilic	A quality...	Source...	PATO:0002078		PATO:0000146
```

### Common Columns

| Column | Purpose | Example |
|--------|---------|---------|
| `ID` | Unique class identifier | `METPO:0000001` |
| `Label` | Human-readable name | `thermophilic` |
| `IAO:0000115` | Textual definition | `A quality of an organism that...` |
| `IAO:0000119` | Definition source | `BacDive analysis 2025-10-24` |
| `skos:exactMatch` | Exact match to external term | `PATO:0002078` |
| `skos:closeMatch` | Close match to external term | `OMP:0005508` |
| `rdfs:subClassOf` or `Parent` | Parent class | `PATO:0000146` |

### Multi-value Columns (use SPLIT)

```tsv
ID	Label	skos:closeMatch	SPLIT=|
METPO:0000001	thermophilic	OMP:0005508|PATO:0002078
```

### ROBOT Commands

**Build from template**:
```bash
robot template --template metpo.tsv \
  --prefix "METPO: http://purl.obolibrary.org/obo/METPO_" \
  --ontology-iri "http://purl.obolibrary.org/obo/metpo.owl" \
  --output metpo.owl
```

**Reason**:
```bash
robot reason --input metpo.owl \
  --reasoner ELK \
  --output metpo-reasoned.owl
```

**Validate**:
```bash
robot report --input metpo.owl \
  --output metpo-report.txt \
  --fail-on ERROR
```

**Chain commands**:
```bash
robot template --template metpo.tsv \
  reason --reasoner ELK \
  report --fail-on ERROR \
  --output metpo.owl
```

## Appendix C: Git Workflow Reference

### Branch Naming

```
add-{class-label}-mapping
add-{class-label}-definition
fix-{class-label}-issue
```

Examples:
- `add-thermophilic-mapping`
- `add-halophilic-definition`
- `fix-motile-typo`

### Commit Message Format

```
[Action] [Class label] ([METPO ID])

- Detail 1
- Detail 2
- Decision: [reference to documentation]
```

Examples:
```
Add PATO mapping for thermophilic (METPO:0000001)

- Maps to PATO:0002078 (thermophilic quality)
- Source: OLS search validated against BacDive
- Decision: metpo-kgm-studio/mapping-decisions/2025-10-24-thermophilic.md
```

```
Add Aristotelian definition for halophilic (METPO:0000002)

- Definition: "A quality of an organism that exhibits optimal growth at elevated salt concentrations"
- Source: BacDive halophily analysis and literature review
- Decision: metpo-kgm-studio/definition-decisions/2025-10-24-halophilic.md
```

### Pull Request Workflow

```bash
# 1. Create branch
git checkout -b add-thermophilic-mapping

# 2. Make change
nano src/templates/metpo.tsv

# 3. Validate
make build
robot reason --input metpo.owl --reasoner ELK

# 4. Commit
git add src/templates/metpo.tsv
git commit -m "Add PATO mapping for thermophilic (METPO:0000001)

- Maps to PATO:0002078
- Decision: metpo-kgm-studio/mapping-decisions/2025-10-24-thermophilic.md"

# 5. Push
git push -u origin add-thermophilic-mapping

# 6. Create PR
gh pr create --title "Add PATO mapping for thermophilic" \
  --body "See commit message for details"

# 7. Address review feedback
# ... make changes ...
git add .
git commit --amend
git push --force-with-lease

# 8. Merge (after approval)
gh pr merge --squash
```

### Common Git Issues

**Merge conflict**:
```bash
# Update your branch with main
git fetch origin
git merge origin/main

# Resolve conflicts in editor
nano src/templates/metpo.tsv

# Mark as resolved
git add src/templates/metpo.tsv
git commit -m "Merge main and resolve conflicts"
```

**Accidentally committed to main**:
```bash
# Create branch from current state
git branch add-my-change

# Reset main to match remote
git checkout main
git reset --hard origin/main

# Switch back to new branch
git checkout add-my-change
```

## Summary

This plan provides a comprehensive framework for undergraduate engagement in METPO development. Key principles:

1. **Scientific rigor**: One change at a time, document everything
2. **Quality over quantity**: OBO-compliant definitions and validated mappings
3. **Semantic precision**: Never conflate entities with qualities
4. **Inclusive engagement**: Tasks for varied skill sets and interests
5. **Sustainable process**: Documented decisions support future maintenance

Success requires combining technical skills (APIs, git, ROBOT) with domain knowledge (microbiology, ontology design) and careful attention to semantic details. The workflow ensures quality through validation at every step while allowing students to work semi-independently on individual classes.

The ultimate goal: a high-quality METPO suitable for EBI OLS submission and ICBO 2025 presentation, maintained by a trained team of student contributors.
