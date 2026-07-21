# METPO (Microbial Ecology Trait and Phenotype Ontology) Synonym Conventions

**Purpose:** How METPO records synonyms, which annotation property each Google-Sheet
column maps to, and the rules a curator (or an automated check) must follow. The
classes tab has two *kinds* of synonym column with different rules.

---

## The Short Version

- **Ontology-native** synonyms are clean, curated US English that METPO asserts in its
  own voice. They use `oboInOwl:hasExactSynonym` / `hasRelatedSynonym` with no source.
- **Source-bound** synonyms are **verbatim** strings from an external database, paired
  with a source column that **reifies** the synonym assertion with its provenance.
- **Never normalize a source-bound value**, and **never de-duplicate source-bound
  synonyms across classes** — both are intentional (see below).
- An **exact** synonym should (almost) uniquely identify one class. The same exact
  synonym on many classes is an *overload* and is discouraged.

---

## The columns and their ROBOT directives

| Column | Directive | Property | Kind |
|---|---|---|---|
| `confirmed exact synonym` | `A oboInOwl:hasExactSynonym SPLIT=\|` | exact synonym | ontology-native |
| `literature mining related synonyms` | `A oboInOwl:hasRelatedSynonym SPLIT=\|` | related synonym | ontology-native |
| `madin synonym or field` | `A oboInOwl:hasRelatedSynonym SPLIT=\|` | related synonym | source-bound |
| `Madin synonym source` | `>AI IAO:0000119 SPLIT=\|` | (axiom annotation) | source provenance |
| `bacdive keyword synonym` | `A oboInOwl:hasRelatedSynonym SPLIT=\|` | related synonym | source-bound |
| `Bacdive synonym source` | `>AI IAO:0000119 SPLIT=\|` | (axiom annotation) | source provenance |
| `bactotraits related synonym` | `A oboInOwl:hasRelatedSynonym SPLIT=\|` | related synonym | source-bound |
| `Bactotraits synonym source` | `>AI IAO:0000119 SPLIT=\|` | (axiom annotation) | source provenance |
| `metatraits synonym` | `A oboInOwl:hasRelatedSynonym SPLIT=\|` | related synonym | source-bound |
| `MetaTraits synonym source` | `>AI IAO:0000119 SPLIT=\|` | (axiom annotation) | source provenance |

The leading `>` on each `*source*` column is a ROBOT template directive that **annotates
the preceding synonym assertion** rather than the term. The result is a reified
synonym, e.g. in the OWL:

```xml
<owl:Axiom>
  <owl:annotatedSource rdf:resource="https://w3id.org/metpo/2000002"/>
  <owl:annotatedProperty rdf:resource="…oboInOwl#hasRelatedSynonym"/>
  <owl:annotatedTarget>assimilation</owl:annotatedTarget>
  <obo:IAO_0000119 rdf:resource="https://bacdive.dsmz.de/"/>
</owl:Axiom>
```

This is how METPO records **which external-system value maps to which METPO entity**:
the synonym is the verbatim external value and the `IAO:0000119` (definition source)
annotation records the database it came from.

---

## Rules

1. **Source-bound columns hold verbatim source strings.** Do not "correct" them, even
   when the source has typos, odd casing, inconsistent prefixes, or non-English forms.
   Downstream consumers (e.g. the kg-microbe transformers) match on the exact source
   string; normalizing breaks the match.
2. **Duplicate source-bound related synonyms across classes are intentional.** One
   external value (e.g. a BactoTraits temperature bin code) legitimately maps to several
   METPO classes; keeping it on each — each reified with its source — is the point. Do
   **not** treat these as duplicates to remove. (A `duplicate_*_synonym` QC finding on a
   `hasRelatedSynonym` is expected for source-bound values.)
3. **Ontology-native columns use clean, consistent US English.** Foreign-language forms,
   source typos, and one-off transcriptions belong in source-bound columns, not here.
4. **Exact synonyms should be near-unique.** `oboInOwl:hasExactSynonym` asserts the value
   *is* a name for the class, so the same exact synonym on many sibling classes is an
   *overload* (a qualitative term like `mesophilic` stamped onto every numeric bin). Pick
   one canonical owner; downgrade the others to `hasRelatedSynonym` or drop them. Tracked
   in issue #444.
5. **If a source value also happens to be the desired ontology-native synonym, put it in
   both columns** — do not rely on a source-bound column to carry English semantics.

---

## Why reification (not bare synonyms)

A bare synonym says "this string names this class." METPO additionally needs to say
"this string is *the value used by database X*," so that the same human-facing concept
can be mapped to multiple external vocabularies and back. The reified `IAO:0000119`
provenance is what makes the synonym a *mapping record*, not just a label. (This is
distinct from the observation-reification layer that was removed in #371; synonym-source
reification is a deliberate, retained feature.)

See also: `docs/deprecation-workflow.md`, `docs/identifier-scheme.md`, and the
"Synonym Column Conventions" section of the repository `CLAUDE.md`.
