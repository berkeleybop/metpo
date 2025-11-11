# SPARQL Queries by Backend

**Last Updated:** 2025-11-11

This directory contains SPARQL queries for different RDF backends used in the METPO project. Each query is categorized by its intended execution target.

---

## Queries for METPO OWL File

**Target:** `src/ontology/metpo.owl` (or released versions)
**Execution:** Load METPO OWL file into RDF library (rdflib, Jena, ROBOT, etc.) and run query

### `find_leaf_classes_without_attributed_synonyms.sparql`
**Purpose:** Quality control - find leaf classes missing synonym attribution
**Used by:** Manual QC workflow
**Key patterns:**
- Filters for METPO namespace: `https://w3id.org/metpo/`
- Finds leaf classes (no subclasses)
- Checks for missing `obo:IAO_0000119` (attribution source) on synonym axioms

### `query_metpo_entities.sparql`
**Purpose:** Export all METPO entities with labels and synonyms
**Used by:** Data extraction workflows
**Key patterns:**
- Filters for METPO namespace: `https://w3id.org/metpo/`
- Extracts labels, exact synonyms, related synonyms
- Returns entity type information

### `query_metpo_labels.rq`
**Purpose:** Look up labels for specific METPO term IDs
**Used by:** Manual lookups (hardcoded term list)
**Key patterns:**
- VALUES clause with specific METPO IRIs
- Simple label extraction

### `metpo_phenotype_classes.rq`
**Purpose:** Browse METPO class hierarchy with parent relationships
**Used by:** Ontology exploration
**Key patterns:**
- Filters for METPO OBO-style IRI: `http://purl.obolibrary.org/obo/METPO_`
- Includes parent class labels
- LIMITED to 100 results

### `chem_interaction_props.rq`
**Purpose:** List chemical interaction properties (subproperties of metpo:2000001)
**Used by:** Schema documentation
**Key patterns:**
- Queries METPO object property hierarchy
- Finds properties related to chemical interactions

### `bacdive_oxygen_phenotype_mappings.rq`
**Purpose:** Extract BacDive-to-METPO oxygen preference mappings
**Used by:** Data integration workflows
**Key patterns:**
- Queries subclasses of `metpo:1000601` (oxygen preference)
- Extracts BacDive labels from `oboInOwl:hasRelatedSynonym`
- Maps to METPO CURIEs and labels

---

## Queries for Multi-Ontology Embeddings

**Target:** RDF triplestore with multiple ontologies loaded (METPO, OMP, PATO, etc.)
**Execution:** Load multiple OWL files into triplestore, then run query

### `extract_for_embeddings.rq`
**Purpose:** Extract labels, synonyms, and definitions from multiple ontologies for ChromaDB embeddings
**Used by:** Semantic similarity analysis workflows
**Key patterns:**
- Queries across any ontology (no namespace filter)
- Handles multiple label properties: `rdfs:label`, `skos:prefLabel`, `dc:title`, `spin:labelTemplate`
- Handles multiple synonym properties: `oboInOwl:hasExactSynonym`, `skos:altLabel`, `owl:altLabel`
- Handles multiple definition properties: `IAO:0000115`, `skos:definition`, `rdfs:comment`
- Excludes W3C built-in classes
- Groups results by class

**Note:** This query was designed for the ChromaDB-based semantic similarity experiments documented in `notebooks/`.

---

## Queries for GraphDB N4L Repository

**Target:** OntoText GraphDB repository with N4L, KG-Microbe, and METPO data
**Execution:** `curl` with GraphDB REST API
**Status:** Archived (N4L work discontinued October 2025)

**Location:** `config/graphdb/sparql/`

### N4L Temperature Extraction
- **`temperature_query.rq`** - Extract temperature-related triples from N4L named graphs
- **`flatten_n4l_parsing_components.rq`** - Flatten ParseGroup/ParseComponent structure to tabular format
- **`metpo_classes_temperature_limits.rq`** - Extract METPO temperature class boundaries

### N4L Data Enrichment (SPARQL Updates)
- **`delete_most_0_value_triples.ru`** - Clean zero-value data from N4L
- **`direct_ncbitaxid_same_as.ru`** - Create owl:sameAs links to NCBI Taxonomy
- **`property_hierarchy.ru`** - Establish property relationships
- **`shared_nm_id_same_as.ru`** - Link entities by shared N4L IDs

See `config/graphdb/README.md` for full documentation of the N4L GraphDB workflow.

---

## Queries for KG-Microbe Exploration

**Target:** KG-Microbe RDF dump loaded into triplestore
**Execution:** Load KG-Microbe TTL files, run exploratory queries
**Status:** Archived (exploratory work from 2025)

**Location:** `sparql/exploration/kg-microbe/`

### KG-Microbe Schema Queries
- **`kg-microbe-Association-predicates.rq`** - Find predicates used with Association entities
- **`kg-microbe-direct-rdf-types.rq`** - Find all rdf:type assertions
- **`kg-microbe-most-associated-taxa.rq`** - Count organisms with most associations
- **`kg-microbe-OrganismTaxon-Association-predicates.rq`** - Predicates linking taxa to associations
- **`kg-microbe-OrganismTaxon-direct-predicates.rq`** - Direct predicates on OrganismTaxon entities
- **`kg-microbe-OrganismTaxon-iri-styles.rq`** - IRI pattern analysis for taxa
- **`kg-microbe-types-bioloink-relations.rq`** - Biolink relation types used

See `sparql/exploration/README.md` for context on these exploratory queries.

---

## Usage Notes

### Running Queries Against METPO OWL

**Using ROBOT:**
```bash
robot query --input src/ontology/metpo.owl \
  --query sparql/find_leaf_classes_without_attributed_synonyms.sparql results.tsv
```

**Using rdflib (Python):**
```python
from rdflib import Graph

g = Graph()
g.parse("src/ontology/metpo.owl", format="xml")

query = open("sparql/query_metpo_entities.sparql").read()
results = g.query(query)
```

### Running Queries Against GraphDB

**Example (archived workflow):**
```bash
curl -X POST http://localhost:7200/repositories/metpo_n4l_etc_automated \
  -H "Content-Type: application/sparql-query" \
  --data-binary @sparql/temperature_query.rq
```

---

## Query Maintenance

When adding new SPARQL queries:

1. **Document the backend** - Add entry to this README under appropriate section
2. **Add header comment** - Include purpose and execution target in query file
3. **Use appropriate extension:**
   - `.rq` - SPARQL query (SELECT/CONSTRUCT/ASK/DESCRIBE)
   - `.ru` - SPARQL update (INSERT/DELETE)
   - `.sparql` - Generic SPARQL (either query or update)

**Header template:**
```sparql
# Backend: METPO OWL file (src/ontology/metpo.owl)
# Purpose: Find classes missing synonym attribution
# Used by: Manual QC workflow

PREFIX owl: <http://www.w3.org/2002/07/owl#>
...
```

---

## Related Documentation

- **N4L GraphDB workflow:** `config/graphdb/README.md`
- **KG-Microbe exploration:** `sparql/exploration/README.md`
- **Ontology development:** `src/ontology/README.md`
- **ChromaDB embeddings:** `notebooks/README.md` (if exists)
