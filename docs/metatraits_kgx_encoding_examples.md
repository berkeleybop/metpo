# MetaTraits to KGX Encoding Examples (Operational Path)

Date: 2026-02-13  
Issue: #348  
Primary audience: Anthea implementing MetaTraits ingestion into kg-microbe-style KGX edges.

## Goal

Encode MetaTraits assertions as deterministic KGX statements using METPO template-sheet mechanisms in this repo.

This is the operational path.
Do not use SSSOM as the runtime mapping artifact for this ingestion path.

## Inputs and In-Repo Resources

- Trait catalog scraper: `metpo/scripts/fetch_metatraits.py`
- In-sheet resolver: `metpo/scripts/resolve_metatraits_in_sheets.py`
- METPO class template: `src/templates/metpo_sheet.tsv`
- METPO property template: `src/templates/metpo-properties.tsv`
- Generated resolution table: `data/mappings/metatraits_in_sheet_resolution.tsv`
- Coverage report: `data/mappings/metatraits_in_sheet_resolution_report.md`

## Runbook

1. Refresh MetaTraits card catalog.

```bash
uv run fetch-metatraits -o data/mappings/metatraits_cards.tsv
```

2. Build deterministic in-sheet resolution table.

```bash
uv run resolve-metatraits-in-sheets \
  -m data/mappings/metatraits_cards.tsv \
  -o data/mappings/metatraits_in_sheet_resolution.tsv \
  -r data/mappings/metatraits_in_sheet_resolution_report.md
```

3. Use `data/mappings/metatraits_in_sheet_resolution.tsv` as your lookup while transforming per-organism MetaTraits assertions.

## Predicate Selection Rules

1. Composed trait (`base: substrate`) with predicate pair available:
Use the resolved `predicate_positive_id` or `predicate_negative_id` from the table.

2. Uncomposed boolean phenotype:
Use `biolink:has_phenotype` with a METPO class object.

3. Standalone process capability assertion:
Use `METPO:2000103` (`capable of`) with GO or METPO process object.

4. Enzyme activity assertions:
Use `METPO:2000302` / `METPO:2000303` with specific GO molecular function object.
Do not use generic SNOMED placeholders as enzyme objects.

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

Preferred object:
- map EC to GO MF via ec2go
- example GO MF: `GO:0004096` (catalase activity)

KGX edge:

```tsv
subject	predicate	object
NCBITaxon:<id>	METPO:2000302	GO:0004096
```

## Implementation Skeleton

Use this minimal transform flow.

```python
# Pseudocode only: adapt to kg-microbe transform classes.

resolution = load_resolution_table("data/mappings/metatraits_in_sheet_resolution.tsv")

for assertion in metatraits_assertions_for_taxon:
    trait = assertion["feature"]
    value = assertion["value"]

    row = resolution.get(trait)
    if row and row["mapping_kind"] == "composed":
        predicate = row["predicate_positive_id"] if is_true(value) else row["predicate_negative_id"]
        obj = resolve_object_curie(assertion, row)  # CHEBI for most composed traits
        emit_edge(subject_taxon, predicate, obj)
        continue

    # fallback routes for base boolean/factor/process/numeric
    emit_via_class_or_process_rules(assertion)
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
