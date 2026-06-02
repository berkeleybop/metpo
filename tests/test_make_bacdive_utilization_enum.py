"""Tests for make_bacdive_utilization_enum utility."""

import yaml

from metpo.tools.make_bacdive_utilization_enum import convert_tsv_to_linkml_enum


def _write_tsv(tmp_path, data_rows):
    tsv_path = tmp_path / "bacdive.tsv"
    content = [
        "ID\tTYPE\tLABEL\tbacdive count",
        "ID\tTYPE\tLABEL\tA",
    ]
    content.extend(data_rows)
    tsv_path.write_text("\n".join(content) + "\n", encoding="utf-8")
    return tsv_path


def test_preserves_apostrophes_in_yaml_values(tmp_path):
    tsv_path = _write_tsv(
        tmp_path,
        [
            "https://example.org/relationship/1\towl:ObjectProperty\tdoesn't utilize\t1",
        ],
    )

    yaml_output = convert_tsv_to_linkml_enum(str(tsv_path), enum_name="RelationshipTypeEnum")
    parsed = yaml.safe_load(yaml_output)

    permissible_values = parsed["enums"]["RelationshipTypeEnum"]["permissible_values"]
    assert "doesn't_utilize" in permissible_values


def test_permissible_value_meaning_uses_full_uri(tmp_path):
    uri = "https://example.org/relationship/123"
    tsv_path = _write_tsv(
        tmp_path,
        [
            f"{uri}\towl:ObjectProperty\tutilizes carbon source\t1",
        ],
    )

    yaml_output = convert_tsv_to_linkml_enum(str(tsv_path), enum_name="RelationshipTypeEnum")
    parsed = yaml.safe_load(yaml_output)

    entry = parsed["enums"]["RelationshipTypeEnum"]["permissible_values"]["utilizes_carbon_source"]
    assert entry["meaning"] == uri
