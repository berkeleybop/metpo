# Embedding and semantic search strategy

The standard approach for semantic similarity and cross-ontology matching in METPO (definition gap-filling, SSSOM mapping candidates, synonym discovery).

ChromaDB was retired (CVE, removed in [#498](https://github.com/berkeleybop/metpo/pull/498); the DIY pipeline was re-scoped in [#364](https://github.com/berkeleybop/metpo/issues/364)). Don't add ChromaDB or another committed local vector store back.

## Priority order

1. **OLS4 embeddings search API.** Server-side semantic search, no local storage or compute, and it covers the roughly 270 OLS-hosted ontologies. Use it for candidate retrieval and ranking whenever OLS hosts the target ontology. Confirm the current endpoint against the [OLS4 API docs](https://www.ebi.ac.uk/ols4/help). Because OLS-hosted ontologies are queried live, there is no need to download or commit local OWL copies of them.
2. **Proven tooling from projects we trust**, for anything OLS doesn't cover (BioPortal-only ontologies like MicrO, MPO, D3O) or for offline/batch work. Prefer components with a good track record in the ecosystems we already rely on (for example `linkml-store` with the `llm` library, tracked in [#364](https://github.com/berkeleybop/metpo/issues/364); OAK/oaklib in [#194](https://github.com/berkeleybop/metpo/issues/194)) over anything bespoke. The current implementation ranks with a local embedding model served by [Ollama](https://ollama.com/) (default `nomic-embed-text`).

## Implementations in this repo

- `metpo/pipeline/cross_ontology_search.py` — the current implementation: OLS4 search for candidate classes, then re-ranking by cosine similarity with a local embedding model. Endpoint and model are CLI options. Moving candidate retrieval to the OLS4 embeddings API (priority 1) is the intended direction.
- `metpo/analysis/assess_ontology_by_api_search.py` — a non-embedding, label-based OLS4/BioPortal search baseline (`assess-ontology-by-api-search`).

## Requirements

- **OLS4 path:** network access to the OLS4 API. No local ontology files or special hardware.
- **Local embedding path:** a machine that can run the chosen embedding tool (for the current Ollama default, any Ollama-capable machine; a GPU/Metal backend helps but is not required). No paid API key, no ~300 GB OLS SQLite dump, no multi-GB committed vector database.
- **Inputs:** METPO term labels and definitions (for example a labels TSV; see `data/metpo_terms/README.md`).
- **External ontologies (local path):** downloaded on demand with `make download-external-bioportal-ontologies`. These are build artifacts and are not committed (`external/` is git-ignored).

## Related issues

- [#364](https://github.com/berkeleybop/metpo/issues/364) — re-scope of the ChromaDB pipeline
- [#194](https://github.com/berkeleybop/metpo/issues/194) — OAK/oaklib for ontology access and similarity
- [#380](https://github.com/berkeleybop/metpo/issues/380) — cleanup of the external-ontology download machinery
