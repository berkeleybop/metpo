# MetaTraits to KGX Encoding Examples (Operational Path)

Date: 2026-02-13  
Issue: #348  
Primary audience: Anthea implementing MetaTraits ingestion into kg-microbe-style KGX edges.

## Goal

Encode MetaTraits assertions as deterministic KGX statements using METPO template-sheet mechanisms in this repo.

This is the operational path.
Do not use SSSOM as the runtime mapping artifact for this ingestion path.

If implementation happens in external repos (`Knowledge-Graph-Hub/kg-microbe` or
`CultureBotAI/KG-Microbe-search`), use:
`docs/metatraits_external_repo_handoff.md`

## Inputs and In-Repo Resources

- Trait catalog scraper: `metpo/scripts/fetch_metatraits.py`
- In-sheet resolver: `metpo/scripts/resolve_metatraits_in_sheets.py`
- METPO class template: `src/templates/metpo_sheet.tsv`
- METPO property template: `src/templates/metpo-properties.tsv`
- Generated resolution table: `data/mappings/metatraits_in_sheet_resolution.tsv`
- Coverage report: `data/mappings/metatraits_in_sheet_resolution_report.md`
- MongoDB fixture records: `docs/examples_metatraits_mongodb_api_like_records.json`

## Do We Already Have API-Like MongoDB Records?

Yes, on this machine.

Local MongoDB has a `metatraits` database with collections including:
- `genome_traits` (one document per assertion-like record)
- `genome_records` (one genome document with nested trait array)
- `ncbi_species_summary` / `ncbi_genus_summary` / `ncbi_family_summary` (aggregated trait summaries)

`genome_traits` is the closest shape to what Anthea is likely to pull from the MetaTraits API/taxonomy endpoints:
- `name`
- `majority_label`
- `percentages`
- `is_ai`
- `ontologies`
- `genome_accession`

I cannot directly inspect your LBL MacBook Pro from this session, but she can run the same checks there:

```bash
mongosh --quiet --eval 'db.adminCommand({listDatabases:1}).databases.map(d=>d.name).join("\\n")'
mongosh metatraits --quiet --eval 'db.getCollectionNames().join("\\n")'
mongosh metatraits --quiet --eval 'db.genome_traits.findOne()'
```

## Runbook

1. Generate deterministic helper files (one command).

```bash
make metatraits-helper-files
```

This produces:
- `data/mappings/metatraits_cards.tsv`
- `data/mappings/metatraits_in_sheet_resolution.tsv`
- `data/mappings/metatraits_in_sheet_resolution_report.md`

2. (Optional manual equivalent) refresh MetaTraits card catalog.

```bash
uv run fetch-metatraits -o data/mappings/metatraits_cards.tsv
```

3. (Optional manual equivalent) build deterministic in-sheet resolution table.

```bash
uv run resolve-metatraits-in-sheets \
  -m data/mappings/metatraits_cards.tsv \
  -o data/mappings/metatraits_in_sheet_resolution.tsv \
  -r data/mappings/metatraits_in_sheet_resolution_report.md
```

4. Use `data/mappings/metatraits_in_sheet_resolution.tsv` as your lookup while transforming per-organism MetaTraits assertions.

5. Optional: run the Mongo-backed demo exporter that writes KGX with official sinks.

```bash
make demo-metatraits-mongo
# writes data/mappings/demo_metatraits_mongo_kgx_nodes.tsv
# and    data/mappings/demo_metatraits_mongo_kgx_edges.tsv
```

## Predicate Selection Rules

1. Composed trait (`base: substrate`) with predicate pair available:
Use the resolved `predicate_positive_id` or `predicate_negative_id` from the table.

2. Uncomposed boolean phenotype:
Use `biolink:has_phenotype` with a METPO class object.

3. Standalone process capability assertion:
Use `METPO:2000103` (`capable of`) with GO or METPO process object.

4. Enzyme activity assertions:
Use `METPO:2000302` / `METPO:2000303` with native MetaTraits object CURIEs
first (e.g., `EC:*` when present). Avoid generic SNOMED placeholders as enzyme
objects. GO normalization is optional later, not required for initial ingest.

5. Numeric measurements:
Prefer dedicated METPO data properties once added/approved.
Until then, do not invent ad hoc blank-node patterns.

## Worked Examples

### A. Composed chemical trait (positive)

Input assertion:
- taxon: `NCBITaxon:562`
- trait: `fermentation: D-glucose`
- value: true

Resolved from table:
- `predicate_positive_id = METPO:2000011`
- substrate object: `CHEBI:4167` (example)

KGX edge:

```tsv
subject	predicate	object	knowledge_level	agent_type	primary_knowledge_source
NCBITaxon:562	METPO:2000011	CHEBI:4167	knowledge_assertion	manual_agent	infores:metatraits
```

### B. Composed chemical trait (negative)

Input assertion:
- taxon: `NCBITaxon:562`
- trait: `fermentation: D-glucose`
- value: false

Resolved predicate:
- `predicate_negative_id = METPO:2000037`

KGX edge:

```tsv
subject	predicate	object	knowledge_level	agent_type	primary_knowledge_source
NCBITaxon:562	METPO:2000037	CHEBI:4167	knowledge_assertion	manual_agent	infores:metatraits
```

### C. New nitrogen-cycle category now supported

Input assertion:
- trait: `denitrification: nitrate`
- value: true

Resolved predicate pair (in `src/templates/metpo-properties.tsv`):
- positive: `METPO:2000601` (`denitrifies`)
- negative: `METPO:2000602` (`does not denitrify`)

KGX edge pattern:

```tsv
subject	predicate	object
NCBITaxon:<id>	METPO:2000601	CHEBI:<nitrate-or-related-object>
```

### D. Uncomposed boolean phenotype

Input assertion:
- trait: `gram positive`
- value: true

KGX edge:

```tsv
subject	predicate	object
NCBITaxon:562	biolink:has_phenotype	METPO:1000698
```

### E. Standalone process capability

Input assertion:
- trait: `nitrogen fixation`
- value: true

KGX edge:

```tsv
subject	predicate	object
NCBITaxon:<id>	METPO:2000103	GO:0009399
```

### F. Enzyme activity

Input assertion:
- trait: `enzyme activity: catalase (EC1.11.1.6)`
- value: true

Preferred object (native-first):
- keep native EC CURIE from MetaTraits when present
- optional later: add GO MF normalization layer

KGX edge:

```tsv
subject	predicate	object
NCBITaxon:<id>	METPO:2000302	EC:1.11.1.6
```

## Implementation Skeleton

Use this minimal transform flow with KGX sink classes (no ad hoc TSV writer).

```python
from kgx.sink import TsvSink
from kgx.transformer import Transformer

resolution = load_resolution_table("data/mappings/metatraits_in_sheet_resolution.tsv")
nodes = {}
edges = []

for assertion in metatraits_assertions_for_taxon:
    trait = assertion["feature"]
    value = assertion["value"]

    row = resolution.get(trait)
    if row and row["mapping_kind"] == "composed":
        predicate = row["predicate_positive_id"] if is_true(value) else row["predicate_negative_id"]
        obj = resolve_object_curie(assertion, row)  # CHEBI for most composed traits
        edge = {
            "subject": subject_taxon,
            "predicate": predicate,
            "object": obj,
            "knowledge_level": "knowledge_assertion",
            "agent_type": "manual_agent",
            "primary_knowledge_source": ["infores:metatraits"],
        }
        edges.append(edge)
        nodes.setdefault(subject_taxon, {"id": subject_taxon, "category": ["biolink:Genome"]})
        nodes.setdefault(obj, {"id": obj, "category": infer_object_category(obj)})
        continue

    # fallback routes for base boolean/factor/process/numeric
    edges.extend(emit_via_class_or_process_rules(assertion))

transformer = Transformer()
sink = TsvSink(owner=transformer, filename="output/metatraits_demo", format="tsv")
for node in nodes.values():
    sink.write_node(node)
for edge in edges:
    sink.write_edge(edge)
sink.finalize()
```

## MongoDB-First Example (No API Calls Yet)

Anthea can prototype the transform logic against local Mongo records and later swap in API fetch code.

```python
# Pseudocode for assertion records from metatraits.genome_traits

record = {
    "name": "denitrification: nitrate",
    "majority_label": "false: (100%)",
    "percentages": {"false": 100},
    "ontologies": ["GO:0019333", "CHEBI:17632"],
    "genome_accession": "GCA_000008565.1",
}

subject = map_genome_to_subject_curie(record["genome_accession"])  # e.g., NCBITaxon or assembly CURIE
trait_name = record["name"]
is_true = parse_majority_label_to_boolean(record["majority_label"])  # false here

row = resolution_table[trait_name]  # from metatraits_in_sheet_resolution.tsv
predicate = row["predicate_positive_id"] if is_true else row["predicate_negative_id"]
obj = choose_object_curie(record["ontologies"], row)  # CHEBI first for composed chemical traits

emit_kgx_edge(
    subject=subject,
    predicate=predicate,
    object=obj,
    knowledge_level="knowledge_assertion",
    agent_type="automated_agent" if record.get("is_ai") else "manual_agent",
    primary_knowledge_source="infores:metatraits",
)
```

## Best Practices

- Use deterministic exact lookup first, not fuzzy matching.
- Keep one canonical edge per fact.
- Keep positive and negative predicates explicit when assay outcome exists.
- Keep Biolink-native predicate usage for phenotype edges (`biolink:has_phenotype`).
- Preserve source attribution in edge metadata.
- Fail loudly on unresolved categories; do not silently assign generic predicates.

## Anti-Patterns to Avoid

- Emitting both process and substrate edges for the same composed fact when one canonical substrate edge already captures it.
- Using fuzzy label matching to choose METPO terms.
- Treating SSSOM rows as runtime assertion rules for this ingestion path.
- Emitting generic GO objects when specific CHEBI/GO MF objects are available.
- Creating placeholder CURIEs when an approved ontology mapping path exists.

## Current Coverage Notes

The current resolver output reports unresolved areas that still need explicit term/modeling work (for example, `utilizes`, portions of `enzyme activity`, and traits missing CHEBI objects in source data).

Use `data/mappings/metatraits_in_sheet_resolution_report.md` to track these gaps and prioritize term additions in METPO templates.
