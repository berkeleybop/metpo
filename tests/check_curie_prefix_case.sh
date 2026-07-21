#!/usr/bin/env bash
# Enforce the blessed METPO CURIE prefix case (berkeleybop/metpo#16):
#   - CURIE prefix token is UPPERCASE  -> METPO:1000059
#   - URI namespace path stays lowercase -> https://w3id.org/metpo/
#
# This guards hand-authored RDF, SPARQL, and documentation against lowercase
# `metpo:` CURIE prefixes creeping back in. The regex only matches `metpo:`
# when it is preceded by a non-identifier character, so it ignores Make targets
# (`load-metpo:`), YAML keys (`strain_phenotype_metpo:`), and Python names
# (`curie_to_metpo:`), none of which are CURIEs.
#
# Deliberately NOT scanned:
#   - generated release artifacts (metpo.owl / -base / -full / *.obo): their
#     lowercase `idspace: metpo` is tracked in berkeleybop/metpo#557 and fixed at
#     the generator, not by hand.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

# `metpo:` as a CURIE = preceded by start-of-line or a non-[A-Za-z0-9_-] char.
pattern='(^|[^A-Za-z0-9_-])metpo:'

hits=$(git grep -nIE "$pattern" -- \
  '*.ttl' '*.rq' '*.sparql' '*.md' \
  ':(exclude)tests/check_curie_prefix_case.sh' || true)

if [ -n "$hits" ]; then
  echo "::error::Lowercase 'metpo:' CURIE prefix found. Use uppercase 'METPO:' (see berkeleybop/metpo#16)."
  echo "$hits"
  exit 1
fi

echo "OK: no lowercase 'metpo:' CURIE prefixes in tracked RDF/SPARQL/doc files."
