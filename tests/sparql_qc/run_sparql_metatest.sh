#!/usr/bin/env bash
# Meta-test for the QC SPARQL violation queries (berkeleybop/metpo#500).
#
# Runs every src/sparql/*-violation.sparql against the positive-control fixture
# (qc-positive-fixture.ttl) and asserts each returns >= 1 row. This proves the
# checks actually MATCH METPO terms: four of them filter on the term namespace
# with STRSTARTS(str(?term), "https://w3id.org/metpo/"), and that filter was
# once "https://w3id.org/METPO_", matching nothing, so every check silently
# reported "0 violations" (#487, #465). A check that cannot fail is worse than
# no check.
#
# This harness lives OUTSIDE the ODK-managed tree (src/ontology, src/sparql): it
# only READS the queries under src/sparql. Queries are discovered dynamically,
# so a new *-violation.sparql with no seeded fixture case fails here, which
# forces the fixture to stay complete.
#
# Run locally from src/ontology:
#   sh run.sh bash ../../tests/sparql_qc/run_sparql_metatest.sh
# Requires: robot on PATH (present in the obolibrary/odkfull container).
# Requires bash (uses bash-only features: `set -o pipefail`, `shopt`, arrays).
if [ -z "${BASH_VERSION:-}" ]; then
  echo "::error::This script must be run with bash (not sh/dash)." >&2
  echo "Hint: sh run.sh bash ../../tests/sparql_qc/run_sparql_metatest.sh" >&2
  exit 1
fi
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
SPARQLDIR="$REPO_ROOT/src/sparql"
FIXTURE="$HERE/qc-positive-fixture.ttl"
OUT="$(mktemp -d)"
trap 'rm -rf "$OUT"' EXIT

shopt -s nullglob
queries=("$SPARQLDIR"/*-violation.sparql)
if [ "${#queries[@]}" -eq 0 ]; then
  echo "::error::no *-violation.sparql queries found in $SPARQLDIR"
  exit 1
fi

fail=0
for q in "${queries[@]}"; do
  name="$(basename "$q")"
  res="$OUT/$name.tsv"
  robot query --input "$FIXTURE" --query "$q" "$res"
  rows=$(($(wc -l < "$res") - 1))   # the first line is the SELECT header
  if [ "$rows" -ge 1 ]; then
    echo "OK   $name matched $rows fixture violation(s)"
  else
    echo "::error::$name matched 0 rows against the positive-control fixture: the check is a silent no-op (e.g. wrong term-namespace filter)."
    fail=1
  fi
done

if [ "$fail" -ne 0 ]; then
  echo
  echo "One or more QC violation queries matched nothing they are meant to catch."
  echo "Fix: seed the missing case in tests/sparql_qc/qc-positive-fixture.ttl, or"
  echo "correct the query's term-namespace filter (https://w3id.org/metpo/)."
  exit 1
fi

echo "All ${#queries[@]} QC violation queries matched their positive-control fixture."

# ---------------------------------------------------------------------------
# Ontology-header QC (berkeleybop/metpo#502). This check is maintained here,
# outside the ODK tree, rather than as an edit to an ODK query. It must:
#   (a) match >= 1 row against the bad-header fixture (proven able to fail), and
#   (b) match 0 rows against the real released metpo.owl (the actual assertion).
# ---------------------------------------------------------------------------
echo
HEADER_Q="$HERE/ontology-header-check.sparql"
REAL_OWL="$REPO_ROOT/metpo.owl"

robot query --input "$FIXTURE" --query "$HEADER_Q" "$OUT/header-fixture.tsv"
hrows=$(($(wc -l < "$OUT/header-fixture.tsv") - 1))
if [ "$hrows" -ge 1 ]; then
  echo "OK   ontology-header-check.sparql matched $hrows fixture violation(s)"

  if [ -f "$REAL_OWL" ]; then
    robot query --input "$REAL_OWL" --query "$HEADER_Q" "$OUT/header-real.tsv"
    rrows=$(($(wc -l < "$OUT/header-real.tsv") - 1))
    if [ "$rrows" -eq 0 ]; then
      echo "OK   ontology-header-check.sparql found no problems in metpo.owl"
    else
      echo "::error::the ontology header in metpo.owl has $rrows metadata problem(s):"
      cat "$OUT/header-real.tsv"
      fail=1
    fi
  else
    echo "::error::expected released ontology at $REAL_OWL but it is missing."
    fail=1
  fi
else
  echo "::error::ontology-header-check.sparql matched 0 rows against the fixture: the check is a silent no-op."
  echo "Skipping check against metpo.owl because the fixture proof-of-failure did not pass."
  fail=1
fi

if [ "$fail" -ne 0 ]; then
  exit 1
fi
