# METPO Development and LLM Workflow Strategy

## ✅ Project Summary

### Repository Focus
- You maintain a GitHub repository supporting:
  - **METPO**: Microbial Ecophysiological Trait and Phenotype Ontology, built using the Ontology Development Kit (ODK).
  - Scripts and tools for converting data (especially from **Names for Life**) into **RDF instance triples** aligned with METPO.
  - Downstream alignment and contribution to **KG-Microbe**, a microbial knowledge graph.

### Current Assets
- **Python scripts** for parsing and transformation.
- **Makefile targets** to automate ontology builds and data workflows.
- **Jupyter notebooks** for exploration, validation, and visualization.
- **SPARQL queries** for semantic reasoning and validation.

### Data Sources
- **Names for Life (N4L)** tables describing microbial temperature traits.
- **KG-Microbe** as the target for semantic alignment and ontology-driven enrichment.

### Problems Observed
- Workflow complexity and fragility.
- No clear testing or auditing of instance triples for:
  - Signal degradation
  - Internal contradictions
  - External consistency with KG-Microbe
- Unstructured exploration of KG-Microbe shortcomings.
- METPO’s current structure may not meet the needs of downstream text mining.

---

## 🎯 Project Goals

1. **Rigorous quality control** for N4L-to-RDF parsing (esp. temperature preferences).
2. **Structure METPO** to serve as a backbone for phenotype/text mining in KG-Microbe.
3. **Validate semantic alignment** between instance triples and KG-Microbe models.
4. **Systematically apply LLMs** across code, data, RDF, and ontologies.

---

## 🤖 Holistic Tooling (LLM + Ecosystem)

| Category | Tool | Use Cases |
|---------|------|-----------|
| Code Auditing | [Goose](https://block.github.io/goose/) | Visualize dependencies, identify unused workflows, resolve fragile build steps. |
| LLM Multi-Agent Coordination | MCP Servers | Multi-step or multi-agent workflows (e.g., parse validation → alignment suggestion → ontology expansion). |
| Metadata Parsing | `pydanticai` Agents | Extract variable names, units, and constraints from tabular files. Identify weakly structured input. |
| RDF Validation | SHACL / LinkML + LLMs | Define rules for class-property usage. Use LLMs to generate examples and negative tests. |
| Parse QC | Claude CLI / OpenAI API | Batch-process parsed triples + input text. Detect ambiguity, signal loss, value/unit mismatches. |
| Ontology Enrichment | Claude + METPO | Extract synonyms, definitions, subclasses from source texts or KG-Microbe gaps. |
| Alignment Debugging | Jupyter + SPARQL + LLM | Compare RDF outputs to KG-Microbe, identify mismatches, suggest ontology-level repairs. |
| Test Engineering | `pytest`, snapshot testing | Prevent regressions in parsers or ontology builds. Validate RDF round-trips. |

---

## 🧠 Recommendations

- [ ] **Run Goose** to visualize and prune redundant workflow components.
- [ ] **Define MCP agent flows** for auditing and semantic integration tasks.
- [ ] **Deploy `pydanticai` agents** to extract metadata from all tabular inputs (N4L, etc.).
- [ ] **Establish parse snapshot testing** and RDF validation pipelines.
- [ ] **Use LLMs to analyze** semantic gaps and overlap with KG-Microbe classes.
- [ ] **Develop enrichment workflows** to feed METPO improvements into KG-Microbe.

---

## 📌 TODO Reminder

> ❗ Mark, please remember to provide:
>
> - A detailed description of your current **N4L workflow**.
> - A list of **files generated** during parsing, validation, and RDF creation.
> - Strengths and weaknesses of these files **in relation to METPO/KG-Microbe goals**.
>   - How much signal is preserved?
>   - What cases are ambiguous or structurally weak?
>   - What components (e.g., unit parsing, range extraction) are most reliable?

Once you do that, we can further develop:
- Automated tests
- Confidence scoring
- Evidence-linked RDF assertions
- Suggestions for KG-Microbe structural changes

---
