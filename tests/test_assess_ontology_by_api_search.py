"""Network-free tests for the ontology-assessment search CLI."""

from metpo.analysis.assess_ontology_by_api_search import (
    calculate_similarity,
    search_bioportal,
    search_ols,
)


def test_calculate_similarity_exact_match():
    distance, ratio = calculate_similarity("mesophilic", "Mesophilic")
    assert distance == 0
    assert ratio == 1.0


def test_calculate_similarity_partial_match():
    distance, ratio = calculate_similarity("oval shaped", "Oval")
    assert distance > 0
    assert 0.0 < ratio < 1.0


def test_calculate_similarity_handles_missing_label():
    assert calculate_similarity("anything", None) == (None, None)


class _FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


def test_search_ols_parses_docs(monkeypatch):
    payload = {
        "response": {
            "docs": [
                {
                    "label": "anaerobic respiration",
                    "iri": "http://purl.obolibrary.org/obo/GO_0009061",
                    "ontology_name": "go",
                    "description": ["release of energy"],
                }
            ]
        }
    }
    monkeypatch.setattr(
        "metpo.analysis.assess_ontology_by_api_search.requests.get",
        lambda *a, **k: _FakeResponse(200, payload),
    )
    results = search_ols("anaerobic respiration", rows=5)
    assert results == [
        {
            "label": "anaerobic respiration",
            "iri": "http://purl.obolibrary.org/obo/GO_0009061",
            "ontology": "go",
            "definition": "release of energy",
        }
    ]


def test_search_bioportal_derives_ontology_from_links(monkeypatch):
    payload = {
        "collection": [
            {
                "prefLabel": "Oval",
                "@id": "http://purl.obolibrary.org/obo/NCIT_C48345",
                "links": {"ontology": "https://data.bioontology.org/ontologies/NCIT"},
                "definition": ["an oval shape"],
            }
        ]
    }
    monkeypatch.setattr(
        "metpo.analysis.assess_ontology_by_api_search.requests.get",
        lambda *a, **k: _FakeResponse(200, payload),
    )
    results = search_bioportal("oval", api_key="token", pagesize=5)
    assert results[0]["ontology"] == "NCIT"
    assert results[0]["definition"] == "an oval shape"
