# LinkML Embedding and Validation Tools for METPO

**Created:** 2026-02-19

---

## Context

METPO needs to map MetaTraits trait card names (plain strings like "casamino acids", "glucose fermentation", "nitrate reduction") to ontology CURIEs for use as definition sources, cross-references, and KGX edge objects. The existing approach uses a ChromaDB database with OLS embeddings (778K vectors across 39 ontologies, 1536 dimensions from OpenAI text-embedding-3-small). Chris Mungall has expressed a preference for using **linkml-store** embedding capabilities instead of ChromaDB directly.

This doc covers the tools available in the LinkML ecosystem for semantic mapping and CURIE validation.

---

## linkml-store

**Repo:** https://github.com/linkml/linkml-store
**Docs:** https://linkml.io/linkml-store/
**PyPI:** `linkml-store` (v0.2.9+)
**Install:** `pip install "linkml-store[llm]"` (or `uv add "linkml-store[llm]"`)

### What it is

linkml-store is an AI-ready data management platform that provides a unified abstraction layer (CRUDSI: Create, Read, Update, Delete, Search, Inference) over multiple storage backends. For our purposes, the key capability is **LLM embedding-based semantic search** over ontology term collections.

### Storage backends

| Backend | Status | Notes |
|---------|--------|-------|
| DuckDB | Best supported | Recommended for local development |
| MongoDB | Well supported | We already have a local MongoDB with MetaTraits data |
| Neo4j | Supported | |
| Filesystem | Supported | JSON/YAML files |
| ChromaDB | Experimental | Adapter exists but documentation warns it may change |

### Key insight: no vector database required

From the linkml-store FAQ: "You don't need to have a vector database to run embedding search!" The LLM indexer computes and caches embeddings alongside any backend. You can run semantic search on top of DuckDB or MongoDB without ChromaDB or Qdrant.

### Indexer types

1. **`simple`**: Trigram-based vector embedding. No external model needed. Only matches literal string overlap. Good for demos.

2. **`llm`**: Uses LLM text embeddings for true semantic search via Simon Willison's `llm` package (https://llm.datasette.io/). Default model is OpenAI text-embedding-ada-002. Pluggable -- install local models with `llm install llm-sentence-transformers`.

### CLI usage

```bash
# Insert ontology terms into a DuckDB collection
linkml-store -d duckdb:///db/chebi.db -c chebi_terms insert -i chebi_terms.json

# Create an LLM embedding index
linkml-store -d duckdb:///db/chebi.db -c chebi_terms index -t llm

# Search for matches
linkml-store -d duckdb:///db/chebi.db -c chebi_terms search "casamino acids"

# RAG inference over a collection
linkml-store -d duckdb:///db/chebi.db -c chebi_terms infer -t rag -q "acid hydrolysate of casein"
```

### Python API

```python
from linkml_store import Client
from linkml_store.index.implementations.llm_indexer import LLMIndexer

# Create database and collection
client = Client()
db = client.attach_database("duckdb:///db/chebi.db")
collection = db.create_collection("chebi_terms")

# Insert terms (e.g., exported from OAK)
collection.insert([
    {"id": "CHEBI:78020", "label": "heptacosanoate"},
    {"id": "CHEBI:33709", "label": "amino acid"},
    # ...
])

# Create LLM index with Jinja2 template and embedding cache
index = LLMIndexer(
    name="chebi_index",
    cached_embeddings_database="cache/chebi_embeddings.db",
    text_template="{{ label }}",
    text_template_syntax="jinja2",
)
collection.attach_indexer(index)

# Semantic search
qr = collection.search("casamino acids")
for score, match in qr.ranked_rows[:5]:
    print(f"{match['id']} ({match['label']}) score={score:.3f}")
```

The `cached_embeddings_database` is a SQLite file storing computed embeddings, so re-runs don't recompute existing vectors.

### Jinja2 text templates

For collections with multiple fields, the indexer textualizes each record before embedding using a Jinja2 template:

```python
template = """
term: {{ label }}
synonyms: {{ synonyms | join(', ') }}
definition: {{ definition }}
"""

index = LLMIndexer(
    name="ontology_index",
    text_template=template,
    text_template_syntax="jinja2",
    cached_embeddings_database="cache/ontology_embeddings.db",
)
```

This is relevant for matching MetaTraits trait names against ontology terms where definitions and synonyms improve match quality beyond label-only matching.

### Storing an ontology directly

linkml-store can ingest an ontology via its JSON representation (see https://linkml.io/linkml-store/how-to/Store-an-Ontology.html). This could be used to load CHEBI, MicrO, or other reference ontologies for matching.

---

## linkml-term-validator

**Docs:** https://linkml.io/linkml-term-validator/schema-validation/
**Install:** `pip install linkml-term-validator`

### What it does

Validates that `meaning` CURIEs in LinkML schema enumerations reference valid ontology terms with correct labels. Runs at schema authoring time.

This is exactly the kind of check that would have caught the CHEBI:78020/heptacosanoate error (see `docs/casamino_acids_curie_mapping_case_study.md`).

### Usage

```bash
# Validate a schema
linkml-term-validator validate-schema schema.yaml

# Strict mode (fails on any mismatch)
linkml-term-validator validate-schema --strict schema.yaml

# Custom OAK configuration for ontology access
linkml-term-validator validate-schema --oak-config oak_config.yaml schema.yaml
```

### What it checks

For each enumeration permissible value with a `meaning` CURIE:
- The CURIE exists in the source ontology
- The canonical label matches the expected label

### Relevance to METPO

If METPO definition source CURIEs (the `>AI IAO:0000119` column in ROBOT templates) were expressed in a LinkML schema, linkml-term-validator could verify that every CURIE resolves to a real term with the expected label. This prevents hallucinated or stale CURIEs from entering the ontology.

---

## linkml-reference-validator

**Repo:** https://github.com/linkml/linkml-reference-validator
**Install:** `pip install linkml-reference-validator`

### What it does

Validates that supporting text quotes actually appear in cited references (fetches PubMed/PMC publications for verification).

```bash
# Validate a quote against a PMID
linkml-reference-validator validate text \
  "TP53 is critical for cell cycle regulation" PMID:12345678
```

### Relevance to METPO

Less directly relevant than linkml-term-validator. Could be useful if METPO definitions cite literature with specific text evidence.

---

## Core linkml-validate

**Docs:** https://linkml.io/linkml/data/validating-data.html

The core LinkML validator validates data instances against LinkML schemas. Supports plugins:

```bash
linkml-validate --schema my_schema.yaml my_data.yaml

# With reference validation plugin
linkml-validate --schema gene.yaml \
  --validate-plugins linkml_reference_validator.plugins.ReferenceValidationPlugin \
  tp53.yaml
```

### Dynamic enumerations

LinkML schemas can constrain values to specific branches of ontologies:

```yaml
enums:
  ChemicalEntityEnum:
    reachable_from:
      source_ontology: obo:chebi
      source_nodes:
        - CHEBI:24431  # chemical entity
      include_self: false
      relationship_types:
        - rdfs:subClassOf
```

This means if a METPO mapping references a CHEBI CURIE, the validator can check that the CURIE is actually a descendant of the expected CHEBI branch, not an unrelated term like heptacosanoate.

---

## OAK (Ontology Access Kit)

**Docs:** https://incatools.github.io/ontology-access-kit/
**Install:** `pip install oaklib`

OAK is the standard tool for programmatic ontology access in this ecosystem. Relevant capabilities:

### Label verification

```bash
# Check what CHEBI:78020 actually is
runoak -i sqlite:obo:chebi label CHEBI:78020
# Returns: heptacosanoate
```

### Lexical matching (outputs SSSOM)

```bash
# Match terms against CHEBI using lexical methods
runoak -i sqlite:obo:chebi lexmatch -o matches.sssom.tsv
```

### Term search

```bash
# Search for terms matching a string
runoak -i sqlite:obo:chebi search "casamino"
# (returns nothing -- casamino acids is not in CHEBI)

runoak -i sqlite:obo:micro search "casamino"
# Returns: MICRO:0000184 casamino acids
```

### Integration with linkml-store

OAK can export ontology terms to JSON, which linkml-store can ingest:

```bash
runoak -i sqlite:obo:chebi terms --output-type json > chebi_terms.json
linkml-store -d duckdb:///db/chebi.db -c chebi insert -i chebi_terms.json
linkml-store -d duckdb:///db/chebi.db -c chebi index -t llm
```

---

## CurateGPT

**Repo:** https://github.com/monarch-initiative/curategpt

LLM-assisted biocuration tool from the Monarch Initiative. Uses ChromaDB (via LangChain) for vector storage. Provides ontology term matching and suggestion capabilities.

The CurateGPT paper states that "future work will integrate CurateGPT with the LinkML-Store framework for using a broader variety of file systems and storage backends." The two projects are converging but currently separate.

---

## Comparison: Current ChromaDB Approach vs. linkml-store

| Aspect | Current (ChromaDB direct) | linkml-store |
|--------|--------------------------|--------------|
| **Code** | `metpo/pipeline/chromadb_semantic_mapper.py` | linkml-store CLI or Python API |
| **Embeddings** | OpenAI text-embedding-3-small (1536d) | Pluggable via `llm` package (default: ada-002) |
| **Ontology source** | OLS bulk download (288 GB SQLite on LBL Mac) | OAK export to JSON, then index |
| **Vector count** | 778K across 39 ontologies | Load what you need |
| **Schema** | None | LinkML schema enforcement |
| **Query types** | Vector similarity only | Structured + faceted + semantic + RAG |
| **Label verification** | Manual | linkml-term-validator integration |
| **Chris's preference** | Deprecated | Preferred |

### Migration path

1. Export relevant ontology terms via OAK (CHEBI, MicrO, GO, etc.)
2. Load into linkml-store DuckDB collections
3. Create LLM embedding indexes with cached embeddings
4. Replace `chromadb_semantic_mapper.py` calls with linkml-store search
5. Add linkml-term-validator to CI for CURIE verification

---

## Practical Workflow: Mapping "Casamino Acids" to a New METPO Class

This example walks through how these tools would work together for a term like "casamino acids" that appears in MetaTraits as a plain string.

### Step 1: Search for existing ontology terms

```bash
# Search across ontologies via OAK
runoak -i sqlite:obo:chebi search "casamino"       # nothing
runoak -i sqlite:obo:micro search "casamino"        # MICRO:0000184
runoak -i sqlite:obo:foodon search "casein hydrol"  # FOODON:03315719
```

Or via linkml-store semantic search (would find MICRO:0000184 even without exact string match).

### Step 2: Verify the CURIE

```bash
runoak -i sqlite:obo:micro info MICRO:0000184
# Label: casamino acids
# Definition: An acid hydrolysate of casein (milk protein from cow's milk, Bos taurus)
```

### Step 3: Add to METPO ROBOT template

In `src/templates/metpo_sheet.tsv`, add a row with:
- **ID**: next available METPO ID
- **Label**: casamino acids
- **Definition**: An acid hydrolysate of casein used as a microbiological medium supplement
- **Definition source** (`>AI IAO:0000119 SPLIT=|`): `MICRO:0000184`
- **Parent**: appropriate METPO parent class (e.g., chemical entity or medium component)

### Step 4: Add synonyms from MetaTraits sources

In the appropriate synonym columns (bacdive, metatraits):
- `casamino acids`
- `casaminoacids` (variant spelling in some MediaDive media)
- `casamino acid` (singular variant)
- `casein hydrolysate` (MicrO synonym)

### Step 5: Validate

```bash
# Verify the CURIE resolves correctly
runoak -i sqlite:obo:micro label MICRO:0000184
# Expected: casamino acids

# If using LinkML schema representation:
linkml-term-validator validate-schema --strict metpo_schema.yaml
```

---

## Key Documentation Links

- linkml-store docs: https://linkml.io/linkml-store/
- linkml-store FAQ (no vector DB needed): https://linkml.io/linkml-store/faq.html
- linkml-store phenopackets indexing tutorial: https://linkml.io/linkml-store/how-to/Index-Phenopackets.html
- linkml-store storing an ontology: https://linkml.io/linkml-store/how-to/Store-an-Ontology.html
- linkml-term-validator: https://linkml.io/linkml-term-validator/schema-validation/
- linkml-reference-validator: https://github.com/linkml/linkml-reference-validator
- OAK mappings guide: https://incatools.github.io/ontology-access-kit/guide/mappings.html
- Simon Willison's llm package: https://llm.datasette.io/
- CurateGPT: https://github.com/monarch-initiative/curategpt

---

*Updated: 2026-02-19*
