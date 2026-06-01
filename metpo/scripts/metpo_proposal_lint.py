"""Deterministic guardrails for METPO term additions and released-content audits.

Lints a ROBOT-template TSV (the canonical METPO sheet export, or a proposal template
such as kg-microbe's ``metpo_proposal_*_robot.tsv``). It keys off the ROBOT directive
row (row 2), so it is schema-aware rather than column-position-dependent, and works on
the classes sheet, the properties sheet, ``stubs.tsv`` and ``deprecated.tsv``.

Two modes:

* **review** a proposed batch before it enters METPO:
  ``metpo-proposal-lint PROPOSAL.tsv --known src/templates/metpo_sheet.tsv --mode submit``
* **audit** released content for existing bad practices:
  ``metpo-proposal-lint src/templates/metpo_sheet.tsv --mode draft``

It is meant to run both as a METPO CI gate and as a pre-flight in the generator repos
(kg-microbe / TraitMech / metpo-kgm-studio) before a proposal PR is opened. It catches
things the ODK build and ELK reasoner cannot: a logically-consistent-but-wrong bin
formula (#357), scrambled threshold synonyms (#356/#432), mapping CURIEs parked in
definition_source (#344), and parents that bypass ROBOT's label-resolution safety net
via CURIE form.

NOTE: ID-RANGE encodes the current observed convention (classes METPO:1xxxxxx,
properties METPO:2xxxxxx). The term-IRI scheme is an open question (#16/#434/#436);
revisit this check when that settles.
"""

import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

import click

# An OBO/ontology *class* CURIE in definition_source means "mapping", not "source".
ONTOLOGY_PREFIXES = {
    "GO",
    "PATO",
    "OMP",
    "MICRO",
    "CHEBI",
    "UBERON",
    "CL",
    "ENVO",
    "OBI",
    "SO",
    "NCBITaxon",
    "PO",
    "FOODON",
    "UO",
    "APO",
    "FYPO",
    "UPHENO",
    "ECOCORE",
    "OHMI",
    "BFO",
    "PHIPO",
    "MP",
    "HP",
    "MONDO",
}
VALID_TYPES = ("owl:Class", "owl:ObjectProperty", "owl:DataProperty", "owl:AnnotationProperty")
PROPERTY_TYPES = ("owl:ObjectProperty", "owl:DataProperty", "owl:DatatypeProperty")
TOL = 0.011  # numeric tolerance for threshold comparison

_SIMPLE_ROLES = {"ID": "id", "LABEL": "label", "TYPE": "type", "DOMAIN": "domain", "RANGE": "range"}
_NEEDLE_ROLES = (
    ("IAO:0000115", "definition"),
    ("IAO:0000119", "def_source"),
    ("hasDbXref", "xref"),
    ("owl:deprecated", "deprecated"),
    ("range_min", "range_min"),
    ("range_max", "range_max"),
)


class Finding:
    __slots__ = ("code", "msg", "rid", "sev")

    def __init__(self, sev, code, rid, msg):
        self.sev, self.code, self.rid, self.msg = sev, code, rid, msg


def read_template(path):
    """Return (labels, directives, data_rows, roles) keyed off the ROBOT directive row."""
    with Path(path).open(encoding="utf-8") as fh:
        rows = list(csv.reader(fh, delimiter="\t"))
    if len(rows) < 2:
        raise click.ClickException(f"{path}: need a label row + a ROBOT directive row")
    labels, directives = rows[0], rows[1]
    data = [r for r in rows[2:] if r and r[0].strip()]
    roles = {"exact_syn": [], "rel_syn": []}
    for i, raw in enumerate(directives):
        d = raw.strip()
        if d in _SIMPLE_ROLES:
            roles[_SIMPLE_ROLES[d]] = i
        elif d.startswith(("SC", "SP")):
            roles["parent"] = i
        elif d.startswith("EC"):
            roles["ec"] = i
        elif "hasExactSynonym" in d:
            roles["exact_syn"].append(i)
        elif "hasRelatedSynonym" in d:
            roles["rel_syn"].append(i)
        else:
            for needle, key in _NEEDLE_ROLES:
                if needle in d and key not in roles:
                    roles[key] = i
                    break
    return labels, directives, data, roles


def cell(r, i):
    return r[i].strip() if (i is not None and i < len(r)) else ""


def fnum(s):
    try:
        return float((s or "").strip())
    except ValueError:
        return None


def load_known(paths):
    labels, ids = set(), set()
    for p in paths:
        try:
            _, _, data, roles = read_template(p)
        except click.ClickException:
            continue
        li = roles.get("label", 1)
        for r in data:
            if r[0].startswith("METPO:"):
                ids.add(r[0].strip())
                labels.add(cell(r, li))
    return labels, ids


def parse_bound(formula):
    """(lower, upper) from an EC facet like xsd:decimal[>= 40] / [>= 10, <= 22]."""
    lo = up = None
    for op, num in re.findall(r"(<=|>=|<|>)\s*([0-9.]+)", formula or ""):
        v = float(num)
        if op in (">=", ">"):
            lo = v
        else:
            up = v
    return lo, up


def parse_syn_threshold(v):
    """(lower, upper) from a threshold-encoded synonym.

    Handles an optional short prefix code and prefix-less forms, e.g.
    ``GC_<=42.65``, ``GC_42.65_57.0``, ``TO_10_to_22``, and bare ``10_to_14`` /
    ``8_to_10`` (the pH-range synonyms that drop their ``pHR_`` prefix). Returns
    ``(None, None)`` unless the whole (prefix-stripped) token is a threshold
    expression, so ordinary synonyms with stray digits are not misread.
    """
    body = re.sub(r"^[A-Za-z]{1,6}_", "", v.strip())
    if not re.fullmatch(
        r"(?:<=|>=|<|>)?\s*\d+(?:\.\d+)?(?:\s*(?:_to_|_|-)\s*\d+(?:\.\d+)?)?\+?", body
    ):
        return (None, None)
    nums = [float(x) for x in re.findall(r"[0-9]+\.?[0-9]*", body)]
    if not nums:
        return (None, None)
    if "<=" in body or body.startswith("<"):
        return (None, nums[-1])
    if ">=" in body or body.startswith(">") or body.endswith("+"):
        return (nums[0], None)
    if len(nums) >= 2:
        return (min(nums), max(nums))
    return (None, None)


def check_id_type(rid, typ, is_metpo):
    """ID-RANGE + TYPE-VOCAB for a non-deprecated row."""
    out = []
    if is_metpo:
        m = re.match(r"^METPO:(\d)\d{6}$", rid)
        isprop = typ in PROPERTY_TYPES
        if not m:
            out.append(Finding("ERROR", "ID-RANGE", rid, "METPO ID is not 7 digits"))
        elif isprop and m.group(1) != "2":
            out.append(Finding("ERROR", "ID-RANGE", rid, "property ID must be METPO:2xxxxxx"))
        elif not isprop and m.group(1) != "1":
            out.append(Finding("ERROR", "ID-RANGE", rid, "class ID must be METPO:1xxxxxx"))
    if typ == "owl:DatatypeProperty":
        out.append(
            Finding(
                "ERROR",
                "TYPE-VOCAB",
                rid,
                "use 'owl:DataProperty' (METPO house style), not 'owl:DatatypeProperty'",
            )
        )
    elif typ not in VALID_TYPES:
        out.append(Finding("ERROR", "TYPE-VOCAB", rid, f"unexpected TYPE '{typ}'"))
    return out


def check_parent(rid, parent_cell, resolve_ids, resolve_labels):
    out = []
    for p in [x.strip() for x in parent_cell.split("|") if x.strip()]:
        if p == "METPO:1000000":
            out.append(
                Finding(
                    "ERROR",
                    "PARENT",
                    rid,
                    "parent 'METPO:1000000' is the nonexistent/over-general root",
                )
            )
        elif re.match(r"^METPO:\d+$", p):
            out.append(
                Finding(
                    "WARN",
                    "HOUSE-STYLE",
                    rid,
                    f"parent given as CURIE '{p}'; sheet convention is parent-by-label "
                    "(CURIE parents also bypass ROBOT's label-resolution safety net)",
                )
            )
            if p not in resolve_ids:
                out.append(Finding("ERROR", "PARENT", rid, f"parent CURIE '{p}' does not resolve"))
        elif p not in resolve_labels:
            out.append(
                Finding(
                    "ERROR", "PARENT", rid, f"parent label '{p}' does not resolve to a known class"
                )
            )
    return out


def check_definition(rid, r, roles, mode):
    out = []
    if "definition" in roles and not cell(r, roles["definition"]) and mode == "submit":
        out.append(Finding("ERROR", "DEF-MISSING", rid, "empty definition"))
    if "def_source" not in roles:
        return out
    toks = [x.strip() for x in cell(r, roles["def_source"]).split("|") if x.strip()]
    if not toks and mode == "submit":
        out.append(Finding("ERROR", "SRC-MISSING", rid, "empty definition_source"))
    for tok in toks:
        pm = re.match(r"^([A-Za-z][A-Za-z0-9]*):", tok)
        if tok == "TODO:add_citation":
            if mode == "submit":
                out.append(
                    Finding("ERROR", "SRC-MISSING", rid, "definition_source is TODO:add_citation")
                )
        elif pm and pm.group(1) in ONTOLOGY_PREFIXES:
            out.append(
                Finding(
                    "ERROR",
                    "SRC-ISMAP",
                    rid,
                    f"ontology-class CURIE '{tok}' in definition_source; belongs in a "
                    "mapping predicate (skos:* / oboInOwl:hasDbXref)",
                )
            )
    return out


def row_bounds(r, roles):
    """Authoritative numeric bounds for a row: EC formula preferred, then range_min/max."""
    alo, aup = parse_bound(cell(r, roles.get("ec")))
    if alo is None:
        alo = fnum(cell(r, roles.get("range_min")))
    if aup is None:
        aup = fnum(cell(r, roles.get("range_max")))
    return alo, aup


def check_formula_synonym(rid, label_text, r, roles, alo, aup):
    out = []
    ec = cell(r, roles.get("ec"))
    if ec:
        flo, fup = parse_bound(ec)
        if re.search(r"\b(high|maximum|max)\b", label_text) and flo is None and fup is not None:
            out.append(
                Finding(
                    "ERROR",
                    "FORMULA-DIR",
                    rid,
                    f"label says high/max but formula only bounds <= {fup}; expected a lower bound (>=)",
                )
            )
        if re.search(r"\b(low|minimum|min)\b", label_text) and fup is None and flo is not None:
            out.append(
                Finding(
                    "ERROR",
                    "FORMULA-DIR",
                    rid,
                    f"label says low/min but formula only bounds >= {flo}; expected an upper bound (<=)",
                )
            )
    if alo is None and aup is None:
        return out
    for i in roles["exact_syn"] + roles["rel_syn"]:
        slo, sup = parse_syn_threshold(cell(r, i))
        if slo is None and sup is None:
            continue
        bad = None
        if slo is not None and alo is not None and abs(slo - alo) > TOL:
            bad = f"synonym lower {slo} != bound {alo}"
        elif sup is not None and aup is not None and abs(sup - aup) > TOL:
            bad = f"synonym upper {sup} != bound {aup}"
        elif sup is not None and alo is not None and sup < alo - TOL:
            bad = f"synonym ceiling {sup} below bin floor {alo} (contradiction)"
        elif slo is not None and aup is not None and slo > aup + TOL:
            bad = f"synonym floor {slo} above bin ceiling {aup} (contradiction)"
        if bad:
            out.append(
                Finding("ERROR", "SYN-THRESHOLD", rid, f"'{cell(r, i)}' vs formula/range: {bad}")
            )
            break
    return out


def check_synonym_scope(rid, r, roles):
    out = []
    for i in roles["exact_syn"]:
        for v in [x.strip() for x in cell(r, i).split("|") if x.strip()]:
            if "/" in v or re.search(r"[A-Za-z0-9_]+\.[A-Za-z0-9_.]+", v):
                out.append(
                    Finding("WARN", "SYN-SCOPE", rid, f"synonym '{v}' looks like a DB field path")
                )
            elif v.lower() in ("yes", "no", "true", "false"):
                out.append(
                    Finding("WARN", "SYN-SCOPE", rid, f"synonym '{v}' is a boolean encoding")
                )
            elif re.match(r"^[0-9.]+$", v):
                out.append(Finding("WARN", "SYN-SCOPE", rid, f"synonym '{v}' is a bare number"))
    return out


def lint(path, known_labels, known_ids, mode, external_known):
    _, _, data, roles = read_template(path)
    has_type = "type" in roles
    batch_ids = {r[0].strip() for r in data if r[0].startswith("METPO:")}
    batch_labels = {cell(r, roles.get("label")) for r in data}
    resolve_ids = known_ids | batch_ids
    resolve_labels = known_labels | batch_labels
    out, seen = [], set()
    for r in data:
        rid = r[0].strip()
        label_text = cell(r, roles.get("label"))
        typ = cell(r, roles.get("type")) if has_type else "owl:Class"
        if rid in seen:
            out.append(Finding("ERROR", "ID-DUP", rid, "duplicate ID within file"))
        if external_known and rid in known_ids:
            out.append(Finding("ERROR", "ID-DUP", rid, "ID already exists in canonical METPO"))
        seen.add(rid)
        if cell(r, roles.get("deprecated")).lower() == "true":
            continue  # deprecated rows are historical: only ID-DUP applies
        out += check_id_type(rid, typ, rid.startswith("METPO:"))
        out += check_parent(rid, cell(r, roles.get("parent")), resolve_ids, resolve_labels)
        out += check_definition(rid, r, roles, mode)
        alo, aup = row_bounds(r, roles)
        out += check_formula_synonym(rid, label_text, r, roles, alo, aup)
        out += check_synonym_scope(rid, r, roles)
    return out, len(data)


def ols_lookup(curie):
    url = "https://www.ebi.ac.uk/ols4/api/v2/entities?" + urllib.parse.urlencode(
        {"search": curie, "size": 10}
    )
    try:
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/json", "User-Agent": "metpo-proposal-lint"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            for e in json.load(resp).get("elements", []):
                if e.get("curie") == curie:
                    lab = e.get("label")
                    lab = lab[0] if isinstance(lab, list) else lab
                    return True, bool(e.get("isObsolete")), lab
    except Exception:
        return None, None, None
    return False, None, None


def validate_curies(path):
    _, _, data, roles = read_template(path)
    out, cache = [], {}
    for r in data:
        rid = r[0].strip()
        for key in ("def_source", "xref"):
            if key not in roles:
                continue
            for tok in [x.strip() for x in cell(r, roles[key]).split("|") if x.strip()]:
                if not re.match(r"^[A-Z][A-Za-z]*:\d+$", tok) or tok.startswith("wikidata"):
                    continue
                if tok not in cache:
                    cache[tok] = ols_lookup(tok)
                    time.sleep(0.15)
                found, obs, lab = cache[tok]
                if found is False:
                    out.append(
                        Finding("ERROR", "CURIE-LIVE", rid, f"{key} CURIE '{tok}' not found in OLS")
                    )
                elif obs:
                    out.append(
                        Finding(
                            "ERROR", "CURIE-LIVE", rid, f"{key} CURIE '{tok}' is OBSOLETE ('{lab}')"
                        )
                    )
    return out


@click.command()
@click.argument("template", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--known",
    "known",
    multiple=True,
    type=click.Path(exists=True),
    help="Canonical METPO template(s) for referential checks (repeatable).",
)
@click.option(
    "--mode",
    type=click.Choice(["draft", "submit"]),
    default="submit",
    help="submit = enforce definitions/citations (proposal review); draft = relaxed (audit).",
)
@click.option(
    "--validate-curies",
    "do_validate_curies",
    is_flag=True,
    help="Networked: check xref/def_source CURIEs resolve and are not obsolete in OLS.",
)
@click.option("--json", "as_json", is_flag=True, help="Emit JSON instead of text.")
@click.option("--warn-only", is_flag=True, help="Exit 0 even when ERROR findings are present.")
def main(template, known, mode, do_validate_curies, as_json, warn_only):
    """Lint a METPO ROBOT-template TSV (proposal review or released-content audit)."""
    external = bool(known)
    kl, ki = load_known(known) if external else (set(), set())
    findings, n = lint(template, kl, ki, mode, external)
    if do_validate_curies:
        findings += validate_curies(template)
    errs = [f for f in findings if f.sev == "ERROR"]
    warns = [f for f in findings if f.sev == "WARN"]
    if as_json:
        click.echo(
            json.dumps(
                {
                    "template": str(template),
                    "rows": n,
                    "errors": [(f.code, f.rid, f.msg) for f in errs],
                    "warnings": [(f.code, f.rid, f.msg) for f in warns],
                },
                indent=1,
            )
        )
    else:
        click.echo(
            f"# metpo-proposal-lint: {template}  ({n} rows, mode={mode}, known={'yes' if external else 'self'})"
        )
        for f in sorted(findings, key=lambda x: (x.sev != "ERROR", x.code)):
            click.echo(f"  [{f.sev:5}] {f.code:13} {f.rid:14} {f.msg}")
        click.echo(f"\n  {len(errs)} error(s), {len(warns)} warning(s)")
    raise SystemExit(1 if errs and not warn_only else 0)


if __name__ == "__main__":
    main()
