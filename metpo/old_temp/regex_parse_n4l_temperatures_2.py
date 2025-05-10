#!/usr/bin/env python3
"""
csv_temperature_to_rdf_simple.py
One-pass, no-frills temperature parser that covers
ranges, lists, single values + basic qualifiers.
"""

import re, sys
from decimal import Decimal
from pathlib import Path
from typing import List, Dict, Tuple

import pandas as pd
from rdflib import Graph, Namespace, Literal, BNode, URIRef
from rdflib.namespace import RDF, XSD

ENV = Namespace("http://example.org/env-parse#")

# ── 1. small cleaner ──────────────────────────────────────────
DASHES = "–—−"
HAIRSP = "\u2000-\u200F\u202F\u205F"
_CLEAN_RX = re.compile(f"[{HAIRSP}]|([{DASHES}])|°\\s*C", re.I)


def _clean(txt: str) -> str:
    def sub(m: re.Match) -> str:
        if m.group(1):  # any exotic dash
            return "-"
        return "°C"  # “° C”

    return _CLEAN_RX.sub(sub, txt).replace("℃", "°C")


# ── 2. core extractor ─────────────────────────────────────────
VAL = r"-?\d+(?:\.\d+)?"
UNIT = r"°C|C\b"
TOKEN_RX = re.compile(rf"(?P<val>{VAL})(?=\s*(?:{UNIT}|[ ,;]|$))", re.I)
RANGE_SEP = re.compile(r"\s*(?:-|–|to)\s*", re.I)
LIST_SEP = re.compile(r"\s*(?:,|and|or)\s*", re.I)
QUAL_RX = re.compile(r"(up to|upto|above|below|≤|>=?|≥|<)", re.I)


def extract_components(text: str) -> List[Dict]:
    comps: List[Dict] = []
    tokens = [(m.start(), m.group("val")) for m in TOKEN_RX.finditer(text)]
    i = 0
    while i < len(tokens):
        pos, v1 = tokens[i]

        # ----- range look-ahead ------------------------------------------------
        if i + 1 < len(tokens):
            between = text[pos + len(v1): tokens[i + 1][0]]
            if RANGE_SEP.fullmatch(between):
                v2 = tokens[i + 1][1]
                comps.append(dict(component_text=f"{v1}-{v2} °C",
                                  minimum_value=Decimal(v1),
                                  maximum_value=Decimal(v2),
                                  unit="Cel"))
                i += 2
                continue

        # ----- shared-unit list (two numbers) ----------------------------------
        if i + 1 < len(tokens):
            between = text[pos + len(v1): tokens[i + 1][0]]
            if LIST_SEP.fullmatch(between):
                # check that right-most carries °C
                tail = text[tokens[i + 1][0] + len(tokens[i + 1][1]):]
                if re.match(r"\s*°?C", tail, re.I):
                    for v in (v1, tokens[i + 1][1]):
                        comps.append(dict(component_text=f"{v} °C",
                                          spot_value=Decimal(v),
                                          unit="Cel"))
                    i += 2
                    continue

        # ----- single / qualifier ---------------------------------------------
        left20 = text[max(0, pos - 20):pos].lower()
        m_qual = QUAL_RX.search(left20)
        qual = None
        if m_qual:
            qual_token = m_qual.group(1)
            qual = {"up to": "maximum", "upto": "maximum",
                    "above": "minimum", "below": "maximum",
                    ">": "minimum", "<": "maximum",
                    "≥": "minimum", "≤": "maximum"}.get(qual_token, None)

        comps.append(dict(component_text=f"{v1} °C",
                          spot_value=Decimal(v1),
                          qualifier_label=qual,
                          unit="Cel"))
        i += 1
    return comps


# ── 3. categorical (unchanged) ───────────────────────────────
CATS = {"mesophile": r"\bmesophil(?:e|ic)\b",
        "thermophile": r"\bthermophil(?:e|ic)\b"}
CATS_RX = {k: re.compile(v, re.I) for k, v in CATS.items()}


def categorical(text: str) -> List[Dict]:
    for lbl, rx in CATS_RX.items():
        if rx.search(text):
            return [dict(component_text=text, categorical_label=lbl)]
    return []


# ── 4. CSV → RDF (same skeleton) ─────────────────────────────
def csv_to_graph(csv: Path, s="subject", p="predicate", o="object") -> Graph:
    df = pd.read_csv(csv, dtype=str).fillna("")
    g, pg_cnt, pc_cnt = Graph(), 0, 0
    g.bind("env", ENV)
    seen: Dict[Tuple[str, str, str], BNode] = {}

    for _, row in df.iterrows():
        subj, pred, raw = row[s].strip(), row[p].strip(), _clean(row[o]).strip()
        if not raw:  # skip empties
            continue

        key = (subj, pred, raw)
        pg = seen.get(key)
        if not pg:
            pg_cnt += 1
            pg = BNode(f"pg{pg_cnt}")
            seen[key] = pg
            g.add((pg, RDF.type, ENV.ParseGroup))
            g.add((pg, ENV.raw_text, Literal(raw)))

            comps = extract_components(raw) or categorical(raw) \
                    or [dict(component_text=raw, unparsed_text=raw)]

            for c in comps:
                pc_cnt += 1
                pc = BNode(f"pc{pc_cnt}")
                g.add((pg, ENV.parse_component, pc))
                g.add((pc, RDF.type, ENV.ParseComponent))
                g.add((pc, ENV.component_text, Literal(c["component_text"])))
                if "minimum_value" in c:
                    g.add((pc, ENV.minimum_value, Literal(c["minimum_value"], datatype=XSD.decimal)))
                    g.add((pc, ENV.maximum_value, Literal(c["maximum_value"], datatype=XSD.decimal)))
                if "spot_value" in c:
                    g.add((pc, ENV.spot_value, Literal(c["spot_value"], datatype=XSD.decimal)))
                if c.get("unit"):            g.add((pc, ENV.unit, Literal(c["unit"])))
                if c.get("qualifier_label"): g.add((pc, ENV.qualifier_label, Literal(c["qualifier_label"])))
                if c.get("categorical_label"): g.add((pc, ENV.categorical_label, Literal(c["categorical_label"])))
                if c.get("unparsed_text"):   g.add((pc, ENV.unparsed_text, Literal(c["unparsed_text"])))

        g.add((URIRef(subj), URIRef(pred), pg))

    return g


# ── 5. CLI ───────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python csv_temperature_to_rdf_simple.py  In.csv  > Out.ttl")
    path = Path(sys.argv[1])
    graph = csv_to_graph(path)
    sys.stdout.write(graph.serialize(format="turtle"))
