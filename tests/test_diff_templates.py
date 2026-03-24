"""Tests for diff_templates CLI."""

from pathlib import Path

import click
import pytest
from click.testing import CliRunner

from metpo.scripts.diff_templates import (
    compare,
    load_full_rows,
    load_headers,
    load_ids,
    main,
    resolve_source,
)

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def template_a(tmp_path):
    """Template with 3 IDs."""
    content = (
        " ID\tlabel\tTYPE\tparent\n"
        " ID\tLABEL\tTYPE\tSC %\n"
        "METPO:1000001\talpha\towl:Class\tphenotype\n"
        "METPO:1000002\tbeta\towl:Class\tphenotype\n"
        "METPO:1000003\tgamma\towl:Class\tphenotype\n"
    )
    p = tmp_path / "a.tsv"
    p.write_text(content)
    return p


@pytest.fixture
def template_b(tmp_path):
    """Template with 3 IDs, one different, one label changed."""
    content = (
        " ID\tlabel\tTYPE\tparent\n"
        " ID\tLABEL\tTYPE\tSC %\n"
        "METPO:1000001\talpha\towl:Class\tphenotype\n"
        "METPO:1000002\tbeta renamed\towl:Class\tquality\n"
        "METPO:1000004\tdelta\towl:Class\tphenotype\n"
    )
    p = tmp_path / "b.tsv"
    p.write_text(content)
    return p


@pytest.fixture
def empty_template(tmp_path):
    """Template with only headers, no data rows."""
    content = " ID\tlabel\tTYPE\n ID\tLABEL\tTYPE\n"
    p = tmp_path / "empty.tsv"
    p.write_text(content)
    return p


class TestLoadIds:
    def test_loads_metpo_ids(self, template_a):
        ids = load_ids(template_a)
        assert len(ids) == 3
        assert ids["METPO:1000001"] == "alpha"
        assert ids["METPO:1000003"] == "gamma"

    def test_skips_header_rows(self, template_a):
        ids = load_ids(template_a)
        assert "ID" not in ids
        assert " ID" not in ids

    def test_empty_template(self, empty_template):
        ids = load_ids(empty_template)
        assert len(ids) == 0


class TestLoadFullRows:
    def test_loads_rows_by_id(self, template_a):
        rows = load_full_rows(template_a)
        assert len(rows) == 3
        assert rows["METPO:1000001"][1] == "alpha"
        assert rows["METPO:1000003"][3] == "phenotype"

    def test_empty_template(self, empty_template):
        rows = load_full_rows(empty_template)
        assert len(rows) == 0


class TestLoadHeaders:
    def test_loads_first_row(self, template_a):
        headers = load_headers(template_a)
        assert headers[0] == "ID"
        assert headers[1] == "label"
        assert headers[2] == "TYPE"


class TestCompare:
    def test_detects_additions_and_removals(self, template_a, template_b):
        result = compare("A", template_a, "B", template_b)
        assert "METPO:1000003" in result["only_a"]
        assert "METPO:1000004" in result["only_b"]
        assert result["common"] == 2

    def test_detects_label_changes(self, template_a, template_b):
        result = compare("A", template_a, "B", template_b)
        assert result["label_changes"] == 1

    def test_identical_files(self, template_a):
        result = compare("A", template_a, "B", template_a)
        assert len(result["only_a"]) == 0
        assert len(result["only_b"]) == 0
        assert result["label_changes"] == 0
        assert result["common"] == 3

    def test_empty_vs_populated(self, empty_template, template_a):
        result = compare("empty", empty_template, "A", template_a)
        assert len(result["only_a"]) == 0
        assert len(result["only_b"]) == 3
        assert result["common"] == 0


class TestResolveSource:
    def test_file_path(self, template_a):
        path = resolve_source(str(template_a), "classes")
        assert path == template_a

    def test_git_ref(self):
        path = resolve_source("HEAD", "classes")
        assert path.exists()
        ids = load_ids(path)
        assert len(ids) > 0

    def test_bad_source(self):
        with pytest.raises(click.exceptions.BadParameter, match="Cannot resolve"):
            resolve_source("nonexistent-ref-and-not-a-file", "classes")


class TestCli:
    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Diff METPO ROBOT templates" in result.output

    def test_file_vs_file(self, template_a, template_b):
        runner = CliRunner()
        result = runner.invoke(
            main, ["-a", str(template_a), "-b", str(template_b), "-t", "classes"]
        )
        assert result.exit_code == 0
        assert "METPO:1000003" in result.output
        assert "METPO:1000004" in result.output
        assert "beta renamed" in result.output

    def test_cell_diffs_flag(self, template_a, template_b):
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["-a", str(template_a), "-b", str(template_b), "-t", "classes", "--cell-diffs"],
        )
        assert result.exit_code == 0
        assert "Cell-level diffs" in result.output

    def test_git_ref(self):
        runner = CliRunner()
        result = runner.invoke(main, ["-a", "HEAD", "-b", "HEAD", "-t", "properties"])
        assert result.exit_code == 0
        assert "IDs and labels are identical" in result.output
