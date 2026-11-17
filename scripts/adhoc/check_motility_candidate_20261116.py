#!/usr/bin/env python3
"""Inspect a regenerated RDF/XML candidate against the maintained source template."""

import argparse
import csv
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path


def inspect(path, template):
    with template.open() as stream:
        rows = {row["ID"]: row for row in csv.DictReader(stream, delimiter="\t")}
    root = ET.parse(path).getroot()
    rdf = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
    owl = "{http://www.w3.org/2002/07/owl#}"
    rdfs = "{http://www.w3.org/2000/01/rdf-schema#}"
    definition = "{http://purl.obolibrary.org/obo/}IAO_0000115"
    iri = "https://w3id.org/metpo/"
    expected = {
        1000701: 1000059,
        1000702: 1000701,
        1000703: 1000701,
        1000704: 1000702,
        1000705: 1000702,
        1000706: 1000702,
    }
    result = []
    for term, parent in expected.items():
        nodes = [
            node
            for node in root.findall(owl + "Class")
            if node.get(rdf + "about") == iri + str(term)
        ]
        if len(nodes) != 1:
            raise ValueError(f"Missing or repeated term {term}")
        node = nodes[0]
        actual = [n.get(rdf + "resource") for n in node.findall(rdfs + "subClassOf")]
        if actual != [iri + str(parent)]:
            raise ValueError(f"Unexpected parent for {term}: {actual}")
        if node.findtext(definition) != rows[f"METPO:{term}"]["definition"]:
            raise ValueError(f"Generated definition differs from template for {term}")
        result.append(
            {
                "id": f"METPO:{term}",
                "parent": f"METPO:{parent}",
                "definition_matches_template": True,
            }
        )
    return {
        "candidate_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "template_sha256": hashlib.sha256(template.read_bytes()).hexdigest(),
        "terms": result,
        "status": "passed",
        "release_status": "unmerged candidate",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--template", type=Path, default=Path("src/templates/metpo_sheet.tsv"))
    args = parser.parse_args()
    print(json.dumps(inspect(args.candidate, args.template), indent=2))
