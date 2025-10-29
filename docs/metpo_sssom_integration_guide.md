# Guide to SSSOM Mappings for METPO

**Date**: 2025-10-29
**Purpose**: This document provides guidelines for creating and managing ontology mappings for METPO, with a focus on the Simple Standard for Sharing Ontology Mappings (SSSOM) format. It covers the use of standard mapping predicates, how to handle METPO's current mapping practices, and how to convert other formats like ROBOT templates and custom search results to SSSOM.

---

## 1. Standard Predicates for SSSOM Mappings

To ensure that mappings are machine-readable and interoperable, it is crucial to use standardized predicates. The following predicates are recommended for creating SSSOM files.

### Common Mapping Predicates

| Predicate | Label | Description | Use Case |
| :--- | :--- | :--- | :--- |
| `skos:exactMatch` | Exact Match | The two concepts are equivalent and can be used interchangeably. This is the most common and strongest mapping predicate. | When a METPO term has the same meaning as a term in another ontology. |
| `skos:closeMatch` | Close Match | The two concepts are similar enough that they can be used interchangeably for some applications, but there are subtle differences. | When a METPO term is very similar but not identical to another term. |
| `skos:broadMatch` | Broad Match | The subject of the mapping is broader than the object. | `METPO:Metabolism` `skos:broadMatch` `METPO:Carbon_Metabolism` |
| `skos:narrowMatch`| Narrow Match | The subject of the mapping is narrower than the object. | `METPO:Carbon_Metabolism` `skos:narrowMatch` `METPO:Metabolism` |
| `owl:equivalentClass`| Equivalent Class | Has the same meaning as `skos:exactMatch` but with stronger logical implications in OWL. | Use when you want to assert logical equivalence in an OWL context. |
| `rdfs:subClassOf` | Subclass Of | The subject is a subclass of the object. | For asserting hierarchical relationships. |
| `oboInOwl:hasDbXref`| Has DB Xref | A common way in OBO ontologies to link to a term in another database. It's generally understood as a close or exact match. | Useful for capturing cross-references from OBO-family ontologies. |
| `rdfs:seeAlso` | See Also | A weak, general-purpose link to another resource for additional information. | When you want to link to a related term that is not a direct match. |

---

## 2. METPO's Current Mapping Practices

An analysis of `metpo.owl` reveals two main patterns for representing relationships to external ontologies.

### Good Practice: `skos:closeMatch`

METPO already correctly uses `skos:closeMatch` to map some of its terms to the Biolink model. For example:

```xml
<owl:Class rdf:about="https://w3id.org/metpo/1000059">
    <rdfs:subClassOf rdf:resource="http://purl.obolibrary.org/obo/BFO_0000019"/>
    <skos:closeMatch rdf:resource="https://biolink.github.io/biolink-model/PhenotypicQuality"/>
</owl:Class>
```

This is an excellent precedent and should be the model for future mappings.

### Problematic Practice: `IAO:0000119` (definition source)

In many places, METPO uses the `IAO:0000119` (definition source) annotation property as a de facto mapping predicate. For example, a METPO class might have a definition, and the `definition source` will point to a term in another ontology (e.g., PATO or GO).

**Why this is a problem:**

*   **Semantic Ambiguity:** `IAO:0000119` is intended to cite the source of a textual definition (e.g., a paper, a book, a URL), not to create a relationship between two ontology terms.
*   **Not Machine-Readable as a Mapping:** Automated tools, including SSSOM parsers and OWL reasoners, will not interpret this as a mapping. This "hides" the intended relationship from any standard analysis.

**Recommendation:** All instances where `IAO:0000119` is used to link to another ontology term should be refactored to use a proper mapping predicate like `skos:closeMatch` or `rdfs:seeAlso`.

---

## 3. Converting Other Formats to SSSOM

### ROBOT Templates

If you have a ROBOT template in TSV format that uses a `definition_source` column to hold mapping information, this is an example of the problematic practice described above. To convert this to a proper SSSOM file, you should:

1.  Rename the column containing the METPO term ID to `subject_id`.
2.  Rename the `definition_source` column to `object_id`.
3.  Add a new column called `predicate_id`.
4.  Populate the `predicate_id` column with a standard predicate, such as `skos:closeMatch`.

### Custom Search Result Files

Files like `notebooks/phase1_high_quality_matches.tsv` are very close to SSSOM format already. To convert them into a compliant SSSOM TSV, you need to:

1.  **Rename columns:**
    *   `metpo_id` -> `subject_id`
    *   `metpo_label` -> `subject_label`
    *   `match_iri` -> `object_id`
    *   `match_label` -> `object_label`
    *   `match_ontology` -> `object_source`
2.  **Add a `predicate_id` column:** This is the most important step. You need to decide on the relationship. For high-quality matches, `skos:exactMatch` or `skos:closeMatch` is usually appropriate.
3.  **Add other SSSOM metadata columns** as needed (e.g., `mapping_justification`, `mapping_provider`).

---

## 4. Summary of Recommendations

1.  **Standardize on SKOS:** Use predicates from the SKOS vocabulary (`skos:exactMatch`, `skos:closeMatch`, etc.) for all new mappings.
2.  **Refactor `IAO:0000119`:** Systematically find and replace the use of `IAO:0000119` as a mapping predicate with a more appropriate SKOS property.
3.  **Be Explicit:** When converting other formats to SSSOM, always add an explicit `predicate_id` column. Do not rely on implicit relationships.
4.  **Use Tooling:** Use the `sssom` toolkit to validate your SSSOM files and to convert them to other formats like OWL when needed.
