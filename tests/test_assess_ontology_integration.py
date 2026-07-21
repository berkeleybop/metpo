"""Integration test for the ontology-assessment search CLI.

Exercises the real OLS4 search endpoint through a recorded vcrpy cassette, so
CI replays deterministically without network access. Marked ``integration`` so
it can be deselected with ``-m 'not integration'``.

To (re)record the cassette against live OLS4:

    VCR_RECORD=1 uv run pytest tests/test_assess_ontology_integration.py

Then commit the updated file under tests/cassettes/. Only OLS4 is covered here;
BioPortal needs an API key and is left to manual runs.
"""

import os
from pathlib import Path

import pytest
import vcr

from metpo.analysis.assess_ontology_by_api_search import search_ols

CASSETTE_DIR = Path(__file__).parent / "cassettes"

# Replay-only in CI; set VCR_RECORD=1 locally to (re)record against live OLS4.
# "all" overwrites the cassette so the documented re-record command actually refreshes it.
_record_mode = "all" if os.getenv("VCR_RECORD") else "none"
ols_vcr = vcr.VCR(
    cassette_library_dir=str(CASSETTE_DIR),
    record_mode=_record_mode,
    match_on=["method", "scheme", "host", "path", "query"],
)


@pytest.mark.integration
def test_search_ols_returns_structured_hits():
    with ols_vcr.use_cassette("ols_search_mesophilic.yaml"):
        results = search_ols("mesophilic", rows=5)

    assert results, "expected at least one OLS hit for 'mesophilic'"
    for hit in results:
        assert set(hit) == {"label", "iri", "ontology", "definition"}
    assert any(hit["iri"] for hit in results)
