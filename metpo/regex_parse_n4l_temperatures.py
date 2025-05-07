#!/usr/bin/env python3
"""env_parse_cli.py

Command‑line tool that converts free‑text environmental condition descriptions
(temperature, pH, oxygen, etc.) stored in a CSV (graph, subject, predicate, object)
into RDF triples that follow the Environmental Condition Parse Ontology Pattern
(ParseGroup / ParseComponent).

Features
--------
* **Deterministic** rule‑based parsing for temperature (default) with hooks for
  additional factors.
* **Qualifiers & categorical labels** recognised via configurable lookup tables.
* **Unit normalisation** to UCUM codes using Pint (relies on Pint's built‑in unit
  definitions, so no external download is required).
* **Streaming** CSV processing for large files.
* **RDF output** via rdflib (Turtle, N‑Triples, or any format rdflib supports).
* **CLI** built with Click; supports progress bars (tqdm) and logging verbosity.

Usage example:
```
parse-env --input n4l-temperature.csv --output parsed.ttl \
          --factor temperature --format turtle --graph-uri https://example.org/temp
```
"""

from __future__ import annotations

import csv
import logging
import re
import sys
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Tuple

import click
from pint import UnitRegistry
from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD
from tqdm import tqdm

###############################################################################
# Configuration tables
###############################################################################

# UCUM unit registry (built‑in to Pint; no external definitions needed)
ureg = UnitRegistry()

# Namespaces
ENV = Namespace("http://example.org/env-parse#")
DEFAULT_GRAPH = Namespace("http://example.org/env-parse/graph/")

# Categorical & qualifier tokens for temperature (lower‑case, punctuation‑stripped)
CATEGORICAL_TOKENS_TEMP = {
    "psychrophilic",
    "psychrotolerant",
    "mesophilic",
    "moderately thermophilic",
    "thermophilic",
    "hyperthermophilic",
    "thermotolerant",
    "cryotolerant",
    "heat resistant",
    "cold adapted",
    "anaerobic",
    "aerobic",
}

QUALIFIER_TOKENS = {
    "optimum": {"optimum", "optimal", "grows best", "best"},
    "upper limit": {"upper limit", "max", "up to", "below", "≤", "<"},
    "lower limit": {"lower limit", "min", "above", "≥", ">"},
}

###############################################################################
# Regex patterns for numeric extraction (temperature‑specific)
###############################################################################

RANGE_REGEX = re.compile(
    r"(?P<min>-?\d+(?:\.\d+)?)\s*[–\-]\s*(?P<max>-?\d+(?:\.\d+)?)\s*[°\s]*[Cc]",
    re.U,
)

SPOT_REGEX = re.compile(
    r"(?P<val>-?\d+(?:\.\d+)?)\s*[°\s]*[Cc]",
    re.U,
)


###############################################################################
# Helper functions
###############################################################################

def _normalise_text(text: str) -> str:
    """Lowercase and strip punctuation/extra whitespace for token matching."""
    return re.sub(r"[\s,.()]+", " ", text.lower()).strip()


def _match_categorical_and_qualifier(text: str) -> Tuple[str | None, str | None]:
    """Return detected categorical_label and qualifier_label (if any)."""
    clean = _normalise_text(text)

    categorical = next((tok for tok in CATEGORICAL_TOKENS_TEMP if tok in clean), None)

    qualifier = None
    for label, variants in QUALIFIER_TOKENS.items():
        if any(v in clean for v in variants):
            qualifier = label
            break

    return categorical, qualifier


def _normalise_unit(raw: str) -> str | None:
    """Return UCUM unit code for temperature strings; currently only Cel."""
    if "c" in raw.lower():
        return "Cel"  # Celsius in UCUM
    return None


def componentize_temperature(text: str) -> Tuple[List[Dict], str]:
    """Return list of component dicts and leftover unparsed string."""
    remaining = text
    components: List[Dict] = []

    # 1. Ranges
    for m in RANGE_REGEX.finditer(text):
        comp = {
            "component_text": m.group(0).strip(),
            "minimum_value": Decimal(m.group("min")),
            "maximum_value": Decimal(m.group("max")),
            "unit": _normalise_unit(m.group(0)),
        }
        components.append(comp)
        remaining = remaining.replace(m.group(0), "", 1)

    # 2. Single values (optimum etc.)
    for m in SPOT_REGEX.finditer(text):
        comp_text = m.group(0).strip()
        categorical, qualifier = _match_categorical_and_qualifier(text)
        comp = {
            "component_text": comp_text,
            "spot_value": Decimal(m.group("val")),
            "unit": _normalise_unit(comp_text),
            "categorical_label": categorical,
            "qualifier_label": qualifier,
        }
        components.append(comp)
        remaining = remaining.replace(m.group(0), "", 1)

    # 3. Pure categorical / qualifier words that have no numbers
    if not components:
        categorical, qualifier = _match_categorical_and_qualifier(text)
        if categorical or qualifier:
            components.append({
                "component_text": text.strip(),
                "categorical_label": categorical,
                "qualifier_label": qualifier,
            })
            remaining = ""

    leftover = remaining.strip()
    return components, leftover


def datatype_of(slot: str):
    mapping = {
        "minimum_value": XSD.decimal,
        "maximum_value": XSD.decimal,
        "spot_value": XSD.decimal,
        "unit": XSD.string,
        "categorical_label": XSD.string,
        "qualifier_label": XSD.string,
        "component_text": XSD.string,
        "unparsed_text": XSD.string,
    }
    return mapping.get(slot, XSD.string)


###############################################################################
# CLI
###############################################################################

@click.command()
@click.option("--input", "input_path", type=click.Path(exists=True, path_type=Path), required=True,
              help="CSV file with columns graph,subject,predicate,object")
@click.option("--output", "output_path", type=click.Path(path_type=Path), required=True,
              help="Destination RDF file (extension decides format, e.g. .ttl, .nt)")
@click.option("--factor", type=click.Choice(["temperature"], case_sensitive=False), default="temperature",
              help="Environmental factor to parse (more coming soon)")
@click.option("--format", "rdf_format", type=str, default=None,
              help="RDF serialization (default inferred from output extension)")
@click.option("--graph-uri", type=str, default=str(DEFAULT_GRAPH),
              help="Named graph URI to place restated triples in.")
@click.option("--verbose", is_flag=True, help="Enable debug logging")
def main(input_path: Path, output_path: Path, factor: str, rdf_format: str | None, graph_uri: str, verbose: bool):
    """Parse environmental condition literals into structured RDF."""

    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO,
                        format="%(levelname)s: %(message)s")

    g = Graph(identifier=URIRef(graph_uri))
    g.bind("env", ENV)

    with input_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if set(reader.fieldnames or []) != {"graph", "subject", "predicate", "object"}:
            logging.error("CSV must have header graph,subject,predicate,object")
            sys.exit(1)

        for row in tqdm(reader, desc="Parsing rows"):
            subj = URIRef(row["subject"].strip())
            pred = URIRef(row["predicate"].strip())
            obj_text = row["object"].strip()

            # Original triple (verbatim)
            g.add((subj, pred, Literal(obj_text)))

            # Parsed structure
            pg = BNode()
            g.add((subj, pred, pg))
            g.add((pg, RDF.type, ENV.ParseGroup))
            g.add((pg, ENV.raw_text, Literal(obj_text)))

            components, leftover = componentize_temperature(obj_text)  # factor‑specific
            if leftover:
                components.append({
                    "component_text": leftover,
                    "unparsed_text": leftover,
                })

            for comp_dict in components:
                comp = BNode()
                g.add((pg, ENV.parse_component, comp))
                g.add((comp, RDF.type, ENV.ParseComponent))
                for slot, val in comp_dict.items():
                    if val is None or val == "":
                        continue
                    g.add((comp, ENV[slot], Literal(val, datatype=datatype_of(slot))))

    rdf_format = rdf_format or output_path.suffix.lstrip(".") or "turtle"
    g.serialize(destination=str(output_path), format=rdf_format)
    logging.info("Wrote %d triples to %s", len(g), output_path)


if __name__ == "__main__":
    main()
