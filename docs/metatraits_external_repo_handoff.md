# MetaTraits External Implementation Handoff (Anthea-Focused)

Date: 2026-02-13  
Scope: Implementation in external repos (`Knowledge-Graph-Hub/kg-microbe` or `CultureBotAI/KG-Microbe-search`).

## Core Handoff Strategy

Show the full deterministic mapping and KGX instantiation logic using local MongoDB records and in-repo mapping artifacts, but leave API acquisition code to Anthea.

This gives her ownership of:
- API client design
- endpoint selection and retries
- request batching/rate limiting
- persistence of API payloads into Mongo

while avoiding ambiguity in ontology mapping and KGX modeling.

## Why This Split Works

- You de-risk modeling correctness by giving fixed mapping/instantiation examples.
- She still contributes substantial engineering work in API integration.
- It avoids reintroducing old anti-patterns during early implementation.

## Strong Constraint: Do Not Reuse Legacy kg-microbe Transform Code/Config

Do not copy or adapt old `kg-microbe` transform utility modules/config as implementation base for this MetaTraits path.

Reasons:
- historical mixed concerns (I/O, mapping, edge emission in same layer)
- historical fallback behavior that can emit placeholders or lossy mappings
- difficult-to-test coupling to old constants/config conventions

Preferred architecture (new, minimal module in her target repo):
1. `acquire` layer: API calls only
2. `normalize` layer: parse values and identifiers
3. `resolve` layer: trait -> METPO predicate/object via deterministic tables
4. `emit` layer: KGX rows only

## Current MongoDB Readiness (local `metatraits` DB)

These counts show there are already many records from multiple MetaTraits-derived sources.

| Collection | Documents | Trait summary items |
|---|---:|---:|
| `ncbi_species_summary` | 54,654 | 5,343,971 |
| `ncbi_genus_summary` | 4,906 | 630,029 |
| `ncbi_family_summary` | 1,022 | 149,610 |
| `gtdb_species_summary` | 65,349 | 7,490,924 |
| `gtdb_genus_summary` | 18,440 | 2,231,509 |
| `gtdb_family_summary` | 4,511 | 570,217 |
| `genome_traits` | 130 | 130 |
| `ncbi2gtdb` (crosswalk) | 92,711 | n/a |

Interpretation:
- "lots of records" requirement is met for summary-scale analysis.
- direct assertion-like rows with ontology arrays are currently concentrated in `genome_traits`.
- `ncbi2gtdb` and `gtdb2ncbi` provide identifier crosswalk scaffolding.

## Identifier Priority for Querying

Priority order for acquisition/search keys:
1. NCBI taxon ID (`tax_id`) when available
2. GTDB taxon ID (convert via crosswalk)
3. Genome accession (`GCA_*`) for record-level retrieval

Recommended persisted fields in her target repo DB schema:
- `source` (api endpoint name)
- `tax_id_ncbi`
- `tax_id_gtdb`
- `genome_accession`
- `trait_name`
- `majority_label`
- `percentages`
- `ontologies`
- `is_ai`
- `retrieved_at`

## Deterministic Mapping Inputs to Reuse

Use these artifacts as authoritative lookup inputs:
- `src/templates/metpo-properties.tsv`
- `src/templates/metpo_sheet.tsv`
- `data/mappings/metatraits_in_sheet_resolution.tsv`
- `data/mappings/metatraits_in_sheet_resolution_report.md`

## Do We Need Additional Mapping Files?

Operationally required: no additional hand-curated mapping files.

Recommended generated support files:
1. `metatraits_identifier_crosswalk.tsv` (from Mongo `ncbi2gtdb`/`gtdb2ncbi`) for fast joins.
2. Optional only: `ec2go` snapshot for downstream interoperability views.

These are generated/reference aids, not new manual mapping governance surfaces.
Operational mapping should keep native MetaTraits object CURIEs (e.g., `EC:*`,
`GO:*`, `CHEBI:*`) unless a downstream consumer requires normalization.

## External Repo Code Example (API Left as TODO)

```python
# target repo: kg-microbe or KG-Microbe-search

from typing import Iterable
from kgx.sink import TsvSink
from kgx.transformer import Transformer


def fetch_metatraits_assertions_by_taxon(tax_id: int) -> list[dict]:
    # Anthea-owned implementation:
    # call MetaTraits API/download endpoints, return normalized records
    raise NotImplementedError


def map_assertion_to_kgx_edges(assertion: dict, resolution_table: dict) -> Iterable[dict]:
    trait = assertion["trait_name"]
    value = assertion["value"]
    row = resolution_table.get(trait)
    if not row:
        return []

    if row["mapping_kind"] == "composed":
        predicate = row["predicate_positive_id"] if value is True else row["predicate_negative_id"]
        obj = choose_object_from_ontologies(assertion.get("ontologies", []), row)
        if not predicate or not obj:
            return []
        return [
            {
                "subject": assertion["subject_curie"],
                "predicate": predicate,
                "object": obj,
                "knowledge_level": "knowledge_assertion",
                "agent_type": "automated_agent" if assertion.get("is_ai") else "manual_agent",
                "primary_knowledge_source": ["infores:metatraits"],
            }
        ]

    return emit_base_trait_edges(assertion, row)


def write_kgx(nodes: list[dict], edges: list[dict], output_prefix: str) -> None:
    transformer = Transformer()
    sink = TsvSink(owner=transformer, filename=output_prefix, format="tsv")
    for node in nodes:
        sink.write_node(node)
    for edge in edges:
        sink.write_edge(edge)
    sink.finalize()
```

## Opportunities That Fit Her Recent Work Pattern

From recent activity, she appears engaged in:
- ingestion and transform updates (`kg-microbe` PRs #425/#452)
- API troubleshooting (`KG-Microbe-search` issue #1)

High-fit ownership opportunities:
1. Robust API batching/retry module (taxon-id first, fallback to genome accession).
2. Mongo persistence layer with id-centric indexes.
3. Retrieval-to-mapping bridge adapter that outputs normalized assertion records.
4. Integration tests from Mongo fixture docs to deterministic KGX expected rows.
5. Metrics/reporting for unresolved categories and missing CHEBI/object coverage.

## Minimal Acceptance Criteria for Her PR

1. No fuzzy mapping in predicate routing.
2. No reuse/copy of legacy kg-microbe transform internals/config.
3. Deterministic outputs for fixed fixture input.
4. Composed traits preserve substrate/object when present.
5. Positive/negative assay outcomes route to correct predicate pair.
