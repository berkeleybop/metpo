"""Tests for the metpo-proposal-lint QC tool."""

from click.testing import CliRunner

from metpo.scripts.metpo_proposal_lint import (
    fnum,
    lint,
    main,
    parse_bound,
    parse_syn_threshold,
)

# A minimal classes ROBOT template (row 1 labels, row 2 directives) exercising each check.
TEMPLATE = (
    "ID\tlabel\tTYPE\tparent\tdefinition\tdef_source\tformula\trange_min\trange_max\tsyn\n"
    "ID\tLABEL\tTYPE\tSC %\tA IAO:0000115\t>A IAO:0000119\tEC %\tA METPO:range_min\tA METPO:range_max\tA oboInOwl:hasExactSynonym\n"
    "METPO:1007001\tgood term\towl:Class\tphenotype\tA phenotype that is good.\tPMID:1\t\t\t\t\n"
    "METPO:1007002\tbad parent\towl:Class\tMETPO:1000000\tA phenotype.\tPMID:1\t\t\t\t\n"
    "METPO:1007003\ttemperature high\towl:Class\tphenotype\tA phenotype.\tPMID:1\t'x' and 'METPO:2000071' some xsd:decimal[<= 8]\t\t\t\n"
    "METPO:1007004\tgc high\towl:Class\tphenotype\tA phenotype.\tPMID:1\t\t66.3\t\tGC_<=42.65\n"
    "METPO:2000099\tbad type\towl:DatatypeProperty\tphenotype\tA relation.\tPMID:1\t\t\t\t\n"
    "METPO:1007005\tno cite\towl:Class\tphenotype\t\t\t\t\t\t\n"
    "METPO:1007006\tmaps in source\towl:Class\tphenotype\tA phenotype.\tGO:0009399\t\t\t\t\n"
)


def _write(tmp_path):
    p = tmp_path / "proposal.tsv"
    p.write_text(TEMPLATE, encoding="utf-8")
    return p


def _codes(tmp_path, mode):
    findings, _ = lint(str(_write(tmp_path)), {"phenotype"}, set(), mode, external_known=False)
    by_id = {}
    for f in findings:
        by_id.setdefault(f.rid, set()).add(f.code)
    return by_id


def test_fnum():
    assert fnum("37.0") == 37.0
    assert fnum("1.2.3") is None  # regression: must not raise ValueError
    assert fnum("") is None
    assert fnum("abc") is None


def test_parse_bound():
    assert parse_bound("xsd:decimal[>= 40]") == (40.0, None)
    assert parse_bound("xsd:decimal[>= 10, <= 22]") == (10.0, 22.0)
    assert parse_bound("xsd:decimal[<= 8]") == (None, 8.0)
    assert parse_bound("") == (None, None)


def test_parse_syn_threshold_prefixed():
    assert parse_syn_threshold("GC_<=42.65") == (None, 42.65)
    assert parse_syn_threshold("GC_>66.3") == (66.3, None)
    assert parse_syn_threshold("GC_42.65_57.0") == (42.65, 57.0)
    assert parse_syn_threshold("TO_10_to_22") == (10.0, 22.0)
    assert parse_syn_threshold("TO_>40") == (40.0, None)


def test_parse_syn_threshold_prefixless():
    # pH-range synonyms drop their pHR_ prefix; must still parse (Copilot #452 review)
    assert parse_syn_threshold("10_to_14") == (10.0, 14.0)
    assert parse_syn_threshold("8_to_10") == (8.0, 10.0)


def test_parse_syn_threshold_rejects_nonthreshold():
    assert parse_syn_threshold("Ox_microaerophile") == (None, None)
    assert parse_syn_threshold("rod-shaped") == (None, None)
    assert parse_syn_threshold("") == (None, None)


def test_lint_submit_mode(tmp_path):
    codes = _codes(tmp_path, "submit")
    assert "PARENT" in codes["METPO:1007002"]  # parent METPO:1000000
    assert "FORMULA-DIR" in codes["METPO:1007003"]  # 'high' label, only upper bound
    assert "SYN-THRESHOLD" in codes["METPO:1007004"]  # GC_<=42.65 contradicts range_min 66.3
    assert "TYPE-VOCAB" in codes["METPO:2000099"]  # owl:DatatypeProperty
    assert "SRC-MISSING" in codes["METPO:1007005"]  # empty def_source
    assert "DEF-MISSING" in codes["METPO:1007005"]  # empty definition
    assert "SRC-ISMAP" in codes["METPO:1007006"]  # GO CURIE in def_source
    assert "METPO:1007001" not in codes  # clean row produces nothing


def test_lint_draft_relaxes_citations(tmp_path):
    codes = _codes(tmp_path, "draft")
    # draft mode must not require definitions/citations...
    assert "METPO:1007005" not in codes
    # ...but structural/value defects still fire
    assert "SYN-THRESHOLD" in codes["METPO:1007004"]
    assert "PARENT" in codes["METPO:1007002"]


def test_cli_exits_nonzero_on_errors(tmp_path):
    result = CliRunner().invoke(main, [str(_write(tmp_path)), "--mode", "draft"])
    assert result.exit_code == 1
    assert "error(s)" in result.output


def test_cli_warn_only_exits_zero(tmp_path):
    result = CliRunner().invoke(main, [str(_write(tmp_path)), "--mode", "draft", "--warn-only"])
    assert result.exit_code == 0


# DEF-FORM: hierarchy/label/definition compatibility -- the genus of an Aristotelian
# definition must be the asserted parent's label (Mark's modeling principle; #64/#377).
DEF_FORM_TEMPLATE = (
    "ID\tlabel\tTYPE\tparent\tdefinition\tdef_source\n"
    "ID\tLABEL\tTYPE\tSC %\tA IAO:0000115\t>A IAO:0000119\n"
    "METPO:1007101\tgood def\towl:Class\tphenotype\tA phenotype that is observable.\tPMID:1\n"
    "METPO:1007102\twrong genus\towl:Class\tphenotype\tA biochemical test that detects catalase.\tPMID:1\n"
    "METPO:1007103\tno that-form\towl:Class\tphenotype\tDetects catalase activity.\tPMID:1\n"
    "METPO:1007104\tin-which ok\towl:Class\ttrophic type\tA trophic type in which an organism fixes carbon.\tPMID:1\n"
    "METPO:1007105\tcharacterized ok\towl:Class\tcell shape\tA cell shape characterized by a rod morphology.\tPMID:1\n"
    "METPO:1007106\tparent phenotype genus\towl:Class\thalophilic\tA halophilic phenotype in which an organism requires high salt.\tPMID:1\n"
)


def test_def_form(tmp_path):
    p = tmp_path / "defform.tsv"
    p.write_text(DEF_FORM_TEMPLATE, encoding="utf-8")
    findings, _ = lint(
        str(p), {"phenotype", "trophic type", "cell shape", "halophilic"}, set(), "submit", external_known=False
    )
    by_id = {}
    for f in findings:
        by_id.setdefault(f.rid, set()).add(f.code)
    # genus == parent label -> compatible, no DEF-FORM
    assert "DEF-FORM" not in by_id.get("METPO:1007101", set())
    # genus 'biochemical test' != parent 'phenotype' -> DEF-FORM
    assert "DEF-FORM" in by_id["METPO:1007102"]
    # missing the 'A <genus> <connector> ...' shape -> DEF-FORM
    assert "DEF-FORM" in by_id["METPO:1007103"]
    # 'in which' / 'characterized by' are valid connectors when genus == parent
    assert "DEF-FORM" not in by_id.get("METPO:1007104", set())
    assert "DEF-FORM" not in by_id.get("METPO:1007105", set())
    # genus "<parent> phenotype" (adjectival parent) is accepted
    assert "DEF-FORM" not in by_id.get("METPO:1007106", set())


def test_baseline_ratchet(tmp_path):
    template = _write(tmp_path)
    baseline = tmp_path / "baseline.json"
    runner = CliRunner()

    # 1. record the current findings as the accepted floor
    r = runner.invoke(
        main, [str(template), "--mode", "submit", "--baseline", str(baseline), "--write-baseline"]
    )
    assert r.exit_code == 0
    assert baseline.exists()

    # 2. re-running against that baseline: nothing new -> pass even though debt exists
    r = runner.invoke(main, [str(template), "--mode", "submit", "--baseline", str(baseline)])
    assert r.exit_code == 0
    assert "baselined" in r.output

    # 3. a NEW violation beyond the baseline -> fail
    broken = tmp_path / "broken.tsv"
    broken.write_text(
        TEMPLATE
        + "METPO:1007200\tnew bad\towl:Class\tMETPO:9999999\tA phenotype.\tPMID:1\t\t\t\t\n",
        encoding="utf-8",
    )
    r = runner.invoke(main, [str(broken), "--mode", "submit", "--baseline", str(baseline)])
    assert r.exit_code == 1
    assert "METPO:1007200" in r.output


def test_write_baseline_requires_path(tmp_path):
    r = CliRunner().invoke(main, [str(_write(tmp_path)), "--write-baseline"])
    assert r.exit_code != 0
