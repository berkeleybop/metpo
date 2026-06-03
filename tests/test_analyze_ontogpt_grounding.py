from metpo.presentations.analyze_ontogpt_grounding import count_groundings, main


def test_count_groundings_tracks_auto_by_category(tmp_path):
    yaml_file = tmp_path / "sample.yaml"
    yaml_file.write_text(
        """
extracted_object:
  chemical_utilizations:
    - object: CHEBI:123
    - object: AUTO:missing_chebi
  study_taxa:
    - NCBITaxon:2
    - AUTO:missing_taxon
"""
    )

    counts = count_groundings(yaml_file)

    assert counts["chebi"] == 1
    assert counts["ncbitaxon"] == 1
    assert counts["auto"] == 2
    assert counts["auto_chemical"] == 1
    assert counts["auto_taxon"] == 1


def test_main_reports_chemical_and_taxon_success_rates(tmp_path, monkeypatch, capsys):
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    (outputs / "doc-chemical.yaml").write_text(
        """
extracted_object:
  chemical_utilizations:
    - object: CHEBI:123
    - object: AUTO:missing_chebi
  study_taxa:
    - NCBITaxon:2
    - AUTO:missing_taxon
"""
    )

    monkeypatch.chdir(tmp_path)
    main()
    captured = capsys.readouterr().out

    assert "ChEBI chemical success rate: 50.0% (1/2)" in captured
    assert "NCBITaxon success rate: 50.0% (1/2)" in captured
