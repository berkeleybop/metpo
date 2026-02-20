# Case Study: "Casamino Acids" CURIE Mapping Failure in KG-Microbe

**Created:** 2026-02-19

---

## Summary

KG-Microbe's MediaDive transform maps "Casamino acids" to **CHEBI:78020**. CHEBI:78020 is actually **heptacosanoate** (a C27 fatty acid anion, formula C27H53O2). This is completely wrong. The error originated from an LLM-generated mapping in the upstream MicroMediaParam repo and propagated through validation into the released knowledge graph.

This case study documents the error, its provenance, its impact, and what it means for METPO's approach to chemical CURIE assignment.

---

## The Error

| Field | Value |
|-------|-------|
| Compound name in MediaDive | Casamino acids |
| Assigned CURIE | CHEBI:78020 |
| Actual CHEBI:78020 label | heptacosanoate |
| CHEBI:78020 formula | C27H53O2 |
| OLS link | https://www.ebi.ac.uk/ols4/ontologies/chebi/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FCHEBI_78020 |
| Rows affected | 57 in `compound_mappings_strict_hydrate.tsv` |
| Edges affected | Dozens of `biolink:has_part` edges in transformed output |

The mapping file's own columns show the mismatch side by side:

```
original          mapped        chebi_label      chebi_formula
Casamino acids    CHEBI:78020   heptacosanoate   C27H53O2
```

---

## What Is Casamino Acids?

Casamino acids is a **complex biological mixture** produced by acid hydrolysis of casein (milk protein from Bos taurus). It is a standard microbiological medium supplement providing free amino acids and small peptides. It is not a single molecule and has no molecular formula.

### Ontology representation

| Ontology | Term ID | Label | Notes |
|----------|---------|-------|-------|
| **CHEBI** | (none) | -- | No CHEBI term exists. CHEBI models individual chemicals, not complex biological mixtures. |
| **MicrO** | MICRO:0000184 | casamino acids | "An acid hydrolysate of casein (milk protein from cow's milk, Bos taurus)" -- synonyms: "Casein Hydrolysate", "acid digest of casein" |
| **MCO** | MCO:0000081 | vitamin assay casamino acids | The vitamin-depleted variant |
| **FOODON** | FOODON:03315719 | mammalian milk protein (hydrolyzed) | Closest FOODON term, not exact |
| **PubChem** | PubChem:167312541 | Vitamin-free casamino acids | Used by KG-Microbe for the vitamin-free variant |

The correct ontology term for casamino acids is **MICRO:0000184**. However, KG-Microbe's MediaDive transform only uses CHEBI, KEGG, PubChem, and CAS-RN CURIEs (it has no MicrO integration).

---

## Provenance of the Error

### Upstream source

The mapping file `compound_mappings_strict_hydrate.tsv` is downloaded from the CultureBotAI/MicroMediaParam repo during KG-Microbe builds:

```
https://github.com/CultureBotAI/MicroMediaParam/.../compound_mappings_strict_final_hydrate.tsv
```

### Origin commit

The bad CHEBI:78020 mapping was introduced in commit `f02b23c1` (2025-10-29) in CultureBotAI/MicroMediaParam, in `src/mapping/microbio_products.py`:

```python
ProductMapping(
    product_name="casamino acids",
    chebi_id="CHEBI:78020",  # casamino acids (if exists, else use peptone)
    description="Acid hydrolysate of casein, mixture of amino acids and small peptides",
    synonyms=["casamino acid", "casaminoacids", "casmino acid", "casmino acids"],
    confidence="medium",
    notes="Complex mixture, no single ChEBI ID perfectly represents it"
)
```

The commit ends with `Co-Authored-By: Claude <noreply@anthropic.com>`. The CHEBI ID was fabricated by the LLM. The comment "if exists, else use peptone" and `confidence="medium"` show the LLM was uncertain but guessed anyway.

### Validation caught it, nobody fixed it

MicroMediaParam's own validation pipeline flagged the mismatch in `pipeline_output/ATTIC/validation/validation_report.tsv`:

```
Casamino acids  CHEBI:78020  CHEBI  casamino acids  heptacosanoate  MISMATCH
  Expected 'casamino acids', got 'heptacosanoate'
```

The remediation pipeline marked it as `NOT_FOUND`. The mapping was never corrected.

No issues have been filed on the MicroMediaParam repo (zero issues in the tracker).

---

## Impact in KG-Microbe

In the transformed output (`data/transformed/mediadive/`):

**nodes.tsv:**
```
CHEBI:78020   biolink:ChemicalEntity   Casamino acids
```

This node asserts that CHEBI:78020's label is "Casamino acids", overriding the actual CHEBI label "heptacosanoate".

**edges.tsv:** Dozens of edges like:
```
mediadive.solution:1029   biolink:has_part   CHEBI:78020
mediadive.solution:1038   biolink:has_part   CHEBI:78020
...
```

Every medium recipe containing casamino acids links to a C27 fatty acid instead.

The "Vitamin-free casamino acids" variant is separately mapped to PubChem:167312541, which appears to be correct (or at least not a fatty acid).

---

## Lessons for METPO

### 1. Never trust LLM-generated CURIEs without label verification

The single most important check: after assigning a CURIE, verify that the authoritative label for that CURIE matches what you think it is. This mapping had `chebi_label: heptacosanoate` right next to `original: Casamino acids` and nobody caught it.

Tools that would have caught this:
- **linkml-term-validator**: validates that CURIEs in LinkML schemas reference valid terms with matching labels
- **OAK label lookup**: `runoak -i sqlite:obo:chebi label CHEBI:78020` returns "heptacosanoate"
- Any SPARQL/API check against OLS, BioPortal, or the source ontology

### 2. Complex biological mixtures may not belong in CHEBI

Casamino acids is a mixture, not a molecule. Trying to force it into CHEBI leads to errors because there is no correct CHEBI ID. The right approach is:
- Use **MICRO:0000184** (MicrO) as the primary ontology term
- Add a METPO class with a `>AI IAO:0000119` definition source CURIE pointing to MICRO:0000184
- If KG-Microbe needs a CHEBI-like CURIE, acknowledge the gap and use a custom prefix rather than guessing

### 3. KG-Microbe CURIE preferences need auditing

KG-Microbe's CURIE preference chain (CHEBI > KEGG > PubChem > CAS-RN > mediadive.ingredient:) assumes that when a CHEBI mapping exists, it is correct. This case shows that assumption is unsafe. The 409 unmapped MediaDive ingredients documented in `kg-microbe/mappings/unmapped_ingredients_analysis.txt` may include similar errors in the mapped set.

### 4. Upstream validation findings need action

MicroMediaParam had validation that detected this error. The finding was recorded but not acted on. Any validation pipeline we build should have a clear workflow from "mismatch detected" to "mapping corrected or removed."

---

## Recommended Actions

1. **File an issue on CultureBotAI/MicroMediaParam** documenting the CHEBI:78020 error and requesting correction (to MICRO:0000184 or removal)
2. **File an issue on berkeleybop/kg-microbe** about the propagated error in transformed output
3. **Audit the MicroMediaParam compound mappings** for other LLM-hallucinated CURIEs where `chebi_label` does not match `original`
4. **For METPO**: when adding chemical/substrate classes, always verify CURIEs against the source ontology before committing to ROBOT templates

---

*Updated: 2026-02-19*
