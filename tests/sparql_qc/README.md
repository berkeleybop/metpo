# QC SPARQL meta-test

This directory proves that the QC violation queries in `src/sparql/*-violation.sparql`
can actually fail. It exists because they once could not.

It lives here, under `tests/`, on purpose: the ODK-managed tree
(`src/ontology/`, `src/sparql/`) holds only ODK-owned scaffolding and the
ontology itself. This harness only *reads* the queries under `src/sparql/`; it
writes nothing there.

## The problem it guards against

The violation queries restrict to METPO terms with a namespace filter:

```sparql
FILTER(isIRI(?term) && STRSTARTS(STR(?term), "https://w3id.org/metpo/"))
```

That literal was once written `https://w3id.org/METPO_`, which matches no real
METPO IRI. Every namespace-filtered check then returned zero rows and reported
"0 violations" while CI stayed green for a long time (berkeleybop/metpo#487,
#465). A check that cannot fail is worse than no check: it is false confidence.

The permanent root-cause fix is the single `namespaces:` declaration in
`src/ontology/metpo-odk.yaml` (#465), which makes ODK regenerate the filters
consistently instead of each query hand-writing the IRI prefix. This meta-test
is the deterministic backstop that catches any future regression regardless of
how it is introduced.

## The contract (read this before editing any check)

**Every `*-violation.sparql` must have at least one matching case in
`qc-positive-fixture.ttl`.** The fixture is a tiny RDF graph seeded with one
deliberate violation per query, on real `https://w3id.org/metpo/` IRIs.
`run_sparql_metatest.sh` runs each query against it and fails if any returns
zero rows.

So:

- **Adding a violation query?** Add a seeded case to the fixture in the same PR.
  The runner discovers queries by glob, so a new query with no fixture case
  fails the meta-test until you add one. This is intentional: a check cannot
  enter the repo without a known-failing input.
- **Editing a violation query?** Re-run the meta-test and confirm its fixture
  case still trips it. If you tighten a filter, make sure the fixture still
  represents something the check is meant to catch.

The fixture IRIs are fixture-only (`9999xxx` range, never allocated) and live
only in this directory; they are never merged into the ontology.

## Running it

In the ODK container, from `src/ontology`:

```sh
sh run.sh bash ../../tests/sparql_qc/run_sparql_metatest.sh
```

CI runs it on every push/PR via `.github/workflows/sparql-metatest.yml`.
