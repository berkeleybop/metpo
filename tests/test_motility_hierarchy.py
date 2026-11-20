"""The motility axis must accommodate both present and absent self-propulsion."""

import csv
import importlib.util
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def rows():
    with (ROOT / "src/templates/metpo_sheet.tsv").open() as stream:
        return {row["ID"]: row for row in csv.DictReader(stream, delimiter="\t")}


def test_nonmotile_inherits_neutral_motility_axis():
    terms = rows()
    axis, positive, negative = (
        terms[f"METPO:{identifier}"] for identifier in (1000701, 1000702, 1000703)
    )
    assert axis["parent classes (one strongly preferred)"] == "phenotype"
    assert "whether and how" in axis["definition"]
    assert "has the capability" not in axis["definition"]
    assert positive["parent classes (one strongly preferred)"] == axis["label"]
    assert negative["parent classes (one strongly preferred)"] == axis["label"]
    assert "has the ability" in positive["definition"]
    assert "lacks the ability" in negative["definition"]
    assert axis["definition source"] == "OMP:0000001"


def test_locomotion_mechanisms_remain_under_positive_branch():
    terms = rows()
    for identifier in (1000704, 1000705, 1000706):
        assert terms[f"METPO:{identifier}"]["parent classes (one strongly preferred)"] == "motile"


def test_generated_candidate_check_rejects_positive_parent(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "check_candidate", ROOT / "scripts/adhoc/check_motility_candidate_20261116.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    terms = rows()
    rdf = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
    owl = "{http://www.w3.org/2002/07/owl#}"
    rdfs = "{http://www.w3.org/2000/01/rdf-schema#}"
    definition = "{http://purl.obolibrary.org/obo/}IAO_0000115"
    iri = "https://w3id.org/metpo/"
    root = ET.Element(rdf + "RDF")
    parents = {
        1000701: 1000059,
        1000702: 1000701,
        1000703: 1000701,
        1000704: 1000702,
        1000705: 1000702,
        1000706: 1000702,
    }
    negative_parent = None
    for term, parent in parents.items():
        node = ET.SubElement(root, owl + "Class", {rdf + "about": iri + str(term)})
        parent_node = ET.SubElement(
            node, rdfs + "subClassOf", {rdf + "resource": iri + str(parent)}
        )
        ET.SubElement(node, definition).text = terms[f"METPO:{term}"]["definition"]
        if term == 1000703:
            negative_parent = parent_node
    path = tmp_path / "candidate.owl"
    ET.ElementTree(root).write(path)
    assert module.inspect(path, ROOT / "src/templates/metpo_sheet.tsv")["status"] == "passed"
    negative_parent.set(rdf + "resource", iri + "1000702")
    ET.ElementTree(root).write(path)
    with pytest.raises(ValueError, match="Unexpected parent for 1000703"):
        module.inspect(path, ROOT / "src/templates/metpo_sheet.tsv")
