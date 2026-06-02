"""Tests for metpo_assessor analysis helpers."""

from metpo.literature_mining.analysis.metpo_assessor import MetpoAssessor


def test_load_semsql_registry_uses_timeout(monkeypatch):
    captured = {}

    class DummyResponse:
        text = "ontologies: []"

        def raise_for_status(self):
            return None

    def fake_get(url, timeout):
        captured["url"] = url
        captured["timeout"] = timeout
        return DummyResponse()

    monkeypatch.setattr(
        "metpo.literature_mining.analysis.metpo_assessor.requests.get",
        fake_get,
    )

    assessor = MetpoAssessor()

    assert assessor.semsql_registry == {"ontologies": []}
    assert (
        captured["url"]
        == "https://raw.githubusercontent.com/INCATools/semantic-sql/refs/heads/main/src/semsql/builder/registry/ontologies.yaml"
    )
    assert captured["timeout"] == 10


def test_analyze_grounding_handles_entities_without_labels():
    assessor = MetpoAssessor.__new__(MetpoAssessor)

    result = assessor._analyze_grounding([{"id": "CHEBI:1"}, {"id": "AUTO:tmp"}])

    assert result["total"] == 2
    assert result["grounded"] == 1
    assert result["ontologies_used"] == {"CHEBI": 1}
