#!/usr/bin/env python3
"""
csv_temperature_to_rdf.py
-------------------------

Read a CSV that already contains RDF-like triples
   subject , predicate , object
(object = free-text temperature sentence)

Emit Turtle in which

   <subject> <predicate> _:pgXX .

and _:pgXX is a env-parse:ParseGroup that follows
environmental_parse_model_v0.3.

Preference cascade
  1) anchored full-match numeric regexes
  2) categorical keyword fallback (plus residual text)
  3) no match  → ParseGroup has 0 ParseComponents
"""

from __future__ import annotations
import re
import sys
from decimal import Decimal
from pathlib import Path
from typing import List, Dict, Optional

import pandas as pd
from rdflib import Graph, Namespace, Literal, BNode
from rdflib.namespace import RDF, XSD

# ---------------------------------------------------------------------
# 0.  REGEX CONFIGURATION
# ---------------------------------------------------------------------
LIST_PAIR_RE = re.compile(
    r"(?P<v1>-?\d+(?:\.\d+)?)\s*(?:and|or)\s*"
    r"(?P<v2>-?\d+(?:\.\d+)?)\s*[°º]?\s*C\b",
    re.I,
)

FULL_PATTERNS: List[str] = [
    # <<< INSERT your complete list here.  Shortened for the example. >>>
    r"\s*-?(?:\d+(?:\.\d+)?|\.\d+)\s*(?:°\s*C?)?[,.;]?",
    r"\s*-?(?:\d+(?:\.\d+)?|\.\d+)\s*(?:°\s*C?)?\s*(?:to|[-–—])\s*-?"
    r"(?:\d+(?:\.\d+)?|\.\d+)\s*(?:°\s*C?)?[,.;]?",
    r"\s*-?\d+(?:\.\d+)?\s*(?:,|and|or|OR)\s*-?\d+(?:\.\d+)?\s*[°º]?\s*C?\s*[,.;]?$",
    r"\s*-?\d+(?:\.\d+)?(?:\s*,\s*-?\d+(?:\.\d+)?){2,}\s*[°º]?\s*C?\s*[,.;]?$",
]

CATS: Dict[str, str] = {
    "psychrophile": r"\b(?:psychrophil(?:e|ic)|psychrotolerant|psychrotrophic|cold[- ]adapted)\b",
    "mesophile": r"\bmesophil(?:e|es|ic)\b",
    "thermotolerant": r"\b(?:thermotolerant|moderate(?:ly)? thermophil(?:e|ic)|slightly thermophil(?:e|ic))\b",
    "thermophile": r"\b(?:thermophil(?:e|ic)|obligate(?:ly)? thermophil(?:e|ic)|strictly thermophil(?:e|ic))\b",
    "hyperthermophile": r"\b(?:hyperthermophil(?:e|ic)|extreme(?:ly)? thermophil(?:e|ic))\b",
}
CATS_RX = {k: re.compile(v, re.I) for k, v in CATS.items()}

DELIM_RE = re.compile(
    r""",\s*(?![^()]*\))      # comma not inside ()
      |\s+\band\b\s+
      |\s+\bor\b\s+""",
    re.I | re.X,
)

RANGE_RE = re.compile(
    r"(?P<min>-?\d+(?:\.\d+)?)\s*[°º]?\s*C?\s*"
    r"(?:to|[-–—‒−])\s*"
    r"(?P<max>-?\d+(?:\.\d+)?)(?:\s*[°º]?\s*C?)?",
    re.I,
)
SPOT_RE = re.compile(
    r"(?P<qual>[<>≥≤⩾⩽]|(?:optimum|max(?:imum)?|min(?:imum)?|above|below))?\s*"
    r"(?P<val>(?<!\d[--–—−])\-?\d+(?:\.\d+)?)\s*[°º]?\s*C\b",
    re.I,
)
QUAL_MAP = {
    "<": "maximum", "≤": "maximum", "⩽": "maximum", "below": "maximum", "maximum": "maximum",
    ">": "minimum", "≥": "minimum", "⩾": "minimum", "above": "minimum", "minimum": "minimum",
    "optimum": "optimum", "min": "minimum", "max": "maximum",
}

# ---------------------------------------------------------------------
# 1.  NAMESPACES
# ---------------------------------------------------------------------
ENV = Namespace("http://example.org/env-parse#")


# ---------------------------------------------------------------------
# 2.  COMPILED FULL-MATCH REGEX
# ---------------------------------------------------------------------
def compile_full(patterns: List[str]) -> re.Pattern:
    anchored = [
        p if p.startswith("^") and p.endswith("$") else f"^{p}$"
        for p in patterns
    ]
    return re.compile("|".join(anchored), re.I | re.S)


FULL_RX = compile_full(FULL_PATTERNS)


# ---------------------------------------------------------------------
# 3.  SMALL PARSING HELPERS
# ---------------------------------------------------------------------
def split_chunks(text: str) -> List[str]:
    parts = [p.strip() for p in DELIM_RE.split(text) if p.strip()]
    return parts or [text.strip()]


def numeric_components(chunk: str) -> list[dict]:
    comps: list[dict] = []
    covered: list[tuple[int, int]] = []

    # ── A.  ‘shared-unit’ pairs / triples  ────────────────────────────
    pair = re.compile(
        r"""
        (?P<num1>-?\d+(?:\.\d+)?)          # first number
        \s*(?:,|and|or|OR)\s*              # delimiter
        (?P<num2>-?\d+(?:\.\d+)?)          # second number
        (?:\s*(?:,|and|or|OR)\s*
            (?P<num3>-?\d+(?:\.\d+)?))?    # optional third number
        \s*[°º]?\s*C\b                     # one shared unit
        """,
        re.I | re.VERBOSE,
    )

    for m in pair.finditer(chunk):
        unit = "Cel"
        n1, n2, n3 = m.group("num1"), m.group("num2"), m.group("num3")
        comps.append(dict(component_text=f"{n1} °C", spot_value=Decimal(n1), unit=unit))
        comps.append(dict(component_text=f"{n2} °C", spot_value=Decimal(n2), unit=unit))
        if n3:
            comps.append(dict(component_text=f"{n3} °C", spot_value=Decimal(n3), unit=unit))
        covered.append(m.span())

    # ── B.  your old RANGE logic  ─────────────────────────────────────
    for m in RANGE_RE.finditer(chunk):
        if any(cs <= m.start() < ce for cs, ce in covered):
            continue
        comps.append(
            dict(component_text=m.group(0).strip(),
                 minimum_value=Decimal(m.group("min")),
                 maximum_value=Decimal(m.group("max")),
                 unit="Cel")
        )
        covered.append(m.span())

    # ── C.  your old SPOT logic  ──────────────────────────────────────
    for m in SPOT_RE.finditer(chunk):
        if any(cs <= m.start() < ce for cs, ce in covered):
            continue
        qualifier = None
        qraw = m.group("qual")
        if qraw:
            qualifier = QUAL_MAP.get(qraw.lower(), qraw)
        comps.append(
            dict(component_text=m.group(0).strip(),
                 spot_value=Decimal(m.group("val")),
                 qualifier_label=qualifier,
                 unit="Cel")
        )
    return comps


def categorical_components(text: str) -> List[Dict]:
    comps = []
    residual = text
    for label, rx in CATS_RX.items():
        for m in rx.finditer(text):
            token = m.group(0)
            comps.append(dict(component_text=token, categorical_label=label))
            residual = residual.replace(token, "")
    residual = residual.strip()
    if residual:
        comps.append(dict(component_text=residual, unparsed_text=residual))
    return comps


# ---------------------------------------------------------------------
# 4.  CSV ➝ RDF GRAPH
# ---------------------------------------------------------------------
def csv_to_graph(csv_file: Path,
                 subj_col: str = "subject",
                 pred_col: str = "predicate",
                 obj_col: str = "object") -> Graph:
    df = pd.read_csv(csv_file, dtype=str)
    df = df.fillna("")

    # retain only the first occurrence of each identical triple
    df = df.drop_duplicates(subset=["subject", "predicate", "object"], keep="first")

    g = Graph()
    g.bind("env", ENV)

    pg_index = 0
    pc_index = 0

    for _, row in df.iterrows():
        subject = row[subj_col].strip()
        predicate = row[pred_col].strip()
        raw_text = row[obj_col].strip()

        if not (subject and predicate and raw_text):
            continue  # skip malformed rows

        pg_index += 1
        pg = BNode(f"pg{pg_index}")

        # --- outermost triple retains original SPO ---------------------
        g.add((g.resource(subject).identifier,  # ensures URIRef
               g.resource(predicate).identifier,
               pg))

        # --- ParseGroup skeleton --------------------------------------
        g.add((pg, RDF.type, ENV.ParseGroup))
        g.add((pg, ENV.raw_text, Literal(raw_text)))

        # decide which parsing branch to follow
        pcs: List[Dict] = []
        if FULL_RX.match(raw_text):  # 1. full match
            for chunk in split_chunks(raw_text):
                pcs.extend(numeric_components(chunk))
        if not pcs:  # 2. categorical
            pcs = categorical_components(raw_text)
        # 3. pcs may stay empty (raw-text only group)

        # materialise ParseComponents
        for comp in pcs:
            pc_index += 1
            pc = BNode(f"pc{pc_index}")

            g.add((pg, ENV.parse_component, pc))
            g.add((pc, RDF.type, ENV.ParseComponent))
            g.add((pc, ENV.component_text, Literal(comp["component_text"])))

            if "minimum_value" in comp:
                g.add((pc, ENV.minimum_value,
                       Literal(comp["minimum_value"], datatype=XSD.decimal)))
                g.add((pc, ENV.maximum_value,
                       Literal(comp["maximum_value"], datatype=XSD.decimal)))

            if "spot_value" in comp:
                g.add((pc, ENV.spot_value,
                       Literal(comp["spot_value"], datatype=XSD.decimal)))

            if comp.get("unit"):
                g.add((pc, ENV.unit, Literal(comp["unit"])))

            if comp.get("categorical_label"):
                g.add((pc, ENV.categorical_label,
                       Literal(comp["categorical_label"])))

            if comp.get("qualifier_label"):
                g.add((pc, ENV.qualifier_label,
                       Literal(comp["qualifier_label"])))

            if comp.get("unparsed_text"):
                g.add((pc, ENV.unparsed_text,
                       Literal(comp["unparsed_text"])))

    return g


# ---------------------------------------------------------------------
# 5.  CLI
# ---------------------------------------------------------------------
def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python csv_temperature_to_rdf.py  Out_11.csv  > parsed.ttl")

    path = Path(sys.argv[1])
    if not path.is_file():
        sys.exit(f"File not found: {path}")

    graph = csv_to_graph(path)
    sys.stdout.write(graph.serialize(format="turtle"))


if __name__ == "__main__":
    main()
