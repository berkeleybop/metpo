# Madin et al. Bacterial Trait Paths

Documentation for extracting metabolic phenotype data from the Madin et al. bacterial trait dataset for the KG-Microbe knowledge graph.

**Source:** Madin et al. 2020 "A synthesis of bacterial and archaeal phenotypic trait data" + MongoDB `madin.madin` collection

**Citation:** Madin JS, Nielsen DA, Brbic M, et al. A synthesis of bacterial and archaeal phenotypic trait data. Sci Data. 2020;7(1):170.

---

## Quick Reference

| Field Category | Example Fields | Status | METPO Alignment |
|----------------|----------------|--------|-----------------|
| Carbon substrates | `d1_lo`, `d1_up`, carbon source lists | TODO | catabolizes, does_not_catabolize |
| Cell morphology | `cell_shape`, `gram_stain` | TODO | has_cell_shape, has_gram_stain |
| Oxygen tolerance | `sporulation`, `motility` | TODO | produces_spores, is_motile |
| Growth conditions | `growth_tmp`, `optimum_tmp` | TODO | has_optimal_temperature |
| Metabolism | `metabolism`, `pathways` | TODO | has_metabolism_type |
| Isolation source | `isolation_source` | TODO | isolated_from |

---

## Comparison with BacDive

| Aspect | BacDive | Madin et al. |
|--------|---------|--------------|
| Source type | Culture collection | Literature synthesis |
| Record structure | Nested JSON paths | Flat CSV fields |
| Taxonomic coverage | ~93K strains | ~14K species |
| Primary identifier | BacDive strain ID | Species name / NCBI tax ID |
| Data granularity | Strain-level | Species-level |
| Metabolite IDs | ChEBI IDs provided | Need mapping |
| Reference tracking | Per-test references | Per-record references |

---

## MongoDB Connection

```python
from pymongo import MongoClient

client = MongoClient()  # localhost, no auth
db = client.madin
collection = db.madin
```

---

## Analysis Scripts

Scripts for analyzing the Madin dataset are in `metpo/scripts/madin/`:

| Script | Description |
|--------|-------------|
| `generate_field_summary_table.py` | Generate field summary with unique value counts |
| `generate_field_value_reports.py` | Generate TSV reports of value distributions |
| `madin_field_values_analysis.py` | Analyze value distribution for a specific field |
| `madin_unique_values_analysis.py` | Analyze unique values across fields |
| `madin_carbon_substrates_unpacked.py` | Unpack carbon substrate columns |
| `madin_tax_id_validation.py` | Validate NCBI tax IDs |
| `verify_ncbi_taxids.py` | Verify NCBI taxids against taxonomy |
| `verify_edge_taxids.py` | Verify taxids in edge files |
| `analyze_cell_shape.py` | Analyze cell shape values |
| `analyze_isolation_source.py` | Analyze isolation source values |
| `analyze_pathways_format.py` | Analyze pathways field format |
| `analyze_ref_id_format.py` | Analyze reference ID formats |
| `analyze_remaining_categorical.py` | Analyze remaining categorical fields |
| `load_madin_references.py` | Load reference metadata |
| `query_madin_references.py` | Query reference information |
| `madin_sample_ids.py` | Handle sample ID extraction |

---

## Processing Pipeline

1. **Load field summary** to identify categorical vs. numeric fields
2. **Map identifiers** (need ChEBI mapping for carbon substrates)
3. **Validate taxonomic IDs** against NCBITaxon
4. **Generate triples** (NCBITaxon → predicate → object)
5. **Add provenance** (Madin et al. reference ID)

---

## METPO Predicates Needed

### Carbon Substrate Utilization
| Predicate | Description |
|-----------|-------------|
| `METPO:catabolizes` / `does_not_catabolize` | Carbon source utilization |

### Cell Morphology
| Predicate | Description |
|-----------|-------------|
| `METPO:has_cell_shape` | Cell shape characteristic |
| `METPO:has_gram_stain` | Gram stain result |

### Growth Characteristics
| Predicate | Description |
|-----------|-------------|
| `METPO:has_optimal_temperature` | Optimal growth temperature |
| `METPO:produces_spores` / `does_not_produce_spores` | Sporulation |
| `METPO:is_motile` / `is_not_motile` | Motility |

---

## External Resources

- **Original paper:** https://doi.org/10.1038/s41597-020-0497-4
- **Condensed Genome Trait Database:** Source for some traits
- **BacDive paths:** [../bacdive_paths/](../bacdive_paths/) - parallel analysis for BacDive data
